"""Read-only textbook-based H01 (Tracks 2-4) and H02 (Arm A vs Arm B) evaluation runner.

Does NOT modify SynTutor production code, models, or grammar rules.
Enforces a zero-call sentinel on burton_roberts._matching_gold_records so no
published gold-tree lookup can ever generate predictions.

H01 Tracks (four separate measurements; never conflated):
  - Track 1 (Full-Tree PARSEVAL on 216+1 dev-exposed book diagrams): run via
    existing `run_hypothesis_checks.py h01`.
  - Track 2 (Unseen Published-Reference Agreement): 16 unseen grammatical items
    (G01-G06, G16-G17, G25-G27, G36-G40) scored strictly on structural relations
    explicitly published in Burton-Roberts (2011) Discussion of exercises.
  - Track 3 (Unseen B-R Rule Compliance): all 50 unseen grammatical items.
  - Track 4 (Unseen Benepar->B-R Conversion Consistency): all 50 unseen items.

H02 Fair Outcome-Based Comparison (symmetrical across Arm A & Arm B):
  - Arm A: Unmodified production `analysis_api.build_payload(..., variety='standard_english')`.
  - Arm B: Functioning ungrounded neural/perturbation baseline using SynTutor's
    own RoBERTa-CoLA (`detector.classify`, native unthrottled verdict) and
    DistilBERT MLM (`corrector.sweep`) for localization and correction.
  - Primary fair outcomes (both arms can score 100%):
      O1: Correct grammatical judgment
      O2: Correct error localization (overlap with pre-registered Affected words)
      O3: Valid correction (matches Expected correction or any Valid alternatives)
      O4: Absence of demonstrably incorrect or unsupported feedback (primary)
  - Separate grounding diagnostics (reported independently for Arm A; never
    penalize Arm B in primary H02 tests):
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
from collections import Counter
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from jsonschema import Draft202012Validator  # noqa: E402

SCHEMA_PATH = ROOT / "docs/canonical-burton-roberts-tree.schema.json"

# Raw Penn Treebank tags that must NEVER leak into a canonical Burton-Roberts tree.
FORBIDDEN_PENN_LABELS = {
    "SBAR", "SBARQ", "SQ", "SINV", "NP-SBJ", "WHNP", "WHADVP", "WHPP", "WHADJP",
    "NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
    "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "IN", "DT", "PRP", "PRP$", "MD",
    "CC", "TO", "WDT", "WP", "WP$", "WRB", "EX", "POS", "RP", "CD", "ADJP", "ADVP",
}

# Exact published partial Burton-Roberts (2011) Discussion-of-exercises structural
# invariants for the 16 unseen Track 2 sentences (pp. 82, 105, 218-220, 249-251).
# Each entry lists ONLY spans/relations explicitly established by the textbook.
H01_PARTIAL_SPECS: dict[str, dict[str, Any]] = {
    "G01": {
        "ref": "B-R Ch. 4 Ex. 1(b), p. 82",
        "required_spans": [
            {"name": "subject_np", "text": "Hot air", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "rises", "labels": {"VP"}},
        ],
    },
    "G02": {
        "ref": "B-R Ch. 4 Ex. 1(e), p. 82",
        "required_spans": [
            {"name": "subject_np", "text": "Someone", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "stole my contact-lenses", "labels": {"VP"}},
            {"name": "direct_object", "text": "my contact-lenses", "labels": {"NP"}},
        ],
    },
    "G03": {
        "ref": "B-R Ch. 4 Ex. 1(c), p. 82",
        "required_spans": [
            {"name": "subject_np", "text": "Richard", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "promised me his spaghetti machine", "labels": {"VP"}},
            {"name": "indirect_object", "text": "me", "labels": {"NP"}},
            {"name": "direct_object", "text": "his spaghetti machine", "labels": {"NP"}},
        ],
    },
    "G04": {
        "ref": "B-R Ch. 4 Ex. 1(d), p. 82",
        "required_spans": [
            {"name": "subject_np", "text": "The sedan-chair", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "proved very useful", "labels": {"VP"}},
            {"name": "subject_predicative", "text": "very useful", "labels": {"AP"}},
        ],
    },
    "G05": {
        "ref": "B-R Ch. 4 Ex. 1(m), p. 82",
        "required_spans": [
            {"name": "subject_np", "text": "He", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "applied for a gun licence", "labels": {"VP"}},
            {"name": "prep_complement", "text": "for a gun licence", "labels": {"PP"}},
        ],
    },
    "G06": {
        "ref": "B-R Ch. 4 Ex. 1(a), p. 82",
        "required_spans": [
            {"name": "subject_np", "text": "The girl in the palace", "labels": {"NP"}},
            {"name": "predicate_vp", "text": "dyed her hair deep purple", "labels": {"VP"}},
            {"name": "direct_object", "text": "her hair", "labels": {"NP"}},
            {"name": "object_predicative", "text": "deep purple", "labels": {"AP"}},
        ],
    },
    "G16": {
        "ref": "B-R Ch. 5 Ex. 1(g), p. 105",
        "required_spans": [
            {"name": "subject_np", "text": "Murdstone", "labels": {"NP"}},
            {"name": "direct_object", "text": "the child", "labels": {"NP"}},
            {"name": "vp_adjunct", "text": "too strictly", "labels": {"AdvP"}},
            {"name": "s_adverbial", "text": "in my opinion", "labels": {"PP"}},
        ],
    },
    "G17": {
        "ref": "B-R Ch. 5 Ex. 1(h), p. 105",
        "required_spans": [
            {"name": "subject_np", "text": "Few students", "labels": {"NP"}},
            {"name": "prep_complement", "text": "about exams", "labels": {"PP"}},
            {"name": "vp_adjunct", "text": "until the end of term", "labels": {"PP"}},
        ],
        "require_nested_vp": True,
    },
    "G25": {
        "ref": "B-R Ch. 9 Ex. 1(a), p. 218",
        "required_spans": [
            {"name": "wh_fronted_clause", "text": "What shall we feed the cat today", "labels": {"S-bar", "S'", "S"}},
            {"name": "subject_np", "text": "we", "labels": {"NP"}},
            {"name": "indirect_object", "text": "the cat", "labels": {"NP"}},
        ],
        "require_c_or_sbar": True,
    },
    "G26": {
        "ref": "B-R Ch. 9 Ex. 2(b), p. 218",
        "required_spans": [
            {"name": "matrix_object_np", "text": "the officer who issued this ridiculous order", "labels": {"NP"}},
            {"name": "relative_clause", "text": "who issued this ridiculous order", "labels": {"S-bar", "S'", "S"}},
        ],
        "require_containment": ("the officer who issued this ridiculous order", "who issued this ridiculous order"),
    },
    "G27": {
        "ref": "B-R Ch. 10 Ex. 1(iii), p. 249",
        "required_spans": [
            {"name": "subject_np", "text": "Morgan", "labels": {"NP"}},
            {"name": "nonfinite_clause", "text": "to give it a good review", "labels": {"S-bar", "S'", "S", "VP"}},
        ],
    },
    "G36": {
        "ref": "B-R Ch. 9 Ex. 4(a), p. 219 (ACA)",
        "required_spans": [
            {"name": "s2_wh_interrog", "text": "how the theory worked", "labels": {"S-bar", "S'", "S"}},
            {"name": "s3_until_clause", "text": "I read your book", "labels": {"S-bar", "S'", "S"}},
        ],
    },
    "G37": {
        "ref": "B-R Ch. 9 Ex. 4(b), p. 219 (ACA)",
        "required_spans": [
            {"name": "s2_subject_clause", "text": "Why Max didn't answer the accusation that he had cheated", "labels": {"S-bar", "S'", "S"}},
            {"name": "s3_noun_comp", "text": "that he had cheated", "labels": {"S-bar", "S'", "S"}},
        ],
        "require_containment": ("Why Max didn't answer the accusation that he had cheated", "that he had cheated"),
    },
    "G38": {
        "ref": "B-R Ch. 9 Ex. 4(d), p. 220 (ACA)",
        "required_spans": [
            {"name": "s2_nonrestr_rel", "text": "who is injured", "labels": {"S-bar", "S'", "S"}},
            {"name": "s3_adj_comp", "text": "that the high-wire is strengthened if it is used again", "labels": {"S-bar", "S'", "S"}},
            {"name": "s4_cond_clause", "text": "if it is used again", "labels": {"S-bar", "S'", "S"}},
        ],
        "require_containment": ("that the high-wire is strengthened if it is used again", "if it is used again"),
    },
    "G39": {
        "ref": "B-R Ch. 10 Ex. 3(i), p. 250 (ACA)",
        "required_spans": [
            {"name": "s2_appear_comp", "text": "to have been eager to join the Crusade", "labels": {"S-bar", "S'", "S", "VP"}},
            {"name": "s3_eager_comp", "text": "to join the Crusade", "labels": {"S-bar", "S'", "S", "VP"}},
        ],
        "require_containment": ("to have been eager to join the Crusade", "to join the Crusade"),
    },
    "G40": {
        "ref": "B-R Ch. 10 Ex. 3(iii), p. 251 (ACA)",
        "required_spans": [
            {"name": "s2_plans_comp", "text": "to recover the vehicles abandoned during the night", "labels": {"S-bar", "S'", "S", "VP"}},
            {"name": "s3_participle_rel", "text": "abandoned during the night", "labels": {"S-bar", "S'", "S", "VP"}},
        ],
        "require_containment": ("to recover the vehicles abandoned during the night", "abandoned during the night"),
    },
}

INTERROGATIVE_H01_IDS = {"G18", "G22", "G25", "G28", "G43", "G44", "G45"}

# Contraction equivalences for fair multi-alternative correction comparison.
CONTRACTION_PAIRS = [
    ("didn't", "did not"),
    ("doesn't", "does not"),
    ("don't", "do not"),
    ("wasn't", "was not"),
    ("weren't", "were not"),
    ("isn't", "is not"),
    ("aren't", "are not"),
    ("haven't", "have not"),
    ("hasn't", "has not"),
    ("hadn't", "had not"),
    ("won't", "will not"),
    ("can't", "cannot"),
    ("couldn't", "could not"),
    ("wouldn't", "would not"),
    ("shouldn't", "should not"),
    ("i'd", "i would"),
    ("he'd", "he would"),
    ("she'd", "she would"),
]


def _alnum_norm(text: str) -> str:
    """Character-only lowercase normalization (resilient to contraction/hyphen splits)."""
    s = (text or "").replace("\u2019", "'").replace("\u2018", "'").lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def _sentence_norm(text: str) -> str:
    """Normalize sentence text for fair multi-alternative correction comparison."""
    s = (text or "").replace("\u2019", "'").replace("\u2018", "'").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([?.!,;:])", r"\1", s)
    s = s.rstrip(".?!")
    for short, full in CONTRACTION_PAIRS:
        s = re.sub(rf"\b{re.escape(short)}\b", full, s)
    return s.strip()


def _content_tokens(text: str) -> set[str]:
    s = (text or "").replace("\u2019", "'").replace("\u2018", "'").lower()
    return set(re.findall(r"[a-z0-9']+", s))


def _tree_yield_str(node: dict[str, Any]) -> str:
    if not isinstance(node, dict):
        return ""
    if "word" in node:
        return "" if node.get("elided") else str(node["word"])
    if node.get("triangle"):
        return " ".join(str(w) for w in node.get("words", []))
    parts = [_tree_yield_str(c) for c in node.get("children", [])]
    return " ".join(p for p in parts if p)


def _iter_tree_spans(node: dict[str, Any], depth: int = 0):
    """Yield (label, raw_yield_str, alnum_yield, depth, node) for every node."""
    if not isinstance(node, dict):
        return
    label = str(node.get("label", ""))
    y = _tree_yield_str(node)
    yield label, y, _alnum_norm(y), depth, node
    for child in node.get("children", []):
        yield from _iter_tree_spans(child, depth + 1)


def score_h01_partial(sentence_id: str, br_tree: dict[str, Any] | None) -> dict[str, Any]:
    """Track 2: Score ONLY relations explicitly established by Burton-Roberts."""
    spec = H01_PARTIAL_SPECS[sentence_id]
    total_checks = len(spec["required_spans"]) + int(bool(spec.get("require_nested_vp"))) \
        + int(bool(spec.get("require_c_or_sbar"))) + int(bool(spec.get("require_containment")))
    if not isinstance(br_tree, dict) or not isinstance(br_tree.get("root"), dict):
        return {
            "ref": spec["ref"], "eligible": True, "resolved": False,
            "passed": 0, "total": total_checks, "rate": 0.0, "all_passed": False,
            "checks": [{"name": "canonical_tree", "passed": False}],
        }
    nodes = list(_iter_tree_spans(br_tree["root"]))
    checks = []
    for req in spec["required_spans"]:
        target_an = _alnum_norm(req["text"])
        allowed = req["labels"]
        matched = any(lbl in allowed and an == target_an for lbl, _, an, _, _ in nodes)
        checks.append({"name": req["name"], "target": req["text"], "passed": matched})

    if spec.get("require_nested_vp"):
        nested_vp = any(
            lbl == "VP" and any(c.get("label") == "VP" for c in n.get("children", []) if isinstance(c, dict))
            for lbl, _, _, _, n in nodes
        )
        checks.append({"name": "nested_vp_adjunct", "passed": nested_vp})

    if spec.get("require_c_or_sbar"):
        has_c = any(lbl in {"S-bar", "S'", "C", "C1", "C2"} for lbl, _, _, _, _ in nodes)
        checks.append({"name": "interrogative_c_or_sbar", "passed": has_c})

    if spec.get("require_containment"):
        outer_t, inner_t = spec["require_containment"]
        outer_an, inner_an = _alnum_norm(outer_t), _alnum_norm(inner_t)
        contained = False
        for _, _, an, _, n in nodes:
            if an == outer_an:
                sub = list(_iter_tree_spans(n))
                if any(san == inner_an and sn is not n for _, _, san, _, sn in sub):
                    contained = True
                    break
        checks.append({"name": "clause_containment", "passed": contained})

    passed = sum(1 for c in checks if c["passed"])
    return {
        "ref": spec["ref"], "eligible": True, "resolved": True,
        "passed": passed, "total": len(checks),
        "rate": round(passed / len(checks), 4) if checks else 0.0,
        "all_passed": passed == len(checks),
        "checks": checks,
    }


def score_h01_compliance(sentence_id: str, sentence: str, br_tree: dict[str, Any] | None) -> dict[str, Any]:
    """Track 3: Deterministic Burton-Roberts Ch. 1-10 rule compliance (no gold tree invented)."""
    if not isinstance(br_tree, dict) or not isinstance(br_tree.get("root"), dict):
        return {
            "resolved": False, "passed": 0, "total": 5, "rate": 0.0, "all_passed": False,
            "checks": {"canonical_labels_only": False, "valid_clause_root": False,
                       "nonempty_yield": False, "xbar_nom_valid": False, "interrogative_fronting": False},
        }
    root = br_tree["root"]
    nodes = list(_iter_tree_spans(root))
    labels = {lbl for lbl, _, _, _, _ in nodes if lbl}
    leaked = sorted(labels & FORBIDDEN_PENN_LABELS)
    canonical_labels_only = len(leaked) == 0
    valid_clause_root = root.get("label") in {"S", "S-bar", "S'", "Sentence"}
    yield_an = _alnum_norm(_tree_yield_str(root))
    nonempty_yield = bool(yield_an) and (yield_an == _alnum_norm(sentence))
    # X-bar check: every non-pronoun, non-triangle NP that has a DET child should have NOM or N
    xbar_ok = True
    for lbl, _, _, _, n in nodes:
        if lbl == "NP" and not n.get("triangle"):
            child_lbls = [c.get("label") for c in n.get("children", []) if isinstance(c, dict)]
            if "DET" in child_lbls and not any(x in {"NOM", "N", "NP"} for x in child_lbls):
                xbar_ok = False
                break
    if sentence_id in INTERROGATIVE_H01_IDS:
        interrog_ok = any(lbl in {"S-bar", "S'", "C", "C1", "C2"} for lbl in labels)
    else:
        interrog_ok = True

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
    """Track 4: Benepar -> B-R conversion consistency (never reported as tree accuracy)."""
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
        "status": status,
        "normalized": normalized,
        "schema_valid": schema_valid,
        "yield_preserved": yield_preserved,
        "fully_consistent": normalized and schema_valid and yield_preserved,
    }


def _parse_valid_corrections(row: dict[str, str]) -> list[str]:
    """Return all normalized valid corrections (Expected correction + Valid alternatives)."""
    if row["Grammatical status"].strip().lower() == "grammatical":
        return [_sentence_norm(row["Sentence text"])]
    out = []
    primary = (row.get("Expected correction") or "").strip()
    if primary and primary.lower() not in {"none", "n/a", "no correction required"}:
        out.append(_sentence_norm(primary))
    alts_raw = (row.get("Valid alternatives") or "").strip()
    if alts_raw and not alts_raw.lower().startswith(("none", "n/a")):
        for part in alts_raw.split(";"):
            cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", part).strip()
            if cleaned and not cleaned.lower().startswith(("none", "n/a")):
                out.append(_sentence_norm(cleaned))
    return list(dict.fromkeys(x for x in out if x))


def _extract_expected_rule_codes(rule_mapping: str) -> set[str]:
    """Extract all pre-registered SynTutor rule IDs from CSV SynTutor rule mapping."""
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


def extract_arm_a_packet(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize production Arm A build_payload() output into the common fair outcome schema."""
    summary = payload.get("summary") or {}
    details = payload.get("details") or {}
    learner = payload.get("learner_analysis") or {}
    cambridge = payload.get("cambridge_evaluation") or {}
    explanation = payload.get("explanation") or payload.get("shared_explanation_evidence") or {}
    br_analysis = payload.get("br_analysis") or {}

    verdict = str(summary.get("verdict") or "unverified").lower()
    # Collect localized error tokens/surfaces from all active error channels
    error_surfaces = []
    fired_rules = set()
    for d in details.values():
        if isinstance(d, dict) and d.get("status") == "error":
            if d.get("surface"):
                error_surfaces.append(str(d["surface"]))
            if d.get("constraint"):
                fired_rules.add(str(d["constraint"]))
            if d.get("rule_id"):
                fired_rules.add(str(d["rule_id"]))
    for f in learner.get("findings") or []:
        if isinstance(f, dict):
            for key in ("surface", "word", "target", "span_text"):
                if f.get(key):
                    error_surfaces.append(str(f[key]))
            for key in ("rule_id", "constraint", "code"):
                if f.get(key):
                    fired_rules.add(str(f[key]))
    for cf in cambridge.get("findings") or []:
        if isinstance(cf, dict):
            if cf.get("rule_id"):
                fired_rules.add(str(cf["rule_id"]))
            for ms in cf.get("matched_sequences") or []:
                if isinstance(ms, dict) and ms.get("sequence"):
                    error_surfaces.append(" ".join(str(x) for x in ms["sequence"]))
            for cm in cf.get("candidate_matches") or []:
                if isinstance(cm, dict) and cm.get("surface"):
                    error_surfaces.append(str(cm["surface"]))
    for r in summary.get("constraints_fired") or []:
        if r:
            fired_rules.add(str(r))

    api_corr = summary.get("corrected_sentence")
    learner_corr = (learner.get("revision") or {}).get("text") if isinstance(learner.get("revision"), dict) else None
    primary_corr = learner_corr or api_corr

    # Check structured provenance integrity (D2 — reported separately, never penalizes Arm B)
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
        "error_surfaces": list(dict.fromkeys(error_surfaces)),
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
    """Run Arm B: functioning ungrounded neural/perturbation baseline (CoLA + DistilBERT MLM).

    Uses native unthrottled CoLA acceptability classification (no 0.20 advisory
    throttle) and DistilBERT MLM perturbation sweep for localization & repair.
    """
    det = detector_mod.classify(sentence)
    if det is None or not det.get("available"):
        return {
            "arm": "B_ungrounded_neural",
            "verdict": "unverified",
            "error_surfaces": [],
            "correction": None,
            "detector": None,
            "perturbation": None,
            "anchor_valid": True,
        }
    verdict = "grammatical" if det["acceptable"] else "ungrammatical"
    error_surfaces = []
    correction = None
    perturbation = None
    if not det["acceptable"]:
        loc = corrector_mod.sweep(sentence, detector_mod.classify_many)
        if loc is not None:
            perturbation = loc
            if loc.get("bad"):
                error_surfaces.append(str(loc["bad"]))
            if loc.get("corrected_text"):
                correction = str(loc["corrected_text"])
    return {
        "arm": "B_ungrounded_neural",
        "verdict": verdict,
        "error_surfaces": error_surfaces,
        "correction": correction,
        "detector": det,
        "perturbation": perturbation,
        "anchor_valid": True,
    }


