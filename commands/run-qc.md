---
description: Run QC on a pilar artifact (Fact-Checker now real; Editor lands in M3 of P5)
argument-hint: <artifact-path>
allowed-tools: Read, Task
---

Run the Fact-Checker subagent against the pilar artifact at `$ARGUMENTS`, demonstrating the §4/§8 Independence Contract.

Real QC runs the Editor first, then the Fact-Checker (per §8 sequencing), then the Strategic Reviewer for consolidated drafts. **This file currently invokes the Fact-Checker only** — Editor invocation lands in M3 of Phase 5 (this in-flight phase); Strategic Reviewer ships with Phase 8.

## Procedure

### Step 1 — Read the artifact under review

Read the artifact file at `$ARGUMENTS`. Parse its frontmatter and capture exactly these three values, ignoring everything else:

- `artifact_id` — the artifact's identifier. For pillars use `pillar_id`; for scientific statements use `pillar_id.SS-id`; for reference statements use `pillar_id.SS-id.RS-id`. If the artifact does not have such an identifier (e.g. it's a roadmap), use the artifact's `project` value.
- `artifact_path` — the absolute path of the artifact file (i.e. the resolution of `$ARGUMENTS`). Capture this from `!realpath "$ARGUMENTS"` or equivalent.
- `sources` — the list of ref-ids referenced from the artifact's `sources:` lists, if any. For pillars and scientific statements without a top-level `sources:` field, collect the union of `sources:` from every reference-statement block in the body.

### Step 2 — Resolve cited source paths

For each ref-id in `sources`, locate the source file via the engagement's `knowledge-base/manifest.md`:

- Find the manifest entry whose heading matches the ref-id (e.g. `### REF-001`).
- Read the `file:` path from that entry; resolve it to an absolute path.
- Verify the file exists; if not, record the ref-id as missing.

Capture the union as `source_paths` — a list of absolute file paths, ordered to match the order of ref-ids in the artifact's reference statements. If any cited source cannot be resolved (manifest missing, entry missing, file missing), include a `MISSING:<REF-NNN>` placeholder string in `source_paths` at the corresponding position. The Fact-Checker subagent treats `MISSING:` entries as gap findings.

### Step 3 — Invoke the Fact-Checker subagent

Use the **Task** tool with `subagent_type: fact-checker` and a prompt produced by substituting the named variables below into this exact template, and **only** this template. Do not add any additional context from your session, the briefing, the roadmap, drafting rationale, lexicon, style guide, prior sprint summaries, other pillars, or manifest entries for uncited sources.

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

- `{operating_context}` — pass the literal string `drafting` for now. (Phase 8 introduces `consolidated-draft` for whole-deliverable review.)
- `{artifact_id}` — the value captured in Step 1.
- `{artifact_path}` — the absolute path captured in Step 1.
- `{source_paths}` — the list captured in Step 2, formatted as a YAML-style inline list (e.g. `[/abs/path/to/REF-001.txt, /abs/path/to/REF-005.txt]`).

The variables `{operating_context}`, `{artifact_id}`, `{artifact_path}`, and `{source_paths}` are the **complete and exhaustive** set of inputs the parent is permitted to pass into the Fact-Checker's context. The static context-audit test in `scripts/context-audit.py` enforces this allowlist.

### Step 4 — Save and surface the report

The Fact-Checker returns a schema-conformant `fact-check-report` markdown document. Save it under `qc/fact-check-reports/` in the engagement repo:

- Filename: `qc/fact-check-reports/sprint-<NN>-fact-check-<artifact-slug>.md` where `<NN>` is the current sprint number from `roadmap.md::current_sprint` zero-padded, and `<artifact-slug>` is a short slug derived from the artifact's id (e.g. `P-04-SS-01` becomes `p-04-ss-01`).
- Validate the saved report with `!python3 scripts/validate-schemas.py qc/fact-check-reports/sprint-<NN>-fact-check-<artifact-slug>.md` if the script is available.

Print the report verbatim to the user. Briefly summarize the count of findings by severity.

Stop. (Do not auto-commit; per decision #4, the user's sprint-close flow handles QC report commits.)
