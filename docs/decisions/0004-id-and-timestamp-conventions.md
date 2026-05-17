# 0004 — ID and timestamp conventions

## Context

`ARCHITECTURE.md` shows IDs like `D-014` (zero-padded to three digits) and timestamps like `date: 2026-04-22` (calendar date). US-P-04 explicitly requires a UTC ISO 8601 *timestamp* when a decision is recorded. We need to lock conventions before code goes out.

A related question is the YAML field name on `Decision`: the architecture example uses `decision:`, but the CLI flag is `--text`. Picking one and mapping the other is unambiguous; mixing them is not.

## Decision

**IDs.** Every canonical entity ID is `KIND-NNN`, where `KIND` is a single uppercase letter (`D` decisions, `Q` open questions, `A` action items, `G` goals) and `NNN` is the entity number zero-padded to at least three digits. Numbers grow past three digits naturally (`D-1042`). Numbers are never re-used; the next ID is `max + 1`.

**Collaborator IDs.** Kebab-case, lowercase, starts with `[a-z0-9]`, max 31 chars (`^[a-z0-9][a-z0-9-]{0,30}$`). Examples: `maria`, `lit-monitor`.

**Timestamps.** All `date` / `created` / `completed_at` fields on entities are timezone-aware UTC datetimes, serialized as RFC 3339 with a `Z` suffix (`2026-04-22T15:30:00Z`). The architecture document's example will be updated alongside this ADR.

**`due_date` exception.** `ActionItem.due_date` is a calendar `date` (no time component), since action items are tracked by day. Same on `Goal.target_date`.

**Decision field name.** The YAML field stays `decision:` (matching the architecture example). The CLI flag `--text` maps to it.

## Consequences

- The example in `ARCHITECTURE.md §State Schemas` should be updated to use the timestamp form (`2026-04-22T00:00:00Z`) for consistency; left as-is means readers see two conventions in one repo.
- A future migration to add a `time_zone` field is unnecessary — everything canonical is UTC.
- Field name mismatch between YAML (`decision`) and CLI (`--text`) is a one-line mapping in the CLI command; cost is small and self-contained.
