# 0002 — Git library: GitPython

## Context

The package needs to init a git repo, resolve the invoking user's identity, and commit files with explicit authorship. Two reasonable options: **GitPython** (pure-Python, shells out to the `git` binary) and **pygit2** (libgit2 bindings, native code).

pygit2 has faster object access and direct index manipulation, but its libgit2 dependency complicates `pip install` on fresh systems (especially minimal containers without a system libgit2 package). Phase 0/1 does small numbers of commits; speed is not the constraint.

## Decision

Use **GitPython** for Phase 0/1. The user already has `git` on PATH (the substrate is git); this library just wraps it.

## Consequences

- Hard dependency on the `git` binary at runtime. Acceptable — a cairn without `git` would be nonsensical.
- If MCP server work (Phase 3) needs fast index reads or bulk object access, revisit and consider pygit2 then. The git operations in this codebase are isolated to `src/cairn/git_ops.py`; switching is a one-module change.
- `cairn init` fails clearly when global git config has no `user.email` (see ADR-0004 / `git_ops.get_user_identity`).
