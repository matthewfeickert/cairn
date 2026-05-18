# Open design questions

This file holds **unresolved design tensions** for the Cairn framework — questions that have been deliberately surfaced but not yet decided. It's the companion to `docs/decisions/`: that directory holds resolved choices (ADRs); this file holds the open ones, so they don't get lost in conversation.

Each entry includes the tension, the options considered, and (where relevant) what's blocking a decision. When an open question is resolved, it migrates to a new ADR and gets removed (or stubbed with a forward-pointer) from this file.

---

## OQ-1 — Where do project design documents live?

**Tension.** When an agent (or human) writes a design document for a project — a rationale for a method choice, a comparison of alternatives, an RFC-style proposal — should it live in:

1. **The cairn**, under `explorations/<owner>/<slug>.md` (paired with a cairn exploration), or
2. **The project repo**, under `docs/design/` (or wherever the project keeps documentation), or
3. **Hybrid**: design doc lives in the cairn; a one-line pointer file is committed to the project repo at `docs/design/<name>.md` saying *"Decision rationale lives at `<cairn>/explorations/<owner>/<slug>.md`. See cairn for full context."*

**Pros / cons.**

| | Pros | Cons |
|---|---|---|
| **In cairn** *(today's default)* | Project repo stays clean; dev-process artifacts (rejected alternatives, design exploration) don't pollute production tree; cairn remains the sole substrate for "thinking" | Provenance is split — a future reader of the project repo in isolation won't see why a choice was made; a fork of the project repo without the cairn is missing context |
| **In project repo** | Provenance colocated with code; project repo is self-contained; matches conventional `docs/design/` patterns; doesn't violate US-P-10 if the user opts in | Mixes dev-process / pre-decision exploration with project's released artifacts; partly defeats cairn's reason to exist (keeping work-in-progress out of the code repo) |
| **Hybrid (pointer file)** | Provenance discoverable from project repo without dragging the conversation in; cairn keeps the bulk; project repo stays clean *and* self-contained-enough | Two files to maintain (cairn + pointer); pointer can rot if cairn moves; requires `cairn link` to know where to write pointers; opt-in friction |

**Live evidence.** During the StellaForge UX experiment, an agent's first auto-proposed action item after closing a cairn exploration was *"move the design doc from `explorations/kyle/docker-hub-submission-design.md` into `StellaForge/docs/external-submissions.md` once the branch closes."* That's the user (or the agent) doing the migration step manually because option (1) forces it. The hybrid in (3) would eliminate the migration step.

**Status.** Open. Probably resolves with a new ADR after the next round of UX testing, ideally one that exercises both options on the same project. Connected to OQ-3 below (the broader project-repo file convention question).

---

## OQ-2 — Structured project-repo references on cairn entities

**Tension.** Today, when a decision, finding, or action references "work done in commit X of the project repo" or "feature branch Y of the project repo", that reference lives in free-form prose. The cairn has no structured field for project-repo SHAs or branch names. US-P-10 explicitly deferred this: *"Format is free-form markdown; structured cross-referencing (decisions → repo + commit SHA, findings → file in a repo) is future work and out of scope for this story."*

**Sub-questions to resolve when this is picked up:**

- **Which entities carry the ref?** Decisions, actions, and findings benefit (they reference implementation moments). Goals and open questions probably don't.
- **What's the ref shape?**
  - Bare SHA — durable but opaque.
  - `<repo-name>@<sha>` — handles multi-repo projects per US-P-10's "Related repositories" list.
  - Richer `{repo: foo, sha: abc123, branch: feat/x, path: src/...}` — most useful, biggest schema cost.
  Probably the right answer: `<repo>@<sha>` as a single string, with optional `branch` and `path` on entities that benefit. All optional.
- **Staleness.** Branch names move; SHAs survive rebase only if recorded post-merge. Recommendation when this lands: encourage capturing the SHA *of the merge commit on the project's default branch*, not in-flight SHAs that may get squashed away. Both branch name and SHA optional.

**Why must be optional.** A cairn for a paper-writing project may have no associated code repo at all. A cairn paired with multiple repos needs to disambiguate. Single optional field with sensible normalization is the right default — never required.

**Status.** Open, deferred. Likely an ADR once US-P-11 (retroactive backfill skill, see below) lands and we have a working version of "agent surveys project repo → writes to cairn" that would naturally use such refs.

---

## OQ-3 — Should the agent ever hand-edit cairn files vs always go through the CLI?

**Tension.** Today's implicit principle is split by file type:

| File type | Edit how? | Why |
|---|---|---|
| `state/*.yaml` (decisions, actions, etc.) | **Always via CLI.** Direct edit bypasses schema validation, attribution, and the auto-commit. | Substrate invariants |
| `knowledge/findings/*.md` | Via `cairn finding add` for new ones. Editing existing ones in-place is fine; agent should explicitly `git add && git commit`. | Frontmatter / attribution |
| `knowledge/meetings/*.md` | Same as findings (when meeting-import ships, US-P-07). | Same |
| `PROJECT.md`, `README.md`, `TRACKING.md`, `explorations/*.md` | **Direct edit is fine** — no schema. The agent should run `git add` + `git commit` with a short message so attribution flows through git. | Free-form prose |
| `.cairn` marker | **Don't edit.** Managed by `cairn init` / `cairn validate --fix`. | Marker invariant |

**Why this is an open question.** The principle is reasonable but not written down anywhere agents or contributors are guaranteed to read. The StellaForge UX experiment surfaced an agent quietly editing `PROJECT.md` directly without anyone (or the doc) telling it whether that was the right thing to do. The agent guessed correctly, but the guess could have gone the other way.

**Sub-questions when this is picked up:**

- Does this belong in TRACKING.md (the posture guide), AGENT-BOOTSTRAP.md ("What you should not do" section), or both?
- For free-form markdown edits, should the agent commit as it goes or batch at session end? Today's bootstrap is silent. Heuristic: commit-as-you-go for substantive changes (PROJECT.md overhaul), batch trivial wording tweaks into a single commit. Worth specifying.
- Is there a case for a `cairn project edit` command for PROJECT.md? Probably not — wrapping free-form prose in a CLI loses what makes it free-form. But worth naming the alternative explicitly so future contributors don't reinvent it.

**Status.** Open. Resolves with a TRACKING.md update + a one-line pointer in AGENT-BOOTSTRAP.md's "What you should *not* do" section. Targeted for PR R3 (the AGENT-BOOTSTRAP + skills rewrite).

---

## OQ-4 — User-story for retroactive cairn population from project artifacts

**Tension.** Today's user stories cover *forward* capture — an agent listens during ongoing work and writes notes into the cairn. They do not cover *retroactive* backfill — "fill in collaborators, decisions, findings from this project's existing README, docs, git log, release notes." US-P-10's bootstrap-time PROJECT.md pre-population is close but doesn't generalize to ongoing backfill after bootstrap.

The StellaForge UX experiment exercised exactly this workflow: an agent surveyed the StellaForge repo's README, code, and git history and populated the cairn with 16 captures (3 collaborators, 4 goals, 6 decisions, 6 open questions, 4 findings) in a single batched proposal. The acceptance criteria for the workflow are now empirically defined.

**Sub-questions when this is picked up:**

- US number: US-A-11 (next agent story slot) seems right.
- Skill name: `seed` reads more naturally than `backfill`; other options `archaeology`, `retro-debrief`. Probably `seed`.
- Bundled or post-install? The skill ships in `templates/default/skills/seed/SKILL.md` so it's available immediately. Once ADR-0006 Stage 3 lands, it becomes a real `/seed` slash command.
- Acceptance criteria: locked to the StellaForge run's outcome (3/4/6/6/4/0 captures, all-attributable commits, `cairn validate` exit 0) as the demonstrated baseline.

**Status.** Open, but the design is largely understood. Targeted for PR S2 (Stage 2 `cairn link` work, since the skill depends on the project-repo / cairn pairing the link command creates). Will be added to USER_STORIES.md as part of that PR.

---

## How to add a new open question

When you encounter a design tension that isn't ready to resolve:

1. Add a new section here, numbered `OQ-N`, with a short title.
2. Describe the tension in 1–3 sentences.
3. Lay out the options (a table works well, with pros/cons per option).
4. Note any live evidence — real UX testing observations, agent transcripts — that bears on the question.
5. Mark **Status: Open** and (if known) what's blocking a decision or which PR would land the resolution.

When the question resolves: write an ADR in `docs/decisions/`, remove the section from this file (or leave a one-line forward-pointer for a few weeks).
