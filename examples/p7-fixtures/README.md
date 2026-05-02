# pilar P7 fixtures — Per-pillar development end-to-end

Self-contained scenario demonstrating a pillar driven from the scaffolding proposal through `status: statements-approved`. Synthetic content; uses the Aurelis ALR-217 / r/r DLBCL engagement defined elsewhere in the fixtures.

## Layout

```
examples/p7-fixtures/
├── README.md                          # this file
├── roadmap-excerpt.md                 # the post-scaffold-pillars ## Pillars table
└── pillars/
    └── p-04-clinical-evidence.md      # P-04 at status: statements-approved
                                       #   - narrative + scope drafted
                                       #   - 2 SS, 4 RS total
                                       #   - sources cite REF-001..003 from
                                       #     examples/p6-fixtures/knowledge-base/manifest.md
```

## What this fixture demonstrates

The `pillars/p-04-clinical-evidence.md` file is the post-state output of these three commands run in sequence (against the synthetic engagement):

1. `/pilar:scaffold-pillars` produces the five-pillar default set; P-04 ("Clinical Evidence") is one of them, written as a stub at `status: draft`.
2. `/pilar:pillar-narrative P-04` populates the `## Strategic Rationale`, `## Narrative`, and `## Scope` sections from briefing context (Strategic Priorities 1 and 3, audiences, indication), with cross-pillar consistency checks against the rest of the proposed set. The user marks the narrative approved at the end of the command. Status moves `draft` → `narrative-approved`.
3. `/pilar:pillar-statements P-04` drafts two scientific statements (SS-01 Pivotal Phase 2 efficacy; SS-02 Tolerability) and four reference statements (RS-01 / RS-02 under each SS), sourcing each RS against `REF-001`, `REF-002`, and `REF-003` from the P6 fixture manifest. After drafting, `scripts/detect-gaps.py` runs against the pillar to check for orphans (none in this fixture — every RS cites a manifest-resolvable REF). The user marks statements approved. Status moves `narrative-approved` → `statements-approved`.

In a real engagement, `/pilar:run-qc <pillar-path> --context drafting` would have run between Steps 2 and 3 (Editor on the narrative) and at the end of Step 3 (Editor + Fact-Checker on the SS/RS) per §6.5 / §8 sequencing — that QC pass is captured by the existing P5 capability, not this fixture.

## Manual smoke tests

### Validate the fixture pillar against the schema

```
python3 ../../scripts/validate-schemas.py pillars/p-04-clinical-evidence.md
```

Expected: `Validated 1 file(s); 0 error(s)`.

### Run detect-gaps against the fixture pillar + the P6 fixture manifest

```
python3 ../../scripts/detect-gaps.py pillars ../p6-fixtures/knowledge-base/manifest.md
```

Expected: `0 orphan(s)`. Every RS in this fixture cites at least one manifest-resolvable REF (REF-001, REF-002, or REF-003).

### End-to-end exercise of the P7 commands

These fixtures cannot be exercised directly via `/pilar:scaffold-pillars`, `/pilar:pillar-narrative`, and `/pilar:pillar-statements` without copying them into a fresh pilar engagement repo (those commands assume the engagement-repo cwd shape and write to `pillars/` / `roadmap.md` / `lexicon.md` rooted there). To do that:

1. From a scratch directory, `/pilar:init` to scaffold a new engagement.
2. Run the briefing sprint until `briefing.md` is populated with the Aurelis ALR-217 content (or copy `examples/p6-fixtures/`-style briefing content directly).
3. Copy the P6 fixture manifest + sources into the scratch engagement's `knowledge-base/`.
4. Run `/pilar:scaffold-pillars` — confirm the proposed default set surfaces, refine if desired, approve. Pillar stubs land at `pillars/p-NN-<slug>.md`; `roadmap.md` `## Pillars` section is populated.
5. Run `/pilar:pillar-narrative P-04` — confirm the briefing-grounded drafting flow, approve at end. Status → `narrative-approved`.
6. Run `/pilar:pillar-statements P-04` — walk through SS/RS drafting; the manifest's REF entries should surface as candidate sources. Approve at end. Status → `statements-approved`.
7. Compare the resulting `pillars/p-04-clinical-evidence.md` against this fixture's version — content will differ (drafting is conversational and varies by writer), but the structure and the schema-conformant frontmatter / SS/RS layout should match.

This is an interactive smoke test, not part of CI. The static gates (`schema-validate`, `context-audit`, `plugin-validate`) continue to enforce baseline correctness on every PR; this fixture is *not* added to CI's `schema-validate` job (which scans `examples/fixtures/` only) — same pattern as `examples/qc-fixtures/` and `examples/p6-fixtures/`.
