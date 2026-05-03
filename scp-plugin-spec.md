# Scientific Communication Platform Plugin

## Natural Language Specification

---

## 1. Purpose

This plugin enables a medical writer to collaborate with Claude Code to build a Scientific Communication Platform (SCP) for a pharmaceutical or biotech client. The plugin is not a generator. It is a structured collaborator that drives a multi-session, multi-sprint process from briefing through pillar development, holding strategic priorities and evidence support in continuous tension and producing a versioned, schema-conformant set of markdown artifacts that can be translated downstream to a normalized database, an Excel workbook, or a Word document.

The plugin is designed for the realities of platform development. Evidence is not fully available at the start. Strategic priorities are client-specific and must be captured before scaffolding is proposed. Every meaningful step requires human review. Quality control is performed independently of the drafting agent. The deliverable evolves across many sessions and the project state is maintained in a way that any session can resume coherently from the prior one.

## 2. Primary User

The primary user is a medical writer working at a medical communications agency. The writer is scientifically literate, familiar with evidence hierarchies and publication conventions, and accustomed to iterative drafting and client review cycles. The plugin's interaction style assumes this background. It does not over-explain platform conventions, evidence levels, or domain terminology. It does explain its own reasoning, its proposed scaffolding choices, and the evidentiary basis for any draft language it produces.

## 3. Project Structure and Git Conventions

Each engagement is a git repository. The repository is the canonical project state. The roadmap markdown file is the source of truth for where the engagement stands. All artifacts are markdown. Binary inputs in the knowledge base are committed as-is. The plugin proposes a starting directory structure and works with the user to refine it as the project evolves.

A typical starting structure:

```
/roadmap.md
/briefing.md
/style-guide.md
/lexicon.md
/knowledge-base/
  /manifest.md
  /clinical/
  /preclinical/
  /guidelines/
  /competitor/
  /other/
/pillars/
  /pillar-01-<slug>/
    /pillar.md
    /evidence-map.md
    /progress.md
/registers/
  /evidence-gaps.md
  /aspirational-statements.md
/qc/
  /fact-check-reports/
  /editorial-reports/
  /strategic-alignment-reports/
/sprints/
  /sprint-01/
    /plan.md
    /summary.md
  /sprint-02/
    /plan.md
    /summary.md
```

The plugin proposes additions, renames, and reorganizations as the project grows. It does not impose structure. It proposes structure and the user approves.

Commits are made at meaningful checkpoints. At minimum: end of each sprint, after each pillar approval, after each QC pass, and after any roadmap amendment. Commit messages reference the sprint number and the artifact affected. The plugin proposes commit messages and the user approves them.

## 4. Agent Roles

The plugin operates through four roles. Three of these roles are capabilities. The implementation may realize them as subagents, as functions of the primary agent, or in any other configuration that serves the user. The roles are described here as conceptual responsibilities.

The two QC roles are different. They must operate independently of the primary interactive agent. Their evaluation must not be conditioned on the drafting context, the user's stated preferences during drafting, or any rationale the primary agent used to produce the copy under review. This independence is a hard requirement of the spec.

### 4.1 Primary Collaborator

Drives the engagement. Conducts briefing and scoping. Maintains and updates the roadmap. Proposes the pillar set. Drafts language with the user. Manages handoffs between stages. Surfaces decisions for human review. Records sprint outcomes.

### 4.2 Knowledge Base Librarian

Ingests new files added to the knowledge base. Maintains the manifest, which catalogs each file with citation, study type, key findings, and tags. Surfaces gaps when reference statements lack support. Proposes search strategies, candidate source types, and specific queries when the user is enlarging the evidence base. Ingests what the user retrieves and updates the manifest.

### 4.3 Fact-Checker

Operates independently of the Primary Collaborator. Verifies each reference statement against its cited source files. Flags reference statements that lack sources, that overstate what their sources support, that misattribute findings, or that rely on sources of insufficient strength for the claim being made. Produces a fact-check report at each QC pass. Does not edit. Reports findings.

### 4.4 Editor

Operates independently of the Primary Collaborator. The Editor's behavior depends on the operating context.

