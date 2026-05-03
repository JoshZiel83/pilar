---
artifact: style-guide
project: aurelis-alr217-dlbcl-2026
source: developed
updated: 2026-05-02
---

# Style Guide

## Voice and Tone

Dry scientific register throughout. Audiences include practicing hematologist-oncologists and academic key opinion leaders, both of whom expect publication-style exposition; payer and P&T audiences receive the same register with additional contextualization rather than a softer register.

## Sentence Construction

Sentences may be long where the science is dense; short for short's sake is disallowed (see Disallowed Patterns 4). Paragraph structure follows the standard publication convention: topic sentence, evidence, qualification.

## Disallowed Patterns

The following patterns are disallowed by default in pilar drafted copy. They codify the dry-scientific-register requirements in §9 of the natural-language spec. The Editor enforces these defaults when running on drafted artifacts. Clients may override individual patterns via the **Overrides** subsection below; an override must specify *which pattern* and *why*.

1. **Em dashes used for rhythmic effect.** Em dashes are permitted only for genuine parenthetical insertions, not for stylistic pacing.
2. **Antithetical constructions of the form "it is not X, it is Y".** Disallowed regardless of whether X and Y are factually accurate. The construction is rhetorical, not scientific.
3. **Sentence-initial conjunctions used for rhetorical pacing.** "But," "And," "So," at sentence start are not allowed for emphasis. Internal conjunctions are unaffected.
4. **Short punchy sentences used for emphasis.** Single-clause stylistic punches that interrupt scientific exposition.
5. **Hedging phrases that soften factual claims without scientific reason.** Hedging is permitted — required, even — when it reflects genuine evidentiary uncertainty. Hedging without that justification is not.
6. **Marketing-register adjectives.** "Robust," "compelling," "groundbreaking," "transformative," "best-in-class," "novel," and similar register markers.
7. **First-person plural framing of the science.** "We see…", "Our data show…" — the science is the subject, not the speakers.
8. **Rhetorical questions.** Particularly in introductory or transitional positions; also disallowed inline.

### Overrides

No client overrides yet.

## Citation Conventions

Vancouver style for the platform's reference list. Inline citations as `[REF-NNN]` during pilar drafting; translation to Vancouver-numbered superscripts is downstream of pilar (§11). Congress abstracts cited with year and abstract number; peer-reviewed publications cited with full author list (or first author + et al if >6 authors), journal, year, volume, pages.

## Evidence Description Conventions

Study design named explicitly (single-arm Phase 2; randomized Phase 3; retrospective real-world cohort) on first invocation per pillar. Primary endpoints distinguished from exploratory or secondary endpoints. Numerical results reported with confidence intervals; medians with ranges. Hedging language calibrated to evidence strength: single-arm data warrant cross-trial-comparison cautions; descriptive comparisons across non-randomized studies are not framed as comparative effectiveness.

## Other

The platform deliberately limits cross-trial numerical comparisons to descriptive context per the Evidence Description Conventions above. Quantitative comparisons across single-arm studies are not made; the platform may flag where such comparisons would be inappropriate.
