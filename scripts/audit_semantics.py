"""SynTutor semantic-layer audit (spec R11).

Deterministic audit of :mod:`server.semantics` against **two separate** corpora,
so syntax correctness and semantic expectations never share a gate:

* the **syntax gold corpus** (:data:`scripts.audit_rules.GOLD`) is semantically
  neutral and must keep its verdict under semantic analysis;
* the **semantic expectation corpus** (:data:`SEMANTIC_CASES`) lists each
  sentence with its expected findings (rule / constraint / severity), and the
  **neutral corpus** (:data:`SEMANTIC_NEUTRAL_EXTRA` plus GOLD) must stay
  finding-free.

Gates
-----
Gate 1  matrix invariance: for every gold sentence ``summary.valid`` and
        ``summary.constraints_fired`` are identical before and after
        ``analyze_semantics``.
Gate 2  false-positive guard: the semantically-neutral corpus produces zero
        findings (including unclassified nouns, which must never be flagged).
Gate 3  finding-set guard: every documented rule fires with the expected
        constraint and severity **and nothing else** — the full expected vs.
        actual finding multiset is compared, so a stray extra finding fails the
        gate as loudly as a missing one (R11.2, R11.3, R11.4, R11.6).  The
        qualitative ``confidence_label`` / ``provenance`` contract is checked
        here too (no numeric confidence may appear).
Gate 4  R11.5 ``The boy saw the man with a telescope.`` reports two structurally
        distinct trees, valid spans, preserved token order, and per-reading
        paraphrase / node_details.
Gate 5  the target ``The number seven is hungry.`` is syntactically valid with
        no false ``C-MOD-POS`` for ``seven``, yields an *advisory* R11.6 warning
        framed "under a literal interpretation" that allows a figurative read,
        and leaves the syntax verdict unchanged.
Gate 6  a controlled semantic failure preserves the syntax verdict and is
        reported as ``unavailable`` (never as an empty all-clear payload).

The process exits non-zero if any gate fails (CI-safe).
"""

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, 'server'))

from server.parse_engine import analyze
from server.matrix import evaluate
from server.semantics import analyze_semantics, structure_fingerprint
from scripts.audit_rules import GOLD  # single source of truth for the syntax corpus

BAR = '=' * 72


# ── helpers ──────────────────────────────────────────────────────────────────

def leaf_surfaces(node):
    """All leaf surfaces in token order."""
    out = []
    stack = [node]
    while stack:
        cur = stack.pop(0)
        if 'children' not in cur:
            out.append(cur['surface'])
        else:
            stack[0:0] = cur['children']
    return out


def walk(node):
    yield node
    for child in node.get('children', []):
        yield from walk(child)


def spans_valid(root):
    """True when every node's span is a contiguous, tightly-nested range."""
    for node in walk(root):
        if 'children' not in node:
            if node['span'][1] != node['span'][0] + 1:
                return False
            continue
        if node['span'] != [node['children'][0]['span'][0],
                            node['children'][-1]['span'][1]]:
            return False
        cursor = node['span'][0]
        for child in node['children']:
            if child['span'][0] != cursor:
                return False
            cursor = child['span'][1]
        if cursor != node['span'][1]:
            return False
    return True


def run(text):
    analysis = analyze(text)
    matrix_result = evaluate(analysis['root'])
    semantics = analyze_semantics(analysis, matrix_result)
    return analysis, matrix_result, semantics


# ── corpora ──────────────────────────────────────────────────────────────────

# Ordinary sentences that must produce NO semantic finding: the false-positive
# guard.  The syntax GOLD corpus is kept semantically neutral and passed here
# too; the extras add explicit uncertainty / idiomaticity / pronoun-NER cases
# (an unclassified noun must never be turned into a finding, a life-state word
# on an artifact is idiomatic, and an animate pronoun/proper noun is fine).
SEMANTIC_NEUTRAL_EXTRA = [
    'The zorblax is hungry.',      # unclassified noun (not in WordNet): no finding
    'The idea is clear.',          # abstract subject, non-biological predicate
    'The rock is cold.',           # inanimate subject, non-biological predicate
    'The battery is dead.',        # life-state word on an artifact is idiomatic
    'She is hungry.',              # pronoun → animate (no literal anomaly)
    'Mary is hungry.',             # PERSON NER → animate
    'They are hungry.',            # plural pronoun → conservative, unclassified
    'The children play in the park every day.',  # habitual: no deictic anchor
    'I always walk to school.',    # generic present: no deictic anchor
]

