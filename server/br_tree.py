"""Canonical Burton-Roberts tree contract and conservative Benepar adapter.

Benepar is a candidate parser, never the B-R authority. This module emits a
canonical tree only from an exact IMG-verified B-R reference or a narrowly
specified convention mapping. Unsupported cases return an explicit unresolved result.
"""
from __future__ import annotations
from difflib import SequenceMatcher
from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0.0"
CONVENTIONS = tuple(f"V{i}" for i in range(1, 11))
_WORD = re.compile(r"[\w]+(?:[-'’][\w]+)*", re.UNICODE)
_DISPLAY = re.compile(r"[\w]+(?:[-'’][\w]+)*|[^\w\s]", re.UNICODE)
LABEL_INTRO = {
    "Sentence": 1, "Phrase": 1, "PHRASE": 2, "S": 2, "NP": 2, "VP": 2,
    "N": 3, "A": 3, "AP": 3, "DEG": 3, "Adv": 3, "AdvP": 3,
    "P": 3, "PP": 3, "name": 3, "pronoun": 3, "V": 4,
    "Prt": 5, "E": 5, "MOD": 6, "PERF": 6, "PROG": 6, "PASS": 6,
    "TENSE": 6, "C": 6, "S-bar": 6, "DET": 7, "ART": 7, "DEM": 7,
    "Q": 7, "POSS": 7, "PRE-DET": 7, "NOM": 7, "PartP": 7,
    "QA": 7, "V-part": 7, "S-dbar": 9, "C1": 9, "C2": 9, "AUX": 10,
}
FEATURE_INTRO = {
    "trans": 4, "intrans": 4, "ditrans": 4, "intens": 4, "complex": 4,
    "prep": 4, "phrasal": 5, "pres": 6, "past": 6, "-tense": 10,
}
FUNCTION_LABELS = {"subject", "predicate", "do", "io", "sp", "op", "pc", "aa", "sa"}
VERB_FEATURES = {"trans", "intrans", "ditrans", "intens", "complex", "prep", "phrasal"}
TENSE_FEATURES = {"pres", "past"}


def _version_number(version: str) -> int:
    if version not in CONVENTIONS:
        raise ValueError(f"unsupported B-R convention version: {version!r}")
    return int(version[1:])


def _atoms(value: str) -> list[str]:
    return [m.group(0).casefold().replace("’", "'") for m in _WORD.finditer(str(value))]


def _token_positions(tokens: list[dict[str, Any]] | None, sentence: str) -> tuple[list[str], list[int]]:
    if not tokens:
        atoms = _atoms(sentence)
        return atoms, list(range(len(atoms)))
    atoms, positions = [], []
    for fallback_index, token in enumerate(tokens):
        for atom in _atoms(str(token.get("t", ""))):
            atoms.append(atom)
            positions.append(int(token.get("i", fallback_index)))
    return atoms, positions


def _source_yield(node: dict[str, Any]) -> list[str]:
    if node.get("gap") or node.get("elided") or node.get("empty"):
        return []
    if "word" in node:
        return _atoms(str(node.get("word", "")))
    if node.get("triangle"):
        return [a for word in node.get("words", []) for a in _atoms(str(word))]
    return [a for child in node.get("children", []) for a in _source_yield(child)]


def _candidate_label(node: dict[str, Any]) -> str:
    return str(node.get("type") or node.get("label") or "")


def _candidate_is_punctuation(node: dict[str, Any]) -> bool:
    return bool(node.get("punct")) or _candidate_label(node) in {
        ".", ",", ":", ";", "?", "!", "-LRB-", "-RRB-",
    }


def _candidate_words(node: dict[str, Any]) -> list[str]:
    if not isinstance(node, dict):
        return []
    if "children" not in node:
        return [str(node.get("surface", ""))]
    return [word for child in node.get("children", []) for word in _candidate_words(child)]


