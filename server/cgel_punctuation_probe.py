"""Offline Chapter 20 punctuation evidence, candidate-only and production-disabled.

Every checker is keyed to a Cambridge diagnostic specification and returns
character spans plus nonautomatic edit hints. It does not enable a runtime rule,
claim detector accuracy, or bypass source review.
"""
from __future__ import annotations

import re
from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


QUOTE_CHARS = '"“”‘’'
PUNCTUATION = {".", ",", ":", ";", "?", "!", "-LRB-", "-RRB-", "-LSB-", "-RSB-"}
CONNECTIVES = {"however", "nevertheless", "nonetheless"}
REPORTING_VERBS = {
    "ask", "asked", "asks", "asking", "wonder", "wondered", "wonders", "wondering",
    "inquire", "inquired", "enquire", "enquired", "say", "said", "says", "saying",
    "reply", "replied", "replies", "add", "added", "adds", "answer", "answered",
    "explain", "explained", "remark", "remarked", "observe", "observed", "note",
    "noted", "insist", "insisted", "suggest", "suggested", "warn", "warned",
    "claim", "claimed", "complain", "complained", "whisper", "whispered",
    "shout", "shouted", "yell", "yelled", "continue", "continued", "begin",
    "began", "conclude", "concluded", "declare", "declared", "state", "stated",
    "tell", "told", "call", "called", "write", "wrote", "mutter", "muttered",
}
REPORTING_TAGS = REPORTING_VERBS | {"replied", "answered", "explained", "added"}
WH_WORDS = {"when", "where", "why", "how", "whether", "if", "who", "whom", "whose",
            "what", "which"}
ABBREVIATIONS = {
    "etc", "vs", "fig", "figs", "mr", "mrs", "ms", "dr", "prof", "st", "jr", "sr",
    "inc", "ltd", "co", "corp", "no", "nos", "gen", "sen", "rep", "rev", "hon",
    "capt", "lt", "col", "sgt", "mt", "ave", "blvd", "rd", "dept", "est", "approx",
    "min", "max", "vol", "vols", "pp", "p", "ch", "sec", "ed", "eds", "trans",
    "comp", "univ", "assn", "al", "ibid", "id", "cf", "viz",
}
NOMINAL_TYPES = {"NN", "NNS", "NNP", "NNPS", "NP", "PRP", "CD", "QP"}
MODAL_AUX = {"can", "could", "may", "might", "must", "shall", "should", "will",
             "would", "have", "has", "had", "am", "is", "are", "was", "were",
             "do", "does", "did"}
LEAF_SURFACES = {
    "-LRB-": "(", "-RRB-": ")", "-LSB-": "[", "-RSB-": "]",
    "-LCB-": "{", "-RCB-": "}",
}


def _result() -> dict[str, Any]:
    return {"status": "not_evaluated", "production_enabled": False,
            "candidates": [], "blocked": []}


def _edit(span: Any, replacement: str) -> dict[str, Any]:
    return {"char_span": list(span), "replacement": replacement,
            "requires_reparse": True, "safe_to_apply_automatically": False}


def _candidate(rule_id: str, pages: list[int], kind: str,
               span: list[int] | None = None, edit: dict[str, Any] | None = None,
               **relation: Any) -> dict[str, Any]:
    payload = {"kind": kind, **relation}
    if span is not None:
        payload.setdefault("mark_char_span", list(span))
    return {"rule_id": rule_id, "source_chapter": 20, "source_pages": pages,
            "relation": payload, "edit_hint": edit}


def _walk(node: dict[str, Any]):
    yield node
    for child in node.get("children", []):
        yield from _walk(child)


def _first_leaf(node: dict[str, Any]) -> dict[str, Any] | None:
    for leaf in _ordered_leaves(node):
        return leaf
    return None


def _last_leaf(node: dict[str, Any]) -> dict[str, Any] | None:
    last = None
    for leaf in _ordered_leaves(node):
        last = leaf
    return last


def _leaf_lower(leaf: dict[str, Any] | None) -> str:
    return (leaf or {}).get("surface", "").casefold().replace("’", "'")


