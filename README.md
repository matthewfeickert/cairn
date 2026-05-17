# Cairn

> A tool and design standard for hybrid human/AI research collaboration.

Cairn defines a repository structure, file schemas, and conventions for maintaining a research group's shared project memory — designed for a world where AI agents contribute alongside humans. The substrate is a git repository; everything else (agents, indices, dashboards, MCP servers) is a layer on top that can be added or replaced without compromising the source of truth.

**Two terms to know:**

- **Cairn** (capitalized) is the framework — this repo, the Python package, the conventions.
- **a cairn** (lowercase) is an instance — one research project's repository organized following Cairn's conventions. A research group runs one cairn per project.

> **Status:** Early development. The design is documented; the Python package is being built. For the full vision, see [the design overview](docs/overview.html).

## What it enables

- **Persistent shared memory** across meetings, decisions, findings, and discussions.
- **Async contribution and recall** — collaborators (and their agents) can ask what was decided, what was discussed, and what's outstanding without sitting through the original conversation.
- **Parallel exploration** via git branches, with explicit merge proposals as a deliberate social step.
- **Uniform interface for human and AI collaborators** — same workflows, attributed identities.
- **Reproducible artifact export** into emerging community standards (ASTRA, ARA, RO-Crate).

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/overview.html](docs/overview.html) | Polished overview for sharing with colleagues |
| [docs/splash.html](docs/splash.html) | Single-page introduction |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design document — principles, components, build path |
| [USER_STORIES.md](USER_STORIES.md) | Specifications for the Python package, agent skills, and MCP server |
| [CLAUDE.md](CLAUDE.md) | Development guide for Claude Code sessions |

## Repository contents

```
cairn/
├── ARCHITECTURE.md       # design document
├── USER_STORIES.md       # testable specifications (US-P-NN, US-A-NN, US-M-NN)
├── CLAUDE.md             # development guide for Claude Code
├── figures/              # architecture diagrams (SVG)
├── docs/                 # presentation artifacts (HTML)
└── (later)
    ├── src/cairn/        # Python package source
    ├── tests/            # pytest tests, organized by user story ID
    ├── templates/        # canonical cairn template for `cairn init`
    └── pyproject.toml
```

## Roadmap

Implementation follows the [build path](ARCHITECTURE.md) in deliberate phases. The first three are the immediate focus:

- [x] Design and architecture documented
- [x] User stories defined
- [ ] **Phase 1** — Canonical cairn template (`templates/default/`)
- [ ] **Phase 1** — State schemas (Pydantic v2)
- [ ] **Phase 1** — `cairn init` CLI (US-P-01, US-P-02)
- [ ] **Phase 1** — Basic state operations (US-P-03 through US-P-06)
- [ ] **Phase 2** — Python package extensions (helpers, validators, status)
- [ ] **Phase 3** — MCP server alongside the repo
- [ ] **Phase 4** — Meeting capture (Whisper + pyannote diarization)
- [ ] **Phase 5** — AI collaborator runtime (literature monitor, etc.)
- [ ] **Phase 6** — Voice-mode meeting participant *(long-term)*

## Development

This repo is being developed with [Claude Code](https://claude.com/claude-code). When you open it in Claude Code, the agent reads `CLAUDE.md` automatically — it provides orientation, conventions, and the current phase's priorities.

**Stack:**
- Python 3.11+
- Environment: [pixi](https://pixi.sh/) (preferred), uv, or conda
- Linting/formatting: [ruff](https://docs.astral.sh/ruff/)
- Schema validation: [Pydantic](https://docs.pydantic.dev/) v2
- CLI: [Typer](https://typer.tiangolo.com/)
- Tests: [pytest](https://docs.pytest.org/)

User stories in [`USER_STORIES.md`](USER_STORIES.md) drive both implementation and tests. Each story has an ID and testable acceptance criteria — implementations should reference the relevant `US-NN` ID in code comments and commit messages.

## Related work

Cairn sits in a small but rapidly evolving ecosystem of tools and specifications for AI-assisted research provenance and reproducibility. Peer projects worth knowing:

- **[ASTRA](https://astra-spec.org)** — Agentic Schema for Transparent Research and Analysis (Lanusse & Parker, 2026, Lightcone Research). An open specification for the scientific record itself, sharing Cairn's substrate-as-specification commitment.
- **[ARA](https://github.com/Orchestra-Research/Agent-Native-Research-Artifact)** — Agent-Native Research Artifact (Liu et al., 2026). Structured layout for crystallized research outputs with provenance tags for human vs. AI contributions.
- **[RO-Crate](https://www.researchobject.org/ro-crate/)** and **[W3C PROV](https://www.w3.org/TR/prov-overview/)** — foundational standards for research artifact packaging and provenance vocabulary.

Cairn captures the *living* state of a project — the group's accumulated thinking, day-to-day. ASTRA and ARA capture *crystallized* records of specific results, structured for external review. They compose: a cairn produces ASTRA- or ARA-compliant artifacts when work is ready to share.

## License

MIT