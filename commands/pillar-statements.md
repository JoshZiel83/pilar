---
description: Draft the Scientific Statements and Reference Statements for one pillar — manifest-aware sourcing, append-only IDs
allowed-tools: Bash, Read, Write, Edit
argument-hint: <pillar-id>
---

Draft the `## Scientific Statements` section of one pillar (per §7.5 / §6.5): SS-NN entries (each with `status`, dates, statement paragraph, strategic argument) and the nested RS-NN entries under each SS (each with `status`, `sources: [<ref-id>, …]`, dates, free-text reference statement). Refuses unless the pillar is at `narrative-approved` (or higher, for additive runs). Decomposes the approved narrative into a full SS slate, walks the writer through one macro review of the slate, persists the SS slate to the pillar file, drafts RS into the file under each SS, then walks one macro review of the SS+RS pairs against the persisted file. Each RS picks sources from `knowledge-base/manifest.md` entries; no ref-ids are invented. Append-only IDs per `docs/CONVENTIONS.md` (highest existing + 1; never reuses retired ids — relevant on rewind).

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

### Step 4 — Decompose-first SS/RS drafting (two macro reviews)

The earlier per-SS micro-loop interleaved claim wording with sourcing and RS drafting, which forced the writer to commit to claim wording before seeing the full slate of claims. The narrative phase already uses a better cadence (one composition, one macro review); this command now matches that shape, with two macro reviews — one on the SS slate as a decomposition of the narrative, one on the SS+RS pairs as written to the pillar file.

#### Step 4a — Propose the full SS slate

Read the pillar's approved `## Strategic Rationale`, `## Narrative`, and `## Scope` sections (Step 3 already captured these). Decompose the narrative into the granular ideas it makes and propose a full slate of `SS-<next_ss_n>` … `SS-<next_ss_n + k - 1>` — each with **Title**, **Statement paragraph**, and **Strategic argument**, framed as the granular claims that comprise the approved narrative.

**No sources, no reference statements at this stage.** This is a decomposition of the narrative into its constituent claims; sourcing follows after the decomposition is right.

In **additive runs** (status was already `statements-approved` when the run started): the slate scopes to "propose new SS to add" only — existing SS are not re-proposed and are not edited.

#### Step 4b — Joint review of the SS slate (first macro review)

Surface the proposed slate as a single artifact. Iterate with the user — adding, removing, splitting, merging, rewording — until the slate is right. The decomposition is a single intellectual judgment about coverage, balance, and overlap against the narrative, made *before* sourcing pressure can reshape claim wording.

Be a partner in this review: flag balance issues ("SS-02 and SS-04 cover overlapping ground; consider merging"), point out gaps ("the narrative claims durability but no SS in the slate operationalizes that"), suggest reorderings. Iterate until the user is satisfied with the slate as a whole.

Lexicon proposals are captured inline here (same pattern as `/pilar:pillar-narrative` Step 5): when a term decision surfaces during slate iteration, accumulate it in `lexicon_additions` for the Step 9 commit; no dedicated lexicon-prompt step at the end.

#### Step 4c — Persist the SS slate to the pillar file

Write the agreed slate to the pillar's `## Scientific Statements` section. Each SS block per the §7.5 schema layout: `### SS-NN: <title>` heading, then the **Statement** paragraph and **Strategic Argument** paragraph; under each SS leave a `**Reference Statements.** _TBD — drafted in 4d._` placeholder so Step 4d can fill it in.

Use Edit:

- **First-pass case** (existing `## Scientific Statements` body is the M1 `_TBD_` placeholder): the `old_string` matches the section heading + the placeholder; the `new_string` is the heading + the SS slate with `_TBD_` RS placeholders.
- **Additive case** (existing SS already present): append the new SS blocks after the last existing SS, with `_TBD_` RS placeholders. Do not modify existing SS/RS content — append-only at this granularity too.

This is a working-draft persist, not a commit. The full `_TBD_` → RS resolution happens in 4d→4e and only commits at Step 9.

#### Step 4d — Draft RS per SS into the pillar file

For each SS in the slate (or each new SS in the additive case): surface the manifest entries most relevant to the SS's claim, **draft the supporting RS slate, and write the drafted RS directly into the pillar file under their SS** (replacing the `_TBD_` placeholder from 4c). At this stage there is trust that Claude can make a competent first attempt — the writer reviews the *persisted* RS in 4e, not a chat-first walkthrough of every RS.

Per RS:

- Compute `next_rs_n = max(existing RS within this SS) + 1` (or `01` if first).
- **Title** — short and concrete.
- **Status** — `draft`.
- **sources** — `[<ref-id>, <ref-id>, …]`, picked from `knowledge-base/manifest.md` only; never invent ref-ids that don't exist in the manifest. Choose by topical relevance per the manifest entry's `type` and `key_findings`. If no manifest entry supports a claim the SS's decomposition implies, draft the RS anyway with `sources: []` — Step 7's orphan-RS scan will surface it for the writer's gap-creation decision rather than blocking the drafting flow here.
- **created** / **updated** — today's ISO date.
- **Body** — free-text reference statement, factual and dry per §7.5 / §6.6 / §9. Hedge appropriately for source strength; the Fact-Checker will catch overstatement during QC.

