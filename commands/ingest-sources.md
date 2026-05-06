---
description: Ingest knowledge-base sources into the manifest — initial intake or incremental update
allowed-tools: Bash, Read, Write, Edit
argument-hint: [knowledge-base-path]
---

Ingest sources from the engagement's `knowledge-base/` directory into `knowledge-base/manifest.md` per §6.2 of `scp-plugin-spec.md`. The command auto-detects mode:

- **Initial intake** (manifest is empty): walk the user-dropped files, propose a taxonomy assignment against the default subfolders seeded by `/pilar:init`, refine with the user, move files into approved subfolders, propose manifest entries, write the manifest, propose the commit.
- **Incremental** (manifest already has entries): detect new files (those whose path is not yet in the manifest), assign each to a subfolder using the existing taxonomy as a guide, propose entries with property-based `<ref-id>` headings derived from each entry's authorship/year/venue per `docs/CONVENTIONS.md`, append to the manifest.

The Librarian role (§4.2) has no QC-style independence contract — the Primary Collaborator runs this workflow with full briefing/roadmap context to make informed taxonomy and metadata proposals.

## KB manifest schema (use to seed entries)

@${CLAUDE_PLUGIN_ROOT}/schemas/kb-manifest.md

## Procedure

### Step 1 — Detect engagement state

Run:

!`pwd && ls -1 roadmap.md knowledge-base/manifest.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** — this directory is not a pilar engagement repo. Recommend `/pilar:init`.

If `knowledge-base/manifest.md` is missing, **stop** — the engagement is under-scaffolded. Recommend re-running `/pilar:init` (the manifest stub is part of its output).

### Step 2 — Determine ingestion mode

Read `knowledge-base/manifest.md`. Match `^### \S+$` headings under `## Entries` against the body. Capture:

- `existing_refs` — list of `<ref-id>` headings already in the manifest.
- `existing_files` — for each existing entry, the value of its `file:` field (used in Step 3 to compute the new-file delta).

Set the mode:

- `existing_refs` is empty → **initial-intake** mode (write a fresh manifest body).
- `existing_refs` is non-empty → **incremental** mode (append new entries to the existing body).

The flow from Steps 3–11 is shared between modes, with mode-specific branches called out where they differ.

### Step 3 — Inventory the knowledge-base directory

Run:

!`find knowledge-base -type f \( ! -name '.gitkeep' ! -name 'manifest.md' \) | sort`

Capture the file list as `kb_files` (relative paths to engagement repo root).

**In incremental mode**, compute the new-file delta:

- `new_files` = `kb_files` minus `existing_files` (the file paths already in the manifest from Step 2).
- If `new_files` is empty, **stop** and tell the user the manifest is already up to date — N entries cover all M sources currently under `knowledge-base/`. No taxonomy work, no commit.
- Replace `kb_files` with `new_files` for the remainder of the procedure (the work below operates only on the delta).

**In initial-intake mode**, if `kb_files` is empty, **stop** and tell the user `knowledge-base/` contains no source files yet — drop sources into the directory (loose or pre-organized into subfolders) and re-run.

### Step 4 — Propose taxonomy assignments

`/pilar:init` seeded five default subfolders under `knowledge-base/`:

- `clinical/` — clinical trial publications and data on the engagement's product
- `preclinical/` — mechanism-of-action, in-vitro, in-vivo data on the engagement's product
- `guidelines/` — treatment guidelines, consensus statements
- `competitor/` — clinical or strategic data on competitor products
- `other/` — anything that does not fit the above (reviews, congress abstracts, regulatory docs, etc.)

Plus a staging subfolder, `knowledge-base/for_ingestion/`, where `/pilar:research` writes provisional sources and writers may drop new files manually. **`for_ingestion/` is a queue, not a destination** — every file in it must be moved to one of the taxonomy subfolders during this command. After this run, `for_ingestion/` ends empty (only `.gitkeep` remains).

**In incremental mode**, the existing manifest may also reveal user-introduced subfolders (any `file:` path whose subfolder is not one of the five defaults). Treat those as additional valid taxonomy slots — the engagement's lived taxonomy is the union of the defaults and whatever the manifest already uses.

