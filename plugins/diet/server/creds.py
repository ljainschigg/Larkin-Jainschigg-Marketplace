"""creds.py — credential access for connectors, routed through secret-resolver (L3).

Connectors never read secrets from their own files or the plugin dir; they ask
the resolver by key `<domain>/<service>/<field>` (domain defaults to 'personal').

Resolver discovery (decision G — convention-based, language-agnostic contract):
  1. env SECRET_RESOLVER_SCRIPT           (explicit override)
  2. pointer file written by `secret_resolver.py install`
     at ${XDG_CONFIG_HOME:-~/.config}/health/resolver-path
  3. `import secret_resolver`             (if on PYTHONPATH)
Otherwise a clear error explains how to wire it.
"""
import importlib.util
import os

_resolver = None


def _config_dir():
    return os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "health"
    )


def _import_from(path):
    spec = importlib.util.spec_from_file_location("secret_resolver", path)
    sr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr)
    return sr


def _load_resolver():
    global _resolver
    if _resolver is not None:
        return _resolver

    candidates = []
    env = os.environ.get("SECRET_RESOLVER_SCRIPT")
    if env:
        candidates.append(env)
    pointer = os.path.join(_config_dir(), "resolver-path")
    if os.path.exists(pointer):
        try:
            candidates.append(open(pointer).read().strip())
        except OSError:
            pass
    for path in candidates:
        if path and os.path.exists(path):
            _resolver = _import_from(path)
            return _resolver

    try:
        import secret_resolver as sr  # type: ignore
        _resolver = sr
        return sr
    except Exception:
        pass

    raise RuntimeError(
        "secret-resolver not found. Run `secret_resolver.py install` (writes a pointer "
        "so tools can find it), or set SECRET_RESOLVER_SCRIPT to its path."
    )


def get(service, field, domain="personal"):
    # Read order (see CONVENTIONS §3): env var (bring-your-own) -> secret-resolver
    # -> loud error. `<SERVICE>_<FIELD>` lets a user inject a secret from their
    # own solution (1Password CLI, Vault, direnv, shell) without adopting the
    # resolver; when unset, behaviour is unchanged.
    env = os.environ.get(f"{service}_{field}".upper())
    if env:
        return env
    return _load_resolver().get_secret(f"{domain}/{service}/{field}")


def set(service, field, value, domain="personal"):
    _load_resolver().set_secret(f"{domain}/{service}/{field}", value)


def get_client(service, domain="personal"):
    """(client_id, client_secret) for an OAuth service."""
    return get(service, "client_id", domain), get(service, "client_secret", domain)


def load_tokens(service, domain="personal"):
    """Return {access_token, refresh_token, expires_at} or {} if unset."""
    rt = get(service, "refresh_token", domain)
    if not rt:
        return {}
    exp = get(service, "expires_at", domain)
    return {
        "access_token": get(service, "access_token", domain),
        "refresh_token": rt,
        "expires_at": float(exp) if exp else 0.0,
    }


def save_tokens(service, tokens, domain="personal"):
    set(service, "access_token", tokens["access_token"], domain)
    set(service, "refresh_token", tokens["refresh_token"], domain)
    set(service, "expires_at", str(tokens["expires_at"]), domain)