def _source_to_runtime(source: dict[str, Any], positions: list[int],
                       cursor: list[int], state: dict[str, int]) -> dict[str, Any]:
    node_id = f"br-n{state['next']}"
    state["next"] += 1
    if source.get("gap"):
        at = positions[cursor[0]] if cursor[0] < len(positions) else (positions[-1] + 1 if positions else 0)
        result = {"id": node_id, "gap": True, "span": [at, at]}
        if source.get("index") is not None:
            result["index"] = source["index"]
        return result
    if "symbol" in source:
        symbol = str(source["symbol"])
        if symbol != "E" or not source.get("elided"):
            raise ValueError(f"unsupported B-R terminal symbol: {symbol!r}")
        start = positions[cursor[0]] if cursor[0] < len(positions) else (
            positions[-1] + 1 if positions else 0)
        return {"id": node_id, "symbol": symbol, "elided": True,
                "span": [start, start], "surface": symbol}
    if "word" in source:
        word = str(source["word"])
        elided = bool(source.get("elided"))
        atoms = [] if elided else _atoms(word)
        start = positions[cursor[0]] if cursor[0] < len(positions) else (
            positions[-1] + 1 if positions else 0)
        cursor[0] += len(atoms)
        end = positions[cursor[0] - 1] + 1 if atoms else start
        result = {"id": node_id, "word": word, "span": [start, end], "surface": word}
        for key in ("elided", "ellipsis", "starred"):
            if source.get(key):
                result[key] = True
        return result
    is_triangle = bool(source.get("triangle"))
    label = source.get("label")
    if not is_triangle and (not isinstance(label, str) or not label):
        raise ValueError("B-R constituent is missing a label")
    features = source.get("features") or []
    if not isinstance(features, list) or any(not isinstance(x, str) for x in features):
        raise ValueError(f"invalid feature list on {label}")
    result = {"id": node_id, "label": label, "features": list(features), "index": source.get("index")}
    if is_triangle:
        words = [str(x) for x in source.get("words", [])]
        atoms = [a for word in words for a in _atoms(word)]
        start = positions[cursor[0]] if atoms and cursor[0] < len(positions) else (
            positions[-1] + 1 if positions else 0)
        cursor[0] += len(atoms)
        end = positions[cursor[0] - 1] + 1 if atoms else start
        result.update({"triangle": True, "words": words, "span": [start, end],
                       "surface": " ".join(words)})
    else:
        children = source.get("children")
        if not isinstance(children, list):
            raise ValueError(f"{label} must have a children list")
        if not children:
            at = positions[cursor[0]] if cursor[0] < len(positions) else (
                positions[-1] + 1 if positions else 0)
            result.update({"triangle": False, "empty": True, "children": [],
                           "span": [at, at], "surface": ""})
        else:
            runtime_children = [_source_to_runtime(child, positions, cursor, state) for child in children]
            spans = [child["span"] for child in runtime_children]
            result.update({
                "triangle": False, "children": runtime_children,
                "span": [min(x[0] for x in spans), max(x[1] for x in spans)],
                "surface": " ".join(
                    text for child in runtime_children if (text := _runtime_surface(child))
                ),
            })
    for key in ("starred", "ellipsis"):
        if source.get(key):
            result[key] = True
    return result


def _runtime_surface(node: dict[str, Any]) -> str:
    if "word" in node:
        return str(node["word"])
    if node.get("triangle"):
        return str(node.get("surface", ""))
    if node.get("gap"):
        return "•"
    return str(node.get("surface", ""))


def _reference_root() -> Path:
    return Path(__file__).resolve().parents[1] / "web" / "content" / "book"