def _align(sentence: str, tree: dict[str, Any]):
    leaves = list(_ordered_leaves(tree))
    spans: list[list[int]] = []
    cursor = 0
    for leaf in leaves:
        while cursor < len(sentence) and sentence[cursor].isspace():
            cursor += 1
        surface = leaf.get("surface", "")
        expected = LEAF_SURFACES.get(surface, surface)
        if expected in {"``", "''"}:
            if cursor >= len(sentence) or sentence[cursor] not in '"“”‘’':
                return None
            expected = sentence[cursor]
        if not expected:
            return None
        if sentence.startswith(expected, cursor):
            spans.append([cursor, cursor + len(expected)])
            cursor += len(expected)
            continue
        if expected in {"'", "’"} and cursor < len(sentence) and sentence[cursor] in {"'", "’"}:
            spans.append([cursor, cursor + 1])
            cursor += 1
            continue
        return None
    if sentence[cursor:].strip():
        return None
    return leaves, spans


def _node_span(node: dict[str, Any], spans: list[list[int]]) -> list[int]:
    start, end = node["span"]
    return [spans[start][0], spans[end - 1][1]]


def _inside_parentheses(sentence: str, index: int) -> bool:
    depth = 0
    for char in sentence[:index]:
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
    return depth > 0


def _starts_interrogative(node: dict[str, Any]) -> bool:
    leaf = _first_leaf(node)
    return bool(leaf) and _leaf_lower(leaf) in WH_WORDS


def _is_abbreviation_prefix(prefix: str) -> bool:
    if re.search(r"(?:[A-Za-z]\.)+[A-Za-z]$", prefix):
        return True
    match = re.search(r"([A-Za-z]+)$", prefix)
    return bool(match) and match.group(1).casefold() in ABBREVIATIONS


def _abbreviation_dot(sentence: str, index: int) -> bool:
    if index <= 0 or index >= len(sentence) or sentence[index] != ".":
        return False
    return _is_abbreviation_prefix(sentence[:index])


def _quoted_spans(sentence: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    for opener, closer in (("“", "”"), ("‘", "’"), ('"', '"')):
        cursor = 0
        while cursor < len(sentence):
            start = sentence.find(opener, cursor)
            if start < 0:
                break
            end = sentence.find(closer, start + 1)
            if end < 0:
                break
            spans.append((start, end + 1, opener))
            cursor = end + 1
    return sorted(spans)


def _vowel_sound(raw: str) -> bool | None:
    word = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", raw)
    if not word:
        return None
    lower = word.casefold()
    if lower.startswith(("hour", "honest", "honor", "honour", "heir", "herb")):
        return True
    if re.match(r"^(uni|use|usu|uti|uro|ubiq|eu|ewe|one|once|ouija)", lower):
        return False
    if lower[0] in "aeiou":
        return True
    if raw.isupper() and len(lower) == 1:
        return lower in "aefhilmnorsx"
    if raw.isupper() and len(lower) > 1 and lower[0] in "aefhilmnorsx":
        return True
    return False


def probe_apostrophe_shape(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"(?<!\w)‘(?=(?:n[’']|n\b|em\b|til\b|cause\b|bout\b|round\b|neath\b|twas\b|twere\b|tis\b))",
        re.IGNORECASE,
    )
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "OTH-671", [1725], "opening_quote_used_as_apostrophe",
            [match.start(), match.start() + 1],
            _edit([match.start(), match.start() + 1], "’"),
        ))
    return rows


