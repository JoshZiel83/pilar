# pilar

> A structured collaborator for medical writers building Scientific Communication Platforms — turns a multi-session, multi-sprint engagement into versioned, schema-conformant, audit-able markdown.

**Status:** pre-release · installable shell (P2a) · in active development. The plugin can be installed from a Claude Code session today, but `/pilar:init` is a no-op stub. Real scaffolding behavior arrives with P2b (subagent isolation proof + functioning `/pilar:init`). See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) for the full plan and current phase.

---

## What pilar is

pilar is a Claude Code plugin that helps a medical writer collaborate with Claude Code to build a **Scientific Communication Platform (SCP)** for a pharmaceutical or biotech client. It is not a generator. It is a structured collaborator that drives a multi-session, multi-sprint process — from briefing through pillar development to consolidated whole-deliverable review — producing a versioned set of markdown artifacts under git.

The deliverables pilar produces are designed to translate downstream to a normalized database, an Excel workbook, or a Word document without rework.

## Who it's for

Medical writers at medical communications agencies. The plugin assumes scientific literacy, familiarity with evidence hierarchies and publication conventions, and comfort with iterative drafting and client review cycles. It does not over-explain platform conventions, evidence levels, or domain terminology — it explains its own reasoning, its proposed scaffolding choices, and the evidentiary basis for any draft language it produces.

## Why it exists

Scientific communication platform development has structural realities that off-the-shelf drafting tools handle poorly:

- **Evidence is not fully available at the start.** Reference statements drafted today may need to be revisited as new publications, congress abstracts, or in-flight study readouts arrive. The plugin tracks evidence gaps as first-class artifacts and re-engages when the knowledge base grows.
- **Strategic priorities are client-specific.** They must be captured before scaffolding is proposed, and the resulting deliverable must be evaluable against them as a whole.
- **Every meaningful step requires human review.** Sprint plans, pillar drafts, QC reports, consolidated drafts — the writer is the gatekeeper at every checkpoint.
- **Quality control must be independent.** Fact-checking, editing, and strategic review must not be conditioned on the rationale used to draft the copy under review. The plugin enforces this with isolated subagent contexts.
- **The deliverable evolves across many sessions.** Project state must be maintained so any session can resume coherently from the prior one.

## How it works

pilar operates through five roles:

- **Primary Collaborator** — drives the engagement, conducts briefing and scoping, maintains the roadmap, drafts language with the writer, manages handoffs between stages.
- **Knowledge Base Librarian** — ingests files added to the knowledge base, maintains the manifest, surfaces evidence gaps, proposes search strategies for closing them.
- **Fact-Checker** *(independent)* — verifies each reference statement against its cited sources. Runs in an isolated context that excludes the drafting rationale. Does not edit; reports findings.
- **Editor** *(independent)* — edits copy for style and lexicon within a meaning-preserving constraint. Runs in an isolated context that excludes the drafting rationale. Items where an edit would change meaning are flagged rather than edited.
- **Strategic Reviewer** *(independent)* — engages at the consolidated-draft stage. Reads only the briefing, the roadmap, and the consolidated draft, and evaluates whether the deliverable as a whole reflects the captured strategic priorities.

Work is organized into **sprints**, each closing with a uniform checkpoint pattern: the writer reviews a structured sprint summary and responds with one of four options — **Confirm**, **Request revisions**, **Defer**, or **Rewind**. Briefing is itself a sprint and uses the same checkpoint.

All artifacts are markdown with YAML frontmatter and stable identifiers (`pillar-id.SS-id.RS-id`, `ref-id`, `gap-id`, `asp-id`). The repository is the canonical project state. Commits are made at meaningful checkpoints — sprint close, pillar approval, QC pass, roadmap amendment — with commit messages proposed by the plugin and approved by the writer.

## The staged process

```
Briefing & Scoping
        │
        ▼
Knowledge Base Initial Intake
        │
        ▼
Initial Evidence Synthesis
        │
        ▼
Scaffolding Recommendation  ─── pillar set finalized
        │
        ▼
Per-Pillar Development  ─── narrative → scientific statements → reference statements
        │                    Editor + Fact-Checker run on each
        ▼
Consolidation
        │
        ▼
Whole-Deliverable Review  ─── Editor + Fact-Checker + Strategic Reviewer
        │                    re-consolidate on substantive findings; loop until clear
        ▼
Handoff  ─── client review · feedback re-entry · re-consolidation
```

Stages may be revisited as evidence and strategic understanding evolve. Movement between stages is recorded in the roadmap and requires explicit user confirmation.

For the full specification of behavior, artifacts, schemas, and interaction contracts, see [`scp-plugin-spec.md`](./scp-plugin-spec.md).

## Installation

> ⚠️ **Pre-release (P2a — installable shell).** The plugin installs and registers `/pilar:init`, but the command is a no-op stub. Real scaffolding behavior lands with P2b. ⭐ the repo to follow progress.

Install from any Claude Code session:

```
/plugin marketplace add JoshZiel83/pilar
/plugin install pilar@pilar
```

The first command registers this repo as a marketplace (it serves as a single-plugin self-marketplace via `.claude-plugin/marketplace.json`). The second installs the `pilar` plugin from the `pilar` marketplace. After install, the `/pilar:*` slash commands become available.

To update later: `/plugin update pilar@pilar`.

## Quickstart

> Available with Phase 2b. The flow below is the planned UX; today, `/pilar:init` is a no-op stub.

```
# In a fresh directory that will become your engagement repo:
/pilar:init                    # scaffolds the engagement directory structure + roadmap stub
/pilar:sprint-plan             # opens the briefing sprint
                               # (the plugin interviews you, drafts the sprint plan, you approve)
# ... briefing happens across one or more sessions ...
/pilar:sprint-close            # produces the structured sprint summary,
                               # presents it for Confirm / Revise / Defer / Rewind
```

The `/pilar:init` command will scaffold the directory structure described in §3 of the spec, create the initial `roadmap.md`, and orient you for the first sprint. Subsequent sessions will start with pilar reading the roadmap, the most recent sprint summary, and any active sprint plan to orient you to current state before any work resumes.

## Requirements

- **Claude Code** — version compatible with the `/plugin marketplace` flow.
- **git** — every engagement is a git repository; the repository is the canonical project state.

## Project status & roadmap

This project is in active development. The phased implementation plan, including the spec-to-implementation traceability table, the QC subagent independence contract, and a synthetic engagement scenario for end-to-end verification, lives in [`IMPLEMENTATION_ROADMAP.md`](./IMPLEMENTATION_ROADMAP.md). The decisions log at the bottom of that file records significant changes to spec interpretation or phase boundaries.

## Specification

The natural-language specification is the source of truth for plugin behavior, artifact schemas, and interaction contracts: [`scp-plugin-spec.md`](./scp-plugin-spec.md). It is not modified by implementation work.

## License

[MIT](./LICENSE) © 2026 Clinton Avenue BioPharma Partners, LLC

## Contributing

Contribution guidelines will be published with the `1.0.0` release. Until then, feedback on the specification or roadmap is welcome via GitHub issues.
