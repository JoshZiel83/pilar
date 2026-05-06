---
description: Register an aspirational statement — walks every §7.7 field, validates the linked target, proposes the commit
allowed-tools: Bash, Read, Write, Edit
argument-hint: <composite-id>
---

Register an aspirational statement (§6.5, §7.7) — a strategically important claim that current evidence cannot fully support. Walks the user through every §7.7 field, validates the linked composite-id against an existing pillar / SS / RS, generates the next `ASP-NNN`, appends to `registers/aspirational-statements.md`, and proposes the commit — waiting for explicit user approval per decision #4.

## Aspirational-statements schema (use to seed the new entry)

@${CLAUDE_PLUGIN_ROOT}/schemas/aspirational-statements.md

## Procedure

### Step 1 — Detect engagement state and parse the argument

Run:

!`pwd && ls -1 roadmap.md briefing.md registers/aspirational-statements.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** — this directory is not a pilar engagement repo. Recommend `/pilar:init`.

If `registers/aspirational-statements.md` is missing, **stop** — the engagement is under-scaffolded. Recommend re-running `/pilar:init`.

Parse `$ARGUMENTS` for the composite-id. The composite must match `^P-\d{2}\.SS-\d{2}(?:\.RS-\d{2})?$` — aspirational statements link at the SS or RS level, never at the pillar level alone. If `$ARGUMENTS` is empty or malformed, **stop** with usage:

```
/pilar:add-aspirational <composite-id>
  composite-id: P-NN.SS-NN[.RS-NN]
  examples: P-04.SS-01, P-04.SS-01.RS-02
```

Capture `linked_statement` = the validated composite-id. Decompose into `pillar_id`, `ss_id`, and (optionally) `rs_id`.

### Step 2 — Verify the linked target exists

Locate the pillar file. Run:

!`grep -l "^pillar_id: <PILLAR_ID>$" pillars/*.md 2>/dev/null`

(substitute the captured `pillar_id`). If no file matches, **stop** — tell the user pillar `<pillar_id>` does not exist yet; aspirational statements can only be linked to existing pillars. Recommend opening a pillar-drafting sprint first.

Read the matched pillar file. Verify:

- The SS-NN heading exists (`### <ss_id>: ` somewhere in the body). If absent, **stop** and tell the user the SS does not exist in that pillar.
- If `rs_id` is present in the composite, verify the RS-NN heading exists (`#### <rs_id>: ` within the SS body). If absent, **stop** and tell the user the RS does not exist in that SS.

### Step 3 — Walk through §7.7 fields with the user

Interview the user for each field. Be brief — one question at a time.

**claim** — *"What is the strategically important claim that current evidence cannot fully support?"*

Capture the user's text verbatim.

**rationale** — *"Why does this matter despite the current evidence gap? (One or two sentences on strategic relevance — typically a connection to a strategic priority from the briefing.)"*

Read `briefing.md`'s `## Strategic Priorities` section to ground the rationale; offer to suggest framings linked to specific priorities. Capture the user's final text.

**evidence_generation_link** — Read `briefing.md` and locate `## Evidence Generation Activities`. Capture the bullet list (lines starting with `- ` under that section).

Present the activities to the user numbered, plus a final "candidate input" option:

```
Available evidence-generation activities from the briefing:

  1. <bullet text 1>
  2. <bullet text 2>
  ...
  N. <bullet text N>
  N+1. candidate input — no plan exists yet; this readout is itself aspirational
```

Ask the user to pick a number. If they pick the final option, set `evidence_generation_link` to the literal string `candidate input`. Otherwise, propose the chosen bullet's text as the link value and let the user refine wording (the schema accepts free text; a short concrete reference such as "long-term follow-up readout from pivotal Phase 2" is the goal).

If the briefing's `## Evidence Generation Activities` section is empty (e.g., still the `_TBD — to be filled during Sprint 1 (briefing)._` stub), warn the user — aspirational statements should ideally tie to plans recorded in the briefing. Offer two paths: (a) defer this aspirational registration and revisit briefing in a future sprint; or (b) proceed with `evidence_generation_link: candidate input`. If (a), **stop** without writing.

**expected_readout** — *"When is the data expected? (ISO date `YYYY-MM-DD` or `tbd`.)"*

Validate format. Reject any other value with a brief explanation.

**fallback_position** — *"What does the platform say if this aspirational claim cannot be supported by readout? (One or two sentences on the alternative narrative — typically a re-positioning toward a strategic priority that does not depend on this readout.)"*

Capture the user's final text.

**status** — Default `active`. Confirm with the user. The only other valid value is `retired` (used when registering a previously-active aspirational that has been archived; rare for a fresh registration).

### Step 4 — Generate the next ASP-NNN id

Read `registers/aspirational-statements.md`. Find every `^### ASP-(\d{3})` heading; compute `max(N) + 1` zero-padded to three digits (or `ASP-001` if no entries exist). The id is append-only per `docs/CONVENTIONS.md` — do not reuse retired ids.

### Step 5 — Propose the new entry

Capture today's ISO date with `!date +%F` for the frontmatter `updated:` field.

Compose the entry block:

```markdown
### ASP-NNN

- linked_statement: <captured in Step 1>
- claim: <captured in Step 3>
- rationale: <captured in Step 3>
- evidence_generation_link: <captured in Step 3>
- expected_readout: <captured in Step 3>
- fallback_position: <captured in Step 3>
- status: <captured in Step 3>
```

Show the entry to the user. Ask for any final edits. Iterate until satisfied. If the user defers, **stop** without writing.

### Step 6 — Append to `registers/aspirational-statements.md`

Update the frontmatter `updated:` field to today's ISO date via Edit.

Insert the new entry under the `# Aspirational Statements` H1:

- If the file currently contains the `/pilar:init` stub placeholder (`<no aspirational statements yet>` or similar), replace that placeholder with the new entry block.
- Otherwise, append the new entry block after the last existing `### ASP-NNN` entry, separated by a blank line. Use Edit with `old_string` matching the last few lines of the final existing entry plus its trailing whitespace; `new_string` is those same lines plus the new entry block. Do not touch existing entries.

### Step 7 — Validate

Run:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate-schemas.py registers/aspirational-statements.md`

If validation fails, surface errors and correct via Edits. Do not proceed until validation passes.

### Step 8 — Propose the commit

Run `git status` to show changes. Propose this commit message (substitute the captured fields):

```
chore(pilar): register ASP-NNN aspirational statement

ASP-NNN registered against <linked_statement> per §7.7. Tied to
"<short evidence_generation_link summary>" with expected readout
<expected_readout>. Fallback position captured for the case where
the readout does not support the aspirational claim.
```

Wait for explicit user approval. On approval:

```bash
git add registers/aspirational-statements.md
git commit -m "$(cat <<'EOF'
... approved message ...
EOF
)"
```

If the user wants to revise the message, accept their version. If the user defers the commit, **stop** without committing — the file edit remains in the working tree.

### Step 9 — Brief the user on next steps

Tell the user:

> ✓ ASP-NNN registered against `<linked_statement>`. Recorded in `registers/aspirational-statements.md`.
>
> When the linked evidence generation activity reads out:
>
> - If data supports the claim: update the RS sources to cite the new readout's `<ref-id>`; the RS becomes evidence-supported and the aspirational entry can be retired (`status: retired`).
> - If data does not support the claim: the fallback position becomes the platform's narrative; retire the aspirational entry (`status: retired`).
>
> Use `/pilar:add-aspirational` again to register additional aspirational statements as the engagement evolves.

Stop.
