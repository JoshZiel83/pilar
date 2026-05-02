---
description: Scaffold a pilar engagement repository in the current directory
allowed-tools: Bash, Read, Write
---

Scaffold a new pilar engagement repository in the user's current working directory, following §3 of the natural-language spec. This is the first action a medical writer takes when starting a new SCP development engagement.

## Roadmap schema template (use this to seed the engagement's roadmap.md)

@${CLAUDE_PLUGIN_ROOT}/schemas/roadmap.md

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
  qc/fact-check-reports \
  qc/editorial-reports \
  qc/strategic-alignment-reports \
  sprints

for d in \
  knowledge-base/clinical knowledge-base/preclinical knowledge-base/guidelines knowledge-base/competitor knowledge-base/other \
  pillars registers \
  qc/fact-check-reports qc/editorial-reports qc/strategic-alignment-reports \
  sprints
do
  touch "$d/.gitkeep"
done
```

### Step 4 — Intake interview

Ask the user — in plain conversation, one cohesive prompt — for the five fields needed to populate the roadmap frontmatter:

1. **Project ID** (kebab-case, e.g. `aurelis-alr217-dlbcl-2026`)
2. **Client** (organization name)
3. **Product** (compound or brand name)
4. **Indication**
5. **Lifecycle stage** (e.g. "post-Phase 2 / pre-launch ~18 months")

Wait for all five answers before proceeding to Step 5. If the user is unsure of any field, suggest a sensible placeholder (e.g. derive Project ID from `<client>-<product>-<indication-slug>-<year>`) and confirm.

### Step 5 — Write the engagement's `roadmap.md`

Write `roadmap.md` at the engagement repo root using the schema template above as the body structure. Populate frontmatter with:

- `artifact: roadmap`
- `project: <user's Project ID>`
- `client: <user's Client>`
- `product: <user's Product>`
- `indication: <user's Indication>`
- `lifecycle_stage: <user's Lifecycle>`
- `created: <today's ISO date, YYYY-MM-DD — get from `date +%F`>`
- `updated: <same as created>`
- `current_sprint: 0`

Keep every H2 section heading from the template. Replace each `<placeholder>` body text with `_TBD — to be filled during Sprint 1 (briefing)._` so the file is human-readable but unmistakably a stub.

### Step 6 — Propose the initial commit

Show the user the result of `git status` and propose this commit message:

```
chore(pilar): scaffold engagement repository

Initialized via /pilar:init. Directory structure follows §3 of
scp-plugin-spec.md. Roadmap frontmatter populated from intake
interview; body sections to be filled during Sprint 1 (briefing).
```

Wait for explicit user approval. If approved, run `git add -A` and `git commit` (use a heredoc for the commit message). If the user wants to revise the message, accept their version and use it. If the user wants to defer the commit, stop without committing.

### Step 7 — Brief the user on next steps

Tell the user:

> ✓ Engagement repo scaffolded at `<absolute path of cwd>`.
>
> Recommended next step: run `/pilar:sprint-plan` to begin the briefing sprint.
>
> Note: `/pilar:sprint-plan` and the rest of the sprint engine ship with Phase 4 of pilar's implementation roadmap. Until then, the directory structure is in place but the sprint engine isn't yet wired.

Stop.
