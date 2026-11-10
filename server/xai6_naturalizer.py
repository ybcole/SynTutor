"""XAI-6 optional, source-safe naturalization selector.

Production policy disables model calls until a *real*, independently human-
reviewed blind fidelity/readability comparison has passed. The fallback is
always the exact XAI-3 deterministic short/deep explanation. No arbitrary
LLM text is trusted: a model can only choose between locally prevalidated
structural-observation variants with identical fact proofs and no citations.

This module never licenses B-R functions, Cambridge constraints, corrections,
or grammaticality claims, and never mutates the original explanation.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from typing import Any

from jsonschema import Draft202012Validator, ValidationError, SchemaError

ROOT = Path(__file__).resolve().parents[1]
VERSION = "xai6-result-1.0.0"
CANDIDATE_VERSION = "xai6-candidate-1.0.0"
POLICY_PATH = ROOT / "grammar/xai6_policy.json"
POLICY_SCHEMA_PATH = ROOT / "grammar/xai6_policy.schema.json"
CANDIDATE_SCHEMA_PATH = ROOT / "grammar/xai6_candidate.schema.json"
RESULT_SCHEMA_PATH = ROOT / "grammar/xai6_result.schema.json"
SHORT_DEEP = ("short", "deep")
LEVELS = {"plain", "standard", "advanced"}
_ALLOWED_SUBSTITUTIONS = (
    ("The tree shows ", "This tree shows "),
    (" is drawn ", " is shown "),
    ("At the root, ", "At the top level, "),
)


class BoundedNaturalizerCache:
    """Small, in-process LRU. No persistent or external storage of learner text."""

    def __init__(self, capacity: int = 64):
        if type(capacity) is not int or capacity < 1 or capacity > 64:
            raise ValueError("XAI-6 cache capacity must be 1..64")
        self.capacity = capacity
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def get(self, key: str) -> dict[str, Any] | None:
        value = self._data.get(key)
        if value is None:
            return None
        self._data.move_to_end(key)
        return deepcopy(value)

    def put(self, key: str, value: dict[str, Any]) -> None:
        self._data[key] = deepcopy(value)
        self._data.move_to_end(key)
        while len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)


_CACHE = BoundedNaturalizerCache()


def load_policy(root: Path | None = None) -> dict[str, Any]:
    """Return repository-owned policy only; never use client supplied approval."""
    base = root or ROOT
    policy = json.loads((base / "grammar/xai6_policy.json").read_text(encoding="utf-8"))
    schema = json.loads(POLICY_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(policy)
    return policy


def promotion_eligible(policy: dict[str, Any]) -> bool:
    """Independent quality evidence plus all explicit server-side cost gates."""
    try:
        review, caps = policy["enablement"], policy["contract"]
        approved = (
            policy["schema_version"] == "xai6-policy-1.0.0"
            and policy["language_policy"] == "ENGLISH_ONLY"
            and policy["release_status"] == "APPROVED_FOR_LIMITED_ROLLOUT"
            and policy["model_enabled"] is True
            and all(review[k] is True for k in (
                "independent_human_blind_comparison",
                "factual_fidelity_at_least_baseline",
                "readability_gain_demonstrated",
                "no_material_increase_in_false_claims"
            ))
            and isinstance(review["reviewed_by"], str) and bool(review["reviewed_by"].strip())
            and isinstance(review["review_report"], str) and bool(review["review_report"].strip())
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(review["reviewed_on"])) is not None
            and policy["human_evaluation_fixture_count"] >= 20
            and caps["model_transport_enabled"] is True
            and isinstance(caps["model_id"], str) and bool(caps["model_id"].strip())
            and 0 < caps["max_output_tokens"] <= 300
            and 0 < caps["max_cost_usd"] <= 0.005
            and 0 < caps["max_latency_ms"] <= 1500
            and caps["max_provider_calls"] == 1
            and 0 < caps["max_cache_entries"] <= 64
            and policy["allowed_observation_scope"] == "STRUCTURAL_OBSERVATION_ONLY"
            and policy["baseline_schema_version"] == "xai-composer-3.0.0"
            and policy["source_policy"] == "PUBLISHED_SOURCE_TEMPLATES_UNCHANGED"
            and policy["log_policy"] == "NO_USER_TEXT_OR_MODEL_TEXT"
        )
        return bool(approved)
    except (KeyError, TypeError, ValueError):
        return False


def _paragraphs(item: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"level": level, "text": item["short" if level == "short" else "deep"],
             "supported_fact_ids": list(item["evidence_atom_ids"]), "source_ids": []}
            for level in SHORT_DEEP]


def _replace_unquoted(text: str, old: str, new: str) -> str:
    # XAI-3 marks lexical/source spans in curly quotes. They are immutable.
    chunks = re.split(r"(“[^”]*”)", text)
    return "".join(chunk.replace(old, new) if i % 2 == 0 else chunk
                   for i, chunk in enumerate(chunks))


def allowed_variants(text: str) -> list[str]:
    """Limited original substitutions, never free-form semantic entailment."""
    options = [text]
    for before, after in _ALLOWED_SUBSTITUTIONS:
        candidate = _replace_unquoted(text, before, after)
        if candidate != text:
            options.append(candidate)
    return list(dict.fromkeys(options))


def _cache_key(graph: dict[str, Any], item: dict[str, Any],
               policy: dict[str, Any], variety: str | None,
               reading_level: str, source_registry_version: str,
               runtime_rule_set_version: str) -> str:
    material = {
        "version": VERSION, "analysis_id": graph.get("analysis_id"),
        "node_id": item["node_id"], "reading_level": reading_level,
        "variety": variety, "source_registry_version": source_registry_version,
        "runtime_rule_set_version": runtime_rule_set_version,
        "policy_version": policy["schema_version"],
        "model_id": policy["contract"]["model_id"],
        "review_report": policy["enablement"]["review_report"],
        "evidence_atom_ids": item["evidence_atom_ids"],
        "paragraphs": _paragraphs(item),
    }
    return sha256(json.dumps(material, sort_keys=True, ensure_ascii=False,
                            separators=(",", ":")).encode("utf-8")).hexdigest()


def _result(graph: dict[str, Any] | None, item: dict[str, Any] | None,
            *, reading_level: str, status: str, reason: str,
            model_enabled: bool = False, cache_status: str = "bypassed",
            provider_calls: int = 0, elapsed: int = 0,
            paragraphs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema_version": VERSION, "language_policy": "ENGLISH_ONLY",
        "status": status, "reason_code": reason, "model_enabled": model_enabled,
        "analysis_id": graph.get("analysis_id") if graph else None,
        "selected_node_id": item["node_id"] if item else None,
        "reading_level": reading_level,
        "paragraphs": deepcopy(paragraphs if paragraphs is not None else _paragraphs(item)
                               if item else []),
        "source_ids": [], "claim_status": "STRUCTURAL_OBSERVATION_ONLY",
        "cache_status": cache_status, "provider_calls": provider_calls,
        "provider_elapsed_ms": elapsed, "whole_sentence_certified": False,
    }


def _safe_item(graph: dict[str, Any], context: dict[str, Any],
               node_id: str | None) -> dict[str, Any] | None:
    if (graph.get("schema_version") != "xai-facts-2.0.0"
            or graph.get("status") not in {"observed", "provisional"}
            or context.get("schema_version") != "xai-composer-3.0.0"
            or context.get("analysis_id") != graph.get("analysis_id")
            or context.get("selected_node_id") != node_id
            or not node_id):
        return None
    items = context.get("items", [])
    if len(items) != 1 or items[0].get("node_id") != node_id:
        return None
    item = items[0]
    ids = item.get("evidence_atom_ids")
    if (item.get("claim_status") != "STRUCTURAL_OBSERVATION_ONLY"
            or item.get("source_ids") != [] or item.get("function_status") != "unknown_unlicensed"
            or not isinstance(ids, list) or not ids or len(ids) != len(set(ids))):
        return None
    atoms = {a["fact_id"]: a for a in graph["atoms"]}
    if any(
        ident not in atoms
        or atoms[ident].get("source_rule_ids") != []
        or atoms[ident].get("evidence_kind") not in {
            "validated_tree_observation", "provisional_tree_observation"
        }
        for ident in ids
    ):
        return None
    proofs = {x["fact_id"] for x in item.get("proof", [])}
    if proofs != set(ids):
        return None
    # Re-derive deterministic baseline, never trust rewritten item fields.
    from xai_composer import compose_explanations
    reference = compose_explanations(graph, node_id=node_id)
    if reference.get("items") != [item]:
        return None
    return item


def _build_request(graph: dict[str, Any], item: dict[str, Any],
                   reading_level: str, caps: dict[str, Any]) -> dict[str, Any]:
    by_id = {x["fact_id"]: x for x in graph["atoms"]}
    packet = {
        "instruction": ("Select only from allowed_texts for each paragraph; do not add "
                        "grammar claims, source citations, corrections or interpretations."),
        "schema_version": CANDIDATE_VERSION, "analysis_id": graph["analysis_id"],
        "node_id": item["node_id"], "reading_level": reading_level,
        "language_policy": "ENGLISH_ONLY",
        "claim_status": "STRUCTURAL_OBSERVATION_ONLY",
        "facts": [
            {"fact_id": ident, "predicate": by_id[ident]["predicate"],
             "subject_node_id": by_id[ident]["subject_node_id"],
             "object_node_id": by_id[ident].get("object_node_id"),
             "value": by_id[ident]["value"], "uncertainty": by_id[ident]["uncertainty"]}
            for ident in item["evidence_atom_ids"]
        ],
        "paragraphs": [{
            **paragraph, "allowed_texts": allowed_variants(paragraph["text"])
        } for paragraph in _paragraphs(item)],
    }
    if len(json.dumps(packet, ensure_ascii=False)) > caps["max_prompt_chars"]:
        raise ValueError("model input exceeds approved prompt budget")
    return packet


def verify_candidate(candidate: dict[str, Any], graph: dict[str, Any],
                     item: dict[str, Any], reading_level: str) -> list[dict[str, Any]]:
    """Prove exact witnessed atoms + allowed semantic-preserving wording."""
    try:
        schema = json.loads(CANDIDATE_SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(candidate)
    except (OSError, ValueError, TypeError, ValidationError, RecursionError):
        raise ValueError("malformed naturalization candidate") from None
    if (candidate["analysis_id"] != graph["analysis_id"]
            or candidate["node_id"] != item["node_id"]
            or candidate["reading_level"] != reading_level):
        raise ValueError("candidate provenance or target mismatch")
    baseline = _paragraphs(item)
    for i, (proposed, expected) in enumerate(zip(candidate["paragraphs"], baseline)):
        if (proposed["level"] != SHORT_DEEP[i]
                or proposed["supported_fact_ids"] != expected["supported_fact_ids"]
                or proposed["source_ids"] != []
                or proposed["text"] not in allowed_variants(expected["text"])):
            raise ValueError("unsupported paraphrase, fact, source or certainty change")
    return deepcopy(candidate["paragraphs"])


def naturalize(graph: dict[str, Any] | None,
               contextual: dict[str, Any] | None, *,
               node_id: str | None = None, reading_level: str = "standard",
               variety: str | None = None, provider=None,
               policy: dict[str, Any] | None = None,
               cache: BoundedNaturalizerCache | None = None,
               source_registry_version: str = "1.0.0",
               runtime_rule_set_version: str = "unapproved") -> dict[str, Any]:
    """Return a source-safe short/deep pair; model calls are always opt-in.

    Provider is a server-controlled callback accepting the strictly bounded
    packet and keyword timeout_ms and max_output_tokens. A real provider MUST
    implement a *hard* network timeout and monetary ceiling. Production policy
    is disabled, so no network/model transport is available by default.
    """
    if reading_level not in LEVELS:
        raise ValueError("reading_level must be plain, standard or advanced")
    if not isinstance(graph, dict) or not isinstance(contextual, dict):
        return _result(graph if isinstance(graph, dict) else None, None,
                       reading_level=reading_level, status="unavailable",
                       reason="NO_CONTEXTUAL_PROOF")
    item = _safe_item(graph, contextual, node_id)
    if item is None:
        return _result(graph, None, reading_level=reading_level,
                       status="unavailable", reason="NO_SELECTED_NODE" if node_id is None
                       else "NO_CONTEXTUAL_PROOF")
    try:
        active_policy = deepcopy(policy if policy is not None else load_policy())
        schema = json.loads(POLICY_SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(active_policy)
    except (OSError, ValueError, TypeError, ValidationError, RecursionError):
        return _result(graph, item, reading_level=reading_level,
                       status="fallback", reason="INVALID_POLICY")
    if not promotion_eligible(active_policy):
        return _result(graph, item, reading_level=reading_level,
                       status="disabled", reason="INDEPENDENT_BLIND_REVIEW_PENDING")
    caps = active_policy["contract"]
    if provider is None or not callable(provider):
        return _result(graph, item, reading_level=reading_level,
                       status="fallback", reason="MODEL_TRANSPORT_UNAVAILABLE",
                       model_enabled=True)
    key = _cache_key(graph, item, active_policy, variety, reading_level,
                     source_registry_version, runtime_rule_set_version)
    storage = cache if cache is not None else _CACHE
    cached = storage.get(key)
    if cached is not None:
        return _result(graph, item, reading_level=reading_level, status="accepted",
                       reason="CACHE_HIT", model_enabled=True, cache_status="hit",
                       paragraphs=cached)
    try:
        packet = _build_request(graph, item, reading_level, caps)
    except (ValueError, TypeError, KeyError):
        return _result(graph, item, reading_level=reading_level,
                       status="fallback", reason="MODEL_BUDGET_EXCEEDED",
                       model_enabled=True)
    start = time.monotonic()
    try:
        answer = provider(deepcopy(packet),
                          timeout_ms=caps["max_latency_ms"],
                          max_output_tokens=caps["max_output_tokens"])
    except Exception:
        elapsed = int(max(0, (time.monotonic() - start) * 1000))
        return _result(graph, item, reading_level=reading_level,
                       status="fallback", reason="MODEL_REQUEST_FAILED",
                       model_enabled=True, cache_status="miss", provider_calls=1,
                       elapsed=elapsed)
    elapsed = int(max(0, (time.monotonic() - start) * 1000))
    if elapsed > caps["max_latency_ms"]:
        return _result(graph, item, reading_level=reading_level,
                       status="fallback", reason="MODEL_DEADLINE_EXCEEDED",
                       model_enabled=True, cache_status="miss", provider_calls=1,
                       elapsed=elapsed)
    try:
        if not isinstance(answer, dict) or set(answer) != {"candidate", "usage"}:
            raise ValueError("missing response metadata")
        raw = json.dumps(answer, ensure_ascii=False)
        if len(raw) > caps["max_response_chars"]:
            raise ValueError("model response exceeds approved size")
        usage = answer["usage"]
        if not isinstance(usage, dict) or set(usage) != {
                "input_tokens", "output_tokens", "cost_usd"}:
            raise ValueError("usage metadata is missing")
        a, b, c = usage["input_tokens"], usage["output_tokens"], usage["cost_usd"]
        if (type(a) is not int or a < 0 or type(b) is not int or b < 0
                or b > caps["max_output_tokens"] or type(c) not in {int, float}
                or not (0 <= c <= caps["max_cost_usd"])):
            raise ValueError("model usage exceeds approved budget")
        paragraphs = verify_candidate(answer["candidate"], graph, item, reading_level)
        if paragraphs == _paragraphs(item):
            return _result(graph, item, reading_level=reading_level,
                           status="fallback", reason="MODEL_UNCHANGED_BASELINE",
                           model_enabled=True, cache_status="miss", provider_calls=1,
                           elapsed=elapsed)
        storage.put(key, paragraphs)
        return _result(graph, item, reading_level=reading_level,
                       status="accepted", reason="NATURALIZATION_ACCEPTED",
                       model_enabled=True, cache_status="miss", provider_calls=1,
                       elapsed=elapsed, paragraphs=paragraphs)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return _result(graph, item, reading_level=reading_level,
                       status="fallback", reason="MODEL_RESPONSE_REJECTED",
                       model_enabled=True, cache_status="miss", provider_calls=1,
                       elapsed=elapsed)
