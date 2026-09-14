"""SynTutor rule-matrix coverage audit.

Deterministic, offline check (no HTTP): drives the real parse engine +
matrix over a gold corpus and reports, for every distinct (parent, child)
edge type seen:

    rule id        -> the matrix constraint that fired
    status         -> valid / error / unlisted

Guarantees we care about:
  * no known-grammatical sentence is flagged invalid (no false positives)
  * no known-ungrammatical sentence passes as valid (no false negatives)
  * every distinct edge produced by the corpus is covered by a dedicated
    matrix rule (the ``unrated`` / ``unlisted`` count stays at 0), so a
    future input can never silently rely on "valid-by-default".

Exit code is non-zero on any regression, making it safe to run in CI.
"""

import os
import sys
from collections import Counter
from collections.abc import Iterator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.matrix import evaluate
from server.parse_engine import analyze

GOLD: list[tuple[str, bool, str]] = [
    # (sentence, expected_valid, why)
    ("The boy reads a book.", True, "simple SVO"),
    ("The clever boy reads a fascinating book.", True, "NP modifiers"),
    ("Mary is running in the park.", True, "be + VBG"),
    ("They read books.", True, "plural subject + VBP"),
    ("John runs fast.", True, "3sg subject + VBZ + ADVP"),
    ("The children play in the park every day.", True, "PP adjunct + ADVP"),
    ("She has eaten the cake.", True, "have + VBN"),
    ("They have eaten the cake.", True, "have + VBN (plural)"),
    ("They came home.", True, "irregular VBD"),
    ("They have come home.", True, "irregular VBN"),
    ("I am reading a book.", True, "am (1sg)"),
    ("The book was read by Mary.", True, "passive be + VBN"),
    ("The boys and girls are playing.", True, "coordinated plural subject + are"),
    ("Kielle and Jaisen are my classmates.", True, "coordinated subject (names)"),
    ("Apples and oranges are my favorite.", True, "coordinated plural subject"),
    ("The dog in the park is barking.", True, "NP + PP postmodifier"),
    ("The man who lives next door is kind.", True, "NP + relative clause"),
    ("He will read the book.", True, "modal + VB"),
    ("They will eat the cake.", True, "modal + VB (plural)"),
    ("Mary can swim very fast.", True, "modal + VB + ADVP"),
    ("The teacher speaks English well.", True, "V + NP object + ADVP"),
    ("You are my best friend.", True, "2nd person + are"),
    ("In the park, they run fast.", True, "fronted PP adjunct at S level"),
    ("That he left is true.", True, "clausal subject (SBAR under S)"),
    ("I know which book you read.", True, "embedded wh-clause"),

    ("The boys runs.", False, "subject-verb agreement"),
    ("The boy run.", False, "subject-verb agreement"),
    ("John are running fast.", False, "subject-verb agreement"),
    ("I runs fast.", False, "subject-verb agreement"),
    ("She have a cat.", False, "subject-verb agreement"),
    ("They runs fast.", False, "subject-verb agreement (plural subj)"),
    ("The boys is running fast.", False, "subject-verb agreement (plural subj)"),
    ("Jaisen and Kielle is my thesis groupmates.", False, "coordinated subject (names)"),
    ("Apples and oranges is my favorite.", False, "coordinated plural subject"),
    ("She and I is best friends.", False, "coordinated pronoun subject"),
    ("The boy and girl runs.", False, "coordinated singular subject + 3sg verb"),

    ("These boy runs.", False, "determiner-noun agreement"),
    ("A dogs bark.", False, "determiner-noun agreement"),
    ("Those cat is sleeping.", False, "determiner-noun agreement (pl det)"),

    ("Mary will eats.", False, "auxiliary form (modal)"),
    ("The girl has eat.", False, "auxiliary form (have)"),
    ("They have came home.", False, "past tense cannot follow have"),
    ("They have becomed happy.", False, "invalid regularized form after have"),
    ("They becomed happy.", False, "invalid regularized past form"),
    ("The girl has eats the cake.", False, "auxiliary form (have)"),
    ("The dog is barks loudly.", False, "auxiliary form (be)"),
    ("She is reads the book.", False, "auxiliary form (be)"),
    ("The boy running.", False, "clause finiteness"),
    ("The boy running fast.", False, "clause finiteness"),

    ("The my book is on the table.", False, "determiner stacking (DT + possessive)"),
    ("His the car is red.", False, "determiner stacking (possessive + DT)"),

    ("I hate your.", False, "NP head-licensing (bare possessive determiner)"),
    ("She loves my.", False, "NP head-licensing (bare possessive determiner)"),
    ("Their is a problem.", False, "NP head-licensing (bare possessive)"),
    ("He gave the book to she.", False, "pronoun case (objective after preposition)"),
    ("Me likes music.", False, "pronoun case (objective as subject)"),
    ("Him is running fast.", False, "pronoun case (objective as subject)"),
    ("They call she a hero.", False, "pronoun case (objective as direct object)"),
    ("I gave the gift to he.", False, "pronoun case (objective after preposition)"),
    ("He runs quick.", False, "adjective-adverb confusion (flat adverb)"),
    ("She sings beautiful.", False, "adjective-adverb confusion (adj after action verb)"),
    ("Dog is barking.", False, "missing article (bare singular subject)"),
    ("I need new car.", False, "missing article (bare singular object)"),
    ("He is doctor.", False, "missing article (bare predicate noun)"),
    ("He saw a elephant.", False, "a-an article selection"),
    ("He is an waiter.", False, "a-an article selection"),
    ("he runs fast.", False, "sentence capitalization"),
    ("i am happy.", False, "sentence capitalization"),
    ("He ate less cookies.", False, "quantifier-noun agreement (less + plural)"),
    ("I have fewer money.", False, "quantifier-noun agreement (fewer + mass)"),
    ("She has much friends.", False, "quantifier-noun agreement (much + plural)"),
    ("I eat many apple.", False, "quantifier-noun agreement (many + singular)"),
    ("He is more smarter.", False, "double comparative"),
    ("He is most biggest.", False, "double superlative"),
    ("I am agree.", False, "VP headed by a noun (missing verb form)"),
    ("He decided to stays.", False, "to-infinitive complement instead of base form"),

    ("I hate your car.", True, "possessive determiner + noun (valid)"),
    ("Our house is big.", True, "possessive determiner + noun (valid)"),
    ("My favorite color is blue.", True, "nominalized adjective head 'favorite' (valid)"),
    ("She likes me.", True, "objective pronoun as object (valid)"),
    ("I gave her the book.", True, "objective pronoun + indirect object (valid)"),
    ("She talked to me.", True, "objective pronoun after preposition (valid)"),
    ("He works quickly.", True, "adverb form after action verb (valid)"),
    ("The boys run fast.", True, "legitimate flat adverb 'fast' (valid)"),
    ("An apple a day helps the doctor.", True, "an + vowel sound (valid)"),
    ("He finished an hour ago.", True, "an + silent-h hour (valid)"),
    ("She is an honest student.", True, "an + silent-h honest (valid)"),
    ("He attends a university.", True, "a + consonant-sound university (valid)"),
    ("I love music.", True, "mass noun without article (valid)"),
    ("Reading is fun.", True, "gerund-like subject + uncountable fun (valid)"),
    ("He goes home.", True, "bare institutional noun (valid)"),
    ("It is I.", True, "nominative after copula (valid)"),
    ("They made her happy.", True, "object complement without case error (valid)"),
    ("He seems happy.", True, "linking verb + predicate adjective (valid)"),
    ("Every boy ran fast.", True, "determiner every + singular (valid)"),
    ("I bought fewer cookies.", True, "fewer + plural count (valid)"),
    ("He has less money.", True, "less + mass noun (valid)"),
    ("She has many friends.", True, "many + plural count (valid)"),
    ("This is my new phone.", True, "standalone demonstrative subject (valid)"),
    ("These are my books.", True, "standalone demonstrative subject (valid)"),
    ("Each is important.", True, "quantifier pronoun head (valid)"),
    ("I wanted to go home.", True, "to-infinitive complement clause (valid)"),
    ("She decided to stay.", True, "to-infinitive complement clause (valid)"),
    ("He is more beautiful.", True, "analytic comparative, degree marker + positive (valid)"),
]


