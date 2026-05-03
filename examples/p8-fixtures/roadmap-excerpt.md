---
artifact: roadmap
project: aurelis-alr217-dlbcl-2026
client: Aurelis Therapeutics
product: ALR-217
indication: Relapsed/refractory diffuse large B-cell lymphoma post-CAR-T
lifecycle_stage: Post-Phase 2 / pre-launch ~18 months
created: 2026-05-02
updated: 2026-05-02
current_sprint: 8
---

# Roadmap

## Engagement Summary

Scientific Communication Platform development for Aurelis Therapeutics' ALR-217 in r/r DLBCL post-CAR-T. Five-pillar default set scaffolded; three pillars (P-01, P-04, P-05) are at `status: statements-approved` and have been consolidated into `cd-001` for whole-deliverable review. P-02 and P-03 remain at `narrative-approved` (deferred to a follow-on sprint at the user's choice; this fixture excerpt reflects the consolidation entered with three pillars approved).

## Strategic Priorities

1. Differentiate ALR-217 from emerging bispecific antibodies on convenience, sequencing flexibility, and tolerability in older patients.
2. Establish ALR-217's optimal positioning in the 3rd-line and beyond setting given the post-CAR-T treatment landscape.
3. Communicate the safety profile credibly to community oncologists, including practical management of expected adverse events.

## Status

Sprint 8 in flight: consolidated `cd-001` and ran the whole-deliverable review (Editor → discrete editorial commit → Fact-Checker → Strategic Reviewer per §6.8). The Strategic Reviewer flagged one substantive finding against Strategic Priority 2; the planned follow-on sprint will reopen P-04 and P-05 to address it, then re-consolidate to `cd-002`.

## Pillars

| pillar_id | slug | status |
|---|---|---|
| P-01 | unmet-need | statements-approved |
| P-02 | disease-mechanism | narrative-approved |
| P-03 | mechanism-of-action | narrative-approved |
| P-04 | clinical-evidence | statements-approved |
| P-05 | clinical-value-framework | statements-approved |

## Active Workstreams

- Sprint 8: whole-deliverable review on `cd-001` (in progress).
- P-02 and P-03 statement drafting deferred to a follow-on sprint after `cd-001` clears.

## Anticipated Inputs

- Long-term follow-up readout of the pivotal Phase 2 study (ETA ~12 months post-engagement open).
- Real-world evidence study interim analysis (ETA ~18 months).
- Investigator-initiated trial in elderly subgroup (first-patient-in TBD).

## Sprint History

- Sprint 1: briefing.
- Sprint 2: KB initial intake (REF-001..003).
- Sprint 3: scaffolding recommendation (5-pillar set).
- Sprint 4: P-04 narrative + statements drafted; P-04 → statements-approved.
- Sprint 5: P-01 narrative + statements drafted; P-01 → statements-approved.
- Sprint 6: P-02 / P-03 narratives drafted; P-02 / P-03 → narrative-approved.
- Sprint 7: P-05 narrative + statements drafted; P-05 → statements-approved.
- Sprint 8: consolidated `cd-001` + whole-deliverable review (in progress).

## Next Sprint Scope

- Reopen P-04 and P-05 to address Strategic Priority 2 under-addressing finding from `cd-001` SA report.
- Re-consolidate to `cd-002`.
- Re-run `/pilar:run-qc --consolidated consolidated/cd-002.md`.
- Continue P-02 and P-03 to `statements-approved` in a parallel or follow-on sprint per user's choice.

## Decisions Log

| Date | Decision | Rationale | Phase / spec § |
|---|---|---|---|
| 2026-05-02 | Consolidate at three pillars approved rather than waiting for all five. | Allows the WDR loop to begin on the strategically central pillars (P-01 unmet need, P-04 clinical evidence, P-05 value framework) while P-02/P-03 (background pillars) finish independently. | §6.7, P8 |
