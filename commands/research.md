---
description: Targeted research — search PubMed and ClinicalTrials.gov via MCP; save kept hits as provisional KB sources via a deterministic script that hits the upstream APIs directly
allowed-tools: Bash, Read, Write, Edit, mcp__claude_ai_PubMed__search_articles, mcp__claude_ai_PubMed__get_article_metadata, mcp__claude_ai_PubMed__find_related_articles, mcp__claude_ai_PubMed__get_full_text_article, mcp__claude_ai_PubMed__lookup_article_by_citation, mcp__claude_ai_PubMed__convert_article_ids, mcp__claude_ai_PubMed__get_copyright_status, mcp__claude_ai_Clinical_Trials__search_trials, mcp__claude_ai_Clinical_Trials__get_trial_details, mcp__claude_ai_Clinical_Trials__search_by_sponsor, mcp__claude_ai_Clinical_Trials__search_by_eligibility, mcp__claude_ai_Clinical_Trials__search_investigators, mcp__claude_ai_Clinical_Trials__analyze_endpoints
argument-hint: "<instruction or query>"
---

Targeted research for the writer mid-drafting: surface a small number of relevant hits from PubMed and ClinicalTrials.gov, let the writer pick what to keep, and save the kept hits as **provisional KB sources** under `knowledge-base/for_ingestion/`. Issue #11.

This is a **gap-fill tool, not a literature-review tool.** Default returns are small (5 per source). The use case is "I'm writing an RS, I need a single supporting source for this claim, find me one." For broader exploration of already-ingested sources, use `/pilar:explore`.

The user types either a natural-language instruction ("studies of our drug in elderly DLBCL") or a specific query (`tisagenlecleucel[Title] AND DLBCL[MeSH]`). This command analyzes the input, composes appropriate queries for each database, shows them, and lets the writer refine before running.

**Two-phase mechanism, by design:**

- **Search/preview** uses the PubMed and Clinical Trials MCP servers (`mcp__claude_ai_PubMed__*`, `mcp__claude_ai_Clinical_Trials__*`). Claude reads MCP responses and renders them for human review — paraphrase is harmless because the writer is the gate.
- **Canonical save** uses `scripts/research-fetch.py`, a deterministic Python script that hits PubMed E-utilities and the ClinicalTrials.gov v2 API **directly**. No LLM ever touches the bytes that get saved into the engagement repo. This is the hallucination guard for issue #11 — abstracts and trial details cited later as fact must be verbatim from upstream.

**Prerequisites:** Both the **PubMed** and **Clinical Trials** Claude.ai connectors must be enabled in your account. If either is missing, the command fails on first MCP call with a clear error; install via Claude.ai connector settings and restart Claude Code.

## Procedure

### Step 1 — Confirm engagement and parse argument

Run:

!`pwd && ls -1 roadmap.md briefing.md 2>&1 | head -5`

If `roadmap.md` is missing, **stop** and recommend `/pilar:init`. (No requirement on `knowledge-base/manifest.md` — research can stage source files before any manifest entries exist.)

Parse `$ARGUMENTS` as a single free-form string. Refuse with usage if empty:

```
/pilar:research "<instruction or query>"
  examples (targeted gap-fills):
    /pilar:research "axi-cel durability in elderly DLBCL"
    /pilar:research "tisagenlecleucel safety in Phase 2 r/r FL"
    /pilar:research "ongoing Phase 3 in r/r DLBCL with CAR-T comparator"
```

Capture as `user_input`.

### Step 2 — Read briefing context

Read `briefing.md`'s `## Indication`, `## Strategic Priorities`, `## Audiences`, `## Competitive Context`, plus `roadmap.md` frontmatter `product`. This context is used in Step 3 to disambiguate phrasing like "our drug" → the engagement's product name. Lightweight — the briefing informs query construction; it does not constrain.

### Step 3 — Construct the searches

Analyze `user_input`:

- If it already contains PubMed E-utility syntax (`[Title]`, `[Author]`, `[MeSH Terms]`, boolean operators) → use it verbatim for PubMed.
- Otherwise, translate to E-utility syntax leveraging briefing context. Resolve ambiguous references ("our drug", "the indication") to specific names from the engagement state.

