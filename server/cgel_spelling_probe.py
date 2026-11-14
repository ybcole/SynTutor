"""Offline spelling-inflection evidence for selected Chapter 18 and 19 rules.

The probe is candidate-only. It never enables a runtime rule, certifies a
spelling as an error in context, or replaces source review for the broader
patterns listed in Cambridge.
"""
from __future__ import annotations

import re
from typing import Any


def _result() -> dict[str, Any]:
    return {"status": "not_evaluated", "production_enabled": False,
            "candidates": [], "blocked": []}


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _edit(span: list[int], replacement: str) -> dict[str, Any]:
    return {"char_span": list(span), "replacement": replacement,
            "requires_reparse": True, "safe_to_apply_automatically": False}


def _candidate(rule_id: str, chapter: int, pages: list[int], kind: str,
               span: list[int], replacement: str,
               relation_span: list[int] | None = None,
               **relation: Any) -> dict[str, Any]:
    payload = {"kind": kind, "mark_char_span": list(span), **relation}
    if relation_span is not None:
        payload.setdefault("token_char_span", list(relation_span))
    return {"rule_id": rule_id, "source_chapter": chapter, "source_pages": pages,
            "relation": payload, "edit_hint": _edit(span, replacement)}


def _mapping_probe(sentence: str, mapping: dict[str, str], rule_id: str,
                   chapter: int, pages: list[int], kind: str,
                   relation_kind: str = "token_char_span") -> list[dict[str, Any]]:
    pattern = re.compile(r"\b(?:" + "|".join(
        map(re.escape, sorted(mapping, key=len, reverse=True))) + r")\b",
        re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        original = match.group(0)
        replacement = _case(original, mapping[original.casefold()])
        relation = {relation_kind: [match.start(), match.end()]}
        rows.append(_candidate(
            rule_id, chapter, pages, kind,
            [match.start(), match.end()], replacement,
            relation_span=[match.start(), match.end()], **relation,
        ))
    return rows


NUMERALS = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
            r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
            r"nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
            r"hundred|thousand)")
TENS = r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
UNITS = (r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
         r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)")
MEASURE_UNITS = {
    "feet": "foot", "inches": "inch", "yards": "yard", "miles": "mile",
    "metres": "metre", "meters": "meter", "kilometres": "kilometre",
    "kilometers": "kilometer", "pounds": "pound", "ounces": "ounce",
    "kilograms": "kilogram", "kilos": "kilo", "grams": "gram",
    "degrees": "degree", "nights": "night", "days": "day", "weeks": "week",
    "months": "month", "years": "year", "hours": "hour", "minutes": "minute",
    "seconds": "second", "storeys": "storey", "stories": "story",
    "bedrooms": "bedroom", "litres": "litre", "liters": "liter",
    "gallons": "gallon",
}
ORDINAL_UNITS = {
    "one": "first", "two": "second", "three": "third", "five": "fifth",
    "eight": "eighth", "nine": "ninth", "twelve": "twelfth",
}
DENOMINATORS = {
    "half": "halves", "third": "thirds", "quarter": "quarters",
    "fifth": "fifths", "sixth": "sixths", "seventh": "sevenths",
    "eighth": "eighths", "ninth": "ninths", "tenth": "tenths",
    "twelfth": "twelfths", "hundredth": "hundredths",
    "thousandth": "thousandths", "millionth": "millionths",
}
INHABITANT_BASES = [
    "Taiwanese", "Chinese", "Japanese", "Portuguese", "Lebanese", "Vietnamese",
    "Burmese", "Nepalese", "Siamese", "Sudanese", "Congolese", "Maltese",
    "Sinhalese", "Bhutanese", "Swiss",
]
NEGATIVE_MAP = {
    "inregular": "irregular", "inbalance": "imbalance", "inlegal": "illegal",
    "inmoral": "immoral", "inpossible": "impossible", "inmortal": "immortal",
    "inlogical": "illogical", "inresponsible": "irresponsible",
    "inreversible": "irreversible", "inpartial": "impartial",
    "inpolite": "impolite", "inmodest": "immodest", "inmaterial": "immaterial",
    "inlegible": "illegible", "inliterate": "illiterate",
}


