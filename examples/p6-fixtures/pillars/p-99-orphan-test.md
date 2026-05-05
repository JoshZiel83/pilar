---
artifact: pillar
pillar_id: P-99
project: aurelis-alr217-dlbcl-2026
slug: p6-fixture-orphan-test
status: draft
created: 2026-05-02
updated: 2026-05-02
---

# Pillar: P6 fixture — orphan-RS test

## Strategic Rationale

This pillar exists only as a fixture for exercising the P6 orphan-RS predicate (`scripts/detect-gaps.py`) and the auto-gap step of `/pilar:ingest-kb`. It deliberately contains reference statements with missing or unresolved sources so that the scan flags them and produces candidate `GAP-NNN` entries.

## Narrative

Synthetic fixture content. Two scientific statements; three reference statements; two of the three RS are deliberately orphan to demonstrate the two structural detection paths (empty sources list; cited ref-id that does not resolve to a manifest entry).

## Scope

In scope: detection-path fixtures only. No real scientific argument is made.

## Scientific Statements

### SS-01: Pivotal Phase 2 efficacy (fixture)

- status: draft
- created: 2026-05-02
- updated: 2026-05-02

**Statement.** Synthetic fixture statement to anchor RS detection paths.

**Strategic Argument.** Not applicable — fixture content.

**Reference Statements.**

#### RS-01: Clean RS — supported by Smith_J_2024_Synth-J-Oncol

- status: draft
- sources: [Smith_J_2024_Synth-J-Oncol]
- created: 2026-05-02
- updated: 2026-05-02

This RS cites Smith_J_2024_Synth-J-Oncol, which exists in the manifest. `detect-gaps.py` should NOT flag it.

#### RS-02: Orphan A — empty sources list

- status: draft
- sources: []
- created: 2026-05-02
- updated: 2026-05-02

This RS has an empty `sources:` list. `detect-gaps.py` should flag it with reason "empty sources list".

### SS-02: Mechanism context (fixture)

- status: draft
- created: 2026-05-02
- updated: 2026-05-02

**Statement.** Synthetic fixture statement to anchor an unresolved-REF detection path.

**Strategic Argument.** Not applicable — fixture content.

**Reference Statements.**

#### RS-01: Orphan B — unresolved ref-id in sources list

- status: draft
- sources: [Smith_J_2024_Synth-J-Oncol, Missing_X_2099_Synth-Test]
- created: 2026-05-02
- updated: 2026-05-02

This RS cites Missing_X_2099_Synth-Test, which does not exist in the manifest. `detect-gaps.py` should flag it with reason "unresolved ref-id(s): Missing_X_2099_Synth-Test".

## Open Items

- This is fixture content; do not draft against it as if it were a real pillar.
