---
description: Close the active sprint at the checkpoint — drafts summary; you respond Confirm / Request revisions / Defer / Rewind
allowed-tools: Bash, Read, Write, Edit
---

Close the active pilar sprint. Drafts the sprint summary from work actually completed since the plan was approved, presents it to the user at the checkpoint, then executes the four-option state machine from Appendix B of `IMPLEMENTATION_ROADMAP.md`. Per decision #4, every commit is proposed and waits for explicit user approval — there are no auto-commits.

## Sprint summary schema (use this to seed the new summary)

@${CLAUDE_PLUGIN_ROOT}/schemas/sprint-summary.md

## Procedure

### Step 1 — Confirm an active sprint exists

Run:

!`pwd && ls -1 roadmap.md 2>&1 && ls -1 sprints/ 2>&1`

If `roadmap.md` is missing, **stop** — recommend `/pilar:init`. If `sprints/` is empty or all sprint directories already contain a `summary.md`, **stop** — recommend `/pilar:sprint-plan` to open a new sprint first. Otherwise, identify the active sprint as the highest-numbered `sprints/sprint-NN/` whose `plan.md` exists *without* a corresponding `summary.md`. Capture `N` and the sprint number padded to two digits as `NN`.

### Step 2 — Read the active sprint plan and engagement state

Read:

- `sprints/sprint-NN/plan.md` — frontmatter (`opened`, `approved`, `project`, `sprint`), Objectives, Artifacts to Create or Modify, QC Roles to Run, Expected Outputs, Notes, and any Amendments appended at the bottom.
- `roadmap.md` — current Active Workstreams, current Next Sprint Scope, prior Sprint History entries, current Decisions Log.
- Run `!git log --oneline --since="<plan.md::approved>"` and `!git status` to surface what was committed during the sprint and what is uncommitted.
- `qc/fact-check-reports/`, `qc/editorial-reports/`, `qc/strategic-alignment-reports/` — list any reports filed during this sprint (filename usually includes the sprint number) and capture their summaries.

### Step 3 — Draft the sprint summary

Conduct a short interactive review with the user to capture what actually happened. Be brief — this is checkpoint plumbing, not a retrospective. Ask only what cannot be inferred from git log + plan.

Write `sprints/sprint-NN/summary.md` with frontmatter set initially as:

- `artifact: sprint-summary`
- `sprint: <N>`
- `project: <project from plan>`
- `opened: <plan's opened date>`
- `closed: <today's ISO date — get from `!date +%F`>`
- `human_response: pending`

Body sections populated:

- **Objectives as Planned.** Mirror the plan's Objectives.
- **Work Completed.** Prose paragraph of what actually happened, grounded in the git log and the artifacts under review.
- **Files Altered.** Bullet list of files created/modified during the sprint (from `git log --name-status` since `approved:`).
- **QC Roles Run and Findings.** For each QC report filed: brief one-line summary plus link to the report file. If no QC ran (e.g. briefing sprint), state "None — <reason>."
- **Artifacts to Review.** List of artifacts the user is being asked to review at this checkpoint (typically the same as Files Altered minus mechanical files like .gitkeep additions).
- **Decisions.** Bullet list of decisions taken during the sprint that should propagate to the roadmap's Decisions Log (substantive interpretive decisions only — not routine choices).
- **Open Items.** Items deferred, blocked, or awaiting external input. Carries forward to next sprint or to the engagement's Anticipated Inputs depending on context.
- **Human Response.** `_pending — populated when the user responds at the checkpoint._`
- **Next Sprint Proposed Scope.** Specific list. Used by `/pilar:sprint-plan` for the next sprint.

### Step 4 — Present at the checkpoint and ask the user

Present the drafted summary. Ask the user to choose one of:

> Sprint <N> checkpoint. Respond with one of:
>
> - **Confirm.** The sprint closes. The summary stands; we update the roadmap and propose the next sprint.
> - **Request revisions.** You provide feedback. If the additional work is bounded (small in-scope adjustments), we amend the plan and continue executing. If the work is substantive, we record the items in next-sprint scope and close this sprint.
> - **Defer.** The work is parked pending external input (e.g. evidence enlargement, client decision). Deferred items go into Open Items.
> - **Rewind.** Earlier-approved work needs to be reopened. We plan a new sprint with that scope; the reopen is recorded in the roadmap's Decisions Log.

Wait for the user's choice.

### Step 5 — Execute the chosen branch

#### Branch A — Confirm

1. Capture the user's verbatim feedback (if any) and write it to the summary's "## Human Response" section under a `confirmed —` prefix. If no feedback was provided, use `confirmed.` alone.
2. Edit the summary's frontmatter `human_response:` from `pending` to `confirmed`.
3. Update `roadmap.md` with three targeted edits (show diff before commit):
   - Frontmatter `updated:` → today's ISO date.
   - "## Sprint History" → append a line `- Sprint <N>: <one-line work summary> ([summary](sprints/sprint-<NN>/summary.md))`.
   - "## Active Workstreams" → remove the Sprint <N> entry added by `/pilar:sprint-plan`.
   - "## Next Sprint Scope" → replace its body with the summary's "Next Sprint Proposed Scope" content.
   - "## Status" → update narrative to reflect new state.
