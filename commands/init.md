---
description: Scaffold a pilar engagement repository in the current directory
allowed-tools: Bash, Read, Write
---

Scaffold a new pilar engagement repository in the user's current working directory, following §3 of the natural-language spec. This is the first action a medical writer takes when starting a new SCP development engagement.

## Engagement-artifact schema templates (use these to seed the engagement's stubs)

@${CLAUDE_PLUGIN_ROOT}/schemas/roadmap.md
@${CLAUDE_PLUGIN_ROOT}/schemas/briefing.md
@${CLAUDE_PLUGIN_ROOT}/schemas/style-guide.md
@${CLAUDE_PLUGIN_ROOT}/schemas/lexicon.md
@${CLAUDE_PLUGIN_ROOT}/schemas/kb-manifest.md
@${CLAUDE_PLUGIN_ROOT}/schemas/evidence-gaps.md
@${CLAUDE_PLUGIN_ROOT}/schemas/aspirational-statements.md

## Procedure

Execute the following steps in order. Stop and ask the user before any irreversible action (commit, branch creation). Do not auto-commit.

### Step 1 — Verify the target directory is suitable

Run:

!`pwd && ls -1A`

The current working directory must be empty OR contain only one or more of: `.git`, `.gitignore`, `README.md`, `CLAUDE.md`. If anything else is present, **stop** — tell the user the directory must be near-empty and ask them to invoke `/pilar:init` from a fresh directory. Do not proceed.

### Step 2 — Initialize git if absent

If `.git/` does not exist, run `git init -b main`. Do not stage or commit anything yet.

### Step 3 — Create the §3 directory tree

Run a single bash command that creates the directory tree and drops `.gitkeep` files in each leaf so git tracks the empty directories:

```bash
mkdir -p \
  knowledge-base/clinical \
  knowledge-base/preclinical \
  knowledge-base/guidelines \
  knowledge-base/competitor \
  knowledge-base/other \
  pillars \
  registers \
  explorations \
  consolidated \
  qc/fact-check-reports \
  qc/editorial-reports \
  qc/strategic-alignment-reports \
  sprints

for d in \
  knowledge-base/clinical knowledge-base/preclinical knowledge-base/guidelines knowledge-base/competitor knowledge-base/other \
  pillars registers explorations consolidated \
  qc/fact-check-reports qc/editorial-reports qc/strategic-alignment-reports \
  sprints
do
  touch "$d/.gitkeep"
done
```

Note on `explorations/`: this directory holds optional per-pillar exploration notes produced by `/pilar:explore` (a P7 refinement). Files in this directory are scratch markdown — not §7 artifacts — and are not validated by `scripts/validate-schemas.py`. The directory is committed (with `.gitkeep`) so future `/pilar:explore` invocations have a stable target path.

Note on `consolidated/`: this directory holds assembled `consolidated/cd-NNN.md` whole-deliverable views produced by `/pilar:consolidate` (P8). Each `cd-NNN` is a `consolidated-draft` artifact (`schemas/consolidated-draft.md`) that the whole-deliverable review (`/pilar:run-qc --consolidated`) operates on. The directory is committed (with `.gitkeep`) so the first `/pilar:consolidate` invocation has a stable target.

### Step 4 — Intake interview

Ask the user — in plain conversation, one cohesive prompt — for the five fields needed to populate the engagement-artifact frontmatter:

1. **Project ID** (kebab-case, e.g. `aurelis-alr217-dlbcl-2026`)
2. **Client** (organization name)
3. **Product** (compound or brand name)
4. **Indication**
5. **Lifecycle stage** (e.g. "post-Phase 2 / pre-launch ~18 months")

Wait for all five answers before proceeding. If the user is unsure of any field, suggest a sensible placeholder (e.g. derive Project ID from `<client>-<product>-<indication-slug>-<year>`) and confirm.

Capture today's ISO date with `!date +%F`. The same date is used as `created:` and `updated:` for every stub artifact below.

### Step 5 — Write the engagement-artifact stubs

For every file below, populate frontmatter from the intake answers + today's date, keep every H2 heading from the schema, and replace `<placeholder>` body text with `_TBD — to be filled during Sprint 1 (briefing)._` unless otherwise noted. The result is a set of empty-but-valid documents that pass `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py` immediately.

#### 5a — `roadmap.md` (engagement repo root)

From the roadmap schema. Frontmatter:

- `artifact: roadmap`
- `project: <user's Project ID>`
- `client: <user's Client>`
- `product: <user's Product>`
- `indication: <user's Indication>`
- `lifecycle_stage: <user's Lifecycle>`
- `created: <today>`
- `updated: <today>`
- `current_sprint: 0`

Body sections retained from the schema with `_TBD — to be filled during Sprint 1 (briefing)._` placeholders.

#### 5b — `briefing.md` (engagement repo root)

From the briefing schema. Frontmatter:

- `artifact: briefing`
- `project: <user's Project ID>`
- `created: <today>`
- `updated: <today>`

Body sections retained with `_TBD — to be filled during Sprint 1 (briefing)._` placeholders.

#### 5c — `style-guide.md` (engagement repo root)

Copy the style-guide schema verbatim — including the §9 disallowed-pattern defaults under "## Disallowed Patterns" — and adjust the frontmatter:

- `artifact: style-guide`
- `project: <user's Project ID>`
- `source: developed`
- `updated: <today>`

