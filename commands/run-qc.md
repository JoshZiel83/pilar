---
description: Run QC on a pilar artifact — Editor → Fact-Checker → Strategic Reviewer (consolidated only), per §8 sequencing
argument-hint: <artifact-path> [--context drafting|consolidated-draft] [--consolidated]
allowed-tools: Bash, Read, Write, Task
---

Run the QC subagents against the pilar artifact at the path supplied in `$ARGUMENTS`.

- At **drafting** context (per-pillar): Editor edits the artifact in place via the Edit tool and produces an editorial report (per §4.4); Fact-Checker then runs against the post-Editor artifact and produces a fact-check report (per §8 sequencing — Fact-Checker reviews edited copy).
- At **consolidated-draft** context (`--consolidated`): per §6.8, all three QC roles are **read-only** — Editor reads the consolidated draft and reports cross-pillar findings (no edits, no discrete editorial commit); Fact-Checker reads the consolidated draft against cited sources; Strategic Reviewer reads briefing + roadmap + consolidated draft. Findings are addressed by editing source pillars and re-consolidating, not by editing the consolidated draft.

Sequencing is enforced by this command's logic per load-bearing decision #3 (`/pilar:run-qc` is the single QC entry point).

## Procedure

### Step 1 — Parse arguments

Parse `$ARGUMENTS`:

- First positional argument: the artifact path (required).
- Optional flag: `--context <drafting|consolidated-draft>` (default: `drafting`).
- Optional flag: `--consolidated`. Implies `--context consolidated-draft` AND triggers the Strategic Reviewer step (Step 9) after Editor and Fact-Checker. The artifact must be a `consolidated-draft` (asserted in Step 2).

If no positional argument, **stop** and tell the user the usage: `/pilar:run-qc <artifact-path> [--context drafting|consolidated-draft] [--consolidated]`.

Capture `artifact_arg`, `operating_context`, and a boolean `run_strategic_reviewer`. Defaults: `operating_context=drafting`, `run_strategic_reviewer=false`. When `--consolidated` is present: set `operating_context=consolidated-draft` (overriding any conflicting `--context`) and `run_strategic_reviewer=true`. When `--context consolidated-draft` is present without `--consolidated`, leave `run_strategic_reviewer=false` — the user is intentionally running consolidated-context Editor + Fact-Checker without the Strategic Reviewer (rare but supported; the consolidated-context Editor remains read-only either way).

### Step 2 — Read the artifact and resolve engagement state

Read the artifact at `artifact_arg`. Capture:

- `artifact_path` — the absolute path of the artifact file (use `!realpath`).
- `artifact_id` — derived from frontmatter:
  - For pillars: `pillar_id`.
  - For consolidated drafts: the `draft_id` (e.g. `cd-001`).
  - For scientific or reference statements (which only appear inside a pillar): the parent pillar's `pillar_id` plus the SS / RS id chain (e.g. `P-04.SS-01.RS-02`).
  - For other artifact types (rare for `/pilar:run-qc`): use the artifact's `project` value.
- The artifact's frontmatter and body, separated by the closing `---` line.
- `sources` — the union of `sources:` lists from all reference-statement blocks in the body (e.g. `[REF-001, REF-005]`).
- `draft_id` — only when the artifact is a consolidated draft: the `draft_id:` value from frontmatter (e.g. `cd-001`).

If `run_strategic_reviewer == true`: assert that the artifact's frontmatter `artifact:` value is `consolidated-draft`. If not, **stop** with usage hint: `--consolidated requires a consolidated-draft artifact (artifact: consolidated-draft in frontmatter); got artifact: <value>. Run /pilar:consolidate first.`

Locate the engagement's lexicon and style guide:

- `lexicon_path` — absolute path to `lexicon.md` at the engagement repo root.
- `style_guide_path` — absolute path to `style-guide.md` at the engagement repo root.

If either is missing, **stop** — the engagement appears under-scaffolded; recommend `/pilar:init` or check that the user is at the engagement repo root.

If `run_strategic_reviewer == true`, also locate:

- `briefing_path` — absolute path to `briefing.md` at the engagement repo root.
- `roadmap_path` — absolute path to `roadmap.md` at the engagement repo root.