4. Propose the commit:

   ```
   chore(pilar): close sprint <N> (confirmed) — <one-line work summary>

   Sprint <N> closed at checkpoint with human_response: confirmed.
   Roadmap updated: Sprint History entry added, Active Workstreams
   cleared of Sprint <N>, Next Sprint Scope replaced with the summary's
   Next Sprint Proposed Scope.
   ```

5. Wait for approval; on approval, `git add sprints/sprint-NN/summary.md roadmap.md && git commit -m "..."`.
6. Tell the user: "✓ Sprint <N> closed. Run `/pilar:sprint-plan` when ready to open Sprint <N+1>."

#### Branch B — Request revisions

Ask: "Are these revisions bounded (small adjustments inside the current sprint scope) or substantive (warrant a new sprint)?"

##### B1 — bounded

1. Do NOT close the summary. Leave `human_response: pending`. Do NOT commit anything.
2. Capture the requested revision items and present them.
3. Recommend `/pilar:sprint-amend` if the plan needs to change to reflect the new scope; otherwise tell the user to execute the additional work and re-run `/pilar:sprint-close` when done.

##### B2 — substantive

1. Capture the user's verbatim feedback and append to the summary's "## Next Sprint Proposed Scope" with a `(carried from Sprint <N> revisions request)` annotation on the new items.
2. Edit summary frontmatter `human_response:` → `confirmed`. Write a Human Response body of `confirmed with revisions deferred to Sprint <N+1>: <verbatim feedback>`.
3. Update roadmap as in Branch A (Sprint History entry notes "(revisions deferred to next sprint)"; Active Workstreams cleared; Next Sprint Scope absorbs the deferred items).
4. Propose commit:

   ```
   chore(pilar): close sprint <N> (revisions deferred) — <one-line summary>

   Sprint <N> closed at checkpoint with human_response: confirmed.
   Substantive revision requests deferred to Sprint <N+1> and recorded
   in the summary's Next Sprint Proposed Scope and roadmap's Next
   Sprint Scope.
   ```

5. Same approval/commit flow as Branch A.

#### Branch C — Defer

1. Ask the user what specifically is being deferred and what external input is awaited.
2. Capture deferred items in the summary's "## Open Items" section with a `deferred — awaiting <reason>` prefix on each.
3. Edit summary frontmatter `human_response:` → `deferred`. Write a Human Response body of `deferred — <reason>`.
4. Update roadmap:
   - Frontmatter `updated:` → today.
   - Sprint History entry: `- Sprint <N>: <work summary> (deferred — awaiting <reason>) ([summary](...))`.
   - Active Workstreams: remove Sprint <N>; add a `Deferred:` sub-list referencing the deferred items.
   - Next Sprint Scope: append deferred items so they aren't lost when external input arrives.
5. Propose commit:

   ```
   chore(pilar): close sprint <N> (deferred) — awaiting <reason>

   Sprint <N> closed at checkpoint with human_response: deferred.
   Deferred items recorded in summary Open Items and roadmap Next
   Sprint Scope; awaiting <reason> before continuation.
   ```

6. Same approval/commit flow as Branch A.
7. Tell the user: "✓ Sprint <N> deferred. When <reason> resolves, run `/pilar:sprint-plan` to open the continuation sprint."

#### Branch D — Rewind

1. Ask the user explicitly: "Which earlier-approved work needs to be reopened? Reference specific pillars / scientific statements / reference statements / decisions by id." Capture the answer verbatim — this is the rewind scope.
2. Per §6.5 and the IMPLEMENTATION_ROADMAP append-only ID rule: ids of reopened items are preserved (not reused); new ids increment from the highest id ever assigned. Verify with the user that they understand reopened ids carry forward.
3. Edit summary frontmatter `human_response:` → `rewind`. Write a Human Response body of `rewind — <verbatim user statement of scope>`.
4. Update roadmap:
   - Frontmatter `updated:` → today.
   - Sprint History entry: `- Sprint <N>: <work summary> (rewind — see decisions log) ([summary](...))`.
   - Active Workstreams: remove Sprint <N>; add the rewind scope as a planned Sprint <N+1> entry.
   - Next Sprint Scope: replace with the rewind scope (this is what the next sprint will tackle).
   - **Decisions Log** (this is mandatory for rewind): append a row like `| <today> | Rewind: reopen <scope> from Sprint <prior-N> | <user's rationale> | Sprint <N> → <N+1>, §6.5 |`.
5. Propose commit:

   ```
   chore(pilar): close sprint <N> (rewind) — reopen <scope summary>

   Sprint <N> closed at checkpoint with human_response: rewind.
   Earlier-approved work reopened per user request: <scope summary>.
   Decisions Log entry recorded in roadmap. Sprint <N+1> will tackle
   the reopened scope; ids of reopened items are preserved per §6.5
   append-only rule.
   ```

6. Same approval/commit flow as Branch A.
7. Tell the user: "✓ Sprint <N> closed with rewind. Run `/pilar:sprint-plan` to open Sprint <N+1> against the reopened scope."

### Step 6 — If the chosen branch did not commit (Branch B1)

Tell the user: "Sprint <N> remains open. The summary draft is preserved at `sprints/sprint-<NN>/summary.md` (uncommitted). Continue execution; revise the plan with `/pilar:sprint-amend` if needed; run `/pilar:sprint-close` again when ready."

Stop.
