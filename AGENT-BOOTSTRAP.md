# Agent bootstrap

> **This file is now a redirect.**
>
> The previous agent-specific bootstrap doc has been folded into the unified setup guide at [`QUICKSTART.md`](QUICKSTART.md). One doc, two readerships.

## For agents (Claude Code, etc.)

If a human pasted this file to you expecting agent-specific bootstrap instructions: **read [`QUICKSTART.md`](QUICKSTART.md) instead.** It covers the full setup flow (install with pipx, register the MCP server with Claude Code, pair a project repo, choose between starting-from-scratch and bootstrapping-from-an-existing-repo). The instructions are written so a human can follow them directly and so an agent can drive them at the user's direction.

After setup completes, the agent's ongoing posture is described in two places:

1. **The cairn's `TRACKING.md`** — capture eagerly during conversation; debrief at end-of-block; two paths (MCP-first, CLI-fallback) for invoking cairn operations.
2. **The MCP server's session-start instructions** — orient the agent to cairn's facilitator-not-stenographer role, the four canonical entity types (decisions, findings, open questions, action items), and the bootstrap workflow.

## For humans

`QUICKSTART.md` is the place. This file exists to prevent broken links from older docs that referenced AGENT-BOOTSTRAP.md.

## Historical note

In earlier versions of cairn, agent bootstrap and human-driven install were separate flows because the MCP server didn't yet exist and the agent had to walk a noticeably different sequence of CLI commands. With the MCP server shipped (ADR-0009 + ADR-0010) and `cairn register --init` collapsing the scaffold-then-register step, the two flows converged. Keeping one canonical document means one source of truth for the install story.
