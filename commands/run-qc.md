---
description: Run QC on a pilar artifact — Editor first, then Fact-Checker (per §8 sequencing); Strategic Reviewer ships with Phase 8
argument-hint: <artifact-path> [--context drafting|consolidated-draft]
allowed-tools: Read, Write, Task
---

Run the Editor and Fact-Checker subagents against the pilar artifact at the path supplied in `$ARGUMENTS`. The Editor runs first, applies meaning-preserving edits to the artifact body, and produces an editorial report; the Fact-Checker then runs against the post-Editor artifact and produces a fact-check report. This sequencing is the §8 mandate ("The Editor runs before the Fact-Checker so that the Fact-Checker reviews the edited copy") and is enforced by this command's logic per load-bearing decision #3.

Strategic Reviewer engagement is out of scope for this command (it engages only at consolidated-draft *whole-deliverable* review per §6.8); it ships with Phase 8.

## Procedure

### Step 1 — Parse arguments

Parse `$ARGUMENTS`:

- First positional argument: the artifact path (required).
- Optional flag: `--context <drafting|consolidated-draft>` (default: `drafting`).

If no positional argument, **stop** and tell the user the usage: `/pilar:run-qc <artifact-path> [--context drafting|consolidated-draft]`.

Capture `artifact_arg`, `operating_context`. The default for `operating_context` is `drafting`.

### Step 2 — Read the artifact and resolve engagement state

Read the artifact at `artifact_arg`. Capture:

- `artifact_path` — the absolute path of the artifact file (use `!realpath`).
- `artifact_id` — derived from frontmatter:
  - For pillars: `pillar_id`.
  - For scientific or reference statements (which only appear inside a pillar): the parent pillar's `pillar_id` plus the SS / RS id chain (e.g. `P-04.SS-01.RS-02`).
  - For other artifact types (rare for `/pilar:run-qc`): use the artifact's `project` value.
- The artifact's frontmatter and body, separated by the closing `---` line. The parent **must preserve frontmatter byte-identically** when writing back the edited body.
- `sources` — the union of `sources:` lists from all reference-statement blocks in the body (e.g. `[REF-001, REF-005]`).

Locate the engagement's lexicon and style guide:

- `lexicon_path` — absolute path to `lexicon.md` at the engagement repo root.
- `style_guide_path` — absolute path to `style-guide.md` at the engagement repo root.

If either is missing, **stop** — the engagement appears under-scaffolded; recommend `/pilar:init` or check that the user is at the engagement repo root.

### Step 3 — Invoke the Editor subagent

Use the **Task** tool with `subagent_type: editor` and a prompt produced by substituting the named variables below into this exact template, and **only** this template. Do not add any additional context from your session, the briefing, the roadmap, drafting rationale, prior sprint summaries, the KB manifest, source files, or other pillars (except as the artifact itself contains them in `consolidated-draft` context).

```
<<<PILAR_EDITOR_PROMPT
OPERATING CONTEXT: {operating_context}

ARTIFACT UNDER REVIEW (id: {artifact_id}):
path: {artifact_path}

ENGAGEMENT LEXICON:
path: {lexicon_path}

ENGAGEMENT STYLE GUIDE:
path: {style_guide_path}

Per the Independence Contract, you may Read only the four paths above. Apply permitted edits to the artifact body; flag items that would require changing meaning. Emit the two-block output (## EDITED COPY + ## EDITORIAL REPORT) per your system prompt.
PILAR_EDITOR_PROMPT>>>
```

Substitutions:

- `{operating_context}` — the value from Step 1.
- `{artifact_id}` — captured in Step 2.
- `{artifact_path}` — captured in Step 2.
- `{lexicon_path}` — captured in Step 2.
- `{style_guide_path}` — captured in Step 2.

The variables `{operating_context}`, `{artifact_id}`, `{artifact_path}`, `{lexicon_path}`, and `{style_guide_path}` are the **complete and exhaustive** set of inputs the parent is permitted to pass into the Editor's context. The static context-audit test in `scripts/context-audit.py` enforces this allowlist.

### Step 4 — Parse the Editor's output

The Editor returns text containing two H2 blocks:

- `## EDITED COPY` — followed by the full edited body (starting with the artifact's H1 line). This is the new body.
- `## EDITORIAL REPORT` — followed by a YAML+markdown editorial-report document (with its own `---` frontmatter and H1).

Extract both blocks. If either is missing, malformed, or empty, **stop** and surface the Editor's raw output to the user; do not modify the artifact file. (This protects the artifact from corruption if the Editor's output drifts off-spec.)

