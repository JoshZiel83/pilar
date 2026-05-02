---
description: Amend the active sprint plan — for in-flight scope changes; you approve the revised plan before commit
allowed-tools: Bash, Read, Write, Edit
---

Amend the in-flight pilar sprint plan. Per §5.2: "If during execution the user determines the plan is incomplete or needs to change, an amended plan is proposed by the Primary Collaborator, approved by the user, and committed before further work proceeds." This command is the canonical surface for that flow.

## Procedure

### Step 1 — Confirm an active sprint exists

Run:

!`pwd && ls -1 roadmap.md 2>&1 && ls -1 sprints/ 2>&1`

If `roadmap.md` is missing, **stop** — recommend `/pilar:init`. If no `sprints/sprint-NN/` exists with a `plan.md` *but no* `summary.md`, **stop** — there is no active sprint to amend; recommend `/pilar:sprint-plan` if the user wants to open a new sprint, or `/pilar:sprint-close` if a draft summary is in progress.

Otherwise identify the active sprint (highest `sprint-NN/` with `plan.md` and no `summary.md`). Capture `N` and `NN`.

### Step 2 — Read the current plan

Read `sprints/sprint-NN/plan.md`. Capture frontmatter, current Objectives, current Artifacts to Create or Modify, current QC Roles to Run, current Expected Outputs, current Notes, and any prior Amendments at the bottom.

### Step 3 — Capture the requested change from the user

Ask the user — in plain conversation — to describe what is changing and why. Examples of valid amendments:

- "Add an objective: synthesize the elderly-subgroup data from the new ASH abstract that arrived mid-sprint."
- "Remove the Editor QC pass — we're not producing drafted copy this sprint after all."
- "Expand Artifacts to include `pillars/pillar-04-clinical-evidence/pillar.md` because we're folding pillar drafting into this sprint."

Wait for the user's description.

### Step 4 — Draft the amended plan

Compute the diff between the current plan and the amended plan. Specifically identify:

- **Added** objectives, artifacts, QC roles, expected outputs.
- **Removed** items in the same categories.
- **Changed** items (e.g. an objective's wording was clarified).

Construct the amended plan body by applying the changes to the current sections. Preserve sections the user did not touch verbatim.

Append (or create) an `## Amendments` section at the bottom of the plan, with a date-stamped entry capturing the delta and the user's stated reason:

```
## Amendments

### Amendment <today's ISO date>

**Reason.** <user's rationale, paraphrased tightly>

**Changes.**
- Added: <list>
- Removed: <list>
- Changed: <list>
```

If an `## Amendments` section already exists from prior amendments, append the new entry below the existing ones (most-recent at bottom).

### Step 5 — Present diff and confirm

Present the user with a clear diff: what each section looked like before, what it looks like now, and the new Amendment entry. Iterate one short round if the user wants tweaks.

Update the plan's frontmatter `approved:` field to today's ISO date, since the amended plan needs fresh approval per §5.2.

### Step 6 — Write the amended plan and propose commit

Overwrite `sprints/sprint-NN/plan.md` with the amended content.

Show `git diff sprints/sprint-NN/plan.md`. Propose this commit message (substitute the delta summary):

```
chore(pilar): amend sprint <N> plan — <delta summary>

Sprint <N> plan amended per §5.2. <One-sentence reason from the
user's rationale.> Approved date refreshed; Amendments section
records the delta.
```

Wait for explicit user approval. On approval:

```bash
git add sprints/sprint-NN/plan.md
git commit -m "..."
```

If the user wants to revise the message, accept their version. If the user wants to defer the commit, stop without committing.

### Step 7 — Brief the user on next steps

Tell the user:

> ✓ Sprint <N> plan amended. The amended plan is committed; resume execution under the new scope. Run `/pilar:sprint-close` when execution is complete to enter the checkpoint.

Stop.