At drafting checkpoints (per-pillar narrative, scientific statement, reference statement) the Editor edits copy for style and lexicon within the constraint of preserving meaning. Permitted edits include swapping terms to lexicon-preferred forms, restructuring sentences to comply with the style guide, removing disallowed rhythmic and stylistic patterns characteristic of LLM output, and tightening construction. Prohibited from changing factual claims, evidence linkages, source attributions, scientific argument structure, scientifically-weighted hedging that reflects evidence uncertainty, and the strategic argument of any scientific statement. Where applying a style or lexicon edit would require changing meaning, the Editor refrains from editing and flags the item for the human reviewer. The Editor produces edited copy and a list of items flagged but not edited; a detailed change log is not required at this stage because the human reviewer is reviewing the copy fresh.

At consolidated-draft checkpoints the Editor reads the consolidated draft and reports findings; it does not edit. Findings include cross-pillar terminology drift, lexicon adherence drift across pillars, claim duplication or contradiction across pillars, and any consistency observation that cuts across pillar boundaries. The Editor produces a list of flagged items only; it does not produce a change log because no changes are applied. Findings are addressed by the writer editing the source pillars and re-consolidating; the consolidated draft itself is a deterministic assembly of the source pillars and is not edited directly. This preserves the source pillars as the canonical state of the engagement and prevents the consolidated draft from drifting from the pillars across re-consolidation cycles.

### 4.5 Strategic Reviewer

Operates independently of the Primary Collaborator. Engages at the consolidated-draft stage. Reads the briefing, the roadmap, and the consolidated platform draft. Evaluates whether the deliverable as a whole reflects the strategic priorities captured in the briefing, whether each pillar advances those priorities, whether the balance of emphasis across pillars is appropriate to the client's strategic intent, and whether any priority is unaddressed or under-addressed. Produces a strategic alignment report. Does not edit. Reports findings.

## 5. The Roadmap and the Sprint Model

### 5.1 The Roadmap

The roadmap markdown file functions as a product roadmap for the engagement. It is created during briefing and scoping and is the canonical reference document for the project. It is updated at the close of each sprint to reflect what was completed, what decisions were made, what is in progress, what is blocked, and what is in scope for the next sprint.

### 5.2 The Sprint Plan

A sprint is a unit of work bounded by user availability and a defined set of objectives. A sprint may span multiple sessions or fit inside a single session. The sprint plan is drafted by the Primary Collaborator at the start of the sprint, working from the next-sprint scope recorded in the roadmap. The plan articulates the sprint's objectives, the artifacts that will be created or modified, the QC roles that will run and the artifacts they will run on, and the expected outputs.

The user reviews and approves the plan. The approved plan is committed before sprint execution begins. Execution may use Claude Code's native task-level tooling, including plan files and todo lists, as ephemeral working scaffolding (see Section 12).

If during execution the user determines the plan is incomplete or needs to change, an amended plan is proposed by the Primary Collaborator, approved by the user, and committed before further work proceeds.

### 5.3 The Sprint-End Checkpoint

Every sprint closes with the same checkpoint pattern. The Primary Collaborator produces the sprint summary as a structured report covering the objectives as planned, the work actually completed, the files altered, the QC roles that ran with their findings, the artifacts that require user review, and any open items. The summary is presented to the user.

The user responds with one of four options:

- Confirm. The sprint closes. The summary is amended with the response, committed, and the roadmap is updated. The next sprint is planned.
- Request revisions. The user provides feedback. If the additional work is bounded, the sprint plan is amended and execution continues. If the work is substantive, the items are recorded and the next sprint takes them up.
- Defer. The work is parked pending external input such as evidence enlargement or a client decision. Deferred items are recorded in open items.
- Rewind. The user determines that earlier-approved work needs to be reopened. A new sprint is planned with that scope. The reopening is recorded in the roadmap decisions log.

The user's response is recorded in the sprint summary's frontmatter and Human Response section, and the summary is committed.