For ClinicalTrials.gov, build a `query.term` string suitable for the v2 API plus any condition / intervention / phase / status filters that map cleanly from the user's intent.

Surface to the writer:

> I'll run these:
>
> - **PubMed:** `<constructed E-utility query>`
> - **ClinicalTrials.gov:** `<constructed query.term>` filters: `<filters>`
>
> Adjust either, or proceed?

Iterate one round if the writer refines (typed adjustments to either query). Capture final `pubmed_query` and `ct_query`.

### Step 4 — Search PubMed (preview)

Use the **`mcp__claude_ai_PubMed__search_articles`** tool with `query=pubmed_query`, `max_results=5`, `sort="relevance"`. Capture the returned PMIDs as `pubmed_pmids`.

If zero results → tell the writer; offer to refine the query (loop back to Step 3) or proceed to CT.gov-only.

Then call **`mcp__claude_ai_PubMed__get_article_metadata`** with `pmids=pubmed_pmids` to fetch title, journal, year, authors, abstract for each in a single batch.

### Step 5 — Search ClinicalTrials.gov (preview)

Use the **`mcp__claude_ai_Clinical_Trials__search_trials`** tool with the constructed `query.term` and any filters Claude inferred from the user input + briefing. Cap to ~5 hits for the targeted gap-fill use case.

If zero results or the MCP errors → tell the writer; offer retry or proceed PubMed-only.

The Clinical Trials MCP also exposes `search_by_sponsor`, `search_by_eligibility`, `search_investigators`, and `analyze_endpoints` — all declared in `allowed-tools`. v1's main loop uses only `search_trials` and `get_trial_details` (Step 7); the others remain available for the writer to invoke ad-hoc through Claude during the Step 3 query-refinement loop (e.g. "narrow to Genentech-sponsored trials" → switch to `search_by_sponsor`).

### Step 6 — Display results

Present two numbered lists side by side. Format:

```
PubMed (5 hits, more available):
  1. PMID 38123456 — Smith 2024 — Lancet
     [first 1–2 sentences of abstract]
  2. PMID 37890123 — Lee 2023 — JCO
     [first 1–2 sentences of abstract]
  …

ClinicalTrials.gov (5 hits, more available):
  1. NCT05123456 — [brief title]
     Phase 2, Recruiting; Conditions: DLBCL, FL
  2. …
```

If the writer asks "show more" → rerun the search with `max_results=20` / larger pageSize and re-display.

### Step 7 — Picks

Ask:

> Keep which?
> - PubMed: comma-separated indices, 'all', or 'none'.
> - CT.gov: same.

Wait for the response. Capture `kept_pubmed_ids` (PMIDs) and `kept_ct_ids` (NCT ids). If both empty/`none` → skip to Step 11 (chat-only outcome — no save).

For CT.gov picks, optionally use **`mcp__claude_ai_Clinical_Trials__get_trial_details`** to surface the full protocol (eligibility, primary outcomes, sponsors) before the writer commits — useful when the writer's pick depends on detail beyond the brief preview. The detail step is conversation-only; it does not affect what the script saves (the script does its own deterministic fetch).

### Step 8 — Per-pick "why kept"

For each kept hit, ask one short question:

> Why is `<id>` worth keeping? (one line — what claim or angle it supports.)

Capture each reason. These reasons feed the optional research note in Step 10, not the saved KB source file (which is verbatim from the API).

### Step 9 — Save provisional source files (deterministic script)