For each file in `kb_files`, partition by **provisional** vs **non-provisional**:

- **Provisional file** — the file's frontmatter contains `provisional: true` and `source: pubmed` or `source: clinicaltrials.gov` (written by `/pilar:research` via `scripts/research-fetch.py`). For these, propose the taxonomy using the structured metadata: PubMed entries with a clinical-trial `publication_type` or trial-related MeSH terms → `clinical/`; PubMed entries on mechanism/preclinical biology → `preclinical/`; guidelines → `guidelines/`; CT.gov registrations whose `lead_sponsor` matches the engagement's product owner → `clinical/`, otherwise → `competitor/`. Files in `for_ingestion/` must move to a taxonomy subfolder (they cannot stay in the staging dir).
- **Non-provisional file** — propose using filename hints (`alr217`, `pivotal`, `phase` → `clinical/`; `nccn`, `guideline` → `guidelines/`; competitor product names → `competitor/`; etc.) plus, if the file is text-readable (`.md`, `.txt`), a brief glance at the first ~30 lines for clarifying hints. Files already correctly placed under a subfolder receive that subfolder as the proposal (no-op move).

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

For each file, propose a `### <ref-id>` entry whose heading is the property-based id derived from the source's authorship, year, and venue per `docs/CONVENTIONS.md` §"KB manifest reference IDs". For provisional files (frontmatter `provisional: true`) the id can be derived deterministically from the staged file's frontmatter (`authors[0]` surname + initials, `year`, `journal` abbreviation). For non-provisional files the id is constructed from the user-confirmed `citation:` field (or proposed by the agent and confirmed alongside the other fields below). Disambiguate collisions with `_a/_b/_c/...` per the convention. Verify the proposed id is not already present in `existing_refs`; if it is, the new file is almost certainly a duplicate of an existing manifest entry — surface to the user before proceeding. Order is the user's call — propose by subfolder (clinical first, then preclinical, etc.) for readable ordering.

**Provisional files** (frontmatter `provisional: true`, written by `/pilar:research`): pre-populate the entry from the file's frontmatter; do not invent any field. Mapping:

- `file:` — post-move path.
- `citation:` — for PubMed: the full Vancouver citation rendered from the frontmatter's title, authors, journal, year, volume, issue, pages. For CT.gov: `<brief_title>. ClinicalTrials.gov Identifier: NCT<id>. Status as of <fetched>: <overall_status>.`
- `type:` — for PubMed: map `publication_type` to one of the standard types (e.g. "Randomized Controlled Trial" → `RCT`; "Clinical Trial, Phase II" → `single-arm trial` or `RCT` per design). For CT.gov: `clinicaltrials-registration` (a literal). When ambiguous, propose `pubmed-abstract` (a literal) and let the user refine.
- `design:` — for PubMed: synthesize one short phrase from `publication_type` + key MeSH terms. For CT.gov: `<phase>; <study_type>; planned enrollment <enrollment>`.
- `population:` — for PubMed: extract from MeSH if present (e.g. an MeSH like "Aged" → "elderly"); otherwise leave the value as `_TBD — extract from full text when acquired._`. For CT.gov: extract from eligibility (age range + condition list).
- `key_findings:` — **always ask the user** even for provisional files. This is the editorial summary — the no-LLM-in-canonical-content principle does not extend to extraction-from-the-abstract because the user must judge what is load-bearing for the engagement. Surface the abstract verbatim alongside the prompt to help the writer answer concisely.
- `tags:` — for PubMed: subset of `mesh_terms` rendered as kebab-case slugs (cap at ~5). For CT.gov: `conditions` + `interventions` rendered the same way.
- `status: provisional` — added to the entry; flags this entry as metadata-only awaiting full-text upgrade.
- `ingested:` — today's ISO date.

Pre-populated provisional entries are surfaced as a single block; the user is asked to confirm `key_findings` for each (one short answer per entry) and then approve the batch. No per-field walking for the other fields — the data came verbatim from PubMed/CT.gov upstream.

**Non-provisional files** (manually-dropped sources): walk the user through every §7.4 field as before. Each entry needs the seven fields:

- `file:` — the post-move path relative to engagement repo root.
- `citation:` — full bibliographic citation. **Always ask the user**; do not invent. For unpublished or internal documents, use a descriptive placeholder (e.g., "ALR-217 internal mechanism-of-action study report, document control ID XXX").
- `type:` — one of: RCT, single-arm trial, real-world evidence, guideline, review, congress abstract, mechanism-of-action paper, regulatory document, internal document. Propose from filename + subfolder; confirm with user.
- `design:` — design notes (study design summary; for non-trial sources: document type and scope).
- `population:` — population studied (clinical sources) or scope (non-clinical sources).
- `key_findings:` — one or two sentences summarizing the source's takeaway. **Always ask the user** — the Librarian should not invent findings from filenames alone.
- `tags:` — a YAML list of short slugs for downstream search (e.g., `[pivotal, phase-2, primary-endpoint, alr217]`). Propose from observation; user refines.
- `ingested:` — today's ISO date (computed above).

(Non-provisional entries do not include a `status:` line; absence defaults to `confirmed` per `schemas/kb-manifest.md`.)

Propose all entries (provisional + non-provisional) as a single block of markdown to the user, preceded by a brief summary of what each entry's `citation` and `key_findings` are claimed to be (so the user can quickly catch invented content).

### Step 8 — Wait for explicit user approval of the manifest entries

Iterate field-by-field with the user as needed. Citation, key_findings, and population are the three highest-stakes fields — never accept defaults the user has not seen and approved. The user may approve in batch ("all entries look right, proceed") or per-entry.

If the user defers, **stop** without writing the manifest. The taxonomy moves from Step 6 are left in place; the user can resume by re-running `/pilar:ingest-sources` — incremental mode will pick up the still-uningested files automatically.

### Step 9 — Write or append to `knowledge-base/manifest.md`

Update the manifest's `updated:` frontmatter field to today's ISO date.

**In initial-intake mode**: replace the empty stub body. The frontmatter becomes:

- `artifact: kb-manifest`
- `project: <project from roadmap.md frontmatter>`
- `updated: <today's ISO date>`

Body: `# Knowledge Base Manifest` H1, `## Entries` H2, then every approved `### <ref-id>` entry block in agreed order, separated by blank lines. Use Edit against the stub or Write the full file if the stub body is empty whitespace.

**In incremental mode**: append the new entry blocks under `## Entries` after the last existing `### <ref-id>` entry, separated by blank lines. Use the Edit tool with `old_string` matching the last few lines of the existing final entry plus the trailing newline; `new_string` is those same lines plus the new entry blocks. Do not touch the existing entries' content — append-only. Update the `updated:` frontmatter via a separate Edit.

### Step 10 — Validate the manifest

Run:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py knowledge-base/manifest.md`

If validation fails, surface the errors to the user. Correct the manifest with targeted Edits and re-validate. Do not proceed to Step 11 until validation passes.

### Step 11 — Auto-detect orphan reference statements (pre-commit)

Run the orphan-RS predicate **before** committing, so manifest entries and any newly-registered evidence gaps land in a single commit. For early-sprint engagements with no pillars yet, the scan returns zero orphans and this step is a silent no-op — proceed directly to Step 12.

Run:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gaps.py pillars knowledge-base/manifest.md --format json`

Parse the JSON output. If `orphan_count` is 0, skip the rest of this step and proceed to Step 12. Otherwise, surface the orphans to the user as a brief summary:

> Found N orphan reference statement(s):
> - P-NN.SS-NN.RS-NN — <reason>
> - …

For each orphan, draft a candidate `GAP-NNN` entry per `schemas/evidence-gaps.md`:

- `linked_to:` — the orphan's `composite_id`.
- `description:` — what is missing. Read the RS at the orphan's `pillar_path` for context. Be specific about the claim the RS makes and why current sources don't support it.
- `evidence_type_needed:` — what kind of evidence would close it (RCT, RWE study, mechanistic data, guideline statement, peer-reviewed publication of an existing readout, etc.). Use the briefing's indication, audience, and strategic priorities for this judgment.
- `proposed_search:` — a concrete search strategy (PubMed query terms, congress bodies and abstract sessions, KOL contacts, internal medical-affairs queries, planned readouts to monitor, etc.). **This is the field a Python script cannot fill** — the Librarian (you, with full briefing/audience/indication context) drafts it.
- `status:` `open`
- `opened:` today's ISO date (computed in Step 7).
- `closed:` (leave empty for open gaps).