The checkpoint is the gate between sprints. The variation that matters across checkpoints lives in what the sprint did and which QC roles ran. The mechanics are the same. A briefing sprint, a pillar-drafting sprint, and a consolidated-draft sprint all close with this pattern. Their reports differ in content because their plans differed in content. Strategic Reviewer engagement is conditional on sprint type and engages only when the sprint produces or revises a consolidated draft.

### 5.4 Session Resumption

At the start of each session, the Primary Collaborator reads the roadmap, the most recent sprint summary, and the active sprint plan if one is in progress, and orients the user to current state before any work resumes.

## 6. The Staged Process

The process is directional rather than prescriptive. The default sequence is described below. Stages may be revisited as evidence and strategic understanding evolve. Movement between stages is recorded in the roadmap and requires explicit user confirmation.

### 6.1 Briefing and Scoping

The Primary Collaborator interviews the user to capture the engagement context. This includes the product, the indication, the lifecycle stage, the audiences, the client's strategic priorities, the competitive context, known constraints, any client-supplied style guide or lexicon, any planned or in-flight evidence generation activities, and the working timeline. The output is the briefing markdown file and the initial roadmap.

If the client has not supplied a style guide or lexicon, this is recorded as a strategic recommendation to be developed during the engagement.

### 6.2 Knowledge Base Initial Intake

The Librarian processes whatever files the user has placed in the knowledge base. The manifest is created. Files are categorized into the proposed subfolders, with the user approving the taxonomy. The user is asked what additional materials are expected, and these are noted in the roadmap as anticipated inputs.

### 6.3 Initial Evidence Synthesis

The Primary Collaborator, working from the manifest and the briefing, produces a high-level synthesis of what the current evidence base can support. The synthesis is not a draft of the platform. It is a structured assessment of what is known, what is suggested, and what is absent, organized in a way that informs scaffolding.

### 6.4 Scaffolding Recommendation

The Primary Collaborator proposes a pillar set. The default pattern includes unmet need, disease mechanism and pathophysiology, mechanism of action, clinical evidence, and clinical value framework. The proposed set is adjusted to the client's strategic priorities and the indication. For each proposed pillar, the recommendation includes a short rationale tied to strategic priorities and a preliminary view of evidentiary support based on the synthesis.

The proposed scaffolding is reviewed by the user via the sprint-end checkpoint described in Section 5.3. The pillar set is finalized when the user confirms it.

### 6.5 Per-Pillar Development

Once the pillar set is approved, the project enters per-pillar development. This transition is recorded in the roadmap. Each pillar is developed as an abstracted work track with its own files and its own progress notes. Pillars may be worked sequentially or in any order the user chooses. They share common dependencies: the briefing, the roadmap, the lexicon, the style guide, and the knowledge base.

For each pillar, development typically proceeds as follows.

The Primary Collaborator drafts a pillar narrative. This narrative articulates the strategic argument the pillar makes and the territory it covers. The Editor runs on the drafted narrative, applying permitted edits and producing a list of items flagged but not edited.

Following narrative approval, the Primary Collaborator drafts scientific statements that operationalize the pillar argument. Each scientific statement is a synthesis that makes a strategically relevant claim. For each scientific statement, the Primary Collaborator drafts the supporting reference statements. Each reference statement is a granular factual summary of a specific evidence element. Each reference statement is linked to one or more references in the knowledge base.

The Editor runs on the drafted scientific and reference statements, applying permitted edits and producing a list of items flagged but not edited. The Fact-Checker runs on the edited copy and produces its report.

How this work is partitioned across sprints is a sprint-sizing decision. A user who wants to review the narrative before any statements are drafted runs a narrative sprint and then one or more statement sprints. A user comfortable batching reviews runs a single sprint covering both. Each sprint closes with the sprint-end checkpoint described in Section 5.3.

Where reference statements lack adequate support, the Librarian flags the gap, articulates the kind of evidence that would close it, and proposes how to find it. Gaps are recorded in the evidence gaps register. The user closes gaps by retrieving evidence and adding it to the knowledge base, where it is ingested and the affected reference statements are revisited.

