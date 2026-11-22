"""Read-only textbook-based H01 (Tracks 2-4) and H02 (Arm A vs Arm B) evaluation runner.

FROZEN EVALUATION V3 RULES (2026-11-22, S-dbar root + | alt-split fixes):
- Does NOT modify SynTutor production code, models, or grammar rules.
- Enforces a strict zero-call sentinel on burton_roberts._matching_gold_records
  during H01 Tracks 2-4 and returns [] during H02 Arm A so no published textbook
  gold tree can ever be retrieved to generate predictions.

H01 Tracks (four strictly separated measurements; never conflated):
  - Track 1 (Full-Tree PARSEVAL on 216+1 dev-exposed book diagrams): executed
    separately via `run_hypothesis_checks.py h01`.
  - Track 2 (Unseen Published-Reference Partial Relations): 16 unseen grammatical
    items (G01-G06, G16-G17, G25-G27, G36-G40) scored STRICTLY on the specific
    spans and structural attachment/containment relations explicitly published in
    Burton-Roberts (2011) Discussion of exercises, with explicit per-item
    `checked_relations` and `not_checked_relations` lists.
  - Track 3 (Unseen B-R Rule Compliance): all 50 unseen grammatical items.
  - Track 4 (Unseen Benepar->B-R Conversion Consistency): all 50 unseen items.

H02 Fair Outcome-Based Comparison (symmetrical across Arm A & Arm B):
  - Arm A: Unmodified production `analysis_api.build_payload(..., variety='standard_english')`.
  - Arm B: Functioning ungrounded neural/perturbation baseline using SynTutor's
    own RoBERTa-CoLA (`detector.classify`, native unthrottled binary verdict) and
    DistilBERT MLM (`corrector.sweep`) for exact-position localization & repair.
  - Primary fair outcomes (both arms can achieve 100%):
      O1: Correct grammatical judgment (abstentions strictly NOT counted as detected)
      O2: Exact position-aware target error localization (character-span overlap
          with resolved Affected words span; wrong occurrences & whole-sentence
          spans rejected)
      O3: Valid correction (matches Expected correction or any Valid alternatives)
      O4_no_incorrect_or_unsupported: Zero demonstrable errors (false positive,
          false negative grammatical certification, wrong-target localization,
          invalid rewrite, or self-contradiction)
      O4_decided_clean: O4 AND not abstained (prevents abstention-gaming)
  - Abstention rates are reported separately (overall, Grammatical n=50,
    Ungrammatical n=50) alongside strict ungrammatical detection recall and
    grammatical false-positive rate.
  - Separate Arm A descriptive grounding diagnostics (NEVER penalize Arm B):
      D1: Structured rule-family application accuracy
      D2: Structured evidence & provenance integrity
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from jsonschema import Draft202012Validator  # noqa: E402

SCHEMA_PATH = ROOT / "docs/canonical-burton-roberts-tree.schema.json"

FORBIDDEN_PENN_LABELS = {
    "SBAR", "SBARQ", "SQ", "SINV", "NP-SBJ", "WHNP", "WHADVP", "WHPP", "WHADJP",
    "NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
    "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "IN", "DT", "PRP", "PRP$", "MD",
    "CC", "TO", "WDT", "WP", "WP$", "WRB", "EX", "POS", "RP", "CD", "ADJP", "ADVP",
}

# Exact published partial Burton-Roberts (2011) Discussion-of-exercises relations
# for the 16 unseen Track 2 sentences. Every relation checked here is explicitly
# verified structurally; relations NOT established or NOT emitted (internal NP/PP
# subtrees, covert controller indices '•', lexical feature tags) are explicitly
# disclosed in `not_checked_relations`.
H01_PARTIAL_SPECS: dict[str, dict[str, Any]] = {
    "V3-G01": {
        "ref": "B-R Ch. 1 Ex. 4(a), p. 21",
        "required_spans": [
            {"name": "subject_np", "text": "John", "labels": {"NP"}},
            {"name": "gerund_constituent", "text": "visiting his great aunt", "labels": {"S-bar", "S'", "S", "NP", "VP"}},
        ],
        "not_checked_relations": ["Internal NP subtree of his great aunt", "Covert subject controller"],
    },
    "V3-G02": {
        "ref": "B-R Ch. 1 Ex. 4(f), p. 21",
        "required_spans": [
            {"name": "subject_np", "text": "Rory", "labels": {"NP"}},
            {"name": "direct_object", "text": "a silencer", "labels": {"NP"}},
            {"name": "locative_pp", "text": "on the gun", "labels": {"PP"}},
        ],
        "require_v_sister": [("put", "a silencer"), ("put", "on the gun")],
        "not_checked_relations": ["Internal NP/PP subtrees", "Verb subcategory feature tag [complex]"],
    },
    "V3-G03": {
        "ref": "B-R Ch. 4 Ex. 2(a), p. 83",
        "required_spans": [
            {"name": "subject_np", "text": "Holden", "labels": {"NP"}},
            {"name": "direct_object", "text": "ten letters", "labels": {"NP"}},
            {"name": "directional_pp", "text": "to Africa", "labels": {"PP"}},
        ],
        "require_v_sister": [("wrote", "ten letters")],
        "not_checked_relations": ["Internal NP/PP subtrees", "Animate vs inanimate PP adjunct disambiguation"],
    },
    "V3-G04": {
        "ref": "B-R Ch. 4 Ex. 2(c), p. 83",
        "required_spans": [
            {"name": "subject_np", "text": "Max", "labels": {"NP"}},
            {"name": "direct_object", "text": "the hyena", "labels": {"NP"}},
            {"name": "locative_pp", "text": "to the station", "labels": {"PP"}},
        ],
        "require_v_sister": [("took", "the hyena")],
        "not_checked_relations": ["Internal NP/PP subtrees", "Verb subcategory feature tag [complex]"],
    },
    "V3-G05": {
        "ref": "B-R Ch. 4 Ex. 2(h), p. 83",
        "required_spans": [
            {"name": "subject_np", "text": "Laura", "labels": {"NP"}},
            {"name": "direct_object", "text": "a place", "labels": {"NP"}},
            {"name": "benefactive_pp", "text": "for Martha", "labels": {"PP"}},
        ],
        "require_v_sister": [("saved", "a place"), ("saved", "for Martha")],
        "not_checked_relations": ["Internal NP/PP subtrees", "Verb subcategory feature tag [ditrans]"],
    },
    "V3-G06": {
        "ref": "B-R Ch. 5 Ex. 4(b), p. 107",
        "required_spans": [
            {"name": "subject_np", "text": "Hieronimo", "labels": {"NP"}},
            {"name": "subject_predicative", "text": "a veritable tyrant", "labels": {"NP"}},
        ],
        "require_v_sister": [("appeared", "a veritable tyrant")],
        "not_checked_relations": ["Internal NP subtree", "Verb subcategory feature tag [intens]"],
    },
    "V3-G12": {
        "ref": "B-R Ch. 4 Ex. 3 answer, p. 83",
        "required_spans": [
            {"name": "subject_np", "text": "The apprehensive butler", "labels": {"NP"}},
            {"name": "subject_predicative", "text": "rather strange", "labels": {"AP"}},
        ],
        "require_v_sister": [("smelt", "rather strange")],
        "not_checked_relations": ["Internal NP/AP subtrees", "Verb subcategory feature tag [intens]"],
    },
    "V3-G16": {
        "ref": "B-R Ch. 2 Ex. 6(b), p. 42",
        "required_spans": [
            {"name": "subject_np", "text": "The well-built gentleman", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "offered me a cigar", "labels": {"VP"}},
            {"name": "indirect_object", "text": "me", "labels": {"NP"}},
            {"name": "direct_object", "text": "a cigar", "labels": {"NP"}},
        ],
        "require_v_sister": [("offered", "me"), ("offered", "a cigar")],
        "not_checked_relations": ["Internal hyphenated modifier structure"],
    },
    "V3-G17": {
        "ref": "B-R Ch. 2 Ex. 6(d), p. 42",
        "required_spans": [
            {"name": "subject_np", "text": "People in running kit", "labels": {"NP"}},
            {"name": "modifier_pp", "text": "in running kit", "labels": {"PP"}},
            {"name": "predicate_vp", "text": "are coming from all directions", "labels": {"VP"}},
        ],
        "require_containment": ("People in running kit", "in running kit"),
        "not_checked_relations": ["Internal NP/PP subtrees"],
    },
    "V3-G18": {
        "ref": "B-R Ch. 2 Ex. 1(g), p. 41",
        "required_spans": [
            {"name": "fronted_adverbial", "text": "That evening", "labels": {"NP", "PP", "AdvP"}},
            {"name": "subject_np", "text": "Laura", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "learned the Health and Safety Regulations by heart", "labels": {"VP"}},
        ],
        "require_parent_label": [("That evening", {"S", "S-bar", "S'"})],
        "not_checked_relations": ["Internal coordinated NP subtree inside object"],
    },
    "V3-G20": {
        "ref": "B-R Ch. 9 Ex. 1(c), p. 218",
        "required_spans": [
            {"name": "wh_clause", "text": "Who was laughing", "labels": {"S-dbar", "S-bar", "S'", "S"}},
        ],
        "require_c_or_sbar": True,
        "not_checked_relations": ["Covert subject gap indexing"],
    },
    "V3-G21": {
        "ref": "B-R Ch. 9 Ex. 1(d), p. 218",
        "required_spans": [
            {"name": "wh_clause", "text": "What is a recidivist", "labels": {"S-dbar", "S-bar", "S'", "S"}},
            {"name": "subject_np", "text": "a recidivist", "labels": {"NP"}},
        ],
        "require_c_or_sbar": True,
        "not_checked_relations": ["Covert predicative gap indexing"],
    },
    "V3-G22": {
        "ref": "B-R Ch. 9 Ex. 1(e), p. 218",
        "required_spans": [
            {"name": "wh_clause", "text": "How arrogant can he get", "labels": {"S-dbar", "S-bar", "S'", "S"}},
            {"name": "subject_np", "text": "he", "labels": {"NP"}},
        ],
        "require_c_or_sbar": True,
        "not_checked_relations": ["Covert predicative AP gap indexing"],
    },
    "V3-G23": {
        "ref": "B-R Ch. 9 Ex. 1(g), p. 218",
        "required_spans": [
            {"name": "wh_clause", "text": "Why did Tessa pocket the fried egg", "labels": {"S-dbar", "S-bar", "S'", "S"}},
            {"name": "subject_np", "text": "Tessa", "labels": {"NP"}},
            {"name": "direct_object", "text": "the fried egg", "labels": {"NP"}},
        ],
        "require_c_or_sbar": True,
        "not_checked_relations": ["Covert wh-adjunct gap indexing"],
    },
    "V3-G24": {
        "ref": "B-R Ch. 9 Ex. 1(h), p. 218",
        "required_spans": [
            {"name": "wh_clause", "text": "Whose toothbrush did he clean his keyboard with", "labels": {"S-dbar", "S-bar", "S'", "S"}},
            {"name": "subject_np", "text": "he", "labels": {"NP"}},
            {"name": "direct_object", "text": "his keyboard", "labels": {"NP"}},
        ],
        "require_c_or_sbar": True,
        "not_checked_relations": ["Covert stranded-preposition gap indexing"],
    },
    "V3-G25": {
        "ref": "B-R Ch. 10 Ex. 1(viii), p. 249",
        "required_spans": [
            {"name": "subject_np", "text": "Max", "labels": {"NP"}},
            {"name": "nonfinite_clause", "text": "to talk", "labels": {"S-bar", "S'", "S", "VP"}},
        ],
        "not_checked_relations": ["Covert subject controller index"],
    },
    "V3-G36": {
        "ref": "B-R Ch. 1 Ex. 4(b), p. 21",
        "required_spans": [
            {"name": "subject_np", "text": "Maria", "labels": {"NP"}},
            {"name": "object_np", "text": "the bollard she had just demolished", "labels": {"NP"}},
            {"name": "relative_clause", "text": "she had just demolished", "labels": {"S-dbar", "S-bar", "S'", "S"}},
        ],
        "require_containment": ("the bollard she had just demolished", "she had just demolished"),
        "not_checked_relations": ["Covert object gap inside zero-relative clause"],
    },
}

INTERROGATIVE_H01_IDS = {"V3-G20", "V3-G21", "V3-G22", "V3-G23", "V3-G24", "V3-G33", "V3-G44", "V3-G45"}

CONTRACTION_PAIRS = [
    ("didn't", "did not"), ("doesn't", "does not"), ("don't", "do not"),
    ("wasn't", "was not"), ("weren't", "were not"), ("isn't", "is not"),
    ("aren't", "are not"), ("haven't", "have not"), ("hasn't", "has not"),
    ("hadn't", "had not"), ("won't", "will not"), ("can't", "cannot"),
    ("couldn't", "could not"), ("wouldn't", "would not"), ("shouldn't", "should not"),
    ("i'd", "i would"), ("he'd", "he would"), ("she'd", "she would"),
]


def _alnum_norm(text: str) -> str:
    s = (text or "").replace("\u2019", "'").replace("\u2018", "'").lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def _sentence_norm(text: str) -> str:
    s = (text or "").replace("\u2019", "'").replace("\u2018", "'").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([?.!,;:])", r"\1", s)
    s = s.rstrip(".?!")
    for short, full in CONTRACTION_PAIRS:
        s = re.sub(rf"\b{re.escape(short)}\b", full, s)
    return s.strip()


def _tree_yield_str(node: dict[str, Any]) -> str:
    if not isinstance(node, dict):
        return ""
    if "word" in node:
        return "" if node.get("elided") else str(node["word"])
    if node.get("triangle"):
        return " ".join(str(w) for w in node.get("words", []))
    parts = [_tree_yield_str(c) for c in node.get("children", [])]
    return " ".join(p for p in parts if p)


def _iter_tree_with_parent(node: dict[str, Any], parent: dict[str, Any] | None = None, depth: int = 0):
    """Yield (label, raw_yield, alnum_yield, depth, node, parent) for every node."""
    if not isinstance(node, dict):
        return
    label = str(node.get("label", ""))
    y = _tree_yield_str(node)
    yield label, y, _alnum_norm(y), depth, node, parent
    for child in node.get("children", []):
        yield from _iter_tree_with_parent(child, node, depth + 1)


def score_h01_partial(sentence_id: str, br_tree: dict[str, Any] | None) -> dict[str, Any]:
    """Track 2: Score ONLY the exact spans & structural relations explicitly established by B-R."""
    spec = H01_PARTIAL_SPECS[sentence_id]
    v_sisters = spec.get("require_v_sister") or []
    parent_reqs = spec.get("require_parent_label") or []
    vp_adj_reqs = spec.get("require_vp_adjunct_sister") or []

    checked_desc = [f"span({r['name']}: '{r['text']}' in {sorted(r['labels'])})" for r in spec["required_spans"]]
    checked_desc += [f"v_complement_sister('{v}', '{c}')" for v, c in v_sisters]
    checked_desc += [f"parent_attachment('{t}' under {sorted(p)})" for t, p in parent_reqs]
    checked_desc += [f"vp_adjunct_sister('{t}' sister of VP inside VP)" for t in vp_adj_reqs]
    if spec.get("require_c_or_sbar"):
        checked_desc.append("interrogative_c_or_sbar")
    if spec.get("require_containment"):
        o_t, i_t = spec["require_containment"]
        checked_desc.append(f"containment('{o_t}' dominates '{i_t}')")

    if not isinstance(br_tree, dict) or not isinstance(br_tree.get("root"), dict):
        return {
            "ref": spec["ref"], "eligible": True, "resolved": False,
            "passed": 0, "total": len(checked_desc), "rate": 0.0, "all_passed": False,
            "checked_relations": checked_desc,
            "not_checked_relations": spec.get("not_checked_relations", []),
            "checks": [{"name": "canonical_tree", "passed": False}],
        }

    nodes = list(_iter_tree_with_parent(br_tree["root"]))
    checks = []

    # 1. Exact span + category checks
    for req in spec["required_spans"]:
        target_an = _alnum_norm(req["text"])
        allowed = req["labels"]
        matched = any(lbl in allowed and an == target_an for lbl, _, an, _, _, _ in nodes)
        checks.append({"name": req["name"], "target": req["text"], "passed": matched})

    # 2. V-complement sisterhood inside VP (explicitly verifies sister-of-V attachment!)
    for verb_txt, comp_txt in v_sisters:
        v_an, c_an = _alnum_norm(verb_txt), _alnum_norm(comp_txt)
        ok = False
        for lbl, _, _, _, n, _ in nodes:
            if lbl != "VP":
                continue
            children = [c for c in n.get("children", []) if isinstance(c, dict)]
            has_v = any(c.get("label") == "V" and _alnum_norm(_tree_yield_str(c)) == v_an for c in children)
            has_c = any(_alnum_norm(_tree_yield_str(c)) == c_an for c in children)
            if has_v and has_c:
                ok = True
                break
        checks.append({"name": f"v_sister:{verb_txt}+{comp_txt}", "passed": ok})

    # 3. Parent-category attachment (e.g. S-adverbial attached directly under S/S', not VP)
    for target_txt, allowed_parents in parent_reqs:
        t_an = _alnum_norm(target_txt)
        ok = any(
            an == t_an and isinstance(par, dict) and str(par.get("label", "")) in allowed_parents
            for _, _, an, _, _, par in nodes
        )
        checks.append({"name": f"parent:{target_txt}", "passed": ok})

    # 4. VP-adjunct sisterhood (adjunct is sister of a lower VP inside a higher VP)
    for adj_txt in vp_adj_reqs:
        a_an = _alnum_norm(adj_txt)
        ok = False
        for lbl, _, _, _, n, _ in nodes:
            if lbl != "VP":
                continue
            children = [c for c in n.get("children", []) if isinstance(c, dict)]
            has_lower_vp = any(c.get("label") == "VP" for c in children)
            has_adj = any(_alnum_norm(_tree_yield_str(c)) == a_an and c.get("label") != "VP" for c in children)
            if has_lower_vp and has_adj:
                ok = True
                break
        checks.append({"name": f"vp_adjunct_sister:{adj_txt}", "passed": ok})

    # 5. Interrogative C / S-bar presence
    if spec.get("require_c_or_sbar"):
        has_c = any(lbl in {"S-bar", "S'", "C", "C1", "C2"} for lbl, _, _, _, _, _ in nodes)
        checks.append({"name": "interrogative_c_or_sbar", "passed": has_c})

    # 6. Clause/NP containment
    if spec.get("require_containment"):
        outer_t, inner_t = spec["require_containment"]
        outer_an, inner_an = _alnum_norm(outer_t), _alnum_norm(inner_t)
        contained = False
        for _, _, an, _, n, _ in nodes:
            if an == outer_an:
                sub = list(_iter_tree_with_parent(n))
                if any(san == inner_an and sn is not n for _, _, san, _, sn, _ in sub):
                    contained = True
                    break
        checks.append({"name": "clause_containment", "passed": contained})

    passed = sum(1 for c in checks if c["passed"])
    return {
        "ref": spec["ref"], "eligible": True, "resolved": True,
        "passed": passed, "total": len(checks),
        "rate": round(passed / len(checks), 4) if checks else 0.0,
        "all_passed": passed == len(checks),
        "checked_relations": checked_desc,
        "not_checked_relations": spec.get("not_checked_relations", []),
        "checks": checks,
    }


def score_h01_compliance(sentence_id: str, sentence: str, br_tree: dict[str, Any] | None) -> dict[str, Any]:
    """Track 3: Deterministic Burton-Roberts Ch. 1-10 rule compliance (never full-tree accuracy)."""
    if not isinstance(br_tree, dict) or not isinstance(br_tree.get("root"), dict):
        return {
            "resolved": False, "passed": 0, "total": 5, "rate": 0.0, "all_passed": False,
            "checks": {"canonical_labels_only": False, "valid_clause_root": False,
                       "nonempty_yield": False, "xbar_nom_valid": False, "interrogative_fronting": False},
        }
    root = br_tree["root"]
    nodes = list(_iter_tree_with_parent(root))
    labels = {lbl for lbl, _, _, _, _, _ in nodes if lbl}
    leaked = sorted(labels & FORBIDDEN_PENN_LABELS)
    canonical_labels_only = len(leaked) == 0
    valid_clause_root = root.get("label") in {"S", "S-bar", "S'", "S-dbar", "S\u2033", "Sentence"}
    yield_an = _alnum_norm(_tree_yield_str(root))
    nonempty_yield = bool(yield_an) and (yield_an == _alnum_norm(sentence))
    xbar_ok = True
    for lbl, _, _, _, n, _ in nodes:
        if lbl == "NP" and not n.get("triangle"):
            child_lbls = [c.get("label") for c in n.get("children", []) if isinstance(c, dict)]
            if "DET" in child_lbls and not any(x in {"NOM", "N", "NP"} for x in child_lbls):
                xbar_ok = False
                break
    interrog_ok = (
        any(lbl in {"S-bar", "S'", "C", "C1", "C2"} for lbl in labels)
        if sentence_id in INTERROGATIVE_H01_IDS else True
    )
    checks = {
        "canonical_labels_only": canonical_labels_only,
        "valid_clause_root": valid_clause_root,
        "nonempty_yield": nonempty_yield,
        "xbar_nom_valid": xbar_ok,
        "interrogative_fronting": interrog_ok,
    }
    passed = sum(1 for v in checks.values() if v)
    return {
        "resolved": True, "passed": passed, "total": len(checks),
        "rate": round(passed / len(checks), 4),
        "all_passed": passed == len(checks),
        "leaked_penn_labels": leaked,
        "checks": checks,
    }


def score_h01_conversion(sentence: str, br_analysis: dict[str, Any], validator: Draft202012Validator) -> dict[str, Any]:
    """Track 4: Benepar -> B-R conversion consistency (never reported as complete tree accuracy)."""
    status = str(br_analysis.get("status", "unresolved"))
    normalized = status == "normalized"
    tree = br_analysis.get("tree") if isinstance(br_analysis.get("tree"), dict) else None
    schema_valid = False
    yield_preserved = False
    if tree is not None:
        schema_valid = len(list(validator.iter_errors(tree))) == 0
        if isinstance(tree.get("root"), dict):
            yield_preserved = _alnum_norm(_tree_yield_str(tree["root"])) == _alnum_norm(sentence)
    return {
        "status": status, "normalized": normalized,
        "schema_valid": schema_valid, "yield_preserved": yield_preserved,
        "fully_consistent": normalized and schema_valid and yield_preserved,
    }


# ---------------------------------------------------------------------------
# Position-aware target character-span resolution (prevents bag-of-words false
# positives when a word like "the" or "have" appears multiple times!)
# ---------------------------------------------------------------------------
def _norm_quotes(s: str) -> str:
    return (s or "").replace("\u2019", "'").replace("\u2018", "'")


def resolve_target_char_spans(sentence: str, affected_words: str) -> list[tuple[int, int]]:
    """Resolve pre-registered Affected words into exact (start, end) char spans in sentence.

    Supports both contiguous phrases ('the from France', 'near I') and
    discontinuous pairs marked with '...' ('accuracy ... have').
    """
    raw_aff = _norm_quotes(affected_words).strip()
    if not raw_aff or raw_aff.lower() in {"none", "n/a"}:
        return []
    sent_norm = _norm_quotes(sentence)
    sent_low = sent_norm.lower()
    segments = [seg.strip() for seg in re.split(r"\.\.\.|…", raw_aff) if seg.strip()]
    spans: list[tuple[int, int]] = []
    cursor = 0
    for seg in segments:
        # Match as exact word-bounded substring (preserving punctuation like commas/apostrophes)
        pat = re.escape(seg.lower())
        # Add word boundaries at ends that are alphanumeric
        if re.match(r"^[a-z0-9]", seg.lower()):
            pat = r"(?<![a-z0-9])" + pat
        if re.search(r"[a-z0-9]$", seg.lower()):
            pat = pat + r"(?![a-z0-9])"
        m = re.search(pat, sent_low[cursor:])
        if m is None and cursor > 0:
            m = re.search(pat, sent_low)
            base = 0
        else:
            base = cursor
        if m is not None:
            s0, s1 = base + m.start(), base + m.end()
            spans.append((s0, s1))
            cursor = s1
    return spans


def _token_span_to_char_span(tok_span: Any, tokens: list[dict[str, Any]], sentence_offset: int) -> tuple[int, int] | None:
    """Convert [start_tok, end_tok] (exclusive or inclusive) into exact (char_start, char_end)."""
    if not isinstance(tok_span, (list, tuple)) or len(tok_span) != 2 or not tokens:
        return None
    try:
        i0, i1 = int(tok_span[0]), int(tok_span[1])
    except (TypeError, ValueError):
        return None
    if i0 < 0 or i0 >= len(tokens):
        return None
    # Handle exclusive end (typical: [i, i+1]) or inclusive end when i1 == i0
    end_idx = i0 if i1 <= i0 else min(i1 - 1, len(tokens) - 1)
    c0 = int(tokens[i0]["start"]) - sentence_offset
    c1 = int(tokens[end_idx]["end"]) - sentence_offset
    if c1 > c0 >= 0:
        return (c0, c1)
    return None


def _unique_surface_char_span(sentence: str, surface: str) -> tuple[int, int] | None:
    """Resolve surface text ONLY if it occurs at a unique position in sentence."""
    surf = _norm_quotes(surface).strip()
    if not surf:
        return None
    sent_low = _norm_quotes(sentence).lower()
    pat = re.escape(surf.lower())
    if re.match(r"^[a-z0-9]", surf.lower()):
        pat = r"(?<![a-z0-9])" + pat
    if re.search(r"[a-z0-9]$", surf.lower()):
        pat = pat + r"(?![a-z0-9])"
    matches = list(re.finditer(pat, sent_low))
    if len(matches) == 1:
        return (matches[0].start(), matches[0].end())
    return None


def _spans_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return max(a[0], b[0]) < min(a[1], b[1])


def _is_overly_broad_span(emitted: tuple[int, int], sentence_len: int, target_spans: list[tuple[int, int]]) -> bool:
    """Reject unlocalized whole-sentence spans when the true error target is localized."""
    if sentence_len <= 0:
        return False
    emitted_ratio = (emitted[1] - emitted[0]) / sentence_len
    target_len = sum(t1 - t0 for t0, t1 in target_spans)
    target_ratio = target_len / sentence_len
    return emitted_ratio > 0.65 and target_ratio <= 0.45


def _parse_valid_corrections(row: dict[str, str]) -> list[str]:
    if row["Grammatical status"].strip().lower() == "grammatical":
        return [_sentence_norm(row["Sentence text"])]
    out = []
    primary = (row.get("Expected correction") or "").strip()
    if primary and primary.lower() not in {"none", "n/a", "no correction required"}:
        out.append(_sentence_norm(primary))
    alts_raw = (row.get("Valid alternatives") or "").strip()
    if alts_raw and not alts_raw.lower().startswith(("none", "n/a")):
        for part in re.split(r"[;|]", alts_raw):
            cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", part).strip()
            if cleaned and not cleaned.lower().startswith(("none", "n/a")):
                out.append(_sentence_norm(cleaned))
    return list(dict.fromkeys(x for x in out if x))


def _extract_expected_rule_codes(rule_mapping: str) -> set[str]:
    return set(re.findall(r"\b(?:C-[A-Z0-9-]+|(?:CLS|COMP|MORPH|OTH|PHR|WCAT)-\d+)\b", rule_mapping or ""))


def _valid_node_ids(tree: dict[str, Any] | None) -> set[str]:
    if not isinstance(tree, dict) or not isinstance(tree.get("root"), dict):
        return set()
    ids = set()
    stack = [(tree["root"], "root")]
    while stack:
        node, path = stack.pop()
        if not isinstance(node, dict):
            continue
        ids.add(str(node.get("id") or path))
        for idx, ch in enumerate(node.get("children", [])):
            stack.append((ch, f"{path}.{idx}"))
    return ids


def extract_arm_a_packet(sentence: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize production Arm A build_payload() output with exact char spans."""
    summary = payload.get("summary") or {}
    parse_info = payload.get("parse") or {}
    tokens = parse_info.get("tokens") or []
    sentences = parse_info.get("sentences") or []
    sentence_offset = int(sentences[0]["start"]) if sentences and "start" in sentences[0] else 0

    details = payload.get("node_details") or payload.get("details") or {}
    unified = (payload.get("unified_findings") or {}).get("findings") or []
    learner = payload.get("learner_analysis") or {}
    cambridge = payload.get("cambridge_evaluation") or {}
    explanation = payload.get("explanation_evidence") or payload.get("explanation") or {}
    br_analysis = payload.get("br_analysis") or {}

    verdict = str(summary.get("verdict") or "unverified").lower()
    error_spans: list[tuple[int, int]] = []
    error_surfaces: list[str] = []
    fired_rules: set[str] = set()

    def _add_span(sp: tuple[int, int] | None, surf: str | None = None) -> None:
        if sp is not None and sp not in error_spans:
            error_spans.append(sp)
        if surf and surf not in error_surfaces:
            error_surfaces.append(surf)

    # 1. Unified legacy findings (exact token spans from findings.py)
    for uf in unified:
        if not isinstance(uf, dict) or uf.get("authority") != "legacy_matrix":
            continue
        if uf.get("rule_id"):
            fired_rules.add(str(uf["rule_id"]))
        sp = _token_span_to_char_span(uf.get("span"), tokens, sentence_offset)
        surf = str(uf["surface"]) if uf.get("surface") else None
        if sp is None and surf:
            sp = _unique_surface_char_span(sentence, surf)
        _add_span(sp, surf)

    # 2. node_details errors
    for d in details.values():
        if not isinstance(d, dict) or d.get("status") != "error":
            continue
        if d.get("constraint"):
            fired_rules.add(str(d["constraint"]))
        if d.get("rule_id"):
            fired_rules.add(str(d["rule_id"]))
        sp = _token_span_to_char_span(d.get("span"), tokens, sentence_offset)
        surf = str(d["surface"]) if d.get("surface") else None
        if sp is None and surf:
            sp = _unique_surface_char_span(sentence, surf)
        _add_span(sp, surf)

    # 3. Cambridge runtime findings (exact char_span or token_span)
    for cf in cambridge.get("findings") or []:
        if not isinstance(cf, dict):
            continue
        if cf.get("rule_id"):
            fired_rules.add(str(cf["rule_id"]))
        for sm in cf.get("structural_matches") or []:
            cs = sm.get("char_span") if isinstance(sm, dict) else None
            if isinstance(cs, (list, tuple)) and len(cs) == 2:
                _add_span((int(cs[0]), int(cs[1])))
        for cm in cf.get("candidate_matches") or []:
            if not isinstance(cm, dict):
                continue
            cs = cm.get("char_span")
            if isinstance(cs, (list, tuple)) and len(cs) == 2:
                _add_span((int(cs[0]), int(cs[1])), str(cm.get("surface") or "") or None)
            elif cm.get("surface"):
                _add_span(_unique_surface_char_span(sentence, str(cm["surface"])), str(cm["surface"]))
        for ms in cf.get("matched_sequences") or []:
            if isinstance(ms, dict):
                seq = " ".join(str(x) for x in (ms.get("sequence") or []))
                sp = _token_span_to_char_span(ms.get("token_span"), tokens, sentence_offset)
                if sp is None and seq:
                    sp = _unique_surface_char_span(sentence, seq)
                _add_span(sp, seq or None)

    for r in summary.get("constraints_fired") or []:
        if r:
            fired_rules.add(str(r))

    api_corr = summary.get("corrected_sentence")
    learner_corr = (learner.get("revision") or {}).get("text") if isinstance(learner.get("revision"), dict) else None
    primary_corr = learner_corr or api_corr

    # Separate Arm A descriptive provenance check (D2)
    tree = br_analysis.get("tree") if isinstance(br_analysis.get("tree"), dict) else None
    valid_ids = _valid_node_ids(tree)
    channel_valid = True
    anchor_valid = True
    channels = explanation.get("channels") if isinstance(explanation.get("channels"), dict) else {}
    for ch_name, items in channels.items():
        req_book = "B-R" if ch_name == "structural" else "Cambridge"
        for it in items or []:
            if not isinstance(it, dict):
                continue
            nid = it.get("node_id")
            if valid_ids and nid and nid not in valid_ids:
                anchor_valid = False
            for src in it.get("sources") or []:
                if isinstance(src, dict) and src.get("book") != req_book:
                    channel_valid = False

    return {
        "arm": "A_rule_grounded",
        "verdict": verdict,
        "error_spans": error_spans,
        "error_surfaces": error_surfaces,
        "correction": primary_corr,
        "api_correction": api_corr,
        "learner_correction": learner_corr,
        "fired_rules": sorted(fired_rules),
        "anchor_valid": anchor_valid,
        "channel_valid": channel_valid,
        "explanation_status": explanation.get("status"),
        "tree_status": br_analysis.get("status"),
    }