def edge_iter(details: dict) -> Iterator[tuple[str, str, str, str]]:
    """Yield (parent_type, child_type, constraint, status) for every edge."""
    type_of = {d['id']: d['type'] for d in details.values()}
    for d in details.values():
        pid = d.get('parent')
        if pid is None:
            continue
        yield type_of[pid], d['type'], d['constraint'], d['status']


def run_corpus() -> tuple[list[dict], Counter, Counter, set]:
    records = []
    violations = []
    edge_counter = Counter()
    status_counter = Counter()
    unlisted_edges = set()
    for text, expected, why in GOLD:
        analysis = analyze(text)
        result = evaluate(analysis['root'])
        details = result['details']
        summary = result['summary']
        actual = summary['valid']
        edges = list(edge_iter(details))
        edge_counter.update((pt, ct) for pt, ct, _, _ in edges)
        status_counter.update(st for _, _, _, st in edges)
        for pt, ct, constraint, status in edges:
            if status == 'unlisted':
                unlisted_edges.add((pt, ct, constraint))
        for d in details.values():
            if d['status'] == 'error':
                violations.append((text, d['type'], d['constraint'], d['text']))
        records.append({
            'text': text,
            'expected': expected,
            'actual': actual,
            'why': why,
            'ok': expected == actual,
            'edges': len(edges),
            'fired': sorted(summary['constraints_fired']),
        })
    return records, edge_counter, status_counter, unlisted_edges


