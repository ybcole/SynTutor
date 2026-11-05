#!/usr/bin/env python3
"""Book-answer validator for SynTutor Chapter 8 (V8)."""
import argparse, json, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ALLOWED={
 'S','S-bar','NP','VP','AP','AdvP','PP','V','MOD','PERF','PROG','PASS','TENSE','C',
 'P','A','Adv','N','NOM','DET','ART','DEM','Q','POSS','PRE-DET','PartP','V-part','pronoun','name'
}

def children(n):
    if n.get('triangle') or 'word' in n or n.get('gap'): return []
    return n.get('children',[])
def leaves(n):
    if n.get('gap') or n.get('elided'): return []
    if 'word' in n: return [n['word']]
    if n.get('triangle'): return list(n.get('words',[]))
    return [w for c in n.get('children',[]) for w in leaves(c)]
def walk(n,parent=None):
    yield n,parent
    for c in children(n): yield from walk(c,n)
def norm_words(ws): return [str(w).replace('’',"'").replace('‘',"'").lower().strip() for w in ws]
def sentence_tokens(sentence,tree):
    s=sentence.replace('’',"'").replace('‘',"'")
    lw=norm_words(leaves(tree))
    if "'m" in lw: s=re.sub(r"\bI'm\b","I 'm",s,flags=re.I)
    toks=re.findall(r"'[A-Za-z0-9]+|[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[^\w\s]",s)
    return [x.lower() for x in toks if re.search(r'[A-Za-z0-9]',x)]
