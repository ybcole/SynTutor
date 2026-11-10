"""XAI-4 typed, narrow English morphology observations; NOT a grammar oracle.

The four XAI-PRE Cambridge source claims await human review. The public
evaluator must never expose a candidate VIOLATED as a verified diagnosis.
Raw tokens remain distinct from canonical B-R node IDs.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "xai4-partial-1.0.0"
TOKEN_RE = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]", re.UNICODE)
HAVE = {"have", "has", "had"}
BE = {"am", "is", "are", "was", "were", "be", "been", "being"}
MODAL = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
SKIP = {"already", "just", "never", "not", "often", "always", "recently", "still"}
PAST = {"went", "ate", "saw", "wrote", "drove", "sang", "spoke", "took",
        "gave", "broke", "drank", "was", "were", "did", "swam", "flew"}
PARTICIPLE = {"gone", "eaten", "seen", "written", "driven", "sung", "spoken",
              "taken", "given", "broken", "drunk", "been", "done", "swum",
              "flown", "made", "read", "paid", "bought", "known", "left"}
PLAIN = {"go", "eat", "see", "write", "drive", "sing", "speak", "take",
         "give", "break", "drink", "be", "do", "have", "run", "swim",
         "fly", "make", "read", "know", "discuss", "walk", "talk", "work",
         "play", "study", "sleep", "laugh"}
FINITE = {"goes", "eats", "sees", "writes", "drives", "sings", "speaks",
          "takes", "gives", "breaks", "drinks", "does", "has", "is",
          "runs", "flies", "makes", "knows", "discusses", "plays", "studies"}
FAMILIES = {"perfect_auxiliary_participle", "modal_plain_form",
            "progressive_auxiliary_gerund_participle", "present_perfect_time_adjunct"}


def tokenize(text):
    return [{"id": "t" + str(i), "index": i, "text": m.group(),
             "lower": m.group().casefold().replace("’", "'"),
             "char_span": [m.start(), m.end()]}
            for i, m in enumerate(TOKEN_RE.finditer(text))]


def next_word(tokens, i):
    j = i + 1
    while j < len(tokens) and tokens[j]["lower"] in SKIP:
        j += 1
    return j if j < len(tokens) and tokens[j]["lower"].isalpha() else None


def observation(tokens, i, j, signal):
    start, end = min(i, j), max(i, j)
    return {"signal": signal, "governor_token_id": tokens[i]["id"],
            "target_token_id": tokens[j]["id"],
            "affected_token_ids": [t["id"] for t in tokens[start:end+1]],
            "token_span": [start, end+1],
            "char_span": [tokens[start]["char_span"][0], tokens[end]["char_span"][1]],
            "observed_tokens": [t["text"] for t in tokens[start:end+1]],
            "evidence_kind": "raw_token_context_only"}


def inspect(family, tokens):
    """Internal candidate signal; never directly rendered as a grammar verdict."""
    if family not in FAMILIES:
        return []
    rows = []
    for i, token in enumerate(tokens):
        word = token["lower"]
        if family == "perfect_auxiliary_participle":
            if word not in HAVE and not word.endswith("'ve") and not word.endswith("'d"):
                continue
        elif family == "modal_plain_form":
            if word not in MODAL:
                continue
        elif family == "progressive_auxiliary_gerund_participle":
            if word not in BE:
                continue
        elif family == "present_perfect_time_adjunct":
            if word not in {"have", "has"} and not word.endswith("'ve"):
                continue
        j = next_word(tokens, i)
        if j is None:
            continue
        after = tokens[j]["lower"]
        if family == "perfect_auxiliary_participle":
            if word.endswith("'d"):
                signal = "AMBIGUOUS"
            elif after in PAST:
                signal = "VIOLATED"
            elif after in PARTICIPLE or (after.endswith("ed") and len(after)>3):
                signal = "SATISFIED"
            elif after in PLAIN or after in FINITE:
                signal = "AMBIGUOUS" if after == "have" else "VIOLATED"
            else:
                continue  # "had breakfast": lexical have, not assumed auxiliary
        elif family == "modal_plain_form":
            if after in PLAIN:
                signal = "SATISFIED"
            elif after in FINITE or after in PAST or after in PARTICIPLE:
                signal = "VIOLATED"
            else:
                continue  # a can opener, a May date, unknown word
        elif family == "progressive_auxiliary_gerund_participle":
            if after.endswith("ing") and len(after)>4:
                signal = "SATISFIED"
            elif after in PLAIN or after in FINITE or after in PAST:
                signal = "VIOLATED"
            elif after in PARTICIPLE or after.endswith("ed"):
                signal = "AMBIGUOUS"  # passive/copular be, not progressive
            else:
                continue  # she is happy: copular, not progressive
        else:
            if not (after in PARTICIPLE or after.endswith("ed")):
                continue
            for k in range(j+1, min(len(tokens),j+18)):
                if tokens[k]["lower"] == "yesterday":
                    rows.append(observation(tokens, i, k, "AMBIGUOUS"))
            continue
        rows.append(observation(tokens, i, j, signal))
    return rows


def load_manifest(root=None):
    root = root or ROOT
    manifest = json.loads((root/"grammar/xai4_candidates.json").read_text())
    audit = json.loads((root/"grammar/xai_pre/source_audit.json").read_text())
    rows = manifest.get("rules")
    if (manifest.get("schema_version") != "xai4-candidates-1.0.0"
            or manifest.get("language_policy") != "ENGLISH_ONLY"
            or audit.get("schema_version") != "xai-pre-source-audit-1.0"
            or not isinstance(rows, list) or len(rows) > 16
            or len({r.get("id") for r in rows if isinstance(r, dict)}) != len(rows)):
        raise ValueError("Invalid XAI-4 source manifest")
    return manifest, audit


def eligible(rule, audit, manifest):
    """Human review + source evidence + crosswalk + test + explicit enablement.

    The present 2026-11-10 XAI-PRE audit has NO eligible claims. Synthetic
    tests may inject independently approved fixtures; production never does.
    """
    review = rule.get("review", {})
    if not (rule.get("id") in manifest.get("runtime_enabled_rule_ids", [])
            and rule.get("runtime_status") == "enabled"
            and rule.get("may_issue_verified_error") is True
            and review.get("status") == "HUMAN_APPROVED"
            and review.get("independent_human_review") is True
            and review.get("exception_review_completed") is True
            and review.get("held_out_adjudication_completed") is True
            and review.get("test_status") == "passed"
            and isinstance(review.get("reviewed_by"), str)
            and review["reviewed_by"].strip()
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(review.get("reviewed_on", "")))):
        return False
    claims = {x.get("id"): x for x in audit.get("claims", [])}
    ids = rule.get("source_claim_ids", [])
    if not ids or any(
        key not in claims
        or claims[key].get("review", {}).get("independent_human_review") is not True
        or claims[key].get("review", {}).get("approval") != "human_approved"
        or claims[key].get("runtime", {}).get("constraint_enabled") is not True
        or claims[key].get("runtime", {}).get("may_issue_grammatical_verdict") is not True
        for key in ids
    ):
        return False
    crosswalk_id = rule.get("crosswalk_id")
    crosswalk = next((x for x in audit.get("crosswalks", [])
                      if x.get("id") == crosswalk_id), None)
    return bool(crosswalk and
                crosswalk.get("review_status") == "independently_approved" and
                crosswalk.get("relation") in {"compatible", "terminology_differs"}
                and crosswalk.get("may_change_br_tree_labels") is False)


def overlap_groups(findings):
    """Witnessed token overlap, not an asserted causal correction dependency."""
    parent = {row["id"]: row["id"] for row in findings}

    def leader(key):
        while parent[key] != key:
            key = parent[key]
        return key

    edges = []
    for i, row in enumerate(findings):
        for other in findings[i+1:]:
            if set(row["affected_token_ids"]) & set(other["affected_token_ids"]):
                edges.append({"from": row["id"], "to": other["id"],
                              "kind": "OVERLAPS_SPAN"})
                parent[leader(other["id"])] = leader(row["id"])
    buckets = {}
    for row in findings:
        buckets.setdefault(leader(row["id"]), []).append(row["id"])
    groups = [
        {"id": f"g{i}", "finding_ids": members,
         "coupling": "interacting" if len(members)>1 else "independent",
         "rationale": "Shared observed tokens; causal repair order is not established."
         if len(members)>1 else "No other approved finding shares these tokens."}
        for i, members in enumerate(buckets.values(), 1)
    ]
    return edges, groups


def evaluate_xai4(sentence, *, analysis_status="unresolved", variety=None,
                  root=None):
    """Return a partial verdict, never an unconditional sentence grammar pass.

    Raw-input checks work when the B-R tree is unresolved. No source,
    signature, approval flag or rule list may be injected via HTTP payloads.
    """
    if sentence is not None and (not isinstance(sentence, str) or len(sentence)>12000):
        raise ValueError("XAI-4 input must be a string of at most 12000 characters")
    if variety is not None and (not isinstance(variety, str) or not variety.strip()):
        raise ValueError("XAI-4 variety must be nonempty or null")
    result = {
        "schema_version": "xai4-partial-1.0.0",
        "language_policy": "ENGLISH_ONLY",
        "status": "not_evaluated", "analysis_status": analysis_status,
        "token_index_basis": "XAI4_RAW_SOURCE_TOKENS_NOT_BR_NODES",
        "candidate_rule_count": 0, "enabled_rule_ids": [],
        "tokens": [], "evaluations": [], "findings": [],
        "dependencies": [], "groups": [],
        "global_verdict": {"status": "NOT_EVALUATED", "whole_sentence_certified": False},
        "diagnostics": [],
    }
    if not sentence or not sentence.strip():
        result["diagnostics"].append({"code": "INPUT_UNAVAILABLE",
             "message": "No source text was available for the raw-token checks."})
        return result
    try:
        manifest, audit = load_manifest(root)
    except (ValueError, OSError, TypeError, KeyError, AttributeError):
        result["diagnostics"].append({"code": "SOURCE_REGISTRY_UNAVAILABLE",
             "message": "No valid XAI-4 source-approval registry is available."})
        return result
    tokens = tokenize(sentence)
    result["tokens"] = [{"id": t["id"], "text": t["text"],
                          "char_span": t["char_span"]} for t in tokens]
    result["candidate_rule_count"] = len(manifest["rules"])
    # Quoted/attributed material and contraction readings require interpretation.
    quotation = any(t["text"] in {'"', "“", "”", "‘", "’"} for t in tokens)
    blocked_count = 0
    for rule in manifest["rules"]:
        if not isinstance(rule, dict) or rule.get("family") not in FAMILIES:
            result["evaluations"].append({"rule_id": str(rule.get("id", "invalid"))
                       if isinstance(rule, dict) else "invalid", "status": "UNIMPLEMENTED",
                       "evidence": [], "reason": "Unsupported typed evaluator."})
            continue
        permitted = eligible(rule, audit, manifest)
        matches = inspect(rule["family"], tokens)
        if not matches:
            result["evaluations"].append({"rule_id": rule["id"], "status": "NOT_APPLICABLE",
                "evidence": [], "reason": "The narrow construction preconditions were not observed; no global pass."})
            continue
        for match in matches:
            hypothesis = "AMBIGUOUS" if quotation else match["signal"]
            public_status = (hypothesis if permitted else
                             "AMBIGUOUS" if hypothesis == "AMBIGUOUS" else "BLOCKED")
            if public_status == "BLOCKED":
                blocked_count += 1
            observed = {k:v for k,v in match.items() if k != "signal"}
            result["evaluations"].append({
                "rule_id": rule["id"], "status": public_status,
                "evidence": [observed], "runtime_eligible": permitted,
                "source_claim_ids": rule["source_claim_ids"] if permitted else [],
                "reason": ("Interpretation or exception is not adjudicated."
                           if public_status == "AMBIGUOUS"
                           else "Independent human source, crosswalk, exception and held-out review is required."
                           if public_status == "BLOCKED"
                           else "A licensed narrow construction check was executed."),
            })
            if permitted:
                result["enabled_rule_ids"].append(rule["id"])
                if public_status == "VIOLATED":
                    result["findings"].append({
                        "id": "f" + str(len(result["findings"])+1),
                        "rule_id": rule["id"], "status": "VIOLATED",
                        "affected_token_ids": observed["affected_token_ids"],
                        "governor_token_id": observed["governor_token_id"],
                        "target_token_id": observed["target_token_id"],
                        "token_span": observed["token_span"],
                        "char_span": observed["char_span"],
                        "source_claim_ids": rule["source_claim_ids"],
                        "interpretation_status": "approved_narrow_condition_only",
                    })
    result["enabled_rule_ids"] = sorted(set(result["enabled_rule_ids"]))
    result["dependencies"], result["groups"] = overlap_groups(result["findings"])
    if result["enabled_rule_ids"]:
        result["status"] = "partially_evaluated"
        result["global_verdict"]["status"] = "PARTIALLY_EVALUATED"
    elif any(e["status"] == "AMBIGUOUS" for e in result["evaluations"]):
        result["status"] = "blocked_or_ambiguous"
    elif blocked_count:
        result["status"] = "blocked"
    else:
        result["status"] = "not_applicable_or_unimplemented"
    if not result["enabled_rule_ids"]:
        result["diagnostics"].append({"code": "NO_APPROVED_CAMBRIDGE_CHECKS",
            "message": "Four candidate rule families remain unapproved for verified learner-facing grammaticality judgments."})
    return result
