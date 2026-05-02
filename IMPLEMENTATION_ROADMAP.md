# pilar — Implementation Roadmap

> Phased plan for building the **pilar** Claude Code plugin from the natural-language spec at `scp-plugin-spec.md`. This document is the canonical reference for how the plugin will be built, in what order, and against what exit criteria. It is updated at the close of every phase; the §-by-§ traceability table is the durable proof that the spec is being honored.

---

## 1. Overview

The pilar plugin is a structured collaborator that drives a medical writer through the multi-sprint development of a Scientific Communication Platform — briefing, knowledge base intake, evidence synthesis, pillar scaffolding, per-pillar development, consolidation, and whole-deliverable review — producing schema-conformant markdown artifacts under git. The natural-language spec at `scp-plugin-spec.md` is the source of truth and is never modified by the plugin or by implementation work. This roadmap is the implementation contract.

### Implementation target

This repository (`/Users/joshuaziel/Documents/coding/pilar`) is the **plugin source repo**. It is packaged as a standard Claude Code plugin (manifest at `.claude-plugin/plugin.json`, plus `commands/`, `agents/`, `skills/`, `hooks/` directories per current conventions) and installed into a separate **engagement repo** for each client. The engagement repo holds the markdown artifacts; the pilar plugin holds the workflow logic.

### Load-bearing technical decisions

These are locked in early so all later phases plug in cleanly.