def direct_clause_words(n,root=True):
    if not root and n.get('label')=='S' and n.get('index') is not None: return []
    if n.get('elided') or n.get('gap'): return []
    if 'word' in n: return [n['word'].lower()]
    if n.get('triangle'): return [str(w).lower() for w in n.get('words',[])]
    out=[]
    for c in n.get('children',[]): out.extend(direct_clause_words(c,False))
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',default=str(HERE/'ch08.trees.json')); args=ap.parse_args()
    d=json.loads(Path(args.data).read_text(encoding='utf-8'))
    checks=[]; failures=[]
    def check(label,ok):
        checks.append(label)
        if not ok: failures.append(label)
    check('chapter and convention version',d.get('chapter')==8 and d.get('convention_version')=='V8')
    trees=d.get('trees',[]); ids=[t['id'] for t in trees]; byid={t['id']:t for t in trees}
    check('unique tree ids',len(ids)==len(set(ids)))
    check('33 tree records present',len(trees)==33)
    for t in trees:
        ident=t['id']; tr=t['tree']
        check(f'{ident}: leaves equal sentence',norm_words(leaves(tr))==sentence_tokens(t['sentence'],tr))
        labs={n.get('label') for n,_ in walk(tr) if n.get('label')}
        check(f'{ident}: V8 label inventory',labs<=ALLOWED)
        check(f'{ident}: source status valid',t.get('status') in {'IMG','IMG_ANOMALY','TXT','DERIVED_FROM_INSTRUCTIONS','UNSURE'})
        for n,p in walk(tr):
            if n.get('triangle'):
                check(f'{ident}: triangle is labelled leaf',bool(n.get('label')) and bool(n.get('words')) and not n.get('children'))
            if n.get('label')=='S-bar' and not n.get('triangle'):
                check(f'{ident}: S-bar immediately dominates C and S',[c.get('label') for c in n.get('children',[])]==['C','S'])
            if n.get('label')=='C':
                check(f'{ident}: C has one complementiser terminal',len(n.get('children',[]))==1 and ('word' in n['children'][0]))
            if n.get('label')=='PP':
                cs=n.get('children',[])
                if len(cs)==2 and cs[0].get('label')=='P':
                    pwords=norm_words(leaves(cs[0])); comp=cs[1]
                    if pwords and pwords[0] in {'after','until','before','since'}:
                        check(f'{ident}: temporal {pwords[0]} takes S directly, not S-bar',comp.get('label')=='S')
                    if pwords and pwords[0] in {'about','of'} and comp.get('label')=='S-bar':
                        cnode=comp.get('children',[{}])[0]
                        check(f'{ident}: P + S-bar has interrogative C',cnode.get('label')=='C' and norm_words(leaves(cnode))==['whether'])
        if t.get('aca'):
            aca=t['aca']; cls=aca.get('clauses',[])
            indexed=[n.get('index') for n,_ in walk(tr) if n.get('label')=='S' and n.get('index') is not None]
            expected_ids=[]
            for c in cls:
                m=re.fullmatch(r'S(\d+)',c.get('id',''))
                if m: expected_ids.append(int(m.group(1)))
            check(f'{ident}: ACA clause ids are represented by indexed S nodes',sorted(indexed)==sorted(expected_ids))
            check(f'{ident}: ACA S1 is the unique main clause',sum(bool(c.get('main')) for c in cls)==1 and bool(cls) and cls[0].get('id')=='S1' and cls[0].get('main') is True)
            refs={c.get('id') for c in cls}
            check(f'{ident}: ACA subordinate references resolve',all(set(c.get('contains',[]))<=refs for c in cls))
            verbs=[c.get('lexical_verb') for c in cls]
            check(f'{ident}: one recorded lexical verb per clause',len(verbs)==len(cls) and all(isinstance(v,str) and v.strip() for v in verbs))
            check(f'{ident}: clause count equals lexical-verb count',len(cls)==len([v for v in verbs if v]))
            indexed_nodes={n.get('index'):n for n,_ in walk(tr) if n.get('label')=='S' and n.get('index') is not None}
            for clause in cls:
                try: idx=int(clause['id'][1:])
                except (KeyError,ValueError): continue
                node=indexed_nodes.get(idx,{})
                words=direct_clause_words(node)
                check(f"{ident}: {clause['id']} lexical verb appears in its own clause",clause.get('lexical_verb','').lower() in words)
    # General S-bar attachment positions verified against the printed trees.
    checks_by_id={
      'ch8-23':('NP','S-bar'), 'ch8-36':('NP','S-bar'),
      'ch8-47':('AP','S-bar'), 'ch8-54':('NOM','S-bar'),
      'ch8-61':('PP','S-bar'), 'ch8-71':('VP','S-bar')
    }
    for ident,(parent_label,child_label) in checks_by_id.items():
        ok=False
        for n,p in walk(byid[ident]['tree']):
            if n.get('label')==child_label and p is not None and p.get('label')==parent_label:
                if ident in {'ch8-23','ch8-36'}: ok=(p.get('label')=='NP' and n in p.get('children',[]))
                elif ident=='ch8-47': ok=[c.get('label') for c in p.get('children',[])]==['A','S-bar']
                elif ident=='ch8-54': ok=[c.get('label') for c in p.get('children',[])]==['N','S-bar']
                elif ident=='ch8-61': ok=[c.get('label') for c in p.get('children',[])]==['P','S-bar']
                elif ident=='ch8-71': ok=[c.get('label') for c in p.get('children',[])]==['VP','S-bar']
                if ok: break
        check(f'{ident}: book-specific S-bar position ({parent_label})',ok)
    # [24] is the explicit extraposed-subject pattern; [23] is the non-extraposed subject pattern.
    t24=byid['ch8-24']['tree'];
    check('Ch8 [24]: expletive NP and extraposed S-bar are daughters of main S',
          t24.get('label')=='S' and any(c.get('label')=='NP' for c in t24.get('children',[])) and any(c.get('label')=='S-bar' for c in t24.get('children',[])))
    t23=byid['ch8-23']['tree']
    check('Ch8 [23]: clausal subject is inside NP',any(n.get('label')=='NP' and any(c.get('label')=='S-bar' for c in n.get('children',[])) for n,_ in walk(t23)))
    # Initial [1b] is the pre-generalisation bare-S analysis; every later subordinate-clause structure uses S-bar/C.
    check('Ch8 [1b]: initial bare S2 retained as printed',any(n.get('label')=='S' for n,p in walk(byid['ch8-1b']['tree']) if p is not None))
    # ACA answer mappings resolve.
    resolved=True
    def visit(x):
        nonlocal resolved
        if isinstance(x,dict):
            if 'tree_ids' in x: resolved &= all(i in byid for i in x['tree_ids'])
            for v in x.values(): visit(v)
        elif isinstance(x,list):
            for v in x: visit(v)
    visit(d.get('discussion_answers',[])); visit(d.get('exercise_answers_from_book',{}))
    check('all discussion/exercise answer ids resolve',resolved)
    check('all 13 ACA examples/answers represented',sum(bool(t.get('aca')) for t in trees)==13)
    print(f"Chapter 8 validator: {len(checks)-len(failures)}/{len(checks)} checks passed; {len(trees)} trees; {sum(bool(t.get('aca')) for t in trees)} ACA records.")
    if failures:
        for f in failures: print('FAIL:',f)
        return 1
    print('ALL OK'); return 0
if __name__=='__main__': sys.exit(main())
