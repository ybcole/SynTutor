"""One-shot helper that injects the Chapter 6 worked example tree, teaching blocks and
guided question into the self-contained pilot JSON (web/content/lessons/br-06-pilot.json).

The reviewed catalog (course.json) is never modified. The pilot is merged over the
catalog at load time, so these authored fields replace the legacy 1.0.0 body only in
preview mode, exactly like the Chapter 5 pilot.

Run once from the repository root with UTF-8 mode:
    python -X utf8 scripts/build_br06_pilot.py
It is idempotent: re-running replaces the authored fields.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'web/content/lessons/br-06-pilot.json'
COURSE = ROOT / 'web/content/lessons/course.json'


def tokenise(text):
    tokens, offset = [], 0
    for word in text.split(' '):
        tokens.append({'index': len(tokens), 'text': word, 'char_span': [offset, offset + len(word)]})
        offset += len(word) + 1
    return tokens


SENTENCE = 'You should have written an essay'
TOKENS = tokenise(SENTENCE)


def build_root():
    return {
        'id': 'lesson-br-06-worked-root',
        'label': 'S',
        'token_span': [0, 6],
        'children': [
            {'id': 'lesson-br-06-worked-root-0', 'label': 'NP', 'triangle': True,
             'words': ['You'], 'token_span': [0, 1]},
            {
                'id': 'lesson-br-06-worked-root-1', 'label': 'VP', 'token_span': [1, 6],
                'children': [
                    {'id': 'lesson-br-06-worked-root-1-0', 'label': 'MOD', 'features': ['past'],
                     'token_span': [1, 2],
                     'children': [{'id': 'lesson-br-06-worked-root-1-0-0', 'word': 'should', 'token_span': [1, 2]}]},
                    {
                        'id': 'lesson-br-06-worked-root-1-1', 'label': 'VP', 'token_span': [2, 6],
                        'children': [
                            {'id': 'lesson-br-06-worked-root-1-1-0', 'label': 'PERF', 'token_span': [2, 3],
                             'children': [{'id': 'lesson-br-06-worked-root-1-1-0-0', 'word': 'have', 'token_span': [2, 3]}]},
                            {
                                'id': 'lesson-br-06-worked-root-1-1-1', 'label': 'VP', 'token_span': [3, 6],
                                'children': [
                                    {'id': 'lesson-br-06-worked-root-1-1-1-0', 'label': 'V', 'features': ['trans'],
                                     'token_span': [3, 4],
                                     'children': [{'id': 'lesson-br-06-worked-root-1-1-1-0-0', 'word': 'written', 'token_span': [3, 4]}]},
                                    {'id': 'lesson-br-06-worked-root-1-1-1-1', 'label': 'NP', 'triangle': True,
                                     'words': ['an', 'essay'], 'token_span': [4, 6]},
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }


TREE = {
    'schema_version': '1.1.0',
    'tree_id': 'lesson-br-06-worked',
    'tokens': TOKENS,
    'convention_profile': {'chapter': 6, 'version': 'V6', 'profile_id': 'V6'},
    'source': {
        'book': 'Burton-Roberts, Analysing Sentences',
        'edition': '3rd edition (Pearson Education, 2011; ISBN 9781408233740)',
        'chapter': 6,
        'printed_page': 122,
        'evidence_status': 'IMG',
        'review_status': 'INDEPENDENTLY_REVIEWED',
        'review_note': 'Tree adapted from printed example [53b] on p. 122.',
        'source_record_id': 'lesson-br-06-worked',
    },
    'movement': [],
    'accepted_alternatives': [],
    'notes': [],
    'sentence': SENTENCE,
    'root': build_root(),
}

WORKED = {
    'sentence': SENTENCE,
    'origin': 'Adapted from printed example [53b] on p. 122.',
    'steps': [
        {'text': 'MOD “should” [past] heads the highest VP and is the only tensed verb.',
         'source_ids': ['BR-3E-P121', 'BR-3E-P122'], 'focus_node_id': 'lesson-br-06-worked-root-1-0'},
        {'text': 'PERF “have” heads the next VP, the complement of the MOD VP.',
         'source_ids': ['BR-3E-P122'], 'focus_node_id': 'lesson-br-06-worked-root-1-1-0'},
        {'text': 'The lexical VP “written an essay” is the complement of the PERF VP.',
         'source_ids': ['BR-3E-P122', 'BR-3E-P123'], 'focus_node_id': 'lesson-br-06-worked-root-1-1-1'},
    ],
    'source_ids': ['BR-3E-P121', 'BR-3E-P122', 'BR-3E-P123'],
    'tree': TREE,
    'accepted_alternatives': [],
}

GUIDED = {
    'id': 'guided',
    'prompt': 'In this worked tree, the PERF VP “have written an essay” is the complement of which node?',
    'options': [
        {'id': 'a', 'text': 'The lexical V “written”', 'feedback': 'Try again. The lexical verb sits lowest. The PERF VP is the complement of the MOD VP.'},
        {'id': 'b', 'text': 'The MOD VP “should”', 'feedback': 'Yes. Each auxiliary VP takes the next VP as its complement; “should” heads the outer VP.'},
        {'id': 'c', 'text': 'The object NP “an essay”', 'feedback': 'Try again. The object NP is below the lexical verb, not above the PERF VP.'},
    ],
    'answer': 'b',
    'hint': 'Look at the highest verb. It is the modal “should”, and the next VP below it is its complement.',
    'source_ids': ['BR-3E-P121', 'BR-3E-P122'],
    'outcome_ids': ['o1'],
    'build_target': {'node_id': 'lesson-br-06-worked-root-1-1', 'field': 'label', 'expected': 'VP'},
}

TEACHING = [
    {'text': 'Each auxiliary is the head of its own VP and takes the next VP as its complement, producing a chain of nested VPs.',
     'source_ids': ['BR-3E-P121', 'BR-3E-P122']},
    {'text': 'Only the first verb in the sequence carries the tense feature.',
     'source_ids': ['BR-3E-P122', 'BR-3E-P123']},
    {'text': 'The auxiliary types appear in a fixed order: MOD, then PERF, then PROG, then PASS.',
     'source_ids': ['BR-3E-P123', 'BR-3E-P124']},
]


def main():
    pilot = json.loads(PILOT.read_text(encoding='utf-8'))
    catalog = json.loads(COURSE.read_text(encoding='utf-8'))
    catalog_ids = {source['id'] for source in catalog['sources']}
    # A pilot merges its preview_sources into the catalog at load time, so any
    # source that already exists in the catalog would duplicate its ID.
    ordered = {}
    for key in ('title', 'content_version', 'estimated_minutes', 'outcomes'):
        if key in pilot:
            ordered[key] = pilot[key]
    ordered['description'] = pilot.get('description', '')
    ordered['teaching'] = TEACHING
    ordered['worked_example'] = WORKED
    ordered['guided'] = GUIDED
    ordered['preview_sources'] = [source for source in pilot['preview_sources']
                                  if source['id'] not in catalog_ids]
    ordered['revised_assessment'] = pilot['revised_assessment']
    PILOT.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Injected teaching, worked example and guided question into br-06-pilot.json.')


if __name__ == '__main__':
    main()
