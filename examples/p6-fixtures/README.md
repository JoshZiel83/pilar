# pilar P6 fixtures — KB Librarian smoke test

Self-contained scenario for exercising the P6 commands manually. Not part of any real engagement; the content is synthetic and intentionally low-fidelity.

## Layout

```
examples/p6-fixtures/
├── knowledge-base/
│   ├── manifest.md                      # post-ingest manifest, 3 cataloged sources
│   ├── clinical/pivotal-trial.md        # synthetic fixture source (markdown stand-in for PDF)
│   ├── competitor/bispecific-summary.md # synthetic fixture source
│   └── guidelines/nccn-3l-excerpt.md    # synthetic fixture source
├── pillars/
│   └── p-99-orphan-test.md              # P-99 with two SS containing 3 RS, two of which are orphan
└── registers/
    ├── evidence-gaps.md                 # 2 GAP entries matching the orphans (post-detect-gaps state)
    └── aspirational-statements.md       # 1 ASP entry registered against P-99.SS-01
```

## What this fixture is designed to elicit

The pillar at `pillars/p-99-orphan-test.md` deliberately contains:

1. **A clean RS** (`P-99.SS-01.RS-01`) that cites `Smith_J_2024_Synth-J-Oncol` (which exists in the manifest). `detect-gaps.py` should NOT flag this RS.
2. **Orphan A** (`P-99.SS-01.RS-02`) with `sources: []`. `detect-gaps.py` should flag this with reason `empty sources list`.
3. **Orphan B** (`P-99.SS-02.RS-01`) with `sources: [Smith_J_2024_Synth-J-Oncol, Missing_X_2099_Synth-Test]`. `detect-gaps.py` should flag this with reason `unresolved ref-id(s): Missing_X_2099_Synth-Test`.

The two GAP entries in `registers/evidence-gaps.md` represent the post-state where the writer has accepted both candidate gaps (with the Librarian-drafted `proposed_search:` filled in for each).

The single ASP entry in `registers/aspirational-statements.md` represents the post-state of running `/pilar:add-aspirational P-99.SS-01` once.

## Manual smoke tests

### Verify the orphan-RS predicate

```
python3 ../../scripts/detect-gaps.py pillars knowledge-base/manifest.md
```

Expected output: 2 orphans surfaced, with `composite_id` `P-99.SS-01.RS-02` (empty sources) and `P-99.SS-02.RS-01` (unresolved Missing_X_2099_Synth-Test). The clean RS at `P-99.SS-01.RS-01` is NOT in the output. The summary line on stderr reads `detect-gaps: scanned 1 pillar(s); manifest has 3 entries; 2 orphan(s)`.

### Validate every artifact in the fixture

```
python3 ../../scripts/validate-schemas.py \
  knowledge-base/manifest.md \
  pillars/p-99-orphan-test.md \
  registers/evidence-gaps.md \
  registers/aspirational-statements.md
```

Expected output: `Validated 4 file(s); 0 error(s)`. Note that the orphan pillar is schema-valid even though two of its RS lack adequate sources — the §7.5 schema does not require that every RS have a populated sources list (that's a content concern, surfaced by `detect-gaps.py` rather than the schema validator).

### End-to-end exercise of the slash commands

These fixtures cannot be exercised against the live `/pilar:ingest-sources` and `/pilar:add-aspirational` commands without copying them into a fresh pilar engagement repo (those commands assume the engagement-repo cwd shape). To do that:

1. From a scratch directory, run `/pilar:init` to scaffold a new engagement.
2. Copy the contents of this fixture's `knowledge-base/clinical/`, `competitor/`, and `guidelines/` source files into the corresponding subfolders of the scratch engagement's `knowledge-base/` (without copying `manifest.md`).
3. Copy `pillars/p-99-orphan-test.md` into the scratch engagement's `pillars/`.
4. Run `/pilar:ingest-sources` — confirm it proposes the same 3 manifest entries (or close), produces a manifest matching the structure of this fixture's `knowledge-base/manifest.md`, then runs the auto-gap scan and proposes the 2 orphans seen above.
5. Run `/pilar:add-aspirational P-99.SS-01` — confirm the walkthrough captures the §7.7 fields and produces an entry similar to this fixture's `registers/aspirational-statements.md`.

This is an interactive smoke test; not part of CI. The static gates (`schema-validate`, `context-audit`, `plugin-validate`) continue to enforce baseline correctness on every PR.