Where a strategically important claim cannot be supported by current or retrievable evidence, the user may designate it as an aspirational statement. The plugin minimizes aspirational statements by default. Each aspirational statement must either link to an existing evidence generation plan or be flagged as a candidate input to such a plan. Aspirational statements are recorded in the aspirational statements register with structured metadata.

### 6.6 Lexicon and Style Guide Development

If the client has supplied a lexicon and style guide, they are loaded during briefing and enforced by the Editor throughout. If not, lexicon entries are accumulated as drafting proceeds and the style guide is developed in parallel. Both are presented as strategic recommendations to the client.

### 6.7 Consolidation

The platform package is assembled into a consolidated draft by deterministic mechanical concatenation of the source artifacts: the briefing, the pillar set with their narratives and statements, the lexicon, and the style guide. Consolidation does not interpret, rewrite, or summarize; it produces a single coherent deliverable view that is byte-determined by the inputs. The consolidated draft is therefore a derived artifact, not an authored one, and the source pillars remain the canonical state of the engagement.

Consolidation may occur more than once during the engagement: an initial consolidated draft is produced at the close of per-pillar development, and additional consolidated drafts are produced after client feedback rounds or after whole-deliverable review surfaces findings that require pillar revision.

### 6.8 Whole-Deliverable Review

Every consolidated draft is subjected to a whole-deliverable review before it is considered ready for client delivery or for sign-off. The QC roles operate independently of the Primary Collaborator. All three roles are read-only at this stage: they report findings against the consolidated draft and do not modify it. Because consolidation is deterministic (§6.7), all corrective edits land in the source pillars (or other source artifacts) and are propagated to the deliverable by the next consolidation. This preserves the source pillars as the canonical state of the engagement.

The Editor reads the consolidated draft and reports cross-pillar findings: terminology consistency, narrative cohesion across pillars, claim duplication or contradiction, internal consistency within each pillar at the level of the consolidated artifact, and lexicon adherence across the deliverable, including drift in preferred terms across pillars and any new terms introduced during pillar development. The Editor produces a list of flagged items only; it does not produce a change log because no changes are applied at this stage.

The Fact-Checker runs on the consolidated draft and produces its report.

The Strategic Reviewer reads the briefing, the roadmap, and the consolidated draft. It evaluates whether the consolidated draft reflects the strategic priorities captured in the briefing, whether each pillar advances those priorities, whether the balance of emphasis is appropriate to the client's strategic intent, and whether any priority is unaddressed or under-addressed. It produces the strategic alignment report.

The three reports (editorial flagged items, fact-check, strategic alignment) are presented to the user. The Primary Collaborator addresses findings in collaboration with the user. Findings are resolved by editing the affected source artifacts — typically the affected pillars — and re-consolidating the deliverable. The whole-deliverable review is then re-run on the new consolidated draft. This loop continues until the consolidated draft clears review.

### 6.9 Handoff

Once a consolidated draft has cleared the whole-deliverable review and any required client review, the Primary Collaborator finalizes the platform package. The roadmap is updated to reflect completion. The final state is committed and tagged.

Client review itself is part of the engagement workflow. Claude Code's involvement pauses while the writer takes the consolidated draft to the client. Client feedback intake resumes Claude Code involvement: a new sprint is planned to address the feedback, typically reopening affected pillars, revising statements, re-consolidating the deliverable, and re-running whole-deliverable QC. Each such sprint closes with the standard sprint-end checkpoint.

## 7. Markdown Schema

The schema below is proposed. Frontmatter uses YAML. Section headings are fixed where indicated. Cross-references between artifacts use stable identifiers so that translation to a normalized database is unambiguous.

### 7.1 Roadmap

```
---
artifact: roadmap
project: <project-id>
client: <client>
product: <product>
indication: <indication>
lifecycle_stage: <stage>
created: <iso-date>
updated: <iso-date>
current_sprint: <n>
---

# Roadmap

## Engagement Summary
<brief>

## Strategic Priorities
<list>

## Status
<stage and progress>

## Pillars
<table or list with pillar id, slug, status>

## Active Workstreams
<list>

## Anticipated Inputs
<list>

## Sprint History
<list of completed sprints with links>

## Next Sprint Scope
<list>

## Decisions Log
<append-only list of significant decisions with date and rationale>
```

