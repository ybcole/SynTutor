"""Regression for server/matrix.py -- every detected error must carry a fix.

Rule enforced: no error detail may be returned without a remediation that
includes a non-empty ``suggested_fix`` the user can act on.

Run:  python test_matrix_remediation.py
"""
import sys

sys.path.insert(0, '/home/jaisenbaloy/Downloads/Programming/SynTutor/server')
from parse_engine import analyze
from matrix import evaluate

# Includes the user's reported example plus a spread of agreement, form,
# determiner, punctuation, fragment, and hybrid-detector style errors.
SENTENCES = [
    "The trees on the birds is really good",   # user's example: VP subject-verb agreement
    "She go to school every day",
    "He are happy",
    "The cat sleep on the mat",
    "I has a book",
    "They was here",
    "The children plays outside",
    "More better than before",
    "Less people came today",
    "Running in the park",
    "the dog barks",
    "She good",
    "The boy run fast",
    "Me and him went home",
    "This are the keys",
    "To go home",
    "Being late",
    "The man who live here is old",
    "Two mans came",
    "She is runing",
    "He had went home",
    "They were ate",
    "She laughed happyly",
    "An apple is red",
    "A apple is red",
    "He don't like it",
    "It rain a lot",
    "We is students",
    "The information are useful",
    "This data is correct",
    "I am agree",
    "She no like it",
    "The book that on the table",
    "He very tall",
    "We going home",
    "They has finished",
]


def main():
    total_errors = 0
    failures = []
    for s in SENTENCES:
        analysis = analyze(s, sentence_index=0)
        root = analysis['root']
        details = evaluate(root, text=s)['details']
        for nid, d in details.items():
            if d['status'] != 'error':
                continue
            total_errors += 1
            rem = d.get('remediation')
            if rem is None:
                failures.append((s, nid, d['constraint'], 'no remediation'))
                continue
            fix = rem.get('suggested_fix') or ''
            if not fix.strip():
                failures.append((s, nid, d['constraint'], 'empty suggested_fix'))
    print(f"errors checked: {total_errors}")
    print(f"failures (error without a usable suggested fix): {len(failures)}")
    for f in failures:
        print("  ", f)
    assert not failures, "some errors lack a suggested fix"
    print("PASS: every detected error has a remediation with a suggested fix")


if __name__ == '__main__':
    main()
