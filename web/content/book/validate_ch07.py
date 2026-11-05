#!/usr/bin/env python3
"""Book-answer validator for SynTutor Chapter 7 (V7)."""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {
    'S','VP','NP','DET','NOM','ART','DEM','Q','POSS','PRE-DET',
    'N','A','AP','DEG','QA','P','PP','PartP','V-part','Adv','AdvP',
    'pronoun','name','V'
}
STATUSES = {'IMG','IMG_ANOMALY','TXT','DERIVED_FROM_INSTRUCTIONS','UNSURE'}

def children(n):
    if n.get('triangle') or 'word' in n or n.get('gap'):
        return []
    return n.get('children', [])

def leaves(n):
    if n.get('gap') or n.get('elided'):
        return []
    if 'word' in n:
        return [n['word']]
    if n.get('triangle'):
        return list(n.get('words', []))
    return [w for c in n.get('children', []) for w in leaves(c)]

def walk(n, parent=None):
    yield n, parent
    for c in children(n):
        yield from walk(c, n)

def norm_words(words):
    return [str(w).replace('’', "'").replace('‘', "'").lower().strip() for w in words]

def sentence_tokens(sentence, tree):
    s = sentence.replace('’', "'").replace('‘', "'")
    lw = norm_words(leaves(tree))
    # In V7 genitive determiners, the book prints NP + a separate -'s terminal.
    if "'s" in lw:
        s = re.sub(r"\b([A-Za-z]+)'s\b", r"\1 's", s)
    # The book's [82] analysis splits I'm into the subject pronoun and the copula.
    if "'m" in lw:
        s = re.sub(r"\bI'm\b", "I 'm", s, flags=re.I)
    toks = re.findall(r"'[A-Za-z0-9]+|[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[^\w\s]", s)
    return [x.lower() for x in toks if re.search(r'[A-Za-z0-9]', x)]

def outer_np_nom_count(tree):
    def visit(n, root=False):
        if n.get('label') == 'NP' and not root:
            return 0
        count = 1 if n.get('label') == 'NOM' else 0
        if not n.get('triangle') and 'word' not in n and not n.get('gap'):
            count += sum(visit(c, False) for c in n.get('children', []))
        return count
    return visit(tree, True)

