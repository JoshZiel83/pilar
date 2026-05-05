#!/usr/bin/env python3
"""Validate engagement-level pilar artifacts against schema templates.

Given one or more target paths (files or directories), parses each file's
YAML frontmatter to find its `artifact:` type, looks up the matching schema
template in `schemas/<artifact>.md`, and asserts:

  - every frontmatter key declared in the schema is present in the target;
  - no frontmatter value in the target is a `<placeholder>` left over from
    the template;
  - every H2 heading declared in the schema is present in the target;
  - every entry-id heading (KB ref-id, P-NN, SS-NN, RS-NN, GAP-NNN,
    ASP-NNN, FC-/ED-/CL-/SA-) matches the format conventions documented
    in `docs/CONVENTIONS.md`;
  - entry ids are unique within their declared scope (e.g. no duplicate
    SS-NN within one pillar, no duplicate ref-id within one manifest);
  - composite-id references (linked_to, linked_statement, target,
    sources) are well-formed.

Exits non-zero if any check fails. Errors are emitted in GitHub Actions
`::error::` workflow-command format so they surface as PR annotations.

Designed to be dependency-free: parses the strict-subset YAML used by pilar
artifact frontmatter (one `key: value` per line, no nesting) without PyYAML.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# ID format patterns. See docs/CONVENTIONS.md for rationale and scope rules.
# ---------------------------------------------------------------------------

ID_PATTERNS: dict[str, str] = {
    "ref": r"^[A-Za-z0-9-]+(?:_[A-Za-z0-9-]+)+$",
    "pillar": r"^P-\d{2}$",
    "ss": r"^SS-\d{2}$",
    "rs": r"^RS-\d{2}$",
    "gap": r"^GAP-\d{3}$",
    "asp": r"^ASP-\d{3}$",
    "fc": r"^FC-\d+-\d{3}$",
    "ed": r"^ED-\d+-\d{3}$",
    "sa": r"^SA-[A-Z0-9-]+-\d{3}$",
    "cd": r"^cd-\d{3}$",
}

# Frontmatter values that must match an ID_PATTERNS regex. Maps
# (artifact, frontmatter-key) -> ID_PATTERNS key. Used to enforce
# foreign-key well-formedness on cross-artifact references that live
# in frontmatter rather than the body (e.g. SA report → consolidated draft).
FRONTMATTER_ID_RULES: dict[tuple[str, str], str] = {
    ("consolidated-draft", "draft_id"): "cd",
    ("strategic-alignment-report", "consolidated_draft"): "cd",
}

COMPOSITE_REF = re.compile(
    r"^P-\d{2}(?:\.SS-\d{2}(?:\.RS-\d{2})?)?$"
)


# Per-artifact heading id rules. Each rule walks a section (or whole body
# if section is None), pulls headings at the given level, and asserts each
# heading's id-prefix (the part before ":") matches the named pattern.
#
# `section` is the H2 heading name; None means "whole body".
# `level` is the markdown heading depth (3 = "###", 4 = "####").
# `pattern` is a key into ID_PATTERNS.
# `scope` is a string used as the uniqueness scope: "file" means uniqueness
# across all entries of this rule in the file.

ID_RULES: dict[str, list[dict]] = {
    "kb-manifest": [
        {"section": "Entries", "level": 3, "pattern": "ref", "scope": "file"},
    ],
    "evidence-gaps": [
        {"section": "Open Gaps", "level": 3, "pattern": "gap", "scope": "file"},
        {"section": "Closed Gaps", "level": 3, "pattern": "gap", "scope": "file"},
    ],
    "aspirational-statements": [
        {"section": None, "level": 3, "pattern": "asp", "scope": "file"},
    ],
    "fact-check-report": [
        {"section": "Findings", "level": 3, "pattern": "fc", "scope": "file"},
    ],
    "editorial-report": [
        {"section": "Items Flagged But Not Edited", "level": 3, "pattern": "ed", "scope": "file"},
    ],
    "strategic-alignment-report": [
        {"section": "Findings", "level": 3, "pattern": "sa", "scope": "file"},
    ],
    # Pillar handled specially via validate_pillar_nested.
}


# ---------------------------------------------------------------------------
# Frontmatter / heading utilities.
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body) for a markdown document with YAML frontmatter."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5 :]
    fm: dict[str, str] = {}
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        fm[key.strip()] = value.strip()
    return fm, body


def extract_h2_headings(body: str) -> list[str]:
    return [line[3:].strip() for line in body.split("\n") if line.startswith("## ")]


def section_body(body: str, section_name: str) -> str | None:
    """Return body of the H2 section with the given name, or None if absent."""
    pattern = re.compile(rf"^##\s+{re.escape(section_name)}\s*$", re.MULTILINE)
    m = pattern.search(body)
    if not m:
        return None
    start = m.end()
    rest = body[start:]
    next_h2 = re.search(r"^##\s+", rest, re.MULTILINE)
    end = start + next_h2.start() if next_h2 else len(body)
    return body[start:end]


def find_headings(body: str, level: int) -> list[tuple[str, int]]:
    """Return [(title, start_offset), ...] for each H<level> heading in body."""
    prefix = "#" * level + " "
    pattern = re.compile(rf"^{re.escape(prefix)}(.+?)\s*$", re.MULTILINE)
    return [(m.group(1), m.start()) for m in pattern.finditer(body)]


def is_placeholder(value: str) -> bool:
    return value.startswith("<") and value.endswith(">") and len(value) > 2


def heading_id(title: str) -> str:
    """Extract the id portion of a heading title (everything before first ':')."""
    return title.split(":", 1)[0].strip()


# ---------------------------------------------------------------------------
# Validators.
# ---------------------------------------------------------------------------


def validate_id_rule(
    target: Path, body: str, rule: dict, ids_seen: set[str]
) -> list[str]:
    section = rule["section"]
    level = rule["level"]
    pattern_key = rule["pattern"]
    pattern = re.compile(ID_PATTERNS[pattern_key])

    scope_body = body if section is None else section_body(body, section)
    if scope_body is None:
        return []

    errors: list[str] = []
    for title, _offset in find_headings(scope_body, level):
        ident = heading_id(title)
        if not pattern.match(ident):
            errors.append(
                f"{target}: id '{ident}' under "
                f"{'whole body' if section is None else f'section ## {section}'} "
                f"does not match {pattern_key.upper()} pattern {pattern.pattern}"
            )
            continue
        if ident in ids_seen:
            errors.append(
                f"{target}: duplicate id '{ident}' in "
                f"{'whole body' if section is None else f'## {section}'}"
            )
        ids_seen.add(ident)
    return errors


def validate_composite_ref(target: Path, label: str, value: str) -> list[str]:
    if not COMPOSITE_REF.match(value):
        return [
            f"{target}: {label} '{value}' is not a well-formed composite id "
            f"(expected `P-NN`, `P-NN.SS-NN`, or `P-NN.SS-NN.RS-NN`)"
        ]
    return []


def validate_pillar_nested(target: Path, fm: dict[str, str], body: str) -> list[str]:
    errors: list[str] = []

    pillar_id = fm.get("pillar_id", "")
    if not re.match(ID_PATTERNS["pillar"], pillar_id):
        errors.append(
            f"{target}: pillar_id '{pillar_id}' does not match P-NN pattern"
        )

    ss_section = section_body(body, "Scientific Statements")
    if ss_section is None:
        return errors

    ss_headings = find_headings(ss_section, 3)
    seen_ss: set[str] = set()
    for i, (ss_title, ss_start) in enumerate(ss_headings):
        ss_id = heading_id(ss_title)
        if not re.match(ID_PATTERNS["ss"], ss_id):
            errors.append(
                f"{target}: SS heading '{ss_title}' id '{ss_id}' does not match SS-NN pattern"
            )
            continue
        if ss_id in seen_ss:
            errors.append(f"{target}: duplicate scientific-statement id '{ss_id}'")
        seen_ss.add(ss_id)

        # Body of this SS = from end of this H3 to start of next H3 or end of section.
        ss_body_start = ss_start + len(f"### {ss_title}")
        ss_body_end = (
            ss_headings[i + 1][1] if i + 1 < len(ss_headings) else len(ss_section)
        )
        ss_body = ss_section[ss_body_start:ss_body_end]

        # RS validation within this SS.
        rs_headings = find_headings(ss_body, 4)
        seen_rs: set[str] = set()
        for rs_title, _rs_offset in rs_headings:
            rs_id = heading_id(rs_title)
            if not re.match(ID_PATTERNS["rs"], rs_id):
                errors.append(
                    f"{target}: in {ss_id}, RS heading '{rs_title}' id '{rs_id}' "
                    "does not match RS-NN pattern"
                )
                continue
            if rs_id in seen_rs:
                errors.append(
                    f"{target}: duplicate reference-statement id '{rs_id}' in {ss_id}"
                )
            seen_rs.add(rs_id)

        # sources: [<ref-id>, <ref-id>, ...] checks within this SS body.
        for sm in re.finditer(r"sources:\s*\[(.*?)\]", ss_body):
            for raw in sm.group(1).split(","):
                ref = raw.strip()
                if not ref:
                    continue
                if not re.match(ID_PATTERNS["ref"], ref):
                    errors.append(
                        f"{target}: in {ss_id}, malformed source reference '{ref}' "
                        "(expected property-based id, e.g. `Smith_J_2024_Synth-J-Med`; "
                        "see docs/CONVENTIONS.md)"
                    )

    return errors


def validate_composite_refs_in_body(target: Path, body: str) -> list[str]:
    """Validate composite-id references for `linked_to:` and `linked_statement:` lines."""
    errors: list[str] = []
    for label in ("linked_to", "linked_statement"):
        for m in re.finditer(rf"^- {label}:\s*(.+?)\s*$", body, re.MULTILINE):
            value = m.group(1)
            errors.extend(validate_composite_ref(target, label, value))
    return errors


KB_MANIFEST_STATUS_VALUES = {"provisional", "confirmed"}


def validate_kb_manifest_status(target: Path, body: str) -> list[str]:
    """Validate that `- status:` lines on kb-manifest entries carry an allowed value.

    Absence is allowed (defaults to `confirmed` semantically). When present,
    only `provisional` or `confirmed` are permitted.
    """
    errors: list[str] = []
    for m in re.finditer(r"^- status:\s*(.+?)\s*$", body, re.MULTILINE):
        value = m.group(1)
        if value not in KB_MANIFEST_STATUS_VALUES:
            errors.append(
                f"{target}: kb-manifest entry `status: {value}` is not allowed; "
                f"valid values are {sorted(KB_MANIFEST_STATUS_VALUES)} (or omit for default `confirmed`)"
            )
    return errors


def validate(target: Path, schema_dir: Path) -> list[str]:
    if not target.exists():
        return [f"{target}: file does not exist"]

    text = target.read_text()
    fm, body = parse_frontmatter(text)

    if "artifact" not in fm:
        return [f"{target}: missing 'artifact' key in frontmatter"]

    artifact = fm["artifact"]
    schema_path = schema_dir / f"{artifact}.md"
    if not schema_path.exists():
        return [f"{target}: no schema for artifact '{artifact}' (expected {schema_path})"]

    schema_fm, schema_body = parse_frontmatter(schema_path.read_text())

    errors: list[str] = []

    for key in schema_fm:
        if key not in fm:
            errors.append(f"{target}: missing frontmatter key '{key}'")
        elif is_placeholder(fm[key]):
            errors.append(
                f"{target}: frontmatter key '{key}' still has placeholder value '{fm[key]}'"
            )

    for (rule_artifact, rule_key), pattern_key in FRONTMATTER_ID_RULES.items():
        if rule_artifact != artifact:
            continue
        value = fm.get(rule_key)
        if value is None or is_placeholder(value):
            continue
        if not re.match(ID_PATTERNS[pattern_key], value):
            errors.append(
                f"{target}: frontmatter '{rule_key}' value '{value}' does not "
                f"match {pattern_key.upper()} pattern {ID_PATTERNS[pattern_key]}"
            )

    schema_headings = set(extract_h2_headings(schema_body))
    target_headings = set(extract_h2_headings(body))
    for h in sorted(schema_headings - target_headings):
        errors.append(f"{target}: missing required H2 heading '## {h}'")

    # Per-artifact id-format and uniqueness rules.
    rules = ID_RULES.get(artifact, [])
    ids_seen: set[str] = set()
    for rule in rules:
        errors.extend(validate_id_rule(target, body, rule, ids_seen))

    if artifact == "pillar":
        errors.extend(validate_pillar_nested(target, fm, body))

    if artifact == "kb-manifest":
        errors.extend(validate_kb_manifest_status(target, body))

    # Composite-id references (linked_to, linked_statement) in any artifact body.
    errors.extend(validate_composite_refs_in_body(target, body))

    return errors


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def collect_targets(args: list[str]) -> list[Path]:
    targets: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            targets.extend(sorted(p.glob("*.md")))
        else:
            targets.append(p)
    return targets


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: validate-schemas.py <target-file-or-dir>...", file=sys.stderr)
        return 2

    schema_dir = Path(__file__).resolve().parent.parent / "schemas"
    if not schema_dir.is_dir():
        print(f"::error::schemas directory not found: {schema_dir}", file=sys.stderr)
        return 2

    targets = collect_targets(argv)
    if not targets:
        print("::error::no target files found", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for t in targets:
        errors = validate(t, schema_dir)
        all_errors.extend(errors)

    for e in all_errors:
        print(f"::error::{e}")

    summary = f"Validated {len(targets)} file(s); {len(all_errors)} error(s)"
    print(summary, file=sys.stderr)

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