### 7.2 Briefing

```
---
artifact: briefing
project: <project-id>
created: <iso-date>
updated: <iso-date>
---

# Briefing

## Product
## Indication
## Lifecycle Stage
## Audiences
## Strategic Priorities
## Competitive Context
## Constraints
## Client Style Guide
## Client Lexicon
## Evidence Generation Activities
## Timeline
## Notes
```

### 7.3 Sprint Plan and Sprint Summary

Each sprint produces two committed artifacts: a plan at the start and a summary at the close. The summary functions as the structured report presented to the user at the sprint-end checkpoint and is amended with the user's response before being recommitted to close the sprint.

```
---
artifact: sprint-plan
sprint: <n>
project: <project-id>
opened: <iso-date>
approved: <iso-date>
---

# Sprint <n> Plan

## Objectives
## Artifacts to Create or Modify
## QC Roles to Run
<which of Editor, Fact-Checker, Strategic Reviewer will run, and on which artifacts>
## Expected Outputs
## Notes
```

```
---
artifact: sprint-summary
sprint: <n>
project: <project-id>
opened: <iso-date>
closed: <iso-date>
human_response: <pending|confirmed|revisions-requested|deferred|rewind>
---

# Sprint <n> Summary

## Objectives as Planned
## Work Completed
## Files Altered
## QC Roles Run and Findings
## Artifacts to Review
## Decisions
## Open Items
## Human Response
<populated when the user responds at the checkpoint; includes the response category and any feedback>
## Next Sprint Proposed Scope
```

### 7.4 Knowledge Base Manifest

```
---
artifact: kb-manifest
project: <project-id>
updated: <iso-date>
---

# Knowledge Base Manifest

## Entries

### <ref-id>
- file: <path>
- citation: <full citation>
- type: <study type>
- design: <design notes>
- population: <population>
- key_findings: <summary>
- tags: <list>
- ingested: <iso-date>
```

Each entry has a stable `ref-id` that is referenced from reference statements.

### 7.5 Pillar File

The pillar file holds the full content of a pillar in a single document: the strategic rationale, the narrative, the scope, all scientific statements with their reference statements, and pillar-level open items. Stable identifiers are preserved at every level so that translation to a normalized database, an Excel workbook, or a Word document remains unambiguous.

```
---
artifact: pillar
pillar_id: <pillar-id>
project: <project-id>
slug: <slug>
status: <draft|narrative-approved|statements-approved|complete>
created: <iso-date>
updated: <iso-date>
---

# Pillar: <name>

## Strategic Rationale
<text>

## Narrative
<text>

## Scope
<text>

## Scientific Statements

### SS-<id>: <short title>
- status: <draft|approved|aspirational>
- created: <iso-date>
- updated: <iso-date>

**Statement.** <single paragraph, dry scientific tone>

**Strategic Argument.** <why this statement matters to the pillar>

**Reference Statements.**

#### RS-<id>: <short title>
- status: <draft|approved|gap|aspirational>
- sources: <list of ref-ids from the manifest>
- created: <iso-date>
- updated: <iso-date>

<reference statement text, factual, dry>

#### RS-<id>: <short title>
<as above>

### SS-<id>: <short title>
<as above>

## Open Items
<list>
```

Identifiers follow a stable convention. `pillar-id` is unique within the project. `SS-<id>` is unique within the pillar. `RS-<id>` is unique within the scientific statement. The full path of a reference statement in the database is therefore `<pillar-id>.<ss-id>.<rs-id>`.

### 7.6 Evidence Gaps Register

```
---
artifact: evidence-gaps
project: <project-id>
updated: <iso-date>
---

# Evidence Gaps

## Open Gaps

### <gap-id>
- linked_to: <rs-id or ss-id>
- description: <what is missing>
- evidence_type_needed: <what would close it>
- proposed_search: <strategy>
- status: <open|in-progress|closed>
- opened: <iso-date>
- closed: <iso-date>

## Closed Gaps
<archive>
```

### 7.7 Aspirational Statements Register

