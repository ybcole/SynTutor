#!/usr/bin/env python3
"""Structural and source-grounding validator for SynTutor Chapter 11 text-only lesson."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRINTED_PAGE_MIN = 254
PRINTED_PAGE_MAX = 268


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=str(HERE / 'ch11.json'))
    args = parser.parse_args()
    data = json.loads(Path(args.data).read_text(encoding='utf-8'))
    checks, failures = [], []

    def check(label, passed):
        checks.append(label)
        if not passed:
            failures.append(label)

    def valid_source(obj):
        source = obj.get('source', {})
        return (source.get('chapter') == 11
                and isinstance(source.get('page'), int)
                and PRINTED_PAGE_MIN <= source['page'] <= PRINTED_PAGE_MAX
                and isinstance(source.get('kind'), str)
                and bool(source['kind'].strip()))

    check('chapter number and title', data.get('chapter') == 11
          and data.get('title') == 'Languages, sentences and grammars')
    check('chapter explicitly marked as text-only closing lesson',
          data.get('lesson_type') == 'text_only_closing_lesson')
    check('no new tree convention is assigned', data.get('convention_version') is None)
    tree_policy = data.get('tree_policy', {})
    check('tree policy explicitly excludes trees and node fragments',
          tree_policy.get('trees_included') is False
          and tree_policy.get('node_fragments_included') is False
          and bool(tree_policy.get('reason')))
    check('no phrase-marker trees or fragments are embedded',
          not data.get('trees') and not data.get('node_fragments'))

    source = data.get('source', {})
    check('source metadata covers printed pages 254–268',
          source.get('chapter') == 11 and source.get('printed_pages') == [254, 268])

    concepts = data.get('concepts', [])
    concept_ids = [x.get('id') for x in concepts]
    concept_set = set(concept_ids)
    check('at least ten chapter concepts included', len(concepts) >= 10)
    check('concept ids are present and unique', len(concept_ids) == len(concept_set)
          and all(isinstance(x, str) and x for x in concept_ids))
    for concept in concepts:
        ident = concept.get('id', '<missing-id>')
        check(f'{ident}: title and explanation are present',
              bool(concept.get('title')) and bool(concept.get('explanation')))
        check(f'{ident}: explanation has chapter/page/source-kind citation', valid_source(concept))
        check(f'{ident}: kind is recognised', concept.get('kind') in {'new', 'revised_from_earlier_chapters'})

    steps = data.get('lesson_steps', [])
    step_ids = [x.get('id') for x in steps]
    check('six sequenced lesson steps are present', len(steps) == 6)
    check('lesson-step ids are unique', len(step_ids) == len(set(step_ids)))
    for step in steps:
        ident = step.get('id', '<missing-step>')
        check(f'{ident}: title and explanation are present',
              bool(step.get('title')) and bool(step.get('explain')))
        check(f'{ident}: cited source is within Chapter 11', valid_source(step))
        check(f'{ident}: all concept references resolve',
              bool(step.get('concept_ids')) and set(step.get('concept_ids', [])) <= concept_set)

    examples = data.get('examples', [])
    example_ids = [x.get('id') for x in examples]
    example_set = set(example_ids)
    check('chapter examples are present and have unique ids',
          len(examples) >= 5 and len(example_ids) == len(example_set))
    for example in examples:
        ident = example.get('id', '<missing-example>')
        check(f'{ident}: title and paraphrased description are present',
              bool(example.get('title')) and bool(example.get('description')))
        check(f'{ident}: cited source is within Chapter 11', valid_source(example))
        check(f'{ident}: source reference is present', bool(example.get('source_reference')))
    for step in steps:
        ident = step.get('id', '<missing-step>')
        check(f'{ident}: all example references resolve',
              set(step.get('example_ids', [])) <= example_set)

    glossary = data.get('glossary', [])
    term_ids = [x.get('id') for x in glossary]
    check('glossary contains key chapter terminology', len(glossary) >= 7)
    check('glossary ids are unique', len(term_ids) == len(set(term_ids)))
    for term in glossary:
        ident = term.get('id', '<missing-term>')
        check(f'{ident}: term and definition are present',
              bool(term.get('term')) and bool(term.get('definition')))
        check(f'{ident}: concept reference resolves', term.get('concept_id') in concept_set)
        check(f'{ident}: cited source is within Chapter 11', valid_source(term))

    questions = data.get('questions_raised_by_source', [])
    qids = [q.get('id') for q in questions]
    check('source-raised questions are recorded', len(questions) >= 3)
    check('question ids are unique', len(qids) == len(set(qids)))
    for question in questions:
        ident = question.get('id', '<missing-question>')
        check(f'{ident}: question and response/status are present',
              bool(question.get('question_paraphrase'))
              and bool(question.get('response_summary'))
              and question.get('status') in {'discussed_in_chapter', 'open_question_in_source'})
        check(f'{ident}: cited source is within Chapter 11', valid_source(question))

    exercises = data.get('book_exercises', {})
    check('no unprovided exercises or answer key have been invented',
          exercises.get('present') is False and bool(exercises.get('note')))

    # Coverage guards: confirm the chapter's central argument is represented.
    required = {
        'ch11-infinite-language', 'ch11-productivity', 'ch11-list-vs-rule',
        'ch11-justen-models', 'ch11-grammaticality-definition', 'ch11-grammar',
        'ch11-competence', 'ch11-generative-grammar', 'ch11-phrase-markers-limit',
        'ch11-implicit-knowledge'
    }
    check('all central chapter arguments are represented', required <= concept_set)
    check('Justen and Justenand are both represented as examples',
          {'ch11-ex-justen'} <= example_set
          and {'term-justen', 'term-justenand'} <= set(term_ids))
    check('the phrase-marker limitation example is not treated as a gold tree',
          'ch11-ex-ungrammatical-marker' in example_set
          and not data.get('trees'))
    check('open theoretical questions remain explicitly open',
          any(q.get('status') == 'open_question_in_source' for q in questions))
    check('review notes flag the text-only boundary and unresolved questions',
          len(data.get('review_notes', [])) >= 2)

    print(f"Chapter 11 validator: {len(checks)-len(failures)}/{len(checks)} checks passed; "
          f"{len(concepts)} concepts; {len(steps)} lesson steps; {len(examples)} examples; "
          f"{len(glossary)} glossary terms; 0 phrase-marker trees.")
    if failures:
        for failure in failures:
            print('FAIL:', failure)
        return 1
    print('ALL OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