def run_arm_b_ungrounded(sentence: str, detector_mod: Any, corrector_mod: Any) -> dict[str, Any]:
    """Run Arm B: functioning ungrounded neural/perturbation baseline with exact char spans."""
    det = detector_mod.classify(sentence)
    if det is None or not det.get("available"):
        return {
            "arm": "B_ungrounded_neural", "verdict": "unverified",
            "error_spans": [], "error_surfaces": [], "correction": None,
            "detector": None, "perturbation": None, "anchor_valid": True,
        }
    verdict = "grammatical" if det["acceptable"] else "ungrammatical"
    error_spans: list[tuple[int, int]] = []
    error_surfaces: list[str] = []
    correction = None
    perturbation = None
    if not det["acceptable"]:
        loc = corrector_mod.sweep(sentence, detector_mod.classify_many)
        if loc is not None:
            perturbation = loc
            words = corrector_mod._words(sentence)
            pos = loc.get("position")
            if isinstance(pos, int) and 0 <= pos < len(words):
                m = words[pos]
                error_spans.append((m.start(), m.end()))
            elif loc.get("bad"):
                sp = _unique_surface_char_span(sentence, str(loc["bad"]))
                if sp is not None:
                    error_spans.append(sp)
            if loc.get("bad"):
                error_surfaces.append(str(loc["bad"]))
            if loc.get("corrected_text"):
                correction = str(loc["corrected_text"])
    return {
        "arm": "B_ungrounded_neural", "verdict": verdict,
        "error_spans": error_spans, "error_surfaces": error_surfaces,
        "correction": correction, "detector": det, "perturbation": perturbation,
        "anchor_valid": True,
    }


