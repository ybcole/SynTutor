"""Published quiz source/content/blueprint gate; never a parser prediction."""
import hashlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'server'))
from burton_roberts import validate_canonical_tree
from explanations import explain_quiz_response
from seed_quizzes import render as seed_sql

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def projection(n):
    return {k:([projection(x) for x in value] if k=='children' else value) for k,value in n.items() if k in {'label','word','words','children','triangle','gap','features','index','empty','empty_role','unlabelled'}}
def validate(bank=None):
    bank=bank or json.loads((ROOT/'web/content/quizzes/bank.json').read_text())
    schema=json.loads((ROOT/'web/content/quizzes/bank.schema.json').read_text());Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(bank)
    receipt=json.loads((ROOT/'sources/assessment_reviews/2026-11-08-bank.json').read_text())
    assert receipt['bank_sha256']==digest(bank),'Question/source/blueprint content changed after review'
    course=json.loads((ROOT/'web/content/lessons/course.json').read_text());lessons={l['lesson_id']:l for l in course['lessons']};sources={s['id']:s for s in bank['sources']}
    prior_sources={s['id']:s for s in course['sources']}
    for s in bank['sources']:assert {k:v for k,v in s.items() if k not in {'crosswalk_status','crosswalk_scope'}}==prior_sources[s['id']]
    assert len(sources)==len(bank['sources'])
    canonical=Draft202012Validator(json.loads((ROOT/'docs/canonical-burton-roberts-tree.schema.json').read_text()))
    evidence=Draft202012Validator(json.loads((ROOT/'grammar/explanation_evidence.schema.json').read_text()))
    ids=set();pools={};trees=0;stems=set()
    lesson_stems={l[k]['prompt'] for l in course['lessons'] for k in ['predict','guided','transfer','exit']}
    for q in bank['items']:
        key=q['item_id']+'@'+q['content_version'];assert key not in ids;ids.add(key);pools.setdefault(q['pool_id'],[]).append(q)
        assert q['prompt'] not in lesson_stems,'Independent assessment copied a lesson question'
        sig=json.dumps([q['prompt'],q['stimulus'],q['options']],sort_keys=True);assert sig not in stems;stems.add(sig)
        lesson=lessons[q['lesson_id']];assert q['source_ids']==lesson['source_ids'];assert q['concept_ids']==lesson['concept_ids'];assert q['rule_ids']==lesson['rule_ids']
        assert q['outcome_ids']==[q['lesson_id']+':o1'];assert q['convention_profile']==lesson['convention_profile']
        assert q['reference_tree_ids']==lesson['tree_ids'];assert q['answer'] in {o['id'] for o in q['options']}
        if q['claim_scope']=='cambridge_classification':assert all(sources[s]['book']=='Cambridge' for s in q['source_ids'])
        else:assert all(sources[s]['book']=='B-R' for s in q['source_ids'])
        result=explain_quiz_response(q,q['answer'],bank['sources']);evidence.validate(result);assert result['status']=='EXPLAINED'
        if q['answer_tree']:
            tree=q['answer_tree'];canonical.validate(tree);assert validate_canonical_tree(tree)['valid'];trees+=1
            assert tree['convention_profile']==q['convention_profile'];assert tree['source']['evidence_status']=='TXT'
            correct=q['options'][ord(q['answer'])-97]
            assert projection(correct['diagram']['root'])==projection(tree['root'])
            assert sum(projection(o['diagram']['root'])==projection(tree['root']) for o in q['options'])==1
        if q['lesson_id']=='br-11':assert q['answer_tree'] is None and q['convention_profile'] is None
    assessment_ids=set()
    for a in bank['assessments']:
        key=a['assessment_id']+'@'+a['content_version'];assert key not in assessment_ids;assessment_ids.add(key)
        assert len(set(a['pool_ids']))==5
        for p in a['pool_ids']:
            assert p in pools and len(pools[p])==2
            assert len({q['kind'] for q in pools[p]})==1 and len({q['difficulty'] for q in pools[p]})==1
        assert len({pools[p][0]['kind'] for p in a['pool_ids']})>=3
        assert all(l in lessons for l in a['recommended_lessons'])
    assert len(bank['items'])==120 and len(bank['assessments'])==16 and trees==20
    assert (ROOT/'supabase/migrations/20261108000003_quiz_catalog.sql').read_text()==seed_sql()
    print(f'PASS: {len(ids)} reviewed quiz variants, {len(assessment_ids)} five-item blueprints, 20 canonical answer trees, source/outcome separation, feedback schema and SQL seed integrity.')
    return bank
if __name__=='__main__':validate()