Sequential `GAP-NNN` ids: read existing `registers/evidence-gaps.md`, find the highest `GAP-NNN` across both `## Open Gaps` and `## Closed Gaps` sections (`docs/CONVENTIONS.md` append-only rule), and continue from `max + 1` zero-padded to three digits.

Present all proposed entries as a single block. Ask the user: *"Append these gap entries inline (commit alongside the manifest in this run) or defer (manifest commits alone; orphans will resurface next run)?"*

- **Inline** → append the entries under `## Open Gaps` in `registers/evidence-gaps.md`. Use the Edit tool with `old_string` matching the section heading + any existing trailing entry text + the next-section boundary; `new_string` inserts the new entries before the `## Closed Gaps` H2. If the file currently reads `<no open gaps yet>` or similar stub text under `## Open Gaps`, replace that placeholder with the new entries. Update the frontmatter `updated:` field to today's ISO date. Validate via `!python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py registers/evidence-gaps.md` and correct any errors via Edits before continuing. Set `gaps_inline = N` (the count) for use in the Step 12 commit message.
- **Defer** → leave `registers/evidence-gaps.md` untouched. Set `gaps_inline = 0`. Tell the user the same orphans will resurface the next time `/pilar:ingest-sources` runs against new files, or during `/pilar:pillar-statements` (which runs the orphan scan automatically after drafting).

### Step 12 — Propose the commit (single commit covering manifest + any inline gaps)

Run `git status` to show all staged/unstaged changes from this run (file moves, manifest write, optional gap-register append).

The commit message reflects both ingest mode and whether gaps were registered inline:

**Initial-intake mode** (substitute entry count `N` and append the gap-suffix line if `gaps_inline > 0`):

```
chore(pilar): initial KB intake — N sources catalogued[, K gaps opened]

Initial knowledge-base ingestion via /pilar:ingest-sources. Files
categorized into the §3 default subfolder taxonomy (or user-approved
extensions); each source has a manifest entry per §7.4 with
user-confirmed citation, type, design, population, key_findings,
and tags.[
K evidence gap(s) opened inline from the post-ingest orphan-RS scan.]
```

**Incremental mode** (substitute `N` = new entries, `M` = total in manifest, optional gap suffix):

```
chore(pilar): KB intake — N new source(s) added (M total)[, K gaps opened]

Incremental knowledge-base ingestion via /pilar:ingest-sources. New
sources appended under existing taxonomy with user-confirmed
metadata per §7.4.[
K evidence gap(s) opened inline from the post-ingest orphan-RS scan.]
```

(Strip the bracketed clauses if `gaps_inline == 0`.)

Wait for explicit user approval. If approved:

```bash
git add knowledge-base/ [registers/evidence-gaps.md]
git commit -m "$(cat <<'EOF'
... approved message ...
EOF
)"
```

(Stage `registers/evidence-gaps.md` only when `gaps_inline > 0`.)

If the user wants to revise the message, accept their version. If the user defers the commit, **stop** without committing — the changes remain in the working directory.

### Step 13 — Brief the user on next steps

Tell the user (substituting `N` ingested sources, `M` total in manifest, and `K` gaps opened from Step 12, where `K` may be zero):

> ✓ N source(s) ingested. `knowledge-base/manifest.md` now contains M entries; files organized under the approved subfolder taxonomy. K evidence gap(s) opened in this run.
>
> Drop additional sources into `knowledge-base/` at any time and re-run `/pilar:ingest-sources` — incremental ingestion + an orphan-RS scan run automatically. After a pillar is drafted or updated, the orphan scan also runs inside `/pilar:pillar-statements` (Step 8) — so day-to-day orphan detection is built into the drafting workflow. To register an aspirational statement (a strategically important claim that current evidence cannot fully support), use `/pilar:add-aspirational`.

Stop.