Compose the script invocation. With `kept_pubmed_ids = [38123456, 37890123]` and `kept_ct_ids = [NCT05123456]`:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/research-fetch.py --pubmed 38123456,37890123 --ctgov NCT05123456`

(Substitute the actual ids; default output is `knowledge-base/for_ingestion/`.)

Surface the script's output (file paths written) to the writer. The script writes one markdown file per id, with frontmatter (`provisional: true`, `source: pubmed|clinicaltrials.gov`, structured fields) and verbatim abstract/brief_summary content.

If a fetch fails for any id (404, malformed response) → the script reports per-id; partial success is OK. The script exits 0 if at least one succeeded; failed ids are listed in stderr. The writer can retry the failed ones individually later by re-running the command with just those ids.

### Step 10 — Optional research note in `explorations/p-NN.md`

Ask:

> Save a research note alongside? (yes / no — default no)

If `no` (or the writer doesn't affirmatively answer yes) → skip to Step 11.

If `yes`:

1. Ask which pillar (`P-NN` — must exist in `pillars/`):

   !`grep -l "^pillar_id: <P-NN>$" pillars/*.md 2>/dev/null` (substitute the captured pillar id)

   If no match, refuse with a brief explanation and re-prompt. Capture `pillar_id` and `pillar_path`.

2. Capture today's ISO date with `!date +%F`.

3. Compute a kebab-case slug from `user_input` (lowercase; strip non-alphanumeric; collapse whitespace to hyphens; truncate to 6 hyphen-separated tokens; strip leading/trailing hyphens).

4. Compose the H2 section body:

   ```markdown
   ## <today> — <slug>

   **Instruction:** <user_input>

   **PubMed query:** `<pubmed_query>`
   **ClinicalTrials.gov query:** `<ct_query>`

   **PubMed kept (N):**
   - PMID NNNN — <first author> <year>, <journal> — <why kept>
   - …

   **ClinicalTrials.gov kept (N):**
   - NCT NNNNNNNN — <brief title> — <Phase>, <Status> — <why kept>
   - …

   **Provisional sources written:**
   - `knowledge-base/for_ingestion/pmid-NNNN.md`
   - `knowledge-base/for_ingestion/nct-NNNNNNNN.md`

   **Hand-off:** run `/pilar:ingest-kb` to file these as REFs (status: provisional).
   ```

5. Check whether `explorations/<pillar_id>.md` exists:

   - **If exists** → Edit append: `old_string` matches the last few lines of the existing final section (with trailing whitespace); `new_string` is those lines plus a blank line plus the new H2 section.
   - **If does not exist** → Write with `# Explorations — <pillar_id> <pillar name>` H1 (read pillar name from the pillar file's `# Pillar: <name>` H1), blank line, the new H2 section. No frontmatter — these are scratch notes per the P7 refinement decision.

### Step 11 — Propose the commit

Run `git status` to show changes (one or more files under `knowledge-base/for_ingestion/`, optionally `explorations/<pillar_id>.md`).

Propose this commit message (substitute `N` = total provisional source files written):

```
docs(pilar): research — N provisional KB source(s) staged

Targeted research via /pilar:research. Provisional source files
written to knowledge-base/for_ingestion/ via
scripts/research-fetch.py (deterministic; no LLM in canonical
bytes per issue #11). Run /pilar:ingest-kb next to file them as
REF-NNN entries with status: provisional.
```

If a research note was saved in Step 10, append a sentence to the body: `Research note saved to explorations/<pillar_id>.md.`

Wait for explicit user approval. On approval:

```bash
git add knowledge-base/for_ingestion/ [explorations/<pillar_id>.md]
git commit -m "$(cat <<'EOF'
... approved message ...
EOF
)"
```

If the writer wants to revise the message, accept their version. If the writer defers, **stop** without committing — the working-tree changes remain.

### Step 12 — Brief next steps

Tell the writer (substituting `N` = number of provisional sources staged):

> ✓ Research complete. N provisional source(s) staged in `knowledge-base/for_ingestion/`.
>
> Next:
>
> - Run `/pilar:ingest-kb`. It will move the staged files to the appropriate taxonomy subfolder (`clinical/`, etc.), pre-fill manifest metadata from each file's frontmatter, ask you only to confirm `key_findings`, and add REFs at `status: provisional`.
> - Cite the new REFs in RS work as needed; they're real REFs in the manifest, just flagged provisional until full text arrives.
> - When the full PDF/source arrives: drop it into the appropriate `knowledge-base/<subfolder>/`, update the REF entry's `file:` and `status:` fields, and the REF becomes confirmed.
> - To check whether provisional content has drifted vs. upstream:
>
>   !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/research-fetch.py --verify <file>`
>
>   The `--verify` mode re-fetches the source and diffs critical fields (title, sponsor / first author, journal, abstract / brief summary). Exit 0 = clean; exit 1 = drift detected with diff.

Stop.
