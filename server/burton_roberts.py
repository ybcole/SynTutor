"""Conservative Burton-Roberts (B-R) tree normalization and validation.

Benepar is a candidate parser, not a B-R authority.  This module only promotes
an analysis when the transformation is explicitly supported by the selected
chapter convention.  Everything else is returned as UNRESOLVED with the raw
candidate retained for diagnostics.

The chapter-tree importer is read-only: it projects the existing book-authored
JSON fixtures into the canonical envelope without modifying those fixtures.
"""
from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
import json
import re
from typing import Any

SCHEMA_VERSION = "1.0.0"
BOOK_TITLE = "Burton-Roberts, Analysing Sentences"
_EVIDENCE = {"IMG", "TXT", "DERIVED_FROM_INSTRUCTIONS", "IMG_ANOMALY",
             "NEEDS_REVIEW", "UNCERTAIN"}
_REVIEW = {"NOT_REVIEWED", "INDEPENDENTLY_REVIEWED", "HUMAN_APPROVED", "REJECTED"}
_ACCEPTANCE = {"ACCEPTED", "PREFERRED", "NOT_ACCEPTED", "NEEDS_REVIEW"}
_TOKEN_RE = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]", re.UNICODE)

# First chapter in which the label is available according to CONVENTIONS.md.
# Unknown labels are retained with a warning in imported gold records; they are
# never accepted as a Benepar-to-B-R mapping.
_LABEL_INTRODUCED = {
    "Sentence": 1, "Phrase": 1, "PHRASE": 1,
    "S": 2, "NP": 2, "VP": 2,
    "N": 3, "A": 3, "AP": 3, "DEG": 3, "Adv": 3,
    "AdvP": 3, "P": 3, "PP": 3, "name": 3, "pronoun": 3,
    "V": 4,
    "Prt": 5, "E": 5,
    "MOD": 6, "PERF": 6, "PROG": 6, "PASS": 6, "TENSE": 6,
    "S-bar": 6, "C": 6,
    "DET": 7, "ART": 7, "DEM": 7, "Q": 7, "POSS": 7,
    "PRE-DET": 7, "NOM": 7, "PartP": 7, "QA": 7,
    "S-dbar": 9, "C1": 9, "C2": 9,
    "AUX": 10, "V(I)": 10, "V(II)": 10,
}
_FEATURE_INTRODUCED = {
    "trans": 4, "intrans": 4, "ditrans": 4, "intens": 4,
    "complex": 4, "prep": 4,
    "phrasal": 5,
    "pres": 6, "past": 6,
    "-tense": 10,
}
_VERB_SUBCATEGORIES = {"trans", "intrans", "ditrans", "intens", "complex", "prep"}
_KNOWN_CANONICAL_PARSER_LABELS = {"S", "NP", "VP"}


def convention_profile(chapter: int | None = None,
                       appendix_nom: bool | None = None) -> dict[str, Any]:
    """Return the chapter profile or approved free-analysis profile.

    No chapter means the declared FINAL profile: V10 plus the Chapter 7
    Appendix D1 NOM refinement. Chapter lessons default to the chapter's core
    convention; Chapter 7 Appendix is opt-in.
    """
    if chapter is None:
        if appendix_nom is False:
            raise ValueError("appendix_nom=False cannot override the FINAL free-analysis profile")
        return {"chapter": 10, "version": "FINAL", "appendix_nom": True,
                "profile_id": "FINAL-D1"}
    if isinstance(chapter, bool) or not isinstance(chapter, int) or not 1 <= chapter <= 10:
        raise ValueError("chapter must be an integer from 1 through 10")
    if chapter != 7 and appendix_nom:
        raise ValueError("appendix_nom is only valid for Chapter 7 or the FINAL profile")
    profile = {"chapter": chapter, "version": f"V{chapter}"}
    if chapter == 7:
        enabled = bool(appendix_nom) if appendix_nom is not None else False
        profile["appendix_nom"] = enabled
        profile["profile_id"] = "V7-APPENDIX-D1" if enabled else "V7-CORE"
    else:
        profile["profile_id"] = f"V{chapter}"
    return profile


def _profile_errors(profile: Any) -> list[str]:
    if not isinstance(profile, dict):
        return ["convention_profile must be an object"]
    chapter = profile.get("chapter")
    version = profile.get("version")
    if isinstance(chapter, bool) or not isinstance(chapter, int) or not 1 <= chapter <= 10:
        return ["convention_profile.chapter must be an integer from 1 through 10"]
    expected = "FINAL" if chapter == 10 and version == "FINAL" else f"V{chapter}"
    if version != expected:
        return [f"convention_profile.version must be {expected} for chapter {chapter}"]
    if profile.get("appendix_nom") and not (chapter == 7 or version == "FINAL"):
        return ["appendix_nom is only valid for V7 or FINAL"]
    return []


