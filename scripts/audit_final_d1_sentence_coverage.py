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
        working = result.get("working_tree")
        available = bool(working and not list(validator.iter_errors(working))
                         and working["sentence"] == analysis["sentence"]
                         and [t["text"] for t in working["tokens"]] ==
                         [t["t"] for t in analysis["tokens"]
                          if any(c.isalnum() or c == "_" for c in t["t"])])
        return {"covered": False, "working_tree_available": available,
                "reasons": result.get("reasons", [])}
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
            if not result["covered"]:
                # Keep the parser hypothesis in the artifact so a failed
                # projection can be reproduced and assessed by construction.
                result["parser_parse_string"] = analysis.get("parse_string")
        except Exception as exc:
            result = {"covered": False, "reasons": [
                {"code": "AUDIT_FAILURE", "detail": str(exc)}
            ]}
        records.append({"sentence_index": index, **result})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--heldout", type=Path,
                        help="Audit an independent list of sentence objects instead of the existing evaluation corpora.")
    parser.add_argument("--require-complete", action="store_true",
                        help="Exit with failure if any corpus case lacks a canonical tree.")
    args = parser.parse_args()
    schema = ROOT / "docs/canonical-burton-roberts-tree.schema.json"
    validator = Draft202012Validator(json.loads(schema.read_text(encoding="utf-8")))
    load_models()

    cases = []
    summary = {}
    inputs = ([("heldout", args.heldout)] if args.heldout else
              [(corpus, ROOT / f"evaluation/{corpus}_sentences.json")
               for corpus in ("grammatical", "ungrammatical")])
    for corpus, path in inputs:
        rows = json.loads(path.read_text(encoding="utf-8"))
        records = []
        for index, row in enumerate(rows):
            if row.get("unit", "sentence") != "sentence":
                continue
            outcomes = audit_case(row["text"], validator)
            records.append({
                "corpus": corpus,
                "row_index": index,
                "text": row["text"],
                "rule_id": row.get("rule_id"),
                "covered": bool(outcomes) and all(item["covered"] for item in outcomes),
                "sentences": outcomes,
            })
        summary[corpus] = {"covered": sum(row["covered"] for row in records),
                           "total": len(records)}
        cases.extend(records)

    covered = sum(row["covered"] for row in cases)
    visible = sum(all(s["covered"] or s.get("working_tree_available", False)
                      for s in row["sentences"]) for row in cases)
    complete = bool(cases) and covered == len(cases)
    report = {
        "scope": ("Availability of canonical FINAL-D1 trees on an independent sentence probe set. "
                  if args.heldout else "Availability of canonical FINAL-D1 trees on existing sentence cases. ")
                 + "A passage case is covered only when all its sentences are covered. "
                   "Availability and schema validity do not establish linguistic accuracy.",
        "dataset": "heldout" if args.heldout else "existing_evaluation",
        "canonical_cases": covered,
        "tree_view_cases": visible,
        "working_tree_cases": visible - covered,
        "total_cases": len(cases),
        "complete": complete,
        "by_corpus": summary,
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"FINAL-D1 availability: {covered}/{len(cases)} corpus cases")
    print(f"Tree views including explicitly unresolved working trees: {visible}/{len(cases)}")
    return int(args.require_complete and not complete)


if __name__ == "__main__":
    raise SystemExit(main())