```
---
artifact: aspirational-statements
project: <project-id>
updated: <iso-date>
---

# Aspirational Statements

### <asp-id>
- linked_statement: <ss-id or rs-id>
- claim: <text>
- rationale: <strategic reason>
- evidence_generation_link: <plan-id or "candidate input">
- expected_readout: <date or "tbd">
- fallback_position: <text>
- status: <active|retired>
```

### 7.8 Lexicon

```
---
artifact: lexicon
project: <project-id>
source: <client-supplied|developed>
updated: <iso-date>
---

# Lexicon

### <term>
- preferred: <preferred term>
- avoid: <list of disallowed alternatives>
- definition: <text>
- rationale: <text>
```

### 7.9 Style Guide

```
---
artifact: style-guide
project: <project-id>
source: <client-supplied|developed>
updated: <iso-date>
---

# Style Guide

## Voice and Tone
## Sentence Construction
## Disallowed Patterns
## Citation Conventions
## Evidence Description Conventions
## Other
```

### 7.10 QC Reports

```
---
artifact: fact-check-report
sprint: <n>
project: <project-id>
created: <iso-date>
---

# Fact-Check Report

## Scope
## Findings

### <finding-id>
- target: <pillar-id.ss-id.rs-id or pillar-id.ss-id>
- issue: <description>
- severity: <high|medium|low>
- recommendation: <text>
```

```
---
artifact: editorial-report
context: <drafting|consolidated-draft>
sprint: <n>
project: <project-id>
created: <iso-date>
---

# Editorial Report

## Scope
<what was reviewed>

## Edits Applied Summary
<at drafting context: count and category breakdown of edits applied. At consolidated-draft context: "0 edits applied (read-only review per §6.8)." since the Editor does not edit the consolidated draft.>

## Items Flagged But Not Edited

### <finding-id>
- target: <pillar-id, pillar-id.ss-id, or pillar-id.ss-id.rs-id>
- category: <tone|lexicon|style|consistency|cross-pillar>
- issue: <description>
- proposed_change: <what would resolve it>
- reason_not_edited: <at drafting context: why this would change meaning. At consolidated-draft context: "n/a — Editor is read-only at consolidated stage; addressed by editing source pillars per §6.8.">
- severity: <high|medium|low>
```

```
---
artifact: strategic-alignment-report
consolidated_draft: <draft-id>
project: <project-id>
created: <iso-date>
---

# Strategic Alignment Report

## Scope
## Briefing Priorities Reviewed
## Findings

### <finding-id>
- target: <pillar-id, pillar-id.ss-id, or "deliverable">
- priority_affected: <briefing priority reference>
- issue: <description>
- severity: <high|medium|low>
- recommendation: <text>
```

## 8. QC Rules

QC roles run as specified by the sprint plan and on demand. The plan identifies which of the Editor, Fact-Checker, and Strategic Reviewer will run, and on which artifacts. The Strategic Reviewer engages only on sprints that produce or revise a consolidated draft.

The Fact-Checker reads only the artifacts under review and the cited source files. It does not read the briefing, the roadmap, or any drafting context that might bias its evaluation. It evaluates whether each reference statement is supported by the sources cited, whether the source strength is appropriate to the claim, and whether scientific statements are supportable as syntheses of their reference statements.

The Editor reads the artifacts under review, the lexicon, and the style guide. It does not read the drafting rationale. At drafting checkpoints the Editor edits copy for style and lexicon within the constraint of preserving meaning, evidence linkages, source attributions, scientific argument structure, and scientifically-weighted hedging; where an edit would change meaning, the Editor flags the item rather than editing it. At consolidated-draft checkpoints the Editor is read-only: it reports cross-pillar findings (terminology drift, lexicon adherence, claim duplication or contradiction, internal consistency at the consolidated level) but does not edit the consolidated draft. Findings at consolidated-draft checkpoints are addressed by editing the source pillars and re-consolidating per §6.7 and §6.8.

The Editor runs before the Fact-Checker so that at drafting checkpoints the Fact-Checker reviews the edited copy; this sequencing also serves as a safety net for drafting-context edits. At consolidated-draft checkpoints the sequencing is preserved (Editor first, then Fact-Checker, then Strategic Reviewer) as a matter of report-ordering convention rather than dependency, since the Editor's read-only consolidated pass does not modify the artifact.

