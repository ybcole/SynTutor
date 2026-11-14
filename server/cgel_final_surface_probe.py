"""Offline surface candidates for the final mixed Phase C batch.

The checks are candidate-only and production-disabled. The remaining queued
specifications are semantic/relativisation cases and are deliberately not
covered here.
"""
from __future__ import annotations

import re
from typing import Any


MASS = {
    "equipment", "furniture", "information", "advice", "luggage", "baggage",
    "news", "money", "water", "milk", "flour", "grit", "repetition",
    "condensation", "stationery", "homework", "research", "traffic", "weather",
    "bread", "cheese", "rice", "sand", "salt", "sugar", "coffee", "tea",
    "music", "art", "work", "evidence", "knowledge", "progress", "software",
    "hardware", "clothing", "machinery", "scenery", "electricity", "air",
    "oxygen", "feedback",
}
POSTMODIFIER_ADJECTIVES = {
    "waterproof", "spicy", "warm", "cold", "new", "old", "big", "small",
    "heavy", "light", "strong", "weak", "soft", "hard", "bright", "dark",
}
RELATIONAL_ADJECTIVES = {
    "tax", "legal", "medical", "financial", "technical", "cultural", "social",
    "political", "environmental", "economic", "historical",
}
SUPERLATIVE_IRREGULAR = {
    "better": "best", "worse": "worst", "farther": "farthest",
    "further": "furthest", "more": "most", "less": "least",
}


def _result() -> dict[str, Any]:
    return {"status": "not_evaluated", "production_enabled": False,
            "candidates": [], "blocked": []}


def _edit(span: list[int], replacement: str) -> dict[str, Any]:
    return {"char_span": list(span), "replacement": replacement,
            "requires_reparse": True, "safe_to_apply_automatically": False}


def _candidate(rule_id: str, chapter: int, pages: list[int], kind: str,
               span: list[int], replacement: str | None,
               **relation: Any) -> dict[str, Any]:
    edit = _edit(span, replacement) if replacement is not None else None
    return {"rule_id": rule_id, "source_chapter": chapter, "source_pages": pages,
            "relation": {"kind": kind, "mark_char_span": list(span), **relation},
            "edit_hint": edit}


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _article(word: str) -> str:
    return "an" if word[:1].casefold() in "aeiou" else "a"


def _pluralize(word: str) -> str:
    lower = word.casefold()
    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if re.search(r"[^aeiou]y$", lower):
        return word[:-1] + "ies"
    return word + "s"


def _superlative(word: str) -> str:
    lower = word.casefold()
    if lower in SUPERLATIVE_IRREGULAR:
        return SUPERLATIVE_IRREGULAR[lower]
    if lower.endswith("ier"):
        return word[:-3] + "iest"
    if lower.endswith("er"):
        return word[:-2] + "est"
    return word + "est"


def probe_postmodifier_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    adjectives = "|".join(sorted(POSTMODIFIER_ADJECTIVES, key=len, reverse=True))
    pattern = re.compile(
        rf"\b(Something|Anything|Everything|Nothing)\s+"
        rf"(for\s+(?:the\s+)?[a-z]+)\s+({adjectives})\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)}"
        rows.append(_candidate(
            "PHR-220", 5, [423], "postmodifier_after_attribute",
            [match.start(), match.end()], _case(match.group(0), replacement),
            attribute=match.group(3),
        ))
    return rows


def probe_prehead_complement(sentence: str) -> list[dict[str, Any]]:
    rows = []
    relational = "|".join(sorted(RELATIONAL_ADJECTIVES, key=len, reverse=True))
    pattern = re.compile(
        rf"\b(a|an)\s+({relational})\s+([a-z]+ed)\s+([a-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        adjective = match.group(3)
        article = _article(adjective)
        replacement = f"{article} {adjective} {match.group(2)} {match.group(4)}"
        rows.append(_candidate(
            "PHR-258", 5, [441], "modifier_between_complement_and_head",
            [match.start(), match.end()], _case(match.group(0), replacement),
            complement=match.group(2), head=match.group(4),
        ))
    return rows


def probe_split_each(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\beach\s+the\s+other\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-590", 17, [1499], "split_each_before_reciprocal_object",
            [match.start(), match.end()], _case(match.group(0), "each other"),
        ))
    for match in re.finditer(r"\beach\s+to\s+the\s+others\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-590", 17, [1499], "split_each_before_reciprocal_object",
            [match.start(), match.end()], _case(match.group(0), "to each other"),
        ))
    return rows


def probe_split_one(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\bone\s+the\s+other\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-593", 17, [1500], "split_one_before_other_object",
            [match.start(), match.end()], _case(match.group(0), "one another"),
        ))
    return rows


