---
description: Draft the Scientific Statements and Reference Statements for one pillar — manifest-aware sourcing, append-only IDs
allowed-tools: Bash, Read, Write, Edit
argument-hint: <pillar-id>
---

Draft the `## Scientific Statements` section of one pillar (per §7.5 / §6.5): SS-NN entries (each with `status`, dates, statement paragraph, strategic argument) and the nested RS-NN entries under each SS (each with `status`, `sources: [<ref-id>, …]`, dates, free-text reference statement). Refuses unless the pillar is at `narrative-approved` (or higher, for additive runs). Iterates with the user one SS at a time. Each RS picks sources from `knowledge-base/manifest.md` entries the writer chooses from. Append-only IDs per `docs/CONVENTIONS.md` (highest existing + 1; never reuses retired ids — relevant on rewind).

After drafting, runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gaps.py` against the pillar to flag orphan RS — those whose sources are missing, empty, or cite ref-ids not in the manifest. Surfaces orphans for inline `GAP-NNN` drafting (mirroring `/pilar:ingest-kb` Step 12) or defers to a follow-up `/pilar:ingest-kb` invocation.

Asks at the end whether to mark the pillar's `status` as `statements-approved`. Proposes the commit and waits for explicit user approval before committing — per decision #4.

Like `/pilar:pillar-narrative`, this command does **not** auto-invoke `/pilar:run-qc`. Editor + Fact-Checker engagement is sprint-planned (§5.2) and explicitly run by the writer.

## Pillar schema

@${CLAUDE_PLUGIN_ROOT}/schemas/pillar.md

## Procedure

### Step 1 — Detect engagement state, parse argument, locate pillar

Run:

!`pwd && ls -1 roadmap.md briefing.md knowledge-base/manifest.md 2>&1 | head -5`

If `roadmap.md` or `knowledge-base/manifest.md` is missing, **stop** with the relevant recommendation. Without a populated manifest, RS sources cannot be picked from the KB — recommend `/pilar:ingest-kb` first if the manifest has zero entries.

Parse `$ARGUMENTS` (must match `^P-\d{2}$`). Stop with usage if missing/malformed:

```
/pilar:pillar-statements <pillar-id>
  pillar-id: P-NN  (zero-padded two-digit pillar id)
  example: /pilar:pillar-statements P-04