def score_h02_fair_outcomes(row: dict[str, str], packet: dict[str, Any]) -> dict[str, Any]:
    """Score O1-O4 fairly and identically for BOTH Arm A and Arm B.

    - Abstention is reported separately from successful error detection (O1) and
      from decided clean feedback (O4_decided_clean).
    - Localization (O2) requires exact character-span intersection with the
      resolved target span(s) of Affected words, rejecting wrong occurrences of
      repeated words and overly broad whole-sentence spans.
    """
    sentence = row["Sentence text"]
    is_gram = row["Grammatical status"].strip().lower() == "grammatical"
    verdict = str(packet.get("verdict") or "unverified").lower()
    raw_spans: list[tuple[int, int]] = [(int(sp[0]), int(sp[1])) for sp in (packet.get("error_spans") or []) if len(sp) == 2 and sp[1] > sp[0]]
    surfaces = [s for s in (packet.get("error_surfaces") or []) if str(s).strip()]
    # If a unit test provides surfaces without explicit spans, resolve ONLY unique occurrences
    if not raw_spans and surfaces:
        for s in surfaces:
            sp = _unique_surface_char_span(sentence, s)
            if sp is not None:
                raw_spans.append(sp)
    has_any_flag = bool(raw_spans) or bool(surfaces)

    correction = packet.get("correction")
    sent_norm = _sentence_norm(sentence)
    valid_corrs = _parse_valid_corrections(row)
    target_spans = resolve_target_char_spans(sentence, row.get("Affected words", ""))

    # O1: Correct Grammatical Judgment (abstentions strictly NOT counted as detected!)
    abstained = verdict in {"unverified", "unresolved"}
    o1 = (verdict == "grammatical") if is_gram else (verdict == "ungrammatical")
    detected_error = (not is_gram) and (verdict == "ungrammatical")

    # O2: Exact Position-Aware Target Localization
    overly_broad_only = False
    if is_gram:
        o2 = not has_any_flag
        wrong_target = has_any_flag
    else:
        localized_spans = [
            sp for sp in raw_spans
            if not _is_overly_broad_span(sp, len(sentence), target_spans)
        ]
        if raw_spans and not localized_spans:
            overly_broad_only = True
        hit_target = any(
            _spans_overlap(esp, tsp)
            for esp in localized_spans
            for tsp in target_spans
        )
        o2 = hit_target
        # Flagging a localized span that misses the actual target is a wrong-target error
        wrong_target = (bool(localized_spans) and not hit_target) or overly_broad_only

    # O3: Valid Correction
    corr_norm = _sentence_norm(correction) if correction else ""
    if is_gram:
        spurious_rewrite = bool(corr_norm) and (corr_norm != sent_norm)
        o3 = not spurious_rewrite
        invalid_rewrite = spurious_rewrite
    else:
        o3 = bool(corr_norm) and (corr_norm in valid_corrs)
        invalid_rewrite = bool(corr_norm) and (corr_norm not in valid_corrs)

    contradiction = (
        (verdict == "grammatical" and (has_any_flag or (bool(corr_norm) and corr_norm != sent_norm)))
        or (not packet.get("anchor_valid", True))
    )

    # O4: Absence of Demonstrably Incorrect or Unsupported Feedback
    if is_gram:
        demonstrable_error = (
            verdict == "ungrammatical"
            or has_any_flag
            or invalid_rewrite
            or contradiction
        )
    else:
        demonstrable_error = (
            verdict == "grammatical"
            or wrong_target
            or invalid_rewrite
            or contradiction
        )
    o4 = not demonstrable_error
    o4_decided_clean = o4 and (not abstained)

    # Fair composite (0-4): O1 + O2 + O3 + O4_decided_clean (prevents abstention-gaming!)
    composite_0_4 = int(o1) + int(o2) + int(o3) + int(o4_decided_clean)
    return {
        "O1_judgment": o1,
        "O2_localization": o2,
        "O3_correction": o3,
        "O4_no_incorrect_or_unsupported": o4,
        "O4_decided_clean": o4_decided_clean,
        "demonstrably_incorrect_or_unsupported": demonstrable_error,
        "full_outcome_adequacy": o1 and o2 and o3 and o4,
        "fair_composite_0_4": composite_0_4,
        "abstained": abstained,
        "detected_ungrammatical": detected_error,
        "false_positive_on_grammatical": is_gram and (verdict == "ungrammatical" or has_any_flag or invalid_rewrite),
        "wrong_target": wrong_target,
        "overly_broad_span": overly_broad_only,
        "invalid_rewrite": invalid_rewrite,
        "contradiction": contradiction,
        "resolved_target_spans": target_spans,
        "non_matching_correction": correction if (not is_gram and bool(corr_norm) and not o3) else None,
    }


