"""Short-lived HTTP MCP client for remote-cairn write dispatch (US-P-13).

Uses the MCP JSON-RPC-over-HTTP protocol (streamable-http transport) via
stdlib ``urllib.request`` so no extra dependencies beyond ``mcp>=1.0`` are
needed for the call itself.  Each CLI invocation opens a connection, fires
one tool call, and closes.  No long-lived session state.

Error mapping:
- Missing token           → ``RemoteAuthError``
- HTTP 401/403            → ``RemoteAuthError``
- Network unreachable     → ``RemoteNetworkError``
- Remote validation error → ``RemoteCallError`` (message forwarded)
- Unknown/unexpected      → ``RemoteCallError``
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class RemoteError(Exception):
    """Base for all remote-dispatch errors."""


class RemoteAuthError(RemoteError):
    """Authentication failed or no credentials configured."""


class RemoteNetworkError(RemoteError):
    """Could not reach the remote server."""


class RemoteCallError(RemoteError):
    """The remote server returned an error for the tool call."""


def call_tool(
    endpoint: str,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    token: str | None = None,
) -> dict[str, Any]:
    """Call *tool_name* on the MCP server at *endpoint*.

    *arguments* maps directly to the tool's parameter list.
    Returns the tool's response dict.
    Raises a ``RemoteError`` subclass on any failure.
    """
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
    ).encode()

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RemoteAuthError(
                f"authentication failed against {endpoint} (HTTP {exc.code})"
            ) from None
        # Try to read an error body.
        try:
            body = exc.read().decode(errors="replace")
        except Exception:
            body = ""
        raise RemoteCallError(
            f"HTTP {exc.code} from {endpoint}: {body[:200]}"
        ) from None
    except urllib.error.URLError as exc:
        raise RemoteNetworkError(
            f"could not reach {endpoint}: {exc.reason}"
        ) from None
    except OSError as exc:
        raise RemoteNetworkError(f"network error calling {endpoint}: {exc}") from None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RemoteCallError(
            f"unexpected non-JSON response from {endpoint}: {exc}"
        ) from None

    # Handle SSE-wrapped responses (text/event-stream with data: ... lines)
    if isinstance(data, str) or (isinstance(raw, bytes) and raw.startswith(b"data:")):
        data = _parse_sse_response(raw)

    if "error" in data:
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise RemoteCallError(f"remote error from {endpoint}: {msg}")

    result = data.get("result")
    if result is None:
        raise RemoteCallError(
            f"unexpected MCP response shape from {endpoint}: {data}"
        )

    # MCP tools/call wraps the payload under result.content[0].text (JSON string)
    # or directly as result if FastMCP serialised it flat.
    if isinstance(result, dict) and "content" in result:
        content = result["content"]
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and first.get("type") == "text":
                try:
                    return json.loads(first["text"])
                except (json.JSONDecodeError, KeyError):
                    return first
        return result
    if isinstance(result, dict):
        return result
    # Scalar or list result — wrap for uniform handling.
    return {"result": result}


def _parse_sse_response(raw: bytes) -> dict[str, Any]:
    """Extract the JSON-RPC response from an SSE data stream."""
    for line in raw.decode(errors="replace").splitlines():
        if line.startswith("data:"):
            payload = line[len("data:"):].strip()
            if payload and payload != "[DONE]":
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    continue
    raise RemoteCallError("could not parse SSE response")


def probe(endpoint: str, *, token: str | None = None, timeout: int = 10) -> bool:
    """Return True if *endpoint* is reachable (any 2xx or 4xx response).

    A 4xx means the server is up but the request was bad (auth, path) —
    still "reachable". Only network errors return False.
    """
    headers: dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(endpoint, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except urllib.error.HTTPError:
        return True  # server responded → reachable
    except (urllib.error.URLError, OSError):
        return False
