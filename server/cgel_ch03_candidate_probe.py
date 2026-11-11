"""Chapter 3 Phase-C typed-evidence candidate checker, deliberately NOT a live detector.

The extracted Cambridge source rules are currently spec_only with unverified
Burton-Roberts crosswalks. This offline probe accepts explicitly typed candidate
relations for engineering tests. It never converts candidate evidence into a
verified grammar verdict or exports an enable-list entry.

A validated B-R tree by itself does not license the supplied relation labels.
Connecting a parser-backed, independently checked relation extractor is a
separate prerequisite before any production integration.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]", re.UNICODE)
MODALS = frozenset({"can", "could", "may", "might", "must",
                    "shall", "should", "will", "would"})
SUPPORT_DO = frozenset({"do", "does", "did", "don't", "doesn't", "didn't",
                        "don’t", "doesn’t", "didn’t"})
SUPPORTED = ("COMP-034", "COMP-031", "CLS-100")
SUPPORTING = {"CLS-100": ("COMP-030",)}
RULE_FILES = {"COMP-034": "complementation", "COMP-031": "complementation",
              "CLS-100": "clauses"}
KINDS = {"modal_selects", "supportive_do_selects"}
CLAUSES = {"declarative", "closed_interrogative", "emphatic_declarative",
           "imperative", "other"}


def tokens_with_spans(sentence: str) -> list[dict[str, Any]]:
    """Index exact source spans; never normalize the string used for edits."""
    return [
        {"index": i, "text": match.group(0),
         "lower": match.group(0).casefold().replace("’", "'"),
         "char_span": [match.start(), match.end()]}
        for i, match in enumerate(TOKENS.finditer(sentence))
    ]


def _source_rules(root: Path) -> dict[str, dict[str, Any]]:
    files = {}
    for file_name in sorted(set(RULE_FILES.values())):
        path = root / "grammar" / "rules" / f"{file_name}.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"{file_name}: expected rule list")
        files[file_name] = {rule.get("id"): rule for rule in rows}
    chosen = {}
    for rid in SUPPORTED:
        rule = files[RULE_FILES[rid]].get(rid)
        if not isinstance(rule, dict):
            raise ValueError(f"{rid}: source record missing")
        if rule.get("rule_type") not in {"constraint", "variety_restricted"}:
            raise ValueError(f"{rid}: not an error-capable rule")
        diagnostic = rule.get("diagnostic")
        if not isinstance(diagnostic, dict) or diagnostic.get("detector") != "spec_only":
            raise ValueError(f"{rid}: expected non-active specification")
        if not diagnostic.get("false_positive_guards"):
            raise ValueError(f"{rid}: missing false-positive guards")
        sources = [source for source in rule.get("sources", [])
                   if source.get("chapter") == 3
                   and "cambridge" in str(source.get("book", "")).lower()]
        if not sources or not all(source.get("pages") for source in sources):
            raise ValueError(f"{rid}: Chapter 3 source evidence missing")
        if rule.get("status") != "NEEDS_REVIEW":
            raise ValueError(f"{rid}: unexpected approval lifecycle change")
        chosen[rid] = rule
    # Reject a stale or unlinked overlapping error specification.
    clauses = files["clauses"]["CLS-100"]
    if "COMP-030" not in clauses.get("related_rules", []):
        raise ValueError("Missing CLS-100/COMP-030 de-duplication cross-link")
    return chosen


def _typed_relation(relation: Any, tokens: list[dict[str, Any]]) -> bool:
    if not isinstance(relation, dict):
        return False
    for field in ("governor", "dependent"):
        value = relation.get(field)
        if type(value) is not int or value < 0 or value >= len(tokens):
            return False
    if relation["governor"] == relation["dependent"]:
        return False
    if relation.get("kind") not in KINDS or relation.get("clause_kind") not in CLAUSES:
        return False
    # Explicit typed selection, within one clause, and not coordinated.
    if relation.get("direct_selection") is not True:
        return False
    if relation.get("same_clause") is not True:
        return False
    if relation.get("coordinated") is not False:
        return False
    return True


def _rule_for(relation: dict[str, Any], tokens: list[dict[str, Any]]) -> str | None:
    governor, dependent = tokens[relation["governor"]], tokens[relation["dependent"]]
    g, d = governor["lower"], dependent["lower"]
    kind = relation["kind"]
    if kind == "modal_selects":
        if relation.get("governor_role") != "central_modal" or g not in MODALS:
            return None
        if relation.get("dependent_role") == "central_modal" and d in MODALS:
            return "COMP-031"
        if (relation.get("dependent_role") == "lexical_verb"
                and relation.get("dependent_form") == "present_3sg"
                and d.isalpha() and d.endswith("s")):
            return "COMP-034"
        if (relation.get("dependent_role") == "infinitival_marker"
                and relation.get("dependent_form") == "infinitival_to" and d == "to"):
            # Require separate evidence for the plain lexical verb after to.
            j = relation.get("infinitival_verb")
            if (type(j) is int and j > relation["dependent"] and j < len(tokens)
                    and relation.get("infinitival_verb_form") == "plain"
                    and tokens[j]["lower"].isalpha()):
                return "COMP-034"
        return None
    if kind == "supportive_do_selects":
        if relation.get("governor_role") != "supportive_do" or g not in SUPPORT_DO:
            return None
        if relation.get("clause_kind") == "imperative":
            return None
        if relation.get("dependent_role") == "perfect_have":
            return "CLS-100" if d in {"have", "has", "had"} else None
        if relation.get("dependent_role") in {"progressive_be", "passive_be", "copular_be"}:
            return "CLS-100" if d in {"be", "been", "being", "am", "is", "are", "was", "were"} else None
        if relation.get("dependent_role") == "central_modal":
            return "CLS-100" if d in MODALS else None
    return None


def _candidate_edit(relation: dict[str, Any], tokens: list[dict[str, Any]],
                    rule_id: str, sentence: str) -> dict[str, Any] | None:
    """Hints only: edits are never applied or asserted to preserve meaning."""
    if rule_id != "COMP-034":
        return None
    dependent = tokens[relation["dependent"]]
    if relation.get("dependent_form") == "infinitival_to":
        start, end = dependent["char_span"]
        if start > 0 and sentence[start - 1] == " ":
            start -= 1
        return {"char_span": [start, end], "replacement": "",
                "requires_reparse": True, "safe_to_apply_automatically": False}
    base = relation.get("candidate_plain_form")
    if (relation.get("dependent_form") == "present_3sg"
            and isinstance(base, str)
            and re.fullmatch(r"[A-Za-z]+", base)
            and base.casefold() != dependent["lower"]):
        return {"char_span": dependent["char_span"], "replacement": base,
                "requires_reparse": True, "safe_to_apply_automatically": False}
    return None


def probe_ch03(sentence: Any, typed_facts: Any, *,
               variety: str | None, root: Path | None = None) -> dict[str, Any]:
    """Inspect explicit typed *candidate* relations, never free-form raw words.

    Production rule activation must still pass the Cambridge registry's separate
    independent review, B-R crosswalk, test and approval gates.
    """
    base = {
        "status": "candidate_only",
        "authority": "TYPED_EVIDENCE_NOT_INDEPENDENTLY_VERIFIED",
        "production_enabled": False,
        "whole_sentence_certified": False,
        "candidates": [], "blocked": [],
    }
    if not isinstance(sentence, str) or not sentence.strip():
        return {**base, "status": "not_evaluated", "blocked": ["invalid_sentence"]}
    if not isinstance(variety, str) or not variety.strip():
        return {**base, "status": "not_evaluated", "blocked": ["explicit_variety_required"]}
    # Non-standard English dialects must not inherit standard double-modal bans.
    if variety.strip().casefold() not in {"standard_english", "standard written english"}:
        return {**base, "status": "not_evaluated", "blocked": ["unassessed_english_variety"]}
    if not isinstance(typed_facts, dict) or typed_facts.get("status") != "typed_candidate":
        return {**base, "status": "not_evaluated", "blocked": ["typed_relations_required"]}
    if typed_facts.get("sentence") != sentence or not isinstance(typed_facts.get("relations"), list):
        return {**base, "status": "not_evaluated", "blocked": ["candidate_sentence_mismatch"]}
    rules = _source_rules(root or ROOT)
    tokens = tokens_with_spans(sentence)
    seen = set()
    for index, relation in enumerate(typed_facts["relations"]):
        if not _typed_relation(relation, tokens):
            base["blocked"].append({"relation_index": index, "reason": "missing_or_invalid_typed_evidence"})
            continue
        rid = _rule_for(relation, tokens)
        if not rid:
            continue
        gov = tokens[relation["governor"]]
        dep = tokens[relation["dependent"]]
        key = (rid, relation["governor"], relation["dependent"])
        if key in seen:
            continue
        seen.add(key)
        source = rules[rid]
        pages = sorted({p for s in source["sources"] if s.get("chapter") == 3
                        for p in s.get("pages", [])})
        char_start = min(gov["char_span"][0], dep["char_span"][0])
        char_end = max(gov["char_span"][1], dep["char_span"][1])
        base["candidates"].append({
            "rule_id": rid,
            "supporting_rule_ids": list(SUPPORTING.get(rid, ())),
            "family": source["diagnostic"]["error_family"],
            "status": "needs_linguistic_validation",
            "relation": {
                "kind": relation["kind"],
                "governor_token_index": gov["index"],
                "dependent_token_index": dep["index"],
                "governor_char_span": gov["char_span"],
                "dependent_char_span": dep["char_span"],
            },
            "token_span": [min(gov["index"], dep["index"]),
                           max(gov["index"], dep["index"]) + 1],
            "char_span": [char_start, char_end],
            "evidence_tokens": [gov["text"], dep["text"]],
            "source_pages": pages,
            "source_chapter": 3,
            "variety_scope": source["diagnostic"]["variety_scope"],
            "provisional_explanation": source["diagnostic"]["learner_explanation"],
            "edit_hint": _candidate_edit(relation, tokens, rid, sentence),
        })
    return base
