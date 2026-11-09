"""Audit canonical tree availability on the existing sentence corpus."""
import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from burton_roberts import build_canonical_analysis  # noqa: E402
from parse_engine import analyze, load_models  # noqa: E402


def audit_sentence(analysis, validator):
    result = build_canonical_analysis(analysis)
    tree = result.get("tree")
    if result["status"] != "normalized" or not tree:
        return {"covered": False, "reasons": result.get("reasons", [])}
    if tree["convention_profile"]["profile_id"] != "FINAL-D1":
        return {"covered": False, "reasons": [{"code": "WRONG_PROFILE"}]}
    if tree["sentence"] != analysis["sentence"]:
        return {"covered": False, "reasons": [{"code": "ORIGINAL_SENTENCE_MISMATCH"}]}
    original_words = [token["t"] for token in analysis["tokens"]
                      if any(char.isalnum() or char == "_" for char in token["t"])]
    tree_words = [token["text"] for token in tree["tokens"]
                  if any(char.isalnum() or char == "_" for char in token["text"])]
    if tree_words != original_words:
        return {"covered": False, "reasons": [{"code": "ORIGINAL_TOKEN_YIELD_MISMATCH"}]}
    error = next(validator.iter_errors(tree), None)
    if error:
        return {"covered": False, "reasons": [
            {"code": "INVALID_CANONICAL_SCHEMA", "detail": error.message}
        ]}
    return {"covered": True, "reasons": []}


def audit_case(text, validator):
    records = []
    try:
        first = analyze(text)
    except Exception as exc:
        return [{"sentence_index": 0, "covered": False, "reasons": [
            {"code": "PARSE_FAILURE", "detail": str(exc)}
        ]}]
    for index in range(first["sentence_count"]):
        try:
            analysis = first if index == 0 else analyze(text, sentence_index=index)
            result = audit_sentence(analysis, validator)
        except Exception as exc:
            result = {"covered": False, "reasons": [
                {"code": "AUDIT_FAILURE", "detail": str(exc)}
            ]}
        records.append({"sentence_index": index, **result})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true",
                        help="Exit with failure if any corpus case lacks a canonical tree.")
    args = parser.parse_args()
    schema = ROOT / "docs/canonical-burton-roberts-tree.schema.json"
    validator = Draft202012Validator(json.loads(schema.read_text(encoding="utf-8")))
    load_models()

    cases = []
    summary = {}
    for corpus in ("grammatical", "ungrammatical"):
        path = ROOT / f"evaluation/{corpus}_sentences.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        records = []
        for index, row in enumerate(rows):
            if row["unit"] != "sentence":
                continue
            outcomes = audit_case(row["text"], validator)
            records.append({
                "corpus": corpus,
                "row_index": index,
                "text": row["text"],
                "rule_id": row["rule_id"],
                "covered": bool(outcomes) and all(item["covered"] for item in outcomes),
                "sentences": outcomes,
            })
        summary[corpus] = {"covered": sum(row["covered"] for row in records),
                           "total": len(records)}
        cases.extend(records)

    covered = sum(row["covered"] for row in cases)
    complete = bool(cases) and covered == len(cases)
    report = {
        "scope": "Availability of canonical FINAL-D1 trees on existing sentence cases. "
                 "A passage case is covered only when all its sentences are covered.",
        "canonical_cases": covered,
        "total_cases": len(cases),
        "complete": complete,
        "by_corpus": summary,
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"FINAL-D1 availability: {covered}/{len(cases)} corpus cases")
    return int(args.require_complete and not complete)


if __name__ == "__main__":
    raise SystemExit(main())
