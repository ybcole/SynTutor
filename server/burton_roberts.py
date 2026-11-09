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

SCHEMA_VERSION = "1.1.0"
SUPPORTED_SCHEMA_VERSIONS = {"1.0.0", SCHEMA_VERSION}
BOOK_TITLE = "Burton-Roberts, Analysing Sentences"
BOOK_EDITION = "3rd edition (Pearson Education, 2011; ISBN 9781408233740)"
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
    allowed = {"chapter", "version", "appendix_nom", "profile_id"}
    unknown = sorted(set(profile) - allowed)
    if unknown:
        return ["unsupported convention_profile field(s): " + ", ".join(unknown)]
    chapter = profile.get("chapter")
    version = profile.get("version")
    if isinstance(chapter, bool) or not isinstance(chapter, int) or not 1 <= chapter <= 10:
        return ["convention_profile.chapter must be an integer from 1 through 10"]

    if chapter == 10 and version == "FINAL":
        if profile.get("appendix_nom") is not True:
            return ["FINAL profile must retain the Appendix D1 NOM refinement"]
        expected_id = "FINAL-D1"
    else:
        expected_version = f"V{chapter}"
        if version != expected_version:
            return [f"convention_profile.version must be {expected_version} for chapter {chapter}"]
        if chapter == 7:
            appendix = profile.get("appendix_nom", False)
            if not isinstance(appendix, bool):
                return ["V7 appendix_nom must be a boolean when supplied"]
            expected_id = "V7-APPENDIX-D1" if appendix else "V7-CORE"
        else:
            if "appendix_nom" in profile:
                return ["appendix_nom is only valid for V7 or the FINAL profile"]
            expected_id = f"V{chapter}"

    profile_id = profile.get("profile_id")
    if profile_id is not None and profile_id != expected_id:
        return [f"convention_profile.profile_id must be {expected_id!r} for this profile"]
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
    """Convert lexical parser tokens to sentence-local canonical token records.

    Phrase markers in the B-R fixtures omit terminal punctuation. Keep
    punctuation in the original sentence and parser diagnostics, but do not
    create artificial punctuation leaves in the canonical phrase marker.
    """
    start = _sentence_start(analysis)
    result = []
    for token in analysis.get("tokens") or []:
        text = str(token.get("t", ""))
        if not any(char.isalnum() or char == "_" for char in text):
            continue
        char_start = int(token.get("start", start)) - start
        char_end = int(token.get("end", start)) - start
        result.append({
            "index": len(result),
            "text": text,
            "char_span": [char_start, char_end],
            "pos": str(token.get("pos", "")),
            "parser_tag": str(token.get("tag", "")),
        })
    return result


def _is_parser_punctuation(node: dict[str, Any]) -> bool:
    if node.get("punct") is True:
        return True
    surface = str(node.get("surface", ""))
    return bool(surface) and not any(char.isalnum() or char == "_" for char in surface)


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


# Verb uses attested in Ch4 pp. 70–72 and Ch5 p. 104. The finite forms
# are checked against both this inventory and the candidate's tense tag.
_FINAL_VERB_FRAMES = {
    "intrans": {
        "sleep sleeps slept", "sigh sighs sighed", "laugh laughs laughed",
        "die dies died", "disappear disappears disappeared",
        "sunbathe sunbathes sunbathed",
    },
    "trans": {
        "inspect inspects inspected", "spot spots spotted", "throw throws threw",
        "dread dreads dreaded",
    },
}
_FINAL_VERBS = {
    (word, tag): frame
    for frame, entries in _FINAL_VERB_FRAMES.items()
    for entry in entries
    for word, tag in zip(entry.split(), ("VBP", "VBZ", "VBD"))
}


def _final_branch(label, refs, *children, features=()):
    node = {"label": label, "source_refs": list(refs), "children": list(children)}
    if features:
        node["features"] = list(features)
    return node


def _final_simple_np(candidate):
    children = candidate.get("children") or []
    if not children or not all(_is_raw_leaf(node) for node in children):
        return None
    tags = [node["type"] for node in children]
    words = [{"word": node["surface"]} for node in children]
    np_refs = ("Ch7 pp. 141–142",)
    if tags in (["NNP"], ["PRP"]):
        label = "name" if tags[0] == "NNP" else "pronoun"
        return _final_branch("NP", np_refs, _final_branch(label, np_refs, words[0]))

    if tags[-1] not in {"NN", "NNS"}:
        return None
    if tags[:-1] in (["DT"], ["DT", "JJ"]) and words[0]["word"].lower() in {"the", "a", "an"}:
        det = _final_branch("DET", np_refs, _final_branch("ART", np_refs, words[0]))
    elif tags in (["NNS"], ["JJ", "NNS"]):
        det = {"label": "DET", "children": [], "source_refs": ["Ch7 p. 144 [10]"]}
    else:
        return None

    nominal = _final_branch("NOM", np_refs, _final_branch("N", np_refs, words[-1]))
    if tags[-2:-1] == ["JJ"]:
        modifier = _final_branch("AP", ("Ch3 p. 55",),
                                 _final_branch("A", ("Ch3 p. 55",), words[-2]))
        nominal = _final_branch("NOM", ("Ch7 pp. 166–168",), modifier, nominal)
    return _final_branch("NP", np_refs, det, nominal)


def _final_lexical_declarative(
        raw_root: dict[str, Any], sentence: str, tokens: list[dict[str, Any]],
        profile: dict[str, Any]) -> dict[str, Any] | None:
    """Project simple finite clauses using attested lexical complement frames."""
    root = raw_root
    while root.get("type") in {"ROOT", "TOP"} and len(root.get("children") or []) == 1:
        root = root["children"][0]
    if root.get("type") != "S":
        return None
    clause = list(root.get("children") or [])
    punctuation = clause.pop() if clause and _is_raw_leaf(clause[-1]) and clause[-1]["surface"] == "." else None
    if [child.get("type") for child in clause] != ["NP", "VP"]:
        return None

    subject, predicate = clause
    np = _final_simple_np(subject)
    verb_and_dependents = predicate.get("children") or []
    if np is None or not verb_and_dependents or not _is_raw_leaf(verb_and_dependents[0]):
        return None
    head, *dependents = verb_and_dependents
    frame = _FINAL_VERBS.get((head["surface"].lower(), head["type"]))
    if frame is None:
        return None
    tense = "past" if head["type"] == "VBD" else "pres"
    frame_refs = ("Ch4 pp. 70–71 [21]",) if frame == "trans" else ("Ch4 pp. 71–72 [22]",)
    if head["surface"].lower() in {"sleep", "sleeps", "slept"}:
        frame_refs += ("Ch5 p. 104 [1e]",)
    verb = _final_branch("V", (*frame_refs, "Ch6 p. 113 [8]–[9]"),
                         {"word": head["surface"]}, features=(frame, tense))
    children = [verb]
    if frame == "trans":
        if not dependents or dependents[0].get("type") != "NP":
            return None
        complement = _final_simple_np(dependents.pop(0))
        if complement is None:
            return None
        children.append(complement)
    vp = _final_branch("VP", frame_refs, *children)
    if dependents:
        if [node.get("type") for node in dependents] != ["ADVP"]:
            return None
        adverb = dependents[0].get("children") or []
        if len(adverb) != 1 or not _is_raw_leaf(adverb[0]) or adverb[0].get("type") != "RB":
            return None
        adjunct = _final_branch("AdvP", ("Ch3 p. 56", "Ch5 pp. 87–90"),
                                _final_branch("Adv", ("Ch3 p. 56",), {"word": adverb[0]["surface"]}))
        vp = _final_branch("VP", ("Ch5 pp. 87–90",), vp, adjunct)

    # Check the complete candidate yield and the original sentence offsets.
    surface_tokens = _tokenize_with_spans(sentence)
    if punctuation and surface_tokens and surface_tokens[-1]["text"] == ".":
        surface_tokens.pop()
    leaves = _raw_leaves(root)
    if punctuation:
        leaves.pop()
    if any(_is_parser_punctuation(leaf) for leaf in leaves):
        return None
    if [token["text"] for token in tokens] != [node.get("surface") for node in leaves]:
        return None
    if surface_tokens != [{"text": token["text"], "char_span": token["char_span"]}
                          for token in tokens]:
        return None

    tree = _final_branch("S", ("Ch2 pp. 29–30",), np, vp)
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "tree_id": _stable_id("sg", sentence + "|FINAL-D1"),
        "sentence": sentence,
        "tokens": tokens,
        "convention_profile": profile,
        "source": {"book": BOOK_TITLE, "edition": BOOK_EDITION, "chapter": 10,
                   "evidence_status": "DERIVED_FROM_INSTRUCTIONS",
                   "review_note": "FINAL-D1 projection. Printed evidence is recorded on each category node."},
        "root": _build_canonical_node(tree, tokens, [0], "sg-root", []),
        "movement": [],
        "accepted_alternatives": [],
    }
    trace = [{
        "rule_id": "FINAL_D1_LEXICAL_DECLARATIVE",
        "evidence": "Ch2 clause structure, Ch4 lexical complementation, Ch5 adjunct attachment, "
                    "Ch6 tense and Ch7 noun-phrase structure.",
    }]
    validation = validate_canonical_tree(envelope)
    if not validation["valid"]:
        return {"status": "rejected", "tree": None,
                "reasons": [{"code": "CANONICAL_VALIDATION_FAILED", "detail": e}
                            for e in validation["errors"]],
                "normalization_trace": trace, "validation": validation}
    return {"status": "normalized", "tree": envelope, "reasons": [],
            "normalization_trace": trace, "validation": validation}


