# pilar P8 fixtures — Whole-deliverable review end-to-end

Self-contained scenario demonstrating consolidation (`/pilar:consolidate` → `scripts/consolidate.py`) and the whole-deliverable review (`/pilar:run-qc --consolidated`) running Editor + Fact-Checker + Strategic Reviewer **all read-only** per §6.7 / §6.8 of `scp-plugin-spec.md`. Synthetic content; uses the Aurelis ALR-217 / r/r DLBCL engagement defined in Appendix C of `IMPLEMENTATION_ROADMAP.md`.

## Layout

```
examples/p8-fixtures/
├── README.md                             # this file
├── briefing.md                           # full briefing per §7.2
├── lexicon.md                            # 3 entries (older patients, r/r, post-CAR-T)
├── style-guide.md                        # full style guide per §7.9 with §9 defaults
├── roadmap-excerpt.md                    # post-Sprint-7 roadmap state, current_sprint: 8
├── knowledge-base/
│   └── manifest.md                       # 3 entries (Smith_J_2024_Synth-J-Oncol, Doe_AB_2023_Synth-Lab-Med, Roe_K_2024_Synth-Clin-Oncol)
├── pillars/
│   ├── p-01-unmet-need.md                # status: statements-approved
│   ├── p-04-clinical-evidence.md         # status: statements-approved (copied verbatim
│   │                                       from examples/p7-fixtures/)
│   └── p-05-clinical-value-framework.md  # status: statements-approved
├── consolidated/
│   └── cd-001.md                         # deterministic mechanical assembly produced by
│                                           scripts/consolidate.py — byte-determined by the
│                                           pillars + briefing + lexicon + style guide;
│                                           NOT edited at the consolidated stage
└── qc/
    ├── editorial-reports/
    │   └── sprint-08-editorial-cd-001.md      # 4 ED flagged items (read-only review per §6.8)
    ├── fact-check-reports/
    │   └── sprint-08-fact-check-cd-001.md     # 1 medium + 2 low findings against cd-001
    └── strategic-alignment-reports/
        └── sprint-08-strategic-cd-001.md      # 1 high (Priority 2 under-addressed) +
                                                #   1 low + 1 medium findings
```

## What this fixture demonstrates

The fixture captures the post-state of running this command sequence (against the synthetic engagement) up through the Sprint 8 whole-deliverable review:

1. `/pilar:consolidate` (P8) shells out to `scripts/consolidate.py` to assemble `briefing.md` + the three approved pillars (P-01, P-04, P-05) + `lexicon.md` + `style-guide.md` into `consolidated/cd-001.md`. The script does the bytes deterministically — running it twice on the same inputs produces byte-identical output. The slash command handles the surrounding UX (drift warning, orphan-RS audit, commit proposal). Open `GAP-NNN`/`ASP-NNN` register entries are excluded — registers are working-state, not deliverable content.
2. `/pilar:run-qc --consolidated consolidated/cd-001.md` runs the three QC subagents in §8 / §6.8 sequence, **all read-only**:
   - **Editor** at `operating_context: consolidated-draft` reads `cd-001.md` + `lexicon.md` + `style-guide.md` (per the Independence Contract). Reports cross-pillar findings only — does not Edit. The fixture's editorial report flags four items: ED-08-001 and ED-08-002 (lexicon drift in P-04 — "elderly patients" should be "older patients" per the lexicon's `older patients` entry; two occurrences in P-04 narrative); ED-08-003 (lexicon drift in P-05 — "after CAR-T" should be "post-CAR-T" per the lexicon's `post-CAR-T` entry; three occurrences across P-05 narrative + SS-01 statement + SS-01.RS-01); ED-08-004 (style observation in P-04.SS-01 strategic argument — antithetical-adjacent "X rather than Y" construction with scientific weight on both halves; meaning-preserving rewrite requires authorial judgment). The Editor does not modify `cd-001.md` — addressing the flagged items is the writer's job, done by editing the source pillars and re-consolidating.
   - **Fact-Checker** at `operating_context: consolidated-draft` reads the consolidated `cd-001.md` + the three cited source files (Smith_J_2024_Synth-J-Oncol pivotal trial, Doe_AB_2023_Synth-Lab-Med bispecific summary, Roe_K_2024_Synth-Clin-Oncol NCCN excerpt). Files one medium-severity finding (drafting placeholder "N months" still in P-04.SS-01.RS-01) and two low-severity observations (one cross-pillar synthesis dependency note, one positive finding).
   - **Strategic Reviewer** reads `briefing.md` + `roadmap.md` + `cd-001.md` (per Appendix A withholds: no lexicon, no style guide, no source files, no Editor or Fact-Checker reports, no per-pillar progress). Files one high-severity substantive finding (Strategic Priority 2 — establishing the 3rd-line+ post-CAR-T positioning — is under-addressed across the three pillars; each pillar touches adjacent territory but none synthesizes the explicit positioning conclusion). Plus one positive finding on Priority 1 and one medium-severity balance finding on Priority 3.

The high-severity SA finding (SA-CD1-001) plus the four Editor flagged items are engineered into this fixture to exercise the §6.8 loop. In a real engagement, the writer would address them by:

1. Editing `pillars/p-04-clinical-evidence.md` to apply ED-08-001 and ED-08-002 (lexicon swaps) and consider ED-08-004 (style restructure).
2. Editing `pillars/p-05-clinical-value-framework.md` to apply ED-08-003 (three lexicon swaps).
3. Reopening P-01 or P-05 (writer's choice) to add a positioning-focused scientific statement that synthesizes P-01.SS-01, P-04.SS-01, P-04.SS-02, P-01.SS-02, and P-05.SS-02 into the explicit 3rd-line+ positioning claim that Priority 2 calls for. (SA-CD1-001 recommendation.)
4. Re-running `/pilar:consolidate` to produce `cd-002` with the corrections propagated automatically — the consolidated draft is regenerated from the now-corrected source pillars.
5. Re-running `/pilar:run-qc --consolidated consolidated/cd-002.md` to verify the loop terminates.

The fixture stops at `cd-001` and does not ship `cd-002` — the re-consolidation iteration is the writer's to perform on a real engagement; the fixture's purpose is to demonstrate the loop's first iteration and the reports that trigger it.

The architectural shift in P8: consolidation is deterministic mechanical assembly, and all three QC roles at consolidated context are read-only. This means the source pillars remain the canonical state of the engagement. Editor edits at the consolidated stage would have created drift between the canonical pillars and the deliverable view (re-consolidation would discard them or have to re-apply them); pushing all consolidated-stage corrections back to the source pillars eliminates that drift class.

## Manual smoke tests

### Validate every fixture artifact against its schema

```
python3 ../../scripts/validate-schemas.py \
  briefing.md lexicon.md style-guide.md roadmap-excerpt.md \
  knowledge-base/manifest.md \
  pillars/ \
  consolidated/cd-001.md \
  qc/editorial-reports/sprint-08-editorial-cd-001.md \
  qc/fact-check-reports/sprint-08-fact-check-cd-001.md \
  qc/strategic-alignment-reports/sprint-08-strategic-cd-001.md
```

Expected: `Validated 12 file(s); 0 error(s)`.

### Verify the consolidated draft is reproducible from the source pillars

The consolidate script is deterministic: regenerating `cd-001.md` from the same inputs should produce a byte-identical file (modulo the `created:` date and the "Assembled on" line, which use today's date).

```
python3 ../../scripts/consolidate.py --engagement-root . --draft-id cd-099 --dry-run | diff -u <(grep -v "^created:\|Assembled on" consolidated/cd-001.md) <(grep -v "^created:\|Assembled on")
```

(Approximate — exact diff comparison requires aligning the date stamps. The fixture's `cd-001.md` is pinned to the engagement-canonical date 2026-05-02 for stability.)

### Inspect the four QC outputs as a tetrad

```
cat qc/editorial-reports/sprint-08-editorial-cd-001.md
cat qc/fact-check-reports/sprint-08-fact-check-cd-001.md
cat qc/strategic-alignment-reports/sprint-08-strategic-cd-001.md
cat consolidated/cd-001.md | head -20
```

Expected: each QC report follows `schemas/{editorial,fact-check,strategic-alignment}-report.md`; the editorial report's "Edits Applied Summary" reads `0 edits applied (read-only review per §6.8)`; the editorial report's flagged items (ED-08-001..004) name pillar-level remediation in their `proposed_change` fields; the SA report's SA-CD1-001 finding identifies the Priority 2 under-addressing.

### Run context-audit to confirm the Strategic Reviewer harness

```
python3 ../../scripts/context-audit.py
```

Expected: `Context-audit: 0 error(s) across 3 harness(es)` (Fact-Checker, Editor, Strategic Reviewer all pass their independence contract).

### End-to-end exercise of the P8 commands

These fixtures cannot be exercised directly via `/pilar:consolidate` and `/pilar:run-qc --consolidated` without copying them into a fresh pilar engagement repo (those commands assume the engagement-repo cwd shape and write to `consolidated/` / `qc/` rooted there). To do that:

1. From a scratch directory, `/pilar:init` to scaffold a new engagement.
2. Copy `briefing.md`, `lexicon.md`, `style-guide.md`, the `pillars/` set, and `knowledge-base/manifest.md` into the scratch engagement at the appropriate paths. Optionally copy the source files referenced by the manifest from `examples/p6-fixtures/knowledge-base/`.
3. Update `roadmap.md` to reflect three pillars at `statements-approved` (mirroring `roadmap-excerpt.md`).
4. Run `/pilar:consolidate` — confirm it discovers the three approved pillars, surfaces a (likely empty) drift warning, runs `detect-gaps.py`, invokes `scripts/consolidate.py`, and validates the resulting `consolidated/cd-001.md`. Compare against this fixture's `consolidated/cd-001.md` — they should be byte-identical modulo the `created:` and "Assembled on" date stamps.
5. Run `/pilar:run-qc --consolidated consolidated/cd-001.md` — walk through Editor (read-only flagged items), then Fact-Checker, then Strategic Reviewer. Compare each generated report against this fixture's reports — content will differ (the QC subagents draft in real time and vary by run), but the structure and the schema-conformant frontmatter / section layout should match. Confirm `git diff consolidated/cd-001.md` is empty after the Editor step (the Editor must not modify the consolidated draft).
6. To exercise `/pilar:handoff`, first address the four Editor flagged items by editing `pillars/p-04-clinical-evidence.md` and `pillars/p-05-clinical-value-framework.md`, then address SA-CD1-001 by adding a positioning-focused SS to one of the pillars, then re-consolidate to `cd-002`, re-run `/pilar:run-qc --consolidated consolidated/cd-002.md`, then run `/pilar:handoff`. The handoff command verifies the WDR reports for `cd-002` exist, walks the user through the high-severity-findings clearance check, proposes a roadmap update, proposes a final commit, then proposes the engagement handoff git tag with explicit per-tag user authorization (per the saved release-gating policy applied analogously to engagement tags).

This is an interactive smoke test, not part of CI. The static gates (`schema-validate`, `context-audit`, `plugin-validate`) continue to enforce baseline correctness on every PR; this fixture is *not* added to CI's `schema-validate` job (which scans `examples/fixtures/` only) — same pattern as `examples/qc-fixtures/`, `examples/p6-fixtures/`, and `examples/p7-fixtures/`.
