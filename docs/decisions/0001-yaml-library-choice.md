# 0001 — YAML library: ruamel.yaml for writes, pyyaml for reads

## Context

State files in a cairn are intended to be hand-edited by researchers. Comments, blank lines, and key ordering carry meaning — a contributor might leave a `# revisit after April meeting` next to a question, or list collaborators in a particular order. A naive read-modify-write loop that strips these would erode the substrate over time, in a way that wouldn't show up as a schema violation but would degrade the file's value to humans.

pyyaml is the standard, fast, ubiquitous YAML library. It does not preserve comments or ordering on round-trip. ruamel.yaml does preserve them, at the cost of more complex API surface and slower parsing.

## Decision

Use **ruamel.yaml** for writes (commands that modify a state file) and **pyyaml** for reads (validation, status, queries that don't write). The two libraries co-exist in the project; conversion happens at the read/write boundary.

## Consequences

- Two YAML dependencies instead of one. Acceptable.
- Comments and ordering survive `cairn collaborator add`, `cairn decision add`, etc.
- Tests must verify comment preservation when those commands are extended later.
- A future contributor who wants to consolidate on one library can pick ruamel.yaml; the read side will get marginally slower but feature-compatible.
