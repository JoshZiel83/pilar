# Changelog

All notable changes to pilar are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Per the project's load-bearing decision #5 (recorded in [`IMPLEMENTATION_ROADMAP.md`](./IMPLEMENTATION_ROADMAP.md)), explicit `version` is set in `.claude-plugin/plugin.json` only on tagged releases; the field is omitted between releases so the commit SHA serves as the version during active development.

## [Unreleased]

Phase 4 closed: sprint engine + Primary Collaborator core. Not yet tagged — release tagging is user-gated.

### Added

- `/pilar:sprint-plan` — opens a new sprint by drafting a plan from roadmap state and the prior sprint summary. Sprint-1 special case for briefing has pre-populated objectives. Writes `sprints/sprint-NN/plan.md`, updates roadmap (`current_sprint`, Active Workstreams), proposes commit message inline, waits for user approval. (commands/sprint-plan.md)
- `/pilar:sprint-close` — closes the active sprint at the §5.3 checkpoint. Drafts the summary from work actually completed, presents at the checkpoint, executes the four-option state machine (Confirm / Request revisions [bounded or substantive] / Defer / Rewind) with branch-specific roadmap updates. Each terminal branch proposes its own commit message inline. (commands/sprint-close.md)
- `/pilar:sprint-amend` — handles in-flight plan revisions per §5.2 ("an amended plan is proposed by the Primary Collaborator, approved by the user, and committed before further work proceeds"). Captures the delta in an `## Amendments` section appended to the plan. (commands/sprint-amend.md)
- `/pilar:init` extended to seed the full set of engagement-artifact stubs whose schemas now exist: `briefing.md`, `style-guide.md` (with the §9 disallowed-pattern defaults inherited verbatim from the schema), `lexicon.md`, `knowledge-base/manifest.md`, `registers/evidence-gaps.md`, `registers/aspirational-statements.md` — alongside the existing `roadmap.md` seeding. All seeded stubs validate clean against `scripts/validate-schemas.py`.
- A static `CLAUDE.md` template dropped at the engagement repo root by `/pilar:init`. Triggers session resumption (§5.4) on every Claude Code session start in the engagement directory: read roadmap → most recent sprint summary → active sprint plan → orient the user briefly → defer to user before offering work. Lists available `/pilar:*` slash commands.

## [0.1.0] — 2026-05-02

First user-facing release. Locks the §7 artifact contract and §9 style defaults; establishes stable-ID conventions and validator enforcement.

### Added

- Full §7 schema coverage (13 schemas total): roadmap, briefing, sprint-plan, sprint-summary, kb-manifest, pillar, evidence-gaps, aspirational-statements, lexicon, style-guide, and the three QC reports (fact-check, editorial, strategic-alignment).
- §9 disallowed-pattern defaults baked into `schemas/style-guide.md`: em dashes for rhythm, antithetical "not X, it is Y" constructions, sentence-initial conjunctions, short punchy sentences for emphasis, hedging without scientific reason, marketing-register adjectives, first-person plural framing, rhetorical questions. Engagements inherit these defaults; clients can override per-pattern via the documented Overrides subsection.
- Stable-ID conventions (`REF-NNN`, `P-NN`, `SS-NN`, `RS-NN`, `GAP-NNN`, `ASP-NNN`, `FC-<sprint>-NNN`, `ED-<sprint>-NNN`, `CL-NNN`, `SA-<draft-tag>-NNN`) documented in [`docs/CONVENTIONS.md`](./docs/CONVENTIONS.md), with composite references like `P-NN.SS-NN.RS-NN` for cross-artifact linking.
- Schema validator (`scripts/validate-schemas.py`) extended with: per-artifact ID-format checks, uniqueness within document scope, nested SS/RS validation for pillar files, composite-reference validation for `linked_to` and `linked_statement` fields, and `sources: [REF-NNN, ...]` reference-format validation. Activated as the `schema-validate` CI job on every PR/push.
- Golden fixtures for all 13 schemas (`examples/fixtures/`) populated from the Aurelis Therapeutics / ALR-217 / r/r DLBCL synthetic engagement scenario defined in Appendix C of `IMPLEMENTATION_ROADMAP.md`.

### Pre-release context

The development arc to v0.1.0:

- **P1** (2026-05-01): Implementation roadmap committed; `LICENSE` (MIT, © 2026 Clinton Avenue BioPharma Partners, LLC), `.gitignore`, and natural-language spec published. Repo public at https://github.com/JoshZiel83/pilar.
- **P2** (2026-05-02): Walking skeleton end-to-end. `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for marketplace install; `/pilar:init` scaffolds an engagement directory tree per §3 of the spec; stub Fact-Checker subagent (`agents/fact-checker.md` with `tools: []`) demonstrates the §4/§8 Independence Contract; `/pilar:run-qc` parent harness with sentinel-bounded prompt template; static `scripts/context-audit.py` gates the harness against regression in CI.
- **P3** (2026-05-02): full schema contract + validator + first user-facing release. (This release.)

What pilar does NOT yet do at v0.1.0: real fact-checking (P5), real editorial enforcement (P5), KB ingestion (P6), pillar drafting workflow (P7), consolidation and strategic review (P8). The v1.0.0 cutover happens at P9 close per the implementation roadmap.

[0.1.0]: https://github.com/JoshZiel83/pilar/releases/tag/v0.1.0
[Unreleased]: https://github.com/JoshZiel83/pilar/compare/v0.1.0...HEAD
