#!/usr/bin/env python3
"""Static context audit for pilar QC subagent harnesses.

Codifies the §4/§8 Independence Contract appendix from
IMPLEMENTATION_ROADMAP.md as executable policy. Failure means the
prompt-construction pattern in commands/run-qc.md or the subagent
isolation in agents/fact-checker.md drifted outside what the spec
permits the Fact-Checker to see.

What this audit checks
----------------------

For commands/run-qc.md:
  - The prompt template enclosed by <<<PILAR_FACT_CHECKER_PROMPT
    ... PILAR_FACT_CHECKER_PROMPT>>> sentinels exists.
  - Every {variable} reference inside that template appears in the
    Fact-Checker allowlist (operating_context, artifact_id,
    artifact_text, source_texts). Any other {var} = leak.
  - The template body contains no forbidden tokens corresponding to
    inputs the contract withholds from the Fact-Checker (briefing,
    roadmap, lexicon, style guide, drafting rationale, sprint summary,
    primary collaborator, other pillars, kb manifest).

For agents/fact-checker.md:
  - The subagent declares `tools: []` in frontmatter. An empty tools
    list is the load-bearing isolation guarantee for the Phase 2 stub:
    no file-system access means the parent's prompt is the entire
    context the subagent can see.

What this audit does NOT check
------------------------------

The agent body intentionally enumerates withheld inputs ("you do not
receive — and must not request — the briefing, the roadmap, ..."), so
forbidden-token scans are NOT applied there. This audit operates on the
prompt template (parent-controlled content) and on the subagent's
frontmatter contract.

Phase 5 extends this audit to register Editor and (Phase 8) Strategic
Reviewer harnesses with their own allowlists and forbidden-token sets.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# -- Fact-Checker harness contract ---------------------------------------

FACT_CHECKER_ALLOWED_VARS: set[str] = {
    "{operating_context}",
    "{artifact_id}",
    "{artifact_text}",
    "{source_texts}",
}

FACT_CHECKER_FORBIDDEN_TOKENS: list[str] = [
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
]

PROMPT_BLOCK = re.compile(
    r"<<<PILAR_FACT_CHECKER_PROMPT\n(.*?)\nPILAR_FACT_CHECKER_PROMPT>>>",
    re.DOTALL,
)
VAR_REF = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


def audit_run_qc(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: file does not exist"]
    text = path.read_text()
    m = PROMPT_BLOCK.search(text)
    if not m:
        return [
            f"{path}: prompt-template sentinels "
            "<<<PILAR_FACT_CHECKER_PROMPT ... PILAR_FACT_CHECKER_PROMPT>>> not found"
        ]
    template = m.group(1)
    errors: list[str] = []

    found_vars = set(VAR_REF.findall(template))
    extra = found_vars - FACT_CHECKER_ALLOWED_VARS
    for v in sorted(extra):
        errors.append(
            f"{path}: prompt template uses unallowed variable {v}; "
            f"Fact-Checker allowlist is {sorted(FACT_CHECKER_ALLOWED_VARS)}"
        )

    lower = template.lower()
    for tok in FACT_CHECKER_FORBIDDEN_TOKENS:
        if tok.lower() in lower:
            errors.append(
                f"{path}: prompt template contains forbidden token '{tok}' — "
                f"this input is withheld from the Fact-Checker per §4/§8 of the spec"
            )

    return errors


def audit_fact_checker_agent(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: file does not exist"]
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
    elif tools_line.replace(" ", "") != "tools:[]":
        errors.append(
            f"{path}: subagent must declare 'tools: []' (got: '{tools_line}'); "
            "an empty tools list is the load-bearing isolation guarantee for "
            "the P2 stub — no file-system access means the parent's prompt is "
            "the entire context the subagent can see"
        )

    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(audit_run_qc(REPO / "commands" / "run-qc.md"))
    errors.extend(audit_fact_checker_agent(REPO / "agents" / "fact-checker.md"))

    for e in errors:
        print(f"::error::{e}")

    summary = f"Context-audit: {len(errors)} error(s)"
    print(summary, file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
