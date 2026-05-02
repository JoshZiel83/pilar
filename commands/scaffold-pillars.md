---
description: Propose the §6.4 pillar set tailored to the briefing, write pillar stub files, update roadmap — once-per-engagement
allowed-tools: Bash, Read, Write, Edit
---

Propose the §6.4 default pillar set, tailor it to the briefing's strategic priorities and indication, refine with the user, and on approval write one stub pillar file per approved pillar. Updates the `## Pillars` section of `roadmap.md`. Proposes the commit and waits for explicit user approval before committing — per decision #4 (no auto-commits).

This command is typically run **once per engagement** at the close of the briefing sprint or in a dedicated scaffolding sprint. To extend an existing pillar set later, edit `pillars/` and `roadmap.md` directly (a `/pilar:add-pillar` helper can land in P9 hardening).

## Pillar schema (use to seed each stub)

@${CLAUDE_PLUGIN_ROOT}/schemas/pillar.md

## Procedure

### Step 1 — Confirm we are in a pilar engagement

Run:

!`pwd && ls -1 roadmap.md briefing.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** — recommend `/pilar:init`. If `briefing.md` is missing or its body is still the `_TBD_` stub from `/pilar:init`, **stop** and recommend completing the briefing sprint first; scaffolding without a populated briefing produces a generic default that defeats the point of tailoring.

### Step 2 — Refuse if pillar files already exist

Run:

!`ls -1 pillars/*.md 2>/dev/null`

If the result is non-empty (any `.md` file under `pillars/` other than `.gitkeep`), **stop** and tell the user the pillar set has already been scaffolded. To extend it, edit `pillars/` and `roadmap.md` directly. To re-scaffold from scratch (rare), the user must remove existing pillar files manually first — confirm explicitly before they do.

### Step 3 — Read engagement state

Read `briefing.md` and capture:

- `## Strategic Priorities` — the numbered list, in order.
- `## Indication` — body text.
- `## Audiences` — list.
- `## Competitive Context` — body text.
- `## Constraints` — list.
- `## Evidence Generation Activities` — list.

Read `roadmap.md` and capture frontmatter (`project`, `client`, `product`, `indication`).

### Step 4 — Propose the default pillar set, tailored

The §6.4 default set is five pillars:

1. **Unmet need** — patient and clinician burden of disease in the indication; gaps current standard-of-care leaves.
2. **Disease mechanism / pathophysiology** — disease biology framing the therapeutic opportunity.
3. **Mechanism of action** — how the product engages the target and produces clinical effect.
4. **Clinical evidence** — pivotal trial(s), subgroup analyses, real-world evidence, key efficacy and safety findings.
5. **Clinical value framework** — positioning, sequencing, audience-relevant value claims tied to strategic priorities.

For each pillar, draft a one-paragraph rationale grounded in the briefing — name the strategic priority(ies) it advances and the audience(s) it speaks to. Be concrete: "P-04 Clinical Evidence advances Strategic Priority 1 (differentiation vs bispecifics on convenience and tolerability) and Strategic Priority 3 (safety communication) by anchoring efficacy and tolerability claims in the pivotal Phase 2 readout."

Propose adjustments to the default set if the briefing motivates them:

- If the indication is mechanism-tight (a single dominant target with limited disease-biology heterogeneity), consider merging "Disease mechanism" and "Mechanism of action" into a single pillar.
- If a Strategic Priority is safety-focused (as in the Aurelis ALR-217 fixture's Priority 3), consider adding a dedicated "Tolerability and safety" pillar — even though `## Clinical evidence` covers safety, splitting can be appropriate when safety is a primary differentiation axis.
- If the lifecycle stage is post-launch (real-world data dominate), consider an "Effectiveness in routine practice" pillar.
- Other adjustments drawn directly from the briefing's competitive context, constraints, or evidence-generation activities.

### Step 5 — Iterate with the user

Present the proposed set as a numbered list with each pillar's name and rationale. Ask the user for refinements: rename a pillar, add one, drop one, reorder, merge, split. Iterate briefly — one or two short rounds — until the user is satisfied.

When the order is settled, that order determines `P-NN` assignment: first proposed pillar becomes `P-01`, second becomes `P-02`, etc. Confirm the user is happy with the order before generating ids.

### Step 6 — Generate P-NN ids and slugs

For each approved pillar (in the user-confirmed order):

- `pillar_id` = `P-NN` zero-padded to two digits.
- `slug` = a kebab-case form of the pillar name (e.g., `Clinical Value Framework` → `clinical-value-framework`; lowercase ASCII alphanumerics + hyphens; collapse internal whitespace; strip leading/trailing hyphens).

Show the user the final id-and-slug list one more time. If they want to adjust a slug, accept it (the slug becomes part of the filename).

### Step 7 — Write one stub pillar file per approved pillar

Capture today's ISO date with `!date +%F`.

For each approved pillar, write `pillars/p-NN-<slug>.md`. Frontmatter:

- `artifact: pillar`
- `pillar_id: <P-NN>`
- `project: <project from roadmap>`
- `slug: <slug>`
- `status: draft`
- `created: <today>`
- `updated: <today>`

Body, per the §7.5 schema:

```markdown
# Pillar: <name>

## Strategic Rationale

_TBD — drafted in /pilar:pillar-narrative._

## Narrative

_TBD — drafted in /pilar:pillar-narrative._

## Scope

_TBD — drafted in /pilar:pillar-narrative._

## Scientific Statements

_TBD — drafted in /pilar:pillar-statements (after narrative is approved)._

## Open Items

_None yet._
```

Use the Write tool — these are new files.

### Step 8 — Update `roadmap.md`'s `## Pillars` section

Replace the current `## Pillars` section body (typically `(none yet)` or a placeholder table after `/pilar:init`) with a populated markdown table:

```markdown
## Pillars

| Pillar ID | Slug | Status |
|---|---|---|
| P-01 | <slug> | draft |
| P-02 | <slug> | draft |
| ... | ... | ... |
```

Use the Edit tool with `old_string` matching the existing `## Pillars` section and `new_string` containing the populated table. Update frontmatter `updated:` to today via a separate Edit.

### Step 9 — Validate

Run:

!`python3 scripts/validate-schemas.py pillars/ roadmap.md`

Note: `scripts/validate-schemas.py`'s directory mode globs `*.md` at the top level only — `pillars/` works because pillar files are flat.

If validation fails, surface errors and correct via Edits before continuing.

### Step 10 — Propose the commit

Run `git status` to show changes. Propose:

```
chore(pilar): scaffold N pillars per §6.4

Pillar set approved: P-01 (<name>), P-02 (<name>), …, P-NN (<name>).
Stubs at status: draft. Narrative + statements drafted in subsequent
sprints via /pilar:pillar-narrative and /pilar:pillar-statements.
```

Wait for explicit user approval. On approval:

```bash
git add pillars/ roadmap.md
git commit -m "$(cat <<'EOF'
... approved message ...
EOF
)"
```

If the user wants to revise the message, accept their version. If the user defers the commit, **stop** without committing — the files remain in the working tree.

### Step 11 — Brief the user on next steps

Tell the user:

> ✓ N pillars scaffolded under `pillars/`. Roadmap `## Pillars` section populated.
>
> Next: open a per-pillar drafting sprint via `/pilar:sprint-plan` — the plan's `## Artifacts to Modify` should list the specific pillar(s) the sprint will draft. Within the sprint, use:
>
> - `/pilar:pillar-narrative <P-NN>` to draft the Strategic Rationale, Narrative, and Scope sections; engage `/pilar:run-qc` for Editor pass; mark narrative-approved at the close.
> - `/pilar:pillar-statements <P-NN>` to draft Scientific Statements and Reference Statements once the narrative is approved; engage `/pilar:run-qc` for Editor + Fact-Checker; mark statements-approved at the close.
>
> Pillars typically take one or two sprints each. The sprint-sizing decision (narrative-only vs combined narrative+statements) is yours per §6.5.

Stop.
