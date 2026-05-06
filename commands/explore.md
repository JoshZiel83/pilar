---
description: Per-pillar exploration of KB source content driven by a free-form instruction — a pre-drafting step
allowed-tools: Bash, Read, Write, Edit
argument-hint: <pillar-id> [--instruction "<text>"]
---

Per-pillar exploration of KB source content for one pillar (a P7 refinement to the per-pillar drafting workflow). The writer passes a free-form instruction — that may be a hypothesis ("does the pivotal data support a durability claim?"), an open-ended strategic question ("what can we say about durability in elderly DLBCL that is evidence-based and strategically useful?"), or a directive ("summarize the safety story for community oncologists"). The command reads the briefing and the manifest; the agent decides which sources are most valuable to read against the instruction, **reads the actual file content** (markdown, txt, or PDF via the Read tool's `pages` parameter for large PDFs), and produces a synthesis discussion.

This is the read-source-content companion to `/pilar:pillar-narrative` (which groups manifest entries by `type` for high-level framing) and `/pilar:pillar-statements` (which surfaces manifest-entry metadata as RS sourcing options) — neither of those commands opens source files. Use `/pilar:explore` between them when something is worth probing against the data before committing it to drafted copy.

The output is a synthesis. **Save and commit are one decision** — saving appends the synthesis as a dated H2 section to `explorations/p-NN.md` and commits in the same step. (Files in `explorations/` are scratch markdown — not §7 artifacts — and are not schema-validated; the commit just keeps the working tree honest.)

The agent decides what's most valuable to read against the instruction; the writer can intercept to skip a source or add one before reading begins. The command never silently reads the entire KB — the agent surfaces its read plan first.

## Procedure

### Step 1 — Detect engagement state and parse argument

Run:

!`pwd && ls -1 roadmap.md briefing.md knowledge-base/manifest.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** and recommend `/pilar:init`. If `knowledge-base/manifest.md` is missing or has zero `### <ref-id>` entries, **stop** and recommend `/pilar:ingest-sources` first — without sources in the manifest there is nothing to read.

Parse `$ARGUMENTS`:

- First positional: must match `^P-\d{2}$` (the pillar id).
- Optional flag: `--instruction "<text>"` for non-interactive scope capture. (`--angle` is accepted as a deprecated alias.)

If the positional is missing or malformed, **stop** with usage:

```
/pilar:explore <pillar-id> [--instruction "<text>"]
  pillar-id:     P-NN  (zero-padded two-digit pillar id)
  --instruction: free-form instruction — hypothesis, open question, or
                 directive (omit to be prompted interactively)
  examples:
    /pilar:explore P-04
    /pilar:explore P-04 --instruction "durability claim grounded in current data"
    /pilar:explore P-04 --instruction "what can we say about safety in elderly DLBCL that is strategically useful?"
    /pilar:explore P-04 --instruction "summarize the tolerability story for community oncologists"
```

Capture `pillar_id` and `instruction_arg` (may be empty).

### Step 2 — Locate the pillar file

Run:

!`grep -l "^pillar_id: <PILLAR_ID>$" pillars/*.md 2>/dev/null` (substitute the captured `pillar_id`).

If no file matches, **stop** and tell the user the pillar does not exist; recommend `/pilar:scaffold-pillars` (or — if scaffolding is already done — point at a likely typo).

Capture the matched path as `pillar_path`. Read the file (any `status` is acceptable — exploration is not gated by pillar status; the writer may want to explore pre-narrative, between narrative and statements, or post-statements-approved when revisiting).

### Step 3 — Read briefing context

Read `briefing.md` and capture `## Strategic Priorities`, `## Audiences`, `## Indication`, `## Competitive Context`, `## Constraints`. The exploration synthesis is grounded in these (a finding only matters if it advances or refutes a strategic priority that affects an audience the engagement cares about).

### Step 4 — Read the KB manifest

Read `knowledge-base/manifest.md`. For every `### <ref-id>` entry, capture the id, `file:`, `type`, `key_findings:`, and `tags:`. Build the candidate source list.

### Step 5 — Capture the exploration instruction

If `instruction_arg` was provided in Step 1, use it (skip to Step 6).

Otherwise, ask the user:

> *"What would you like me to explore for `<pillar_id>`? Free-form — a hypothesis, an open question, or a directive all work. Examples:*
> - *'does the pivotal data support a durability claim?'*
> - *'what can we say about safety in elderly DLBCL that is evidence-based and strategically useful?'*
> - *'summarize the tolerability story for community oncologists'*

Wait for the user's response. Capture as `instruction`. The instruction is the lens through which sources are chosen, read, and the synthesis is composed.

### Step 6 — Propose a read plan and read the chosen sources

Given `instruction` plus the briefing context, judge which manifest sources are most likely to be valuable. Use each entry's `type`, `key_findings`, and `tags` as the signals. Strategic priorities and audiences from the briefing inform priority — a tolerability instruction for community oncologists weights single-arm trial AE tables and guidelines higher than mechanism-of-action papers.

Surface the read plan as one line per source — ref-id, type, and a brief reason — then a `proceed` cue:

```
Read plan for "<instruction>":

  <ref-id-1>   Single-arm Phase 2 trial   ALR-217 pivotal — primary efficacy and AE data
  <ref-id-2>   Treatment guideline         NCCN — sequencing context for community-onc audience
  <ref-id-3>   Congress abstract           ASH 2024 — elderly-subgroup readout

Reading these unless you say otherwise — reply 'skip <ref-id>', 'add <ref-id>', or 'go'.
```

Default action is to proceed. The writer can interject before any read begins (`skip <ref-id>` removes from the plan; `add <ref-id>` adds; `go` is the explicit confirmation if they want to send one). After the writer's response (or `go`), execute the reads:

For each ref-id in the final plan:

1. Look up the source path from the manifest entry (the `file:` value, resolved relative to the engagement repo root).
2. Use the Read tool on the source file. For PDFs, use the `pages: "1-10"` parameter on the first read (the spec's binary KB inputs are committed as-is per §3, and the Read tool handles PDFs natively); after reading the first 10 pages, ask the user *"Read deeper? (specify a page range like 11-20, or 'no')"* — extend the read only if the user opts in.
3. Surface key passages, quotes, and concepts relevant to `instruction`. Quote when a specific sentence or phrase from the source is load-bearing for the synthesis. Note absences too — a Limitations section that does NOT discuss durability is itself a finding for a durability instruction.

If a source file is missing from disk (the manifest may reference an unconverted binary), surface this and **skip** that entry without stopping — the exploration continues with the remaining sources.

The writer may request additional reads mid-exploration ("now read `<ref-id-X>`", "go deeper on `<ref-id-2>`"). Honor those without re-running the full read plan.

### Step 7 — Write the synthesis

Compose a 1–2 paragraph synthesis covering:

1. **What the exploration found** with respect to `instruction`. Be specific about which manifest entry/entries ground each claim. Where the instruction is hypothesis-shaped, frame as supports / refutes / suggests; where the instruction is open-ended, frame as the strategically useful evidence-based things you can now say.
2. **What's still unclear** — gaps the sources don't address, hedging the instruction requires.
3. **Concrete framings for downstream drafting** — phrasings the writer might reuse (or avoid) in the eventual `/pilar:pillar-narrative` or `/pilar:pillar-statements` work.

Surface the synthesis to the user. Iterate briefly if they want refinement (one or two short rounds is the goal — heavy refinement is the Editor's job, not the explorer's).

### Step 8 — Save and commit (single gate) or discard

Per the post-#19 convention, saving and committing are one decision. The writer's `save` choice authorizes both the file write and the commit; there is no second "approve commit?" prompt.

Capture today's ISO date with `!date +%F`.

Compute a kebab-case slug from `instruction`:

- Lowercase.
- Strip characters outside `[a-z0-9 -]`.
- Collapse internal whitespace to single hyphens.
- Truncate to the first 6 hyphen-separated tokens.
- Strip leading/trailing hyphens.

Compute the H2 section heading: `## <today's ISO date> — <slug>` (e.g. `## 2026-05-15 — what-can-we-say-about-durability`).

Compute the section body:

- The 1–2 paragraph synthesis from Step 7.
- A trailing line: `**References explored:** <ref-id>, <ref-id>, …` listing the entries actually read in Step 6 (excluding any that were skipped due to missing files).

Propose the commit message (substitute `<pillar_id>`, a short instruction phrasing, and the count of sources read):

```
docs(pilar): exploration — <pillar_id> <short instruction phrasing>

Exploration of "<instruction>" against N source(s) from the manifest.
Synthesis appended to explorations/<pillar_id>.md. Scratch notes per
the §3 / §12 ephemeral-vs-engagement distinction; not a §7 artifact
and not schema-validated.
```

Ask:

> Save and commit this exploration to `explorations/<pillar_id>.md`?
>   `save / discard / revise commit: <new> / defer (write the file but do not commit)`

- **`save`** → execute the file write per the rules below, then `git add explorations/<pillar_id>.md && git commit -m "<approved message>"` (heredoc).
- **`discard`** → end without writing or committing. Skip to Step 9.
- **`revise commit: <new>`** → use the new message; restate the prompt; wait for `save`.
- **`defer`** → execute the file write but do not commit. The exploration sits in the working tree; the writer takes responsibility for committing later. (Intentionally a low-friction escape hatch; `save` is the recommended path.)

File-write rules (used by `save` and `defer`):

- Check whether `explorations/<pillar_id>.md` exists.
  - **If it exists**, use the Edit tool to append the new H2 section after the last existing content. Match `old_string` against the last few lines of the existing final section (with trailing whitespace) and produce a `new_string` with those lines plus a blank line plus the new section.
  - **If it does not exist**, use the Write tool. The file's first line is `# Explorations — <pillar_id> <pillar name>` (read pillar name from the pillar file's `# Pillar: <name>` H1). No frontmatter — these are scratch notes, not §7 artifacts. Then a blank line, then the new H2 section.

### Step 9 — Brief next steps

Tell the user (substitute the appropriate save/defer/discard branch):

> ✓ Exploration of "<instruction>" complete. <Synthesis was saved and committed to explorations/<pillar_id>.md | Synthesis was written to explorations/<pillar_id>.md but not committed (working tree dirty) | Synthesis was discarded (conversation only).>
>
> The exploration informs your downstream drafting but does not auto-load into it — re-state any specific framings you want to carry forward when you invoke the drafting commands.
>
> Next, depending on `<pillar_id>`'s current `status`:
>
> - `draft` → run `/pilar:pillar-narrative <pillar_id>` to draft the Strategic Rationale, Narrative, and Scope sections.
> - `narrative-approved` → run `/pilar:pillar-statements <pillar_id>` to draft the Scientific Statements and Reference Statements.
> - `statements-approved` or higher → exploration findings can inform a future revision (which would require a rewind sprint per §5.3).
>
> To probe another instruction on the same pillar, re-run `/pilar:explore <pillar_id>` — saved sections accumulate in the same `explorations/<pillar_id>.md` file.

Stop.