# Explicit semantic expectations, kept separate from the syntax corpus: each row
# is (sentence, [(rule, constraint, status), ...]).  Gate 3 compares the FULL
# multiset, so each row is both a false-negative and a false-positive guard.
SEMANTIC_CASES = [
    # R11.2 / R8.1 — governed prepositions & light-verb collocations
    ('They depend in the teacher.', [('R11.2', 'S-PREPOSITION', 'error')]),
    ('He will do a decision.', [('R11.2', 'S-COLLOCATION', 'error')]),
    # R11.3 — deictic anchor clashing with the predicate of its own clause
    ('Yesterday I go to school.', [('R11.3', 'S-TENSE-TIME', 'error')]),
    # R11.3 — a habitual adverb no longer blanket-suppresses the whole sentence
    ('Yesterday I go to school every day.',
     [('R11.3', 'S-TENSE-TIME', 'error')]),
    # R11.4 — selectional restriction on the subject and on the object
    ('The book eats the boy.', [('R11.4', 'S-SELECTIONAL', 'error'),
                                ('R11.4', 'S-SELECTIONAL', 'error')]),
    ('The boy eats the rock.', [('R11.4', 'S-SELECTIONAL', 'error')]),
    # R11.6 — explicit project lexicon subjects (numeral head, object, organism)
    ('The number seven is dead.', [('R11.6', 'S-PREDICATE-COMPAT', 'warning')]),
    # R11.6 — WordNet fallback abstraction, and an artifact with no adverb
    ('The algorithm is hungry.', [('R11.6', 'S-PREDICATE-COMPAT', 'warning')]),
    ('The telescope is hungry.', [('R11.6', 'S-PREDICATE-COMPAT', 'warning')]),
]

# §6 preposition-aware attachment paraphrases: (sentence, preposition,
# VP-reading keywords, NP reading keywords).  Gate 4 checks the candidate
# wording changes with the preposition rather than always claiming an
# instrument reading.
PP_CASES = [
    ('The boy saw the man with a telescope.', 'with',
     ('instrument', 'accompaniment'), ('possession', 'attribute')),
    ('She put the book on the table.', 'on',
     ('location', 'setting'), ('location',)),
    ('He bought a gift for his mother.', 'for',
     ['purpose', 'beneficiary'], ['intended for', 'purpose']),
]


# ── gates ────────────────────────────────────────────────────────────────────

def gate_1(corpus):
    """The semantic layer never changes the syntax verdict (matrix invariance)."""
    fails = []
    for text, expected, why in corpus:
        analysis = analyze(text)
        matrix_result = evaluate(analysis['root'])
        before = matrix_result['summary']
        before_key = (before['valid'], tuple(before['constraints_fired']))
        analyze_semantics(analysis, matrix_result)
        after = matrix_result['summary']
        after_key = (after['valid'], tuple(after['constraints_fired']))
        if before_key != after_key:
            fails.append((text, before_key, after_key))
    return fails


def gate_2(texts):
    """No semantic finding on ordinary / neutral sentences (false positives)."""
    fails = []
    for text in texts:
        _, _, semantics = run(text)
        if semantics['findings']:
            fails.append((text, [f['constraint'] for f in semantics['findings']]))
    return fails


QUALITATIVE_LABELS = frozenset({
    'Direct Rule Match', 'Advisory Suggestion', 'Insufficient Evidence',
})


def gate_3():
    """Finding-set guard: each expectation sentence must produce exactly the
    documented findings — a missing finding AND a stray extra finding both fail.
    The qualitative confidence contract is asserted for every finding too."""
    fails = []
    for text, expected in SEMANTIC_CASES:
        _, _, semantics = run(text)
        findings = semantics['findings']
        actual = sorted((f['rule'], f['constraint'], f['status'])
                        for f in findings)
        want = sorted(tuple(w) for w in expected)
        if want != actual:
            extra = list(actual)
            for w in want:
                if w in extra:
                    extra.remove(w)
            missing = list(want)
            for a in actual:
                if a in missing:
                    missing.remove(a)
            if missing:
                fails.append(f'   {text!r}: missing findings {missing}')
            if extra:
                fails.append(f'   {text!r}: unexpected extra findings {extra}')
        for f in findings:
            label = f.get('confidence_label')
            if label not in QUALITATIVE_LABELS:
                fails.append(f'   {text!r}: non-qualitative confidence_label '
                             f'{label!r}')
            if not f.get('provenance'):
                fails.append(f'   {text!r}: finding {f["constraint"]} has no '
                             'provenance')
    return fails