The Strategic Reviewer reads the briefing, the roadmap, and the edited consolidated draft. It does not read the drafting rationale. It evaluates whether the consolidated draft reflects the strategic priorities captured in the briefing, whether each pillar advances those priorities, whether the balance of emphasis is appropriate to the client's strategic intent, and whether any priority is unaddressed or under-addressed.

All three roles produce reports that the user reviews at the sprint-end checkpoint. The Primary Collaborator addresses findings in collaboration with the user and re-runs QC as needed.

## 9. Writing Style Requirements

All drafted copy uses a dry scientific register. The following are disallowed by default and flagged by the Editor:

- Em dashes used for rhythmic effect
- Antithetical constructions of the form "it is not X, it is Y"
- Sentence-initial conjunctions used for rhetorical pacing
- Short punchy sentences used for emphasis
- Hedging phrases that soften factual claims without scientific reason
- Marketing-register adjectives
- First-person plural framing of the science
- Rhetorical questions

The Editor enforces these defaults. The user may override specific items in the style guide if the client requests a different register.

## 10. Evidence Enlargement Protocol

When the Librarian identifies a gap, it produces a gap entry that names what is unsupported, articulates the kind of evidence that would close the gap, and proposes how to find it. Proposals may include search strategies, candidate source types, specific PubMed query constructions, congress abstract sources, guidelines bodies, or known authors in the area.

The user retrieves evidence and places it in the knowledge base. The Librarian ingests, updates the manifest, and notifies the Primary Collaborator that affected reference statements should be revisited. The Primary Collaborator updates the affected statements with the user and the gap is closed in the register.

## 11. Output Translation

All artifacts are markdown with structured frontmatter and stable identifiers. The schema is designed to support translation to:

- A normalized database, where each artifact type maps to a table and identifiers serve as foreign keys
- An Excel workbook, where each artifact type maps to a sheet
- A Word document, assembled from the briefing, pillar narratives, scientific and reference statements, lexicon, and style guide

Translation is out of scope for this spec but the schema is designed to support it without rework.

## 12. Claude Code Tooling and Artifact Layering

The spec is written at the level of behavior, artifacts, and interaction contracts. It does not preclude or constrain the use of Claude Code's native task-level tooling. Plan files, todo lists, file inspection, bash, git operations, and subagent invocation are expected and complementary capabilities that the implementation uses as needed.

Two layers of artifacts coexist in the project. They serve different purposes and have different lifetimes.

Engagement-level artifacts are persistent and committed to git. They represent the durable state of the engagement and are referenced across sessions. They include the roadmap, briefing, sprint plans and summaries, pillar files, lexicon, style guide, evidence gaps register, aspirational statements register, and QC reports. Their schema is defined in Section 7. Their lifecycle is governed by the staged process in Section 6.

Task-level execution artifacts are the working scaffolding Claude Code uses to organize its execution within a sprint. These include native plan files, todo lists, scratch notes, and any other transient artifacts Claude Code's tooling produces. They are ephemeral. They are not required to follow the engagement schema. They need not persist beyond the sprint they served. The implementation may create, update, and discard them freely without reference to the engagement-level workflow.

The sprint plan defined in Section 5 is engagement-level and persistent. It is the user's instrument for approving sprint scope before execution begins. Once the sprint plan is approved and committed, Claude Code may use any of its native task-level tooling to execute against it. The sprint plan and the task-level execution artifacts are not substitutes for one another. They operate at different layers and serve different audiences. The sprint plan is the contract between the user and the Primary Collaborator. The task-level execution artifacts are Claude Code's internal working method.

## 13. Out of Scope

This spec describes behavior, artifacts, and interaction contracts. It does not specify model selection, prompt internals, tool plumbing, or implementation details of how subagents are realized. It does not specify the translation utilities for converting markdown to database, Excel, or Word. It does not prescribe a specific git workflow beyond the commit checkpoints described in Section 3.
