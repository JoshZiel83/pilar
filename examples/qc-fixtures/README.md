# pilar QC fixtures

Self-contained test scenario for exercising the Editor and Fact-Checker subagents through `/pilar:run-qc`. Not part of any real engagement; the content is synthetic and intentionally low-fidelity.

## Layout

```
examples/qc-fixtures/
├── pillar.md            # P-99 with one SS containing one RS that has known-bad copy
├── manifest.md          # kb-manifest with one entry (Smith_J_2024_Synth-J-Oncol) pointing to the source below
├── lexicon.md           # two lexicon entries with clear avoid → preferred swaps
├── style-guide.md       # §9 defaults inherited; minimal otherwise
└── sources/
    └── Smith_J_2024_Synth-J-Oncol.txt      # synthetic source content for Smith_J_2024_Synth-J-Oncol
```

## What this fixture is designed to elicit

The RS body in `pillar.md` deliberately contains:

1. **A lexicon avoid term.** "r/r diffuse large b-cell lymphoma" (lowercase b-cell). The Editor should swap to the preferred "DLBCL" form (or "diffuse large B-cell lymphoma" with proper orthography).
2. **A §9 disallowed pattern.** Antithetical construction: "ALR-217 is not just active … it is highly effective at extending overall survival." The Editor should flag (the antithetical construction) and the Fact-Checker should flag the overstatement (Smith_J_2024_Synth-J-Oncol reports ORR only — no overall-survival data).
3. **An overstatement vs cited source.** Smith_J_2024_Synth-J-Oncol's "Limitations" section explicitly states "long-term follow-up including overall survival has not yet been reported." The RS's claim about overall survival extension is unsupported by the cited source; the Fact-Checker should flag this as `unsupported` or `overstatement`.

## How to invoke

These fixtures cannot be schema-validated end-to-end via the CI `schema-validate` job (which scans only `examples/fixtures/`). Manual invocation in a Claude Code session against this fixture set:

```
/pilar:run-qc examples/qc-fixtures/pillar.md --context drafting
```

The expected behavior is:

- Editor reads `pillar.md`, `lexicon.md`, `style-guide.md`. Applies the lexicon swap; flags the antithetical construction. Returns the two-block output.
- Parent applies edited copy to `pillar.md`; saves editorial report under `qc/editorial-reports/`.
- Fact-Checker reads the now-edited `pillar.md` plus `sources/Smith_J_2024_Synth-J-Oncol.txt`. Flags the unsupported overall-survival claim. Returns a fact-check report.
- Parent saves the fact-check report under `qc/fact-check-reports/` and surfaces both reports.

This is an interactive smoke test, not part of CI. The static `context-audit` CI job continues to gate the prompt-template allowlists and the subagent isolation contracts on every PR.
