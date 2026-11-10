"""One canonical evaluator for Generator and learner-constructed trees.

No parser, detector, client source claims or legacy matrix establishes authority.
"""
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from burton_roberts import validate_canonical_tree
from cambridge_evaluator import evaluate_cambridge
from cambridge_registry import load_runtime_registry
from explanations import explain_analysis, nodes_of
ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Draft202012Validator(json.loads((ROOT/'docs/canonical-burton-roberts-tree.schema.json').read_text()))

def signature(tree):
    """Identity-free ordered structure; movement references resolve to paths."""
    paths = {ident:path for path,(ident,_) in enumerate(nodes_of(tree))}
    def node(n):
        keys = ('label','word','words','triangle','unlabelled','gap','empty','empty_role','elided','index')
        out = {k:n[k] for k in keys if k in n}
        if n.get('features'): out['features'] = sorted(n['features'])
        if 'children' in n: out['children'] = [node(c) for c in n['children']]
        return out
    movement = []
    for m in tree.get('movement',[]):
        movement.append({k:(paths.get(v,v) if k.endswith('_node_id') else v) for k,v in m.items() if k!='notes'})
    return {'root':node(tree['root']),'movement':sorted(movement,key=lambda m:json.dumps(m,sort_keys=True))}

def compare_target(tree, target):
    if tree['convention_profile'] != target['convention_profile']:
        return {'status':'profile_mismatch','matched':False}
    candidates = [('primary',target)]
    for i,alt in enumerate(target.get('accepted_alternatives',[])):
        if alt.get('acceptance') not in {'ACCEPTED','PREFERRED'}: continue
        candidate = {**target,'root':alt['root'],'movement':[],'accepted_alternatives':[]}
        if validate_canonical_tree(candidate)['valid'] and not list(SCHEMA.iter_errors(candidate)):
            candidates.append((alt.get('analysis_id',f'alternative-{i}'),candidate))
    for ident,candidate in candidates:
        if signature(tree)==signature(candidate): return {'status':'matched','matched':True,'analysis_id':ident}
    return {'status':'different_from_target','matched':False,
            'message':'This structure differs from the reviewed exercise analyses. This is not a grammaticality verdict.'}

def evaluate_analysis(analysis, *, variety=None):
    tree = analysis.get('tree')
    structure = {'valid':False,'errors':[],'warnings':[],'status':'unresolved'}
    if analysis.get('status')=='normalized' and isinstance(tree,dict):
        structure = validate_canonical_tree(tree)
        structure['errors'] += [f'{e.json_path}: {e.message}' for e in list(SCHEMA.iter_errors(tree))[:20]]
        structure['valid'] = not structure['errors']
        structure['status'] = 'invalid' if not structure['valid'] else 'unsupported' if structure['warnings'] else 'well_formed'
    # Preserve raw source text for XAI-4 token-level observations even when
    # the B-R structural envelope cannot be normalized. No B-R role is inferred.
    safe = analysis if structure['valid'] else {
        'status': 'unresolved',
        'sentence': analysis.get('sentence') or (tree.get('sentence') if isinstance(tree, dict) else None),
    }
    runtime = load_runtime_registry()
    evaluation = evaluate_cambridge(safe,runtime,variety=variety)
    evidence = explain_analysis(safe,variety=variety)
    details = {}
    if structure['valid']:
        for ident,node in nodes_of(tree):
            records = [r for channel in evidence['channels'].values() for r in channel if r.get('node_id')==ident]
            details[ident] = {'node_id':ident,'label':node.get('label'),'status':'explained' if records else 'NO_BOOK_BASIS',
                              'evidence':records,'source_refs':[s for r in records for s in r.get('sources',[])]}
    findings = evaluation.get('findings',[])
    grammar = {'status':'constraint_violation' if findings else 'unresolved',
               'message':'A reviewed constraint found a violation.' if findings else 'No grammaticality verdict is established by this tree check.',
               'evaluated_rule_ids':evaluation.get('evaluated_rule_ids',[])}
    return {'schema_version':'1.0.0','br_analysis':safe,'structure':structure,'grammaticality':grammar,
            'cambridge_evaluation':evaluation,'explanation_evidence':evidence,
            'fact_graph':evidence.get('fact_graph'),
            'contextual_explanations':evidence.get('contextual_explanations'),
            'xai4_partial_evaluation':evidence.get('xai4_partial_evaluation'),
            'xai5_localization':evidence.get('xai5_localization'),
            'xai6_naturalization':evidence.get('xai6_naturalization'),
            'xai7_unified':evidence.get('xai7_unified'),
            'node_details':details,
            'target_comparison':{'status':'not_requested','matched':None}}

def evaluate_request(data):
    if not isinstance(data,dict) or set(data)-{'tree','target_lesson_id','variety'}:
        raise ValueError('Only tree, target_lesson_id and variety are accepted')
    tree = data.get('tree')
    if not isinstance(tree,dict): raise ValueError('A canonical tree object is required')
    variety = data.get('variety')
    if variety is not None and (not isinstance(variety,str) or not variety.strip()):raise ValueError('Invalid variety')
    # Explicit bounds before recursive validators; malformed graphs return 400.
    pending=[(tree.get('root'),0)];count=0
    while pending:
        n,depth=pending.pop();count+=1
        if count>500 or depth>80: raise ValueError('Tree exceeds 500 nodes or depth 80')
        if isinstance(n,dict) and isinstance(n.get('children'),list):pending.extend((c,depth+1) for c in n['children'])
    if len(json.dumps(tree))>240000:raise ValueError('Tree exceeds supported size')
    result = evaluate_analysis({'status':'normalized','tree':tree},variety=variety)
    target_id = data.get('target_lesson_id')
    if target_id is not None:
        if not isinstance(target_id,str):raise ValueError('Invalid exercise ID')
        course=json.loads((ROOT/'web/content/lessons/course.json').read_text())
        lesson=next((l for l in course['lessons'] if l['lesson_id']==target_id and l.get('review_status')=='INDEPENDENTLY_REVIEWED'),None)
        target=lesson.get('worked_example',{}).get('tree') if lesson else None
        if not target:raise ValueError('Unknown reviewed tree exercise')
        result['target_comparison'] = compare_target(tree,target) if result['structure']['valid'] else {'status':'not_evaluated','matched':None}
    return result
