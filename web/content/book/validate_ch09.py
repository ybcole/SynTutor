#!/usr/bin/env python3
"""Book-answer validator for SynTutor Chapter 9 (V9)."""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {
    'S', 'S-bar', 'S-dbar', 'NP', 'VP', 'AP', 'AdvP', 'PP',
    'V', 'MOD', 'PROG', 'TENSE', 'C1', 'C2',
    'N', 'NOM', 'DET', 'ART', 'A', 'P', 'pronoun', 'name'
}
STATUSES = {'IMG', 'IMG_ANOMALY', 'TXT', 'DERIVED_FROM_INSTRUCTIONS', 'UNSURE'}


def children(node):
    if node.get('triangle') or 'word' in node or node.get('gap'):
        return []
    return node.get('children', [])


def leaves(node):
    if node.get('gap') or node.get('elided'):
        return []
    if 'word' in node:
        return [node['word']]
    if node.get('triangle'):
        return list(node.get('words', []))
    return [word for child in node.get('children', []) for word in leaves(child)]


def walk(node, parent=None):
    yield node, parent
    for child in children(node):
        yield from walk(child, node)


def norm_words(words):
    return [str(w).replace('’', "'").replace('‘', "'").lower().strip() for w in words]


def sentence_tokens(sentence):
    sentence = sentence.replace('’', "'").replace('‘', "'")
    tokens = re.findall(r"'[A-Za-z0-9]+|[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[^\w\s]", sentence)
    return [x.lower() for x in tokens if re.search(r'[A-Za-z0-9]', x)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=str(HERE / 'ch09.trees.json'))
    args = parser.parse_args()
    data = json.loads(Path(args.data).read_text(encoding='utf-8'))

    checks, failures = [], []

    def check(label, ok):
        checks.append(label)
        if not ok:
            failures.append(label)

    check('chapter and convention version', data.get('chapter') == 9 and data.get('convention_version') == 'V9')
    trees = data.get('trees', [])
    ids = [tree.get('id') for tree in trees]
    by_id = {tree.get('id'): tree for tree in trees}
    check('unique tree ids', len(ids) == len(set(ids)))
    check('21 phrase-marker records present', len(trees) == 21)

    for record in trees:
        ident = record.get('id', '<missing-id>')
        tree = record.get('tree', {})
        check(f'{ident}: source status valid', record.get('status') in STATUSES)
        check(f'{ident}: leaves match sentence in order', norm_words(leaves(tree)) == sentence_tokens(record.get('sentence', '')))
        labels = {node.get('label') for node, _ in walk(tree) if node.get('label')}
        check(f'{ident}: V9 label inventory', labels <= ALLOWED)
        for node, parent in walk(tree):
            if node.get('triangle'):
                check(f'{ident}: triangle is a labelled or C2-unlabelled leaf',
                      (bool(node.get('label')) or (parent is not None and parent.get('label') == 'C2'))
                      and bool(node.get('words')) and not node.get('children'))
            if node.get('gap'):
                check(f'{ident}: gap is a leaf', 'word' not in node and not node.get('children'))
            if node.get('label') == 'S-dbar' and not node.get('triangle'):
                check(f'{ident}: S-double-bar dominates C2 then S-bar',
                      [c.get('label') for c in node.get('children', [])] == ['C2', 'S-bar'])
            if node.get('label') == 'S-bar':
                check(f'{ident}: S-bar dominates C1 then S',
                      [c.get('label') for c in node.get('children', [])] == ['C1', 'S'])
            if node.get('label') == 'C1':
                check(f'{ident}: C1 is empty or contains one terminal',
                      len(node.get('children', [])) in (0, 1)
                      and (not node.get('children') or 'word' in node['children'][0]))
            if node.get('label') == 'C2' and not node.get('triangle'):
                check(f'{ident}: C2 contains one wh terminal/phrase', len(node.get('children', [])) == 1)

        gap_category = record.get('wh_gap_category')
        if gap_category:
            check(f'{ident}: wh-gap category recorded', gap_category in {'NP', 'PP', 'AP', 'AdvP'})
            explicit_gaps = [(node, parent) for node, parent in walk(tree) if node.get('gap')]
            if tree.get('label') == 'S-dbar' and not any(n.get('triangle') for n, _ in walk(tree)):
                check(f'{ident}: wh-fronting leaves an explicit category gap',
                      any(parent is not None and parent.get('label') == gap_category for _, parent in explicit_gaps))

    echo = by_id['ch9-11a']['tree']
    moved = by_id['ch9-11b']['tree']
    check('[11a] echo question remains a basic S, without S-double-bar', echo.get('label') == 'S')
    check('[11b] fronted wh-question begins with S-double-bar', moved.get('label') == 'S-dbar')
    check('[11b] both C2 wh and C1 auxiliary are present',
          [c.get('label') for c in moved.get('children', [])] == ['C2', 'S-bar']
          and norm_words(leaves(moved['children'][0])) == ['what']
          and norm_words(leaves(moved['children'][1]['children'][0])) == ['is'])
    check('[11b] the object and progressive positions are gaps',
          sum(1 for n, _ in walk(moved) if n.get('gap')) == 2)

    t26 = by_id['ch9-26']['tree']
    sbar26 = next((n for n, _ in walk(t26) if n.get('label') == 'S-bar'), {})
    v26 = next((n for n, _ in walk(t26) if n.get('label') == 'V' and norm_words(leaves(n)) == ["wasn't"]), {})
    check('[26] image anomaly preserved: wasn’t is printed with [intens, pres]',
          by_id['ch9-26'].get('status') == 'IMG_ANOMALY' and v26.get('features') == ['intens', 'pres'])
    check('[26] subordinate wh clause has empty C1',
          bool(sbar26) and sbar26.get('children', [{}])[0].get('label') == 'C1'
          and not sbar26['children'][0].get('children'))
    check('[26] who leaves an NP gap as complement of P to',
          any(n.get('label') == 'PP' and len(n.get('children', [])) == 2
              and n['children'][0].get('label') == 'P'
              and norm_words(leaves(n['children'][0])) == ['to']
              and n['children'][1].get('label') == 'NP'
              and any(g.get('gap') for g, _ in walk(n['children'][1]))
              for n, _ in walk(t26)))

    t38, t39, t59, t60 = (by_id[x]['tree'] for x in ('ch9-38', 'ch9-39', 'ch9-59', 'ch9-60'))
    check('[38] noun-complement clause is S-bar introduced by C1 that, with no gap',
          any(n.get('label') == 'S-bar' and n.get('children', [{}])[0].get('label') == 'C1'
              and norm_words(leaves(n['children'][0])) == ['that']
              and not any(g.get('gap') for g, _ in walk(n)) for n, _ in walk(t38)))
    check('[39] restrictive relative clause is sister of NOM',
          any(n.get('label') == 'NOM' and any(c.get('label') == 'S-dbar' and c.get('triangle') for c in n.get('children', []))
              for n, _ in walk(t39)))
    check('[59] restrictive relative clause is sister of NOM',
          any(n.get('label') == 'NOM' and any(c.get('label') == 'S-dbar' and c.get('triangle') for c in n.get('children', []))
              for n, _ in walk(t59)))
    check('[60] non-restrictive relative clause is sister of NP',
          t60.get('label') == 'NP' and [c.get('label') for c in t60.get('children', [])] == ['NP', 'S-dbar'])

    known = set(ids)
    refs_ok = True
    for answer in data.get('discussion_answers', []):
        refs_ok &= set(answer.get('tree_ids', [])) <= known
    for answer in data.get('exercise_answers_from_book', {}).values():
        refs_ok &= set(answer.get('tree_ids', [])) <= known
    check('discussion and exercise tree references resolve', refs_ok)
    check('one structural fragment for the [10] two-C-position schema',
          len(data.get('node_fragments', [])) == 1
          and data['node_fragments'][0].get('id') == 'ch9-frag-10')
    fragment = data.get('node_fragments', [{}])[0].get('node', {})
    check('[10] fragment records S-double-bar > C2 + S-bar > C1 + S',
          fragment.get('label') == 'S-dbar'
          and [c.get('label') for c in fragment.get('children', [])] == ['C2', 'S-bar']
          and [c.get('label') for c in fragment['children'][1].get('children', [])] == ['C1', 'S'])

    acas = data.get('acas', [])
    check('four Exercise 4 ACA answers present', len(acas) == 4)
    for aca in acas:
        ident = aca.get('id', '<missing-aca>')
        clauses = aca.get('clauses', [])
        clause_ids = [c.get('id') for c in clauses]
        refs = {c.get('id') for c in clauses}
        check(f'{ident}: unique S ids', len(clause_ids) == len(set(clause_ids)))
        check(f'{ident}: exactly one main S1', sum(bool(c.get('main')) for c in clauses) == 1
              and any(c.get('id') == 'S1' and c.get('main') is True for c in clauses))
        check(f'{ident}: subordinate clause references resolve',
              all(set(c.get('contains', [])) <= refs for c in clauses))
        check(f'{ident}: one lexical verb recorded per clause',
              len(clauses) == len([c for c in clauses if isinstance(c.get('lexical_verb'), str) and c['lexical_verb'].strip()]))
        expected = [f'S{i}' for i in range(1, len(clauses) + 1)]
        check(f'{ident}: clause ids are sequential', clause_ids == expected)

    print(f"Chapter 9 validator: {len(checks)-len(failures)}/{len(checks)} checks passed; "
          f"{len(trees)} trees; {len(data.get('node_fragments', []))} node fragments; {len(acas)} ACAs.")
    if failures:
        for failure in failures:
            print('FAIL:', failure)
        return 1
    print('ALL OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
