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

### Phase 2 — Walking skeleton (plugin packaging + subagent isolation + marketplace install path)

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

### Phase 3 — Schemas, defaults, registers, validator

**Scope.** All ten artifact templates from §7 with frontmatter and stable-ID conventions; §9 disallowed-pattern defaults seeded into the style guide; lexicon and the two registers (evidence gaps, aspirational statements) as empty-but-valid documents; a read-only schema validator that the plugin can run before commits to catch drift.

**Exit criteria.** Every schema in §7 has a template and validator coverage. Stable-ID conventions (`pillar-id.SS-id.RS-id`, `ref-id`, `gap-id`, `asp-id`) are documented and asserted by the validator so §11 translation has zero rework later.

**Risks.** Schema churn during later phases. Mitigation: validator + golden examples in `examples/`; any change requires an explicit migration note in the decisions log.

**Dependencies.** P2.

---

### Phase 4 — Sprint engine + Primary Collaborator core  *(briefing merged in)*

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

### Phase 5 — Editor and Fact-Checker subagents  *(independence contract codified)*

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

### Phase 6 — Knowledge Base Librarian + registers

**Scope.** KB intake (§6.2), manifest entry creation (§7.4), taxonomy proposal with user approval, gap detection on reference statements lacking sources, search-strategy proposal (§10), aspirational statement registration with evidence-generation linkage (§7.7).

Lands after P5 because gap detection and Fact-Checker's "lacks support" finding share an unsupported-RS predicate that should be implemented once.

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
| §3 | Project structure & git conventions | P2, P4 | `/pilar:init`, `/pilar:commit-checkpoint`, commit-message proposals | planned |
| §4.1 | Primary Collaborator | P4 | Plugin top-level prompt + slash commands | planned |
| §4.2 | KB Librarian | P6 | `agents/librarian.md` (or skill) + `/pilar:ingest-kb` | planned |
| §4.3 | Fact-Checker (independence) | P2 stub, P5 real | `agents/fact-checker.md` | planned |
| §4.4 | Editor (independence, two contexts) | P5 | `agents/editor.md` | planned |
| §4.5 | Strategic Reviewer (independence) | P8 | `agents/strategic-reviewer.md` | planned |
| §5.1 | Roadmap | P3 schema, P4 maintenance | `schemas/roadmap.md`, `/pilar:sprint-close` updates roadmap | planned |
| §5.2 | Sprint plan | P3 schema, P4 logic | `schemas/sprint-plan.md`, `/pilar:sprint-plan`, `/pilar:sprint-amend` | planned |
| §5.3 | Sprint-end checkpoint (4 options) | P4 | `/pilar:sprint-close` state machine (Appendix B) | planned |
| §5.4 | Session resumption | P4 | Session-start orientation in plugin top-level prompt | planned |
| §6.1 | Briefing & scoping | P4 | Briefing as canonical first sprint | planned |
| §6.2 | KB initial intake | P6 | `/pilar:ingest-kb` | planned |
| §6.3 | Initial evidence synthesis | P6 / P7 | Primary Collaborator workflow before scaffolding | planned |
| §6.4 | Scaffolding recommendation | P7 | `/pilar:scaffold-pillars` | planned |
| §6.5 | Per-pillar development | P7 | `/pilar:pillar-narrative`, `/pilar:pillar-statements` | planned |
| §6.6 | Lexicon & style guide | P3 defaults, P5 enforce, P7 accumulate | `schemas/lexicon.md`, `schemas/style-guide.md`, Editor subagent | planned |
| §6.7 | Consolidation | P8 | `/pilar:consolidate` | planned |
| §6.8 | Whole-deliverable review | P8 | `/pilar:run-qc --consolidated`, discrete editorial commit | planned |
| §6.9 | Handoff | P8 / P9 | `/pilar:handoff` (tag + roadmap update) | planned |
| §7.1 | Roadmap schema | P2 stub, P3 full | `schemas/roadmap.md` | planned |
| §7.2 | Briefing schema | P3 | `schemas/briefing.md` | planned |
| §7.3 | Sprint plan & summary schemas | P3 | `schemas/sprint-plan.md`, `schemas/sprint-summary.md` | planned |
| §7.4 | KB manifest schema | P3 | `schemas/kb-manifest.md` | planned |
| §7.5 | Pillar file schema | P3 | `schemas/pillar.md` | planned |
| §7.6 | Evidence gaps register schema | P3 | `schemas/evidence-gaps.md` | planned |
| §7.7 | Aspirational statements register schema | P3 | `schemas/aspirational-statements.md` | planned |
| §7.8 | Lexicon schema | P3 | `schemas/lexicon.md` | planned |
| §7.9 | Style guide schema | P3 | `schemas/style-guide.md` | planned |
| §7.10 | QC report schemas (3) | P3 | `schemas/{fact-check,editorial,strategic-alignment}-report.md` | planned |
| §8 | QC rules (independence, sequencing) | P5, P8 | `/pilar:run-qc` command logic | planned |
| §9 | Writing style requirements | P3 defaults, P5 enforce | Style-guide template + Editor subagent | planned |
| §10 | Evidence enlargement protocol | P6 | Librarian gap detection + search-strategy proposal | planned |
| §11 | Output translation | out-of-scope | Schemas designed for future translation; stable IDs asserted in P3 | out-of-scope |
| §12 | Tooling and artifact layering | P2, throughout | Engagement-level vs Claude Code task-level separation enforced by directory layout and command behavior | planned |
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

