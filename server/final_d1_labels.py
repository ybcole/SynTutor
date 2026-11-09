"""Resolve Generator display labels directly from the FINAL-D1 master sheet."""
from functools import lru_cache
from pathlib import Path
import re
from xml.etree import ElementTree
from zipfile import ZipFile


MASTER = Path(__file__).resolve().parents[1] / "grammar/SynTutor_FINAL-D1_Labeling_Master.xlsx"
_XML = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_FEATURE = re.compile(r"\[([a-z-]+)\]")
_LABEL = re.compile(r"([^\s\[]+)?\s*((?:\[[a-z-]+\])*)")
_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_SPECIAL = {"•", "•₁", "NP₁", "△", "Category + △", "The original word"}
_STORAGE = {"S-bar": "S′", "S-dbar": "S″", "AUX": ""}


@lru_cache(maxsize=1)
def load_label_master():
    """Index the two-column worksheet by category and feature set."""
    with ZipFile(MASTER) as workbook:
        worksheet = ElementTree.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        strings = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            shared = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))
            strings = ["".join(item.itertext()) for item in shared]

    def cell_text(cell):
        value = cell.findtext(_XML + "v", "")
        if cell.get("t") == "s":
            return strings[int(value)]
        if cell.get("t") == "inlineStr":
            return "".join(cell.find(_XML + "is").itertext())
        return value

    labels = {}
    special = set()
    data = worksheet.find(_XML + "sheetData")
    if data is None:
        raise ValueError("Labeling master has no worksheet data")
    for row in data:
        if int(row.get("r", 0)) <= 5:
            continue
        cells = {cell.get("r", "").rstrip("0123456789"): cell_text(cell) for cell in row}
        if not cells.get("A", "").startswith("For "):
            continue
        display = cells.get("B", "")
        if display in _SPECIAL:
            special.add(display)
            continue
        match = _LABEL.fullmatch(display)
        if not match or not any(match.groups()):
            raise ValueError(f"Invalid master label {display!r}")
        category, stack = match.groups()
        features = tuple(_FEATURE.findall(stack))
        key = (category or "", frozenset(features))
        lines = ([category] if category else []) + [f"[{value}]" for value in features]
        if len(key[1]) != len(features) or (key in labels and labels[key] != lines):
            raise ValueError(f"Conflicting master feature stack {display!r}")
        labels[key] = lines
    if not {("S", frozenset()), ("", frozenset({"-tense"}))} <= labels.keys() or special != _SPECIAL:
        raise ValueError("Labeling master is missing required categories or marks")
    return labels


def final_d1_display_labels(root):
    """Return display rows keyed by canonical node ID, preserving structure."""
    master = load_label_master()
    display = {}

    def visit(node, parent=None):
        index = node.get("index")
        subscript = "" if index is None else str(index).translate(_SUBSCRIPTS)
        if node.get("gap"):
            lines = ["•" + subscript]
        elif "word" in node:
            lines = ["E" if node.get("elided") else node["word"]]
        elif node.get("unlabelled") and node.get("triangle"):
            lines = []
        else:
            category = node["label"]
            if category in {"C", "Comp"} and parent in {"S-bar", "S′"}:
                category = "C1"
            category = _STORAGE.get(category, category)
            features = node.get("features", [])
            key = (category, frozenset(features))
            if key not in master or len(key[1]) != len(features):
                raise ValueError(f"Label {node['label']!r} with features {features!r} is absent from the FINAL-D1 master")
            lines = master[key].copy()
            if category:
                # The Third Edition labels the lowest numbered/basic VP as
                # VP1. Gold-source node references retain VP1/VP2 as metadata.
                # Surface the printed reference rather than dropping it.
                refs = node.get("source_refs") or []
                vp_ref = next((ref for ref in refs
                               if isinstance(ref, str) and re.fullmatch(r"VP[1-9][0-9]*", ref)), None)
                if category == "VP" and vp_ref:
                    lines[0] = "VP" + vp_ref[2:].translate(_SUBSCRIPTS)
                lines[0] += subscript
        display[node["id"]] = lines
        for child in node.get("children", []):
            visit(child, node.get("label"))

    visit(root)
    return display

# Fallback for an *explicitly provisional* B-R working tree only.
# The strict master above remains the canonical tree's source of authority.
# A missing master row must not erase a valid working tree from the UI.
def final_d1_working_display_labels(root):
    """Render provisional B-R categories without pretending unverified features are approved.

    A working tree already uses B-R storage labels, not raw parser tags.
    Unsupported label/feature combinations are displayed conservatively and
    flagged, never converted into a supposedly source-certified master label.
    """
    try:
        master = load_label_master()
    except (OSError, ValueError, KeyError, IndexError):
        master = {}
    known = {category for category, _ in master}
    # Used only if the workbook is unavailable, not as a substitute for it.
    if not known:
        known = {
            "S", "NP", "VP", "NOM", "N", "V", "AP", "A",
            "AdvP", "Adv", "PP", "P", "name", "pronoun", "DET",
            "ART", "DEM", "POSS", "PRE-DET", "Q", "QA", "DEG",
            "PartP", "V-part", "Prt", "S′", "S″", "C", "C1", "C2",
            "MOD", "PERF", "PROG", "PASS", "TENSE", "AUX",
            "V(I)", "V(II)", "",
        }
    display = {}
    warnings = []

    def visit(node, parent=None):
        idx = node.get("index")
        subscript = "" if idx is None else str(idx).translate(_SUBSCRIPTS)
        if node.get("gap"):
            lines = ["•" + subscript]
        elif "word" in node:
            lines = ["E" if node.get("elided") else node["word"]]
        elif node.get("unlabelled") and node.get("triangle"):
            lines = []
        else:
            raw = node.get("label", "")
            category = "C1" if raw in {"C", "Comp"} and parent in {"S-bar", "S′"} else raw
            category = _STORAGE.get(category, category)
            features = node.get("features", [])
            key = (category, frozenset(features))
            if key in master and len(key[1]) == len(features):
                lines = master[key].copy()
            elif category in known:
                # Category is explicitly B-R, but master-row licensing for its
                # exact features has not been demonstrated. Do not invent them.
                lines = [category] if category else ["△"]
                warnings.append({"node_id": node.get("id"),
                                 "code": "UNREVIEWED_WORKING_LABEL",
                                 "category": raw,
                                 "features_not_displayed": list(features)})
            else:
                # A stray Penn/unknown label cannot become the apparent book
                # category; retain a visibly unanalyzed marker instead.
                lines = ["△"]
                warnings.append({"node_id": node.get("id"),
                                 "code": "UNKNOWN_WORKING_CATEGORY",
                                 "category": str(raw)})
            if lines and lines[0] not in {"△", ""}:
                refs = node.get("source_refs") or []
                vp_ref = next((ref for ref in refs if isinstance(ref, str)
                               and re.fullmatch(r"VP[1-9][0-9]*", ref)), None)
                if category == "VP" and vp_ref:
                    lines[0] = "VP" + vp_ref[2:].translate(_SUBSCRIPTS)
                lines[0] += subscript
        display[node["id"]] = lines
        for child in node.get("children", []):
            visit(child, node.get("label"))

    visit(root)
    return {"labels": display, "warnings": warnings}