If either is missing in this case, **stop** — the engagement is under-scaffolded; the Strategic Reviewer requires both.

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

Per the Independence Contract, you may Read only the four paths above. At drafting context, apply permitted edits to the artifact body via Edit and flag items that would change meaning. At consolidated-draft context, do not Edit — report cross-pillar findings as flagged items only. Emit only the editorial report per your system prompt.
PILAR_EDITOR_PROMPT>>>
```

Substitutions:

- `{operating_context}` — the value from Step 1.
- `{artifact_id}` — captured in Step 2.
- `{artifact_path}` — captured in Step 2.
- `{lexicon_path}` — captured in Step 2.
- `{style_guide_path}` — captured in Step 2.

The variables `{operating_context}`, `{artifact_id}`, `{artifact_path}`, `{lexicon_path}`, and `{style_guide_path}` are the **complete and exhaustive** set of inputs the parent is permitted to pass into the Editor's context. The static context-audit test in `scripts/context-audit.py` enforces this allowlist.

### Step 4 — Inspect the Editor's output (drafting context only)

If `operating_context == drafting`: the Editor used the **Edit** tool to apply each change surgically directly to `{artifact_path}` during its Task invocation. By the time it returns, the artifact file is in its post-edit state. Capture the Editor's response — it should begin with `---` and the editorial-report YAML frontmatter, followed by `# Editorial Report` and the body. Extract this content as `editorial_report_content`. If the Editor's response does not start with the editorial-report frontmatter, **stop** and surface its raw response to the user.

Run:

```bash
git diff {artifact_path}
```

Show the user the diff and summarize the change categories from the editorial report's "Edits Applied Summary" section (e.g. "5 edits applied: 2 lexicon, 2 style, 1 consistency").

Cross-check the editorial report against the actual diff:

- Parse the report's "Edits Applied Summary" line for the claimed edit count `N`.
- Count distinct hunks in the `git diff` output.
- If `N > 0` but the diff is empty, the Editor's Edits silently failed — surface the discrepancy and **stop** before invoking Fact-Checker.
- If `N == 0` and the diff is empty, the Editor legitimately found nothing to edit; proceed.
- If `N` and the diff hunk count are both nonzero, accept the result and proceed (exact one-to-one matching is not required because surgical edits in adjacent text may merge into a single hunk).

If `operating_context == consolidated-draft`: the Editor is read-only (per §6.8 and `agents/editor.md`); the artifact file is byte-identical to its pre-Editor state. Capture the Editor's response as `editorial_report_content` (it should be only the editorial report — no `## EDITS APPLIED` because none were applied). Skip the diff inspection; instead, verify via `!git diff {artifact_path}` that the diff is empty (confirms the Editor honored the read-only contract). If the diff is non-empty, surface the discrepancy as a contract violation and **stop** — the Editor must not modify the consolidated draft.

### Step 5 — Save the editorial report

Compute the report filename: `qc/editorial-reports/sprint-<NN>-editorial-<slug>.md` where `<NN>` is `roadmap.md::current_sprint` zero-padded and `<slug>` is the artifact's id lowercased with dots → hyphens (e.g. `P-04.SS-01` → `p-04-ss-01`; `cd-001` stays `cd-001`).

Write `editorial_report_content` to that path.

Validate it: `!python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py qc/editorial-reports/sprint-<NN>-editorial-<slug>.md`. If validation fails, surface the errors but continue (the report is still useful as content).

### Step 6 — Resolve cited source paths

For each ref-id in `sources` (collected in Step 2), look up the source file via `knowledge-base/manifest.md`:

- Find the manifest entry whose heading matches the ref-id (e.g. `### REF-001`).
- Read the `file:` path; resolve to absolute.
- Verify the file exists.

Collect the union as `source_paths` — a list of absolute paths ordered to match the artifact's RS source ordering. For unresolved sources, include `MISSING:<REF-NNN>` as a placeholder string at the corresponding position (the Fact-Checker treats these as gap findings).

### Step 7 — Invoke the Fact-Checker subagent

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
- `{artifact_id}` — captured in Step 2.
- `{artifact_path}` — captured in Step 2 (at drafting context the file is the post-Editor version; at consolidated-draft context the file is the byte-identical-to-pre-Editor consolidated draft, since the Editor was read-only).
- `{source_paths}` — the list captured in Step 6 formatted as YAML-style inline list.