### Step 5 — Apply the edited body to the artifact

Construct the new artifact file content:

```
<original frontmatter, byte-identical>
<the body extracted from ## EDITED COPY>
```

Show the user a `git diff` of the proposed change. If the diff is non-trivial, briefly summarize the change categories (e.g. "5 lexicon swaps, 2 §9 pattern removals").

Use **Write** to overwrite the artifact file with the new content. Per decision #4, do **not** auto-commit.

### Step 6 — Save the editorial report

Compute the report filename: `qc/editorial-reports/sprint-<NN>-editorial-<slug>.md` where `<NN>` is `roadmap.md::current_sprint` zero-padded and `<slug>` is the artifact's id lowercased with dots → hyphens (e.g. `P-04.SS-01` → `p-04-ss-01`).

Write the editorial-report content (extracted in Step 4) to that path.

Validate it: `!python3 scripts/validate-schemas.py qc/editorial-reports/sprint-<NN>-editorial-<slug>.md`. If validation fails, surface the errors to the user but continue (the report is still useful as content).

### Step 7 — Discrete editorial commit (consolidated-draft context only)

If `operating_context == consolidated-draft`, per §6.8 the Editor's edits are committed in a discrete commit before the Fact-Checker runs, so the editorial diff is inspectable. Show the user `git status` and propose:

```
chore(pilar): editorial pass on consolidated draft <draft-id> — <artifact-id>

Editor pass at consolidated-draft context. <one-line summary of edit
categories and counts>. Change log captured at the editorial-report
path; Fact-Checker runs next on the edited artifact.
```

Wait for explicit user approval. On approval: `git add <artifact-path> qc/editorial-reports/<filename>` and commit. If the user rejects or defers, **stop** before invoking Fact-Checker (the user can resume later by re-running `/pilar:run-qc` with the same args; Editor will idempotently re-apply on the now-edited copy).

If `operating_context == drafting`, **skip this step** — drafting context does not gate Fact-Checker on a discrete editorial commit (§6.8 footnote: drafting checkpoint reviewer reviews edited copy fresh).

### Step 8 — Resolve cited source paths

For each ref-id in `sources` (collected in Step 2), look up the source file via `knowledge-base/manifest.md`:

- Find the manifest entry whose heading matches the ref-id (e.g. `### REF-001`).
- Read the `file:` path; resolve to absolute.
- Verify the file exists.

Collect the union as `source_paths` — a list of absolute paths ordered to match the artifact's RS source ordering. For unresolved sources, include `MISSING:<REF-NNN>` as a placeholder string at the corresponding position (the Fact-Checker treats these as gap findings).

### Step 9 — Invoke the Fact-Checker subagent

Use the **Task** tool with `subagent_type: fact-checker` and a prompt produced by substituting the named variables below into this exact template, and **only** this template.

```
<<<PILAR_FACT_CHECKER_PROMPT
OPERATING CONTEXT: {operating_context}

ARTIFACT UNDER REVIEW (id: {artifact_id}):
path: {artifact_path}

CITED SOURCE FILES:
paths: {source_paths}

Per the Independence Contract, you may Read only the artifact at the path above and each source at the listed paths. Produce a fact-check report per §7.10 of scp-plugin-spec.md.
PILAR_FACT_CHECKER_PROMPT>>>
```

Substitutions:

- `{operating_context}` — the value from Step 1.
- `{artifact_id}` — captured in Step 2 (unchanged across the Editor's pass; the artifact's frontmatter `pillar_id` etc. were not modified).
- `{artifact_path}` — same as Step 3 (the file is now the post-Editor version).
- `{source_paths}` — the list captured in Step 8 formatted as YAML-style inline list.

### Step 10 — Save the fact-check report and surface both

Save the Fact-Checker's returned report to `qc/fact-check-reports/sprint-<NN>-fact-check-<slug>.md`. Validate with `!python3 scripts/validate-schemas.py qc/fact-check-reports/sprint-<NN>-fact-check-<slug>.md`.

Print both reports (editorial + fact-check) verbatim to the user. Briefly summarize:

- Editorial: count of edits applied + count of flagged items.
- Fact-check: count of findings by severity.

Per decision #4, do not auto-commit the QC reports — the surrounding `/pilar:sprint-close` flow handles QC report commits as part of the sprint summary.

Stop.
