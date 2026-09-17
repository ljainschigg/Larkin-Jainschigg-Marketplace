#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "requests>=2.31",
#   "beautifulsoup4>=4.12",
# ]
# ///
"""
linkcheck — check for broken links in a versioned MkDocs documentation site.

Usage:
    python linkcheck.py [options] SITE_URL

    SITE_URL is the root of the docs site, e.g.:
        https://docs.example.com/project

The tool:
  1. Fetches SITE_URL/versions.json to discover published versions
     (hidden entries like "next" are skipped automatically)
  2. For each version, parses the navigation sidebar to enumerate all pages
  3. Fetches each page and collects links from the content area only
     (nav/header/footer links are ignored)
  4. Checks every unique link once (cached across versions)
  5. Reports broken links (HTTP >= 400 or connection failure) grouped by version,
     with the pages on which each broken link appears

Options:
    -w, --workers N     Concurrent request workers (default: 10)
    -t, --timeout N     Request timeout in seconds (default: 10)
    -v, --version VER   Check only this version; may be repeated
    --ignore PREFIX     Skip links whose URL starts with PREFIX (repeatable)
                        http://127.0.0.1, http://localhost, and http://0.0.0.0
                        are always ignored (unreachable from remote checker)
    --no-color          Disable ANSI color output
"""

import argparse
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Thread, Event
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup

RED    = "\033[31m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def fmt(code, text, color):
    return f"{code}{text}{RESET}" if color else text


def is_broken(status, err):
    return err is not None or (status is not None and status >= 400)


