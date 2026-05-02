# Changelog

All notable changes to pilar are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Per the project's load-bearing decision #5 (recorded in [`IMPLEMENTATION_ROADMAP.md`](./IMPLEMENTATION_ROADMAP.md)), explicit `version` is set in `.claude-plugin/plugin.json` only on tagged releases; the field is omitted between releases so the commit SHA serves as the version during active development.

## [Unreleased]

(no changes yet)

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