def probe_every_reciprocal(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bEvery\s+([a-z]+)\s+([a-z]+ed)\s+(each other|one another)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        noun = _pluralize(match.group(1))
        replacement = f"All the {noun} {match.group(2)} {match.group(3)}"
        rows.append(_candidate(
            "PHR-600", 17, [1501], "every_singular_as_reciprocal_antecedent",
            [match.start(), match.end()], _case(match.group(0), replacement),
            antecedent=match.group(1),
        ))
    return rows


def probe_reciprocal_adjunct(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^(The\s+[a-z]+s)\s+(each other|one another)\s+([a-z]+ed)\b",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = f"{match.group(1)} themselves {match.group(3)}"
        rows.append(_candidate(
            "PHR-602", 17, [1502], "compound_reciprocal_as_emphatic_adjunct",
            [match.start(), match.end()], replacement,
        ))
    pattern = re.compile(
        r"^(The\s+[a-z]+s)\s+([a-z]+ed)\s+(the\s+[a-z]+)\s+(one another|each other)\b",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = f"{match.group(1)} {match.group(2)} {match.group(3)} themselves"
        rows.append(_candidate(
            "PHR-602", 17, [1502], "compound_reciprocal_as_emphatic_adjunct",
            [match.start(), match.end()], replacement,
        ))
    return rows


def probe_mass_one(sentence: str) -> list[dict[str, Any]]:
    lower = sentence.casefold()
    if not any(re.search(rf"\b{re.escape(noun)}\b", lower) for noun in MASS):
        return []
    rows = []
    pattern = re.compile(
        r"\bthe one\b(?=\s+(?:in|from|of|on|at|with|beside|near)\b)",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-653", 17, [1515], "pro_one_for_mass_antecedent",
            [match.start(), match.end()], _case(match.group(0), "that"),
        ))
    return rows


def probe_supplementary_as(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^As\s+(you|I|we|they|he|she)\s+"
        r"(know|mentioned|said|noted|explained|reported)\s+it,",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        rows.append(_candidate(
            "CLS-1222", 13, [1148], "resumptive_it_in_supplementary_as",
            [match.end() - 4, match.end() - 1], "",
            reporting_verb=match.group(2),
        ))
    return rows


def probe_comparative_grade(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bthe\s+([a-z]+er)\s+of\s+the\s+"
        r"(three|four|five|six|seven|eight|nine|ten|\d+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"the {_superlative(match.group(1))} of the {match.group(2)}"
        rows.append(_candidate(
            "CLS-1259", 13, [1162], "comparative_for_larger_set_ranking",
            [match.start(), match.end()], _case(match.group(0), replacement),
            comparative=match.group(1),
        ))
    return rows


def probe_superlative_definiteness(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(a|an)\s+([a-z]+est)\s+([a-z]+)\s+(in\s+(?:the\s+)?[a-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"the {match.group(2)} {match.group(3)} {match.group(4)}"
        rows.append(_candidate(
            "CLS-1274", 13, [1168, 1169], "indefinite_article_with_ranking_superlative",
            [match.start(), match.end()], _case(match.group(0), replacement),
            superlative=match.group(2),
        ))
    pattern = re.compile(
        r"\b(two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
        r"([a-z]+est)\s+([a-z]+s?)\s+(in\s+(?:the\s+)?[a-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        if sentence[:match.start()].rstrip().casefold().endswith("the"):
            continue
        replacement = f"the {match.group(1)} {match.group(2)} {match.group(3)} {match.group(4)}"
        rows.append(_candidate(
            "CLS-1274", 13, [1168, 1169], "bare_numeral_with_ranking_superlative",
            [match.start(), match.end()], _case(match.group(0), replacement),
            superlative=match.group(2),
        ))
    return rows


def probe_free_superlative(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bis\s+(lowest|highest|best|worst|fastest|slowest|earliest|latest)"
        r"\s+it\s+(has|had)\s+been\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "CLS-1276", 13, [1169], "free_superlative_without_definite_article",
            [match.start(1), match.start(1)], "the ",
            superlative=match.group(1),
        ))
    pattern = re.compile(
        r"\b(the\s+most\s+[a-z]+ly)\s+(which)\s+it\s+(ever\s+has|ever\s+had)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "CLS-1276", 13, [1169], "which_after_free_superlative",
            [match.start(2), match.end(2)], "that",
            superlative=match.group(1),
        ))
    return rows


def probe_double_object_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(sent|gave|offered|handed|showed|brought|told)\s+"
        r"((?:a|an|the)\s+[a-z]+)\s+"
        r"(everyone(?:\s+on\s+the\s+[a-z]+(?:\s+[a-z]+)?)?|"
        r"each\s+[a-z]+(?:\s+who\s+[a-z]+(?:\s+[a-z]+)*)?)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)}"
        rows.append(_candidate(
            "CLS-1329", 16, [1384], "recipient_after_direct_object",
            [match.start(), match.end()], _case(match.group(0), replacement),
            recipient=match.group(3), object=match.group(2),
        ))
    return rows


def probe_final_surface(sentence: str, *, variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_postmodifier_order,
        probe_prehead_complement,
        probe_split_each,
        probe_split_one,
        probe_every_reciprocal,
        probe_reciprocal_adjunct,
        probe_mass_one,
        probe_supplementary_as,
        probe_comparative_grade,
        probe_superlative_definiteness,
        probe_free_superlative,
        probe_double_object_order,
    ):
        result["candidates"].extend(checker(sentence))
    return result
