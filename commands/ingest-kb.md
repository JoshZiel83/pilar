---
description: Ingest knowledge-base sources into the manifest — propose taxonomy (M1) or incremental update (M2 — not yet implemented)
allowed-tools: Bash, Read, Write, Edit
argument-hint: [knowledge-base-path]
---

Ingest sources from the engagement's `knowledge-base/` directory into `knowledge-base/manifest.md` per §6.2 of `scp-plugin-spec.md`. The command operates in two modes:

- **Initial intake** (manifest is empty): walk the user-dropped files, propose a taxonomy assignment against the default subfolders seeded by `/pilar:init`, refine with the user, move files into approved subfolders, propose manifest entries, write the manifest, propose the commit. Implemented in M1 (this milestone).
- **Incremental** (manifest already has entries): detect new files since last ingest, propose entries for them only, append. Implemented in M2 (subsequent milestone).

The Librarian role (§4.2) has no QC-style independence contract — the Primary Collaborator runs this workflow with full briefing/roadmap context to make informed taxonomy and metadata proposals.

## KB manifest schema (use to seed entries)

@${CLAUDE_PLUGIN_ROOT}/schemas/kb-manifest.md

## Procedure

### Step 1 — Confirm we are in a pilar engagement

Run:

!`pwd && ls -1 roadmap.md knowledge-base/manifest.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** — this directory is not a pilar engagement repo. Recommend `/pilar:init`.

If `knowledge-base/manifest.md` is missing, **stop** — the engagement is under-scaffolded. Recommend re-running `/pilar:init` (the manifest stub is part of its output).

### Step 2 — Determine ingestion mode

Read `knowledge-base/manifest.md`. Count `### REF-NNN` entries under `## Entries` (a regex match for `^### REF-\d{3}$` against the body suffices).

- **Zero entries** → initial-intake mode. Continue with Step 3.
- **One or more entries** → incremental mode. **Stop** for now and tell the user:

  > `knowledge-base/manifest.md` already has N entries. Incremental ingestion will land in Milestone M2; for now this command only handles initial intake against an empty manifest. If you need to manually add a single entry, edit the manifest directly and run `python3 scripts/validate-schemas.py knowledge-base/manifest.md`.

### Step 3 — Inventory the knowledge-base directory

Run:

!`find knowledge-base -type f \( ! -name '.gitkeep' ! -name 'manifest.md' \) | sort`

If the result is empty, **stop** and tell the user `knowledge-base/` contains no source files yet — drop sources into the directory (loose or pre-organized into subfolders) and re-run.

Capture the file list as `kb_files`. For each entry, note its current path (relative to engagement repo root).

### Step 4 — Propose taxonomy assignments

`/pilar:init` seeded five default subfolders under `knowledge-base/`:

- `clinical/` — clinical trial publications and data on the engagement's product
- `preclinical/` — mechanism-of-action, in-vitro, in-vivo data on the engagement's product
- `guidelines/` — treatment guidelines, consensus statements
- `competitor/` — clinical or strategic data on competitor products
- `other/` — anything that does not fit the above (reviews, congress abstracts, regulatory docs, etc.)

For each file in `kb_files`, propose an assignment using filename hints (`alr217`, `pivotal`, `phase` → `clinical/`; `nccn`, `guideline` → `guidelines/`; competitor product names → `competitor/`; etc.) plus, if the file is text-readable (`.md`, `.txt`), a brief glance at the first ~30 lines for clarifying hints. Files already correctly placed under a subfolder receive that subfolder as the proposal (no-op move).

Present the assignments to the user as a table or tree, e.g.:

```
knowledge-base/
├── clinical/
│   ├── (already there) alr217-phase2-pivotal.pdf
│   └── alr217-elderly-subgroup-ash.pdf  ← from knowledge-base/
├── preclinical/
│   └── alr217-moa.pdf  ← from knowledge-base/
├── competitor/
│   └── bispecific-A-pivotal.pdf  ← from knowledge-base/
└── guidelines/
    └── nccn-bcell-lymphomas-excerpt.pdf  ← from knowledge-base/
```

If a file's category is unclear, propose `other/` and flag for user attention.

If the writer needs a subfolder beyond the five defaults, accept it — create the new subfolder via `mkdir -p knowledge-base/<new-name>` and proceed with the user's choice. Note: introducing a non-default subfolder is a taxonomy choice the engagement is locked into for the duration; surface the consequence briefly so the user can confirm.

### Step 5 — Wait for explicit user approval of the taxonomy

Ask the user to approve the assignments. Accept refinements: file-by-file overrides, new subfolders, holding files for a future ingest. Iterate until the user is satisfied. If the user defers, **stop** without moving any files.

### Step 6 — Move files into approved subfolders

For each file whose proposed subfolder differs from its current location, run:

```bash
git mv <current-path> <new-path>
```

