---
description: Finalize the engagement after the consolidated draft clears whole-deliverable review (§6.9) — updates roadmap, proposes final commit, proposes engagement-handoff git tag with explicit user authorization
allowed-tools: Bash, Read, Edit
---

Finalize a pilar engagement per §6.9 of `scp-plugin-spec.md`. Run this **after** at least one consolidated draft has cleared the whole-deliverable review (`/pilar:run-qc --consolidated`) and the user has reviewed the SA / FC / Editorial reports for that draft.

Spec §6.9: "Once a consolidated draft has cleared the whole-deliverable review and any required client review, the Primary Collaborator finalizes the platform package. The roadmap is updated to reflect completion. The final state is committed and tagged."

This command does not auto-tag. The git tag is the engagement's handoff record and is user-gated per the saved release-gating policy applied to engagement tags: tags are never created without explicit per-tag user authorization. The command proposes the tag name and waits for `y` before tagging.

## Procedure

### Step 1 — Detect engagement state

Run:

!`pwd && ls -1 roadmap.md briefing.md 2>&1 | head`

If `roadmap.md` is missing, **stop** — recommend `/pilar:init` from a fresh directory; this is not a pilar engagement repo.

### Step 2 — Locate the latest consolidated draft

Run:

!`ls -1 consolidated/cd-*.md 2>/dev/null | sort | tail -1`

If no `consolidated/cd-NNN.md` exists, **stop**:

> No consolidated draft exists yet. Run `/pilar:consolidate` to assemble one from the approved pillars, then `/pilar:run-qc --consolidated <path>` to run the whole-deliverable review, then return here.

Otherwise, capture `<cd-id>` (e.g. `cd-001`) and `<artifact-path>` (e.g. `consolidated/cd-001.md`).

### Step 3 — Locate the WDR reports for this draft

The whole-deliverable review for `<cd-id>` produces three reports — editorial, fact-check, strategic-alignment — saved by `/pilar:run-qc --consolidated` under `qc/`. Find:

- Editorial report: `qc/editorial-reports/sprint-*-editorial-<cd-id>.md` (most recent if multiple).
- Fact-check report: `qc/fact-check-reports/sprint-*-fact-check-<cd-id>.md` (most recent if multiple).
- Strategic-alignment report: `qc/strategic-alignment-reports/sprint-*-strategic-<cd-id>.md` (most recent if multiple).

Run `ls -1 qc/editorial-reports/sprint-*-editorial-<cd-id>.md qc/fact-check-reports/sprint-*-fact-check-<cd-id>.md qc/strategic-alignment-reports/sprint-*-strategic-<cd-id>.md 2>&1` (substituting the captured `<cd-id>`).

If any of the three is missing, **stop**:

> The whole-deliverable review for `<cd-id>` is incomplete — `<list missing report kinds>` not found. Run `/pilar:run-qc --consolidated <artifact-path>` to complete the review, then return here.

### Step 4 — Report-clearance check (user-confirmed)

Read each of the three reports and parse their Findings sections. For each finding with `severity: high`, capture its `target:` and `issue:` lines. The reports do not carry a `status:` or `resolved:` field — clearance is the user's judgment, not the report's.

If at least one `severity: high` finding exists across the three reports, present the list to the user:

> The following high-severity findings were filed against `<cd-id>`. For each, confirm that it has been addressed in a follow-up sprint (typically by revising the affected pillars, re-consolidating to a later `cd-NNN`, and re-running the whole-deliverable review):
>
> - `<finding-id>` (`<report-kind>`): target `<target>` — `<issue (one line)>`
> - …
>
> Has each of the above been addressed? Respond `y` only if you are certain; respond `n` to abort handoff and reopen the affected pillars.

Wait for `y`. On `n` or anything other than `y`, **stop**:

> Handoff aborted. Recommended next steps: revise the affected pillars (`/pilar:pillar-statements <pillar-id>` or direct edits), then `/pilar:consolidate` to produce `cd-<NNN+1>`, then `/pilar:run-qc --consolidated consolidated/cd-<NNN+1>.md` to re-run the whole-deliverable review on the revised draft. Return to `/pilar:handoff` once the new draft clears.

If no `severity: high` findings exist, **proceed silently** — the draft is clear by report inspection (medium and low findings are surfaced for awareness but not gate handoff).

### Step 5 — Update the roadmap