def probe_split_another(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(an)(\s+)(other)\b", sentence, re.IGNORECASE):
        original = match.group(0)
        rows.append(_candidate(
            "PHR-164", 5, [391], "split_alternative_additive_determiner",
            [match.start(), match.end()], _case(original, "another"),
            relation_span=[match.start(), match.end()],
        ))
    return rows


def probe_final_c_k(sentence: str) -> list[dict[str, Any]]:
    verbs = ["bivouac", "traffic", "picnic", "frolic", "tarmac", "magic", "panic"]
    pattern = re.compile(r"\b(" + "|".join(verbs) + r")(ed|ing)\b", re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        insertion = match.end(1)
        rows.append(_candidate(
            "MORPH-109", 18, [1598], "missing_k_after_final_c",
            [insertion, insertion], "k",
            relation_span=[match.start(), match.end()],
            verb=match.group(1), suffix=match.group(2),
        ))
    return rows


def probe_er_preposition_plural(sentence: str) -> list[dict[str, Any]]:
    mapping = {
        "passer-bys": "passers-by", "runner-ups": "runners-up",
        "hanger-ons": "hangers-on", "looker-ons": "lookers-on",
        "diner-outs": "diners-out",
    }
    return _mapping_probe(sentence, mapping, "MORPH-237", 19, [1655],
                          "plural_suffix_after_final_preposition")


def _singular_measure(unit: str) -> str:
    lower = unit.casefold()
    if lower in MEASURE_UNITS:
        return MEASURE_UNITS[lower]
    if lower.endswith("ies"):
        return unit[:-3] + "y"
    if lower.endswith("es"):
        return unit[:-2]
    if lower.endswith("s"):
        return unit[:-1]
    return unit


def probe_attributive_measure(sentence: str) -> list[dict[str, Any]]:
    units = "|".join(sorted(MEASURE_UNITS, key=len, reverse=True))
    pattern = re.compile(
        rf"\b({NUMERALS})-({units})\s+(?=[A-Za-z])", re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        singular = _singular_measure(match.group(2))
        rows.append(_candidate(
            "MORPH-258", 19, [1660], "plural_measure_base_in_attributive_compound",
            [match.start(2), match.end(2)], _case(match.group(2), singular),
            relation_span=[match.start(), match.end()],
            numeral=match.group(1),
        ))
    return rows


def probe_lexical_doubling(sentence: str) -> list[dict[str, Any]]:
    return _mapping_probe(
        sentence, {"propelant": "propellant", "deterence": "deterrence"},
        "MORPH-309", 19, [1675], "missing_consonant_doubling")


def probe_mute_e_deletion(sentence: str) -> list[dict[str, Any]]:
    return _mapping_probe(
        sentence, {"driveer": "driver", "believeable": "believable"},
        "MORPH-311", 19, [1675], "retained_mute_e_before_vowel_suffix")


def probe_soft_c_g_retention(sentence: str) -> list[dict[str, Any]]:
    return _mapping_probe(
        sentence, {"enforcable": "enforceable", "managable": "manageable"},
        "MORPH-313", 19, [1676], "deleted_e_after_soft_c_or_g")


def probe_y_replacement(sentence: str) -> list[dict[str, Any]]:
    return _mapping_probe(
        sentence, {"applyant": "applicant", "likelyhood": "likelihood",
                   "happyness": "happiness", "carryage": "carriage"},
        "MORPH-316", 19, [1676, 1677], "retained_final_y_before_suffix")


def probe_negative_prefix(sentence: str) -> list[dict[str, Any]]:
    return _mapping_probe(
        sentence, NEGATIVE_MAP, "MORPH-357", 19, [1687],
        "default_negative_prefix_in_established_form")


def probe_invariant_inhabitants(sentence: str) -> list[dict[str, Any]]:
    bases = "|".join(sorted(INHABITANT_BASES, key=len, reverse=True))
    pattern = re.compile(rf"\b({bases})(s|es)\b", re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        base = match.group(1)
        for candidate in INHABITANT_BASES:
            if candidate.casefold() == base.casefold():
                base = candidate
                break
        rows.append(_candidate(
            "MORPH-385", 19, [1694, 1695], "plural_suffix_on_invariant_inhabitant",
            [match.start(), match.end()], _case(match.group(0), base),
            relation_span=[match.start(), match.end()],
        ))
    return rows


def probe_possessive_ed(sentence: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        rf"\b({NUMERALS})-([A-Za-z]+s)ed\b", re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        noun = match.group(2)
        if not noun.casefold().endswith("s"):
            continue
        singular = _singular_measure(noun)
        replacement = _case(noun, singular) + "ed"
        rows.append(_candidate(
            "MORPH-445", 19, [1709], "plural_nominal_before_possessive_ed",
            [match.start(2), match.end()], replacement,
            relation_span=[match.start(), match.end()],
            numeral=match.group(1),
        ))
    return rows


def probe_power_head_inflection(sentence: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        rf"\b({NUMERALS})\s+(hundreds|thousands|millions|billions|trillions)\b",
        re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        power = match.group(2)
        rows.append(_candidate(
            "MORPH-477", 19, [1717], "plural_power_head_inside_numeral",
            [match.start(2), match.end(2)], _case(power, power[:-1]),
            relation_span=[match.start(), match.end()],
            multiplier=match.group(1),
        ))
    return rows


def probe_compound_ordinal(sentence: str) -> list[dict[str, Any]]:
    units = "|".join(sorted(ORDINAL_UNITS, key=len, reverse=True))
    pattern = re.compile(rf"\b({TENS})-({units})th\b", re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        unit = match.group(2)
        ordinal = None
        for key, value in ORDINAL_UNITS.items():
            if key == unit.casefold():
                ordinal = value
                break
        replacement = _case(match.group(0), f"{match.group(1)}-{ordinal}")
        rows.append(_candidate(
            "MORPH-482", 19, [1718, 1719], "regular_cardinal_unit_in_compound_ordinal",
            [match.start(), match.end()], replacement,
            relation_span=[match.start(), match.end()],
            cardinal_unit=unit,
        ))
    return rows


def probe_fraction_denominator(sentence: str) -> list[dict[str, Any]]:
    numerators = (r"(?:[2-9]|\d{2,}|two|three|four|five|six|seven|eight|nine|"
                  r"ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
                  r"seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|"
                  r"sixty|seventy|eighty|ninety)")
    denominators = "|".join(sorted(DENOMINATORS, key=len, reverse=True))
    pattern = re.compile(
        rf"\b({numerators})\s+({denominators})\s+of\b", re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        denominator = match.group(2).casefold()
        plural = DENOMINATORS[denominator]
        rows.append(_candidate(
            "MORPH-483", 19, [1719], "singular_denominator_after_plural_numerator",
            [match.start(2), match.end(2)], _case(match.group(2), plural),
            relation_span=[match.start(), match.end()],
            numerator=match.group(1),
        ))
    return rows


def probe_spelling(sentence: str, *, variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_split_another,
        probe_final_c_k,
        probe_er_preposition_plural,
        probe_attributive_measure,
        probe_lexical_doubling,
        probe_mute_e_deletion,
        probe_soft_c_g_retention,
        probe_y_replacement,
        probe_negative_prefix,
        probe_invariant_inhabitants,
        probe_possessive_ed,
        probe_power_head_inflection,
        probe_compound_ordinal,
        probe_fraction_denominator,
    ):
        result["candidates"].extend(checker(sentence))
    return result
