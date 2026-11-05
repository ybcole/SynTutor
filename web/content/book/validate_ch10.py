#!/usr/bin/env python3
"""Book-answer validator for SynTutor Chapter 10 (V10)."""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {
    'S', 'S-bar', 'S-dbar', 'NP', 'VP', 'NOM', 'DET', 'POSS', 'N',
    'AP', 'A', 'PP', 'P', 'V', 'AUX', 'PERF', 'PROG', 'PASS', 'TENSE',
    'C1', 'C2', 'ART', 'DEM', 'Q', 'PRE-DET', 'PartP', 'AdvP', 'Adv',
    'MOD', 'pronoun', 'name'
}
STATUSES = {'IMG', 'IMG_ANOMALY', 'TXT', 'DERIVED_FROM_INSTRUCTIONS', 'UNSURE'}
OLD_V_FEATURES = {'trans', 'intrans', 'ditrans', 'intens', 'complex', 'prep'}


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


def normalise(words):
    return [str(word).replace('’', "'").replace('‘', "'").lower().strip() for word in words]


def sentence_tokens(sentence):
    sentence = sentence.replace('’', "'").replace('‘', "'")
    tokens = re.findall(r"'[A-Za-z0-9]+|[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[^\w\s]", sentence)
    return [token.lower() for token in tokens if re.search(r'[A-Za-z0-9]', token)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=str(HERE / 'ch10.trees.json'))
    args = parser.parse_args()
    data = json.loads(Path(args.data).read_text(encoding='utf-8'))

    checks, failures = [], []

    def check(label, passed):
        checks.append(label)
        if not passed:
            failures.append(label)

    check('chapter and convention version', data.get('chapter') == 10 and data.get('convention_version') == 'V10')
    trees = data.get('trees', [])
    ids = [tree.get('id') for tree in trees]
    by_id = {tree.get('id'): tree for tree in trees}
    check('unique tree ids', len(ids) == len(set(ids)))
    check('17 phrase-marker records present', len(trees) == 17)

    for record in trees:
        ident = record.get('id', '<missing-id>')
        tree = record.get('tree', {})
        check(f'{ident}: valid source status', record.get('status') in STATUSES)
        check(f'{ident}: terminal sequence matches sentence',
              normalise(leaves(tree)) == sentence_tokens(record.get('sentence', '')))
        labels = {node.get('label') for node, _ in walk(tree) if node.get('label')}
        check(f'{ident}: V10 label inventory', labels <= ALLOWED)
        for node, parent in walk(tree):
            if node.get('triangle'):
                check(f'{ident}: triangle is a labelled leaf',
                      bool(node.get('label')) and bool(node.get('words')) and not node.get('children'))
            if node.get('gap'):
                check(f'{ident}: gap is a leaf', 'word' not in node and not node.get('children'))
            if node.get('label') == 'AUX':
                check(f'{ident}: [-tense] auxiliary is to',
                      node.get('features') == ['-tense'] and normalise(leaves(node)) == ['to'])
            if node.get('label') == 'S-bar':
                check(f'{ident}: S-bar expands to C1 + S',
                      [child.get('label') for child in node.get('children', [])] == ['C1', 'S'])
            if node.get('label') == 'S-dbar':
                check(f'{ident}: S-double-bar expands to C2 + S-bar',
                      [child.get('label') for child in node.get('children', [])] == ['C2', 'S-bar'])
            if node.get('label') == 'C1':
                check(f'{ident}: C1 is empty or has one terminal',
                      len(node.get('children', [])) in (0, 1)
                      and (not node.get('children') or 'word' in node['children'][0]))
            if node.get('label') == 'V' and node.get('verb_type'):
                check(f'{ident}: Type I/II V has no old six-way feature',
                      node.get('verb_type') in {'I', 'II'}
                      and not (set(node.get('features', [])) & OLD_V_FEATURES))

        # Internal co-indexing must resolve within the same tree, unless the source
        # figure is a constituent whose controller is explicitly documented outside it.
        indexes = set()
        gap_indexes = set()
        for node, _ in walk(tree):
            if node.get('index') is not None:
                indexes.add(node['index'])
            if node.get('gap') and node.get('index') is not None:
                gap_indexes.add(node['index'])
        external = {x.get('index') for x in record.get('external_controllers', [])}
        if record.get('external_controller'):
            external.add(record['external_controller'].get('index'))
        check(f'{ident}: every indexed gap has an internal or documented external controller',
              gap_indexes <= indexes | external)

    # Book's key worked structures and their chapter-specific properties.
    t11 = by_id['ch10-11']['tree']
    check('[11] infinitive to is an AUX above a VP complement',
          t11.get('label') == 'VP' and [c.get('label') for c in t11.get('children', [])] == ['AUX', 'VP'])
    t12 = by_id['ch10-12']['tree']
    check('[12] to + PERF + PASS + lexical V order',
          t12.get('label') == 'VP'
          and [c.get('label') for c in t12.get('children', [])] == ['AUX', 'VP']
          and [c.get('label') for c in t12['children'][1].get('children', [])] == ['PERF', 'VP']
          and [c.get('label') for c in t12['children'][1]['children'][1].get('children', [])] == ['PASS', 'VP'])
    check('[12] printed bottom VP gap retained and flagged, indexed 1 to external controller Max',
          by_id['ch10-12'].get('status') == 'IMG_ANOMALY'
          and any(parent is not None and parent.get('label') == 'VP' and node.get('gap') and node.get('index') == 1
                  for node, parent in walk(t12))
          and by_id['ch10-12'].get('external_controller', {}).get('controller') == 'Max')

    t14 = by_id['ch10-14a']['tree']
    check('[14a] subject and passive-object gaps are co-indexed',
          sum(1 for n, _ in walk(t14) if n.get('gap') and n.get('index') == 1) == 2)
    t21 = by_id['ch10-21']['tree']
    check('[21] covert subject gap itself carries index 1',
          any(n.get('gap') and n.get('index') == 1 for n, _ in walk(t21))
          and by_id['ch10-21'].get('external_controller', {}).get('controller') == 'he')
    t22 = by_id['ch10-22']['tree']
    check('[22] PERF having is marked [-tense]',
          any(n.get('label') == 'PERF' and n.get('features') == ['-tense'] for n, _ in walk(t22)))

    t37 = by_id['ch10-37']['tree']
    check('[37] non-finite wh-clause uses C2 and C1, without an overt subordinate subject',
          t37.get('label') == 'S-dbar'
          and [c.get('label') for c in t37.get('children', [])] == ['C2', 'S-bar']
          and not any('word' in n for n, _ in walk(t37['children'][1]['children'][0])))
    check('[37] index 1 subject control and index 2 wh/object dependency',
          any(n.get('gap') and n.get('index') == 1 for n, _ in walk(t37))
          and any(n.get('gap') and n.get('index') == 2 for n, _ in walk(t37))
          and t37['children'][0].get('index') == 2)

    # Discussion trees: ensure all book tree references resolve.
    known = set(ids)
    refs_ok = all(set(item.get('tree_ids', [])) <= known for item in data.get('discussion_answers', []))
    check('all Discussion of in-text exercises tree references resolve', refs_ok)
    check('seven discussion answer records represented', len(data.get('discussion_answers', [])) == 7)
    t44a = by_id['ch10-d3-44a']['tree']
    t44b = by_id['ch10-d3-44b']['tree']
    check('[44a] gap dot is co-indexed with controller Max',
          any(n.get('gap') and n.get('index') == 1 for n, _ in walk(t44a))
          and any(n.get('triangle') and n.get('label') == 'NP' and n.get('index') == 1
                  for n, _ in walk(t44a)))
    check('[44b] lower subject is free and object gap is co-indexed with piano',
          any(n.get('gap') and n.get('index') is None for n, _ in walk(t44b))
          and any(n.get('gap') and n.get('index') == 1 for n, _ in walk(t44b))
          and any(n.get('triangle') and n.get('label') == 'NP' and n.get('index') == 1
                  for n, _ in walk(t44b)))
    t50 = by_id['ch10-d4-50']['tree']
    check('[50] -ing clause subject gap is co-indexed with We',
          any(n.get('gap') and n.get('index') == 1 for n, _ in walk(t50))
          and any(n.get('triangle') and n.get('label') == 'NP' and n.get('index') == 1
                  for n, _ in walk(t50)))
    t55 = by_id['ch10-d5-55b']['tree']
    check('[55b] subject and passive object gaps are both indexed to We',
          sum(1 for n, _ in walk(t55) if n.get('gap') and n.get('index') == 1) == 2
          and any(n.get('triangle') and n.get('label') == 'NP' and n.get('index') == 1
                  for n, _ in walk(t55)))
    check('Discussion 3 includes both adjective-complement patterns',
          set(('ch10-d3-44a', 'ch10-d3-44b')) <= known)
    check('Discussion 6 tree records possessive-controller indexing',
          any(n.get('label') == 'POSS' and n.get('index') == 1
              for n, _ in walk(by_id['ch10-d6-62']['tree']))
          and any(n.get('gap') and n.get('index') == 1
                  for n, _ in walk(by_id['ch10-d6-62']['tree'])))

    # Exercise 2: the two analyses differ in referential/expletive it and V subcategory.
    a, b = by_id['ch10-ex2a']['tree'], by_id['ch10-ex2b']['tree']
    check('Exercise 2(a) represents it as a referential NP and move as transitive',
          a.get('children', [{}])[0].get('index') == 1
          and any(n.get('label') == 'V' and 'trans' in n.get('features', []) for n, _ in walk(a)))
    check('Exercise 2(b) represents expletive it and intransitive move',
          b.get('label') == 'S' and len(b.get('children', [])) == 3
          and b['children'][1].get('triangle')
          and any(n.get('label') == 'V' and 'intrans' in n.get('features', []) for n, _ in walk(b)))

    # Type I / Type II clause-complement distinction.
    t101, t102 = by_id['ch10-101b']['tree'], by_id['ch10-102b']['tree']
    v101 = next((n for n, _ in walk(t101) if n.get('verb_type') == 'I'), {})
    v102 = next((n for n, _ in walk(t102) if n.get('verb_type') == 'II'), {})
    check('[101b] Type I has a single clause complement with overt lower subject',
          bool(v101) and len(v101.get('features', [])) == 1
          and any(n.get('label') == 'S-bar' for n, _ in walk(t101))
          and not any(n.get('gap') for n, _ in walk(t101)))
    check('[102b] Type II has an NP object and controlled covert lower subject',
          bool(v102) and any(n.get('label') == 'NP' and n.get('index') == 1 for n, _ in walk(t102))
          and any(n.get('gap') and n.get('index') == 1 for n, _ in walk(t102)))

    # Standalone fragments [6] and [17].
    fragments = data.get('node_fragments', [])
    check('two single-V fragments [6] and [17] present',
          len(fragments) == 2 and {x.get('id') for x in fragments} == {'ch10-6', 'ch10-17'})
    for fragment in fragments:
        node = fragment.get('node', {})
        check(f"{fragment.get('id')}: node is V with [-tense]", 
              node.get('label') == 'V' and '-tense' in node.get('features', []))

    # Exercise answer completeness and book-provided ACA bookkeeping.
    ex1 = data.get('exercise_answers_from_book', {}).get('exercise_1', {}).get('items', [])
    check('Exercise 1 contains all 12 book discussion answers', len(ex1) == 12)
    check('Exercise 1 distinguishes controlled and free covert NPs',
          all(all(c.get('control') in {'free', 'controlled'} for c in item.get('covert', [])) for item in ex1))
    ex2 = data.get('exercise_answers_from_book', {}).get('exercise_2', {})
    check('Exercise 2 references both interpretation trees', set(ex2.get('tree_ids', [])) == {'ch10-ex2a', 'ch10-ex2b'})
    acas = data.get('acas', [])
    check('five Exercise 3 ACA answers present', len(acas) == 5)
    for aca in acas:
        aid = aca.get('id', '<missing-aca>')
        clauses = aca.get('clauses', [])
        clause_ids = [c.get('id') for c in clauses]
        refs = {c.get('id') for c in clauses}
        check(f'{aid}: S ids unique and sequential',
              len(clause_ids) == len(set(clause_ids))
              and clause_ids == [f'S{i}' for i in range(1, len(clauses) + 1)])
        check(f'{aid}: exactly one main S1',
              sum(bool(c.get('main')) for c in clauses) == 1
              and bool(clauses) and clauses[0].get('id') == 'S1' and clauses[0].get('main') is True)
        check(f'{aid}: clause references resolve',
              all(set(c.get('contains', [])) <= refs for c in clauses))
        check(f'{aid}: lexical verb present for each clause',
              all(isinstance(c.get('lexical_verb'), str) and c['lexical_verb'].strip() for c in clauses))
    check('Exercise 3 answer id references resolve',
          set(data.get('exercise_answers_from_book', {}).get('exercise_3', {}).get('aca_ids', []))
          == {a.get('id') for a in acas})

    relatives = data.get('nonfinite_relative_examples', [])
    check('four non-finite relative-clause schemata are represented', len(relatives) == 4
          and [x.get('fig') for x in relatives] == ['[38b]', '[39b]', '[40b]', '[41b]'])
    check('[38b] preserves a free subject and a wh-controlled object gap',
          any(g.get('position') == 'subject' and g.get('control') == 'free' for g in relatives[0].get('gaps', []))
          and any(g.get('position') == 'object' and g.get('control') == 'controlled' for g in relatives[0].get('gaps', [])))
    check('[39b] retains overt subject you and C1 for',
          relatives[1].get('overt_subject') == 'you' and relatives[1].get('complementiser') == 'for')
    check('[40b] represents the covert wh-subject gap',
          any(g.get('position') == 'subject' for g in relatives[2].get('gaps', [])))
    check('[41b] distinguishes the relative subject gap from the passive object gap',
          len(relatives[3].get('gaps', [])) == 2)

    whether_examples = data.get('nonfinite_whether_examples', [])
    check('three C1 whether-clause examples represented', len(whether_examples) == 3
          and [x.get('fig') for x in whether_examples] == ['[30]', '[31]', '[32]'])
    check('whether examples distinguish controlled subjects from a free subject clause',
          [x.get('subject_control') for x in whether_examples] == ['controlled', 'controlled', 'free'])
    check('controlled whether-clause subjects use the higher clause subjects as controllers',
          whether_examples[0].get('controller', '').startswith('King Louis')
          and whether_examples[1].get('controller', '').startswith('Olsen'))

    wh_examples = data.get('nonfinite_wh_examples', [])
    check('four non-finite wh-interrogative examples represented', len(wh_examples) == 4
          and [x.get('fig') for x in wh_examples] == ['[33]', '[34]', '[35]', '[36]'])
    check('[33] subject is controlled by matrix subject Sarah',
          wh_examples[0].get('subject_gap', {}).get('controller', '').startswith('Sarah'))
    check('[34] subject is controlled by matrix object me',
          wh_examples[1].get('subject_gap', {}).get('controller', '').startswith('me'))
    check('[35] wh-gap is complement of P for',
          wh_examples[2].get('wh_gap', {}).get('position') == 'complement of P for')
    check('[36] expletive it leaves lower subject free',
          wh_examples[3].get('subject_gap', {}).get('control') == 'free')

    for_examples = data.get('for_clause_examples', [])
    check('four for-infinitive examples represented', len(for_examples) == 4
          and [x.get('fig') for x in for_examples] == ['[26]', '[27]', '[28]', '[29]'])
    check('[29] records that for is not possible and C1 is empty',
          for_examples[-1].get('C1') == 'empty')

    # Verb lists and chapter-level boundaries.
    check('Type I and Type II reference inventories are non-empty and disjoint',
          bool(data.get('type_i_verbs')) and bool(data.get('type_ii_verbs'))
          and not (set(data['type_i_verbs']) & set(data['type_ii_verbs'])))
    classif = data.get('exercise_3_type_classification', {})
    check('Discussion 7 exercise classification includes all 17 verbs',
          len(classif.get('type_i', [])) + len(classif.get('type_ii', [])) == 17
          and not (set(classif.get('type_i', [])) & set(classif.get('type_ii', []))))
    check('Further Exercises without printed answers are explicitly excluded',
          len(data.get('no_book_tree', [])) >= 2)

    print(f"Chapter 10 validator: {len(checks)-len(failures)}/{len(checks)} checks passed; "
          f"{len(trees)} trees; {len(fragments)} node fragments; {len(acas)} ACAs.")
    if failures:
        for failure in failures:
            print('FAIL:', failure)
        return 1
    print('ALL OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