def report(records, edge_counter, status_counter, unlisted_edges) -> tuple[int, int, int, int]:
    print('=' * 88)
    print('SynTutor rule-matrix coverage audit')
    print('=' * 88)

    failed = [r for r in records if not r['ok']]
    print(f'\nGold corpus: {len(records)} sentences, '
          f'{len([r for r in records if r["expected"]])} expected-valid / '
          f'{len([r for r in records if not r["expected"]])} expected-invalid.')
    if failed:
        print(f'\n!! REGRESSIONS ({len(failed)})')
        for r in failed:
            print(f'   {r["text"]!r}: expected {"valid" if r["expected"] else "INVALID"} '
                  f'but got {"valid" if r["actual"] else "INVALID"}  [{r["why"]}]  fired={r["fired"]}')
    else:
        print('   all expected verdicts matched  [no false positives / no false negatives]')

    total_edges = sum(status_counter.values())
    print(f'\nEdges evaluated: {total_edges} -> '
          f'{status_counter.get("valid", 0)} valid / '
          f'{status_counter.get("error", 0)} error / '
          f'{status_counter.get("unlisted", 0)} unlisted')
    print(f'Distinct (parent, child) type pairs exercised: {len(edge_counter)}')

    print('\nEdge-coverage matrix (parent TYPE -> child TYPE : constraint)')
    rows = {}
    for (pt, ct), count in sorted(edge_counter.items()):
        rows.setdefault(pt, []).append((ct, count))
    for pt, children in rows.items():
        print(f'  [{pt}]')
        for ct, count in sorted(children):
            print(f'      -> {ct:<6} x{count}')

    if unlisted_edges:
        print(f'\n!! UNLISTED edge types ({len(unlisted_edges)}) - fall through to valid-by-default:')
        for pt, ct, constraint in sorted(unlisted_edges):
            print(f'   [{pt}] -> [{ct}] ({constraint})')
    else:
        print('\n   no unlisted edges - every edge type in the corpus hits a dedicated rule')

    all_errors = []
    for r in records:
        if not r['expected']:
            all_errors.append(r['text'])
    return len(failed), len(unlisted_edges), total_edges, len(all_errors)


def main() -> int:
    records, edges, statuses, unlisted = run_corpus()
    failures, unrated, total, err_total = report(records, edges, statuses, unlisted)
    print(f'\nSUMMARY: gold regressions={failures}  unrated_edge_types={unrated}  '
          f'edges={total}')
    return 1 if (failures or unrated) else 0


if __name__ == '__main__':
    sys.exit(main())