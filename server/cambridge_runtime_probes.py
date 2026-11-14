"""Allow-listed candidate probes that may execute in the Cambridge runtime.

Only the probes named here can be selected by a rule's runtime_check. This is a
closed registry, not a dynamic import surface.
"""
from __future__ import annotations

from typing import Any, Callable


def _load(module_name: str, function_name: str) -> Callable:
    try:
        if __package__:
            module = __import__(f"{__package__}.{module_name}", fromlist=[function_name])
        else:
            module = __import__(module_name, fromlist=[function_name])
    except ImportError:
        module = __import__(module_name, fromlist=[function_name])
    return getattr(module, function_name)


def _punctuation_abbreviation(sentence: str, tree: Any = None):
    return _load("cgel_punctuation_probe", "probe_abbreviation_full_stop")(sentence)


def _spelling_final_c_k(sentence: str, tree: Any = None):
    return _load("cgel_spelling_probe", "probe_final_c_k")(sentence)


def _spelling_i_arent(sentence: str, tree: Any = None):
    return _load("cgel_usage_probe", "probe_i_arent")(sentence)


def _determiner_no_none(sentence: str, tree: Any = None):
    return _load("cgel_determiner_probe", "probe_no_none")(sentence, tree)


PROBE_SPECS: dict[str, dict[str, Any]] = {
    "punctuation.abbreviation_full_stop": {
        "function": _punctuation_abbreviation,
        "requires_tree": False,
    },
    "spelling.final_c_k": {
        "function": _spelling_final_c_k,
        "requires_tree": False,
    },
    "spelling.i_arent": {
        "function": _spelling_i_arent,
        "requires_tree": False,
    },
    "determiner.no_none": {
        "function": _determiner_no_none,
        "requires_tree": False,
    },
}


def supported_probe_names() -> set[str]:
    return set(PROBE_SPECS)


def run_candidate_probe(name: str, sentence: str, tree: Any = None) -> list[dict[str, Any]]:
    spec = PROBE_SPECS.get(name)
    if spec is None:
        raise KeyError(f"candidate probe is not allow-listed: {name}")
    if spec["requires_tree"] and not isinstance(tree, dict):
        return []
    return spec["function"](sentence, tree)