def score_h02_fair_outcomes(row: dict[str, str], packet: dict[str, Any]) -> dict[str, Any]:
    """Score O1-O4 fairly and identically for BOTH Arm A and Arm B.

    NEVER requires structured rule IDs or Cambridge provenance metadata, so Arm B
    is never disadvantaged simply for having rule grounding disabled.
    """
    is_gram = row["Grammatical status"].strip().lower() == "grammatical"
    verdict = str(packet.get("verdict") or "unverified").lower()
    surfaces = [s for s in (packet.get("error_surfaces") or []) if str(s).strip()]
    correction = packet.get("correction")
    sent_norm = _sentence_norm(row["Sentence text"])
    valid_corrs = _parse_valid_corrections(row)
    affected_tokens = _content_tokens(row.get("Affected words", ""))
    emitted_tokens = set()
    for s in surfaces:
        emitted_tokens |= _content_tokens(s)

    # O1: Correct Grammatical Judgment
    if is_gram:
        o1 = verdict == "grammatical"
    else:
        o1 = verdict == "ungrammatical"
    abstained = verdict in {"unverified", "unresolved"}

    # O2: Correct Error Localization
    if is_gram:
        o2 = len(surfaces) == 0
        wrong_target = len(surfaces) > 0
    else:
        overlap = bool(affected_tokens & emitted_tokens)
        o2 = overlap
        wrong_target = (len(emitted_tokens) > 0) and (not overlap)

    # O3: Valid Correction
    corr_norm = _sentence_norm(correction) if correction else ""
    if is_gram:
        spurious_rewrite = bool(corr_norm) and (corr_norm != sent_norm)
        o3 = not spurious_rewrite
        invalid_rewrite = spurious_rewrite
    else:
        o3 = bool(corr_norm) and (corr_norm in valid_corrs)
        invalid_rewrite = bool(corr_norm) and (corr_norm not in valid_corrs)

    # Internal contradiction check (applicable symmetrically to both arms)
    contradiction = (
        (verdict == "grammatical" and (len(surfaces) > 0 or (bool(corr_norm) and corr_norm != sent_norm)))
        or (not packet.get("anchor_valid", True))
    )

    # O4: Absence of Demonstrably Incorrect or Unsupported Feedback (Primary H02 Endpoint)
    # Note: Principled abstention (unverified, no false flag, no invalid rewrite) is NOT a
    # demonstrable error on O4, while false-positive error, false-negative 'grammatical'
    # certification on an ungrammatical item, wrong-target localization, invalid rewrite,
    # or self-contradiction IS a demonstrable error.
    if is_gram:
        demonstrable_error = (
            verdict == "ungrammatical"
            or len(surfaces) > 0
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

    composite_0_4 = int(o1) + int(o2) + int(o3) + int(o4)
    return {
        "O1_judgment": o1,
        "O2_localization": o2,
        "O3_correction": o3,
        "O4_no_incorrect_or_unsupported": o4,
        "demonstrably_incorrect_or_unsupported": demonstrable_error,
        "full_outcome_adequacy": o1 and o2 and o3 and o4,
        "fair_composite_0_4": composite_0_4,
        "abstained": abstained,
        "wrong_target": wrong_target,
        "invalid_rewrite": invalid_rewrite,
        "contradiction": contradiction,
        "non_matching_correction": correction if (not is_gram and bool(corr_norm) and not o3) else None,
    }


def score_h02_grounding_diagnostics(row: dict[str, str], arm_a_packet: dict[str, Any]) -> dict[str, Any]:
    """Separate Arm A descriptive diagnostics D1 & D2 (never used to penalize Arm B)."""
    is_gram = row["Grammatical status"].strip().lower() == "grammatical"
    fired = set(arm_a_packet.get("fired_rules") or [])
    expected_codes = _extract_expected_rule_codes(row.get("SynTutor rule mapping", ""))
    if is_gram:
        d1_rule_ok = len(fired) == 0
    else:
        d1_rule_ok = bool(fired & expected_codes) if expected_codes else bool(fired)
    d2_provenance_ok = bool(arm_a_packet.get("anchor_valid", True)) and bool(arm_a_packet.get("channel_valid", True))
    return {
        "D1_rule_family_match": d1_rule_ok,
        "D2_provenance_integrity": d2_provenance_ok,
        "expected_rule_codes": sorted(expected_codes),
        "fired_rules": sorted(fired),
    }


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> dict[str, float]:
    if n == 0:
        return {"rate": 0.0, "ci_low": 0.0, "ci_high": 0.0}
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / denom
    return {"rate": round(p, 4), "ci_low": round(max(0.0, center - half), 4),
            "ci_high": round(min(1.0, center + half), 4)}


def exact_mcnemar(a_pass: list[bool], b_pass: list[bool]) -> dict[str, Any]:
    """Exact two-sided McNemar test on paired binary pass outcomes."""
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
    """Paired Wilcoxon signed-rank test (normal approximation with tie correction)."""
    diffs = [a - b for a, b in zip(a_scores, b_scores)]
    nz = [d for d in diffs if d != 0]
    n_nz = len(nz)
    if n_nz == 0:
        return {"n_nonzero": 0, "w_pos": 0.0, "w_neg": 0.0, "rank_biserial_r": 0.0, "p_value_approx": 1.0}
    abs_sorted = sorted((abs(d), d > 0) for d in nz)
    # Assign average ranks for ties
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


def run_evaluation(csv_path: Path, output_dir: Path) -> dict[str, Any]:
    """Execute H01 Tracks 2-4 and H02 Arm A vs Arm B with strict zero-lookup sentinel."""
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

    # 1. H01 Tracks 2-4: strict zero-call sentinel on _matching_gold_records.
    with patch.object(
        br, "_matching_gold_records",
        side_effect=AssertionError("Gold textbook lookup attempted during H01!"),
    ) as h01_lookup_sentinel:
        for row in rows:
            sid = row["Sentence ID"]
            text = row["Sentence text"]
            is_gram = row["Grammatical status"].strip().lower() == "grammatical"
            if not is_gram:
                continue
            parsed = parse_engine.analyze(text)
            br_an = br.normalize_benepar_candidate(parsed, br.convention_profile())
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

    # 2. H02 Arm A vs Arm B: force _matching_gold_records -> [] so build_payload()
    # can NEVER retrieve a published textbook tree for Arm A.
    with patch.object(br, "_matching_gold_records", return_value=[]):
        for row in rows:
            sid = row["Sentence ID"]
            text = row["Sentence text"]
            payload_a = analysis_api.build_payload(text, variety="standard_english")
            pkt_a = extract_arm_a_packet(payload_a)
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

    # Aggregate H01 Tracks 2-4
    t2_rows = [r for r in h01_rows if r["track2_partial_ref"] is not None]
    h01_summary = {
        "note": "Track 1 (216+1 dev-exposed full-tree PARSEVAL) is run separately via run_hypothesis_checks.py h01.",
        "track2_unseen_partial_ref": {
            "n": len(t2_rows),
            "all_passed": sum(1 for r in t2_rows if r["track2_partial_ref"]["all_passed"]),
            "all_passed_ci": wilson_ci(sum(1 for r in t2_rows if r["track2_partial_ref"]["all_passed"]), len(t2_rows)),
            "mean_relation_rate": round(sum(r["track2_partial_ref"]["rate"] for r in t2_rows) / len(t2_rows), 4) if t2_rows else 0.0,
        },
        "track3_unseen_br_compliance": {
            "n": len(h01_rows),
            "all_passed": sum(1 for r in h01_rows if r["track3_br_compliance"]["all_passed"]),
            "all_passed_ci": wilson_ci(sum(1 for r in h01_rows if r["track3_br_compliance"]["all_passed"]), len(h01_rows)),
        },
        "track4_unseen_conversion": {
            "n": len(h01_rows),
            "fully_consistent": sum(1 for r in h01_rows if r["track4_conversion"]["fully_consistent"]),
            "fully_consistent_ci": wilson_ci(sum(1 for r in h01_rows if r["track4_conversion"]["fully_consistent"]), len(h01_rows)),
            "by_difficulty": {
                diff: wilson_ci(
                    sum(1 for r in h01_rows if r["Difficulty"] == diff and r["track4_conversion"]["fully_consistent"]),
                    sum(1 for r in h01_rows if r["Difficulty"] == diff),
                )
                for diff in ("Simple", "Moderate", "Complex")
            },
        },
    }

    # Aggregate H02 Fair Comparison (Arm A vs Arm B) + Separate Grounding Diagnostics
    h02_summary = {
        "primary_fair_comparison": {
            "O4_no_incorrect_or_unsupported": exact_mcnemar(
                [r["arm_a_fair"]["O4_no_incorrect_or_unsupported"] for r in h02_rows],
                [r["arm_b_fair"]["O4_no_incorrect_or_unsupported"] for r in h02_rows],
            ),
            "O1_judgment": exact_mcnemar(
                [r["arm_a_fair"]["O1_judgment"] for r in h02_rows],
                [r["arm_b_fair"]["O1_judgment"] for r in h02_rows],
            ),
            "O2_localization": exact_mcnemar(
                [r["arm_a_fair"]["O2_localization"] for r in h02_rows],
                [r["arm_b_fair"]["O2_localization"] for r in h02_rows],
            ),
            "O3_correction": exact_mcnemar(
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
