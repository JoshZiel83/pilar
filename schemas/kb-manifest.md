---
artifact: kb-manifest
project: <project-id>
updated: <iso-date>
---

# Knowledge Base Manifest

## Entries

<!-- ref-id grammar: property-based (e.g. `Smith_J_2024_Synth-J-Med`). See docs/CONVENTIONS.md §"KB manifest reference IDs" for the recommended shapes (journal article / congress abstract / guideline / pre-print) and the disambiguation rule. -->

### <ref-id>

- file: <path>
- citation: <full citation>
- type: <study type — e.g. RCT, single-arm trial, real-world evidence, guideline, review, congress abstract, mechanism-of-action paper, pubmed-abstract, clinicaltrials-registration>
- design: <design notes>
- population: <population>
- key_findings: <summary>
- tags: <list>
- status: <provisional | confirmed — optional; absent means confirmed. `provisional` indicates the source file is metadata-only (e.g. PubMed abstract, ClinicalTrials.gov registration) captured by `/pilar:research`, awaiting upgrade when full text/source is acquired>
- ingested: <iso-date>
