#!/usr/bin/env python3
"""Deterministic fetcher for provisional KB sources from PubMed and ClinicalTrials.gov.

This script is the canonical-bytes path for `/pilar:research` (issue #11).
It deliberately bypasses the MCP layer used by the slash command for
search/preview — the MCP responses are LLM-mediated when read by Claude,
which reintroduces hallucination risk for any bytes that get saved into
the engagement. This script hits the upstream APIs directly and writes
verbatim content; no LLM ever touches the saved bytes.

Same input + same calendar date → byte-identical output (only the
`fetched:` line varies across days). The `--verify` mode re-fetches and
diffs critical fields against a previously-saved file, so drift can be
detected at any time.

Stdlib-only: urllib.request, xml.etree.ElementTree, json, argparse,
pathlib, re, sys, datetime. No third-party dependencies.

Usage:
  research-fetch.py --pubmed PMID[,PMID,...] [--ctgov NCT[,NCT,...]] [--output DIR]
  research-fetch.py --ctgov NCT[,NCT,...] [--output DIR]
  research-fetch.py --verify FILE
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_OUTPUT_REL = "knowledge-base/for_ingestion"

PUBMED_EFETCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    "?db=pubmed&id={pmid}&retmode=xml"
)
CTGOV_STUDY_URL = (
    "https://clinicaltrials.gov/api/v2/studies/{nct}?format=json"
)

USER_AGENT = "pilar-research-fetch/1.0 (https://github.com/JoshZiel83/pilar)"


# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------


def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


# ---------------------------------------------------------------------------
# PubMed
# ---------------------------------------------------------------------------


def fetch_pubmed(pmid: str) -> dict:
    """Fetch PubMed metadata for a PMID via E-utilities efetch (XML).

    Returns a dict with verbatim fields extracted from the XML. Raises on
    HTTP errors or unparseable responses.
    """
    if not re.fullmatch(r"\d+", pmid):
        raise ValueError(f"PMID '{pmid}' is not numeric")
    raw = _http_get(PUBMED_EFETCH_URL.format(pmid=pmid))
    root = ET.fromstring(raw)
    article = root.find(".//PubmedArticle")
    if article is None:
        raise RuntimeError(f"PMID {pmid}: no <PubmedArticle> in response")

    medline = article.find("MedlineCitation")
    if medline is None:
        raise RuntimeError(f"PMID {pmid}: no <MedlineCitation>")
    art = medline.find("Article")
    if art is None:
        raise RuntimeError(f"PMID {pmid}: no <Article>")

    title_el = art.find("ArticleTitle")
    title = _xml_text(title_el)

    abstract = _format_abstract(art.find("Abstract"))

    journal_el = art.find("Journal")
    journal_title = _xml_text(journal_el.find("Title")) if journal_el is not None else ""
    journal_iso = _xml_text(journal_el.find("ISOAbbreviation")) if journal_el is not None else ""
    journal = journal_iso or journal_title

    issue_el = journal_el.find("JournalIssue") if journal_el is not None else None
    volume = _xml_text(issue_el.find("Volume")) if issue_el is not None else ""
    issue = _xml_text(issue_el.find("Issue")) if issue_el is not None else ""

    pubdate_el = issue_el.find("PubDate") if issue_el is not None else None
    year = ""
    if pubdate_el is not None:
        year = _xml_text(pubdate_el.find("Year"))
        if not year:
            medline_date = _xml_text(pubdate_el.find("MedlineDate"))
            m = re.search(r"\d{4}", medline_date)
            year = m.group(0) if m else ""

    pagination_el = art.find("Pagination")
    pages = _xml_text(pagination_el.find("MedlinePgn")) if pagination_el is not None else ""

    authors: list[str] = []
    author_list = art.find("AuthorList")
    if author_list is not None:
        for au in author_list.findall("Author"):
            last = _xml_text(au.find("LastName"))
            initials = _xml_text(au.find("Initials"))
            collective = _xml_text(au.find("CollectiveName"))
            if last:
                authors.append(f"{last} {initials}".strip())
            elif collective:
                authors.append(collective)

    pub_types: list[str] = []
    pt_list = art.find("PublicationTypeList")
    if pt_list is not None:
        for pt in pt_list.findall("PublicationType"):
            pub_types.append(_xml_text(pt))

    mesh_terms: list[str] = []
    mh_list = medline.find("MeshHeadingList")
    if mh_list is not None:
        for mh in mh_list.findall("MeshHeading"):
            desc = _xml_text(mh.find("DescriptorName"))
            if desc:
                mesh_terms.append(desc)

    doi = ""
    pmcid = ""
    for eloc in art.findall("ELocationID"):
        if eloc.get("EIdType") == "doi":
            doi = (eloc.text or "").strip()
    article_ids = article.find(".//PubmedData/ArticleIdList")
    if article_ids is not None:
        for aid in article_ids.findall("ArticleId"):
            t = aid.get("IdType")
            v = (aid.text or "").strip()
            if t == "doi" and not doi:
                doi = v
            elif t == "pmc":
                pmcid = v

    return {
        "pmid": pmid,
        "pmcid": pmcid,
        "doi": doi,
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "publication_type": pub_types,
        "mesh_terms": mesh_terms,
        "abstract": abstract,
    }


def _xml_text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(_xml_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts).strip()


def _format_abstract(abstract_el: ET.Element | None) -> str:
    if abstract_el is None:
        return ""
    blocks: list[str] = []
    for at in abstract_el.findall("AbstractText"):
        label = at.get("Label")
        text = _xml_text(at)
        if not text:
            continue
        if label:
            blocks.append(f"**{label}.** {text}")
        else:
            blocks.append(text)
    return "\n\n".join(blocks)


def render_pubmed(data: dict, fetched: str) -> str:
    """Render PubMed metadata as canonical markdown.

    Output is deterministic: same `data` + same `fetched` → identical bytes.
    """
    pmid = data["pmid"]
    citation = _vancouver_citation(data)
    authors_yaml = _yaml_inline_list(data["authors"])
    pub_types_yaml = _yaml_inline_list(data["publication_type"])
    mesh_yaml = _yaml_inline_list(data["mesh_terms"])

    parts: list[str] = []
    parts.append("---")
    parts.append("artifact: kb-source")
    parts.append("provisional: true")
    parts.append("source: pubmed")
    parts.append(f"pmid: {pmid}")
    parts.append(f"pmcid: {data['pmcid']}")
    parts.append(f"doi: {data['doi']}")
    parts.append(f"title: {_yaml_inline_string(data['title'])}")
    parts.append(f"authors: {authors_yaml}")
    parts.append(f"journal: {_yaml_inline_string(data['journal'])}")
    parts.append(f"year: {data['year']}")
    parts.append(f"volume: {data['volume']}")
    parts.append(f"issue: {data['issue']}")
    parts.append(f"pages: {data['pages']}")
    parts.append(f"publication_type: {pub_types_yaml}")
    parts.append(f"mesh_terms: {mesh_yaml}")
    parts.append(f"fetched: {fetched}")
    parts.append(
        f"fetch_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    )
    parts.append("---")
    parts.append("")
    parts.append(f"# {data['title']}")
    parts.append("")
    parts.append(f"**Citation:** {citation}")
    parts.append("")
    doi_link = f"[{data['doi']}](https://doi.org/{data['doi']})" if data["doi"] else "—"
    parts.append(
        f"**DOI:** {doi_link} **PMID:** [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})"
    )
    parts.append("")
    parts.append("## Abstract")
    parts.append("")
    parts.append(data["abstract"] or "_(no abstract returned by PubMed)_")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(
        "_Provisional KB source captured by `/pilar:research`. Bytes fetched verbatim "
        "from PubMed E-utilities (`efetch.fcgi`) on the date in the `fetched:` field. "
        "Verify against upstream:_"
    )
    parts.append(
        f"_`python3 ${{CLAUDE_PLUGIN_ROOT}}/scripts/research-fetch.py --verify <this-file>`_"
    )
    parts.append("")
    return "\n".join(parts)


def _vancouver_citation(data: dict) -> str:
    authors = data["authors"]
    if len(authors) > 6:
        author_str = ", ".join(authors[:6]) + ", et al."
    else:
        author_str = ", ".join(authors)
    pieces: list[str] = []
    if author_str:
        pieces.append(f"{author_str}.")
    if data["title"]:
        title = data["title"].rstrip(".")
        pieces.append(f"{title}.")
    if data["journal"]:
        pieces.append(f"{data['journal']}.")
    locator: list[str] = []
    if data["year"]:
        locator.append(data["year"])
    vol_issue = data["volume"]
    if data["issue"]:
        vol_issue = f"{vol_issue}({data['issue']})"
    if vol_issue:
        if locator:
            locator[-1] = f"{locator[-1]};{vol_issue}"
        else:
            locator.append(vol_issue)
    if data["pages"]:
        if locator:
            locator[-1] = f"{locator[-1]}:{data['pages']}"
        else:
            locator.append(data["pages"])
    if locator:
        pieces.append(f"{locator[0]}.")
    return " ".join(pieces)


# ---------------------------------------------------------------------------
# ClinicalTrials.gov
# ---------------------------------------------------------------------------


def fetch_ctgov(nct_id: str) -> dict:
    """Fetch a study record from ClinicalTrials.gov v2 API (JSON)."""
    if not re.fullmatch(r"NCT\d+", nct_id):
        raise ValueError(f"NCT id '{nct_id}' is malformed (expected NCT followed by digits)")
    raw = _http_get(CTGOV_STUDY_URL.format(nct=nct_id))
    payload = json.loads(raw)
    proto = payload.get("protocolSection", {})

    ident = proto.get("identificationModule", {})
    status = proto.get("statusModule", {})
    design = proto.get("designModule", {})
    sponsors = proto.get("sponsorCollaboratorsModule", {})
    conditions_mod = proto.get("conditionsModule", {})
    arms = proto.get("armsInterventionsModule", {})
    elig = proto.get("eligibilityModule", {})
    desc = proto.get("descriptionModule", {})
    outcomes = proto.get("outcomesModule", {})

    return {
        "nct_id": nct_id,
        "brief_title": ident.get("briefTitle", ""),
        "official_title": ident.get("officialTitle", ""),
        "overall_status": status.get("overallStatus", ""),
        "study_type": design.get("studyType", ""),
        "phases": design.get("phases", []) or [],
        "conditions": conditions_mod.get("conditions", []) or [],
        "interventions": [
            i.get("name", "") for i in (arms.get("interventions", []) or [])
        ],
        "lead_sponsor": (sponsors.get("leadSponsor", {}) or {}).get("name", ""),
        "collaborators": [
            c.get("name", "") for c in (sponsors.get("collaborators", []) or [])
        ],
        "start_date": (status.get("startDateStruct", {}) or {}).get("date", ""),
        "completion_date": (status.get("completionDateStruct", {}) or {}).get("date", ""),
        "enrollment": (design.get("enrollmentInfo", {}) or {}).get("count", ""),
        "minimum_age": elig.get("minimumAge", ""),
        "maximum_age": elig.get("maximumAge", ""),
        "sex": elig.get("sex", ""),
        "eligibility_criteria": elig.get("eligibilityCriteria", ""),
        "brief_summary": desc.get("briefSummary", ""),
        "primary_outcomes": [
            (o.get("measure", ""), o.get("description", ""))
            for o in (outcomes.get("primaryOutcomes", []) or [])
        ],
        "secondary_outcomes": [
            (o.get("measure", ""), o.get("description", ""))
            for o in (outcomes.get("secondaryOutcomes", []) or [])
        ],
    }


def render_ctgov(data: dict, fetched: str) -> str:
    nct = data["nct_id"]
    phase_str = "; ".join(data["phases"]) if data["phases"] else ""
    conds_yaml = _yaml_inline_list(data["conditions"])
    interv_yaml = _yaml_inline_list(data["interventions"])
    collab_yaml = _yaml_inline_list(data["collaborators"])

    parts: list[str] = []
    parts.append("---")
    parts.append("artifact: kb-source")
    parts.append("provisional: true")
    parts.append("source: clinicaltrials.gov")
    parts.append(f"nct_id: {nct}")
    parts.append(f"brief_title: {_yaml_inline_string(data['brief_title'])}")
    parts.append(f"official_title: {_yaml_inline_string(data['official_title'])}")
    parts.append(f"phase: {phase_str}")
    parts.append(f"overall_status: {data['overall_status']}")
    parts.append(f"study_type: {data['study_type']}")
    parts.append(f"conditions: {conds_yaml}")
    parts.append(f"interventions: {interv_yaml}")
    parts.append(f"lead_sponsor: {_yaml_inline_string(data['lead_sponsor'])}")
    parts.append(f"collaborators: {collab_yaml}")
    parts.append(f"start_date: {data['start_date']}")
    parts.append(f"completion_date: {data['completion_date']}")
    parts.append(f"enrollment: {data['enrollment']}")
    parts.append(f"fetched: {fetched}")
    parts.append(
        f"fetch_url: https://clinicaltrials.gov/api/v2/studies/{nct}?format=json"
    )
    parts.append("---")
    parts.append("")
    parts.append(f"# {data['brief_title']}")
    parts.append("")
    parts.append(f"[**{nct}**](https://clinicaltrials.gov/study/{nct})")
    parts.append("")
    if data["official_title"]:
        parts.append(f"**Official title:** {data['official_title']}")
        parts.append("")
    line = []
    if phase_str:
        line.append(f"**Phase:** {phase_str}")
    if data["overall_status"]:
        line.append(f"**Status:** {data['overall_status']}")
    if data["study_type"]:
        line.append(f"**Type:** {data['study_type']}")
    if line:
        parts.append("; ".join(line))
        parts.append("")
    if data["conditions"]:
        parts.append(f"**Conditions:** {', '.join(data['conditions'])}")
    if data["interventions"]:
        parts.append(f"**Interventions:** {', '.join(data['interventions'])}")
    if data["conditions"] or data["interventions"]:
        parts.append("")
    sponsor_line = []
    if data["lead_sponsor"]:
        sponsor_line.append(f"**Sponsor:** {data['lead_sponsor']}")
    if data["collaborators"]:
        sponsor_line.append(f"**Collaborators:** {', '.join(data['collaborators'])}")
    if sponsor_line:
        parts.append("; ".join(sponsor_line))
        parts.append("")
    timing_line = []
    if data["start_date"]:
        timing_line.append(f"**Start:** {data['start_date']}")
    if data["completion_date"]:
        timing_line.append(f"**Estimated completion:** {data['completion_date']}")
    if data["enrollment"] != "":
        timing_line.append(f"**Enrollment:** {data['enrollment']}")
    if timing_line:
        parts.append("; ".join(timing_line))
        parts.append("")

    if data["brief_summary"]:
        parts.append("## Brief summary")
        parts.append("")
        parts.append(data["brief_summary"])
        parts.append("")

    if data["eligibility_criteria"]:
        parts.append("## Eligibility")
        parts.append("")
        elig_meta = []
        if data["minimum_age"]:
            elig_meta.append(f"Minimum age: {data['minimum_age']}")
        if data["maximum_age"]:
            elig_meta.append(f"Maximum age: {data['maximum_age']}")
        if data["sex"]:
            elig_meta.append(f"Sex: {data['sex']}")
        if elig_meta:
            parts.append("; ".join(elig_meta))
            parts.append("")
        parts.append(data["eligibility_criteria"])
        parts.append("")

    if data["primary_outcomes"] or data["secondary_outcomes"]:
        parts.append("## Outcomes")
        parts.append("")
        if data["primary_outcomes"]:
            parts.append("**Primary:**")
            for measure, desc in data["primary_outcomes"]:
                if desc:
                    parts.append(f"- {measure} — {desc}")
                else:
                    parts.append(f"- {measure}")
            parts.append("")
        if data["secondary_outcomes"]:
            parts.append("**Secondary:**")
            for measure, desc in data["secondary_outcomes"]:
                if desc:
                    parts.append(f"- {measure} — {desc}")
                else:
                    parts.append(f"- {measure}")
            parts.append("")

    parts.append("---")
    parts.append("")
    parts.append(
        "_Provisional KB source captured by `/pilar:research`. Bytes fetched verbatim "
        "from ClinicalTrials.gov v2 API on the date in the `fetched:` field. "
        "Verify against upstream:_"
    )
    parts.append(
        f"_`python3 ${{CLAUDE_PLUGIN_ROOT}}/scripts/research-fetch.py --verify <this-file>`_"
    )
    parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# YAML helpers (strict-subset, matching parse_frontmatter in validate-schemas.py)
# ---------------------------------------------------------------------------


def _yaml_inline_string(s: str) -> str:
    """Render a string as a YAML inline value. Quote if it contains : or starts/ends with whitespace."""
    if not s:
        return ""
    needs_quote = (
        ":" in s
        or s.startswith(" ")
        or s.endswith(" ")
        or s.startswith("[")
        or s.startswith("{")
        or s.startswith("&")
        or s.startswith("*")
        or s.startswith("!")
        or s.startswith("|")
        or s.startswith(">")
        or s.startswith("'")
        or s.startswith('"')
        or s.startswith("#")
        or s.startswith("@")
    )
    if needs_quote:
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    return s


def _yaml_inline_list(items: list[str]) -> str:
    if not items:
        return "[]"
    rendered = [_yaml_inline_string(x) for x in items]
    return "[" + ", ".join(rendered) + "]"


# ---------------------------------------------------------------------------
# Verify mode
# ---------------------------------------------------------------------------


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise RuntimeError(f"{path}: missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise RuntimeError(f"{path}: no closing '---' in frontmatter")
    fm: dict = {}
    for line in text[4:end].split("\n"):
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm


def _read_section(path: Path, heading: str) -> str:
    text = path.read_text()
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    m = pat.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    next_h2 = re.search(r"^##\s+", rest, re.MULTILINE)
    next_hr = re.search(r"^---\s*$", rest, re.MULTILINE)
    end_candidates = [x.start() for x in (next_h2, next_hr) if x is not None]
    if end_candidates:
        return rest[: min(end_candidates)].strip()
    return rest.strip()


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def verify_file(path: Path) -> int:
    fm = _read_frontmatter(path)
    source = fm.get("source", "")
    drift: list[str] = []

    if source == "pubmed":
        pmid = fm.get("pmid", "")
        if not pmid:
            print(f"::error::{path}: source=pubmed but no pmid in frontmatter", file=sys.stderr)
            return 1
        upstream = fetch_pubmed(pmid)
        # Compare title, journal, first author, abstract verbatim (whitespace-normalized).
        if _normalize(upstream["title"]) != _normalize(fm.get("title", "").strip('"')):
            drift.append(f"  title: saved='{fm.get('title', '')}' upstream='{upstream['title']}'")
        if _normalize(upstream["journal"]) != _normalize(fm.get("journal", "").strip('"')):
            drift.append(f"  journal: saved='{fm.get('journal', '')}' upstream='{upstream['journal']}'")
        first_author_upstream = upstream["authors"][0] if upstream["authors"] else ""
        # Saved authors are a YAML inline list; extract the first element.
        first_author_saved = _first_yaml_list_item(fm.get("authors", "[]"))
        if _normalize(first_author_upstream) != _normalize(first_author_saved):
            drift.append(
                f"  first author: saved='{first_author_saved}' upstream='{first_author_upstream}'"
            )
        saved_abstract = _read_section(path, "Abstract")
        upstream_abstract = upstream["abstract"]
        if _normalize(saved_abstract) != _normalize(upstream_abstract):
            drift.append(
                f"  abstract: saved length={len(saved_abstract)} upstream length={len(upstream_abstract)} (whitespace-normalized strings differ)"
            )

    elif source == "clinicaltrials.gov":
        nct = fm.get("nct_id", "")
        if not nct:
            print(f"::error::{path}: source=clinicaltrials.gov but no nct_id in frontmatter", file=sys.stderr)
            return 1
        upstream = fetch_ctgov(nct)
        if _normalize(upstream["brief_title"]) != _normalize(fm.get("brief_title", "").strip('"')):
            drift.append(
                f"  brief_title: saved='{fm.get('brief_title', '')}' upstream='{upstream['brief_title']}'"
            )
        if _normalize(upstream["lead_sponsor"]) != _normalize(fm.get("lead_sponsor", "").strip('"')):
            drift.append(
                f"  lead_sponsor: saved='{fm.get('lead_sponsor', '')}' upstream='{upstream['lead_sponsor']}'"
            )
        saved_summary = _read_section(path, "Brief summary")
        upstream_summary = upstream["brief_summary"]
        if _normalize(saved_summary) != _normalize(upstream_summary):
            drift.append(
                f"  brief_summary: saved length={len(saved_summary)} upstream length={len(upstream_summary)} (whitespace-normalized strings differ)"
            )

    else:
        print(f"::error::{path}: unknown source '{source}' (expected pubmed or clinicaltrials.gov)", file=sys.stderr)
        return 1

    if drift:
        print(f"::error::{path}: drift detected vs upstream:")
        for line in drift:
            print(line)
        return 1
    print(f"{path}: clean (no drift detected in title/sponsor/first-author/abstract).")
    return 0


def _first_yaml_list_item(yaml_list: str) -> str:
    s = yaml_list.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return ""
    inside = s[1:-1].strip()
    if not inside:
        return ""
    # Split on top-level commas; YAML inline strings may contain quoted commas.
    items: list[str] = []
    buf = ""
    in_quote = False
    for ch in inside:
        if ch == '"':
            in_quote = not in_quote
            buf += ch
        elif ch == "," and not in_quote:
            items.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        items.append(buf.strip())
    if not items:
        return ""
    first = items[0].strip()
    if first.startswith('"') and first.endswith('"'):
        first = first[1:-1].replace('\\"', '"')
    return first


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def parse_id_list(arg: str | None) -> list[str]:
    if not arg:
        return []
    return [s.strip() for s in arg.split(",") if s.strip()]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic fetcher for provisional KB sources.",
    )
    parser.add_argument(
        "--pubmed",
        help="Comma-separated PubMed IDs (e.g. 38123456,37890123)",
    )
    parser.add_argument(
        "--ctgov",
        help="Comma-separated ClinicalTrials.gov NCT IDs (e.g. NCT05123456,NCT04999000)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=f"Output directory (default: {DEFAULT_OUTPUT_REL} relative to cwd)",
    )
    parser.add_argument(
        "--verify",
        help="Re-fetch the source for the given file and diff against saved content",
    )
    args = parser.parse_args(argv)

    if args.verify:
        return verify_file(Path(args.verify))

    pmids = parse_id_list(args.pubmed)
    ncts = parse_id_list(args.ctgov)
    if not pmids and not ncts:
        parser.error("supply at least one of --pubmed, --ctgov, or --verify")

    output = Path(args.output) if args.output else Path(DEFAULT_OUTPUT_REL)
    output.mkdir(parents=True, exist_ok=True)

    fetched = _dt.date.today().isoformat()
    written: list[Path] = []
    failed: list[tuple[str, str]] = []

    for pmid in pmids:
        try:
            data = fetch_pubmed(pmid)
            md = render_pubmed(data, fetched)
            target = output / f"pmid-{pmid}.md"
            target.write_text(md)
            written.append(target)
        except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, ValueError, ET.ParseError) as e:
            failed.append((f"pmid:{pmid}", str(e)))

    for nct in ncts:
        try:
            data = fetch_ctgov(nct)
            md = render_ctgov(data, fetched)
            target = output / f"nct-{nct}.md"
            target.write_text(md)
            written.append(target)
        except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, ValueError, json.JSONDecodeError) as e:
            failed.append((f"nct:{nct}", str(e)))

    print(f"Wrote {len(written)} provisional source file(s) to {output}/:")
    for p in written:
        print(f"  - {p}")
    if failed:
        print(f"\nFailed ({len(failed)}):", file=sys.stderr)
        for ident, msg in failed:
            print(f"  - {ident}: {msg}", file=sys.stderr)

    return 0 if written and not failed else (1 if failed and not written else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
