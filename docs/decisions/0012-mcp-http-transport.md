# ADR-0012 — MCP HTTP transport and remote-cairn CLI dispatch

**Status:** accepted  
**Date:** 2026-05-21  
**Supersedes:** nothing  
**Related:** ADR-0006 (cairn.toml + endpoint placeholder), ADR-0009 (MCP v0 stdio), ADR-0010 (one server, many cairns)

---

## Context

ADR-0009 shipped the MCP server stdio-only.  ADR-0010 made one server address many cairns.  Stdio
cannot reach the topology that combination implies:

- A long-running per-machine (or per-group) MCP server, not per-session.
- Background Phase-5 agents needing a stable endpoint independent of any interactive client.
- A cairn hosted on a group box that every collaborator's Claude Code reaches without ssh-tunneling.

ADR-0006 left an `endpoint` field in `cairn.toml` as an unreached placeholder and deferred
`CairnTarget` resolution.  This ADR closes both gaps.

---

## Decision

### Three cairn.toml modes

| Mode | Fields | Resolves to |
|---|---|---|
| local-path | `path = "..."` only | filesystem path, relative to cairn.toml's directory |
| local-registry | `name = "..."` only | user registry (`~/.config/cairn/server.toml`) lookup |
| remote-MCP | `endpoint = "..."` + `name = "..."` | HTTP MCP server at `endpoint`; `name` is the cairn handle |

**Invalid combinations** (rejected with actionable errors): empty pointer; `path + name`;
`path + endpoint`; `endpoint` without `name`; all three together.

### cairn mcp HTTP transport (US-P-11)

`cairn mcp --transport {stdio,streamable-http,sse}` selects transport; default stays `stdio`
so existing setups continue unchanged.  HTTP options: `--host` (default `127.0.0.1`), `--port`
(default `8765`), `--path` (default `/mcp`).  The tool surface is identical across transports.
Invalid `--transport` values fail fast before any SDK import.

Default binding `127.0.0.1` keeps the trust surface identical to stdio for single-user setups.
Binding `0.0.0.0` is allowed but the flag's help text names the tradeoff.  No built-in auth in
this slice; operators use a reverse proxy / private-network pattern.

### Remote pairing (US-P-12)

`cairn link --endpoint <url> --name <handle>` writes a remote-mode `cairn.toml` and prints
client-neutral pairing info (endpoint + cairn name + credential setup hints).  A connectivity
probe runs before writing; `--no-probe` escapes it for offline pairing.  Credentials are never
written into `cairn.toml` and never committed.

### CLI remote dispatch + read-after-write confirmation (US-P-13)

`cairn decision add`, `cairn finding add`, `cairn action add`, `cairn action complete` detect a
remote-mode `cairn.toml` via `resolve_target()` and transparently dispatch over HTTP.

**Key design choice — echoing the resolved cairn and ID back to the CLI:** the MCP write tools
already return `{"cairn": entry.name, "id": new_id, ...}`.  The CLI prints this on every remote
write (e.g., `"Recorded D-001 in cairn 'my-cairn' at https://…"`).  This closes the blind-write
loop: if `name` in `cairn.toml` is wrong the response shows the server's resolved handle, not
the local pointer's string — making the discrepancy visible before reads land.

**Credential resolution order:** `CAIRN_BEARER_TOKEN` env var first; then
`~/.config/cairn/credentials.toml` (keyed by endpoint URL, written mode 0600).  No third source.

**Reads are out of scope for this slice.** `cairn status`, `cairn validate`, `cairn agenda draft`
against a remote-mode repo continue to error; agents handle reads through their MCP client.

### HTTP client implementation

Remote dispatch uses stdlib `urllib.request` (no extra dependency).  The MCP JSON-RPC-over-HTTP
protocol (streamable-http transport) is a simple POST with a `tools/call` JSON-RPC body.  Each
CLI invocation opens a short-lived connection, fires one tool call, closes.

### Attribution vs authentication

The `author` parameter the server validates against `state/collaborators.yaml` remains
**attribution, not authentication** — a request claiming to be `kyle` is recorded as `kyle` if
the id exists.  Binding the bearer-token holder's identity to the `author` claim is a follow-up
ADR (TLS / OIDC subject / token-to-id mapping).

---

## Consequences

- **Unchanged for existing users**: `cairn mcp` still defaults to stdio; local-mode `cairn.toml`
  files keep working; the `--name`-only form of `cairn link` is unchanged.
- **Remote-mode write commands confirm destination**: each write prints the server-resolved cairn
  name and new entity ID — mitigates the duplicate-write risk from silent failures.
- **Reads are deferred**: `cairn status` in remote mode still errors; the human must use their
  MCP client or wait for the read-side story (US-P-14, not yet filed).
- **No in-process TLS / OAuth**: operators wanting auth must front the server with a reverse
  proxy.  Future ADR binds caller identity to the `author` claim once the deployment pattern is
  known.
