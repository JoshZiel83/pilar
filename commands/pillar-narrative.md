---
description: Draft the Strategic Rationale, Narrative, and Scope sections for one pillar — grounded in briefing + manifest + cross-pillar context
allowed-tools: Bash, Read, Write, Edit
argument-hint: <pillar-id>
---

Draft the `## Strategic Rationale`, `## Narrative`, and `## Scope` sections of one pillar (per §7.5 / §6.5). Reads briefing (Strategic Priorities, Audiences, Indication, Competitive Context, Constraints), KB manifest (so the narrative is grounded in available evidence), and any already-narrative-approved pillars (for cross-pillar consistency). Iterates with the user on the drafted text; writes back to the pillar file. Optionally accumulates new lexicon entries (§6.6). Asks at the end whether to mark the pillar's `status` as `narrative-approved`. Proposes the commit and waits for explicit user approval before committing — per decision #4.

This command does **not** invoke `/pilar:run-qc` automatically. Editor engagement on the drafted narrative is a sprint-planned step (§5.2); the writer runs `/pilar:run-qc <pillar-path>` separately when the sprint plan calls for it. This command surfaces that as the next-step recommendation.

## Pillar schema

@${CLAUDE_PLUGIN_ROOT}/schemas/pillar.md

## Procedure

### Step 1 — Detect engagement state and parse the argument

Run:

!`pwd && ls -1 roadmap.md briefing.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** — recommend `/pilar:init`.

Parse `$ARGUMENTS`. The argument must match `^P-\d{2}$`. If empty or malformed, **stop** with usage:

```
/pilar:pillar-narrative <pillar-id>
  pillar-id: P-NN  (zero-padded two-digit pillar id)
  example: /pilar:pillar-narrative P-04
