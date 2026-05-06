---
description: Snapshot mid-sprint progress without closing — pause notes appended to the active plan, single commit
allowed-tools: Bash, Read, Edit
---

Mid-sprint checkpoint for the active pilar sprint. Drafts a short snapshot of work done so far against the plan, appends it as a date-stamped sub-section under `## Pause Notes` in the active `plan.md`, and proposes a single commit. The sprint stays open — pause is observation, not amendment, and not closure.

Use this when you want to checkpoint progress mid-sprint without invoking the §5.3 four-option state machine. For scope changes mid-sprint use `/pilar:sprint-amend`. To close the sprint at the §5.3 checkpoint use `/pilar:sprint-close`.

## Procedure

### Step 1 — Detect active sprint

Run:

!`pwd && ls -1 roadmap.md 2>&1 && ls -1 sprints/ 2>&1`

If `roadmap.md` is missing, **stop** — recommend `/pilar:init`. If no `sprints/sprint-NN/` exists with a `plan.md` *but no* `summary.md`, **stop** — there is no active sprint to pause; recommend `/pilar:sprint-plan` to open a sprint, or `/pilar:sprint-close` if a draft summary is in progress.

Otherwise identify the active sprint (highest `sprint-NN/` with `plan.md` and no `summary.md`). Capture `N` and `NN`.

### Step 2 — Read state

Read:

- `sprints/sprint-NN/plan.md` — frontmatter (`opened`, `approved`, `project`, `sprint`), Objectives, Artifacts to Create or Modify, QC Roles to Run, Expected Outputs, Notes, any prior `## Amendments`, and any prior `## Pause Notes`.
- Run `!git log --oneline --since="<plan.md::approved>"` to see commits made during the sprint (or, if prior pauses exist, since the most recent pause's date — surface both for the writer's awareness).
- Run `!git status` to surface uncommitted changes.
- List any QC reports filed during this sprint under `qc/` (filename includes the sprint number).

### Step 3 — Draft the pause notes

Conduct a short interactive review with the writer. Brief — this is a checkpoint, not a retrospective. The agent proposes a 3–6-line draft covering:

- **What's been done** since the plan was approved (or since the last pause if any). Group by objective if helpful.
- **Files altered** during the period (from `git log --name-status`).
- **Open observations** — brief notes on anything surprising, unresolved, or worth flagging for the eventual sprint summary.
- **What's planned next** within the remaining sprint — the immediate next step, not a re-plan.

Iterate one short round if the writer wants tweaks.

### Step 4 — Append to `plan.md`'s `## Pause Notes` section

Capture today's ISO date with `!date +%F`.

Determine insertion point:

- If `## Pause Notes` already exists in `plan.md`: append the new sub-section after the last existing pause sub-section.
- If `## Pause Notes` does not exist: create the section. Insert it after `## Amendments` if that section exists, else after `## Notes`. Use the Edit tool with `old_string` matching the trailing section's last line + the file's trailing whitespace; `new_string` is those lines plus a blank line plus the new `## Pause Notes` H2 plus the first sub-section.

The sub-section format:

```markdown
### Pause <today's ISO date>

**Done.** <one or two short sentences on what's been done since the plan was approved or last pause>

**Files altered.** <comma-separated list, or "see git log --since=<approved>" for long lists>

**Observations.** <short notes; or "none" if there's nothing to flag>

**Next.** <the immediate next step within the remaining sprint>
```

Do **not** modify Objectives, Artifacts to Create or Modify, QC Roles to Run, Expected Outputs, Notes, or Amendments — those represent the plan's contract and the §5.2 amendment surface. Pause is observation.

Do **not** edit frontmatter — `sprint-plan` schema has no `updated:` field; `opened:` and `approved:` are immutable for the life of the sprint.

### Step 5 — Approve commit (single gate)

Run `!git diff sprints/sprint-NN/plan.md` to show the writer the appended sub-section.

Propose the commit message (substitute `<N>`, `<NN>`, and a one-line snapshot — typically the **Done.** line):

```
chore(pilar): pause sprint <N> — <one-line snapshot>

Mid-sprint pause. Notes appended to sprints/sprint-<NN>/plan.md
under ## Pause Notes. Sprint remains open; resume execution and
run /pilar:sprint-close when the sprint is complete.
```

Reply: `approve / revise commit: <new> / defer (leave plan.md edit in working tree, do not commit)`.

- **`approve`** → `git add sprints/sprint-NN/plan.md && git commit -m "<approved message>"` (heredoc).
- **`revise commit: <new>`** → use the new message; restate the prompt; wait for `approve`.
- **`defer`** (or anything else) → **stop without committing** — the appended pause-notes sub-section remains in the working tree.

### Step 6 — Brief next steps

Tell the writer:

> ✓ Sprint <N> paused. Notes appended to `sprints/sprint-<NN>/plan.md` under `## Pause Notes`. Sprint remains open.
>
> Resume execution. Re-run `/pilar:sprint-pause` for additional checkpoints if useful (each pause appends a new dated sub-section). For mid-sprint scope changes use `/pilar:sprint-amend`. When the sprint is complete, run `/pilar:sprint-close` to enter the §5.3 checkpoint.

Stop.