def probe_parenthetical_article(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(a|an)(\s+)\(([^()]*)\)", sentence, re.IGNORECASE):
        inner = match.group(3).strip()
        expected = _vowel_sound(inner)
        if expected is None:
            continue
        wanted = "an" if expected else "a"
        observed = match.group(1)
        if observed.casefold() == wanted:
            continue
        replacement = wanted if observed.islower() else wanted.capitalize()
        span = [match.start(1), match.end(1)]
        rows.append(_candidate(
            "OTH-726", [1748], "article_before_parenthesised_element", span,
            _edit(span, replacement),
            observed_article=observed, expected_article=replacement,
        ))
    return rows


def probe_compound_numeral_hyphen(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(\s+)"
        r"(one|two|three|four|five|six|seven|eight|nine)\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(sentence):
        if sentence[match.end():].startswith("-"):
            continue
        span = [match.start(2), match.end(2)]
        rows.append(_candidate(
            "OTH-756", [1761], "compound_numeral_missing_hyphen", span,
            _edit(span, "-"),
            numeral_char_span=[match.start(), match.end()],
        ))
    return rows


def probe_abbreviation_full_stop(sentence: str) -> list[dict[str, Any]]:
    stripped = sentence.rstrip()
    if not stripped.endswith("..") or stripped.endswith("..."):
        return []
    extra = len(stripped) - 1
    abbreviation = extra - 1
    if abbreviation <= 0 or stripped[abbreviation - 1].isspace():
        return []
    if stripped[abbreviation - 1] == ".":
        return []
    if not _abbreviation_dot(stripped, abbreviation):
        return []
    span = [extra, extra + 1]
    return [_candidate(
        "OTH-764", [1764], "terminal_after_abbreviation_full_stop", span,
        _edit(span, ""),
        abbreviation_char_span=[max(0, abbreviation - 4), abbreviation + 1],
    )]


def probe_direct_speech_boundary(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = "|".join(sorted(REPORTING_VERBS, key=len, reverse=True))
    pattern = re.compile(rf"\b({verbs})(\s+)([\"“‘])", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        quote = match.group(3)
        closer = {"“": "”", "‘": "’", '"': '"'}[quote]
        if sentence.find(closer, match.start(3) + 1) < 0:
            continue
        span = [match.end(1), match.start(3)]
        rows.append(_candidate(
            "OTH-712", [1743], "missing_boundary_before_direct_speech", span,
            _edit(span, ", "),
            reporting_verb=match.group(1),
        ))
    return rows


def probe_parenthetical_insulation(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\(and\s+[^()]+\)", sentence, re.IGNORECASE):
        before = sentence[:match.start()].rstrip()
        after = sentence[match.end():].lstrip()
        word_match = re.search(r"([A-Za-z][A-Za-z’'-]*)$", before)
        if not word_match:
            continue
        head = word_match.group(1)
        plural_verb = re.match(r"([A-Za-z]+)", after)
        agreement_depends = (
            plural_verb is not None
            and plural_verb.group(1).casefold() in {"have", "are", "were", "do"}
            and not head.casefold().endswith("s")
        )
        pronoun_depends = bool(re.search(r"\b(them|they|these|those)\b", after[:100], re.IGNORECASE))
        if not agreement_depends and not pronoun_depends:
            continue
        span = list(match.span())
        rows.append(_candidate(
            "OTH-730", [1750], "parenthesised_coordinate_used_by_surrounding_text", span,
            _edit(span, match.group(0)[1:-1]),
            dependency="agreement" if agreement_depends else "pronoun",
        ))
    return rows


def probe_nested_quotes(sentence: str) -> list[dict[str, Any]]:
    rows = []
    stack: list[tuple[str, int]] = []
    reported: set[int] = set()
    for index, char in enumerate(sentence):
        if char in "“‘":
            if stack and stack[-1][0] == char and index not in reported:
                closer = "”" if char == "“" else "’"
                depth = 0
                closing = None
                for cursor in range(index, len(sentence)):
                    if sentence[cursor] == char:
                        depth += 1
                    elif sentence[cursor] == closer:
                        depth -= 1
                        if depth == 0:
                            closing = cursor
                            break
                if closing is not None:
                    replacement_open = "‘" if char == "“" else "“"
                    replacement_close = "’" if char == "“" else "”"
                    for cursor, replacement in ((index, replacement_open),
                                                (closing, replacement_close)):
                        if cursor in reported:
                            continue
                        reported.add(cursor)
                        rows.append(_candidate(
                            "OTH-737", [1753], "same_quote_type_at_nested_level",
                            [cursor, cursor + 1], _edit([cursor, cursor + 1], replacement),
                            paired_char_span=[index, closing + 1],
                        ))
            stack.append((char, index))
        elif char in "”’":
            if stack and ((stack[-1][0] == "“" and char == "”")
                          or (stack[-1][0] == "‘" and char == "’")):
                stack.pop()
    return rows


def probe_quoted_terminal_medial(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for start, end, _ in _quoted_spans(sentence):
        content = sentence[start + 1:end - 1].rstrip()
        if not content.endswith("."):
            continue
        dot = start + 1 + len(content) - 1
        if _abbreviation_dot(sentence, dot):
            continue
        after = sentence[end:]
        stripped = after.lstrip()
        if not stripped:
            continue
        words = re.findall(r"[A-Za-z]+", stripped)[:3]
        if not words:
            continue
        first = words[0]
        reporting = any(word.casefold() in REPORTING_TAGS for word in words)
        if first.casefold() in {"and", "but", "or", "so", "yet"}:
            edit = _edit([dot, dot + 1], "")
        elif reporting:
            edit = _edit([dot, dot + 1], ",")
        elif first[0].islower():
            edit = None
        else:
            continue
        rows.append(_candidate(
            "OTH-740", [1754], "quoted_terminal_inside_continuing_matrix",
            [dot, dot + 1], edit,
            quoted_char_span=[start, end],
        ))
    return rows


def probe_quoted_terminal_suppression(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"([?!])([”\"])\s*\.", sentence):
        mark = match.group(1)
        if sentence.rfind("“" if match.group(2) == "”" else '"', 0, match.start(1)) < 0:
            continue
        dot = match.end() - 1
        rows.append(_candidate(
            "OTH-743", [1755], "competing_full_stop_after_quoted_terminal",
            [dot, dot + 1], _edit([dot, dot + 1], ""),
            retained_terminal=mark,
        ))
    for match in re.finditer(r"\.([”\"])\s*([?!])", sentence):
        dot = match.start()
        if _abbreviation_dot(sentence, dot):
            continue
        rows.append(_candidate(
            "OTH-743", [1755], "competing_full_stop_inside_quotation",
            [dot, dot + 1], _edit([dot, dot + 1], ""),
            retained_terminal=match.group(2),
        ))
    return rows


def probe_embedded_question_terminal(sentence: str,
                                     tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or any(char in sentence for char in QUOTE_CHARS):
        return []
    leaves, spans = aligned
    if tree.get("type") != "S" or not leaves or leaves[-1].get("surface") != "?":
        return []

    def locate(node):
        children = node.get("children", [])
        for index, child in enumerate(children):
            if child.get("type") in {"SBAR", "S"} and index > 0:
                previous = children[index - 1]
                if (previous.get("pos", "").startswith("VB")
                        and _leaf_lower(previous) in REPORTING_VERBS
                        and index == len(children) - 1
                        and _starts_interrogative(child)):
                    return child
            found = locate(child)
            if found is not None:
                return found
        return None

    if locate(tree) is None:
        return []
    terminal = leaves[-1]
    span = spans[-1]
    return [_candidate(
        "OTH-688", [1733], "question_mark_on_subordinate_interrogative",
        span, _edit(span, "."),
        interrogative_char_span=_node_span(locate(tree), spans),
    )]


def probe_repeated_secondary(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None:
        return []
    leaves, spans = aligned
    parent = {}
    for node in _walk(tree):
        for child in node.get("children", []):
            parent[child["id"]] = node
    rows = []
    flagged = set()
    for mark, kind in ((":", "colon"), (";", "semicolon")):
        indices = [i for i, leaf in enumerate(leaves) if leaf.get("surface") == mark]
        for outer in indices:
            if _inside_parentheses(sentence, spans[outer][0]):
                continue
            owner = parent.get(leaves[outer]["id"])
            if not owner:
                continue
            children = owner.get("children", [])
            position = next((i for i, child in enumerate(children)
                             if child["id"] == leaves[outer]["id"]), None)
            if position is None or position + 1 >= len(children):
                continue
            right = children[position + 1]
            right_leaves = set(range(right["span"][0], right["span"][1]))
            for inner in indices:
                if inner != outer and inner in right_leaves and inner not in flagged:
                    flagged.add(inner)
                    span = spans[inner]
                    rows.append(_candidate(
                        "OTH-698", [1737, 1738], f"nested_{kind}_levels", span,
                        _edit(span, ","),
                        outer_char_span=spans[outer],
                    ))
    if tree.get("type") == "S" and len(flagged) == 0:
        children = tree.get("children", [])
        marks = [i for i, child in enumerate(children) if child.get("surface") == ";"]
        clauses = [child for child in children if child.get("type") == "S"]
        if len(marks) >= 2 and len(clauses) >= 3:
            first_leaves = list(_ordered_leaves(clauses[0]))
            plural_scope = any(
                leaf.get("pos") == "NNS"
                or _leaf_lower(leaf) in {"all", "every", "each", "many", "most", "some"}
                for leaf in first_leaves
            )
            second = _first_leaf(clauses[1])
            third = _first_leaf(clauses[2])
            if (plural_scope and second is not None and third is not None
                    and second.get("pos") == "NNP"
                    and _leaf_lower(third) in {"he", "she", "it", "they"}):
                leaf_index = next(i for i, leaf in enumerate(leaves)
                                  if leaf.get("surface") == ";"
                                  and leaf["span"][0] == children[marks[1]]["span"][0])
                span = spans[leaf_index]
                rows.append(_candidate(
                    "OTH-698", [1737, 1738], "nested_semicolon_levels", span,
                    _edit(span, ","),
                    outer_char_span=spans[next(i for i, leaf in enumerate(leaves)
                                               if leaf.get("surface") == ";"
                                               and leaf["span"][0] == children[marks[0]]["span"][0])],
                ))
    return rows


def probe_colon_series(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if any(child.get("surface") == ";" for child in children):
        return []
    colon_positions = [i for i, child in enumerate(children) if child.get("surface") == ":"]
    clause_count = sum(1 for child in children if child.get("type") in {"S", "SQ"})
    if len(colon_positions) < 2 or clause_count < 3:
        return []
    rows = []
    for position in colon_positions:
        if position == 0 or position + 1 >= len(children):
            continue
        if (children[position - 1].get("type") not in {"S", "SQ"}
                or children[position + 1].get("type") not in {"S", "SQ"}):
            continue
        leaf_index = next(i for i, leaf in enumerate(leaves)
                          if leaf.get("surface") == ":"
                          and leaf["span"][0] == children[position]["span"][0])
        span = spans[leaf_index]
        rows.append(_candidate(
            "OTH-699", [1738], "colon_separating_peer_coordinates", span,
            _edit(span, ";"),
            left_char_span=_node_span(children[position - 1], spans),
            right_char_span=_node_span(children[position + 1], spans),
        ))
    return rows


def probe_bare_coordinate_boundary(sentence: str,
                                   tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None:
        return []
    leaves, spans = aligned
    rows = []
    for node in _walk(tree):
        if node.get("type") != "NP":
            continue
        children = node.get("children", [])
        for index, child in enumerate(children):
            if (child.get("type") != "CC" or _leaf_lower(child) not in {"and", "or"}
                    or index < 2 or index + 1 >= len(children)):
                continue
            left = [item for item in children[:index] if not item.get("punct")]
            right = [item for item in children[index + 1:] if not item.get("punct")]
            if len(left) < 2 or not right or right[0].get("type") not in NOMINAL_TYPES:
                continue
            if any(item.get("type") not in NOMINAL_TYPES for item in left):
                continue
            for first, second in zip(left, left[1:]):
                if second["span"][0] != first["span"][1]:
                    continue
                insertion = spans[first["span"][1] - 1][1]
                rows.append(_candidate(
                    "OTH-701", [1739], "unmarked_noninitial_bare_coordinate",
                    [insertion, insertion], _edit([insertion, insertion], ","),
                    first_char_span=_node_span(first, spans),
                    second_char_span=_node_span(second, spans),
                ))
    return rows


def probe_connective_adjunct_boundary(sentence: str,
                                       tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    rows = []
    for index, child in enumerate(children):
        if child.get("surface") != ",":
            continue
        left = children[index - 1] if index > 0 else None
        right = children[index + 1] if index + 1 < len(children) else None
        if not left or left.get("type") not in {"S", "SQ", "SBAR"} or not right:
            continue
        flagged = False
        if (right.get("type") == "ADVP"
                and _leaf_lower(_first_leaf(right)) in CONNECTIVES
                and index + 2 < len(children) and children[index + 2].get("surface") == ","):
            flagged = True
        if right.get("type") in {"S", "SQ"}:
            first = (right.get("children") or [None])[0]
            if (first is not None and first.get("type") == "ADVP"
                    and _leaf_lower(_first_leaf(first)) in CONNECTIVES):
                flagged = True
        if not flagged:
            continue
        span = spans[child["span"][0]]
        rows.append(_candidate(
            "OTH-708", [1741, 1742], "comma_only_before_connective_adjunct",
            span, _edit(span, ";"),
            left_char_span=_node_span(left, spans),
            right_char_span=_node_span(right, spans),
        ))
    return rows


def probe_subject_verb_comma(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if len(children) != 4:
        return []
    subject, comma, predicate, terminal = children
    if comma.get("surface") != "," or predicate.get("type") != "VP":
        return []
    if subject.get("type") not in {"NP", "SBAR"}:
        return []
    if subject.get("type") == "SBAR":
        return []
    if any(node.get("type") in {"SBAR", "SBARQ"} for node in _walk(subject)):
        return []
    last = _last_leaf(subject)
    if last is None or last.get("pos") == "MD" or _leaf_lower(last) in MODAL_AUX:
        return []
    first = _first_leaf(predicate)
    if first is None or not first.get("pos", "").startswith("VB"):
        return []
    span = spans[comma["span"][0]]
    return [_candidate(
        "OTH-715", [1744], "comma_between_subject_and_finite_verb",
        span, _edit(span, ""),
        subject_char_span=_node_span(subject, spans),
        verb_char_span=_node_span(predicate, spans),
    )]


def probe_vocative_delimitation(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None:
        return []
    leaves, spans = aligned
    rows = []

    def is_subject_phrase(node, root):
        parent = None
        for candidate in _walk(root):
            if any(child["id"] == node["id"] for child in candidate.get("children", [])):
                parent = candidate
                break
        if parent is None or parent.get("type") not in {"S", "SQ"}:
            return False
        return any(child.get("type") == "VP" for child in parent.get("children", []))

    for node in _walk(tree):
        if node.get("type") != "NP" or not is_subject_phrase(node, tree):
            continue
        children = node.get("children", [])
        for first, second in zip(children, children[1:]):
            pronoun = (first.get("type") == "NP" and len(first.get("children", [])) == 1
                       and first["children"][0].get("pos") == "PRP")
            if pronoun and second.get("pos") == "NNP":
                for leaf, replacement in ((first["children"][0], ","), (second, ",")):
                    insertion = spans[leaf["span"][1] - 1][1]
                    rows.append(_candidate(
                        "OTH-717", [1745], "missing_delimiting_comma_around_vocative",
                        [insertion, insertion], _edit([insertion, insertion], replacement),
                        vocative_char_span=_node_span(second, spans),
                    ))

    for node in _walk(tree):
        if node.get("type") != "NP" or not is_subject_phrase(node, tree):
            continue
        children = node.get("children", [])
        for index in range(1, len(children) - 1):
            first, comma, second = children[index - 1], children[index], children[index + 1]
            pronoun = (first.get("type") == "NP" and len(first.get("children", [])) == 1
                       and first["children"][0].get("pos") == "PRP")
            named = ((second.get("type") == "NP"
                      and any(leaf.get("pos") == "NNP" for leaf in _ordered_leaves(second)))
                     or second.get("pos") == "NNP")
            if (pronoun and comma.get("surface") == "," and named
                    and (index + 2 >= len(children) or children[index + 2].get("surface") != ",")):
                insertion = spans[second["span"][1] - 1][1]
                rows.append(_candidate(
                    "OTH-717", [1745], "missing_delimiting_comma_after_vocative",
                    [insertion, insertion], _edit([insertion, insertion], ","),
                    vocative_char_span=_node_span(second, spans),
                ))

    if tree.get("type") == "S" and tree.get("children"):
        predicate = tree["children"][0]
        if predicate.get("type") == "VP":
            parts = predicate.get("children", [])
            first = _first_leaf(predicate)
            final = parts[-1] if parts else None
            if (first is not None and first.get("pos") == "VB"
                    and final is not None and final.get("type") == "NP"
                    and len(parts) >= 2 and parts[-2].get("surface") != ","
                    and any(leaf.get("pos") == "NNP" for leaf in _ordered_leaves(final))
                    and any(part.get("type") == "NP" for part in parts[1:-1])):
                insertion = spans[final["span"][0]][0]
                rows.append(_candidate(
                    "OTH-717", [1745], "missing_delimiting_comma_before_vocative",
                    [insertion, insertion], _edit([insertion, insertion], ","),
                    vocative_char_span=_node_span(final, spans),
                ))
    return rows


def probe_all(sentence: str, tree: dict[str, Any] | None = None, *,
              variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_apostrophe_shape,
        probe_parenthetical_article,
        probe_compound_numeral_hyphen,
        probe_abbreviation_full_stop,
        probe_direct_speech_boundary,
        probe_parenthetical_insulation,
        probe_nested_quotes,
        probe_quoted_terminal_medial,
        probe_quoted_terminal_suppression,
    ):
        result["candidates"].extend(checker(sentence))
    if tree is None:
        result["blocked"].append("tree_relations_unavailable")
        return result
    for checker in (
        probe_embedded_question_terminal,
        probe_repeated_secondary,
        probe_colon_series,
        probe_bare_coordinate_boundary,
        probe_connective_adjunct_boundary,
        probe_subject_verb_comma,
        probe_vocative_delimitation,
    ):
        result["candidates"].extend(checker(sentence, tree))
    return result
