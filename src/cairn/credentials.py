"""Bearer-token credential resolution for remote-MCP cairn targets.

Resolution order for a given endpoint URL:
1. ``CAIRN_BEARER_TOKEN`` environment variable (any endpoint).
2. ``~/.config/cairn/credentials.toml`` entry keyed by endpoint URL.

Credentials are never written into ``cairn.toml`` and never committed.
The credentials file is written mode 0600 on creation.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

_CREDENTIALS_FILE = Path("~/.config/cairn/credentials.toml")
_ENV_VAR = "CAIRN_BEARER_TOKEN"


def resolve_token(endpoint: str) -> str | None:
    """Return the bearer token for *endpoint*, or None if not configured.

    Checks the environment variable first; falls back to the credentials file.
    """
    env = os.environ.get(_ENV_VAR)
    if env:
        return env
    return _load_from_file(endpoint)


def _credentials_path() -> Path:
    return _CREDENTIALS_FILE.expanduser()


def _load_from_file(endpoint: str) -> str | None:
    creds_path = _credentials_path()
    if not creds_path.is_file():
        return None
    try:
        data = tomllib.loads(creds_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    endpoints = data.get("endpoints")
    if not isinstance(endpoints, dict):
        return None
    entry = endpoints.get(endpoint)
    if isinstance(entry, dict):
        return entry.get("token") or None
    return None


def store_token(endpoint: str, token: str) -> Path:
    """Persist *token* for *endpoint* in the credentials file (mode 0600).

    Returns the credentials file path.
    """
    creds_path = _credentials_path()
    creds_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing content
    existing: dict = {}
    if creds_path.is_file():
        try:
            existing = tomllib.loads(creds_path.read_text(encoding="utf-8"))  # type: ignore[assignment]
        except Exception:
            existing = {}

    if "endpoints" not in existing or not isinstance(existing["endpoints"], dict):
        existing["endpoints"] = {}
    existing["endpoints"][endpoint] = {"token": token}

    # Write as TOML manually (avoid tomli-w dep)
    lines = ["# Cairn remote-MCP credentials — do not commit.", ""]
    for ep, entry in existing.get("endpoints", {}).items():
        ep_esc = ep.replace('"', '\\"')
        tok_esc = entry.get("token", "").replace('"', '\\"')
        lines.append(f'[endpoints."{ep_esc}"]')
        lines.append(f'token = "{tok_esc}"')
        lines.append("")

    creds_path.write_text("\n".join(lines), encoding="utf-8")
    creds_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return creds_path


def missing_token_hint(endpoint: str) -> str:
    """Return a human-readable hint when credentials are not configured."""
    return (
        f"no credentials configured for {endpoint}; "
        f"set the {_ENV_VAR!r} environment variable "
        f"or add an entry to ~/.config/cairn/credentials.toml:\n"
        f"  [endpoints.\"{endpoint}\"]\n"
        f"  token = \"<your-bearer-token>\""
    )