Capture today's ISO date via `!date +%F`. Read `roadmap.md`. Make these targeted edits (show the user the diff via `!git diff roadmap.md` before proposing the commit):

1. **Frontmatter** `updated:` → today's ISO date.
2. **`## Status`** — replace the current status narrative with a terminal narrative. Suggested wording (refine with the user as appropriate to the engagement's specific shape):

   ```
   Engagement complete. Consolidated draft `<cd-id>` was delivered on <today's date> after clearing whole-deliverable review (Editor, Fact-Checker, Strategic Reviewer per §6.8). The platform package — briefing, <count> approved pillars, lexicon, style guide, and the final consolidated draft — is committed at this state. Per §6.9, the engagement closes at this point; subsequent client-feedback rounds reopen via `/pilar:sprint-plan` and follow the re-entry sprint pattern documented there.
   ```

3. **`## Decisions Log`** — append a new row to the table. Format mirrors the existing Decisions Log style. Suggested entry:

   ```
   | <today's date> | Engagement handoff: consolidated draft `<cd-id>` delivered. | Whole-deliverable review (Editor, Fact-Checker, Strategic Reviewer) cleared per §6.8; user confirmed at handoff. | §6.9, P8 |
   ```

Do **not** edit `## Sprint History` — handoff is a ceremonial step after the final WDR sprint closes, not a sprint itself. Sprint History remains sprints-only.

### Step 6 — Propose the final commit

Run `!git status` to show the user the staged/unstaged changes. Propose:

```
chore(pilar): handoff — consolidated draft <cd-id> delivered

Engagement complete per §6.9. Roadmap Status set to terminal narrative;
Decisions Log records the handoff date and the delivered consolidated
draft. The whole-deliverable review for <cd-id> cleared (Editor,
Fact-Checker, Strategic Reviewer per §6.8); high-severity findings
addressed in follow-up sprints and confirmed by the user at handoff.
```

Wait for explicit user approval. On approval:

```bash
git add roadmap.md
git commit -m "..."  # heredoc with the approved message
```

If the user wants to revise the message, accept their version. If the user defers the commit, **stop without committing AND without proposing the tag** — do not tag against an uncommitted state.

### Step 7 — Propose the engagement handoff tag (explicit user authorization required)

Per the saved release-gating policy applied analogously to engagement tags: never tag without explicit per-tag user authorization for that specific tag.

Run `!git rev-parse HEAD` to capture the commit SHA the tag would point at. Propose:

```
Tag name (default): engagement-handoff-<today's date>-<cd-id>
Tag message:        Engagement handoff. Consolidated draft <cd-id> delivered on <today's date> after clearing whole-deliverable review per §6.8.
Tagged commit:      <short-sha> (from Step 6)

Authorize tag 'engagement-handoff-<today's date>-<cd-id>'? [y/N]
```

Wait for `y` (case-sensitive — anything else does not authorize).

- On `y`: run `!git tag -a engagement-handoff-<today's date>-<cd-id> -m "<tag message>"`. Confirm with `!git tag -l "engagement-handoff-*"` and report the new tag to the user. Do not push — pushing tags is a separate user action.
- On anything other than `y`: do not tag. Report:

  > Tag not created. To create later, run: `git tag -a engagement-handoff-<today's date>-<cd-id> -m "Engagement handoff. Consolidated draft <cd-id> delivered on <today's date>."`

If the user proposes a different tag name, accept it (still requires explicit `y` after restating the proposal).

### Step 8 — Brief the user on next steps

Tell the user:

> ✓ Engagement handed off. Consolidated draft `<cd-id>` is the delivered state. Roadmap reflects completion; Decisions Log records the handoff. <If tagged: "Tag `engagement-handoff-<date>-<cd-id>` created at `<short-sha>`."> <If not tagged: "Tag deferred — see message above for the manual command.">
>
> The engagement is now in client-review territory. Per §6.9, Claude Code's involvement pauses while you take the consolidated draft to the client. Client feedback intake resumes via `/pilar:sprint-plan` — when the post-handoff state is detected, the command proposes a templated client-feedback re-entry sprint plan that follows the §6.9 pattern (reopen affected pillars, revise statements, re-consolidate to `cd-<NNN+1>`, re-run `/pilar:run-qc --consolidated` on the new draft, sprint-end checkpoint as usual). Subsequent client rounds repeat this pattern.

Stop.
