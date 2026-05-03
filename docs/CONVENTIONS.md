# pilar Stable-ID Conventions

> Stable identifiers are how every pilar artifact references every other artifact. They are the load-bearing primitive that lets the schemas in §7 of `scp-plugin-spec.md` translate cleanly to a normalized database, an Excel workbook, or a Word document later (§11) without rework. The validator at `scripts/validate-schemas.py` enforces these conventions on every commit via the `schema-validate` CI job.

## Format reference

| Artifact | ID kind | Pattern | Scope of uniqueness | Example |
|---|---|---|---|---|
| KB manifest entry | `ref-id` | `REF-NNN` | manifest file | `REF-001` |
| Pillar | `pillar-id` | `P-NN` | project | `P-04` |
| Scientific statement | `SS-id` | `SS-NN` | parent pillar | `SS-01` |
| Reference statement | `RS-id` | `RS-NN` | parent scientific statement | `RS-02` |
| Evidence-gap entry | `gap-id` | `GAP-NNN` | evidence-gaps file | `GAP-001` |
| Aspirational statement | `asp-id` | `ASP-NNN` | aspirational-statements file | `ASP-001` |
| Fact-check finding | `finding-id` | `FC-<sprint>-NNN` | fact-check-report file | `FC-04-001` |
| Editorial flagged item | `finding-id` | `ED-<sprint>-NNN` | editorial-report file | `ED-04-001` |
| Strategic-alignment finding | `finding-id` | `SA-<draft-tag>-NNN` | strategic-alignment-report file | `SA-CD1-001` |

`NN` is two zero-padded digits; `NNN` is three. `<sprint>` is the zero-padded sprint number. `<draft-tag>` is a kebab/upper-case tag tied to the consolidated draft (e.g. `CD1` for `cd-001`).

## Composite references

Cross-artifact references compose IDs with `.` as the separator:

- `pillar-id.SS-id` — e.g. `P-04.SS-01` (a scientific statement)
- `pillar-id.SS-id.RS-id` — e.g. `P-04.SS-01.RS-02` (a reference statement)
- `<draft-id>` — e.g. `cd-001` (a consolidated draft, used in strategic-alignment-report frontmatter)

The full path of a reference statement in the future normalized database is therefore `<pillar-id>.<SS-id>.<RS-id>` (per §7.5 of the spec).

## Where these IDs are referenced

- Reference statements cite KB entries via `sources: [REF-NNN, ...]`. Source ids must be well-formed (`REF-NNN`); cross-document resolution to actual manifest entries is verified by P6 (KB Librarian).
- Evidence-gap entries link via `linked_to: <pillar-id.SS-id[.RS-id]>`.
- Aspirational statements link via `linked_statement: <pillar-id.SS-id[.RS-id]>`.
- Fact-check, editorial, and strategic-alignment findings use `target:` to point at a pillar, scientific statement, reference statement, or the literal string `deliverable` (strategic-alignment only).

## Enforcement

The validator at `scripts/validate-schemas.py` enforces:

1. **Format.** Every entry's heading id matches its artifact's pattern.
2. **Uniqueness within scope.** No duplicate ids in the same scope (e.g. two `SS-01` in one pillar; two `REF-001` in one manifest).
3. **Composite reference format.** Where present, dotted-id references like `P-04.SS-01.RS-02` parse as `<pillar-id>.<SS-id>[.<RS-id>]` with correct component formats.
4. **Source reference format.** RS `sources:` list entries are well-formed `REF-NNN` ids (cross-document resolution remains P6 territory).

A deliberate-fail injection test in M5 of P3 verified the validator catches duplicate SS ids and malformed REF references; see the M5 commit message for details.

## Append-only renumbering

Per §6.5 and the §7 schema for pillar/SS/RS: ids are assigned **append-only**. When work is rewound and an SS or RS is reopened, its id is preserved (not reused). When the rewind produces new content, new ids increment from the highest id ever assigned, not from the highest currently-active id. This keeps cross-references stable across revisions.

## When these conventions might change

A change to any pattern above requires a decisions-log entry in `IMPLEMENTATION_ROADMAP.md` recording the migration plan for existing engagement repos. Format changes are breaking — bump the plugin's minor version and document in `CHANGELOG.md`.
