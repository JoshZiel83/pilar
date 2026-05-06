---
description: Assemble approved pillars + briefing + lexicon + style guide into a consolidated draft (§6.7) — deterministic mechanical assembly via scripts/consolidate.py
allowed-tools: Bash, Read
---

Assemble a single coherent deliverable view per §6.7 of `scp-plugin-spec.md`. Concatenates `briefing.md` + every approved pillar (`status: statements-approved` or `complete`) + `lexicon.md` + `style-guide.md` into `consolidated/cd-NNN.md` — a `consolidated-draft` artifact (`schemas/consolidated-draft.md`).

The actual byte-level assembly is performed by `scripts/consolidate.py`, a deterministic Python script that does not interpret, rewrite, or summarize: running it twice on the same inputs produces byte-identical output. The source pillars remain the canonical state of the engagement; the consolidated draft is a derived view that is regenerated from the source pillars on every consolidation. This command is a thin wrapper around the script — it handles the surrounding UX (engagement-state confirmation, drift warning, orphan-RS audit, commit proposal) but does not author the consolidated draft itself.

The consolidated draft is the input to `/pilar:run-qc --consolidated`, which runs Editor + Fact-Checker + Strategic Reviewer all read-only per §6.8. Findings are addressed by editing source pillars and re-consolidating, not by editing the consolidated draft.

## Procedure

### Step 1 — Detect engagement state

Run:

!`pwd && ls -1 roadmap.md briefing.md lexicon.md style-guide.md 2>&1 | head`

If `roadmap.md` is absent at cwd, **stop** — recommend `/pilar:init` from a fresh directory; this is not a pilar engagement repo.

If any of `briefing.md`, `lexicon.md`, or `style-guide.md` is missing, **stop** — the engagement is under-scaffolded. Recommend `/pilar:init` to seed the missing stubs.

### Step 2 — Pre-assembly drift warning (informational, not a gate)

If at least one prior `consolidated/cd-NNN.md` exists, find the most recent one:

!`ls -1 consolidated/cd-*.md 2>/dev/null | sort | tail -1`

Capture its mtime via `!stat -f %Sm -t %F consolidated/<latest-cd>.md` (macOS) or `!stat -c %y consolidated/<latest-cd>.md | cut -d' ' -f1` (Linux); accept either format.

For each pillar at `pillars/*.md` with `status: statements-approved` or `status: complete` in its frontmatter, compare its `updated:` date to that mtime. List any pillars whose `updated:` is **later** than the prior draft's mtime — these are the drifted pillars whose changes will land in the new consolidation. List any pillars whose `updated:` is **earlier** for context (these reflect state already represented in the prior draft).

Show the drift summary to the user. The user may proceed even if no drift exists (re-consolidating against unchanged inputs produces a near-identical file — only the assembly date in the body changes).

If no prior `consolidated/cd-NNN.md` exists, skip this step.

### Step 3 — Pre-assembly orphan-RS audit (informational, not a gate)

Run:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gaps.py pillars/ 2>&1 | head -100`

If the script reports orphan-RS findings within any approved pillar, surface the findings and ask:

> The following approved pillars have unresolved orphan-RS findings: `<list>`. Consolidating ships a deliverable view that contains unsupported reference statements. Proceed anyway? [y/N]

On anything other than `y`, **stop** — recommend the user close the gaps via `/pilar:ingest-kb` (Step 12 walks the user through gap creation) or revise the affected RS to remove the orphan.

If the audit finds no orphan-RS within the approved pillars, **proceed silently**.

### Step 4 — Run the assembly

Invoke the consolidation script:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/consolidate.py`

The script auto-detects the next sequential `cd-NNN` (highest existing in `consolidated/` + 1, or `cd-001` for the first run); reads `briefing.md`, `lexicon.md`, `style-guide.md`, and every approved pillar in `pillar-id` order; assembles the body with deterministic heading demotion (briefing H2 → H3; pillar H2 → H4 / H3 → H5 / H4 → H6; lexicon entries unchanged at H3; style-guide H2 → H3); writes `consolidated/<cd-id>.md`. Frontmatter populated as `artifact: consolidated-draft`, `draft_id: <cd-id>`, `project: <from briefing>`, `created: <today>`. Open `GAP-NNN`/`ASP-NNN` register entries are excluded — registers are working-state, not deliverable content.

Refusal cases the script handles:
- No approved pillars (no pillar at `status: statements-approved` or `status: complete`) → exits non-zero with an error message; surface the error and recommend `/pilar:pillar-narrative` + `/pilar:pillar-statements` first.
- Missing required input file (briefing/lexicon/style-guide) → exits non-zero; surface and recommend `/pilar:init`.

If the script exits non-zero, **stop** — do not propose a commit.

If the script succeeds, capture the resulting `<cd-id>` from the script's stderr output (the `wrote consolidated/<cd-id>.md (...)` line).

### Step 5 — Validate the consolidated draft

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py consolidated/<cd-id>.md` (substituting the captured `<cd-id>`).

Expected: `Validated 1 file(s); 0 error(s)`. If validation fails (rare — the script's output is byte-deterministic and the schema constraints are mechanical), surface the errors and **stop** before proposing a commit. The likely failure mode is a malformed input artifact (e.g. a pillar's frontmatter missing required keys); fix the source artifact and re-run.

### Step 6 — Propose the commit

Run `!git status` to show the new file. Propose:

```
chore(pilar): assemble consolidated draft <cd-id>

Deterministic mechanical assembly per §6.7 (scripts/consolidate.py).
Source pillars: <comma-separated pillar-ids>. Schema-valid.

Next: /pilar:run-qc --consolidated consolidated/<cd-id>.md to run the
whole-deliverable review (Editor + Fact-Checker + Strategic Reviewer,
all read-only per §6.8). Findings are addressed by editing source
pillars and re-consolidating.
```

Wait for explicit user approval. On approval:

```bash
git add consolidated/<cd-id>.md
git commit -m "..."  # heredoc with the approved message
```

If the user wants to revise the message, accept their version. If the user defers the commit, stop without committing — the file is on disk for inspection.

### Step 7 — Brief the user on next steps

Tell the user:

> ✓ Consolidated draft `<cd-id>` assembled at `consolidated/<cd-id>.md` by `scripts/consolidate.py`. Source pillars: `<list>`.
>
> Next: run `/pilar:run-qc --consolidated consolidated/<cd-id>.md` to enter the whole-deliverable review per §6.8. The Editor reads the consolidated draft and reports cross-pillar findings (terminology drift, lexicon adherence, claim duplication or contradiction); the Fact-Checker re-verifies the union of cited sources against the consolidated body; the Strategic Reviewer evaluates the deliverable against the briefing's strategic priorities. All three roles are read-only at this stage — none of them modifies the consolidated draft.
>
> Findings are addressed by editing the source pillars (or other source artifacts) and re-running `/pilar:consolidate` to produce `cd-<NNN+1>`, then re-running `/pilar:run-qc --consolidated`. The loop terminates when a consolidated draft clears review; `/pilar:handoff` finalizes the engagement at that point.

Stop.