def _stable_id(prefix: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _sentence_start(analysis: dict[str, Any]) -> int:
    rows = analysis.get("sentences") or []
    idx = analysis.get("sentence_index", 0)
    if isinstance(idx, int) and 0 <= idx < len(rows):
        return int(rows[idx].get("start", 0))
    return 0


def _candidate_tokens(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert parser token offsets to sentence-local canonical token records."""
    start = _sentence_start(analysis)
    result = []
    for i, token in enumerate(analysis.get("tokens") or []):
        char_start = int(token.get("start", start)) - start
        char_end = int(token.get("end", start)) - start
        result.append({
            "index": i,
            "text": str(token.get("t", "")),
            "char_span": [char_start, char_end],
            "pos": str(token.get("pos", "")),
            "parser_tag": str(token.get("tag", "")),
        })
    return result


def _raw_leaves(node: dict[str, Any]) -> list[dict[str, Any]]:
    children = node.get("children")
    if not children:
        return [node]
    out: list[dict[str, Any]] = []
    for child in children:
        out.extend(_raw_leaves(child))
    return out


def _is_raw_leaf(node: dict[str, Any]) -> bool:
    return isinstance(node, dict) and not node.get("children") and "surface" in node


def normalize_benepar_candidate(analysis: dict[str, Any],
                                profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize only a tightly supported V2 shell; otherwise fail unresolved.

    The currently approved adapter supports B-R V2's S -> NP VP skeleton when
    both NP and VP are left unanalyzed triangles and punctuation is absent.
    POS tags remain token metadata; they are not promoted to B-R phrase nodes.
    Later profiles need additional reviewed mappings (lexical categories,
    verbal features, auxiliary layers, NOM, clauses, gaps, indices and control).
    """
    profile = profile or convention_profile()
    errors = _profile_errors(profile)
    if errors:
        return {"status": "rejected", "tree": None,
                "reasons": [{"code": "INVALID_PROFILE", "detail": e} for e in errors],
                "normalization_trace": []}

    sentence = str(analysis.get("sentence", ""))
    tokens = _candidate_tokens(analysis)
    raw_root = analysis.get("root")
    parse_string = analysis.get("parse_string")
    reasons: list[dict[str, str]] = []
    trace: list[dict[str, Any]] = []

    if not isinstance(raw_root, dict):
        reasons.append({"code": "MISSING_PARSER_TREE", "detail": "Benepar did not provide a serializable candidate tree."})
    if profile.get("chapter") != 2:
        reasons.append({
            "code": "PROFILE_MAPPING_NOT_APPROVED",
            "detail": (f"The conservative Benepar adapter currently supports only the V2 S → NP VP shell; "
                       f"{profile.get('version')} requires mappings not yet source-verified."),
        })
    if reasons:
        return _unresolved_result(profile, reasons, trace, analysis, tokens)

    root = raw_root
    while (root.get("type") in {"ROOT", "TOP"}
           and isinstance(root.get("children"), list)
           and len(root["children"]) == 1):
        trace.append({"rule_id": "STRIP_SINGLE_PARSER_WRAPPER",
                      "from": root.get("type"), "to": root["children"][0].get("type"),
                      "evidence": "transport wrapper only; no linguistic node relabelled"})
        root = root["children"][0]

    if root.get("type") != "S":
        reasons.append({"code": "UNSUPPORTED_ROOT_LABEL",
                        "detail": f"Expected a B-R V2 S root; received {root.get('type')!r}."})
    children = root.get("children") or []
    child_labels = [c.get("type") for c in children if isinstance(c, dict)]
    if len(children) != 2 or child_labels != ["NP", "VP"]:
        reasons.append({"code": "UNSUPPORTED_V2_S_SHAPE",
                        "detail": "V2 promotion requires exactly S → NP VP; extra clauses, punctuation or other branches remain unresolved."})

    triangles = []
    if not reasons:
        for label, node in zip(("NP", "VP"), children):
            leaves = _raw_leaves(node)
            if not all(_is_raw_leaf(leaf) for leaf in leaves):
                reasons.append({"code": "UNANALYZED_PHRASE_REQUIRED",
                                "detail": f"The {label} candidate contains internal structure; V2 does not license a Penn-style relabelling of that structure."})
                continue
            words = [str(leaf.get("surface", "")) for leaf in leaves]
            if not words or any(not word for word in words):
                reasons.append({"code": "EMPTY_PHRASE", "detail": f"The {label} candidate has no overt terminal words."})
                continue
            if any(bool(leaf.get("punct")) for leaf in leaves):
                reasons.append({"code": "PUNCTUATION_POLICY_UNVERIFIED",
                                "detail": f"Punctuation occurs inside the {label} candidate; no B-R punctuation projection is approved here."})
                continue
            triangles.append({
