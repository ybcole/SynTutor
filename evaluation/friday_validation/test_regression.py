
import json
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:8001/api/parse"

TEST_CASES = [
    {
        "sentence": "The boy runs.",
        "expected_rules": [],
    },
    {
        "sentence": "The boys runs.",
        "expected_rules": ["C-SUBJECT-AGREEMENT"],
        "expected_correction": "The boys run.",
    },
    {
        "sentence": "She can sing.",
        "expected_rules": [],
    },
    {
        "sentence": "She can sings.",
        "expected_rules": ["C-MODAL-VERB-FORM"],
        "expected_correction": "She can sing.",
    },
]


def analyze(sentence):
    body = json.dumps({"text": sentence}).encode("utf-8")
    request = Request(
        API_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


def run_test(case):
    data = analyze(case["sentence"])
    summary = data.get("summary", {})

    actual_rules = summary.get("constraints_fired", [])
    expected_rules = case["expected_rules"]

    checks = [
        set(actual_rules) == set(expected_rules),
        not summary.get("checker_errors"),
    ]

    if "expected_correction" in case:
        checks.append(
            summary.get("corrected_sentence")
            == case["expected_correction"]
        )

    passed = all(checks)

    print(f"{'PASS' if passed else 'FAIL'}: {case['sentence']}")
    print(f"  Rules: {actual_rules}")
    print(f"  Legacy verdict: {summary.get('verdict')}")
    print(f"  Book verified: {summary.get('book_verified')}")
    print(
        "  Cambridge status:",
        data.get("cambridge_evaluation", {}).get("status"),
    )

    if not passed:
        print(f"  Expected rules: {expected_rules}")
        print(
            "  Actual correction:",
            summary.get("corrected_sentence"),
        )

    return passed


if __name__ == "__main__":
    passed = 0

    for case in TEST_CASES:
        try:
            if run_test(case):
                passed += 1
        except Exception as error:
            print(f"ERROR: {case['sentence']}: {error}")

    total = len(TEST_CASES)
    print(f"\nResults: {passed}/{total} tests passed")
    raise SystemExit(0 if passed == total else 1)