```

Capture `pillar_id`.

### Step 2 — Locate the pillar file

Run:

!`grep -l "^pillar_id: <PILLAR_ID>$" pillars/*.md 2>/dev/null` (substitute the captured `pillar_id`).

If no file matches, **stop** and tell the user pillar `<pillar_id>` does not exist; recommend `/pilar:scaffold-pillars` (or — if scaffolding is already done — point at the writer's likely typo).

Capture the matched path as `pillar_path`.

### Step 3 — Verify status is appropriate for narrative drafting

Read the pillar file's frontmatter. Capture `status`.

- `draft` → proceed.
- `narrative-approved`, `statements-approved`, `complete` → **stop** and tell the user the pillar is past narrative drafting. To revise an approved narrative, the user must rewind the prior approval per §5.3 (open a rewind sprint via `/pilar:sprint-plan`, record the reopening in the roadmap decisions log). Do not silently overwrite approved content.

If `status` is `draft` but the `## Narrative` body is non-empty (i.e., not the M1 `_TBD_` stub), surface the existing content to the user and ask whether this is a continuation of an in-flight draft (proceed, refining what's there) or whether the existing content should be discarded (proceed, replacing it). Either path is allowed — the user picks.

### Step 4 — Read engagement state to ground drafting

Read these in full or in part as noted:

- `briefing.md` — full body. The drafting needs `## Indication`, `## Audiences`, `## Strategic Priorities`, `## Competitive Context`, `## Constraints`, `## Evidence Generation Activities`.
- `knowledge-base/manifest.md` — capture every `### <ref-id>` entry's id, `type`, and `key_findings`. Group by `type` (e.g., `Single-arm Phase 2 trial: <ref-id>, <ref-id>`; `Treatment guideline: <ref-id>`) — the narrative will reference categories of evidence available, not specific manifest entries (those are in scope for `/pilar:pillar-statements`).
- `pillars/*.md` — for each pillar file at `status` ≥ `narrative-approved` (i.e., `narrative-approved`, `statements-approved`, or `complete`), capture the pillar's name, slug, and a one-sentence summary of its `## Narrative` (the first paragraph). This grounds cross-pillar consistency: the new narrative should not duplicate or contradict already-approved framing.

### Step 5 — Draft the three sections with the user (lexicon proposals captured inline)

The Primary Collaborator drafts in the main session — no subagent. The user reviews and refines each section.

**Strategic Rationale** — a one-paragraph (occasionally two) statement of *why this pillar exists* and *which Strategic Priority(ies) it advances*. Tie explicitly to the briefing's numbered Strategic Priorities. Mention the audience(s) primarily addressed.

**Narrative** — the strategic argument the pillar makes and the evidentiary territory it covers. Two to four paragraphs typically. Grounded in available evidence categories from the manifest (without naming specific manifest entries — that's RS-level work). Should read in dry scientific tone per §6.6 / §9, with no §9 disallowed patterns (the Editor will catch any that slip in; the writer aims to avoid them at draft time).

**Scope** — what is in scope for this pillar and what is explicitly out of scope (deferred to other pillars or the engagement boundary). Use the cross-pillar map from Step 4 to make in/out decisions concrete. Two short paragraphs or a brief in/out list.

Iterate with the user. Be brief — one or two short rounds per section is the goal. The user can request rewrites at any granularity (whole-section, paragraph, sentence).

**Lexicon proposals are captured inline.** When the user makes a term decision during drafting (a preferred orthography, an avoid-form → preferred-form pair, a disease abbreviation), capture it in a running `lexicon_additions` list as `<avoid form> -> <preferred form>` per §6.6. Surface the running list at the end of the iteration (before persisting in Step 6) for one final user confirmation; the final lexicon write happens in Step 6 alongside the pillar edit, in the same commit. Do not run a separate lexicon-prompt step at the end — that was a co-located approval gate the user had already implicitly granted by accepting term decisions during drafting.

### Step 6 — Write the drafted sections to the pillar file (and any lexicon additions)

Use the Edit tool, one Edit per section. For each of the three sections, the `old_string` matches the section heading + the `_TBD_` placeholder body (or whatever is currently there if the user is continuing an in-flight draft); the `new_string` is the section heading + the drafted body.

Examples of `old_string` in the M1-stub state (each with surrounding context for uniqueness):

```
## Strategic Rationale

_TBD — drafted in /pilar:pillar-narrative._

## Narrative
```

If the existing content is something else (continuation case), match against that.

If `lexicon_additions` from Step 5 is non-empty: read `lexicon.md`, draft a new entry per term per the §7.8 schema, and append at the end of the body (lexicon entries are insertion-ordered by convention; no numeric ids). Edit `lexicon.md` frontmatter `updated:` to today.

### Step 7 — Update frontmatter `updated:`

Capture today's ISO date with `!date +%F`. Edit the pillar file's frontmatter `updated:` field to today.

### Step 8 — Validate

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py <pillar_path> [lexicon.md]` (substituting the captured `<pillar_path>`; include `lexicon.md` if Step 6 edited it).

If validation fails, surface errors and correct via Edits before continuing.

### Step 9 — Approve commit (status flip + commit in one gate)

Run `git status` to show changes (pillar file edit, possibly `lexicon.md` if Step 6 appended entries).

Propose the commit message **and** the implied status flip in one prompt. The commit message records the status flip, so the prior pattern of asking "mark approved?" then "approve commit?" had the user authorizing the same decision twice.

```
APPROVE COMMIT

Records status flip: P-NN draft → narrative-approved
Commit message:
  feat(pilar): P-NN narrative approved (<name>)

  Pillar narrative drafted; Strategic Rationale, Narrative, and Scope
  populated from briefing-grounded drafting with cross-pillar
  consistency check. Status moved draft → narrative-approved.
  Next: /pilar:run-qc <pillar-path> for Editor engagement;
  /pilar:pillar-statements P-NN once Editor pass clears.

  (Append "; lexicon: <terms>" if Step 6 appended lexicon entries.)

Reply: approve / revise message: <new> / defer (leave status at draft, do not commit)
```

- **`approve`** → Edit the pillar frontmatter `status: draft` → `status: narrative-approved`. Then `git add pillars/<pillar-file> [lexicon.md] && git commit -m "<approved message>"`.
- **`revise message: <new>`** → use the new message; restate the prompt with the substitution; wait for `approve`.
- **`defer`** (or anything else) → leave `status: draft`. Do not commit. The working tree retains the edits; the writer can re-run the command later (continuation case) or commit by hand. The `defer-until-sprint-close` semantic is preserved by this branch.

### Step 10 — Brief the user on next steps

Tell the user (substituting):

> ✓ P-NN narrative drafted. Status: <draft | narrative-approved>.
>
> Next, per the sprint plan's `## QC Roles to Run`:
>
> - **`/pilar:run-qc <pillar-path> --context drafting`** — engages the Editor on the drafted narrative (and reads the lexicon + style guide for enforcement). Per §6.5, the Editor runs after narrative drafting and before user approval; if you have not yet approved the narrative (status still `draft`), do this before re-running this command to set `narrative-approved`.
> - When the narrative is approved, **`/pilar:pillar-statements P-NN`** drafts the supporting Scientific Statements and Reference Statements. The pillar moves to `statements-approved` after that drafting + Editor + Fact-Checker pass + your approval.

Stop.
