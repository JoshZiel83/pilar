---
description: Open a new sprint — drafts the plan from roadmap state; you approve before commit
allowed-tools: Bash, Read, Write, Edit
---

Open a new sprint in the current pilar engagement. Drafts a sprint plan from the roadmap's "Next Sprint Scope" and the prior sprint summary's "Next Sprint Proposed Scope", refines it with the user, writes `sprints/sprint-NN/plan.md`, updates `roadmap.md`, and proposes the commit message — waiting for explicit user approval before committing.

## Sprint plan schema (use this to seed the new plan)

@${CLAUDE_PLUGIN_ROOT}/schemas/sprint-plan.md

## Procedure

### Step 1 — Confirm we are in a pilar engagement

Run:

!`pwd && ls -1 roadmap.md CLAUDE.md 2>&1 | head -5`

If `roadmap.md` does not exist at the cwd root, **stop** and tell the user this directory is not a pilar engagement repo — recommend `/pilar:init` from a fresh directory. Do not proceed.

### Step 2 — Read engagement state

Read these files and capture key state:

- `roadmap.md` — capture frontmatter (`project`, `current_sprint`), and the body sections "Status", "Active Workstreams", "Next Sprint Scope", "Sprint History".
- The most recent `sprints/sprint-NN/summary.md` if any exist (highest NN). Capture the summary's `human_response`, "Next Sprint Proposed Scope", and "Open Items".

Compute the new sprint number = `roadmap.md::current_sprint + 1`. Call this `N` for the rest of the procedure.

### Step 3 — Refuse if a sprint is already open

If `sprints/sprint-N/plan.md` exists OR `sprints/sprint-<current_sprint>/` exists *without* a corresponding `summary.md`, a sprint is already open. **Stop** and tell the user one of:

- "Sprint <current_sprint> is already open and has not been closed. Run `/pilar:sprint-close` to close it before planning Sprint <new>."
- "Sprint <current_sprint> appears to be in flight (plan present, summary absent). Run `/pilar:sprint-amend` to revise its plan, or `/pilar:sprint-close` if execution is complete."

Do not proceed.

### Step 4 — Determine sprint scope

#### If `N == 1` (briefing sprint, special case)

The first sprint is always briefing. Pre-populate the plan with these defaults; refine with the user only if they want to expand:

- **Objectives.**
  1. Capture the engagement briefing (product, indication, lifecycle, audiences, strategic priorities, competitive context, constraints, evidence generation activities, timeline) by interviewing the writer.
  2. Initialize the engagement roadmap with briefing-derived strategic priorities and the anticipated-inputs list.
  3. Confirm or develop the lexicon and style guide (if no client-supplied versions, record the decision to develop both during the engagement per §6.6).
  4. Propose the next-sprint scope.
- **Artifacts to Create or Modify.** `briefing.md`, `roadmap.md`, `sprints/sprint-01/plan.md` (this), `sprints/sprint-01/summary.md` (created at sprint close).
- **QC Roles to Run.** None — briefing produces no drafted scientific copy; QC engages on subsequent drafting sprints.
- **Expected Outputs.** Complete `briefing.md`; `roadmap.md` reflecting briefing-derived state; signed-off Sprint 1 summary (`human_response: confirmed`).
- **Notes.** Briefing is itself a sprint per §5.3 and exercises the full sprint-end checkpoint pattern before any drafting work begins.

#### If `N > 1` (subsequent sprint)

Derive scope from these inputs in order of priority:

1. The prior summary's "Next Sprint Proposed Scope" (the writer signed off on it at the prior checkpoint).
2. The roadmap's "Next Sprint Scope" section (canonical engagement-level next-step list, possibly augmented by the writer between sprints).
3. The roadmap's "Open Items" lists across prior sprint summaries, if any are flagged for this sprint.

Draft the plan's Objectives, Artifacts to Create or Modify, QC Roles to Run, and Expected Outputs from those inputs. Be specific; avoid generic restatement.

For QC Roles: per §8 sequencing, sprints that produce drafted pillar / scientific-statement / reference-statement content typically run Editor-then-Fact-Checker via `/pilar:run-qc`. Strategic Reviewer engages only on sprints producing or revising a consolidated draft. Reflect this in the QC Roles to Run section.

### Step 5 — Refine the plan with the user

Present the drafted plan to the user. Ask for refinements: scope adjustments, additional objectives, removed scope, QC scope changes. Iterate until the user is satisfied. Be brief — one or two short rounds is the goal.

### Step 6 — Write `sprints/sprint-NN/plan.md`

Capture today's ISO date with `!date +%F`. Create the directory and write the plan file.

The directory name is `sprints/sprint-NN/` where `NN` is the new sprint number zero-padded to two digits (e.g., `sprint-01`, `sprint-12`). Run `mkdir -p sprints/sprint-NN`.

The file's frontmatter:

- `artifact: sprint-plan`
- `sprint: <N>` (integer, no padding in the YAML value)
- `project: <project from roadmap frontmatter>`
- `opened: <today's ISO date>`
- `approved: <today's ISO date>` (planning + approval happen together; if the user defers approval the command stops without writing the file)

The body uses the schema's H2 sections (`## Objectives`, `## Artifacts to Create or Modify`, `## QC Roles to Run`, `## Expected Outputs`, `## Notes`) populated with the refined content from Step 4/5.

### Step 7 — Update `roadmap.md`

Make two targeted edits to `roadmap.md`:

1. Update `current_sprint:` in frontmatter to the new value `N`.
2. Update `updated:` in frontmatter to today's ISO date.
3. Append to "## Active Workstreams" a one-line entry: `- Sprint <N>: <one-line objective summary>` (in progress).

Show the user the diff (use `git diff roadmap.md` after writing) before committing. Do NOT touch "## Sprint History" — that is `/pilar:sprint-close`'s responsibility.

### Step 8 — Propose the commit

Run `git status` to show staged/unstaged changes. Propose this commit message (substitute `<N>` and the one-line objective summary):

```
chore(pilar): open sprint <N> — <objective summary>

Sprint <N> plan opened. <One-sentence elaboration of scope: e.g.
"Briefing sprint to capture Aurelis ALR-217 engagement context." or
"Initial evidence synthesis from current KB seed.">
```

Wait for explicit user approval. If approved, run:

```bash
git add sprints/sprint-NN/plan.md roadmap.md
git commit -m "..."  # heredoc with the approved message
```

If the user wants to revise the message, accept their version. If the user wants to defer the commit, stop without committing — leave the files in the working directory.

### Step 9 — Brief the user on next steps

Tell the user:

> ✓ Sprint <N> open. Plan committed: `sprints/sprint-<NN>/plan.md`. Roadmap `current_sprint` is now <N> and Active Workstreams reflects the open sprint.
>
> Next: execute the sprint. For the briefing sprint, that means conducting the briefing in conversation. For drafting sprints, that means drafting pillar narratives / scientific statements / reference statements (P5 + P7 of pilar's roadmap will provide dedicated drafting commands; for now do drafting in-conversation and use existing tooling).
>
> When execution is complete, run `/pilar:sprint-close` to enter the checkpoint.

Stop.
