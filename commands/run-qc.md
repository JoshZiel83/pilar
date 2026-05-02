---
description: Run QC on a pilar artifact (Phase 2 stub — Fact-Checker only)
argument-hint: <artifact-path>
allowed-tools: Read, Task
---

Run the Fact-Checker subagent against the pilar artifact at `$ARGUMENTS`, demonstrating the §4/§8 Independence Contract.

Real QC runs the Editor first, then the Fact-Checker (per §8 sequencing), then the Strategic Reviewer for consolidated drafts. This Phase 2 stub exercises the Fact-Checker only — Editor and Strategic Reviewer ship with Phases 5 and 8 respectively.

## Procedure

### Step 1 — Read the artifact under review

Read the artifact file at `$ARGUMENTS`. Parse its frontmatter and capture exactly these three values, ignoring everything else:

- `artifact_id` — the artifact's identifier. For pillars use `pillar_id`; for scientific statements use `pillar_id.SS-id`; for reference statements use `pillar_id.SS-id.RS-id`. If the artifact does not have such an identifier (e.g. it's a roadmap), use the artifact's `project` value.
- `artifact_text` — the full body text of the artifact (everything after the closing `---` of the frontmatter).
- `sources` — the list of ref-ids referenced from the artifact's `sources:` frontmatter, if any. For pillars and scientific statements without a top-level `sources:` field, collect the union of `sources:` from every reference-statement block in the body.

### Step 2 — Resolve cited sources

For each ref-id in `sources`, locate the source file via the engagement's `knowledge-base/manifest.md`:

- Find the manifest entry whose heading matches the ref-id (e.g. `### REF-001`).
- Read the `file:` path from that entry.
- Read the source file at that path.

Capture the union as `source_texts`, with each source preceded by a clear delimiter line of the form `=== <ref-id>: <file-path> ===`. If a cited source cannot be resolved (manifest missing, entry missing, file missing), include a delimiter line followed by `MISSING — Fact-Checker should report this as a gap finding.` Do not abort.

### Step 3 — Invoke the Fact-Checker subagent

Use the **Task** tool with `subagent_type: fact-checker` and a prompt produced by substituting the named variables below into this exact template, and **only** this template. Do not add any additional context from your session, the briefing, the roadmap, drafting rationale, lexicon, style guide, prior sprint summaries, other pillars, or manifest entries for uncited sources.

```
<<<PILAR_FACT_CHECKER_PROMPT
OPERATING CONTEXT: {operating_context}

ARTIFACT UNDER REVIEW (id: {artifact_id}):
---
{artifact_text}
---

CITED SOURCE FILES:
---
{source_texts}
---

Per the Independence Contract, you have only the artifact above and its cited sources. Produce a fact-check report per §7.10 of scp-plugin-spec.md.
PILAR_FACT_CHECKER_PROMPT>>>
```

Substitutions:

- `{operating_context}` — pass the literal string `drafting` for this Phase 2 stub. (Phase 8 introduces `consolidated-draft`.)
- `{artifact_id}` — the value captured in Step 1.
- `{artifact_text}` — the value captured in Step 1.
- `{source_texts}` — the value captured in Step 2.

The variables `{operating_context}`, `{artifact_id}`, `{artifact_text}`, and `{source_texts}` are the **complete and exhaustive** set of inputs the parent is permitted to pass into the Fact-Checker's context. The static context-audit test in `scripts/context-audit.py` enforces this allowlist.

### Step 4 — Surface the report

Print the report the Fact-Checker returned, verbatim, to the user. Then add one summary sentence: "Fact-Checker ran under the Phase 2 Independence Contract stub; the report above is a stub. Real fact-checking arrives with Phase 5."

Stop.