```

Locate the pillar file via `grep -l "^pillar_id: <PILLAR_ID>$" pillars/*.md`. Stop with a specific error if absent. Capture `pillar_path`.

### Step 2 — Verify pillar status allows SS/RS drafting

Read pillar frontmatter. Capture `status`.

- `draft` → **stop** and tell the user the narrative must be approved first. Recommend `/pilar:pillar-narrative <pillar-id>`.
- `narrative-approved` → proceed (the canonical case — first SS/RS drafting pass on this pillar).
- `statements-approved` → proceed *with a warning*: SS/RS already drafted on this pillar are present and approved; this run will be additive (new SS or new RS appended to existing). Confirm the user wants to extend an approved set rather than rewinding (§5.3 covers re-opening approved content).
- `complete` → **stop** — P8 territory; consolidation has begun, modifying pillar SS/RS at this stage requires a deliberate rewind.

### Step 3 — Read engagement state to ground drafting

Read these:

- The pillar file's `## Strategic Rationale`, `## Narrative`, and `## Scope` (already approved if `status: narrative-approved`). The SS/RS work operationalizes the narrative argument; do not draft an SS that contradicts the scope.
- The pillar's existing `## Scientific Statements` body — capture every existing `### SS-NN: ` heading and each SS's `#### RS-NN: ` headings. Compute `next_ss_n = max(existing SS-NN) + 1` zero-padded to two digits (or `01` if none) for new SS additions.
- `briefing.md` — `## Strategic Priorities` and `## Audiences` are the most relevant; the SS's strategic argument should tie to a numbered priority.
- `knowledge-base/manifest.md` — capture every `### <ref-id>` entry's id, `type`, and `key_findings`. This is the source pool the writer picks from when drafting each RS's `sources:`.

### Step 4 — Iteratively draft scientific statements with the user

Loop. For each new SS:

1. Propose `SS-<next_ss_n>` with:
   - **Title** — short, concrete (e.g., "Pivotal Phase 2 efficacy in r/r DLBCL").
   - **Statement paragraph** — single paragraph in dry scientific tone per §6.6 / §9. State the scientific claim concretely; avoid §9 disallowed patterns at draft time (the Editor will catch any that slip in).
   - **Strategic argument** — one paragraph on why this statement matters to the pillar; tie to a specific Strategic Priority from the briefing. Be concrete about the differentiation or value claim it advances.
   Refine with the user until the SS is right.
2. Loop on RS within this SS. For each new RS:
   - Compute `next_rs_n = max(existing RS within this SS) + 1` (or `01` if first).
   - Propose `RS-<next_rs_n>`:
     - **Title** — short and concrete.
     - **Status** — `draft`.
     - **sources** — `[<ref-id>, <ref-id>, …]`. **Surface relevant manifest entries** based on the RS topic (e.g., for an "elderly subgroup efficacy" RS in a clinical-evidence pillar, surface entries whose `type` is `Single-arm Phase 2 trial` or `Congress abstract` and whose `key_findings` mention subgroup or elderly). Let the user pick the source(s); never invent ref-ids that don't exist in the manifest. If no manifest entry supports the proposed RS, flag this to the user — they can either reshape the RS to fit available evidence, defer this RS until evidence is added, or accept it as an orphan that Step 7 will surface.
     - **created** / **updated** — today's ISO date (capture via `!date +%F`).
     - **Body** — free-text reference statement, factual and dry per §7.5. The body's claims must be supportable by the cited source(s); the Fact-Checker will evaluate this in run-qc. Do not overstate; hedge appropriately for source strength.
   - Refine with the user until the RS is right.
   - Ask: *"Add another RS to SS-NN?"* — loop until the user is done with this SS.
3. Ask: *"Add another SS to this pillar?"* — loop until the user is done with the pillar.

Be brief. One or two short refinement rounds per SS / RS is the goal — over-refining at draft time wastes effort the Editor can spot more efficiently in the QC pass.

### Step 5 — Insert the drafted SS/RS structure into the pillar file

Compose the SS/RS markdown blocks per the §7.5 schema layout (each SS body has `**Statement.**` and `**Strategic Argument.**` paragraphs and a `**Reference Statements.**` heading; each RS body has its frontmatter-style fields and a free-text reference paragraph).

Use Edit:

- **First-pass case** (existing `## Scientific Statements` body is the M1 `_TBD_` placeholder): the `old_string` matches the section heading + the `_TBD_` placeholder line; the `new_string` is the section heading + the drafted SS/RS blocks.
- **Additive case** (existing SS already present): the `old_string` matches the last few lines of the final existing SS/RS block (with trailing whitespace); the `new_string` is those same lines plus the new SS/RS blocks. Do not modify any existing SS/RS content — append-only at this granularity too.

### Step 6 — Update frontmatter `updated:`

Edit the pillar's frontmatter `updated:` field to today's ISO date.

### Step 7 — Validate

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py <pillar_path>` (substituting the captured `<pillar_path>`).

The validator enforces SS-NN / RS-NN format, uniqueness within scope (no duplicate SS-NN within the pillar; no duplicate RS-NN within an SS), and `sources: [<ref-id>, …]` format. If validation fails, surface errors and correct via Edits before continuing.

### Step 8 — Orphan-RS check

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gaps.py <pillar_path> knowledge-base/manifest.md --format json` (substituting the captured `<pillar_path>`).

Parse the JSON. If `orphan_count` is 0, proceed silently to Step 9.

If orphans surfaced, present them to the user. For each orphan, draft a candidate `GAP-NNN` per `schemas/evidence-gaps.md` (mirroring `/pilar:ingest-kb` Step 12 — `linked_to`, `description`, `evidence_type_needed`, `proposed_search` from briefing/audience context, `status: open`, `opened: <today>`).

Compute next `GAP-NNN` from `registers/evidence-gaps.md` (highest existing + 1 zero-padded to three digits; append-only).

Ask the user: *"Append these gap entries inline (commit alongside the pillar) or defer to a follow-up `/pilar:ingest-kb` (which will re-detect them)?"*

- **Inline** → Edit `registers/evidence-gaps.md` to append the gaps under `## Open Gaps`. Update its frontmatter `updated:`. Validate via !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py registers/evidence-gaps.md`.
- **Defer** → leave `registers/evidence-gaps.md` untouched; the orphans will resurface the next time `/pilar:ingest-kb` runs against new files or the next time this pillar (or another) is drafted via `/pilar:pillar-statements`.

### Step 9 — Approve commit (status flip + commit in one gate)

Run `git status` to show changes (pillar file, optionally `lexicon.md` if lexicon additions were captured during drafting iteration, optionally `registers/evidence-gaps.md` from Step 8 inline-gap branch).

Lexicon proposals are captured **inline during drafting** (same pattern as `/pilar:pillar-narrative` Step 5): when the user accepts a term decision in iteration, the proposal accumulates in a running `lexicon_additions` list; the actual lexicon write happens in Step 5's persistence step (or in a sub-step of the decompose-first restructure, when that lands). No dedicated lexicon-prompt step at the end — the user's term decisions during drafting *are* the approval.

Propose the commit message **and** the implied status flip in one prompt. The commit message records the status flip, so the prior pattern of asking "mark approved?" then "approve commit?" had the user authorizing the same decision twice.

```
APPROVE COMMIT

Records status flip: P-NN narrative-approved → statements-approved
Commit message:
  feat(pilar): P-NN statements approved (<name>)

  N scientific statement(s) and M reference statement(s) drafted under
  ## Scientific Statements; sources cited from the KB manifest.
  Status moved narrative-approved → statements-approved.
  Next: /pilar:run-qc <pillar-path> for Editor + Fact-Checker pass.

  (Append "; K gaps opened" if Step 8 wrote inline gap entries;
   "; lexicon: <terms>" if drafting added lexicon entries.)

Reply: approve / revise message: <new> / defer (leave status at narrative-approved, do not commit)
```

- **`approve`** → Edit pillar frontmatter `status` → `statements-approved`. Then `git add <pillar-path> [lexicon.md] [registers/evidence-gaps.md] && git commit -m "<approved message>"`.
- **`revise message: <new>`** → use the new message; restate the prompt; wait for `approve`.
- **`defer`** (or anything else) → leave `status: narrative-approved`. Do not commit. The working tree retains edits. Re-running the command later (additive case) is allowed; the `defer-until-sprint-close` semantic is preserved.

For the additive case (status was already `statements-approved` when the run started), the gate is the same shape but the "status flip" line reads `(no flip — additive run; status remains statements-approved)` and the message body reflects "additional N statements appended" rather than "approved".

### Step 10 — Brief the user on next steps

Tell the user (substituting):

> ✓ P-NN statements drafted: N SS / M RS. Status: <narrative-approved | statements-approved>. K gap(s) opened in this run.
>
> Next, per the sprint plan's `## QC Roles to Run`:
>
> - **`/pilar:run-qc <pillar-path> --context drafting`** — Editor first (lexicon + style enforcement, §9 disallowed-pattern checks), Fact-Checker second (RS claims vs cited source content, overstatement / misattribution / source-strength). Per §6.5 the Fact-Checker reviews the post-Editor copy, so the sequencing is enforced inside `/pilar:run-qc`.
> - When all pillars in the engagement are at `status: statements-approved`, P8 consolidation begins (`/pilar:consolidate` ships with Phase 8). Until then, draft additional pillars via `/pilar:pillar-narrative` and `/pilar:pillar-statements`.

Stop.
