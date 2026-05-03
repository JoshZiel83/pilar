---
artifact: fact-check-report
sprint: 8
project: aurelis-alr217-dlbcl-2026
created: 2026-05-02
---

# Fact-Check Report

## Scope

Reviewed the consolidated draft `cd-001` (`consolidated/cd-001.md`) at `operating_context: consolidated-draft` (the Editor's preceding pass at this context is read-only per §6.8, so the consolidated draft is byte-identical to its as-assembled state). Source files read against cited reference statements: `knowledge-base/clinical/pivotal-trial.md` (REF-001), `knowledge-base/competitor/bispecific-summary.md` (REF-002), `knowledge-base/guidelines/nccn-3l-excerpt.md` (REF-003) — the union of REFs cited across the consolidated body's reference statements.

## Findings

### FC-08-001

- target: P-04.SS-01.RS-01
- issue: The reference statement reads "the overall response rate by independent review was reported at the protocol-defined primary analysis after a median follow-up of N months in adults with r/r DLBCL who had received ≥2 prior lines of therapy." The placeholder "N months" is a drafting artifact — the source (REF-001) reports a specific median follow-up that should be filled in. Until filled, the RS is supportable in structure but does not commit to the specific value the source reports.
- severity: medium
- recommendation: Fill the median-follow-up duration from REF-001 before client delivery. The structural shape of the claim is correct; the placeholder is the only issue.

### FC-08-002

- target: P-05.SS-02
- issue: The Statement asserts that ALR-217's profile "distributes value across the framework dimensions in a pattern that prioritizes tolerability and operational fit alongside efficacy." The supporting RS-01 and RS-02 establish the tolerability and operational profile credibly against REF-001 and REF-002. The "prioritizes tolerability and operational fit alongside efficacy" framing is a defensible synthesis of the reference statements; however, "alongside efficacy" is a comparative weighting that requires the SS to also point to the efficacy evidence in P-04.SS-01. The synthesis is structurally fine but the cross-pillar dependency on P-04 should be made explicit either in the Strategic Argument or via an explicit cross-reference.
- severity: low
- recommendation: Add a one-line cross-reference in the SS-02 Strategic Argument naming P-04.SS-01 as the efficacy anchor; this preserves the synthesis while making the multi-pillar evidence base explicit.

### FC-08-003

- target: P-01.SS-02.RS-01
- issue: The reference statement reads "documented incidence rates of grade ≥2 CRS and immune effector cell-associated neurotoxicity syndrome that warrant active management." REF-002 supports the reporting of CRS and ICANS rates and the active-management framing; the strength of the source for general-population claims is appropriate to the descriptive language used here. No issues.
- severity: low
- recommendation: No action.
