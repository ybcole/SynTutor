
import json
from pathlib import Path
from collections import Counter
from evaluate_corpus import analyze

CORPUS = Path(__file__).with_name("grammar_corpus.jsonl")

cases = [
    json.loads(line)
    for line in CORPUS.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

acceptable = [
    case for case in cases
    if case["expected_acceptable"]
]

counts = Counter()

print("SYNTUTOR — STRUCTURAL COVERAGE EVALUATION")
print("=" * 55)

for case in acceptable:
    try:
        result = analyze(case["sentence"])
        br = result.get("br_analysis") or {}
        status = br.get("status") or "missing"
    except Exception as error:
        status = "request_failed"
        print(f'{case["id"]}: REQUEST FAILED — {error}')

    counts[status] += 1

    print(f'\n{case["id"]}: {status.upper()}')
    print("  Sentence:", case["sentence"])
    print("  Phenomenon:", case["phenomenon"])

print("\n" + "=" * 55)
print("RESULTS")
print("=" * 55)

total = len(acceptable)
normalized = counts["normalized"]
unresolved = counts["unresolved"]
failures = counts["request_failed"]

print("Acceptable sentences:", total)
print("Normalized:", normalized)
print("Unresolved:", unresolved)
print("Request failures:", failures)
print("Other statuses:", total - normalized - unresolved - failures)

if total:
    print(f"Normalized coverage: {normalized / total:.1%}")

print("\nLIMITATIONS")
print("- Corpus is small and draft-labeled.")
print("- Normalized does not prove tree correctness.")
print("- Unresolved does not mean ungrammatical.")
print("- Tree structure requires separate validation.")