@lru_cache(maxsize=1)
def load_reference_records() -> tuple[dict[str, Any], ...]:
    root = _reference_root()
    if not root.is_dir():
        return tuple()
    records = []
    for path in sorted(root.glob("ch[0-9][0-9].trees.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for raw in payload.get("trees", []):
            if not isinstance(raw, dict) or not isinstance(raw.get("tree"), dict):
                continue
            record = dict(raw)
            record["_convention_version"] = raw.get("convention_version") or payload.get("convention_version")
            record["_chapter"] = payload.get("chapter")
            record["_source_path"] = path.relative_to(root.parents[2]).as_posix()
            records.append(record)
    return tuple(records)


def validate_tree(tree: dict[str, Any], convention_version: str,
                  expected_tokens: list[str] | None = None) -> list[str]:
    version = _version_number(convention_version)
    errors, seen = [], set()

    def visit(node: Any, path: str = "tree", parent_label: str | None = None) -> tuple[list[str], int, int]:
        if not isinstance(node, dict):
            errors.append(f"{path}: node must be an object")
            return [], 0, 0
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append(f"{path}: missing node id")
        elif node_id in seen:
            errors.append(f"{path}: duplicate node id {node_id}")
        else:
            seen.add(node_id)
        span = node.get("span")
        if (not isinstance(span, list) or len(span) != 2
                or any(not isinstance(v, int) or v < 0 for v in span) or span[1] < span[0]):
            errors.append(f"{path}: invalid token span")
            span = [0, 0]
        if node.get("gap"):
            if any(key in node for key in ("word", "label", "children")) or node.get("triangle"):
                errors.append(f"{path}: gap cannot also be a word, constituent, or triangle")
            if node.get("index") is not None and (
                not isinstance(node["index"], int) or node["index"] < 1
            ):
                errors.append(f"{path}: gap index must be a positive integer")
            if span[0] != span[1]:
                errors.append(f"{path}: gap span must be zero-width")
            return [], span[0], span[1]
        if "symbol" in node:
            if node.get("symbol") != "E" or node.get("elided") is not True:
                errors.append(f"{path}: only the elided B-R symbol E is supported")
            if any(key in node for key in ("word", "label", "children", "triangle", "gap")):
                errors.append(f"{path}: symbolic E cannot also be a word, constituent, or gap")
            if version < 5:
                errors.append(f"{path}: elision symbol E is introduced in V5")
            if span[0] != span[1]:
                errors.append(f"{path}: elision symbol must have a zero-width span")
            return [], span[0], span[1]
        if "word" in node:
            if not isinstance(node["word"], str) or not node["word"]:
                errors.append(f"{path}: terminal word must be non-empty text")
            if any(key in node for key in ("label", "children", "symbol")) or node.get("triangle"):
                errors.append(f"{path}: terminal cannot also be a constituent")
            atoms = [] if node.get("elided") else _atoms(str(node.get("word", "")))
            if atoms and span[1] - span[0] != len(atoms):
                errors.append(f"{path}: terminal span does not match lexical yield")
            if not atoms and span[0] != span[1]:
                errors.append(f"{path}: elided/non-lexical terminal must have zero-width span")
            return atoms, span[0], span[1]
        label = node.get("label")
        if not isinstance(label, str) or not label:
            if not (node.get("triangle") and parent_label == "C2" and version >= 9 and label is None):
                errors.append(f"{path}: constituent label is required")
        if isinstance(label, str) and label.casefold() in FUNCTION_LABELS:
            errors.append(f"{path}: grammatical function {label!r} must not be a tree label")
        introduced = LABEL_INTRO.get(label) if isinstance(label, str) else None
        symbolic = isinstance(label, str) and (
            (bool(re.fullmatch(r"PHRASE-[a-z]+", label)) and version <= 3)
            or (label in {"B", "C", "D", "F"} and version <= 2)
        )
        unlabeled_c2_triangle = (
            node.get("triangle") and parent_label == "C2" and version >= 9 and label is None
        )
        if introduced is None and not symbolic and not unlabeled_c2_triangle and version > 1:
            errors.append(f"{path}: label {label!r} is not in B-R inventory")
        elif introduced is not None and introduced > version:
            errors.append(f"{path}: label {label!r} is introduced after {convention_version}")
        elif label in {"Sentence", "Phrase"} and version > 1:
            errors.append(f"{path}: {label} label is replaced by later chapter conventions")
        elif label == "PHRASE" and version > 3:
            errors.append(f"{path}: PHRASE placeholder is not used after V3")
        features = node.get("features", [])
        if not isinstance(features, list) or any(not isinstance(x, str) for x in features):
            errors.append(f"{path}: features must be a list of strings")
            features = []
        for feature in features:
            intro = FEATURE_INTRO.get(feature)
            if intro is None:
                errors.append(f"{path}: unknown feature {feature!r}")
            elif intro > version:
                errors.append(f"{path}: feature {feature!r} is introduced after {convention_version}")
            elif feature in VERB_FEATURES and label != "V":
                errors.append(f"{path}: feature {feature!r} is only valid on V")
            elif feature in TENSE_FEATURES and label not in {"V", "MOD", "PERF", "PROG", "PASS", "TENSE"}:
                errors.append(f"{path}: tense feature {feature!r} is not valid on {label!r}")
            elif feature == "-tense" and label not in {"AUX", "PERF", "V"}:
                errors.append(f"{path}: -tense is not valid on {label!r}")
        if node.get("index") is not None and (
            not isinstance(node["index"], int) or node["index"] < 1
        ):
            errors.append(f"{path}: index must be a positive integer")
        if node.get("empty"):
            if node.get("triangle") or node.get("word") is not None or node.get("children") != []:
                errors.append(f"{path}: empty constituent must have empty children")
            if span[0] != span[1]:
                errors.append(f"{path}: empty constituent span must be zero-width")
            return [], span[0], span[1]
        if node.get("triangle"):
            if "children" in node:
                errors.append(f"{path}: triangle must not have children")
            words = node.get("words")
            if not isinstance(words, list) or not words or any(not isinstance(w, str) or not w for w in words):
                errors.append(f"{path}: triangle requires non-empty words")
                words = []
            atoms = [a for word in words for a in _atoms(word)]
            if atoms and span[1] - span[0] < len(atoms):
                errors.append(f"{path}: triangle span is shorter than its lexical yield")
            return atoms, span[0], span[1]
        children = node.get("children")
        if not isinstance(children, list) or not children:
            errors.append(f"{path}: non-triangle constituent requires children or empty:true")
            return [], span[0], span[1]
        atoms, spans = [], []
        for i, child in enumerate(children):
            child_atoms, start, end = visit(child, f"{path}.children[{i}]", label)
            atoms.extend(child_atoms)
            spans.append((start, end))
        previous_end = -1
        for start, end in spans:
            if start < previous_end:
                errors.append(f"{path}: children overlap or are out of order")
            previous_end = max(previous_end, end)
        coordinators = [
            i for i, child in enumerate(children)
            if isinstance(child, dict) and str(child.get("word", "")).casefold() in {"and", "or", "but"}
        ]
        if coordinators:
            if len(coordinators) != 1 or coordinators[0] != 1 or len(children) != 3:
                errors.append(f"{path}: coordination must have two conjuncts and one medial coordinator")
            else:
                left = children[0].get("label") if isinstance(children[0], dict) else None
                right = children[2].get("label") if isinstance(children[2], dict) else None
                if left != label or right != label:
                    errors.append(f"{path}: coordination mother and conjuncts must share category {label!r}")
        if spans:
            expected_span = [min(x[0] for x in spans), max(x[1] for x in spans)]
            if span != expected_span:
                errors.append(f"{path}: parent span does not cover children")
        return atoms, span[0], span[1]

    atoms, _, _ = visit(tree)
    if expected_tokens is not None:
        expected = [atom for value in expected_tokens for atom in _atoms(value)]
        if atoms != expected:
            errors.append("tree lexical yield does not match input token sequence")
    if version <= 4 and tree.get("label") == "S":
        children = tree.get("children", [])
        labels = [child.get("label") for child in children if isinstance(child, dict)]
        coordinated_s = (
            len(children) == 3
            and isinstance(children[0], dict) and children[0].get("label") == "S"
            and isinstance(children[1], dict) and str(children[1].get("word", "")).casefold() in {"and", "or", "but"}
            and isinstance(children[2], dict) and children[2].get("label") == "S"
        )
        if labels != ["NP", "VP"] and not coordinated_s:
            errors.append(f"{convention_version} S must immediately dominate NP then VP, or be an S coordination")
    return errors


def _make_reference(record: dict[str, Any], tokens: list[dict[str, Any]] | None,
                    sentence: str, version: str) -> dict[str, Any]:
    expected, positions = _token_positions(tokens, sentence)
    source_tree = record["tree"]
    if _source_yield(source_tree) != expected:
        raise ValueError("source reference tree yield mismatch")
    runtime_tree = _source_to_runtime(source_tree, positions, [0], {"next": 0})
    errors = validate_tree(runtime_tree, version, expected)
    if errors:
        raise ValueError("; ".join(errors))
    alternatives, diagnostics = [], []
    for alternative in record.get("accepted_alternatives") or []:
        if not isinstance(alternative, dict) or not isinstance(alternative.get("tree"), dict):
            diagnostics.append({"code": "INVALID_SOURCE_ALTERNATIVE", "message": "Alternative lacks a tree."})
            continue
        if _source_yield(alternative["tree"]) != expected:
            diagnostics.append({"code": "ALTERNATIVE_TOKEN_MISMATCH", "message": "Alternative yield mismatch."})
            continue
        try:
            alt_tree = _source_to_runtime(alternative["tree"], positions, [0], {"next": 0})
            alt_errors = validate_tree(alt_tree, version, expected)
        except (TypeError, ValueError) as exc:
            alt_tree, alt_errors = None, [str(exc)]
        if alt_errors:
            diagnostics.append({"code": "ALTERNATIVE_VALIDATION_FAILED", "message": "; ".join(alt_errors)})
        else:
            alternatives.append({"label": alternative.get("label"), "tree": alt_tree})
    return {
        "schema_version": SCHEMA_VERSION, "status": "normalized",
        "convention_version": version,
        "profile": "free_analysis_v10_plus_ch7_d1" if version == "V10" else "chapter",
        "profile_refinements": (
            {"ch7_appendix_d1": "retained_from_verified_source; no inferred restructuring"}
            if version == "V10" else {"ch7_appendix_nom": record.get("appendix_nom")}
        ),
        "source": {
            "book": "Burton-Roberts", "chapter": record.get("_chapter"),
            "page": record.get("page"), "figure": record.get("fig"),
            "tree_id": record.get("id"), "evidence": record.get("status"),
            "path": record.get("_source_path"), "method": "exact_verified_reference",
        },
        "tree": runtime_tree, "accepted_alternatives": alternatives,
        "movement": record.get("movement", []),
        "external_controller": record.get("external_controller"),
        "diagnostics": diagnostics,
    }


def _make_v2_mapping(candidate: dict[str, Any], tokens: list[dict[str, Any]] | None,
                     sentence: str) -> dict[str, Any] | None:
    root = candidate
    if _candidate_label(root) == "ROOT":
        roots = [x for x in root.get("children", []) if not _candidate_is_punctuation(x)]
        if len(roots) != 1:
            return None
        root = roots[0]
    if _candidate_label(root) != "S":
        return None
    children = [x for x in root.get("children", []) if not _candidate_is_punctuation(x)]
    if len(children) != 2 or [_candidate_label(x) for x in children] != ["NP", "VP"]:
        return None
    actual = [a for child in children for word in _candidate_words(child) for a in _atoms(word)]
    expected, positions = _token_positions(tokens, sentence)
    if actual != expected:
        return None
    cursor = [0]

    def triangle(label: str, child: dict[str, Any], node_id: str) -> dict[str, Any]:
        words = [word for word in _candidate_words(child) if _atoms(word)]
        atoms = [a for word in words for a in _atoms(word)]
        start = positions[cursor[0]] if atoms and cursor[0] < len(positions) else (
            positions[-1] + 1 if positions else 0)
        cursor[0] += len(atoms)
        end = positions[cursor[0] - 1] + 1 if atoms else start
        return {"id": node_id, "label": label, "features": [], "index": None,
                "triangle": True, "words": words, "span": [start, end], "surface": " ".join(words)}
    np_node, vp_node = triangle("NP", children[0], "br-n1"), triangle("VP", children[1], "br-n2")
    return {"id": "br-n0", "label": "S", "features": [], "index": None,
            "triangle": False, "children": [np_node, vp_node],
            "span": [np_node["span"][0], vp_node["span"][1]], "surface": sentence.strip()}


def _unresolved(version: str, code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "status": "unresolved",
        "convention_version": version,
        "profile": "free_analysis_v10_plus_ch7_d1" if version == "V10" else "chapter",
        "source": None, "tree": None, "accepted_alternatives": [], "movement": [],
        "diagnostics": [{"code": code, "message": message, **extra}],
    }


def normalize_candidate(candidate: dict[str, Any], tokens: list[dict[str, Any]] | None,
                        sentence: str, convention_version: str = "V10",
                        reference_records: Iterable[dict[str, Any]] | None = None,
                        appendix_nom: bool | None = None) -> dict[str, Any]:
    """Normalize exact IMG references or the explicit V2 S -> NP VP mapping.

    For Chapter 7, Appendix D1 records are never substituted for the V7 core
    (or vice versa). A source fixture must explicitly match the requested
    refinement before it can be selected.
    """
    try:
        version_number = _version_number(convention_version)
    except ValueError as exc:
        return _unresolved(convention_version, "UNSUPPORTED_CONVENTION", str(exc))
    if appendix_nom is not None and not isinstance(appendix_nom, bool):
        return _unresolved(convention_version, "INVALID_PROFILE",
                           "appendix_nom must be true, false, or null.")
    expected, _ = _token_positions(tokens, sentence)
    records = list(reference_records) if reference_records is not None else list(load_reference_records())
    matching = []
    for record in records:
        if record.get("_convention_version") != convention_version:
            continue
        if version_number == 7 and bool(record.get("appendix_nom", False)) != bool(appendix_nom):
            continue
        if record.get("status") != "IMG" or record.get("correct") is False:
            continue
        if not isinstance(record.get("sentence"), str) or _atoms(record["sentence"]) != expected:
            continue
        if _source_yield(record["tree"]) == expected:
            matching.append(record)
    mapped = []
    reference_failures = []
    for record in matching:
        try:
            mapped.append(_make_reference(record, tokens, sentence, convention_version))
        except (TypeError, ValueError) as exc:
            reference_failures.append({
                "tree_id": record.get("id"),
                "chapter": record.get("_chapter"),
                "page": record.get("page"),
                "code": "REFERENCE_VALIDATION_FAILED",
                "message": str(exc),
            })
    if mapped:
        signatures = {json.dumps(row["tree"], sort_keys=True, ensure_ascii=False) for row in mapped}
        if len(signatures) > 1:
            return _unresolved(convention_version, "AMBIGUOUS_REFERENCE",
                               "Distinct verified B-R source trees match; no analysis was selected.")
        selected = mapped[0]
        selected["diagnostics"].extend(
            {"code": "ALTERNATIVE_REFERENCE_REJECTED", **failure}
            for failure in reference_failures
        )
        return selected
    if reference_failures:
        return _unresolved(
            convention_version, "REFERENCE_VALIDATION_FAILED",
            "A B-R source record matches the sentence but failed canonical validation; the adapter refused to expose it.",
            rejected_references=reference_failures,
        )
    if version_number == 2:
        tree = _make_v2_mapping(candidate, tokens, sentence)
        if tree is not None:
            errors = validate_tree(tree, convention_version, expected)
            if not errors:
                return {
                    "schema_version": SCHEMA_VERSION, "status": "normalized",
                    "convention_version": convention_version, "profile": "chapter",
                    "profile_refinements": {},
                    "source": {"book": "Burton-Roberts", "chapter": 2,
                               "method": "supported_v2_top_level_mapping",
                               "evidence": "CONVENTIONS.md: S -> NP VP"},
                    "tree": tree, "accepted_alternatives": [], "movement": [],
                    "diagnostics": [{"code": "PARTIAL_ANALYSIS",
                                     "message": "V2 leaves NP and VP internal structure unanalyzed as triangles."}],
                }
    return _unresolved(
        convention_version, "NO_SAFE_B_R_MAPPING",
        "The Benepar candidate cannot be mapped to this B-R convention without an unsupported structural assumption.",
        candidate_root_label=_candidate_label(candidate),
    )


def _display_tokens(text: str) -> list[dict[str, Any]]:
    return [{"text": m.group(0), "start": m.start(), "end": m.end()} for m in _DISPLAY.finditer(text)]


def _terminal_ids_for_span(tree: dict[str, Any] | None,
                           tokens: list[dict[str, Any]] | None, span: list[int]) -> list[str]:
    if not isinstance(tree, dict) or not tokens:
        return []
    by_index = {int(row.get("i", i)): row for i, row in enumerate(tokens)}
    start, end = span
    found = []
    def walk(node: dict[str, Any]) -> None:
        children = node.get("children")
        if children:
            for child in children:
                walk(child)
            return
        token_span = node.get("span")
        if not isinstance(token_span, list) or len(token_span) != 2:
            return
        for i in range(token_span[0], token_span[1]):
            token = by_index.get(i)
            if token and int(token.get("start", 0)) < end and int(token.get("end", 0)) > start:
                found.append(str(node.get("id")))
                break
    walk(tree)
    return found


def build_correction_alignment(original: str, corrected: str,
                               parser_tokens: list[dict[str, Any]] | None = None,
                               original_tree: dict[str, Any] | None = None,
                               source_char_offset: int = 0) -> dict[str, Any]:
    before, after = _display_tokens(original), _display_tokens(corrected)
    matcher = SequenceMatcher(a=[x["text"] for x in before],
                              b=[x["text"] for x in after], autojunk=False)
    alignment, edits = [], []
    for operation, i1, i2, j1, j2 in matcher.get_opcodes():
        old_span = ([before[i1]["start"], before[i2 - 1]["end"]] if i1 < i2 else
                    [before[i1]["start"] if i1 < len(before) else len(original)] * 2)
        new_span = ([after[j1]["start"], after[j2 - 1]["end"]] if j1 < j2 else
                    [after[j1]["start"] if j1 < len(after) else len(corrected)] * 2)
        row = {
            "operation": operation, "original_token_range": [i1, i2],
            "corrected_token_range": [j1, j2],
            "original_char_span": old_span, "corrected_char_span": new_span,
            "original_tokens": before[i1:i2], "corrected_tokens": after[j1:j2],
        }
        alignment.append(row)
        if operation != "equal":
            changed = dict(row)
            changed["affected_terminal_ids"] = _terminal_ids_for_span(
                original_tree, parser_tokens,
                [old_span[0] + source_char_offset, old_span[1] + source_char_offset],
            )
            edits.append(changed)
    return {"original_text": original, "corrected_text": corrected,
            "original_tokens": before, "corrected_tokens": after,
            "token_alignment": alignment, "edits": edits}
