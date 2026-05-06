---
description: Bounded, hypothesis-driven per-pillar exploration of KB source content — a pre-drafting step
allowed-tools: Bash, Read, Write, Edit
argument-hint: <pillar-id> [--angle "<hypothesis>"]
---

Bounded exploration of KB source content for one pillar (a P7 refinement to the per-pillar drafting workflow). The writer brings a hypothesis or angle ("does the pivotal data actually support a durability claim?", "is safety a credible differentiation axis vs bispecifics?"); the command surfaces relevant manifest sources, **reads the actual file content** (markdown, txt, or PDF via the Read tool's `pages` parameter for large PDFs), and produces a synthesis discussion.

This is the read-source-content companion to `/pilar:pillar-narrative` (which groups manifest entries by `type` for high-level framing) and `/pilar:pillar-statements` (which surfaces manifest-entry metadata as RS sourcing options) — neither of those commands opens source files. Use `/pilar:explore` between them when an angle is worth probing against the data before committing it to drafted copy.

The output is a synthesis. Saving is optional; if saved, the synthesis is appended as a dated H2 section to `explorations/p-NN.md` (one file per pillar; sections accumulate across invocations). Files in `explorations/` are scratch markdown — not §7 artifacts — and are not schema-validated.

The command is **bounded by user direction**: the user picks the angle, and the user picks which manifest sources to read. The command never silently reads the entire KB.

## Procedure

### Step 1 — Detect engagement state and parse argument

Run:

!`pwd && ls -1 roadmap.md briefing.md knowledge-base/manifest.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** and recommend `/pilar:init`. If `knowledge-base/manifest.md` is missing or has zero `### <ref-id>` entries, **stop** and recommend `/pilar:ingest-kb` first — without sources in the manifest there is nothing to read.

Parse `$ARGUMENTS`:

- First positional: must match `^P-\d{2}$` (the pillar id).
- Optional flag: `--angle "<text>"` for non-interactive scope capture.

If the positional is missing or malformed, **stop** with usage:

```
/pilar:explore <pillar-id> [--angle "<hypothesis>"]
  pillar-id: P-NN  (zero-padded two-digit pillar id)
  --angle:   one-sentence hypothesis to bound the exploration
             (omit to be prompted interactively)
  examples:
    /pilar:explore P-04
    /pilar:explore P-04 --angle "durability claim grounded in current data"
```

Capture `pillar_id` and `angle_arg` (may be empty).

### Step 2 — Locate the pillar file

Run:

!`grep -l "^pillar_id: <PILLAR_ID>$" pillars/*.md 2>/dev/null` (substitute the captured `pillar_id`).

If no file matches, **stop** and tell the user the pillar does not exist; recommend `/pilar:scaffold-pillars` (or — if scaffolding is already done — point at a likely typo).

Capture the matched path as `pillar_path`. Read the file (any `status` is acceptable — exploration is not gated by pillar status; the writer may want to explore pre-narrative, between narrative and statements, or post-statements-approved when revisiting).

### Step 3 — Read briefing context

Read `briefing.md` and capture `## Strategic Priorities`, `## Audiences`, `## Indication`, `## Competitive Context`, `## Constraints`. The exploration synthesis is grounded in these (a finding only matters if it advances or refutes a strategic priority that affects an audience the engagement cares about).

### Step 4 — Read the KB manifest

Read `knowledge-base/manifest.md`. For every `### <ref-id>` entry, capture the id, `file:`, `type`, and `key_findings:`. Build the candidate source list.

### Step 5 — Capture exploration scope (the bounded hypothesis)

If `angle_arg` was provided in Step 1, use it as the bounded hypothesis (skip to Step 6).

Otherwise, ask the user:

> *"What hypothesis or angle would you like to explore for `<pillar_id>`? Keep it to one sentence — that sentence is the bounded scope of this exploration. Examples: 'durability claims grounded in current data', 'safety as a differentiation axis vs bispecifics', 'community-oncologist comfort with toxicity management.'"*

Wait for the user's response. Capture as `angle`. The angle remains the lens through which sources are read and the synthesis is composed.

### Step 6 — Surface relevant manifest sources, ranked

Rank every manifest entry by likely relevance to `angle`. Use each entry's `type` and `key_findings` as ranking signals: a `type: Single-arm Phase 2 trial` ranks high for an efficacy or safety angle; a `type: Treatment guideline` ranks high for a positioning or sequencing angle; a `type: Mechanism-of-action` ranks high for a biology angle.

Present a ranked list, one entry per line — one column for the `<ref-id>`, one for the `type`, a star-rating column for the agent's relevance estimate, then a short label:

```
Manifest sources ranked by likely relevance to "<angle>":

  <ref-id-1>   Single-arm Phase 2 trial   ★★★  ALR-217 pivotal — ORR primary endpoint
  <ref-id-2>   Phase 2 pivotal trial       ★★   bispecific A — competitor data
  <ref-id-3>   Treatment guideline         ★    NCCN 3rd-line excerpt
  …
```

Ask the user: *"Which source(s) would you like to explore? (Comma-separated `<ref-id>` values; or 'top N' for the top-ranked N; or 'all' if the manifest is short.)"*

Wait for the user's selection. Capture as `picked_refs`. **Bounded by user direction** — they decide breadth.

### Step 7 — Read each picked source and discuss findings against the angle

For each `<ref-id>` in `picked_refs`:

1. Look up the source path from the manifest entry (the `file:` value, resolved relative to the engagement repo root).
2. Use the Read tool on the source file. For PDFs, use the `pages: "1-10"` parameter on the first read (the spec's binary KB inputs are committed as-is per §3, and the Read tool handles PDFs natively); after reading the first 10 pages, ask the user *"Read deeper? (specify a page range like 11-20, or 'no')"* — extend the read only if the user opts in.
3. Surface key passages, quotes, and concepts relevant to `angle`. Quote when a specific sentence or phrase from the source is load-bearing for the synthesis. Note absences too — a Limitations section that does NOT discuss durability is itself a finding for a durability angle.
4. Discuss with the user. They may want to refine the angle, add another source, or move on. Iterate briefly.

If a source file is missing from disk (the manifest may reference an unconverted binary), surface this and **skip** that entry without stopping — the exploration continues with the remaining picks.

### Step 8 — Write the synthesis

Compose a 1–2 paragraph synthesis covering:

1. **What the exploration supports, refutes, or suggests** with respect to `angle`. Be specific about which manifest entry/entries ground each claim.
2. **What's still unclear** — gaps the sources don't address, hedging the angle requires.
3. **Concrete framings for downstream drafting** — phrasings the writer might reuse (or avoid) in the eventual `/pilar:pillar-narrative` or `/pilar:pillar-statements` work.

Surface the synthesis to the user. Iterate briefly if they want refinement (one or two short rounds is the goal — heavy refinement is the Editor's job, not the explorer's).

### Step 9 — Save or discard

Ask the user:

> *"Save this exploration to `explorations/<pillar_id>.md`? (yes / no — default no)"*

**If no (or the user does not affirmatively answer yes)** → end the command without writing anything. Skip to Step 12.

**If yes** → continue to Step 10.

### Step 10 — Append the synthesis to `explorations/<pillar_id>.md`

Capture today's ISO date with `!date +%F`.

Compute a kebab-case slug from `angle`:

- Lowercase.
- Strip characters outside `[a-z0-9 -]`.
- Collapse internal whitespace to single hyphens.
- Truncate to the first 6 hyphen-separated tokens.
- Strip leading/trailing hyphens.

Compute the H2 section heading: `## <today's ISO date> — <slug>` (e.g. `## 2026-05-15 — durability-claim-grounded-in-current`).

Compute the section body:

- The 1–2 paragraph synthesis from Step 8.
- A trailing line: `**References explored:** <ref-id>, <ref-id>, …` listing the entries actually read in Step 7 (excluding any that were skipped due to missing files).

Check whether `explorations/<pillar_id>.md` exists:

- **If it exists**, use the Edit tool to append the new H2 section after the last existing content. Match `old_string` against the last few lines of the existing final section (with trailing whitespace) and produce a `new_string` with those lines plus a blank line plus the new section.
- **If it does not exist**, use the Write tool. The file's first line is `# Explorations — <pillar_id> <pillar name>` (read pillar name from the pillar file's `# Pillar: <name>` H1). No frontmatter — these are scratch notes, not §7 artifacts. Then a blank line, then the new H2 section.

### Step 11 — Propose the commit

Run `git status` to show changes.

Propose this commit message (substitute `<pillar_id>`, `<short angle phrasing>`, and the count of sources read):

```
docs(pilar): exploration — <pillar_id> <short angle phrasing>

Bounded exploration of "<angle>" against N source(s) from the
manifest. Synthesis appended to explorations/<pillar_id>.md.
Scratch notes per the §3 / §12 ephemeral-vs-engagement
distinction; not a §7 artifact and not schema-validated.
```

Wait for explicit user approval. On approval:

```bash
git add explorations/<pillar_id>.md
git commit -m "$(cat <<'EOF'
... approved message ...
EOF
)"
```

If the user wants to revise the message, accept their version. If the user defers the commit, **stop** without committing — the file edit remains in the working tree.

### Step 12 — Brief next steps

Tell the user:

> ✓ Exploration of "<angle>" complete. <Synthesis was saved to explorations/<pillar_id>.md | Synthesis was discarded (conversation only).>
>
> The exploration informs your downstream drafting but does not auto-load into it — re-state any specific framings you want to carry forward when you invoke the drafting commands.
>
> Next, depending on `<pillar_id>`'s current `status`:
>
> - `draft` → run `/pilar:pillar-narrative <pillar_id>` to draft the Strategic Rationale, Narrative, and Scope sections.
> - `narrative-approved` → run `/pilar:pillar-statements <pillar_id>` to draft the Scientific Statements and Reference Statements.
> - `statements-approved` or higher → exploration findings can inform a future revision (which would require a rewind sprint per §5.3).
>
> To probe another angle on the same pillar, re-run `/pilar:explore <pillar_id>` — saved sections accumulate in the same `explorations/<pillar_id>.md` file.

Stop.
