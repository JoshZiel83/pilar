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

Synthetic fixture content. Two scientific statements; three reference statements; two of the three RS are deliberately orphan to demonstrate the two structural detection paths (empty sources list; cited REF that does not resolve to a manifest entry).

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

#### RS-01: Clean RS — supported by REF-001

- status: draft
- sources: [REF-001]
- created: 2026-05-02
- updated: 2026-05-02

This RS cites REF-001, which exists in the manifest. `detect-gaps.py` should NOT flag it.

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

#### RS-01: Orphan B — unresolved REF in sources list

- status: draft
- sources: [REF-001, REF-999]
- created: 2026-05-02
- updated: 2026-05-02

This RS cites REF-999, which does not exist in the manifest. `detect-gaps.py` should flag it with reason "unresolved REF(s): REF-999".

## Open Items

- This is fixture content; do not draft against it as if it were a real pillar.