def normalize_benepar_candidate(analysis: dict[str, Any],
                                profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Project the V2 lesson shell or the guarded FINAL-D1 declarative."""
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
    elif profile["version"] == "FINAL":
        final = _final_lexical_declarative(raw_root, sentence, tokens, profile)
        if final is not None:
            return final
    if profile["chapter"] != 2:
        reasons.append({
            "code": "PROFILE_MAPPING_NOT_APPROVED",
            "detail": (f"No reviewed mapping for this construction under {profile['version']}. "
                       "The adapter supports the V2 lesson shell and a guarded FINAL-D1 declarative."),
        })
    if reasons:
        return _unresolved_result(profile, reasons, trace, analysis, tokens)

    root = raw_root
    while root.get("type") in {"ROOT", "TOP"} and isinstance(root.get("children"), list):
        semantic_children = [child for child in root["children"]
                             if isinstance(child, dict) and not _is_parser_punctuation(child)]
        if len(semantic_children) != 1:
            break
        trace.append({"rule_id": "STRIP_SINGLE_PARSER_WRAPPER",
                      "from": root.get("type"), "to": semantic_children[0].get("type"),
                      "evidence": "transport wrapper and sentence-final punctuation are not B-R phrase-marker nodes"})
        root = semantic_children[0]

    if root.get("type") != "S":
        reasons.append({"code": "UNSUPPORTED_ROOT_LABEL",
                        "detail": f"Expected a B-R V2 S root; received {root.get('type')!r}."})
    children = [
        child for child in (root.get("children") or [])
        if isinstance(child, dict) and not _is_parser_punctuation(child)
    ]
    child_labels = [c.get("type") for c in children]
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
            # Only sentence-final punctuation may be excluded; medial punctuation
            # still requires a reviewed mapping. Never mutate parser diagnostics.
            if label == "VP" and leaves and _is_parser_punctuation(leaves[-1]):
                last = leaves[-1]
                tail = str(last.get("surface", ""))
                if tail in {".", "!", "?"} and sentence.rstrip().endswith(tail):
                    leaves = leaves[:-1]
                    trace.append({"rule_id": "EXCLUDE_SENTENCE_FINAL_PUNCTUATION",
                                  "evidence": "V2 phrase marker represents lexical yield; original punctuation remains in sentence/parser diagnostics."})
            words = [str(leaf.get("surface", "")) for leaf in leaves]
            if not words or any(not word for word in words):
                reasons.append({"code": "EMPTY_PHRASE", "detail": f"The {label} candidate has no overt terminal words."})
                continue
            if any(bool(leaf.get("punct")) for leaf in leaves):
                reasons.append({"code": "PUNCTUATION_POLICY_UNVERIFIED",
                                "detail": f"Punctuation occurs inside the {label} candidate; no B-R punctuation projection is approved here."})
                continue
            triangles.append({
                "id": f"sg-{label.lower()}", "label": label, "triangle": True,
                "words": words,
            })
            trace.append({"rule_id": f"V2_TRIANGLE_{label}", "from": label,
                          "to": f"{label} triangle", "evidence": "CONVENTIONS.md: V2 permits NP/VP triangles; internal parser structure is intentionally not promoted."})

    if reasons:
        return _unresolved_result(profile, reasons, trace, analysis, tokens)

    # The parser's leaf order must be identical to the token stream produced by
    # spaCy. A different tokenization is not repaired by guessing.
    leaves = _raw_leaves(raw_root)
    leaf_text = [str(x.get("surface", "")) for x in leaves
                 if not _is_parser_punctuation(x)]
    token_text = [t["text"] for t in tokens]
    if leaf_text != token_text:
        reasons.append({"code": "TOKEN_ALIGNMENT_MISMATCH",
                        "detail": "Benepar leaf text is not identical to the ordered spaCy token stream."})
        return _unresolved_result(profile, reasons, trace, analysis, tokens)

    cursor = 0
    for triangle in triangles:
        width = len(triangle["words"])
        triangle["token_span"] = [cursor, cursor + width]
        cursor += width
    if cursor != len(tokens):
        reasons.append({"code": "TOKEN_COVERAGE_MISMATCH",
                        "detail": f"V2 triangles cover {cursor} token(s), but the parser returned {len(tokens)}."})
        return _unresolved_result(profile, reasons, trace, analysis, tokens)

    root_node = {"id": "sg-s", "label": "S", "token_span": [0, len(tokens)],
                 "children": triangles}
    tree_id = _stable_id("sg", sentence + "|V2")
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "tree_id": tree_id,
        "sentence": sentence,
        "tokens": tokens,
        "convention_profile": profile,
        "source": {"book": BOOK_TITLE, "edition": BOOK_EDITION, "chapter": 2,
                   "evidence_status": "NEEDS_REVIEW"},
        "root": root_node,
        "movement": [],
        "accepted_alternatives": [],
        "notes": ["Benepar remains a candidate parser. This V2 projection is limited to S → NP VP with unanalyzed NP/VP triangles."],
    }
    validation = validate_canonical_tree(envelope)
    if not validation["valid"]:
        return {"status": "rejected", "tree": None,
                "reasons": [{"code": "CANONICAL_VALIDATION_FAILED", "detail": e}
                            for e in validation["errors"]],
                "normalization_trace": trace,
                "validation": validation}
    return {"status": "normalized", "tree": envelope, "reasons": [],
            "normalization_trace": trace, "validation": validation}


def _unresolved_result(profile: dict[str, Any], reasons: list[dict[str, str]],
                       trace: list[dict[str, Any]], analysis: dict[str, Any],
                       tokens: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": "unresolved", "tree": None, "reasons": reasons,
            "normalization_trace": trace,
            "diagnostics": {"parser": "benepar_en3", "parse_string": analysis.get("parse_string"),
                            "raw_candidate_tree": analysis.get("root"),
                            "token_count": len(tokens)}}


def _matching_gold_records(sentence: str, profile: dict[str, Any],
                            reference_records: Any = None) -> list[dict[str, Any]]:
    """Find exact sentence/profile-matched image-verified B-R source records."""
    try:
        from .br_tree import _atoms, _source_yield, load_reference_records
    except ImportError:  # direct script-directory imports
        from br_tree import _atoms, _source_yield, load_reference_records

    expected = _atoms(sentence)
    version = "V10" if profile.get("version") == "FINAL" else profile.get("version")
    chapter = profile.get("chapter")
    records = load_reference_records() if reference_records is None else reference_records
    matches = []
    for record in records:
        if record.get("_chapter") != chapter or record.get("_convention_version") != version:
            continue
        if record.get("status") != "IMG" or record.get("correct") is False:
            continue
        if not isinstance(record.get("sentence"), str):
            continue
        if _atoms(record["sentence"]) != expected:
            continue
        if not isinstance(record.get("tree"), dict) or _source_yield(record["tree"]) != expected:
            continue
        if chapter == 7 and bool(record.get("appendix_nom", False)) != bool(profile.get("appendix_nom", False)):
            continue
        matches.append(record)
    return matches


def build_canonical_analysis(analysis: dict[str, Any], chapter: int | None = None,
                             appendix_nom: bool | None = None,
                             correction: dict[str, Any] | None = None,
                             reference_records: Any = None) -> dict[str, Any]:
    """Build an API result whose normalized tree uses the M1-approved envelope.

    Exact IMG-verified source trees take priority when sentence and convention
    match. Conflicting source analyses remain unresolved. Otherwise the narrow
    parser adapter is attempted for the V2 shell or the guarded FINAL-D1
    declarative. Other Benepar structures fail closed.
    """
    profile = convention_profile(chapter, appendix_nom)
    sentence = str(analysis.get("sentence", ""))
    try:
        matches = _matching_gold_records(sentence, profile, reference_records)
    except Exception as exc:  # malformed source index/data must fail closed
        matches = []
        match_failure = exc
    else:
        match_failure = None
    if match_failure is not None:
        result = {
            "status": "unresolved", "tree": None,
            "reasons": [{
                "code": "GOLD_LOOKUP_FAILURE",
                "detail": f"Exact B-R source lookup failed safely: {match_failure}",
            }],
            "normalization_trace": [{
                "rule_id": "EXACT_GOLD_REFERENCE_LOOKUP",
                "evidence": "Source lookup failed; the raw Benepar candidate was not promoted.",
            }],
        }
    elif matches:
        signatures = {
            json.dumps(
                {"tree": row.get("tree"),
                 "accepted_alternatives": row.get("accepted_alternatives") or []},
                ensure_ascii=False, sort_keys=True,
            )
            for row in matches
        }
        if len(signatures) > 1:
            result = {
                "status": "unresolved", "tree": None,
                "reasons": [{
                    "code": "AMBIGUOUS_GOLD_REFERENCE",
                    "detail": "Different IMG-verified B-R source analyses match this sentence and convention; no tree was selected.",
                }],
                "normalization_trace": [{
                    "rule_id": "EXACT_GOLD_REFERENCE_LOOKUP",
                    "evidence": "The matching source records disagree structurally.",
                }],
            }
        else:
            try:
                imported = canonicalize_gold_record(
                    matches[0], {"chapter": int(profile["chapter"])})
            except Exception as exc:  # malformed source projection must fail closed
                imported = {
                    "status": "unresolved", "tree": None,
                    "errors": [f"gold source importer failed safely: {type(exc).__name__}: {exc}"],
                }
            if imported.get("status") != "normalized" or not isinstance(imported.get("tree"), dict):
                result = {
                    "status": "unresolved", "tree": None,
                    "reasons": [{
                        "code": "GOLD_SOURCE_IMPORT_UNRESOLVED",
                        "detail": "; ".join(imported.get("errors") or ["The matching B-R source record could not be projected."]),
                    }],
                    "normalization_trace": [{
                        "rule_id": "EXACT_GOLD_REFERENCE_LOOKUP",
                        "evidence": "The matching IMG record was retained as unresolved; no parser fallback was substituted.",
                    }],
                }
            else:
                envelope = imported["tree"]
                # The exact-gold lookup matches lexical yield, not punctuation
                # or whitespace. Preserve the submitted sentence and rebase
                # lexical-token character offsets onto that exact request text.
                source_tokens = envelope.get("tokens") or []
                rebased_tokens, alignment_errors = _align_words_to_sentence(
                    [str(token.get("text", "")) for token in source_tokens], sentence)
                if alignment_errors or len(rebased_tokens) != len(source_tokens):
                    result = {
                        "status": "unresolved", "tree": None,
                        "reasons": [{
                            "code": "REQUEST_TOKEN_ALIGNMENT_FAILED",
                            "detail": "; ".join(alignment_errors or [
                                "The selected gold tree's tokenization could not be aligned to the submitted sentence."
                            ]),
                        }],
                        "normalization_trace": [{
                            "rule_id": "EXACT_IMG_GOLD_REFERENCE",
                            "evidence": "The lexical source match could not be safely rebased to the exact request text.",
                        }],
                    }
                else:
                    for token, rebased in zip(source_tokens, rebased_tokens):
                        token["char_span"] = rebased["char_span"]
                    envelope["sentence"] = sentence
                    # The declared free-analysis profile is FINAL-D1 (V10 plus
                    # the adopted Appendix NOM refinement), not merely a Ch10 lesson.
                    envelope["convention_profile"] = profile
                    try:
                        validation = validate_canonical_tree(envelope)
                    except Exception as exc:  # unexpected validator error cannot promote a tree
                        validation = {
                            "valid": False,
                            "errors": [f"canonical validator failed safely: {type(exc).__name__}: {exc}"],
                            "warnings": [],
                        }
                    if not validation["valid"]:
                        result = {
                            "status": "unresolved", "tree": None,
                            "reasons": [{
                                "code": "CANONICAL_GOLD_VALIDATION_FAILED",
                                "detail": "; ".join(validation["errors"]),
                            }],
                            "normalization_trace": [{
                                "rule_id": "EXACT_GOLD_REFERENCE_LOOKUP",
                                "evidence": "The imported source envelope failed the approved M1 canonical validator.",
                            }],
                        }
                    else:
                        duplicate_ids = [str(row.get("id")) for row in matches[1:]]
                        if duplicate_ids:
                            envelope.setdefault("notes", []).append(
                                "identical_gold_reference_records=" + ",".join(duplicate_ids))
                        result = {
                            "status": "normalized", "tree": envelope, "reasons": [],
                            "normalization_trace": [{
                                "rule_id": "EXACT_IMG_GOLD_REFERENCE",
                                "evidence": "Exact lexical yield and convention-profile match to an IMG-verified Burton-Roberts source record.",
                                "source_record_id": matches[0].get("id"),
                            }],
                            "validation": validation,
                        }
    else:
        try:
            result = normalize_benepar_candidate(analysis, profile)
        except Exception as exc:  # unexpected adapter errors become explicit unresolved data
            result = {
                "status": "unresolved", "tree": None,
                "reasons": [{
                    "code": "NORMALIZER_FAILURE",
                    "detail": f"B-R normalization failed safely: {type(exc).__name__}: {exc}",
                }],
                "normalization_trace": [{
                    "rule_id": "FAIL_CLOSED_NORMALIZER",
                    "evidence": "An adapter exception occurred; no candidate labels were promoted.",
                }],
            }

    result["convention_profile"] = profile
    result["convention_version"] = profile["version"]
    raw_diagnostics = result.get("diagnostics")
    if isinstance(raw_diagnostics, dict):
        result["parser_diagnostics"] = raw_diagnostics
    else:
        result["parser_diagnostics"] = {
            "parser": "benepar_en3", "parse_string": analysis.get("parse_string"),
            "raw_candidate_tree": analysis.get("root"),
            "token_count": len(analysis.get("tokens") or []),
        }
    result["canonical_schema"] = "docs/canonical-burton-roberts-tree.schema.json"
    result["diagnostics"] = [
        {"code": row.get("code", "NORMALIZATION_UNRESOLVED"),
         "message": row.get("detail", row.get("message", "The B-R analysis is unresolved."))}
        for row in result.get("reasons", [])
    ]
    if correction:
        result["correction_alignment"] = align_correction(
            str(correction.get("original_sentence", analysis.get("sentence", ""))),
            str(correction.get("corrected_sentence", "")),
            source_edits=correction.get("edits") or [])
    else:
        result["correction_alignment"] = None
    return result


def _tokenize_with_spans(text: str) -> list[dict[str, Any]]:
    return [{"text": m.group(0), "char_span": [m.start(), m.end()]}
            for m in _TOKEN_RE.finditer(text)]


def align_correction(original: str, corrected: str,
                     source_edits: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Align correction tokens, retaining substitutions/inserts/deletes and punctuation.

    Contractions are kept as one lexical token when apostrophized; punctuation
    marks are separate tokens. Multi-token rewrites remain a single operation
    with explicit token and character ranges on both sides.
    """
    before = _tokenize_with_spans(original)
    after = _tokenize_with_spans(corrected)
    a = [x["text"].casefold() for x in before]
    b = [x["text"].casefold() for x in after]
    matcher = SequenceMatcher(a=a, b=b, autojunk=False)
    operations = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            kind = "unchanged"
        else:
            left = before[i1:i2]
            right = after[j1:j2]
            left_text = [x["text"] for x in left]
            right_text = [x["text"] for x in right]
            apostrophe = any("'" in x or "’" in x for x in left_text + right_text)
            punctuation = any(not any(ch.isalnum() for ch in x)
                              for x in left_text + right_text)
            if apostrophe:
                kind = "contraction"
            elif punctuation:
                kind = "punctuation"
            elif tag == "insert":
                kind = "insertion"
            elif tag == "delete":
                kind = "deletion"
            elif max(i2 - i1, j2 - j1) > 1:
                kind = "multi_token_replacement"
            else:
                kind = "substitution"
        left = before[i1:i2]
        right = after[j1:j2]
        def char_span(rows: list[dict[str, Any]], fallback: int) -> list[int]:
            if not rows:
                return [fallback, fallback]
            return [rows[0]["char_span"][0], rows[-1]["char_span"][1]]
        old_point = left[0]["char_span"][0] if left else (before[i1 - 1]["char_span"][1] if i1 else 0)
        new_point = right[0]["char_span"][0] if right else (after[j1 - 1]["char_span"][1] if j1 else 0)
        operations.append({
            "kind": kind,
            "opcode": tag,
            "original_token_range": [i1, i2],
            "corrected_token_range": [j1, j2],
            "original_char_span": char_span(left, old_point),
            "corrected_char_span": char_span(right, new_point),
            "original_tokens": [x["text"] for x in left],
            "corrected_tokens": [x["text"] for x in right],
        })
    return {"original_sentence": original, "corrected_sentence": corrected,
            "original_tokens": before, "corrected_tokens": after,
            "operations": operations, "source_edits": source_edits or []}


def _tree_words(node: dict[str, Any]) -> list[str]:
    if node.get("gap") is True or node.get("empty") is True:
        return []
    if "word" in node:
        if node.get("ellipsis") or node.get("elided") or node.get("word") == "...":
            return []
        return [str(node["word"])]
    if node.get("triangle"):
        return [str(w) for w in node.get("words", []) if str(w) != "..."]
    out: list[str] = []
    for child in node.get("children") or []:
        out.extend(_tree_words(child))
    return out


def _align_words_to_sentence(words: list[str], sentence: str | None) -> tuple[list[dict[str, Any]], list[str]]:
    """Align book-tree terminals monotonically without substring false matches.

    The source's tokenization is retained. Matching is case-insensitive but an
    alphanumeric terminal must begin/end on a token boundary, so e.g. ``he``
    cannot accidentally align to the initial letters of ``theory``.
    """
    tokens = []
    errors = []
    cursor = 0
    sentence = sentence or ""
    search_sentence = sentence.replace("’", "'")
    for i, word in enumerate(words):
        search_word = word.replace("’", "'")
        if not sentence:
            tokens.append({"index": i, "text": word, "char_span": [0, 0]})
            continue
        found = None
        for match in re.finditer(re.escape(search_word), search_sentence[cursor:], re.IGNORECASE):
            pos = cursor + match.start()
            end = cursor + match.end()
            has_word_chars = any(ch.isalnum() or ch == "_" for ch in word)
            left_ok = (search_word.startswith("'") and pos == cursor or not has_word_chars or pos == 0
                       or not (sentence[pos - 1].isalnum() or sentence[pos - 1] == "_"))
            right_ok = (not has_word_chars or end == len(sentence)
                        or not (sentence[end].isalnum() or sentence[end] == "_"))
            if left_ok and right_ok:
                found = (pos, end)
                break
        if found is None:
            errors.append(f"tree terminal {word!r} could not be aligned to the sentence")
            tokens.append({"index": i, "text": word, "char_span": [cursor, cursor]})
            continue
        pos, end = found
        tokens.append({"index": i, "text": word, "char_span": [pos, end]})
        cursor = end
    return tokens, errors


def _preserve_source_node_metadata(out: dict[str, Any],
                                   raw: dict[str, Any]) -> dict[str, Any]:
    """Carry source-only node metadata without miscasting it as B-R structure.

    Diagram references are kept in source_refs. Symbols, multiword markers,
    verb-type notes, and any future node-level fields are retained verbatim in
    notes until a reviewed typed schema field is approved.
    """
    refs = []
    existing_refs = raw.get("source_refs")
    if isinstance(existing_refs, list):
        refs.extend(str(value) for value in existing_refs)
    elif existing_refs not in (None, ""):
        out.setdefault("notes", []).append(
            "unmapped_source_refs=" + json.dumps(existing_refs, ensure_ascii=False, sort_keys=True))
    if raw.get("ref") not in (None, ""):
        refs.append(str(raw["ref"]))
    if refs:
        # Stable order, but avoid duplicating a reference repeated in both fields.
        out["source_refs"] = list(dict.fromkeys(refs))

    raw_notes = raw.get("notes")
    if isinstance(raw_notes, list):
        out.setdefault("notes", []).extend(str(note) for note in raw_notes)
    elif raw_notes not in (None, ""):
        out.setdefault("notes", []).append(
            "source_node_notes=" + json.dumps(raw_notes, ensure_ascii=False, sort_keys=True))

    semantic_fields = {
        "id", "label", "children", "word", "triangle", "words", "features",
        "index", "gap", "ellipsis", "elided", "starred", "ref", "source_refs",
        "notes",
    }
    for key in sorted(set(raw) - semantic_fields):
        out.setdefault("notes", []).append(
            f"source_node_metadata:{key}="
            + json.dumps(raw[key], ensure_ascii=False, sort_keys=True))

    if raw.get("starred"):
        out.setdefault("notes", []).append("source tree node is starred")
    if "ellipsis" in raw and raw.get("ellipsis"):
        out.setdefault("notes", []).append("source ellipsis marker retained")
    if raw.get("elided"):
        out.setdefault("notes", []).append("source elided terminal retained")
    return out


def _build_canonical_node(raw: dict[str, Any], tokens: list[dict[str, Any]], cursor: list[int],
                          node_id: str, notes: list[str]) -> dict[str, Any]:
    if raw.get("gap") is True:
        out = {"id": node_id, "gap": True}
        if raw.get("index") is not None:
            out["index"] = raw["index"]
        return _preserve_source_node_metadata(out, raw)

    if "word" in raw:
        word = str(raw["word"])
        if raw.get("ellipsis") or word == "...":
            notes.append("Source ellipsis marker retained as a non-overt placeholder.")
            out = {"id": node_id, "word": word, "elided": True}
            return _preserve_source_node_metadata(out, raw)
        if raw.get("elided"):
            notes.append(f"Source elided terminal {word!r} retained without overt token coverage.")
            out = {"id": node_id, "word": word, "elided": True}
            return _preserve_source_node_metadata(out, raw)
        idx = cursor[0]
        if idx >= len(tokens) or tokens[idx]["text"] != word:
            raise ValueError(f"terminal {word!r} does not align with source token {idx}")
        cursor[0] += 1
        out = {"id": node_id, "word": word, "token_span": [idx, idx + 1]}
        return _preserve_source_node_metadata(out, raw)

    if raw.get("triangle"):
        words = [str(w) for w in raw.get("words", []) if str(w) != "..."]
        start = cursor[0]
        for word in words:
            idx = cursor[0]
            if idx >= len(tokens) or tokens[idx]["text"] != word:
                raise ValueError(f"triangle word {word!r} does not align to source token {idx}")
            cursor[0] += 1
        if not words:
            raise ValueError("triangle contains no overt source words")
        out = {"id": node_id, "label": str(raw.get("label", "")),
               "triangle": True, "words": words,
               "token_span": [start, cursor[0]]}
        if not raw.get("label"):
            out.pop("label", None)
            out["unlabelled"] = True
        if raw.get("index") is not None:
            out["index"] = raw["index"]
        if "..." in raw.get("words", []):
            notes.append("A source ellipsis marker inside a triangle was omitted from overt token coverage.")
        return _preserve_source_node_metadata(out, raw)

    if raw.get("elided") and "word" not in raw:
        if raw.get("symbol") != "E":
            raise ValueError("unknown non-lexical elision symbol")
        return _preserve_source_node_metadata({
            "id": node_id, "empty": True, "label": "E", "empty_role": "ellipsis",
            "token_span": [cursor[0], cursor[0]],
        }, raw)

    label = raw.get("label")
    children_raw = raw.get("children")
    if not isinstance(label, str) or not label:
        raise ValueError("gold branch node is missing a label")
    if children_raw == [] and label in {"DET", "C1"}:
        return _preserve_source_node_metadata({
            "id": node_id, "empty": True, "label": label,
            "empty_role": {"DET": "determiner", "C1": "complementiser"}[label],
            "token_span": [cursor[0], cursor[0]],
        }, raw)
    if not isinstance(children_raw, list) or not children_raw:
        raise ValueError(f"gold branch {label!r} has no children")
    children = [_build_canonical_node(child, tokens, cursor, f"{node_id}-{i}", notes)
                for i, child in enumerate(children_raw)]
    overt = [child.get("token_span") for child in children
             if child.get("token_span") and not child.get("empty")]
    span = [min(item[0] for item in overt), max(item[1] for item in overt)] if overt else None
    out = {"id": node_id, "label": label, "children": children}
    if span is not None:
        out["token_span"] = span
    if "features" in raw:
        features = raw.get("features")
        if isinstance(features, list) and all(isinstance(item, str) for item in features):
            out["features"] = list(features)
        else:
            notes.append(f"Invalid source feature metadata retained in notes for {label!r}.")
            out.setdefault("notes", []).append(
                "invalid_source_features=" + json.dumps(features, ensure_ascii=False))
    if raw.get("index") is not None:
        out["index"] = raw["index"]
    return _preserve_source_node_metadata(out, raw)

def canonicalize_gold_record(record: dict[str, Any], chapter_data: dict[str, Any]) -> dict[str, Any]:
    """Project one existing chapter tree record into the canonical schema.

    This function never edits the source JSON. Unsupported metadata is retained
    in notes and reported; alternatives with tree shapes are mapped explicitly.
    """
    chapter = int(chapter_data.get("chapter", 0))
    profile = convention_profile(chapter,
                                 bool(record.get("appendix_nom")) if chapter == 7 else None)
    raw_tree = record.get("tree")
    if not isinstance(raw_tree, dict):
        return {"status": "rejected", "tree": None,
                "errors": ["gold record has no tree object"]}
    sentence = record.get("sentence")
    words = _tree_words(raw_tree)
    tokens, alignment_errors = _align_words_to_sentence(words, sentence)
    if alignment_errors:
        return {"status": "unresolved", "tree": None, "errors": alignment_errors,
                "raw_tree": raw_tree}
    notes: list[str] = []
    cursor = [0]
    tree_id = str(record.get("id") or _stable_id(f"ch{chapter}", json.dumps(raw_tree, sort_keys=True)))
    try:
        root = _build_canonical_node(raw_tree, tokens, cursor, f"{tree_id}-root", notes)
        if cursor[0] != len(tokens):
            raise ValueError(f"tree consumed {cursor[0]} of {len(tokens)} source token(s)")
    except (TypeError, ValueError) as exc:
        return {"status": "unresolved", "tree": None, "errors": [str(exc)],
                "raw_tree": raw_tree}

    raw_review_status = record.get("review_status")
    valid_review_statuses = {
        "NOT_REVIEWED", "INDEPENDENTLY_REVIEWED", "HUMAN_APPROVED", "REJECTED",
    }
    if raw_review_status in valid_review_statuses:
        review_status = raw_review_status
        default_review_note = (
            f"Review status {review_status} imported from the source record."
        )
    else:
        review_status = "NOT_REVIEWED"
        if raw_review_status is None:
            default_review_note = (
                "IMG indicates image evidence only; this import does not establish "
                "independent review or human approval."
            )
        else:
            default_review_note = (
                "Unrecognized source review_status "
                + json.dumps(raw_review_status, ensure_ascii=False, sort_keys=True)
                + "; canonical status retained as NOT_REVIEWED. IMG indicates image "
                "evidence only and does not establish independent review or human approval."
            )
    source = {
        "book": BOOK_TITLE, "edition": BOOK_EDITION, "chapter": chapter,
        "evidence_status": record.get("status") if record.get("status") in _EVIDENCE else "NEEDS_REVIEW",
        "review_status": review_status,
        "review_note": str(record.get("review_note") or default_review_note),
        "source_record_id": tree_id,
    }
    if record.get("page") is not None:
        source["printed_page"] = int(record["page"])
    if record.get("fig") is not None:
        source["figure_id"] = str(record["fig"])
    movement_records: list[dict[str, Any]] = []
    # Ch9 movement notes identify linguistic positions in prose, not stable
    # node IDs. Preserve those labels as a source-linked movement note rather
    # than inventing node-to-node links.
    for movement in record.get("movement") or []:
        if isinstance(movement, dict):
            source_position = str(movement.get("from", "unspecified source position"))
            target_position = str(movement.get("to", "unspecified target position"))
            movement_records.append({
                "kind": "movement",
                "source_ref": tree_id,
                "note": f"Source-described movement: {source_position} → {target_position}",
            })
        else:
            notes.append("unmapped_movement_item=" + json.dumps(movement, ensure_ascii=False, sort_keys=True))
    external_rows = []
    if isinstance(record.get("external_controller"), dict):
        external_rows.append(record["external_controller"])
    plural_external = record.get("external_controllers")
    if isinstance(plural_external, list):
        external_rows.extend(x for x in plural_external if isinstance(x, dict))
        invalid_external = [x for x in plural_external if not isinstance(x, dict)]
        if invalid_external:
            notes.append("unmapped_external_controllers=" + json.dumps(invalid_external, ensure_ascii=False, sort_keys=True))
    elif plural_external not in (None, "", [], {}):
        notes.append("unmapped_external_controllers=" + json.dumps(plural_external, ensure_ascii=False, sort_keys=True))
    for external in external_rows:
        relation = {"kind": "external_controller"}
        if external.get("index") is not None:
            relation["index"] = external["index"]
        if external.get("controller") is not None:
            relation["controller"] = str(external["controller"])
        if external.get("source") is not None:
            relation["source_ref"] = str(external["source"])
        movement_records.append(relation)
    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "tree_id": tree_id,
        "tokens": tokens, "convention_profile": profile,
        "source": source, "root": root, "movement": movement_records,
        "accepted_alternatives": [], "notes": notes,
    }
    if isinstance(sentence, str):
        envelope["sentence"] = sentence
    if record.get("note"):
        envelope["notes"].append(str(record["note"]))
    represented_fields = {
        "id", "fig", "page", "sentence", "status", "tree", "note",
        "appendix_nom", "accepted_alternatives", "external_controller",
        "external_controllers", "movement", "review_status", "review_note",
    }
    # Preserve every remaining chapter-specific answer/interpretation field.
    # The schema's notes array is intentionally used as a lossless, readable
    # escape hatch until dedicated typed fields are approved.
    for field in sorted(set(record) - represented_fields):
        value = record[field]
        if value not in (None, [], {}, ""):
            envelope["notes"].append(
                f"source_metadata:{field}={json.dumps(value, ensure_ascii=False, sort_keys=True)}")

    alternative_errors = []
    for i, alt in enumerate(record.get("accepted_alternatives") or []):
        if not isinstance(alt, dict) or not isinstance(alt.get("tree"), dict):
            alternative_errors.append(f"accepted alternative {i + 1} has no tree shape; its metadata is retained in notes")
            envelope["notes"].append("unmaterialized_accepted_alternative=" + json.dumps(alt, ensure_ascii=False, sort_keys=True))
            continue
        alt_words = _tree_words(alt["tree"])
        if alt_words != words:
            alternative_errors.append(f"accepted alternative {i + 1} has different terminal sequence")
            envelope["notes"].append("unaligned_accepted_alternative=" + json.dumps(alt, ensure_ascii=False, sort_keys=True))
            continue
        alt_cursor = [0]
        try:
            alt_root = _build_canonical_node(alt["tree"], tokens, alt_cursor,
                                        f"{tree_id}-alt-{i + 1}", envelope["notes"])
            if alt_cursor[0] != len(tokens):
                raise ValueError(f"alternative consumed {alt_cursor[0]} of {len(tokens)} source token(s)")
        except (TypeError, ValueError) as exc:
            alternative_errors.append(f"accepted alternative {i + 1} could not be projected: {exc}")
            envelope["notes"].append("unprojected_accepted_alternative=" + json.dumps(alt, ensure_ascii=False, sort_keys=True))
            continue
        acceptance = alt.get("acceptance", "ACCEPTED")
        if acceptance not in _ACCEPTANCE:
            acceptance = "ACCEPTED"
        alternative = {"analysis_id": f"{tree_id}-alt-{i + 1}",
                       "root": alt_root, "acceptance": acceptance,
                       "source_refs": [tree_id]}
        if alt.get("note") or alt.get("label"):
            alternative["rationale"] = str(alt.get("note") or alt.get("label"))
        alt_metadata = {k: v for k, v in alt.items()
                        if k not in {"tree", "acceptance", "note", "label"}}
        if alt_metadata:
            envelope["notes"].append(
                f"accepted_alternative_metadata:{i + 1}="
                + json.dumps(alt_metadata, ensure_ascii=False, sort_keys=True))
        envelope["accepted_alternatives"].append(alternative)
    validation = validate_canonical_tree(envelope)
    errors = list(validation["errors"]) + alternative_errors
    return {"status": "normalized" if not errors else "unresolved",
            "tree": envelope if not errors else None,
            "partial_tree": envelope if errors else None,
            "errors": errors, "warnings": validation["warnings"],
            "raw_tree": raw_tree if errors else None}


