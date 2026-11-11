
import json
from pathlib import Path
from evaluate_corpus import analyze

CORPUS = Path(__file__).with_name("grammar_corpus.jsonl")

# Local QA taxonomy, not Cambridge-approved rule IDs.
RULE_FAMILIES = {
    "C-SUBJECT-AGREEMENT": "subject_verb_agreement",
    "C-MODAL-VERB-FORM": "modal_plain_form",
}

correct = 0
incorrect = 0
missed = 0
unevaluated = 0

cases = [
    json.loads(line)
    for line in CORPUS.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

print("SYNTUTOR — RULE ATTRIBUTION EVALUATION")
print("=" * 50)

for case in cases:
    if case["expected_acceptable"]:
        continue

    try:
        data = analyze(case["sentence"])
        summary = data["summary"]
        rules = summary["constraints_fired"]

        if not isinstance(rules, list) or summary.get("checker_errors"):
            raise ValueError("Diagnostic result is not usable")

    except Exception as error:
        unevaluated += 1
        print(f'{case["id"]}: UNEVALUATED — {error}')
        continue

    expected = case["phenomenon"]
    actual_families = {
        RULE_FAMILIES.get(rule, f"unmapped:{rule}")
        for rule in rules
    }

    if not rules:
        result = "MISSED"
        missed += 1
    elif expected in actual_families:
        result = "CORRECT ATTRIBUTION"
        correct += 1
    else:
        result = "WRONG OR UNMAPPED ATTRIBUTION"
        incorrect += 1

    print(f'\n{case["id"]}: {result}')
    print("  Sentence:", case["sentence"])
    print("  Expected family:", expected)
    print("  Triggered rules:", rules)
    print("  Observed families:", sorted(actual_families))

print("\n" + "=" * 50)
print("Correct attribution:", correct)
print("Wrong/unmapped attribution:", incorrect)
print("Missed errors:", missed)
print("Unevaluated:", unevaluated)

detected = correct + incorrect
total = detected + missed

if detected:
    print(f"Attribution among detected errors: {correct/detected:.1%}")

if total:
    print(f"Detection + attribution success: {correct/total:.1%}")

print("\nNOTE: These are small, draft-labeled QA examples.")
print("Rule-family mapping is local and requires review.")
print("A match does not independently validate a diagnostic.")