Use Edit, one Edit per SS, replacing the SS's `_TBD_` RS placeholder with the drafted RS slate. Preserve the SS's Statement and Strategic Argument paragraphs verbatim.

#### Step 4e — Joint review of SS+RS pairs against the persisted pillar file (second macro review)

The pillar file is now in its proposed end state. Walk each SS with its drafted RS together with the writer, reviewing against the persisted file (use `git diff <pillar_path>` to surface the change set in one view). Refine via Edit on the file — do not regenerate the SS/RS section wholesale.

Be brief. One or two short refinement rounds is the goal — heavy refinement of RS prose is the Editor's job, and source-strength judgments are the Fact-Checker's; the writer's job in 4e is to confirm decomposition, sourcing choices, and overall coverage.

Lexicon additions captured during 4b/4d/4e accumulate in `lexicon_additions`; they are written to `lexicon.md` alongside the pillar edit in Step 9's commit.

### Step 5 — Update frontmatter `updated:`

Edit the pillar's frontmatter `updated:` field to today's ISO date.

### Step 6 — Validate

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py <pillar_path>` (substituting the captured `<pillar_path>`).

The validator enforces SS-NN / RS-NN format, uniqueness within scope (no duplicate SS-NN within the pillar; no duplicate RS-NN within an SS), and `sources: [<ref-id>, …]` format. If validation fails, surface errors and correct via Edits before continuing.

### Step 7 — Orphan-RS check

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gaps.py <pillar_path> knowledge-base/manifest.md --format json` (substituting the captured `<pillar_path>`).

Parse the JSON. If `orphan_count` is 0, proceed silently to Step 9.

If orphans surfaced, present them to the user. For each orphan, draft a candidate `GAP-NNN` per `schemas/evidence-gaps.md` (mirroring `/pilar:ingest-kb` Step 12 — `linked_to`, `description`, `evidence_type_needed`, `proposed_search` from briefing/audience context, `status: open`, `opened: <today>`).

Compute next `GAP-NNN` from `registers/evidence-gaps.md` (highest existing + 1 zero-padded to three digits; append-only).

Ask the user: *"Append these gap entries inline (commit alongside the pillar) or defer to a follow-up `/pilar:ingest-kb` (which will re-detect them)?"*

- **Inline** → Edit `registers/evidence-gaps.md` to append the gaps under `## Open Gaps`. Update its frontmatter `updated:`. Validate via !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py registers/evidence-gaps.md`.
- **Defer** → leave `registers/evidence-gaps.md` untouched; the orphans will resurface the next time `/pilar:ingest-kb` runs against new files or the next time this pillar (or another) is drafted via `/pilar:pillar-statements`.

### Step 8 — Approve commit (status flip + commit in one gate)

Run `git status` to show changes (pillar file, optionally `lexicon.md` if lexicon additions were captured during drafting iteration, optionally `registers/evidence-gaps.md` from Step 7 inline-gap branch).

Lexicon proposals are captured **inline during the macro reviews in Step 4** (4b, 4d, 4e). When the user accepts a term decision in iteration, the proposal accumulates in `lexicon_additions`; the lexicon write lands alongside the pillar edit in this commit. No dedicated lexicon-prompt step at the end — the user's term decisions during drafting *are* the approval.

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

  (Append "; K gaps opened" if Step 7 wrote inline gap entries;
   "; lexicon: <terms>" if drafting added lexicon entries.)

Reply: approve / revise message: <new> / defer (leave status at narrative-approved, do not commit)
```

- **`approve`** → Edit pillar frontmatter `status` → `statements-approved`. Then `git add <pillar-path> [lexicon.md] [registers/evidence-gaps.md] && git commit -m "<approved message>"`.
- **`revise message: <new>`** → use the new message; restate the prompt; wait for `approve`.
- **`defer`** (or anything else) → leave `status: narrative-approved`. Do not commit. The working tree retains edits. Re-running the command later (additive case) is allowed; the `defer-until-sprint-close` semantic is preserved.

For the additive case (status was already `statements-approved` when the run started), the gate is the same shape but the "status flip" line reads `(no flip — additive run; status remains statements-approved)` and the message body reflects "additional N statements appended" rather than "approved".

### Step 9 — Brief the user on next steps

Tell the user (substituting):

> ✓ P-NN statements drafted: N SS / M RS. Status: <narrative-approved | statements-approved>. K gap(s) opened in this run.
>
> Next, per the sprint plan's `## QC Roles to Run`:
>
> - **`/pilar:run-qc <pillar-path> --context drafting`** — Editor first (lexicon + style enforcement, §9 disallowed-pattern checks), Fact-Checker second (RS claims vs cited source content, overstatement / misattribution / source-strength). Per §6.5 the Fact-Checker reviews the post-Editor copy, so the sequencing is enforced inside `/pilar:run-qc`.
> - When all pillars in the engagement are at `status: statements-approved`, P8 consolidation begins (`/pilar:consolidate` ships with Phase 8). Until then, draft additional pillars via `/pilar:pillar-narrative` and `/pilar:pillar-statements`.

Stop.
