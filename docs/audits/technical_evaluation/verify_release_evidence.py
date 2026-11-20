"""Verify release evidence without loading NLP models. No human quality claims."""
import csv, hashlib, json, subprocess
from pathlib import Path
from verify_metrics import recompute
from run_technical_evaluation import _extract_spans, aggregate_parseval
D=Path(__file__).resolve().parent

def read(name):
    return list(csv.DictReader((D/name).open(encoding='utf-8')))

def compare(rows, expected):
    for mode, ops in expected.items():
        for op, want in ops.items():
            got=recompute(rows,'rules_verdict' if mode=='rules_only' else 'hybrid_verdict',op)
            for key,value in got.items():
                assert value == want[key], (mode,op,key,value,want[key])

def main():
    dev,ho,frozen=read('RAW_PREDICTIONS.csv'),read('HOLDOUT_PREDICTIONS.csv'),read('FROZEN_UNTOUCHED_HOLDOUT.csv')
    comp=json.loads((D/'_computed_results.json').read_text())
    hcomp=json.loads((D/'_holdout_results.json').read_text())
    assert len(dev)==476 and len(ho)==len(frozen)==320
    assert len({r['item_id'] for r in dev})==len(dev)
    assert len({r['item_id'] for r in ho})==len(ho)
    assert all(all(a[k]==b[k] for k in a) for a,b in zip(frozen,ho))
    assert all(r['execution_status']=='ok' and r['cola_label'] for r in dev+ho)
    assert not ({r['sentence'].strip().casefold() for r in dev}&{r['sentence'].strip().casefold() for r in ho})
    assert hashlib.sha256((D/'FROZEN_UNTOUCHED_HOLDOUT.csv').read_bytes()).hexdigest()==hcomp['holdout_sha256']
    for name,want in comp['section_511']['overall'].items():
        if name=='external_all_400': rows=[r for r in dev if r['dataset'] in {'blimp_stratified','jfleg_stratified','cola_stratified'}]
        elif name=='external_strict_uncontaminated_320': rows=[r for r in dev if r['dataset'] in {'blimp_stratified','jfleg_stratified'}]
        else: rows=[r for r in dev if r['dataset']==name]
        compare(rows,want)
    for name,want in hcomp['overall'].items():
        rows=ho if name=='holdout_all_320' else [r for r in ho if r['dataset']==('holdout_blimp' if 'blimp' in name else 'holdout_jfleg')]
        compare(rows,want)
    tree=comp['section_512']; cases=tree['book_case_records']
    for c in cases:
        assert c['has_multiword_triangle']==bool(_extract_spans(c['reference_tree'])[2])
    fixed=[c for c in cases if not c['has_multiword_triangle']]
    assert aggregate_parseval(fixed)==tree['book_final_d1_bypass_nontriangle_subset']
    x=comp['section_513']; rows=[r for r in x['case_records'] if r['execution_status']=='ok']; summary=x['summary']
    assert len(rows)==summary['n_ok']
    for flag,total in [('verdict_consistent','verdict_evidence_consistent'),('display_gating_ok','display_status_truth_gating_ok'),('learner_prose_count','total_node_explanations_generated'),('learner_prose_nonempty','total_node_explanations_nonempty')]:
        assert sum(r[flag] for r in rows)==summary[total]
    assert sum(r['has_correction'] for r in rows)==summary['corrections_generated']
    root=D.parents[2]
    changed=subprocess.check_output(['git','diff','--name-only','5f582552504fb2d584fa02f4dfa55f1a704e3be1','HEAD','--','server','grammar','web','benchmarks','evaluation'],cwd=root,text=True)
    assert not changed, 'Production or reference files changed: '+changed
    manifest={'evaluation_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'production_base_commit':'5f582552504fb2d584fa02f4dfa55f1a704e3be1','production_reference_files_unchanged':True,'verified_development_records':len(dev),'verified_additional_validation_records':len(ho),'reference_nontriangle_count':len(fixed),'sample_history':'Both supplied samples were already examined before this source-reproduction run. Historical untouched status is not certified.','jfleg_label_policy':'Source-versus-correction proxy labels; not independently adjudicated binary grammaticality.','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.glob('*')) if p.suffix in {'.csv','.json','.py'} and p.name!='EVIDENCE_MANIFEST.json'}}
    (D/'EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('RELEASE EVIDENCE VERIFIED',json.dumps({k:v for k,v in manifest.items() if k!='files'}))
if __name__=='__main__':main()