class Progress:
    def __init__(self, color, tty):
        self.color = color
        self.tty = tty
        self.lock = Lock()
        self._d = {'phase': '', 'checked': 0, 'total': 0, 'broken': 0, 'last': ''}
        self._stop = Event()
        self._t0 = time.time()
        self._thread = Thread(target=self._loop, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()
        if self.tty:
            print(f'\r{" " * 132}\r', end='', flush=True)

    def update(self, **kw):
        with self.lock:
            self._d.update(kw)

    def _loop(self):
        while not self._stop.is_set():
            time.sleep(0.5)
            with self.lock:
                d = dict(self._d)
            elapsed = time.time() - self._t0
            last = (d['last'][:65] + '…') if len(d['last']) > 66 else d['last']
            pct  = f" {100 * d['checked'] // d['total']:3d}%" if d['total'] else ''
            brok = fmt(RED, f"broken:{d['broken']}", self.color) if d['broken'] else f"broken:0"
            line = (f"  {elapsed:5.0f}s  [{d['phase']}]  "
                    f"{d['checked']}/{d['total']}{pct}  {brok}  "
                    f"{fmt(DIM, last, self.color)}")
            if self.tty:
                print(f'\r{line:<132}', end='', flush=True)
            else:
                print(line, flush=True)


class DocsChecker:
    _DEFAULT_IGNORE = ('http://127.0.0.1', 'http://localhost', 'http://0.0.0.0')

    def __init__(self, site_url, workers=10, timeout=10, color=True,
                 version_filter=None, ignore_prefixes=None):
        self.site_url      = site_url.rstrip('/')
        self.workers       = workers
        self.timeout       = timeout
        self.color         = color
        self.version_filter = set(version_filter) if version_filter else None
        self.ignore_prefixes = tuple(self._DEFAULT_IGNORE) + tuple(ignore_prefixes or ())

        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'linkcheck/2.0'

        self._link_cache      = {}   # url -> (status, err)
        self._link_cache_lock = Lock()

    # ------------------------------------------------------------------ HTTP

    def _get(self, url):
        try:
            r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            return r.status_code, None, r
        except requests.exceptions.TooManyRedirects:
            return None, 'too many redirects', None
        except requests.exceptions.SSLError:
            return None, 'SSL error', None
        except requests.exceptions.ConnectionError:
            return None, 'connection error', None
        except requests.exceptions.Timeout:
            return None, 'timeout', None
        except Exception as e:
            return None, str(e), None

    # --------------------------------------------------------------- Discovery

    def get_versions(self):
        url = f'{self.site_url}/versions.json'
        status, err, resp = self._get(url)
        if err:
            raise RuntimeError(f'Cannot fetch {url}: {err}')
        if status != 200:
            raise RuntimeError(f'Cannot fetch {url}: HTTP {status}')
        out = []
        for v in resp.json():
            if v.get('properties', {}).get('hidden'):
                continue
            ver = v['version']
            if self.version_filter and ver not in self.version_filter:
                continue
            out.append(ver)
        return out

    def get_pages(self, version):
        """
        Fetch the version homepage and extract all intra-version page URLs
        from the MkDocs navigation sidebar.
        Returns a sorted list of absolute URLs.
        """
        base = f'{self.site_url}/{version}/'
        status, err, resp = self._get(base)
        if err or (status and status >= 400):
            print(f'  Warning: {base} unreachable ({err or f"HTTP {status}"})',
                  flush=True)
            return []

        final_base = resp.url  # respect redirects
        soup = BeautifulSoup(resp.text, 'html.parser')
        nav  = (soup.select_one('nav[aria-label="Navigation"]') or
                soup.select_one('.md-nav--primary'))

        pages = {final_base}
        if nav:
            prefix = f'{self.site_url}/{version}/'
            for a in nav.find_all('a', href=True):
                href = a['href'].strip()
                if not href or href.startswith(
                        ('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
                    continue
                if href.startswith('http://') or href.startswith('https://'):
                    continue           # skip external nav links (GitHub etc.)
                abs_url, _ = urldefrag(urljoin(final_base, href))
                if abs_url.startswith(prefix):
                    pages.add(abs_url)

        return sorted(pages)

    # ---------------------------------------------------------- Link extraction

    def get_content_links(self, page_url):
        """
        Fetch a page and return all links found in the content area.
        Returns (page_status, page_err, [link_url, ...]).
        """
        status, err, resp = self._get(page_url)
        if err or (status and status >= 400):
            return status, err, []

        final_url = resp.url
        soup      = BeautifulSoup(resp.text, 'html.parser')
        content   = (soup.select_one('article.md-content__inner') or
                     soup.select_one('article') or
                     soup.select_one('main'))
        if not content:
            return status, None, []

        links = []
        for a in content.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith(
                    ('mailto:', 'tel:', 'javascript:', 'data:', '#')):
                continue
            abs_url, _ = urldefrag(urljoin(final_url, href))
            if urlparse(abs_url).scheme not in ('http', 'https'):
                continue
            if abs_url.startswith(self.ignore_prefixes):
                continue
            text = ' '.join(a.get_text().split()).strip()
            links.append((abs_url, text))
        return status, None, links

    # ------------------------------------------------------------ Link checking

    def check_link(self, url):
        with self._link_cache_lock:
            if url in self._link_cache:
                return self._link_cache[url]

        status, err, _ = self._get(url)
        result = (status, err)
        with self._link_cache_lock:
            self._link_cache[url] = result
        return result

    # -------------------------------------------------------------------- Main

    def run(self):
        tty      = sys.stdout.isatty()
        progress = Progress(self.color, tty)
        progress.start()
        t0       = time.time()

        try:
            versions = self.get_versions()
            print(f'Versions: {", ".join(versions)}', flush=True)

            # version -> {link_url: (status, err, [referencing_page_urls])}
            all_results = {}
            total_broken = 0

            for version in versions:
                print(f'\nVersion {version}:', flush=True)

                pages = self.get_pages(version)
                print(f'  {len(pages)} pages in nav', flush=True)

                # ---- Phase A: collect content links from all pages ----
                progress.update(phase=f'{version} collecting', checked=0,
                                total=len(pages), broken=total_broken, last='')

                link_to_pages = defaultdict(set)   # link -> set of pages
                link_to_texts = defaultdict(set)   # link -> set of anchor texts
                with ThreadPoolExecutor(max_workers=self.workers) as pool:
                    futures = {pool.submit(self.get_content_links, p): p
                               for p in pages}
                    done = 0
                    for f in as_completed(futures):
                        page = futures[f]
                        done += 1
                        try:
                            _, _, links = f.result()
                        except Exception:
                            links = []
                        for url, text in links:
                            link_to_pages[url].add(page)
                            if text:
                                link_to_texts[url].add(text)
                        progress.update(checked=done, last=page)

                unique_links = list(link_to_pages)
                print(f'  {len(unique_links)} unique content links to check',
                      flush=True)

                # ---- Phase B: check each unique link (cache deduplicates) ----
                progress.update(phase=f'{version} checking', checked=0,
                                total=len(unique_links), last='')

                link_results = {}
                with ThreadPoolExecutor(max_workers=self.workers) as pool:
                    futures = {pool.submit(self.check_link, lnk): lnk
                               for lnk in unique_links}
                    done = 0
                    for f in as_completed(futures):
                        link = futures[f]
                        done += 1
                        try:
                            status, err = f.result()
                        except Exception as e:
                            status, err = None, str(e)
                        link_results[link] = (status, err)
                        if is_broken(status, err):
                            total_broken += 1
                        progress.update(checked=done, broken=total_broken,
                                        last=link)

                all_results[version] = {
                    link: (status, err, sorted(link_to_pages[link]),
                           sorted(link_to_texts.get(link, [])))
                    for link, (status, err) in link_results.items()
                }

        finally:
            progress.stop()

        print(f'\nDone in {time.time() - t0:.1f}s', flush=True)
        self._report(all_results)
        sys.exit(1 if total_broken else 0)

    # ------------------------------------------------------------------ Report

    def _report(self, all_results):
        c = self.color
        total_links  = sum(len(vr) for vr in all_results.values())
        total_broken = sum(1 for vr in all_results.values()
                           for s, e, *_ in vr.values() if is_broken(s, e))

        print(f'\n{"=" * 60}')
        print(f'  Site:    {self.site_url}')
        print(f'  Checked: {total_links} unique links across '
              f'{len(all_results)} version(s)')
        print(f'  {fmt(GREEN, f"OK: {total_links - total_broken}", c)}  '
              f'{fmt(RED, f"Broken: {total_broken}", c)}')
        print(f'{"=" * 60}')

        if not total_broken:
            print(fmt(GREEN, '\nNo broken links found.\n', c))
            return

        for version in sorted(all_results):
            vr = all_results[version]
            broken = {lnk: (s, e, pgs, txts)
                      for lnk, (s, e, pgs, txts) in vr.items() if is_broken(s, e)}
            if not broken:
                print(f'\nVersion {version}: {fmt(GREEN, "no broken links", c)}')
                continue

            print(f'\nVersion {version}: '
                  f'{fmt(RED, f"{len(broken)} broken link(s)", c)}\n')
            for link in sorted(broken):
                status, err, pages, texts = broken[link]
                reason = (fmt(YELLOW, f'error: {err}', c) if err
                          else fmt(RED, f'HTTP {status}', c))
                print(f'  {reason}')
                print(f'    {link}')
                for text in sorted(texts):
                    print(fmt(DIM, f'    text: {text}', c))
                for page in pages[:5]:
                    print(fmt(DIM, f'    on: {page}', c))
                if len(pages) > 5:
                    print(fmt(DIM, f'    ... and {len(pages) - 5} more', c))
                print()


def main():
    parser = argparse.ArgumentParser(
        description='Check for broken links in a versioned MkDocs docs site.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('site_url', metavar='SITE_URL')
    parser.add_argument('-w', '--workers', type=int, default=10)
    parser.add_argument('-t', '--timeout', type=int, default=10)
    parser.add_argument('-v', '--version', action='append', dest='versions',
                        metavar='VER',
                        help='Check only this version (repeatable)')
    parser.add_argument('--ignore', action='append', dest='ignore_prefixes',
                        metavar='PREFIX',
                        help='Skip links starting with PREFIX (repeatable)')
    parser.add_argument('--no-color', action='store_true')
    args = parser.parse_args()

    color = not args.no_color and sys.stdout.isatty()
    print(f'Checking {args.site_url} ...', flush=True)

    DocsChecker(
        site_url=args.site_url,
        workers=args.workers,
        timeout=args.timeout,
        color=color,
        version_filter=args.versions,
        ignore_prefixes=args.ignore_prefixes,
    ).run()


if __name__ == '__main__':
    main()