Use `git mv` (not plain `mv`) so the move is tracked as a rename in git history. If `git mv` fails (e.g., file is not yet tracked), fall back to `mv` and let the subsequent `git add` pick up the new path.

After moves complete, re-run the inventory:

!`find knowledge-base -type f \( ! -name '.gitkeep' ! -name 'manifest.md' \) | sort`

Confirm every file is now under one of the approved subfolders.

### Step 7 — Propose manifest entries

Capture today's ISO date with `!date +%F` for the `ingested:` field.

For each file, propose a `### REF-NNN` entry using sequential numbering starting at `REF-001`. Order is the user's call — propose by subfolder (clinical first, then preclinical, etc.) for readable ordering.

Each entry needs the seven §7.4 fields:

- `file:` — the post-move path relative to engagement repo root.
- `citation:` — full bibliographic citation. **Always ask the user**; do not invent. For unpublished or internal documents, use a descriptive placeholder (e.g., "ALR-217 internal mechanism-of-action study report, document control ID XXX").
- `type:` — one of: RCT, single-arm trial, real-world evidence, guideline, review, congress abstract, mechanism-of-action paper, regulatory document, internal document. Propose from filename + subfolder; confirm with user.
- `design:` — design notes (study design summary; for non-trial sources: document type and scope).
- `population:` — population studied (clinical sources) or scope (non-clinical sources).
- `key_findings:` — one or two sentences summarizing the source's takeaway. **Always ask the user** — the Librarian should not invent findings from filenames alone.
- `tags:` — a YAML list of short slugs for downstream search (e.g., `[pivotal, phase-2, primary-endpoint, alr217]`). Propose from observation; user refines.
- `ingested:` — today's ISO date (computed above).

Propose all entries as a single block of markdown to the user, preceded by a brief summary of what each entry's `citation` and `key_findings` are claimed to be (so the user can quickly catch invented content).

### Step 8 — Wait for explicit user approval of the manifest entries

Iterate field-by-field with the user as needed. Citation, key_findings, and population are the three highest-stakes fields — never accept defaults the user has not seen and approved. The user may approve in batch ("all five entries look right, proceed") or per-entry.

If the user defers, **stop** without writing the manifest. The taxonomy moves from Step 6 are left in place; the user can resume by re-running `/pilar:ingest-kb` (which will detect the empty manifest and pick up from Step 3).

### Step 9 — Write `knowledge-base/manifest.md`

Replace the empty stub manifest with the populated version. Frontmatter:

- `artifact: kb-manifest`
- `project: <project from roadmap.md frontmatter>`
- `updated: <today's ISO date>`

Body: `# Knowledge Base Manifest` H1, `## Entries` H2, then every approved `### REF-NNN` entry block in agreed order, separated by blank lines.

Use the Edit tool against the existing stub (preserving the H1 and H2 headings) by replacing the empty body under `## Entries` with the entry blocks. If Edit cannot match cleanly (because the stub body is just whitespace), write the full file with the Write tool.

### Step 10 — Validate the manifest

Run:

!`python3 scripts/validate-schemas.py knowledge-base/manifest.md`

If validation fails, surface the errors to the user. Correct the manifest with targeted Edits and re-validate. Do not proceed to Step 11 until validation passes.

### Step 11 — Propose the commit

Run `git status` to show the staged and unstaged changes (file moves + manifest write).

Propose this commit message (substitute the entry count):

```
feat(p6-m1): initial KB intake — N sources catalogued

Initial knowledge-base ingestion via /pilar:ingest-kb. Files
categorized into the §3 default subfolder taxonomy (or user-approved
extensions); each source has a manifest entry per §7.4 with
user-confirmed citation, type, design, population, key_findings,
and tags. Subsequent ingestions append via M2 incremental mode.
```

Wait for explicit user approval. If approved, run:

```bash
git add knowledge-base/
git commit -m "$(cat <<'EOF'
... approved message ...
EOF
)"
```

If the user wants to revise the message, accept their version. If the user defers the commit, **stop** without committing — the changes remain in the working directory.

### Step 12 — Brief the user on next steps

Tell the user:

> ✓ N sources ingested into `knowledge-base/manifest.md`. Files organized under the approved subfolder taxonomy.
>
> Next steps:
>
> - **Phase 6 M3 (coming soon)** will run an orphan-RS scan after each ingest, automatically proposing `GAP-NNN` entries against pillars whose reference statements lack support in the manifest.
> - **Phase 6 M4 (coming soon)** ships `/pilar:add-aspirational` for registering aspirational statements per §7.7.
> - **Phase 7** provides per-pillar drafting commands; reference statements drafted in pillars cite manifest entries by `REF-NNN`.
>
> If you have additional sources to add later, drop them under `knowledge-base/` and re-run `/pilar:ingest-kb` (incremental mode lands in M2).

Stop.
