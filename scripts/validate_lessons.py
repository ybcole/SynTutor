"""Read-only lesson publication/structure/provenance gate, without parser models."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'server'))
from burton_roberts import validate_canonical_tree
from seed_lessons import render as seed_sql
from seed_foundations import render as foundations_sql, TARGET as FOUNDATIONS_SEED

def digest(lesson):
    return hashlib.sha256(json.dumps(lesson,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate(course=None, *, lesson_id=None):
    course=course or json.loads((ROOT/'web/content/lessons/course.json').read_text())
    schema=json.loads((ROOT/'web/content/lessons/course.schema.json').read_text())
    Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(course)
    canonical=Draft202012Validator(json.loads((ROOT/'docs/canonical-burton-roberts-tree.schema.json').read_text()))
    sources={s['id']:s for s in course['sources']};assert len(sources)==len(course['sources'])
    source_hashes={}
    for family in ['burton_roberts','cambridge']:
        source_hashes.update(json.loads((ROOT/f'sources/{family}/reviews/2026-11-08-lessons.json').read_text())['source_sha256'])
    for source in course['sources']:assert source_hashes.get(source['id'])==digest(source),'Source metadata changed after review'
    concepts={c['id']:c for c in course['concepts']};assert len(concepts)==len(course['concepts'])
    lessons={l['lesson_id']:l for l in course['lessons']};assert len(lessons)==len(course['lessons'])
    rules=set()
    for path in (ROOT/'grammar/rules').glob('*.json'):
        data=json.loads(path.read_text());rules.update(r['id'] for r in (data if isinstance(data,list) else data.get('rules',[])))
    ranges={row['chapter']:(row['printed_start'],row['printed_end']) for row in json.loads((ROOT/'sources/burton_roberts/source_manifest_2026-11-08.json').read_text())['files']}
    fixtures={}
    for ch in range(1,11):
        for row in json.loads((ROOT/f'web/content/book/ch{ch:02}.trees.json').read_text())['trees']:fixtures[row['id']]=row
    def cited(ids):
        assert ids and all(id in sources for id in ids),ids
        for ident in ids:
            source=sources[ident]
            if source['book']=='B-R':assert ranges[source['chapter']][0]<=source['printed_page']<=ranges[source['chapter']][1]
    for c in course['concepts']:cited(c['source_ids'])
    if lesson_id is not None and lesson_id not in lessons:
        raise ValueError(f'Unknown lesson ID: {lesson_id}')
    selected = [lessons[lesson_id]] if lesson_id else course['lessons']
    for lesson in selected:
        ident=lesson['lesson_id'];cited(lesson['source_ids'])
        receipt=json.loads((ROOT/lesson['review_receipt']).read_text())
        assert receipt['lesson_sha256'][ident]==digest(lesson),f'{ident}: content changed after source review'
        assert set(lesson['concept_ids'])<=set(concepts)
        assert set(lesson['rule_ids'])<=rules
        for prereq in lesson['prerequisites']:
            prior = lessons[prereq['lesson_id']]
            assert prior['content_version'] == prereq['content_version'] or (
                prior.get('revised_assessment') and prereq['content_version'] == '1.0.0')
        assessment = lesson.get('revised_assessment')
        if assessment:
            assert lesson['track'] == 'foundations' and ident == f"br-{lesson['chapter']:02d}"
            assert lesson['content_version'] != '1.0.0'
            questions = assessment['opening'] + assessment['closing']
            assert len({q['id'] for q in questions}) == len(questions)
            assert len({q['prompt'].strip().casefold() for q in questions}) == len(questions)
            outcomes = {o['id'] for o in lesson['outcomes']}
            for question in questions:
                cited(question['source_ids'])
                assert set(question['outcome_ids']) <= outcomes
                options = {o['id'] for o in question['options']}
                assert question['answer'] in options and len(options) == len(question['options'])
                assert question['prompt'].strip() and all(o['text'].strip() and o['feedback'].strip() for o in question['options'])
            assert outcomes <= {o for q in assessment['closing'] for o in q['outcome_ids']}
        for tree_id in lesson['tree_ids']:
            assert tree_id in fixtures and fixtures[tree_id].get('correct') is not False
            assert fixtures[tree_id]['status']=='IMG',f'{ident}: reference anomaly/uncertainty must be reviewed separately'
        for block in [*lesson['teaching'],*lesson['worked_example']['steps'],*lesson['cambridge_insights']]:cited(block['source_ids'])
        for block in lesson['cambridge_insights']:assert all(sources[s]['book']=='Cambridge' for s in block['source_ids'])
        for key in ['predict','guided','transfer','exit']:
            question=lesson[key];cited(question['source_ids'])
            assert question['id']==key and question['answer'] in {o['id'] for o in question['options']}
            assert set(question['outcome_ids'])<={o['id'] for o in lesson['outcomes']}
        if not assessment:
            assert {o['id'] for o in lesson['outcomes']} <= set(lesson['exit']['outcome_ids'])
        if lesson['track']=='foundations':assert all(sources[s]['book']=='B-R' for s in lesson['source_ids'])
        else:assert all(sources[s]['book']=='Cambridge' for s in lesson['source_ids'])
        tree=lesson['worked_example']['tree']
        if lesson['track']=='foundations' and lesson['chapter']==11:
            assert tree is None and lesson['convention_profile'] is None and not lesson['tree_ids']
        if tree:
            canonical.validate(tree);result=validate_canonical_tree(tree);assert result['valid'],result
            assert tree['convention_profile']==lesson['convention_profile']
            assert tree['convention_profile']['chapter']==lesson['chapter']
            assert tree['source']['evidence_status']=='TXT','Original instructional trees must not claim to be printed diagrams'
            nodes={}
            def walk(node):
                nodes[node.get('id')]=node
                for c in node.get('children',[]):walk(c)
            walk(tree['root'])
            for step in lesson['worked_example']['steps']:assert step['focus_node_id'] in nodes
            target=lesson['guided']['build_target'];node=nodes[target['node_id']]
            actual=node.get('label') if target['field']=='label' else node.get('features',[None])[0]
            assert actual==target['expected'],f'{ident}: guided target does not match its reviewed tree'
    old_seed = (ROOT/'supabase/migrations/20261108000001_lesson_catalog.sql').read_text()
    retired = {lesson['lesson_id'] for lesson in lessons.values() if lesson.get('revised_assessment')}
    if retired:
        old_seed = '\n'.join(line for line in old_seed.splitlines()
                             if not line.startswith(tuple(f"('{ident}','" for ident in retired)))
        current = dict(course, lessons=[lesson for lesson in course['lessons'] if lesson['lesson_id'] not in retired])
        assert old_seed + '\n' == seed_sql(current), 'Legacy database answer contract drift.'
    else:
        assert old_seed == seed_sql(course), 'Legacy database answer contract drift.'
    assert FOUNDATIONS_SEED.read_text() == foundations_sql(course), 'Revised database answer contract drift.'
    scope = lesson_id or f'{len(selected)} lessons'
    print(f'PASS: {scope} lesson checks, {len(sources)} shared source records, course schema and SQL seed integrity.')
    return course

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', help='Check one lesson receipt and content, plus shared schema and SQL seed.')
    validate(lesson_id=parser.parse_args().lesson)
