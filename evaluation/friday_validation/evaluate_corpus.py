
import json
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:8001/api/parse"
CORPUS = Path(__file__).with_name("grammar_corpus.jsonl")


def analyze(sentence):
    request = Request(
        API_URL,
        data=json.dumps({"text": sentence}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


def safe_divide(a, b):
    return a / b if b else None


def percentage(value):
    return f"{value:.1%}" if value is not None else "N/A"


def main():
    cases = [
        json.loads(line)
        for line in CORPUS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    counts = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    unevaluated = 0
    verdict_counts = Counter()
    tree_counts = Counter()
    correction_matches = 0
    correction_total = 0

    print("SYNTUTOR — INDEPENDENT GRAMMAR EVALUATION")
    print("=" * 55)

    for case in cases:
        expected_error = not case["expected_acceptable"]

        try:
            data = analyze(case["sentence"])
            summary = data.get("summary")

            if not isinstance(summary, dict):
                raise ValueError("Missing diagnostic summary")

            rules = summary.get("constraints_fired")

            if not isinstance(rules, list):
                raise ValueError("Missing diagnostic rule list")

            if summary.get("checker_errors"):
                raise ValueError(
                    f"Checker errors: {summary['checker_errors']}"
                )

            detected_error = bool(rules)

        except Exception as error:
            unevaluated += 1
            print(f"\n{case['id']} | ERROR")
            print("  Sentence:", case["sentence"])
            print("  Reason:", error)
            continue

        if expected_error and detected_error:
            result = "TP"
        elif not expected_error and detected_error:
            result = "FP"
        elif expected_error and not detected_error:
            result = "FN"
        else:
            result = "TN"

        counts[result] += 1
        verdict_counts[summary.get("verdict", "missing")] += 1
        tree_counts[(data.get("br_analysis") or {}).get("status", "missing")] += 1

        print(f"\n{case['id']} | {result}")
        print("  Sentence:", case["sentence"])
        print("  Rules:", rules)
        print("  Reference:", case["reference"])

        if expected_error:
            correction_total += 1

            actual = summary.get("corrected_sentence")
            expected = case.get("preferred_correction")
            match = actual == expected

            correction_matches += int(match)

            print("  Suggested correction:", actual)
            print("  Preferred correction:", expected)
            print("  Exact repair match:", match)

        print(
            "  Cambridge:",
            (data.get("cambridge_evaluation") or {}).get("status")
        )
        print("  Book verified:", summary.get("book_verified"))

    tp, fp = counts["TP"], counts["FP"]
    fn, tn = counts["FN"], counts["TN"]

    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    specificity = safe_divide(tn, tn + fp)
    f1 = safe_divide(2 * tp, 2 * tp + fp + fn)

    print("\n" + "=" * 55)
    print("RESULTS — LEGACY DIAGNOSTIC")
    print("=" * 55)

    for label, count in counts.items():
        print(f"{label}: {count}")

    print("Unevaluated:", unevaluated)
    print("Legacy verdicts:", dict(verdict_counts))
    print("Tree statuses:", dict(tree_counts))
    print("Precision:", percentage(precision))
    print("Recall:", percentage(recall))
    print("Specificity:", percentage(specificity))
    print("F1:", percentage(f1))

    print(
        "Preferred correction exact matches:",
        f"{correction_matches}/{correction_total}"
    )

    print("\nLIMITATIONS")
    print("- Corpus annotations are draft, not independently reviewed.")
    print("- Metrics cover only these selected examples.")
    print("- Findings are from legacy constraints, not Cambridge approval.")
    print("- Exact repair matches are not proof of correction validity.")
    print("- No triggered rule does not certify grammatical correctness.")


if __name__ == "__main__":
    main()