def validate_canonical_tree(envelope: dict[str, Any]) -> dict[str, Any]:
    """Validate schema-level and B-R structural invariants without dependencies."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(envelope, dict):
        return {"valid": False, "errors": ["canonical envelope must be an object"], "warnings": []}
    required = {"schema_version", "tree_id", "tokens", "convention_profile",
                "source", "root", "movement", "accepted_alternatives"}
    allowed_envelope = required | {"sentence", "notes"}
    missing = sorted(required - set(envelope))
    if missing:
        errors.append("missing required envelope field(s): " + ", ".join(missing))
    unknown_envelope = sorted(set(envelope) - allowed_envelope)
    if unknown_envelope:
        errors.append("unsupported envelope field(s): " + ", ".join(unknown_envelope))
    if envelope.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(f"schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
    if not isinstance(envelope.get("tree_id"), str) or not envelope.get("tree_id"):
        errors.append("tree_id must be a non-empty string")
    profile = envelope.get("convention_profile")
    errors.extend(_profile_errors(profile))
    if isinstance(profile, dict):
        profile_unknown = sorted(set(profile) - {"chapter", "version", "appendix_nom", "profile_id"})
        if profile_unknown:
            errors.append("unsupported convention_profile field(s): " + ", ".join(profile_unknown))
    chapter = profile.get("chapter", 0) if isinstance(profile, dict) else 0
    tokens = envelope.get("tokens")
    if not isinstance(tokens, list):
        errors.append("tokens must be an array")
        tokens = []
    sentence = envelope.get("sentence")
    previous_end = -1
    for i, token in enumerate(tokens):
        if not isinstance(token, dict):
            errors.append(f"token {i} must be an object")
            continue
        token_unknown = sorted(set(token) - {"index", "text", "char_span", "pos", "parser_tag"})
        if token_unknown:
            errors.append(f"token {i} has unsupported field(s): " + ", ".join(token_unknown))
        if isinstance(token.get("index"), bool) or not isinstance(token.get("index"), int) or token.get("index") != i:
            errors.append(f"token {i} index must equal its zero-based integer position")
        if not isinstance(token.get("text"), str) or not token.get("text"):
            errors.append(f"token {i} text must be non-empty")
        span = token.get("char_span")
        if not (isinstance(span, list) and len(span) == 2
                and all(isinstance(x, int) and not isinstance(x, bool) for x in span)
                and 0 <= span[0] <= span[1]):
            errors.append(f"token {i} char_span must be [start, end] with non-negative integers")
        else:
            if span[0] < previous_end:
                errors.append(f"token {i} character span overlaps or precedes the prior token")
            previous_end = span[1]
            if isinstance(sentence, str) and span[1] > len(sentence):
                errors.append(f"token {i} character span exceeds sentence length")
            if isinstance(sentence, str) and span[1] > span[0] and sentence[span[0]:span[1]] != token.get("text"):
                warnings.append(f"token {i} surface differs from sentence substring; this may reflect source tokenization")

    source = envelope.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        source_allowed = {"book", "edition", "chapter", "section", "printed_page", "pdf_page",
                          "figure_id", "evidence_status", "review_status", "review_note", "source_record_id"}
        source_unknown = sorted(set(source) - source_allowed)
        if source_unknown:
            errors.append("unsupported source field(s): " + ", ".join(source_unknown))
        if not isinstance(source.get("book"), str) or not source.get("book"):
            errors.append("source.book must be non-empty")
        if source.get("evidence_status") not in _EVIDENCE:
            errors.append("source.evidence_status is not recognized")
        if source.get("review_status") is not None and source.get("review_status") not in _REVIEW:
            errors.append("source.review_status is not recognized")
        if source.get("chapter") != chapter:
            errors.append("source.chapter must match convention_profile.chapter")
        for page_key in ("printed_page", "pdf_page"):
            page = source.get(page_key)
            if page is not None and (isinstance(page, bool) or not isinstance(page, int) or page < 1):
                errors.append(f"source.{page_key} must be a positive integer")

    ids: set[str] = set()
    node_kinds: dict[str, str] = {}
    node_indices: dict[str, int | None] = {}
    covered: list[int] = []
    def walk(node: Any, path: str, parent_label: str | None = None) -> tuple[int, int] | None:
        if not isinstance(node, dict):
            errors.append(f"{path} must be a node object")
            return None
        for metadata_key in ("source_refs", "notes"):
            if metadata_key in node:
                metadata_value = node[metadata_key]
                if (not isinstance(metadata_value, list)
                        or any(not isinstance(value, str) for value in metadata_value)):
                    errors.append(f"{path}.{metadata_key} must be an array of strings")
        node_id = node.get("id")
        if node_id is not None:
            if not isinstance(node_id, str) or not node_id:
                errors.append(f"{path}.id must be a non-empty string")
            elif node_id in ids:
                errors.append(f"duplicate node id {node_id!r}")
            else:
                ids.add(node_id)
        kind = ("terminal" if "word" in node else "gap" if node.get("gap") is True
                else "empty" if node.get("empty") is True
                else "triangle" if node.get("triangle") is True else "branch")
        if node_id is not None and isinstance(node_id, str):
            node_kinds[node_id] = kind
        if node.get("empty") is True:
            if envelope.get("schema_version") != "1.1.0":
                errors.append(f"{path} zero-word nodes require schema v1.1.0")
            unknown = set(node) - {"id", "empty", "label", "empty_role", "token_span", "source_refs", "notes"}
            label = node.get("label")
            roles = {"DET": ("determiner", 7), "C1": ("complementiser", 9), "E": ("ellipsis", 5)}
            role, introduced = roles.get(label, (None, 99))
            if unknown or role is None or node.get("empty_role") != role:
                errors.append(f"{path} unsupported empty-category shape or role")
            if chapter < introduced:
                errors.append(f"{path} empty {label} is not introduced in this chapter")
            span = node.get("token_span")
            if not (isinstance(span, list) and len(span) == 2
                    and all(isinstance(value, int) and not isinstance(value, bool) for value in span)
                    and 0 <= span[0] == span[1] <= len(tokens)):
                errors.append(f"{path} empty node must have an in-range zero-width span")
            return None
        if "word" in node:
            unknown = sorted(set(node) - {"id", "word", "pos", "elided", "token_span", "source_refs", "notes"})
            if unknown:
                errors.append(f"{path} terminal has unsupported field(s): " + ", ".join(unknown))
            if "children" in node or "triangle" in node or "gap" in node:
                errors.append(f"{path} terminal cannot also be a branch, triangle or gap")
            word = node.get("word")
            if not isinstance(word, str) or not word:
                errors.append(f"{path}.word must be non-empty")
            if "elided" in node and not isinstance(node.get("elided"), bool):
                errors.append(f"{path}.elided must be a boolean")
            if node.get("elided"):
                return None
            span = node.get("token_span")
            if not (isinstance(span, list) and len(span) == 2
                    and all(isinstance(value, int) and not isinstance(value, bool) for value in span)):
                errors.append(f"{path}.token_span must be a two-integer half-open span")
                return None
            start, end = span
            if not (0 <= start < end <= len(tokens)):
                errors.append(f"{path}.token_span is out of range")
                return None
            if end != start + 1:
                errors.append(f"{path}.token_span must cover exactly one token")
                return None
            covered.append(start)
            if tokens[start].get("text") != word:
                errors.append(f"{path}.word does not match token {start}")
            return start, end
        if "gap" in node:
            unknown = sorted(set(node) - {"id", "gap", "index", "token_span", "source_refs", "notes"})
            if unknown:
                errors.append(f"{path} gap has unsupported field(s): " + ", ".join(unknown))
            if node.get("gap") is not True:
                errors.append(f"{path}.gap must be true")
            index = node.get("index")
            if index is not None and (not isinstance(index, int) or isinstance(index, bool) or index < 0):
                errors.append(f"{path}.index must be a non-negative integer or null")
            if node_id is not None:
                node_indices[node_id] = index
            return None
        if "triangle" in node or "words" in node:
            unknown = sorted(set(node) - {"id", "label", "unlabelled", "triangle", "words", "token_span", "index", "source_refs", "notes"})
            if unknown:
                errors.append(f"{path} triangle has unsupported field(s): " + ", ".join(unknown))
        if node.get("triangle") is True:
            if "children" in node or "gap" in node or "word" in node:
                errors.append(f"{path} triangle cannot also be a branch, terminal or gap")
            label = node.get("label")
            if node.get("unlabelled") is True:
                if label is not None or envelope.get("schema_version") != "1.1.0":
                    errors.append(f"{path} unlabelled triangle requires v1.1.0 and no label")
                if chapter < 9 or parent_label != "C2":
                    errors.append(f"{path} unlabelled triangle is only licensed under C2 from V9")
            elif not isinstance(label, str) or not label:
                errors.append(f"{path}.label must be non-empty")
            else:
                intro = _LABEL_INTRODUCED.get(label)
                if intro is not None and intro > chapter:
                    errors.append(f"{path} uses label {label!r} before its introduction in Chapter {intro}")
                elif intro is None:
                    warnings.append(f"{path} uses label {label!r} not in the core label inventory; retain source-specific review")
            words = node.get("words")
            if not isinstance(words, list) or not words or any(not isinstance(w, str) or not w for w in words):
                errors.append(f"{path}.words must contain one or more non-empty strings")
                return None
            span = node.get("token_span")
            if not (isinstance(span, list) and len(span) == 2
                    and all(isinstance(value, int) and not isinstance(value, bool) for value in span)
                    and 0 <= span[0] < span[1] <= len(tokens)):
                errors.append(f"{path}.token_span is out of range")
                return None
            start, end = span
            index = node.get("index")
            if index is not None and (not isinstance(index, int) or isinstance(index, bool) or index < 0):
                errors.append(f"{path}.index must be a non-negative integer or null")
            if node_id is not None:
                node_indices[node_id] = index
            if end - start != len(words):
                errors.append(f"{path} triangle token_span width must equal words length")
            else:
                for offset, word in enumerate(words):
                    index = start + offset
                    covered.append(index)
                    if tokens[index].get("text") != word:
                        errors.append(f"{path}.words[{offset}] does not match token {index}")
            return start, end

        branch_unknown = sorted(set(node) - {"id", "label", "features", "index", "token_span", "children", "source_refs", "notes"})
        if branch_unknown:
            errors.append(f"{path} branch has unsupported field(s): " + ", ".join(branch_unknown))
        if node.get("triangle") is True or node.get("gap") is True or "word" in node:
            errors.append(f"{path} branch has incompatible node markers")
        label = node.get("label")
        children = node.get("children")
        if not isinstance(label, str) or not label:
            errors.append(f"{path}.label must be non-empty")
        else:
            intro = _LABEL_INTRODUCED.get(label)
            if intro is not None and intro > chapter:
                errors.append(f"{path} uses label {label!r} before its introduction in Chapter {intro}")
            elif intro is None:
                warnings.append(f"{path} uses label {label!r} not in the core label inventory; retain source-specific review")
        features = node.get("features", [])
        if not isinstance(features, list):
            errors.append(f"{path}.features must be an array")
            features = []
        for feature in features:
            if not isinstance(feature, str):
                errors.append(f"{path} feature values must be strings")
                continue
            if feature not in _FEATURE_INTRODUCED:
                errors.append(f"{path} uses unknown feature {feature!r}")
            elif _FEATURE_INTRODUCED[feature] > chapter:
                errors.append(f"{path} uses feature {feature!r} before Chapter {_FEATURE_INTRODUCED[feature]}")
            if feature in _VERB_SUBCATEGORIES | {"phrasal"} and label != "V":
                errors.append(f"{path} feature {feature!r} is only licensed on a V node")
            if feature in {"pres", "past"} and label not in {"V", "MOD", "PERF", "PROG", "PASS", "TENSE"}:
                errors.append(f"{path} tense feature {feature!r} is not licensed on {label!r}")
            if feature == "-tense" and label not in {"AUX", "V", "PERF"}:
                errors.append(f"{path} feature '-tense' is not licensed on {label!r} in the current convention inventory")
        if label == "V" and chapter >= 4 and chapter <= 9:
            if not (set(features) & _VERB_SUBCATEGORIES):
                errors.append(f"{path} V node in V{chapter} requires a V4 sub-categorisation feature")
        index = node.get("index")
        if index is not None and (not isinstance(index, int) or isinstance(index, bool) or index < 0):
            errors.append(f"{path}.index must be a non-negative integer or null")
        if node_id is not None:
            node_indices[node_id] = index
        if not isinstance(children, list) or not children:
            errors.append(f"{path}.children must be a non-empty array")
            return None
        child_spans = []
        for i, child in enumerate(children):
            span = walk(child, f"{path}.children[{i}]", label)
            if span:
                child_spans.append(span)
        if not child_spans:
            return None
        for left, right in zip(child_spans, child_spans[1:]):
            if left[1] > right[0]:
                errors.append(f"{path} children overlap or are out of token order")
        span = [child_spans[0][0], child_spans[-1][1]]
        declared = node.get("token_span")
        if declared is not None:
            if not (isinstance(declared, list) and len(declared) == 2
                    and all(isinstance(value, int) and not isinstance(value, bool) for value in declared)
                    and 0 <= declared[0] <= declared[1] <= len(tokens)):
                errors.append(f"{path}.token_span must be a valid two-integer half-open span")
            elif declared != span:
                errors.append(f"{path}.token_span must equal the span derived from its children")
        return tuple(span)

    root_span = walk(envelope.get("root"), "root")
    if tokens:
        if sorted(covered) != list(range(len(tokens))):
            errors.append("overt terminal/triangle coverage must include each token exactly once")
        if root_span and root_span != (0, len(tokens)):
            errors.append("root token_span must cover all canonical tokens")
    elif root_span is not None:
        errors.append("a tree with no tokens cannot contain overt token spans")

    movement = envelope.get("movement")
    if not isinstance(movement, list):
        errors.append("movement must be an array")
    else:
        known_ids = ids
        for i, item in enumerate(movement):
            if not isinstance(item, dict) or item.get("kind") not in {
                    "movement", "control", "co_reference", "external_controller"}:
                errors.append(f"movement[{i}] has an invalid kind")
                continue
            item_unknown = sorted(set(item) - {"kind", "from_node_id", "to_node_id", "gap_node_id",
                                               "index", "controller", "source_ref", "note"})
            if item_unknown:
                errors.append(f"movement[{i}] has unsupported field(s): " + ", ".join(item_unknown))
            for key in ("from_node_id", "to_node_id", "gap_node_id"):
                if item.get(key) and item[key] not in known_ids:
                    errors.append(f"movement[{i}].{key} refers to an unknown node id")
            index = item.get("index")
            if index is not None and (not isinstance(index, int) or isinstance(index, bool) or index < 0):
                errors.append(f"movement[{i}].index must be a non-negative integer")
            if item.get("kind") == "external_controller" and index is not None:
                if index not in {value for value in node_indices.values() if value is not None}:
                    errors.append(f"movement[{i}] external-controller index does not match any indexed node or gap")
            gap_id = item.get("gap_node_id")
            if gap_id:
                if node_kinds.get(gap_id) != "gap":
                    errors.append(f"movement[{i}].gap_node_id must refer to a gap node")
                index = item.get("index")
                gap_index = node_indices.get(gap_id)
                if index is not None and (not isinstance(index, int) or isinstance(index, bool) or index < 0):
                    errors.append(f"movement[{i}].index must be a non-negative integer")
                if index is not None and gap_index is not None and index != gap_index:
                    errors.append(f"movement[{i}] index does not match the linked gap index")
                if (profile.get("version") in {"V10", "FINAL"}
                        and item.get("kind") in {"movement", "control"}
                        and (index is None or gap_index is None)):
                    errors.append(f"movement[{i}] requires matching indices on a V10/FINAL movement or control gap")

    alternatives = envelope.get("accepted_alternatives")
    if not isinstance(alternatives, list):
        errors.append("accepted_alternatives must be an array")
    else:
        alternative_ids: set[str] = set()
        for i, alt in enumerate(alternatives):
            path = f"accepted_alternatives[{i}]"
            if not isinstance(alt, dict):
                errors.append(f"{path} must be an object")
                continue
            allowed_alt = {"analysis_id", "root", "acceptance", "rationale", "meaning_or_context", "source_refs", "notes"}
            alt_unknown = sorted(set(alt) - allowed_alt)
            if alt_unknown:
                errors.append(f"{path} has unsupported field(s): " + ", ".join(alt_unknown))
            if (not isinstance(alt.get("analysis_id"), str) or not alt.get("analysis_id")
                    or alt.get("acceptance") not in _ACCEPTANCE
                    or not isinstance(alt.get("root"), dict)):
                errors.append(f"{path} requires a non-empty string analysis_id, valid acceptance and root")
                continue
            if alt["analysis_id"] in alternative_ids:
                errors.append(f"{path}.analysis_id must be unique")
            alternative_ids.add(alt["analysis_id"])
            # Re-use the same envelope invariants against each alternative root.
            # This prevents an accepted alternative from bypassing token order,
            # span, label-introduction or node-shape checks.
            alt_envelope = dict(envelope)
            alt_envelope["tree_id"] = f"{envelope.get('tree_id')}-alternative-{i}"
            alt_envelope["root"] = alt["root"]
            alt_envelope["movement"] = []
            alt_envelope["accepted_alternatives"] = []
            alt_validation = validate_canonical_tree(alt_envelope)
            for error in alt_validation["errors"]:
                errors.append(f"{path}: {error}")
            warnings.extend(f"{path}: {warning}" for warning in alt_validation["warnings"])

    return {"valid": not errors, "errors": errors, "warnings": warnings}
