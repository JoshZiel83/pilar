#!/usr/bin/env python3
"""Static context audit for pilar QC subagent harnesses.

Codifies the §4/§8 Independence Contract appendix from
IMPLEMENTATION_ROADMAP.md as executable policy. Failure means the
prompt-construction pattern in commands/run-qc.md or the subagent
isolation in agents/<role>.md drifted outside what the spec permits
that role to see.

What this audit checks
----------------------

For each registered harness in QC_HARNESSES:

For commands/run-qc.md:
  - The prompt template enclosed by the harness's sentinel pair (e.g.
    <<<PILAR_FACT_CHECKER_PROMPT … PILAR_FACT_CHECKER_PROMPT>>>) exists.
  - Every {variable} reference inside that template appears in the
    harness's allowlist. Any other {var} = leak.
  - The template body contains no forbidden tokens corresponding to
    inputs the contract withholds from this role.

For agents/<role>.md:
  - The subagent declares `tools: []` or `tools: [Read]` in frontmatter.
    No other tools list is permitted. Read is allowed because the
    parent passes paths (not inlined content) for the artifact + the
    role-specific permitted resources, and the subagent reads them.

What this audit does NOT check
------------------------------

The agent body intentionally enumerates withheld inputs ("you do not
receive — and must not request — the briefing, the roadmap, …"), so
forbidden-token scans are NOT applied there. This audit operates on the
prompt template (parent-controlled content) and on the subagent's
frontmatter contract.

The Strategic Reviewer harness will be registered in P8 — adding it is
a one-entry append to QC_HARNESSES.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

VAR_REF = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


# -- QC harness registry -------------------------------------------------
# Adding a new QC subagent (e.g. Strategic Reviewer at P8) is a single
# dict appended to this list.

QC_HARNESSES: list[dict] = [
    {
        "name": "fact-checker",
        "agent_path": "agents/fact-checker.md",
        "sentinel_open": "<<<PILAR_FACT_CHECKER_PROMPT",
        "sentinel_close": "PILAR_FACT_CHECKER_PROMPT>>>",
        "allowed_vars": {
            "{operating_context}",
            "{artifact_id}",
            "{artifact_path}",
            "{source_paths}",
        },
        "forbidden_tokens": [
            "briefing",
            "roadmap",
            "lexicon",
            "style guide",
            "style-guide",
            "drafting rationale",
            "sprint summary",
            "sprint-summary",
            "primary collaborator",
            "other pillars",
            "other pillar",
            "kb manifest",
            "kb-manifest",
        ],
        # Fact-Checker reports findings; never edits. Read-only or zero-tool
        # are the only permissible declarations.
        "allowed_tools_sets": [set(), {"Read"}],
    },
    {
        "name": "editor",
        "agent_path": "agents/editor.md",
        "sentinel_open": "<<<PILAR_EDITOR_PROMPT",
        "sentinel_close": "PILAR_EDITOR_PROMPT>>>",
        "allowed_vars": {
            "{operating_context}",
            "{artifact_id}",
            "{artifact_path}",
            "{lexicon_path}",
            "{style_guide_path}",
        },
        "forbidden_tokens": [
            "briefing",
            "roadmap",
            "drafting rationale",
            "sprint summary",
            "sprint-summary",
            "primary collaborator",
            "source file",
            "source files",
            "fact-check report",
            "fact-checker report",
            "kb manifest",
            "kb-manifest",
        ],
        # Editor applies meaning-preserving edits surgically via the Edit tool
        # (P5 refinement). Read alone (legacy two-block reproduction pattern)
        # is also still permitted but no longer used by the harness.
        "allowed_tools_sets": [{"Read"}, {"Read", "Edit"}],
    },
    {
        "name": "strategic-reviewer",
        "agent_path": "agents/strategic-reviewer.md",
        "sentinel_open": "<<<PILAR_STRATEGIC_REVIEWER_PROMPT",
        "sentinel_close": "PILAR_STRATEGIC_REVIEWER_PROMPT>>>",
        "allowed_vars": {
            "{operating_context}",
            "{draft_id}",
            "{briefing_path}",
            "{roadmap_path}",
            "{artifact_path}",
        },
        "forbidden_tokens": [
            "drafting rationale",
            "sprint summary",
            "sprint-summary",
            "primary collaborator",
            "kb manifest",
            "kb-manifest",
            "source file",
            "source files",
            "lexicon path",
            "style guide",
            "style-guide",
            "fact-check report",
            "fact-checker report",
            "editorial report",
            "per-pillar progress",
            "progress notes",
        ],
        # Strategic Reviewer reads briefing + roadmap + edited consolidated
        # draft. Reports findings; never edits. Read-only is the only
        # permissible tools declaration.
        "allowed_tools_sets": [{"Read"}],
    },
]


def extract_prompt_template(text: str, sentinel_open: str, sentinel_close: str) -> str | None:
    """Return the body between the sentinel markers, or None if missing."""
    pattern = re.compile(
        rf"{re.escape(sentinel_open)}\n(.*?)\n{re.escape(sentinel_close)}",
        re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1) if m else None


def audit_run_qc_for_harness(path: Path, run_qc_text: str, harness: dict) -> list[str]:
    template = extract_prompt_template(
        run_qc_text, harness["sentinel_open"], harness["sentinel_close"]
    )
    if template is None:
        return [
            f"{path}: prompt-template sentinels "
            f"{harness['sentinel_open']} ... {harness['sentinel_close']} not found "
            f"(harness: {harness['name']})"
        ]

    errors: list[str] = []
    name = harness["name"]
    allowed = harness["allowed_vars"]

    found_vars = set(VAR_REF.findall(template))
    extra = found_vars - allowed
    for v in sorted(extra):
        errors.append(
            f"{path}: {name} prompt template uses unallowed variable {v}; "
            f"{name} allowlist is {sorted(allowed)}"
        )

    lower = template.lower()
    for tok in harness["forbidden_tokens"]:
        if tok.lower() in lower:
            errors.append(
                f"{path}: {name} prompt template contains forbidden token '{tok}' — "
                f"this input is withheld from the {name} per §4/§8 of the spec"
            )

    return errors


def parse_tools_list(line: str) -> set[str] | None:
    """Parse a frontmatter line like 'tools: [Read, Edit]' into {'Read', 'Edit'}.

    Returns None if the line is not a recognizable tools list. Empty list
    `tools: []` returns the empty set.
    """
    s = line.strip()
    if not s.startswith("tools:"):
        return None
    rest = s[len("tools:") :].strip()
    if not (rest.startswith("[") and rest.endswith("]")):
        return None
    inside = rest[1:-1].strip()
    if not inside:
        return set()
    items = [
        p.strip().strip('"').strip("'")
        for p in inside.split(",")
    ]
    return {item for item in items if item}


def format_tool_sets(sets: list[set[str]]) -> str:
    """Render a list of allowed tools sets as a human-readable summary."""
    return ", ".join(
        "[]" if not s else f"[{', '.join(sorted(s))}]"
        for s in sets
    )


def audit_subagent_frontmatter(path: Path, harness: dict) -> list[str]:
    if not path.exists():
        return [f"{path}: file does not exist (harness: {harness['name']})"]
    text = path.read_text()
    errors: list[str] = []

    fm_end = text.find("\n---\n", 4)
    if fm_end == -1:
        return [f"{path}: missing closing --- in frontmatter"]
    fm = text[4:fm_end]

    tools_line: str | None = None
    for line in fm.split("\n"):
        s = line.strip()
        if s.startswith("tools:"):
            tools_line = s
            break

    if tools_line is None:
        errors.append(f"{path}: subagent must declare 'tools' in frontmatter")
        return errors

    parsed = parse_tools_list(tools_line)
    if parsed is None:
        errors.append(
            f"{path}: could not parse tools declaration '{tools_line}' "
            "(expected `tools: [Tool1, Tool2, …]`)"
        )
        return errors

    allowed_sets: list[set[str]] = harness.get("allowed_tools_sets", [])
    if parsed not in allowed_sets:
        errors.append(
            f"{path}: {harness['name']} declares tools {sorted(parsed) or '[]'} "
            f"which is not in this harness's allowlist; allowed sets are "
            f"{format_tool_sets(allowed_sets)}. The Independence Contract "
            "constrains each QC subagent's filesystem access; loosening it "
            "requires updating QC_HARNESSES with rationale."
        )

    return errors


def main() -> int:
    run_qc_path = REPO / "commands" / "run-qc.md"
    if not run_qc_path.exists():
        print(f"::error::{run_qc_path}: does not exist", file=sys.stderr)
        return 1
    run_qc_text = run_qc_path.read_text()

    errors: list[str] = []
    for harness in QC_HARNESSES:
        errors.extend(audit_run_qc_for_harness(run_qc_path, run_qc_text, harness))
        errors.extend(
            audit_subagent_frontmatter(REPO / harness["agent_path"], harness)
        )

    for e in errors:
        print(f"::error::{e}")

    summary = f"Context-audit: {len(errors)} error(s) across {len(QC_HARNESSES)} harness(es)"
    print(summary, file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