def score_h02_grounding_diagnostics(row: dict[str, str], arm_a_packet: dict[str, Any]) -> dict[str, Any]:
    """Separate Arm A descriptive diagnostics D1 & D2 (never used to penalize Arm B)."""
    is_gram = row["Grammatical status"].strip().lower() == "grammatical"
    fired = set(arm_a_packet.get("fired_rules") or [])
    expected_codes = _extract_expected_rule_codes(row.get("SynTutor rule mapping", ""))
    d1_rule_ok = (len(fired) == 0) if is_gram else (bool(fired & expected_codes) if expected_codes else bool(fired))
    d2_provenance_ok = bool(arm_a_packet.get("anchor_valid", True)) and bool(arm_a_packet.get("channel_valid", True))
    return {
        "D1_rule_family_match": d1_rule_ok,
        "D2_provenance_integrity": d2_provenance_ok,
        "expected_rule_codes": sorted(expected_codes),
        "fired_rules": sorted(fired),
    }


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> dict[str, float]:
    if n == 0:
        return {"k": 0, "n": 0, "rate": 0.0, "ci_low": 0.0, "ci_high": 0.0}
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / denom
    return {"k": k, "n": n, "rate": round(p, 4),
            "ci_low": round(max(0.0, center - half), 4),
            "ci_high": round(min(1.0, center + half), 4)}