def gate_4():
    """R11.5 produces two distinct, span-valid readings with distinct
    paraphrase / node_details."""
    text = 'The boy saw the man with a telescope.'
    analysis, _, semantics = run(text)
    original = analysis['root']
    original_leaves = leaf_surfaces(original)
    fails = []

    ambiguity = semantics.get('ambiguity') or {}
    if not ambiguity.get('ambiguous'):
        fails.append(f'   {text!r}: ambiguity.ambiguous is not True')
        return fails

    readings = ambiguity.get('readings') or []
    if len(readings) != 2:
        fails.append(f'   {text!r}: expected 2 readings, got {len(readings)}')
        return fails

    fingerprints = []
    for reading in readings:
        label = reading.get('label')
        tree = reading.get('tree')
        if not isinstance(tree, dict):
            fails.append(f'   reading {label!r}: missing tree')
            continue
        if not spans_valid(tree):
            fails.append(f'   reading {label!r}: invalid spans')
        if leaf_surfaces(tree) != original_leaves:
            fails.append(f'   reading {label!r}: token order changed')
        fingerprints.append(structure_fingerprint(tree))
        if not reading.get('paraphrase'):
            fails.append(f'   reading {label!r}: missing paraphrase')
        if not reading.get('thematic_roles'):
            fails.append(f'   reading {label!r}: missing thematic_roles')
        if not reading.get('node_details'):
            fails.append(f'   reading {label!r}: missing node_details')

    if len(set(fingerprints)) != len(fingerprints):
        fails.append('   readings are not structurally distinct')

    paraphrases = [r.get('paraphrase') for r in readings]
    if len(set(paraphrases)) != len(paraphrases):
        fails.append('   readings share a paraphrase')

    detail_blobs = [
        tuple(sorted((k, v.get('role'), v.get('parent'),
                      tuple(v.get('span', [])))
                     for k, v in (r.get('node_details') or {}).items()))
        for r in readings
    ]
    if len(set(detail_blobs)) != len(detail_blobs):
        fails.append('   readings share node_details')

    # §6 — the comparison states its two-reading scope and is not exhaustive.
    scope = (ambiguity.get('scope') or '').lower()
    if 'two' not in scope or 'not' not in scope or 'exhaustive' not in scope:
        fails.append('   ambiguity.scope does not state the two-reading, '
                     'non-exhaustive scope')

    # §6 — paraphrases are hedged candidates, never asserted readings.
    for reading in readings:
        para = (reading.get('paraphrase') or '').lower()
        if 'candidate' not in para and 'one reading' not in para \
                and 'another reading' not in para:
            fails.append(f"   reading {reading.get('label')!r}: paraphrase is "
                         'not framed as a candidate reading')

    # §6 — the candidate wording is preposition-aware (instrument/accompaniment
    # vs. possession for 'with'; location/setting for 'in'/'at'/'on';
    # purpose/beneficiary for 'for').
    for text, prep, vp_terms, np_terms in PP_CASES:
        _, _, sem = run(text)
        amb = sem.get('ambiguity') or {}
        if not amb.get('ambiguous'):
            fails.append(f'   {text!r}: no ambiguity reported')
            continue
        if amb.get('preposition') != prep:
            fails.append(f'   {text!r}: expected preposition {prep!r}, got '
                         f"{amb.get('preposition')!r}")
        rs = amb.get('readings') or []
        if len(rs) != 2:
            fails.append(f'   {text!r}: expected 2 readings, got {len(rs)}')
            continue
        vp_txt = ((rs[0].get('label') or '') + ' '
                  + (rs[0].get('paraphrase') or '')).lower()
        np_txt = ((rs[1].get('label') or '') + ' '
                  + (rs[1].get('paraphrase') or '')).lower()
        if not any(t in vp_txt for t in vp_terms):
            fails.append(f'   {text!r}: VP reading not preposition-aware '
                         f'(missing {vp_terms})')
        if not any(t in np_txt for t in np_terms):
            fails.append(f'   {text!r}: NP reading not preposition-aware '
                         f'(missing {np_terms})')

    return fails


def gate_5():
    """Target sentence: syntactically VALID with no false C-MOD-POS, reported by
    the semantic layer as an advisory literal-interpretation anomaly that allows
    a figurative/personified reading, and with the syntax verdict unchanged."""
    text = 'The number seven is hungry.'
    analysis = analyze(text)
    matrix_result = evaluate(analysis['root'])
    before_key = (matrix_result['summary']['valid'],
                  tuple(matrix_result['summary']['constraints_fired']))
    semantics = analyze_semantics(analysis, matrix_result)
    after_key = (matrix_result['summary']['valid'],
                 tuple(matrix_result['summary']['constraints_fired']))
    fails = []

    if not matrix_result['summary']['valid']:
        fails.append(f'   {text!r}: syntax verdict is not valid')
    if 'C-MOD-POS' in matrix_result['summary']['constraints_fired']:
        fails.append(f"   {text!r}: false C-MOD-POS on the numeral 'seven'")
    if before_key != after_key:
        fails.append(f'   {text!r}: semantic analysis changed the syntax verdict')

    compat = [f for f in semantics['findings']
              if f['constraint'] == 'S-PREDICATE-COMPAT']
    if not compat:
        fails.append(f'   {text!r}: missing the advisory literal-interpretation finding')

    for f in compat:
        if f['status'] != 'warning':
            fails.append(f"   R11.6 finding status is {f['status']!r}, expected 'warning'")
        if f.get('confidence_label') != 'Advisory Suggestion':
            fails.append('   R11.6 finding is not labelled '
                         "'Advisory Suggestion'")
        if 'literal' not in f['text'].lower():
            fails.append('   R11.6 text does not frame the anomaly literally')
        if 'figurative' not in f['suggestion'].lower():
            fails.append('   R11.6 suggestion does not allow a figurative reading')
    return fails


