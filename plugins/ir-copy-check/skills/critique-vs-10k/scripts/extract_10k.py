#!/usr/bin/env python3
"""extract_10k.py — turn a filed 10-K into a sectioned, citable plain-text corpus.

A 10-K as filed is not readable in one pass. A large filer's annual report can run
to tens of megabytes as a Word document — millions of characters of text, of which
often only a third or so is the 10-K body proper. The remainder is exhibit
documents (purchase agreements, escrow agreements, SOX certifications) appended
after the signature page. Critiquing marketing copy against "the 10-K" means the
body, not the exhibits.

This script does three deterministic things:

  1. Extracts text from the filing (Word/OOXML, HTML, or plain text), keeping
     paragraphs and table rows in document order so tables stay readable.
  2. Splits the 10-K BODY from the appended EXHIBITS at the signature page.
  3. Sections the body on its `ITEM n.` headings and writes one file per section,
     plus an index recording every section's line range and size.

Output is plain text, one file per section, so a critique can cite an Item and
quote the filed language exactly.

Usage:
    python3 extract_10k.py <filing> [-o OUTDIR] [--list]

    <filing>    Path to the filing. Accepts:
                  - Word/OOXML (.docx, or a .docx misnamed .rtf/.doc — detected
                    by content, not extension)
                  - HTML (.htm/.html, e.g. as downloaded from SEC EDGAR)
                  - plain text (.txt)
    -o OUTDIR   Where to write the corpus. Default: ./extract
    --list      Print the detected section map and exit; write nothing.

Exit codes: 0 ok, 1 error (unreadable file, no sections found), 2 usage error.

Standard library only — no pip install, no network.
"""

import argparse
import os
import re
import sys
import zipfile
from html.parser import HTMLParser

# ---------------------------------------------------------------- text extraction

_WT = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
_BLOCK = re.compile(r"<w:tr[\s>].*?</w:tr>|<w:p[\s>].*?</w:p>|<w:p/>", re.S)
_TC = re.compile(r"<w:tc[\s>].*?</w:tc>", re.S)

_ENTITIES = (
    ("&amp;", "&"),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&quot;", '"'),
    ("&apos;", "'"),
    ("&nbsp;", " "),
    ("&#160;", " "),
)


def _unescape(s):
    for a, b in _ENTITIES:
        s = s.replace(a, b)
    return re.sub(r"&#\d+;", "", s)


def from_ooxml(path):
    """Extract text from a Word/OOXML file, preserving paragraph and table order.

    Table rows become ' | '-joined cell text so figures stay associated with
    their labels — essential for the financial tables.
    """
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "word/document.xml" not in names:
            raise ValueError("zip archive is not a Word document (no word/document.xml)")
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    body_start = xml.find("<w:body>")
    if body_start != -1:
        xml = xml[body_start:]
    lines = []
    for m in _BLOCK.finditer(xml):
        seg = m.group(0)
        if seg.startswith("<w:tr"):
            cells = [_unescape("".join(_WT.findall(c.group(0)))).strip() for c in _TC.finditer(seg)]
            row = " | ".join(cells)
            if row.strip(" |"):
                lines.append(row)
        else:
            para = _unescape("".join(_WT.findall(seg))).strip()
            if para:
                lines.append(para)
    return lines