def exact_mcnemar(a_pass: list[bool], b_pass: list[bool]) -> dict[str, Any]:
    assert len(a_pass) == len(b_pass)
    n11 = sum(1 for a, b in zip(a_pass, b_pass) if a and b)
    n10 = sum(1 for a, b in zip(a_pass, b_pass) if a and not b)
    n01 = sum(1 for a, b in zip(a_pass, b_pass) if not a and b)
    n00 = sum(1 for a, b in zip(a_pass, b_pass) if not a and not b)
    m = n10 + n01
    if m == 0:
        p_val = 1.0
    else:
        lo = min(n10, n01)
        p_val = min(1.0, 2.0 * sum(math.comb(m, i) * (0.5 ** m) for i in range(lo + 1)))
    n = len(a_pass)
    return {
        "n": n, "n11": n11, "n10_arm_a_wins": n10, "n01_arm_b_wins": n01, "n00": n00,
        "arm_a_rate": round((n11 + n10) / n, 4) if n else 0.0,
        "arm_b_rate": round((n11 + n01) / n, 4) if n else 0.0,
        "net_diff": round((n10 - n01) / n, 4) if n else 0.0,
        "p_value_exact_two_sided": round(p_val, 6),
    }


def paired_wilcoxon_signed_rank(a_scores: list[float], b_scores: list[float]) -> dict[str, Any]:
    diffs = [a - b for a, b in zip(a_scores, b_scores)]
    nz = [d for d in diffs if d != 0]
    n_nz = len(nz)
    if n_nz == 0:
        return {"n_nonzero": 0, "w_pos": 0.0, "w_neg": 0.0, "mean_diff": 0.0, "rank_biserial_r": 0.0, "p_value_approx": 1.0}
    abs_sorted = sorted((abs(d), d > 0) for d in nz)
    ranks = []
    i = 0
    tie_corr = 0.0
    while i < n_nz:
        j = i
        while j < n_nz and abs_sorted[j][0] == abs_sorted[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        t = j - i
        tie_corr += t * (t * t - 1)
        for k in range(i, j):
            ranks.append((avg_rank, abs_sorted[k][1]))
        i = j
    w_pos = sum(r for r, pos in ranks if pos)
    w_neg = sum(r for r, pos in ranks if not pos)
    total_r = n_nz * (n_nz + 1) / 2.0
    r_rb = (w_pos - w_neg) / total_r
    mean_w = total_r / 2.0
    var_w = (n_nz * (n_nz + 1) * (2 * n_nz + 1) - tie_corr / 2.0) / 24.0
    if var_w <= 0:
        p_val = 1.0
    else:
        z = (abs(w_pos - mean_w) - 0.5) / math.sqrt(var_w)
        p_val = math.erfc(max(0.0, z) / math.sqrt(2.0))
    return {
        "n_nonzero": n_nz, "w_pos": round(w_pos, 2), "w_neg": round(w_neg, 2),
        "mean_diff": round(sum(diffs) / len(diffs), 4),
        "rank_biserial_r": round(r_rb, 4),
        "p_value_approx": round(p_val, 6),
    }


def _arm_breakdown(h02_rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    """Explicitly separate abstention rates from detection and false-positive rates."""
    gram = [r[key] for r in h02_rows if r["Grammatical status"].lower() == "grammatical"]
    ungram = [r[key] for r in h02_rows if r["Grammatical status"].lower() != "grammatical"]
    all_sc = [r[key] for r in h02_rows]
    return {
        "overall_abstention_rate": wilson_ci(sum(1 for s in all_sc if s["abstained"]), len(all_sc)),
        "grammatical_acceptance_rate": wilson_ci(sum(1 for s in gram if s["O1_judgment"]), len(gram)),
        "grammatical_false_positive_rate": wilson_ci(sum(1 for s in gram if s["false_positive_on_grammatical"]), len(gram)),
        "grammatical_abstention_rate": wilson_ci(sum(1 for s in gram if s["abstained"]), len(gram)),
        "ungrammatical_error_detection_rate": wilson_ci(sum(1 for s in ungram if s["detected_ungrammatical"]), len(ungram)),
        "ungrammatical_abstention_rate": wilson_ci(sum(1 for s in ungram if s["abstained"]), len(ungram)),
        "ungrammatical_missed_as_grammatical_rate": wilson_ci(
            sum(1 for s in ungram if (not s["detected_ungrammatical"]) and (not s["abstained"])), len(ungram)
        ),
        "ungrammatical_target_localization_rate": wilson_ci(sum(1 for s in ungram if s["O2_localization"]), len(ungram)),
        "ungrammatical_valid_correction_rate": wilson_ci(sum(1 for s in ungram if s["O3_correction"]), len(ungram)),
    }


def run_evaluation(csv_path: Path, output_dir: Path) -> dict[str, Any]:
    """Execute H01 Tracks 2-4 and H02 Arm A vs Arm B with strict zero-lookup enforcement."""
    import analysis_api
    import burton_roberts as br
    import corrector
    import detector
    import parse_engine

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_bytes = csv_path.read_bytes()
    csv_sha256 = hashlib.sha256(csv_bytes).hexdigest()
    rows = list(csv.DictReader(csv_bytes.decode("utf-8").splitlines()))
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))

    h01_rows = []
    h02_rows = []
    non_matching_audit = []

    # 1. H01 Tracks 2-4: strict zero-call sentinel on _matching_gold_records
    with patch.object(
        br, "_matching_gold_records",
        side_effect=AssertionError("Gold textbook lookup attempted during H01!"),
    ) as h01_lookup_sentinel:
        for row in rows:
            sid = row["Sentence ID"]
            text = row["Sentence text"]
            if row["Grammatical status"].strip().lower() != "grammatical":
                continue
            parsed = parse_engine.analyze(text)
            try:
                br_an = br.normalize_benepar_candidate(parsed, br.convention_profile())
            except Exception as exc:
                br_an = {
                    "status": "unresolved", "tree": None,
                    "reasons": [{"code": "NORMALIZER_FAILURE",
                                 "detail": f"B-R normalization failed safely: {type(exc).__name__}: {exc}"}],
                }
            br_tree = br_an.get("tree") if br_an.get("status") == "normalized" else None
            conv = score_h01_conversion(text, br_an, validator)
            comp = score_h01_compliance(sid, text, br_tree)
            part = score_h01_partial(sid, br_tree) if sid in H01_PARTIAL_SPECS else None
            h01_rows.append({
                "Sentence ID": sid, "Difficulty": row["Difficulty"], "Sentence text": text,
                "track2_partial_ref": part,
                "track3_br_compliance": comp,
                "track4_conversion": conv,
            })
        if h01_lookup_sentinel.called:
            raise AssertionError("Gold textbook lookup sentinel was triggered during H01!")

    # 2. H02 Arm A vs Arm B: force _matching_gold_records -> [] for Arm A
    with patch.object(br, "_matching_gold_records", return_value=[]):
        for row in rows:
            sid = row["Sentence ID"]
            text = row["Sentence text"]
            payload_a = analysis_api.build_payload(text, variety="standard_english")
            pkt_a = extract_arm_a_packet(text, payload_a)
            sc_a = score_h02_fair_outcomes(row, pkt_a)
            diag_a = score_h02_grounding_diagnostics(row, pkt_a)

            pkt_b = run_arm_b_ungrounded(text, detector, corrector)
            sc_b = score_h02_fair_outcomes(row, pkt_b)

            if sc_a["non_matching_correction"] or sc_b["non_matching_correction"]:
                non_matching_audit.append({
                    "Sentence ID": sid, "Sentence text": text,
                    "Expected correction": row["Expected correction"],
                    "Valid alternatives": row["Valid alternatives"],
                    "Arm_A_correction": pkt_a["correction"] or "",
                    "Arm_B_correction": pkt_b["correction"] or "",
                })

            h02_rows.append({
                "Sentence ID": sid, "Pair ID": row["Pair ID"],
                "Grammatical status": row["Grammatical status"], "Difficulty": row["Difficulty"],
                "Sentence text": text,
                "arm_a_packet": pkt_a, "arm_a_fair": sc_a, "arm_a_grounding_diag": diag_a,
                "arm_b_packet": pkt_b, "arm_b_fair": sc_b,
            })

    t2_rows = [r for r in h01_rows if r["track2_partial_ref"] is not None]
    h01_summary = {
        "note": "Track 1 (216+1 dev-exposed full-tree PARSEVAL) is run separately via run_hypothesis_checks.py h01.",
        "track2_unseen_partial_published_relations": {
            "scope_disclaimer": (
                "Measures ONLY the specific constituent spans, V-complement sisterhood, "
                "VP-adjunct/S-adverbial attachments, and overt clause boundaries explicitly "
                "published in B-R Discussion of exercises (pp. 82, 105, 218-220, 249-251). "
                "Does NOT measure internal unprinted subtrees, covert traces/controllers, or complete-tree accuracy."
            ),
            "n": len(t2_rows),
            "all_checked_relations_passed": wilson_ci(
                sum(1 for r in t2_rows if r["track2_partial_ref"]["all_passed"]), len(t2_rows)
            ),
            "total_checked_relations_passed": wilson_ci(
                sum(r["track2_partial_ref"]["passed"] for r in t2_rows),
                sum(r["track2_partial_ref"]["total"] for r in t2_rows),
            ),
            "mean_item_relation_rate": round(
                sum(r["track2_partial_ref"]["rate"] for r in t2_rows) / len(t2_rows), 4
            ) if t2_rows else 0.0,
        },
        "track3_unseen_br_compliance": {
            "scope_disclaimer": "Deterministic B-R structural rule compliance only; NOT gold syntax-tree accuracy.",
            "n": len(h01_rows),
            "all_passed": wilson_ci(sum(1 for r in h01_rows if r["track3_br_compliance"]["all_passed"]), len(h01_rows)),
        },
        "track4_unseen_conversion": {
            "scope_disclaimer": "Benepar->B-R canonical conversion consistency only; NOT gold syntax-tree accuracy.",
            "n": len(h01_rows),
            "fully_consistent": wilson_ci(sum(1 for r in h01_rows if r["track4_conversion"]["fully_consistent"]), len(h01_rows)),
            "by_difficulty": {
                diff: wilson_ci(
                    sum(1 for r in h01_rows if r["Difficulty"] == diff and r["track4_conversion"]["fully_consistent"]),
                    sum(1 for r in h01_rows if r["Difficulty"] == diff),
                )
                for diff in ("Simple", "Moderate", "Complex")
            },
        },
    }

    h02_summary = {
        "primary_fair_comparison": {
            "O4_no_incorrect_or_unsupported": exact_mcnemar(
                [r["arm_a_fair"]["O4_no_incorrect_or_unsupported"] for r in h02_rows],
                [r["arm_b_fair"]["O4_no_incorrect_or_unsupported"] for r in h02_rows],
            ),
            "O4_decided_clean_non_abstaining": exact_mcnemar(
                [r["arm_a_fair"]["O4_decided_clean"] for r in h02_rows],
                [r["arm_b_fair"]["O4_decided_clean"] for r in h02_rows],
            ),
            "O1_judgment": exact_mcnemar(
                [r["arm_a_fair"]["O1_judgment"] for r in h02_rows],
                [r["arm_b_fair"]["O1_judgment"] for r in h02_rows],
            ),
            "O2_target_localization": exact_mcnemar(
                [r["arm_a_fair"]["O2_localization"] for r in h02_rows],
                [r["arm_b_fair"]["O2_localization"] for r in h02_rows],
            ),
            "O3_valid_correction": exact_mcnemar(
                [r["arm_a_fair"]["O3_correction"] for r in h02_rows],
                [r["arm_b_fair"]["O3_correction"] for r in h02_rows],
            ),
            "full_outcome_adequacy": exact_mcnemar(
                [r["arm_a_fair"]["full_outcome_adequacy"] for r in h02_rows],
                [r["arm_b_fair"]["full_outcome_adequacy"] for r in h02_rows],
            ),
            "fair_composite_0_4_wilcoxon": paired_wilcoxon_signed_rank(
                [r["arm_a_fair"]["fair_composite_0_4"] for r in h02_rows],
                [r["arm_b_fair"]["fair_composite_0_4"] for r in h02_rows],
            ),
        },
        "abstention_and_detection_breakdown": {
            "arm_a_rule_grounded": _arm_breakdown(h02_rows, "arm_a_fair"),
            "arm_b_ungrounded_neural": _arm_breakdown(h02_rows, "arm_b_fair"),
        },
        "separate_arm_a_grounding_diagnostics": {
            "note": "Reported independently; NEVER included in primary Arm A vs Arm B comparison.",
            "D1_rule_family_match": wilson_ci(
                sum(1 for r in h02_rows if r["arm_a_grounding_diag"]["D1_rule_family_match"]), len(h02_rows)
            ),
            "D2_provenance_integrity": wilson_ci(
                sum(1 for r in h02_rows if r["arm_a_grounding_diag"]["D2_provenance_integrity"]), len(h02_rows)
            ),
        },
    }

    report = {
        "csv_path": str(csv_path), "csv_sha256": csv_sha256, "total_rows": len(rows),
        "gold_lookup_sentinel_verified_zero_calls": True,
        "h01": h01_summary, "h02": h02_summary,
    }
    (output_dir / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "h01_details.json").write_text(json.dumps(h01_rows, indent=2), encoding="utf-8")
    (output_dir / "h02_details.json").write_text(json.dumps(h02_rows, indent=2), encoding="utf-8")
    if non_matching_audit:
        with (output_dir / "non_matching_corrections_audit.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(non_matching_audit[0].keys()))
            w.writeheader()
            w.writerows(non_matching_audit)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    report = run_evaluation(args.csv_path, args.output_dir)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
