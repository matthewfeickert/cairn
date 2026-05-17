# 0003 — Template engine: bundled Jinja2 renderer, optional cookiecutter for URLs

## Context

US-P-02 requires `cairn init --template <path-or-url>` to accept both local paths and cookiecutter URLs. Two extremes:

1. Depend on the `cookiecutter` library at runtime for everything — including the common no-template `cairn init` case. Drags in extra deps and prompts UX we don't control.
2. Implement everything ourselves, including HTTP/git fetching for URLs. Re-invents most of what cookiecutter already does well.

## Decision

Split the responsibility:

- **Bundled default template** lives at `templates/default/` and uses cookiecutter's directory + variable convention (`{{cookiecutter.project_name}}/...`, `cookiecutter.json`).
- **Local-path rendering** (default template and `--template <local-path>`) is handled by our own Jinja2-based renderer in `src/cairn/template/render.py`. No runtime dependency on cookiecutter.
- **URL-based rendering** (`--template <url>`) shells out to the `cookiecutter` library, imported lazily. The dependency lives in the optional `cookiecutter` extra (`pip install cairn[cookiecutter]`). A missing extra produces a clear actionable error.

## Consequences

- We commit publicly to the cookiecutter variable-naming convention forever (`{{cookiecutter.foo}}`). That's already the de facto standard for template repos.
- The base `pip install cairn` stays small — no `cookiecutter` subdependencies (requests, jinja2-time, click, …).
- Custom local templates from users must follow the cookiecutter convention. Documented in `README.md` of the rendered project.
- A future contributor who finds the duplication grating can collapse both paths onto the cookiecutter library by making the `cookiecutter` extra required. Cost: ~10 extra subdependencies in the base install.