### Step 8 — Save the fact-check report

Save the Fact-Checker's returned report to `qc/fact-check-reports/sprint-<NN>-fact-check-<slug>.md`. Validate with `!python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py qc/fact-check-reports/sprint-<NN>-fact-check-<slug>.md`.

If `run_strategic_reviewer == false`, **skip ahead to Step 10** (surface and stop). Otherwise proceed to Step 9.

### Step 9 — Invoke the Strategic Reviewer subagent (consolidated only)

Reached only when `run_strategic_reviewer == true` (i.e. `--consolidated` was set in Step 1). Per §6.8 the Strategic Reviewer engages on the consolidated draft after Editor and Fact-Checker have completed. Per §4.5 and Appendix A of the Independence Contract, the Strategic Reviewer reads only the briefing, the roadmap, and the consolidated draft — never the lexicon, style guide, KB manifest, source files, Editor's report, Fact-Checker's report, prior sprint summaries, drafting rationale, or per-pillar progress notes.

Use the **Task** tool with `subagent_type: strategic-reviewer` and a prompt produced by substituting the named variables below into this exact template, and **only** this template.

```
<<<PILAR_STRATEGIC_REVIEWER_PROMPT
OPERATING CONTEXT: {operating_context}

CONSOLIDATED DRAFT (id: {draft_id}):
path: {artifact_path}

BRIEFING:
path: {briefing_path}

ROADMAP:
path: {roadmap_path}

Per the Independence Contract, you may Read only the three paths above. Produce a strategic-alignment report per §7.10 of scp-plugin-spec.md.
PILAR_STRATEGIC_REVIEWER_PROMPT>>>
```

Substitutions:

- `{operating_context}` — the value from Step 1 (always `consolidated-draft` when this step runs).
- `{draft_id}` — captured in Step 2 (the consolidated draft's `cd-NNN` id).
- `{artifact_path}` — same as Steps 3 and 7 (the file is byte-identical to its as-assembled state since neither Editor nor Fact-Checker modified it at consolidated context).
- `{briefing_path}` — captured in Step 2 (only when `run_strategic_reviewer == true`).
- `{roadmap_path}` — captured in Step 2 (only when `run_strategic_reviewer == true`).

The variables `{operating_context}`, `{draft_id}`, `{artifact_path}`, `{briefing_path}`, and `{roadmap_path}` are the **complete and exhaustive** set of inputs the parent is permitted to pass into the Strategic Reviewer's context. The static context-audit test in `scripts/context-audit.py` enforces this allowlist.

Save the Strategic Reviewer's returned report to `qc/strategic-alignment-reports/sprint-<NN>-strategic-<draft-id>.md` (e.g. `qc/strategic-alignment-reports/sprint-08-strategic-cd-001.md`). Validate with `!python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py qc/strategic-alignment-reports/sprint-<NN>-strategic-<draft-id>.md`. If validation fails, surface the errors but continue (the report content is still useful).

### Step 10 — Surface the reports

Print every produced report verbatim to the user, in produced order:

1. Editorial report.
2. Fact-check report.
3. Strategic-alignment report (only when `run_strategic_reviewer == true`).

Briefly summarize:

- Editorial: at drafting context, count of edits applied + count of flagged items. At consolidated-draft context, count of flagged items only (no edits applied).
- Fact-check: count of findings by severity.
- Strategic alignment (when applicable): count of findings by severity, and (key) the count of findings with severity `high` against `target: deliverable` — these are the substantive findings that, per §6.8, may require revising affected pillars and re-consolidating.

Per decision #4, do not auto-commit any of the reports here — the surrounding `/pilar:sprint-close` flow handles QC report commits as part of the sprint summary. (At consolidated context there is no discrete editorial commit either, since the Editor is read-only.)

If any Editor flagged items, Fact-Checker findings, or Strategic Reviewer findings have severity `high`, briefly remind the user of the §6.8 loop: address the findings by editing the affected source pillars, re-run `/pilar:consolidate` to produce `cd-<NNN+1>`, then re-run `/pilar:run-qc --consolidated` on the new draft. The loop terminates when a consolidated draft clears review; `/pilar:handoff` finalizes at that point.

Stop.
