---
artifact: editorial-report
context: consolidated-draft
sprint: 8
project: aurelis-alr217-dlbcl-2026
created: 2026-05-02
---

# Editorial Report

## Scope

Reviewed the consolidated draft `cd-001` (`consolidated/cd-001.md`) at `operating_context: consolidated-draft`, against the engagement lexicon (`lexicon.md`) and style guide (`style-guide.md`). Per §6.8 the Editor is read-only at the consolidated stage; cross-pillar findings are reported as flagged items only and addressed by editing the source pillars and re-consolidating.

## Edits Applied Summary

0 edits applied (read-only review per §6.8). 4 items flagged.

## Items Flagged But Not Edited

### ED-08-001

- target: P-04
- category: lexicon
- issue: P-04's narrative paragraph 1 uses "elderly patients" ("Subgroup analyses, including elderly patients, support consistent activity..."). Lexicon `older patients` entry: preferred term is "older patients"; "elderly patients" is on the avoid list with rationale tied to ASH/ASCO style guidance. P-01 and P-05 use "older patients" / no "elderly" in the corresponding contexts; P-04 is the only pillar with the avoid-list variant.
- proposed_change: In `pillars/p-04-clinical-evidence.md`, replace "elderly patients" with "older patients" in the narrative section. Re-run `/pilar:consolidate` to regenerate the consolidated draft with the fix propagated.
- reason_not_edited: n/a — Editor is read-only at consolidated stage; addressed by editing source pillars per §6.8.
- severity: medium

### ED-08-002

- target: P-04
- category: lexicon
- issue: P-04's narrative paragraph 2 uses "elderly or community-treated patients" ("...may constrain access for elderly or community-treated patients..."). Same lexicon entry as ED-08-001; second occurrence within P-04.
- proposed_change: In `pillars/p-04-clinical-evidence.md`, replace "elderly or community-treated patients" with "older patients or community-treated patients". Re-consolidate.
- reason_not_edited: n/a — Editor is read-only at consolidated stage; addressed by editing source pillars per §6.8.
- severity: medium

### ED-08-003

- target: P-05
- category: cross-pillar
- issue: P-05 uses "after CAR-T" in the narrative paragraph ("Clinical value in r/r DLBCL after CAR-T comprises..."), in SS-01 statement ("Clinical value in r/r DLBCL after CAR-T is appropriately evaluated..."), and in SS-01.RS-01 reference statement ("treatment selection in r/r DLBCL after CAR-T is shaped by..."). Lexicon `post-CAR-T` entry: preferred form is the hyphenated compound; "after CAR-T" is on the avoid list. P-01 and P-04 use "post-CAR-T" consistently; P-05 is the drift.
- proposed_change: In `pillars/p-05-clinical-value-framework.md`, replace each occurrence of "after CAR-T" with "post-CAR-T" (three occurrences: narrative paragraph 1, SS-01 statement, SS-01.RS-01 body). Re-consolidate.
- reason_not_edited: n/a — Editor is read-only at consolidated stage; addressed by editing source pillars per §6.8.
- severity: medium

### ED-08-004

- target: P-04.SS-01
- category: style
- issue: P-04.SS-01 strategic argument contains "The single-arm design is hedged appropriately rather than overclaimed" — a "X rather than Y" construction adjacent to disallowed pattern 2 (antithetical "it is not X, it is Y"). Both halves of the "rather than" carry distinct scientific weight (the design *was* deliberately hedged to avoid overclaim), so a meaning-preserving rewrite requires authorial judgment about which framing best serves the strategic argument paragraph; the consolidated-context Editor is read-only and does not exercise that judgment.
- proposed_change: In `pillars/p-04-clinical-evidence.md`, consider restructuring SS-01 strategic argument to a non-antithetical form, e.g. "The single-arm design is hedged appropriately to avoid overclaim of the comparative position (see GAP-002 for the comparative-data gap)." Re-consolidate after revision.
- reason_not_edited: n/a — Editor is read-only at consolidated stage; addressed by editing source pillars per §6.8.
- severity: low