1. **Slash commands, not skills, for user-gated workflow.** Skills auto-trigger on context; the spec requires the user to gate every meaningful checkpoint. Slash commands are the idiomatic surface. Naming convention: `/pilar:<verb-object>` (e.g. `/pilar:init`, `/pilar:sprint-plan`, `/pilar:sprint-close`, `/pilar:run-qc`).
2. **Subagents for the three QC roles** (Editor, Fact-Checker, Strategic Reviewer). Each runs in an isolated context window. The parent passes only the inputs §8 permits — see the Independence Contract appendix below. Defined in `agents/<role>.md`.
3. **QC sequencing (Editor → Fact-Checker → Strategic Reviewer) is enforced by command logic, not hooks.** Claude Code hooks can block or approve a single tool call but cannot reliably orchestrate a multi-step ordering across separately invocable subagents. `/pilar:run-qc` is the single entry point that invokes the roles in spec-mandated order.
4. **No auto-commits.** A `/pilar:commit-checkpoint` command stages files, proposes a commit message, and waits for explicit user approval — aligning with §3 ("the plugin proposes commit messages and the user approves them") and Claude Code conventions.
5. **Versioning strategy.** During active development, `version` is omitted from `plugin.json` so the git commit SHA serves as the version (every push appears to installed clients as an available update — useful for iteration). On releases, `version: "X.Y.Z"` is set explicitly in `plugin.json` to match a git tag (`v0.1.0`, `v0.2.0`, …) and bumped per [semver](https://semver.org/). `CHANGELOG.md` is updated per release in [Keep-a-Changelog](https://keepachangelog.com/) format.

---

## 2. Phasing

### Phase 1 — Implementation Roadmap document  *(this file is the deliverable)*

**Scope.** This document — phasing, exit criteria, dependencies, risk register, the §-by-§ traceability table, the independence-contract appendix, the synthetic engagement scenario, and the decisions log scaffolding.

**Exit criteria.** User reviews and approves; document is committed (`docs: add implementation roadmap`).

**Risks.** Roadmap drifts from spec across the long implementation. Mitigation: the traceability table is updated at the close of every later phase as part of that phase's exit gate.

**Dependencies.** Spec only.

---

### Phase 2 — Walking skeleton (plugin packaging + subagent isolation + marketplace install path)  *(complete)*

**Status.** Closed 2026-05-02. All exit criteria met — see decisions log.

**Scope.** A minimal but end-to-end-shaped plugin that proves the load-bearing technical decisions AND the canonical marketplace install path before larger phases commit to them.

- `.claude-plugin/plugin.json` manifest with `name: "pilar"`, `description`, `author`, `homepage`, `repository`, `license: "MIT"`, `keywords`, and `$schema`. `version` is omitted during active dev (commit SHA serves as version per decision #5).
- `.claude-plugin/marketplace.json` declaring this repo as a single-plugin self-marketplace: `name: "pilar"`, `owner`, and a single plugin entry with `source: "./"`. This is what allows `/plugin marketplace add https://github.com/JoshZiel83/pilar` to work.
- One slash command `/pilar:init` that scaffolds the §3 directory structure plus a roadmap stub in a target engagement repo.
- One artifact schema (the roadmap, §7.1) with YAML frontmatter and a stub validator.
- One **stub Fact-Checker subagent** demonstrating the independence contract: receives only the artifact under review and cited source files, returns a stub fact-check report. Stubbed evaluation; the point is to prove context isolation works.
- README transitioned from pre-release status to install-verified — install path documented as `/plugin marketplace add https://github.com/JoshZiel83/pilar` → `/plugin install pilar@pilar`. (HTTPS URL is required because the `<owner>/<repo>` shorthand defaults to SSH, which fails for users without SSH keys configured.)
- CI scaffolding that runs the schema validator, a context-audit assertion, and `claude plugin validate .` as a release gate.

**Exit criteria.** From a clean Claude Code session: `/plugin marketplace add https://github.com/JoshZiel83/pilar` succeeds → `/plugin install pilar@pilar` succeeds → `/pilar:init` scaffolds an engagement repo → stub Fact-Checker subagent is invoked with a constrained context → context-audit assertion passes (no drafting-only inputs leaked into the subagent prompt) → CI passes including `claude plugin validate .`.

**Risks.** Subagent context isolation remains the single hardest technical unknown. Marketplace install path is well-trodden ground but adds a non-trivial verification surface; mitigation is `claude plugin validate .` running in CI from this phase forward. If we cannot constrain subagent inputs the way §4 requires, the entire QC architecture must be rethought. Locating these risks in P2 is deliberate.

**Dependencies.** P1.

---

### Phase 3 — Schemas, defaults, registers, validator  *(complete)*

**Status.** Closed 2026-05-02 with the **v0.1.0** release tag. All §7 schemas ship with golden fixtures and validator coverage; §9 disallowed-pattern defaults are baked into the style-guide schema; stable-ID conventions are documented in [docs/CONVENTIONS.md](./docs/CONVENTIONS.md) and enforced by the validator. See decisions log and `CHANGELOG.md` for the full closure trail.

**Scope.** All ten artifact templates from §7 with frontmatter and stable-ID conventions; §9 disallowed-pattern defaults seeded into the style guide; lexicon and the two registers (evidence gaps, aspirational statements) as empty-but-valid documents; a read-only schema validator that the plugin can run before commits to catch drift.

**Exit criteria.** Every schema in §7 has a template and validator coverage. Stable-ID conventions (`pillar-id.SS-id.RS-id`, `ref-id`, `gap-id`, `asp-id`) are documented and asserted by the validator so §11 translation has zero rework later.

**Risks.** Schema churn during later phases. Mitigation: validator + golden examples in `examples/`; any change requires an explicit migration note in the decisions log.

**Dependencies.** P2.

---

### Phase 4 — Sprint engine + Primary Collaborator core  *(briefing merged in)*  *(complete)*

**Status.** Closed 2026-05-02. `/pilar:init` extended to seed the full set of engagement-artifact stubs and a CLAUDE.md (M1); `/pilar:sprint-plan` drafts and commits sprint plans from roadmap state with §5.3 checkpoint discipline (M2); `/pilar:sprint-close` implements the four-option checkpoint state machine — Confirm / Request revisions (bounded or substantive) / Defer / Rewind — with branch-specific roadmap updates and inline commit-message proposals (M3); `/pilar:sprint-amend` handles in-flight plan revisions per §5.2 (M4); seven seeded engagement-artifact stubs validated clean against the schema validator in a smoke-test simulation (M5). No release tagged at this phase per release-gating policy.

**Scope.** Briefing is a sprint per §5.3, so the sprint engine and the briefing flow are built together to avoid duplicating checkpoint plumbing.

- Project init (extending P2's `/pilar:init` to also drop a CLAUDE.md authoring note).
- **Session resumption** (§5.4): on session start, read roadmap + most recent sprint summary + active sprint plan, orient the user.
- `/pilar:sprint-plan` to draft and commit a sprint plan from the next-sprint scope in the roadmap.
- `/pilar:sprint-close` implementing the four-option checkpoint (Confirm / Revise / Defer / Rewind), Human Response capture in summary frontmatter, **commit-message proposal**, and roadmap update on close.
- `/pilar:sprint-amend` for in-flight plan amendments.
- Briefing implemented as the canonical first sprint, exercising every checkpoint mechanic against real artifacts.

**Exit criteria.** A briefing sprint runs end-to-end against a fresh engagement repo and is committed; the next sprint can be planned from the closed sprint's "Next Sprint Proposed Scope".

**Risks.** Checkpoint state machine and rewind semantics. Mitigation: a tested state-machine artifact lives in this roadmap (Appendix B below) and is reused as the implementation reference.

**Dependencies.** P3.

---

### Phase 5 — Editor and Fact-Checker subagents  *(independence contract codified)*  *(complete)*

**Status.** Closed 2026-05-02 (untagged on `main` per saved release-gating policy). Five sub-milestones: M1 upgraded the Fact-Checker from P2 stub to real evaluation with `tools: [Read]` and path-based prompt template; M2 shipped the Editor subagent with both `drafting` and `consolidated-draft` operating contexts in a single `agents/editor.md` file; M3 extended `/pilar:run-qc` to orchestrate Editor → apply edits → Fact-Checker per §8 sequencing (decision #3); M4 refactored `scripts/context-audit.py` to a `QC_HARNESSES` registry and registered the Editor harness; M5 shipped `examples/qc-fixtures/` as a self-contained QC test scenario.

**Scope.** Built **before** pillar development so the first pillar drafted gets real QC, rather than back-filling QC against artifacts produced without it.

- **Editor subagent** with two operating contexts: drafting (no change log, flagged-items list only) and consolidated-draft (structured change log required, edits committed in a discrete commit per §6.8). Reads only artifact under review + lexicon + style guide.
- **Fact-Checker subagent**. Reads only artifact under review + cited source files (§8). Verifies reference statements against sources, flags overstatement, misattribution, insufficient source strength.
- **Editor-before-Fact-Checker sequencing** wired into `/pilar:run-qc` command logic (per the load-bearing decision above).
- Reusable **subagent invocation harness** consumed by P8 for the Strategic Reviewer.
- Automated **context-audit test** asserting each subagent prompt contains only the inputs §8 permits.

**Exit criteria.** Both subagents run on hand-authored example pillar fragments stored in `examples/` and produce schema-conformant reports per §7.10.

**Risks.** Leakage of drafting rationale into QC context. Mitigation: context-audit test runs in CI; any new subagent-bound input requires a roadmap-decisions-log entry.

**Dependencies.** P4.

---

### Phase 6 — Knowledge Base Librarian + registers  *(complete)*

**Status.** Closed 2026-05-02 (untagged on `phase-6` branch per saved release-gating policy). Five sub-milestones: M1 shipped `/pilar:ingest-kb` initial-intake mode (taxonomy proposal against the five default subfolders seeded by `/pilar:init`, manifest entry proposal with user-confirmed citation/key_findings/population, validate-schemas gate); M2 added auto-detected incremental mode (new-file delta vs existing manifest, append-only `REF-NNN` continuation, mode-specific commit messages); M3 shipped `scripts/detect-gaps.py` (orphan-RS predicate reusing `validate-schemas.py` parsing primitives via `importlib.util`; flags missing/empty sources lists and unresolved REFs with three orphan classes; markdown and JSON output formats) and wired auto-gap creation into `/pilar:ingest-kb` Step 12 with separate user-approved commit; M4 shipped `/pilar:add-aspirational` with full §7.7 walkthrough including briefing-driven `evidence_generation_link` selection from `## Evidence Generation Activities`; M5 shipped `examples/p6-fixtures/` (3 synthetic markdown sources, post-ingest manifest with REF-001..003, P-99 orphan pillar with two intentional orphans across both detection paths, post-detect evidence-gaps with two GAP entries, one ASP entry, README documenting manual smoke tests). User design decisions: slash-command-driven Librarian with no `agents/librarian.md` file (no §4 independence contract per spec); orphan-RS predicate as a standalone Python script invokable both via the slash command and ad-hoc; deferred unification with the Fact-Checker's "lacks support" finding to P8 cleanup (the predicates are structurally different — orphan-RS is structural; FC "lacks support" is semantic).

**Scope.** KB intake (§6.2), manifest entry creation (§7.4), taxonomy proposal with user approval, gap detection on reference statements lacking sources, search-strategy proposal (§10), aspirational statement registration with evidence-generation linkage (§7.7).

Lands after P5 because gap detection and Fact-Checker's "lacks support" finding share an unsupported-RS predicate that should be implemented once. (P6 closure note: the two predicates turned out to be structurally distinct — orphan-RS is a manifest-resolution check; FC "lacks support" is source-reading semantic evaluation. Unification deferred to P8 if it remains useful.)

**Exit criteria.** Ingesting a sample KB folder produces a valid manifest; orphaned RS in fixture pillars open gap entries automatically; proposing an aspirational statement walks the user through every §7.7 field including evidence-generation linkage.

**Risks.** Binary inputs in the KB. Mitigation: commit binaries as-is per §3; store extracted metadata only in the manifest.

**Dependencies.** P5.

---

### Phase 7 — Per-pillar development

**Scope.** Scaffolding recommendation (§6.4 default pillar set tailored to client priorities), pillar narrative drafting, scientific-statement and reference-statement drafting, sprint-sized partition (narrative-only sprint vs combined sprint), pillar status frontmatter transitions (`draft` → `narrative-approved` → `statements-approved` → `complete`), pillar-approval commit. P5 QC and P6 Librarian engage automatically per the sprint plan.

**Exit criteria.** One pillar driven from scaffolding proposal through `statements-approved` against the synthetic engagement.

**Risks.** SS/RS identifier collisions and re-numbering on rewind. Mitigation: append-only ID assignment recorded in the decisions log; rewinds reopen IDs but do not re-use them.

**Dependencies.** P5, P6.

---

### Phase 8 — Consolidation + Strategic Reviewer + whole-deliverable review

**Scope.** Consolidated-draft assembly (§6.7); Strategic Reviewer subagent (§4.5) reading only briefing + roadmap + edited consolidated draft; **discrete editorial commit** at the consolidated stage with structured change log (§6.8); whole-deliverable review loop on substantive findings; handoff and tagging on clearance (§6.9); client-feedback re-entry sprint pattern.

**Exit criteria.** Full whole-deliverable review runs on a multi-pillar fixture and produces all three reports; the re-consolidation loop terminates cleanly when the consolidated draft clears review.

**Risks.** Change-log granularity and diff readability. Mitigation: per-target change records (per §7.10 editorial-report schema) and a pre-commit diff preview shown to the user before the discrete editorial commit.

**Dependencies.** P5, P7.

---

### Phase 9 — Sample engagement, release management, hardening

**Scope.** Dogfood on the synthetic engagement defined in Appendix C below from briefing through handoff. Ship `examples/` with anonymized fixtures (briefing, KB sample, one finished pillar, one full whole-deliverable review cycle). CLAUDE.md authoring guidance for the writer. Final spec-to-implementation traceability audit.

**Release management additions.**

- `CHANGELOG.md` (Keep-a-Changelog format), back-filled to cover the path from `v0.1.0` through `v1.0.0`.
- Git tag conventions (`v0.1.0`, `v0.2.0`, …, `v1.0.0`) as the release boundary; tags are the source of truth for what a release contains.
- `claude plugin validate .` as a pre-release gate (CI-enforced from P2 onward).
- README polished to launch quality: features, quickstart with a real walkthrough, badges, contributing guide, requirements.
- `1.0.0` release tag at P9 close — first stable, semver-pinned version, with explicit `version: "1.0.0"` in `plugin.json` matching the tag (transitioning out of commit-SHA-as-version per decision #5).

**Exit criteria.** A fresh installer can run the synthetic engagement end-to-end with the user roleplaying the medical writer at each checkpoint; the §-by-§ traceability table is fully green; `v1.0.0` is tagged on `main`; `plugin.json` has `version: "1.0.0"` matching the tag; `CHANGELOG.md` documents the full path from `v0.1.0` to `v1.0.0`.

**Dependencies.** All prior.

---

## 3. Spec Traceability

Updated at the close of every phase. Status legend: `planned` (in scope of named phase, not yet built) · `partial` (started, exit criteria not met) · `done` (phase exit criteria met) · `out-of-scope` (excluded per §13).

| Spec section | Subject | Phase | Plugin surface | Status |
|---|---|---|---|---|
| §3 | Project structure & git conventions | P2, P4 | `/pilar:init` (full §3 tree + all engagement-artifact stubs), `/pilar:sprint-plan`/`-close`/`-amend` propose commit messages inline | done |
| §4.1 | Primary Collaborator | P4 | CLAUDE.md auto-load + sprint slash commands drive every meaningful interaction | done |
| §4.2 | KB Librarian | P6 | `commands/ingest-kb.md`, `commands/add-aspirational.md`, `scripts/detect-gaps.py` (slash-command-driven; no `agents/librarian.md` per P6 design decision — Librarian has no §4 independence contract) | done |
| §4.3 | Fact-Checker (independence) | P2 stub, P5 real | `agents/fact-checker.md` (`tools: [Read]`, real evaluation), `commands/run-qc.md`, `scripts/context-audit.py` | done |
| §4.4 | Editor (independence, two contexts) | P5 | `agents/editor.md` (single file with `operating_context` flag; `tools: [Read, Edit]` for surgical edits), `commands/run-qc.md`, `scripts/context-audit.py` | done |
| §4.5 | Strategic Reviewer (independence) | P8 | `agents/strategic-reviewer.md` | planned |
| §5.1 | Roadmap | P3 schema, P4 maintenance | `schemas/roadmap.md`, `/pilar:sprint-plan` and `/pilar:sprint-close` mutate roadmap with targeted edits | done |
| §5.2 | Sprint plan | P3 schema, P4 logic | `schemas/sprint-plan.md`, `/pilar:sprint-plan`, `/pilar:sprint-amend` | done |
| §5.3 | Sprint-end checkpoint (4 options) | P4 | `/pilar:sprint-close` state machine encoding Appendix B in command body | done |
| §5.4 | Session resumption | P4 | CLAUDE.md auto-loaded from engagement repo root (dropped by `/pilar:init`) | done |
| §6.1 | Briefing & scoping | P4 | Briefing implemented as Sprint 1 special case in `/pilar:sprint-plan` | done |
| §6.2 | KB initial intake | P6 | `/pilar:ingest-kb` (auto-detected initial-intake or incremental mode; taxonomy proposal against §3 default subfolders) | done |
| §6.3 | Initial evidence synthesis | P6 / P7 | KB intake done at P6 (`/pilar:ingest-kb`); the synthesis flow that informs §6.4 scaffolding remains P7 territory | partial |
| §6.4 | Scaffolding recommendation | P7 | `/pilar:scaffold-pillars` | planned |
| §6.5 | Per-pillar development | P7 | `/pilar:pillar-narrative`, `/pilar:pillar-statements` | planned |
| §6.6 | Lexicon & style guide | P3 defaults, P5 enforce, P7 accumulate | `schemas/lexicon.md`, `schemas/style-guide.md` (with §9 defaults), `agents/editor.md` enforces both | done |
| §6.7 | Consolidation | P8 | `/pilar:consolidate` | planned |
| §6.8 | Whole-deliverable review | P8 | `/pilar:run-qc --consolidated`, discrete editorial commit | planned |
| §6.9 | Handoff | P8 / P9 | `/pilar:handoff` (tag + roadmap update) | planned |
| §7.1 | Roadmap schema | P2 stub, P3 full | `schemas/roadmap.md`, `scripts/validate-schemas.py` | done |
| §7.2 | Briefing schema | P3 | `schemas/briefing.md` | done |
| §7.3 | Sprint plan & summary schemas | P3 | `schemas/sprint-plan.md`, `schemas/sprint-summary.md` | done |
| §7.4 | KB manifest schema | P3 | `schemas/kb-manifest.md` | done |
| §7.5 | Pillar file schema | P3 | `schemas/pillar.md` (with nested SS/RS validation) | done |
| §7.6 | Evidence gaps register schema | P3 | `schemas/evidence-gaps.md` | done |
| §7.7 | Aspirational statements register schema | P3 | `schemas/aspirational-statements.md` | done |
| §7.8 | Lexicon schema | P3 | `schemas/lexicon.md` | done |
| §7.9 | Style guide schema (with §9 defaults baked in) | P3 | `schemas/style-guide.md` | done |
| §7.10 | QC report schemas (3) | P3 | `schemas/{fact-check,editorial,strategic-alignment}-report.md` | done |
| §8 | QC rules (independence, sequencing) | P2 isolation proof + P5 + P8 full | `/pilar:run-qc` orchestrates Editor → Fact-Checker; `agents/{editor,fact-checker}.md`; `scripts/context-audit.py` registry. Strategic Reviewer added at P8. | done |
| §9 | Writing style requirements | P3 defaults, P5 enforce | `schemas/style-guide.md` + `agents/editor.md` enforces the eight defaults during the editorial pass | done |
| §10 | Evidence enlargement protocol | P6 | `scripts/detect-gaps.py` (orphan-RS predicate: missing/empty sources, unresolved REFs); `/pilar:ingest-kb` Step 12 wires the scan in and walks the user through Librarian-drafted `proposed_search:` fields per gap | done |
| §11 | Output translation | out-of-scope | Schemas designed for future translation; stable IDs asserted in P3 (see [docs/CONVENTIONS.md](./docs/CONVENTIONS.md)) | out-of-scope |
| §12 | Tooling and artifact layering | P2, throughout | Engagement-level vs Claude Code task-level separation enforced by directory layout and command behavior | done |
| §13 | Out of scope | n/a | n/a | out-of-scope |

> **Note on distribution infrastructure.** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `CHANGELOG.md`, the `README.md`, the LICENSE, and CI configuration are implementation infrastructure that supports §13's framing of the spec ("behavior, artifacts, and interaction contracts"). They are not §-mapped requirements — they are the packaging that lets the §-mapped behavior be installed and operated. P2 is responsible for the install-path infrastructure; P9 is responsible for release-management infrastructure.

---

## 4. Appendix A — Independence Contract for QC Subagents

§4 and §8 require the QC roles to evaluate copy without seeing the Primary Collaborator's drafting context. This appendix specifies, per role, the exact set of inputs the parent is **permitted** to pass into the subagent's context window and the inputs that are **explicitly withheld**. The context-audit test in P5 asserts these constraints for every invocation.

### Editor

**Permitted inputs.** Artifact under review (pillar narrative, scientific statement, reference statement, or consolidated draft). Lexicon. Style guide. Editor's own operating-context flag (`drafting` or `consolidated-draft`).

**Withheld inputs.** Briefing. Roadmap. Drafting rationale or the Primary Collaborator's reasoning notes. Prior sprint summaries. KB manifest. Source files. Other pillars (except in `consolidated-draft` context, where the consolidated draft itself contains them).

### Fact-Checker

**Permitted inputs.** Artifact under review (scientific statement and reference statement copy, with their `sources` ref-ids). The cited source files themselves, retrieved from the KB. Operating-context flag.

**Withheld inputs.** Briefing. Roadmap. Drafting rationale. Lexicon. Style guide. Prior sprint summaries. Other pillars. The Editor's report. Manifest entries for *uncited* sources.

### Strategic Reviewer

**Permitted inputs.** Briefing. Roadmap. Edited consolidated draft (post-Editor). Strategic Reviewer engages only at the consolidated-draft stage.

**Withheld inputs.** Drafting rationale. Per-pillar progress notes. KB manifest and source files. Editor's change log and Fact-Checker's report (the Strategic Reviewer evaluates the deliverable itself, not the QC discourse around it).

### Enforcement

The harness that invokes each subagent constructs the prompt from a fixed allowlist of fields drawn from the artifact graph. Adding a new field to any allowlist requires a decisions-log entry tied to a spec citation. The context-audit test fails if any subagent prompt contains a token signature characteristic of a withheld input.

---

## 5. Appendix B — Sprint-End Checkpoint State Machine (§5.3)

```
[draft sprint plan]  ──approved──▶  [sprint open]
                                          │
                                  execution + QC
                                          │
                                          ▼
                                 [sprint summary draft]
                                          │
                          present to user at checkpoint
                                          │
        ┌──────────────┬────────────┴────────────┬──────────────┐
        ▼              ▼                         ▼              ▼
    Confirm        Request revisions         Defer          Rewind
        │              │                         │              │
   amend summary  bounded? ─yes─▶ amend     park items     plan new sprint
   with response  plan & continue execution   in open      with reopened scope
        │           │                          items        record reopen in
   commit summary   no ─▶ record items in       │           decisions log
        │           next-sprint scope           │              │
   update roadmap   │                           │              │
        │           │                           │              ▼
   plan next sprint  ▶ close sprint  ◀──────────┘     [sprint open]
```

`human_response` frontmatter values: `pending` (default while open) → `confirmed` | `revisions-requested` | `deferred` | `rewind` (terminal). The "Human Response" section captures the user's verbatim feedback. The summary is committed only after `human_response` reaches a terminal value.

---

## 6. Appendix C — Synthetic Engagement (Phase 9 dogfood target)

Defining this scenario in P1 anchors every later phase to a concrete acceptance test and supplies fixture content for `examples/`.

- **Client (anonymized).** Aurelis Therapeutics — mid-stage biotech.
- **Product (fictional).** ALR-217, an oral small-molecule inhibitor.
- **Indication.** Relapsed/refractory diffuse large B-cell lymphoma (DLBCL) in patients ineligible for or progressing after CAR-T.
- **Lifecycle stage.** Post-Phase 2 single-arm pivotal readout; ~18 months to anticipated launch.
- **Audiences.** Practicing hematologist-oncologists (community + academic); academic key opinion leaders in lymphoma; pharmacy & therapeutics committees at large IDNs.
- **Strategic priorities.**
  1. Differentiate ALR-217 from emerging bispecific antibodies on convenience, sequencing flexibility, and tolerability in older patients.
  2. Establish ALR-217's optimal positioning in the 3rd-line and beyond setting given the post-CAR-T treatment landscape.
  3. Communicate the safety profile credibly to community oncologists, including practical management of expected adverse events.
- **KB seed (fixtures to ship in P9 `examples/`).**
  - One pivotal Phase 2 trial publication.
  - One mechanism-of-action paper.
  - Two competitor data publications (one bispecific antibody, one alternative oral agent).
  - The current NCCN B-cell lymphomas guideline excerpt covering 3rd-line.
  - One ASH abstract reporting subgroup analysis in elderly patients.
  - One review article on post-CAR-T treatment sequencing.
- **Anticipated inputs (per §6.1).** Long-term follow-up readout (TBD); ongoing real-world evidence study (TBD); investigator-initiated trial in elderly subgroup (TBD).
- **Constraints.** No client-supplied lexicon or style guide — both developed during the engagement (§6.6).

The fixtures will be hand-authored at P9 time. No real publications, no real patient data, no real product names beyond what is fictional here.

---

## 7. Open Assumptions

These are recorded here rather than blocking the plan; the user can correct any of them at sign-off or during a later phase.

1. The plugin source lives in this repo; engagements are separate repos that install the plugin. *(If the user prefers the plugin live alongside a real engagement, P2 packaging changes.)*
2. This repo is its own marketplace from P2 onward — a single-plugin self-marketplace at `.claude-plugin/marketplace.json` with `source: "./"`. Multi-plugin marketplace expansion (hosting other plugins under the same marketplace) is out of scope.
3. The synthetic engagement scenario (Appendix C) is invented. If the user has a real anonymizable scenario they prefer for dogfooding, it replaces Appendix C.
4. CI for the plugin repo (running schema validator + context-audit tests) is set up in P2 alongside the walking skeleton.
5. The plugin uses the slash-command prefix `/pilar:` for all user-facing entry points. (Consistent with the plugin name; can be changed before P2.)

---

## 8. Decisions Log

Append-only. Every decision that affects spec interpretation, schema, or phase boundary is recorded here with date and rationale. Empty at P1 commit.

| Date | Decision | Rationale | Phase / spec § |
|---|---|---|---|
| 2026-05-01 | Fold marketplace distribution into P2; add release management to P9; add load-bearing decision #5 (versioning). | Without `.claude-plugin/marketplace.json` the canonical install path (`/plugin marketplace add JoshZiel83/pilar`) cannot be validated until P9 — too late given that P2's whole purpose is to de-risk the install path. Treating distributability as a property the walking skeleton ships with from day one keeps the install UX honest from first commit. | P2, P9, §13 |
| 2026-05-02 | Document install command using full HTTPS URL (`https://github.com/JoshZiel83/pilar`) rather than `<owner>/<repo>` shorthand. | The shorthand defaults to SSH protocol (`git@github.com:...`) and fails with `Permission denied (publickey)` for users without SSH keys configured — a hostile failure for pilar's audience (medical writers). The HTTPS URL form sidesteps the SSH default and is also typo-resistant (full URL rather than two transcribed identifiers). Verified working by user against the live repo. README also gains a Troubleshooting subsection covering the SSH failure and other common errors. | P2, README install UX |
| 2026-05-02 | Phase 2 (walking skeleton) closed. | All exit criteria met across six sub-milestones: M1 install UX hardened with HTTPS URL + troubleshooting; M2 roadmap schema (§7.1) + Python validator + `examples/fixtures/roadmap.md` golden file + CI `schema-validate` job; M3 real `/pilar:init` scaffolds the §3 directory tree + seeds roadmap.md from the schema template + intake interview + commit-approval gate; M4 stub Fact-Checker subagent (`agents/fact-checker.md` with `tools: []` for maximum isolation) + `/pilar:run-qc` parent harness using a sentinel-bounded prompt template with a four-variable allowlist; M5 static context-audit (`scripts/context-audit.py`) parses the run-qc template and asserts only allowlisted variables and no forbidden tokens, plus enforces the empty-tools contract on the subagent; CI `context-audit` job activated. The §4/§8 Independence Contract is now both demonstrated (M4) and gated against regression (M5). Phase 3 (full §7 schemas) is the natural next step. | P2 closure |
| 2026-05-02 | Phase 3 (schemas, defaults, registers, validator) closed; tagged **v0.1.0** as the first user-facing release. | All §7 schemas (briefing, sprint-plan/-summary, kb-manifest, pillar, evidence-gaps, aspirational-statements, lexicon, style-guide, fact-check/editorial/strategic-alignment reports) ship with golden fixtures based on the Aurelis/ALR-217 synthetic engagement; §9 disallowed-pattern defaults baked into the style-guide schema; stable-ID conventions adopted (`REF-NNN`, `P-NN`, `SS-NN`, `RS-NN`, `GAP-NNN`, `ASP-NNN`, `FC-<sprint>-NNN`, `ED-<sprint>-NNN`, `CL-NNN`, `SA-<draft-tag>-NNN`) and enforced by the validator (format checks, uniqueness within scope, nested SS/RS validation in pillar, composite-id reference checks). Conventions documented in `docs/CONVENTIONS.md`. `CHANGELOG.md` initialized in Keep-a-Changelog format. Decision #5 versioning cycle: pin `version: "0.1.0"` for the release commit, then unpin in the immediate follow-up commit so commit-SHA-as-version resumes for ongoing dev. | P3 closure, §7, §9, §11, decision #5 |
| 2026-05-02 | Phase 4 (sprint engine + Primary Collaborator core, briefing merged in) closed. **No release tag** — release-tagging is now user-gated per the saved release policy and was not authorized for P4 closure. | Five sub-milestones: M1 extends `/pilar:init` to seed the seven engagement-artifact stubs (`roadmap.md`, `briefing.md`, `style-guide.md` with §9 defaults inherited, `lexicon.md`, `knowledge-base/manifest.md`, two registers) plus a static `CLAUDE.md` template that triggers session resumption (§5.4) on every Claude Code session start in the engagement directory. M2 ships `/pilar:sprint-plan` with the §5.2 sprint-opening flow + Sprint-1 briefing-sprint defaults. M3 ships `/pilar:sprint-close` encoding the §5.3 four-option checkpoint state machine (Confirm / Request revisions [bounded or substantive] / Defer / Rewind) with branch-specific roadmap updates. M4 ships `/pilar:sprint-amend` for in-flight plan revisions per §5.2 second paragraph. M5 verified via simulated scaffolding — seven seeded artifact stubs validate clean against `scripts/validate-schemas.py`. Design decisions: CLAUDE.md auto-load over a `/pilar:resume` command (user choice this session); inline commit-message proposals in each sprint command rather than a shared `/pilar:commit-checkpoint` helper (user choice this session). | P4 closure, §3, §4.1, §5.1–§5.4, §6.1 |
| 2026-05-02 | Phase 5 (Editor and Fact-Checker subagents, Independence Contract codified for real evaluation) closed. **No release tag** per saved release-gating policy. | Five sub-milestones: M1 upgraded the Fact-Checker from P2 stub to real evaluation — `tools: []` → `tools: [Read]`, prompt template variables `{artifact_text, source_texts}` → `{artifact_path, source_paths}`, real verification logic flagging overstatement / misattribution / source-strength mismatch / unsupported claims and synthesis defensibility. M2 shipped `agents/editor.md` as a single subagent file handling both `drafting` and `consolidated-draft` operating contexts via an `operating_context` flag; system prompt enumerates permitted edits per §4.4/§6.6 (lexicon swaps, §9 disallowed-pattern removal preserving meaning, tightening, cross-pillar harmonization in consolidated context) and prohibited edits (factual claims, evidence linkages, scientifically-weighted hedging, frontmatter); two-block output structure (`## EDITED COPY` + `## EDITORIAL REPORT`) parsed by the parent. M3 extended `/pilar:run-qc` to orchestrate Editor → apply edits → Fact-Checker per §8 sequencing (decision #3 — enforced in command logic, not hooks); discrete editorial commit at consolidated-draft context per §6.8; `--context drafting\|consolidated-draft` flag with drafting default. M4 refactored `scripts/context-audit.py` to a `QC_HARNESSES` registry pattern (one-entry append for the Strategic Reviewer at P8) and registered the Editor harness with its own allowlist (`{operating_context, artifact_id, artifact_path, lexicon_path, style_guide_path}`) and forbidden-token set. M5 shipped `examples/qc-fixtures/` as a self-contained QC test scenario (P-99 pillar fragment with deliberately-bad RS that exercises lexicon swap + §9 antithetical-pattern flag + overstatement-vs-source). User design decisions: `tools: [Read]` for both QC subagents (parent passes paths, subagent reads); single Editor file with `operating_context` flag rather than separate drafting / consolidated files. | P5 closure, §4.3, §4.4, §6.6, §8, §9, decisions #3 + #4 |
| 2026-05-02 | P5 design refinement: Editor uses surgical Edit-tool edits in place of the original full-body-reproduction pattern. | The original M2/M3 pattern had the Editor return a `## EDITED COPY` block (full reproduction of the artifact body) plus a `## EDITORIAL REPORT` block; the parent then wrote `frontmatter + edited body` back to the artifact file. User flagged this as lossy and error-prone — full-body retype risks silent drift; the parent's second full rewrite multiplies the failure surface. Replaced with surgical Edit-tool edits: `agents/editor.md` declares `tools: [Read, Edit]`, system prompt directs the subagent to use Edit per change with sufficient `old_string` context for uniqueness, and the file is in its post-edit state by the time the subagent returns. Editor's only output is now the editorial report (the `## EDITED COPY` block is removed). `commands/run-qc.md` simplified: parent uses `git diff` to inspect Editor's changes, with a sanity check that the editorial report's claimed edit count matches the diff (catches silently-failed Edit calls). `scripts/context-audit.py` per-harness `allowed_tools_sets` field — Fact-Checker constrained to `[set(), {"Read"}]`, Editor permitted `[{"Read"}, {"Read", "Edit"}]`. New `parse_tools_list` helper does proper YAML-list parsing rather than string normalization. Verified by deliberate fail injection: Editor with `[Read, Edit, Bash]` → caught; Fact-Checker with `[Read, Edit]` → caught; legacy `tools: []` (Fact-Checker P2 state) and `tools: [Read]` (Editor pre-refinement state) both still pass. Tradeoff: Editor's tool allowlist loosens — but the Independence Contract (what context the subagent *sees*) is unchanged. | P5 refinement, §4.4, §6.8, decision #3 |
| 2026-05-02 | Phase 6 (KB Librarian + registers) closed on the `phase-6` branch. **No release tag** per saved release-gating policy. | Five sub-milestones: M1 shipped `/pilar:ingest-kb` initial-intake mode (taxonomy proposal against `/pilar:init`'s five default subfolders, manifest entry proposal with always-user-confirmed citation/key_findings/population, validate-schemas gate before commit). M2 added the auto-detected incremental mode in the same command (new-file delta against existing manifest `file:` paths, append-only `REF-NNN` continuation per `docs/CONVENTIONS.md`, mode-specific user-facing commit messages — the M1 dev-milestone format `feat(p6-m1):` is no longer used at command runtime). M3 shipped `scripts/detect-gaps.py` reusing `parse_frontmatter` / `section_body` / `find_headings` / `heading_id` / `ID_PATTERNS` from `validate-schemas.py` via `importlib.util` (the source filename's hyphen prevents a normal `import`); detects three orphan classes (missing `sources:` line, empty list, unresolved REFs) with markdown and JSON output formats; exit code 0 even on orphans (the script detects, doesn't gate). New Step 12 of `/pilar:ingest-kb` invokes the scan after manifest commit lands, walks the user through Librarian-drafted `proposed_search:` per orphan (the single field a Python script cannot fill), and proposes a separate commit for the gap entries. M4 shipped `/pilar:add-aspirational` with full §7.7 walkthrough; the `evidence_generation_link` step reads `briefing.md`'s `## Evidence Generation Activities` section and presents bullets as numbered choices plus a literal `candidate input` option per the schema. M5 shipped `examples/p6-fixtures/` (3 synthetic markdown sources standing in for binary KB inputs per §3, post-ingest manifest with `REF-001..003`, P-99 orphan pillar exercising both structural detection paths, post-detect evidence-gaps with two GAP entries, one ASP entry, README documenting manual smoke tests). User design decisions: slash-command-driven Librarian with **no `agents/librarian.md` file** (the Librarian has no §4 independence contract per spec — the Primary Collaborator runs the workflow with full briefing/roadmap context); the orphan-RS predicate as a standalone script invokable both via the slash command and ad-hoc rather than buried in the command body; deferred unification of orphan-RS with Fact-Checker's "lacks support" finding to P8 — the predicates turned out to be structurally distinct (orphan-RS is manifest-resolution; FC "lacks support" is source-reading semantic evaluation), so the roadmap's original "implemented once" framing was an over-anticipation. | P6 closure, §4.2, §6.2, §6.3 (partial), §7.4, §7.6, §7.7, §10 |