class _HTMLText(HTMLParser):
    """Collect text from an HTML filing, breaking lines on block-level tags."""

    _BREAK = {
        "p", "div", "br", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
        "li", "table", "thead", "tbody",
    }
    _SKIP = {"script", "style"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = []
        self._buf = []
        self._skip = 0

    def _flush(self):
        text = " ".join("".join(self._buf).split())
        if text:
            self.lines.append(text)
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip += 1
        elif tag in self._BREAK:
            self._flush()
        elif tag == "td":
            self._buf.append(" | ")

    def handle_endtag(self, tag):
        if tag in self._SKIP:
            self._skip = max(0, self._skip - 1)
        elif tag in self._BREAK:
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


def from_html(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        parser = _HTMLText()
        parser.feed(fh.read())
        parser.close()
    return [ln.strip(" |") if ln.strip(" |") else ln for ln in parser.lines if ln.strip(" |")]


def extract_lines(path):
    """Dispatch on file *content*, not extension.

    Filings arrive misnamed often enough to matter — a filing is sometimes a
    .docx carrying a .rtf extension, or HTML saved with a .txt name.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError("no such file")
    with open(path, "rb") as fh:
        head = fh.read(8)
    if head[:2] == b"PK":
        return from_ooxml(path)
    if head[:5].lower() in (b"<html", b"<!doc") or head[:6].lower() == b"<?xml ":
        return from_html(path)
    if head[:5] == b"{\\rtf":
        raise ValueError(
            "this is a real RTF file; convert it first "
            "(e.g. `libreoffice --headless --convert-to docx <file>`)"
        )
    if head[:4] == b"\xd0\xcf\x11\xe0":
        raise ValueError(
            "this is a legacy binary .doc file; convert it first "
            "(e.g. `libreoffice --headless --convert-to docx <file>`)"
        )
    with open(path, encoding="utf-8", errors="replace") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


# ---------------------------------------------------------------- sectioning

# Item headings as they appear in the body: "ITEM 1A.    RISK FACTORS".
# The table of contents uses a different, table-row form ("| Item 1A. | Risk
# Factors | 27"), so anchoring on a line that *starts* with ITEM excludes it.
_ITEM = re.compile(r"^ITEM\s+(\d+[A-C]?)\s*\.\s*(.*)$", re.I)
_PART = re.compile(r"^PART\s+([IVX]+)\s*$", re.I)
_SIGNATURES = re.compile(r"^SIGNATURES\s*$", re.I)
_EXHIBIT_DOC = re.compile(r"^Exhibit\s+\d+\.\d+", re.I)

# Item headings are filed in caps ("MANAGEMENT'S DISCUSSION AND ANALYSIS..."), and
# str.title() would render that "Management’S ... And". Lower-case the connectives
# and split only on whitespace so apostrophes stay inside their word.
_LOWER = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into", "nor",
    "of", "on", "or", "the", "to", "with",
}


def _titlecase(text):
    words = text.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if w.startswith("[") or (w.isupper() and len(w) <= 5 and not w.isalpha()):
            out.append(w)  # "[Reserved]", "10-K", bracketed or coded tokens
        elif i != 0 and lw in _LOWER:
            out.append(lw)
        else:
            out.append(lw[0].upper() + lw[1:])
    return " ".join(out)


def find_body_end(lines):
    """Return the index one past the last line of the 10-K body.

    The body ends at the signature page. Standalone exhibit documents follow it,
    each opening with an `Exhibit N.N` line. Everything from the first such line
    after SIGNATURES onward is exhibit material, not the 10-K.
    """
    sig = next((i for i, ln in enumerate(lines) if _SIGNATURES.match(ln)), None)
    if sig is None:
        return len(lines)
    for i in range(sig + 1, len(lines)):
        if _EXHIBIT_DOC.match(lines[i]):
            return i
    return len(lines)


def find_sections(lines, body_end):
    """Locate front matter and each ITEM section within the body.

    Returns a list of (slug, title, start, end) with 0-based, end-exclusive
    bounds. A repeated ITEM heading (10-Ks restate them in running headers) is
    ignored — only the first occurrence anchors a section.
    """
    marks, seen = [], set()
    for i, ln in enumerate(lines[:body_end]):
        m = _ITEM.match(ln)
        if not m:
            continue
        num = m.group(1).upper()
        if num in seen:
            continue
        seen.add(num)
        title = _titlecase(" ".join(m.group(2).split()).rstrip(".")) or f"Item {num}"
        marks.append((i, f"item{num.lower()}", f"Item {num}. {title}"))

    if not marks:
        return []

    sections = []
    # Everything before the first ITEM heading: cover page, forward-looking
    # statements, glossary of defined terms, risk summary. All of it is
    # messaging-relevant, so keep it as a section rather than discarding it.
    if marks[0][0] > 0:
        sections.append(("00-front-matter", "Front matter (cover, forward-looking statements, glossary)", 0, marks[0][0]))
    for idx, (start, slug, title) in enumerate(marks):
        end = marks[idx + 1][0] if idx + 1 < len(marks) else body_end
        sections.append((f"{idx + 1:02d}-{slug}", title, start, end))
    return sections


# ---------------------------------------------------------------- output

def write_corpus(lines, sections, body_end, outdir, source):
    body_dir = os.path.join(outdir, "body")
    os.makedirs(body_dir, exist_ok=True)

    for slug, title, start, end in sections:
        path = os.path.join(body_dir, f"{slug}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"# {title}\n")
            fh.write(f"# source: {os.path.basename(source)}  body lines {start + 1}-{end}\n\n")
            fh.write("\n".join(lines[start:end]) + "\n")

    with open(os.path.join(outdir, "full-body.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines[:body_end]) + "\n")

    exhibits = lines[body_end:]
    if exhibits:
        with open(os.path.join(outdir, "exhibits.txt"), "w", encoding="utf-8") as fh:
            fh.write(
                "# Appended exhibit documents — NOT part of the 10-K body.\n"
                "# Purchase/escrow/credit agreements, certifications, policies.\n"
                "# Do not cite these as 10-K disclosure.\n\n"
            )
            fh.write("\n".join(exhibits) + "\n")

    index = os.path.join(outdir, "00-INDEX.md")
    with open(index, "w", encoding="utf-8") as fh:
        fh.write("# 10-K extract index\n\n")
        fh.write(f"Source filing: `{source}`\n\n")
        fh.write(f"Body: {body_end:,} lines / {sum(len(l) for l in lines[:body_end]):,} chars. ")
        fh.write(f"Appended exhibits: {len(exhibits):,} lines / {sum(len(l) for l in exhibits):,} chars ")
        fh.write("(excluded from the body, kept in `exhibits.txt` for reference).\n\n")
        fh.write("| Section | File | Body lines | Chars |\n")
        fh.write("|---|---|---|---|\n")
        for slug, title, start, end in sections:
            chars = sum(len(l) for l in lines[start:end])
            fh.write(f"| {title} | `body/{slug}.txt` | {start + 1}–{end} | {chars:,} |\n")
    return index


def main():
    ap = argparse.ArgumentParser(
        description="Split a filed 10-K into a sectioned, citable plain-text corpus."
    )
    ap.add_argument("filing", help="path to the 10-K (Word/OOXML, HTML, or text)")
    ap.add_argument("-o", "--outdir", default="./extract", help="output directory (default: ./extract)")
    ap.add_argument("--list", action="store_true", help="print the section map and exit")
    args = ap.parse_args()

    try:
        lines = extract_lines(args.filing)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: could not read {args.filing}: {exc}", file=sys.stderr)
        return 1

    if not lines:
        print(f"error: no text extracted from {args.filing}", file=sys.stderr)
        return 1

    body_end = find_body_end(lines)
    sections = find_sections(lines, body_end)
    if not sections:
        print(
            "error: no `ITEM n.` headings found — is this a 10-K? "
            "(Check the extraction with --list.)",
            file=sys.stderr,
        )
        return 1

    total = sum(len(l) for l in lines)
    body_chars = sum(len(l) for l in lines[:body_end])
    print(f"{len(lines):,} lines / {total:,} chars extracted")
    print(f"body: lines 1-{body_end:,} ({body_chars:,} chars)")
    if body_end < len(lines):
        print(
            f"appended exhibits: lines {body_end + 1:,}-{len(lines):,} "
            f"({total - body_chars:,} chars) — excluded from the body"
        )
    print()
    for slug, title, start, end in sections:
        chars = sum(len(l) for l in lines[start:end])
        print(f"  {title:<70} lines {start + 1:>5}-{end:<5} {chars:>9,} chars")

    if args.list:
        return 0

    os.makedirs(args.outdir, exist_ok=True)
    index = write_corpus(lines, sections, body_end, args.outdir, args.filing)
    print(f"\nwrote {len(sections)} sections to {args.outdir}/body/, index at {index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