The `<placeholder>` body text in "Voice and Tone", "Sentence Construction", "Citation Conventions", "Evidence Description Conventions", and "Other" is replaced with `_TBD — to be filled during Sprint 1 (briefing) or as the engagement progresses._`. The "## Disallowed Patterns" section keeps its full content (the §9 defaults) verbatim, including the "### Overrides" subsection (which gets `No client overrides yet.` as body text).

#### 5d — `lexicon.md` (engagement repo root)

From the lexicon schema. Frontmatter:

- `artifact: lexicon`
- `project: <user's Project ID>`
- `source: developed`
- `updated: <today>`

Body: keep the `# Lexicon` H1; remove the `### <term>` example entry (the schema's example is illustrative — the engagement starts with no entries). The lexicon accumulates entries during pillar drafting (P5/P7 territory).

#### 5e — `knowledge-base/manifest.md`

From the kb-manifest schema. Frontmatter:

- `artifact: kb-manifest`
- `project: <user's Project ID>`
- `updated: <today>`

Body: keep the `# Knowledge Base Manifest` H1 and the `## Entries` H2; remove the `### <ref-id>` example entry. KB ingestion (P6 territory) populates entries.

#### 5f — `registers/evidence-gaps.md`

From the evidence-gaps schema. Frontmatter:

- `artifact: evidence-gaps`
- `project: <user's Project ID>`
- `updated: <today>`

Body: keep the `# Evidence Gaps` H1 and both `## Open Gaps` and `## Closed Gaps` H2 sections; remove the `### <gap-id>` example entry. Body of "## Closed Gaps" reads `<no closed gaps yet>`.

#### 5g — `registers/aspirational-statements.md`

From the aspirational-statements schema. Frontmatter:

- `artifact: aspirational-statements`
- `project: <user's Project ID>`
- `updated: <today>`

Body: keep the `# Aspirational Statements` H1; remove the `### <asp-id>` example entry. Body reads `<no aspirational statements yet>`.

### Step 6 — Drop the engagement `CLAUDE.md`

Write the following content to `CLAUDE.md` at the engagement repo root, with no substitutions — it is a static template that triggers session resumption (§5.4) on every Claude Code session start in this directory.

```markdown
# pilar engagement — Claude Code session guide

This repository is a pilar engagement. The pilar plugin (https://github.com/JoshZiel83/pilar) drives the workflow. Every session in this directory should follow the procedure below.

## At session start — orient yourself

Before doing any work, read these files in order and briefly state the engagement's current state to the user:

1. `roadmap.md` — frontmatter (current_sprint, lifecycle_stage), Status, Active Workstreams, Next Sprint Scope.
2. The most recent `sprints/sprint-NN/summary.md` if any exist (highest NN). The summary's Human Response section tells you whether the prior sprint closed Confirmed, was Deferred, or was Rewound.
3. The active sprint plan at `sprints/sprint-NN/plan.md` for the current sprint, if a sprint is open.

State the orientation in one short paragraph: "Currently in Sprint N (briefing/per-pillar/consolidation). Last sprint closed <Confirmed|Deferred|Rewound> on <date>. Active workstreams: <list>. Open items: <count>." Then defer to the user before offering work.

If `current_sprint` is 0 or no sprints exist yet, the engagement is in pre-Sprint-1 state — recommend `/pilar:sprint-plan` to open the briefing sprint.

## Available pilar slash commands

- `/pilar:sprint-plan` — open a new sprint (drafts the plan from roadmap's Next Sprint Scope; you approve before commit).
- `/pilar:sprint-close` — close the active sprint (drafts the summary; you respond Confirm / Request revisions / Defer / Rewind at the checkpoint).
- `/pilar:sprint-amend` — amend the active sprint plan in flight if scope changes during execution.
- `/pilar:run-qc <artifact-path>` — run the Phase 2 stub Fact-Checker subagent under the §4/§8 Independence Contract (real QC arrives with Phase 5 of pilar).

## Engagement-level vs Claude Code task-level work

Per §12 of `scp-plugin-spec.md`: engagement-level artifacts (this `roadmap.md`, `briefing.md`, sprint plans/summaries, pillar files, lexicon, style guide, registers, QC reports) are persistent and committed. Claude Code's native task-level scaffolding (plan files, todo lists, scratch notes) is ephemeral — feel free to use it within a sprint without persisting beyond the sprint.

## Commit discipline

Per §3 of the spec and pilar's load-bearing decision #4: never auto-commit. The pilar slash commands propose commit messages and wait for explicit user approval. Outside the slash commands, follow the same pattern.
```

### Step 7 — Propose the initial commit

Show the user the result of `git status` and propose this commit message:

```
chore(pilar): scaffold engagement repository

Initialized via /pilar:init. Directory structure and engagement-artifact
stubs follow §3 + §7 of scp-plugin-spec.md. Frontmatter populated from
intake interview; body sections to be filled during Sprint 1 (briefing).
CLAUDE.md provides session-resumption guidance (§5.4).
```

Wait for explicit user approval. If approved, run `git add -A` and `git commit` (use a heredoc for the commit message). If the user wants to revise the message, accept their version and use it. If the user wants to defer the commit, stop without committing.

### Step 8 — Brief the user on next steps

Tell the user:

> ✓ Engagement repo scaffolded at `<absolute path of cwd>`.
>
> Recommended next step: run `/pilar:sprint-plan` to open the briefing sprint. The plugin will draft a Sprint 1 plan from the briefing-sprint defaults; you approve before commit, then conduct the briefing in conversation, then run `/pilar:sprint-close` when you're ready for the checkpoint.

Stop.
