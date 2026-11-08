"""M12 fixed-corpus comparison: legacy diagnostic vs source-authorized B-R output.

This is a *behavioral comparison*, not a claimed accuracy score or a new
reference answer set. Only the already-reviewed B-R chapter profile can
authorize a tree; a legacy diagnostic verdict is never source-grounded.
Run in the parser-backed CI environment:
    python scripts/compare_pipeline_fixed_corpus.py
"""
import json
from pathlib import Path
import sys
from unittest.mock import patch

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
import api  # noqa: E402

CORPUS = [
    ("subject_plural", "The students laugh."),
    ("subject_singular", "The student laughs."),
    ("determiner_noun", "A teacher reads the book."),
    ("preposition", "The child walked to the garden."),
    ("legacy_diagnostic", "The students laughs."),
    ("ambiguous", "I saw her duck."),
]
SCHEMA = json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def inspect(text, chapter):
    # Disable optional CoLA/model-assisted classification for a deterministic
    # matrix comparison; the real spaCy+Benepar parser still runs.
    with patch.object(api, "classify", return_value=None):
        result = api.build_payload(text, chapter=chapter)
    br = result["br_analysis"]
    status = br["status"]
    assert result["tree"] == result["candidate_tree"]
    assert result["summary"]["verdict_authority"] == "legacy_diagnostic"
    assert result["summary"]["book_verified"] is False
    assert result["meta"]["acceptability_signal_can_create_rule_violation"] is False
    assert result["meta"]["cambridge_runtime_rule_ids"] == [], (
        "Unreviewed Cambridge runtime constraints must stay disabled.")
    if status == "normalized":
        assert br.get("tree"), "A normalized analysis must include its tree"
        VALIDATOR.validate(br["tree"])
    else:
        assert not br.get("tree"), "Unresolved analysis must not present an authoritative tree"
    return {
        "legacy_verdict": result["summary"]["verdict"],
        "legacy_authority": result["summary"]["verdict_authority"],
        "br_status": status,
        "br_profile": result["meta"]["br_profile_id"],
        "source_evidence_status": result["explanation_evidence"]["status"],
        "unresolved_codes": [
            r.get("code") for r in br.get("reasons", []) if isinstance(r, dict)
        ],
        "candidate": result["candidate_tree"],
    }


def main():
    records = []
    for case, sentence in CORPUS:
        early = inspect(sentence, 2)
        final = inspect(sentence, None)
        assert early["candidate"] == final["candidate"], (
            "Convention selection must not change the underlying parser candidate")
        assert early["legacy_verdict"] == final["legacy_verdict"], (
            "Chapter-specific B-R conventions must not silently alter legacy diagnostics")
        records.append({
            "case": case,
            "sentence": sentence,
            "legacy_diagnostic_verdict": early["legacy_verdict"],
            "chapter_2": {k: v for k, v in early.items() if k != "candidate"},
            "final_d1": {k: v for k, v in final.items() if k != "candidate"},
        })
    target = ROOT / "artifacts/m12_pipeline_comparison.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "purpose": "Deterministic corpus comparison; not grammatical accuracy or complete source coverage",
        "model": "spaCy en_core_web_md + Benepar benepar_en3",
        "cola": "disabled for deterministic diagnostic comparison",
        "corpus_size": len(records),
        "cases": records,
    }, indent=2) + "\n")
    print(f"PASS: compared legacy diagnostic with chapter V2 and FINAL-D1 on {len(records)} parser-backed sentences")
    print(f"Report: {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