def gate_6():
    """A controlled semantic-layer failure preserves the syntax verdict and is
    reported as ``unavailable`` rather than an empty all-clear payload."""
    import app  # server/app.py, imported with server/ on sys.path

    original = app.analyze_semantics

    def _boom(*_args, **_kwargs):
        raise RuntimeError('simulated semantic failure')

    fails = []
    app.analyze_semantics = _boom
    try:
        payload = app.build_payload('The boy reads a book.')
    finally:
        app.analyze_semantics = original

    if not payload['summary']['valid']:
        fails.append('   syntax verdict lost when the semantic layer failed')
    sem = payload.get('semantics') or {}
    if sem.get('status') != 'unavailable':
        fails.append(f"   expected semantics.status 'unavailable', got {sem.get('status')!r}")
    if sem.get('available') is not False:
        fails.append('   expected semantics.available to be False')
    if sem.get('findings'):
        fails.append('   failure payload must not carry findings')
    if not isinstance(sem.get('summary'), dict):
        fails.append('   failure payload is missing the summary structure')
    return fails


def main() -> int:
    print(BAR)
    print('SynTutor semantic-layer audit (R11.2/R8.1, R11.3, R11.4, R11.5, R11.6)')
    print(BAR)
    print('Syntax corpus : GOLD (semantically neutral)')
    print('Semantic cases: SEMANTIC_CASES (explicit expected findings)')
    print('Neutral guard : GOLD + SEMANTIC_NEUTRAL_EXTRA')

    fails = []

    print('\nGate 1  [matrix invariance]  %d gold sentences' % len(GOLD))
    g1 = gate_1(GOLD)
    if g1:
        fails.append('Gate 1 FAILED')
        for text, before, after in g1:
            print(f'   {text!r}: summary changed {before} -> {after}')
    else:
        print('   pass: summary.valid + constraints_fired unchanged for every sentence')

    neutral = [row[0] for row in GOLD] + list(SEMANTIC_NEUTRAL_EXTRA)
    print(f'\nGate 2  [semantic false-positive guard]  {len(neutral)} sentences')
    g2 = gate_2(neutral)
    if g2:
        fails.append('Gate 2 FAILED')
        for text, fired in g2:
            print(f'   {text!r}: unexpected findings {fired}')
    else:
        print('   pass: 0 semantic findings across the neutral corpus')

    print(f'\nGate 3  [finding-set guard]  {len(SEMANTIC_CASES)} cases')
    g3 = gate_3()
    if g3:
        fails.append('Gate 3 FAILED')
        for line in g3:
            print(line)
    else:
        print('   pass: exact finding sets (rule/constraint/status/count) with '
              'qualitative confidence labels and provenance')

    print('\nGate 4  [R11.5 PP-attachment ambiguity + §6 preposition-aware '
          'paraphrase]')
    g4 = gate_4()
    if g4:
        fails.append('Gate 4 FAILED')
        for line in g4:
            print(line)
    else:
        print('   pass: two distinct, span-valid readings with distinct, hedged, '
              'preposition-aware paraphrase / node_details')

    print('\nGate 5  [target sentence: valid syntax + advisory anomaly]')
    g5 = gate_5()
    if g5:
        fails.append('Gate 5 FAILED')
        for line in g5:
            print(line)
    else:
        print("   pass: 'The number seven is hungry.' is valid and advisory "
              '(R11.6, literal-interpretation wording)')

    print('\nGate 6  [semantic-failure handling]')
    g6 = gate_6()
    if g6:
        fails.append('Gate 6 FAILED')
        for line in g6:
            print(line)
    else:
        print('   pass: failure keeps the syntax verdict and reports '
              "semantics.status='unavailable'")

    print(BAR)
    if fails:
        print('SEMANTIC AUDIT: FAILED')
        for line in fails:
            print(f'   {line}')
        return 1
    print('SEMANTIC AUDIT: ALL GATES PASSED')
    print('  syntax gold corpus (verdicts) and semantic corpus (findings) are '
          'checked separately')
    return 0


if __name__ == '__main__':
    sys.exit(main())
