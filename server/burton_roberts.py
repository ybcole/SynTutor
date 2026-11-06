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
    leaf_text = [str(x.get("surface", "")) for x in leaves]
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
        "source": {"book": BOOK_TITLE, "chapter": 2,
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


def build_canonical_analysis(analysis: dict[str, Any], chapter: int | None = None,
                             appendix_nom: bool | None = None,
                             correction: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build the stable API wrapper around a canonical tree or unresolved state."""
    profile = convention_profile(chapter, appendix_nom)
    result = normalize_benepar_candidate(analysis, profile)
    result["convention_profile"] = profile
    result.setdefault("diagnostics", {
        "parser": "benepar_en3", "parse_string": analysis.get("parse_string"),
        "raw_candidate_tree": analysis.get("root"),
        "token_count": len(analysis.get("tokens") or []),
    })
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
    if node.get("gap") is True:
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
    for i, word in enumerate(words):
        if not sentence:
            tokens.append({"index": i, "text": word, "char_span": [0, 0]})
            continue
        found = None
        for match in re.finditer(re.escape(word), sentence[cursor:], re.IGNORECASE):
            pos = cursor + match.start()
            end = cursor + match.end()
            has_word_chars = any(ch.isalnum() or ch == "_" for ch in word)
            left_ok = (not has_word_chars or pos == 0
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


def _build_gold_node(raw: dict[str, Any], tokens: list[dict[str, Any]], cursor: list[int],
                     node_id: str, notes: list[str]) -> dict[str, Any]:
    if raw.get("gap") is True:
        index = raw.get("index")
        out = {"id": node_id, "gap": True}
        if index is not None:
            out["index"] = index
        return out
    if "word" in raw:
        word = str(raw["word"])
        if raw.get("ellipsis") or word == "...":
            notes.append("Source ellipsis marker retained as a non-overt placeholder.")
            return {"id": node_id, "word": word, "elided": True,
                    "notes": ["source_ellipsis_marker"]}
        if raw.get("elided"):
            notes.append(f"Source elided terminal {word!r} retained without overt token coverage.")
            return {"id": node_id, "word": word, "elided": True,
                    "notes": ["source_elided_terminal"]}
        idx = cursor[0]
        if idx >= len(tokens) or tokens[idx]["text"] != word:
            raise ValueError(f"terminal {word!r} does not align with source token {idx}")
        cursor[0] += 1
        return {"id": node_id, "word": word, "token_span": [idx, idx + 1]}
    if raw.get("triangle"):
        words = [str(w) for w in raw.get("words", []) if str(w) != "..."]
        start = cursor[0]
        for word in words:
            idx = cursor[0]
            if idx >= len(tokens) or tokens[idx]["text"] != word:
                raise ValueError(f"triangle word {word!r} does not align with source token {idx}")
            cursor[0] += 1
        if not words:
            raise ValueError("triangle contains no overt source words")
        out = {"id": node_id, "label": str(raw.get("label", "")),
               "triangle": True, "words": words,
               "token_span": [start, cursor[0]]}
        if raw.get("index") is not None:
            out["index"] = raw["index"]
        if "..." in raw.get("words", []):
            notes.append("A source ellipsis marker inside a triangle was omitted from overt token coverage.")
        return out
    label = raw.get("label")
    children_raw = raw.get("children")
    if not isinstance(label, str) or not label:
        raise ValueError("gold branch node is missing a label")
    if not isinstance(children_raw, list) or not children_raw:
        raise ValueError(f"gold branch {label!r} has no children")
    children = [_build_gold_node(child, tokens, cursor, f"{node_id}-{i}", notes)
                for i, child in enumerate(children_raw)]
    overt = [c.get("token_span") for c in children if c.get("token_span")]
    span = [min(x[0] for x in overt), max(x[1] for x in overt)] if overt else None
    out = {"id": node_id, "label": label, "children": children}
    if span is not None:
        out["token_span"] = span
    features = raw.get("features")
    if features:
        if isinstance(features, list) and all(isinstance(x, str) for x in features):
            out["features"] = list(features)
        else:
            notes.append(f"Invalid source feature metadata retained in notes for {label!r}.")
            out["notes"] = ["invalid_source_features=" + json.dumps(features, ensure_ascii=False)]
    if raw.get("index") is not None:
        out["index"] = raw["index"]
    if raw.get("starred"):
        out.setdefault("notes", []).append("source tree is starred")
    return out


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
        root = _build_gold_node(raw_tree, tokens, cursor, f"{tree_id}-root", notes)
        if cursor[0] != len(tokens):
            raise ValueError(f"tree consumed {cursor[0]} of {len(tokens)} source token(s)")
    except (TypeError, ValueError) as exc:
        return {"status": "unresolved", "tree": None, "errors": [str(exc)],
                "raw_tree": raw_tree}

    source = {"book": BOOK_TITLE, "chapter": chapter,
              "evidence_status": record.get("status") if record.get("status") in _EVIDENCE else "NEEDS_REVIEW",
              "source_record_id": tree_id}
    if record.get("page") is not None:
        source["printed_page"] = int(record["page"])
    if record.get("fig") is not None:
        source["figure_id"] = str(record["fig"])
    movement_records: list[dict[str, Any]] = []
    external = record.get("external_controller")
    if isinstance(external, dict):
        relation = {"kind": "external_controller"}
        if external.get("index") is not None:
            relation["index"] = external["index"]
        if external.get("controller") is not None:
            relation["controller"] = str(external["controller"])
        if external.get("source") is not None:
            relation["source_ref"] = str(external["source"])
        movement_records.append(relation)
    elif external not in (None, "", [], {}):
        notes.append("unmapped_external_controller=" + json.dumps(external, ensure_ascii=False, sort_keys=True))
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
    for field in ("book_simplification", "clause_id", "movement"):
        if record.get(field) not in (None, [], {}, ""):
            envelope["notes"].append(f"source_metadata:{field}={json.dumps(record[field], ensure_ascii=False, sort_keys=True)}")

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
            alt_root = _build_gold_node(alt["tree"], tokens, alt_cursor,
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
    if envelope.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
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