def spans(tree):
    out, pos = [], [0]
    def rec(n):
        start = pos[0]
        if n.get('gap') or n.get('elided'):
            pass
        elif 'word' in n:
            pos[0] += 1
        elif n.get('triangle'):
            pos[0] += len(n.get('words', []))
        else:
            for c in n.get('children', []): rec(c)
        if 'label' in n:
            out.append((n['label'], start, pos[0]))
    rec(tree)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=str(HERE/'ch07.trees.json'))
    args = ap.parse_args()
    d = json.loads(Path(args.data).read_text(encoding='utf-8'))
    checks, failures = [], []
    def check(label, ok):
        checks.append(label)
        if not ok: failures.append(label)
    check('chapter and convention version', d.get('chapter') == 7 and d.get('convention_version') == 'V7')
    trees = d.get('trees', [])
    ids = [t['id'] for t in trees]
    check('unique tree ids', len(ids) == len(set(ids)))
    check('62 tree records present', len(trees) == 62)
    for t in trees:
        ident = t['id']; tr = t['tree']
        check(f'{ident}: source status valid', t.get('status') in STATUSES)
        check(f'{ident}: appendix_nom boolean', isinstance(t.get('appendix_nom'), bool))
        check(f'{ident}: leaves equal sentence', norm_words(leaves(tr)) == sentence_tokens(t['sentence'], tr))
        labs = {n.get('label') for n,_ in walk(tr) if n.get('label')}
        check(f'{ident}: V7 label inventory', labs <= ALLOWED)
        # Every triangle must have a category, a word span, and no branching children.
        for n,p in walk(tr):
            if n.get('triangle'):
                check(f'{ident}: triangle is a labelled leaf', bool(n.get('label')) and isinstance(n.get('words'), list) and len(n.get('words')) > 0 and not n.get('children'))
            if n.get('gap'):
                check(f'{ident}: gap is not also a terminal', 'word' not in n)
            if n.get('label') == 'NP' and not n.get('triangle'):
                labs_ch = [c.get('label') for c in n.get('children', [])]
                pronoun_name = (len(labs_ch) == 1 and labs_ch[0] in {'pronoun','name'})
                predet_np = (labs_ch == ['PRE-DET','NP'])
                regular = (labs_ch == ['DET','NOM'])
                modified_pronoun = (len(labs_ch) == 2 and labs_ch[0] == 'pronoun' and labs_ch[1] in {'AP','PP'})
                check(f'{ident}: NP expansion ({"/".join(labs_ch)})', pronoun_name or predet_np or regular or modified_pronoun)
            if n.get('label') == 'DET' and not n.get('triangle') and not n.get('children'):
                parent_is_np = p is not None and p.get('label') == 'NP'
                sibling_nom = p is not None and len(p.get('children',[])) == 2 and p['children'][1].get('label') == 'NOM'
                head_words = norm_words(leaves(p['children'][1])) if sibling_nom else []
                allowed_empty = bool(set(head_words) & {
                    'essays','smoke','men','mistake','mistakes','trampolines','address',
                    'curries','experts','syntax','quotations','contributions','charity',
                    'maths','one','observations','scientists','engineers','alchemy'
                }) or 'E' in head_words
                check(f'{ident}: empty DET only for book-licensed NP', parent_is_np and sibling_nom and allowed_empty)
            if n.get('label') == 'PRE-DET':
                check(f'{ident}: PRE-DET is NP sister of an NP', p is not None and p.get('label') == 'NP' and len(p.get('children',[])) == 2 and p['children'][1].get('label') == 'NP')
            if n.get('label') == 'QA':
                check(f'{ident}: QA is inside AP or printed anomaly', (p is not None and p.get('label') == 'AP') or (ident == 'ch7-disc5-38' and p is not None and p.get('label') == 'NOM'))
        if t.get('accepted_alternatives'):
            for alt in t['accepted_alternatives']:
                check(f'{ident}: alternative {alt.get("label")} leaves match', norm_words(leaves(alt['tree'])) == sentence_tokens(t['sentence'], alt['tree']))
    # Recursive-NOM counts explicitly visible in the book's worked examples.
    byid = {t['id']:t for t in trees}
    nom_counts = {
        'ch7-36':2, 'ch7-42':2, 'ch7-disc5-37':3, 'ch7-disc5-38':3,
        'ch7-58':3, 'ch7-disc7':3, 'ch7-app-11':2
    }
    for ident,want in nom_counts.items():
        got=outer_np_nom_count(byid[ident]['tree'])
        check(f'{ident}: NOM recursion count {want}',got==want)
    # Quantifying adjective order: QA-headed AP is the first NOM premodifier.
    for ident in ('ch7-25','ch7-26','ch7-disc5-38','ch7-ex1-c-i'):
        nom_nodes=[n for n,_ in walk(byid[ident]['tree']) if n.get('label')=='NOM']
        first=nom_nodes[0]
        kids=first.get('children',[])
        has_qa=any(k.get('label')=='QA' or (k.get('label')=='AP' and any(c.get('label')=='QA' for c in k.get('children',[]))) for k in kids)
        check(f'{ident}: quantifier precedes other modifiers', bool(kids) and (has_qa or ident=='ch7-disc5-38'))
    # Friendly Head Principle, visible in the printed chef/AP tree.
    ap67=next(n for n,_ in walk(byid['ch7-67']['tree']) if n.get('label')=='AP')
    check('Ch7 [67]: complement-bearing AP has A next to its PP complement', [c.get('label') for c in ap67.get('children',[])]==['A','PP'])
    par67=next(p for n,p in walk(byid['ch7-67']['tree']) if n is ap67)
    check('Ch7 [67]: complement-bearing AP post-modifies the head N', par67.get('label')=='NOM' and [c.get('label') for c in par67.get('children',[])]==['N','AP'])
    # The book explicitly denies the constituent [pub for more cherry brandy].
    s=norm_words(leaves(byid['ch7-42']['tree']))
    target=['pub','for','more','cherry','brandy']
    start=s.index('pub')
    no_pub_for_const=not any(a==start and b==start+len(target) for _,a,b in spans(byid['ch7-42']['tree']))
    check('Ch7 [42]: pub for more cherry brandy is not a constituent',no_pub_for_const)
    # Book's explicit A/B decisions, plus genuinely accepted alternatives.
    expected={'ch7-47':'A','ch7-48':'B','ch7-49':'B','ch7-50':'A','ch7-51':'A','ch7-52':'B'}
    for ident,choice in expected.items():
        check(f'{ident}: printed A/B verdict',byid[ident].get('analysis')==choice)
    for ident,choice in expected.items():
        root_nom=byid[ident]['tree']['children'][1]
        wanted=['NOM','PP'] if choice=='A' else ['AP','NOM']
        check(f'{ident}: tree matches A/B configuration {choice}',[c.get('label') for c in root_nom.get('children',[])]==wanted)
    for ident in ('ch7-55-A/B','ch7-56-A/B','ch7-57-A/B'):
        alts={a['label'] for a in byid[ident].get('accepted_alternatives',[])}
        check(f'{ident}: both accepted analyses retained',alts=={'A','B'})
    # Ch7 Appendix flags and figure references.
    app_ids={t['id'] for t in trees if t['id'].startswith('ch7-app-')}
    check('Appendix D1 trees included',{'ch7-app-11','ch7-app-16','ch7-app-17','ch7-app-18','ch7-app-19b','ch7-app-20b'}<=app_ids)
    check('core [4] remains Appendix NOM false',byid['ch7-4'].get('appendix_nom') is False)
    check('Appendix [11] has Appendix NOM true',byid['ch7-app-11'].get('appendix_nom') is True)
    app20=byid['ch7-app-20b']['tree']
    app20_noms=[n for n,_ in walk(app20) if n.get('label')=='NOM']
    check('Appendix [20b]: pro-NOM one is directly dominated by NOM',any(any(c.get('word')=='one' for c in n.get('children',[])) for n in app20_noms))
    # Discussion and exercise answer pointers all resolve.
    resolved=True
    for sec in ('discussion_answers','exercise_answers_from_book'):
        def visit(x):
            nonlocal resolved
            if isinstance(x,dict):
                if 'tree_ids' in x:
                    resolved &= all(i in byid for i in x['tree_ids'])
                for v in x.values(): visit(v)
            elif isinstance(x,list):
                for v in x: visit(v)
        visit(d.get(sec,{}))
    check('all discussion/exercise answer ids resolve',resolved)
    # Node fragments are structurally present and V7-labelled.
    for f in d.get('node_fragments',[]):
        check(f"{f['id']}: fragment has a labelled node",bool(f.get('node',{}).get('label')))
        check(f"{f['id']}: fragment uses V7 labels",{n.get('label') for n,_ in walk(f['node']) if n.get('label')}<=ALLOWED)
    print(f"Chapter 7 validator: {len(checks)-len(failures)}/{len(checks)} checks passed; {len(trees)} trees; {len(d.get('node_fragments',[]))} node fragments.")
    if failures:
        for f in failures: print('FAIL:',f)
        return 1
    print('ALL OK')
    return 0

if __name__=='__main__': sys.exit(main())
