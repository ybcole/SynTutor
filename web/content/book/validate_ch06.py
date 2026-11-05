import json
d=json.load(open('ch06.trees.json')); T={t['id']:t for t in d['trees']}; ok=True
AUX={'MOD','PERF','PROG','PASS','TENSE'}; VERBY=AUX|{'V'}
RANK={'TENSE':0,'MOD':0,'PERF':1,'PROG':2,'PASS':3,'V':4}   # MOD < PERF < PROG < PASS < V (book p.120); TENSE (do) stands alone
ADJ={'AdvP','PP','NP','S-bar'}                               # adjunct adverbials (book Ch5)
ALLOWED={'S','S-bar','NP','VP','AP','AdvP','PP','V','MOD','PERF','PROG','PASS','TENSE','C'}   # V6 label set; no NOM/DET/S-dbar/C1/C2 yet
TRI_OK={'NP','AP','AdvP','PP'}
def check(name,c):
    global ok; print(('OK   ' if c else 'FAIL ')+name); ok&=bool(c)
def kids(n): return [] if n.get('triangle') or 'word' in n or n.get('gap') else n.get('children',[])
def leaves(n):
    if n.get('gap') or n.get('elided'): return []
    if 'word' in n: return [n['word']]
    if n.get('triangle'): return list(n['words'])
    return [w for c in n['children'] for w in leaves(c)]
def text(n): return ' '.join(leaves(n))
def nodes(n,parent=None):
    yield n,parent
    for c in kids(n): yield from nodes(c,n)
def spans(n):
    out=[];pos=[0]
    def w(x):
        s=pos[0]
        if x.get('gap'): out.append(('gap',s,s)); return
        if 'word' in x: pos[0]+=1
        elif x.get('triangle'): pos[0]+=len(x['words'])
        else:
            for c in x['children']: w(c)
        out.append((x.get('label'),s,pos[0]))
    w(n); return out
def is_const(tree,words,label=None):
    L=[x.lower() for x in leaves(tree)]; ws=words.lower().split()
    for i in range(len(L)-len(ws)+1):
        if L[i:i+len(ws)]==ws and any(a==i and b==i+len(ws) and (label is None or l==label) for l,a,b in spans(tree)): return True
    return False
def verbs(tree): return [n for n,_ in nodes(tree) if n.get('label') in VERBY]       # pre-order = left-to-right
def tense(n): return [f for f in n.get('features',[]) if f in('pres','past')]
SUB={'intrans':[()],'trans':[('NP',)],'ditrans':[('NP','NP'),('NP','PP')],'intens':[('AP',),('NP',),('PP',)],
     'complex':[('NP','AP'),('NP','NP'),('NP','PP')],'prep':[('PP',)]}

for t in d['trees']:
    tr=t['tree']; i=t['id']
    # 1. leaves = sentence
    check(f'leaves {i}',[x.lower() for x in leaves(tr)]==t['sentence'].lower().split())
    # 2. V6 label set; triangles only where the book uses them
    labs={n.get('label') for n,_ in nodes(tr) if 'label' in n}
    check(f'{i} only V6 labels',labs<=ALLOWED)
    bad=[n['label'] for n,_ in nodes(tr) if n.get('triangle') and not (n['label'] in TRI_OK or (n['label'] in('MOD','TENSE') and any(w in('not',"n't") for w in n['words'])) or (n['label']=='VP' and i=='ch6-69'))]
    check(f'{i} triangles only on NP/AP/AdvP/PP (+ negated aux, + VP in [69])',not bad)
    # 3. exactly one tensed verb, and it is the first verb in the sentence (p.113)
    V=verbs(tr); tv=[n for n in V if tense(n)]
    check(f'{i} exactly one tensed verb, and it is the first verb',len(tv)==1 and V[0] is tv[0])
    # 4. fixed auxiliary order MOD < PERF < PROG < PASS < V (p.120-121)
    r=[RANK[n['label']] for n in V]
    check(f'{i} verb order MOD<PERF<PROG<PASS<V ({" ".join(n["label"] for n in V)})',r==sorted(r) and len({n['label'] for n in V if n['label'] in AUX})==len([n for n in V if n['label'] in AUX]))
    # 5. every auxiliary heads a VP and takes exactly one VP complement (p.121-122)
    for n,p in nodes(tr):
        if n.get('label') in AUX:
            check(f'{i} {n["label"]} = head of a VP with a VP complement',p is not None and p['label']=='VP' and [c.get('label') for c in p['children']]==[n['label'],'VP'])
    # 6. VP shapes: [AUX VP] | [VP adjunct] | [adjunct VP] | [VP and VP] | [V complements...] with complements matching the V feature (Ch4/Ch5)
    for n,_ in nodes(tr):
        if n.get('label')!='VP' or n.get('triangle'): continue
        ch=n['children']; L=[c.get('label') or c.get('word') for c in ch]
        if L[0] in AUX or L==['VP','and','VP']: good=True
        elif len(ch)==2 and 'VP' in L and (set(L)-{'VP'})<=ADJ: good=True
        elif L[0]=='V':
            f=[x for x in ch[0].get('features',[]) if x in SUB]; comp=tuple(L[1:])
            good=len(f)==1 and comp in SUB[f[0]]
        else: good=False
        check(f'{i} VP shape {L}',good)
    # 7. gaps: one for each movement (passive object; fronted aux/verb); gap sits where the book puts it
    gaps=[(n,p) for n,p in nodes(tr) if n.get('gap')]
    passive=any(n.get('label')=='PASS' for n in V); question=tr['label']=='S-bar'
    nV=len([n for n in V if n['label']=='V'])
    check(f'{i} number of gaps = one object gap per lexical V if passive + one if question',len(gaps)==(nV if passive else 0)+int(question))
    if question:
        S=tr['children']
        check(f'{i} S-bar = C + S; C holds the fronted tensed auxiliary',[c['label'] for c in S]==['C','S'] and len(leaves(S[0]))==1 and leaves(S[0])[0].lower()==t['sentence'].split()[0].lower())
        check(f'{i} aux gap sits under the tensed verb node',any(p is tv[0] for _,p in gaps))
    else: check(f'{i} no aux gap in a declarative',not any(p in V for _,p in gaps))
    if passive:
        og=[p for _,p in gaps if p.get('label')=='NP']
        vv=[n for n in V if n['label']=='V'][0]
        check(f'{i} passive: [trans]/[ditrans]/[complex] verb',bool(set(vv['features'])&{'trans','ditrans','complex'}))
        check(f'{i} passive: object gap is a sister of V',len(og)>=1)
    # 8. negation / do-support
    if any(w.lower() in('not',) for w in leaves(tr)) :
        check(f'{i} negation attached to the tensed auxiliary',any(n.get('triangle') and 'not' in n['words'] for n in tv))
    if any(n['label']=='TENSE' for n in V):
        vv=[n for n in V if n['label']=='V'][0]
        check(f'{i} do-support: lexical V is untensed',not tense(vv))

# ---- the book's own arguments, checked against the trees ----
# Auxiliary + VP complement; lexical VP survives (do so / ellipsis, p.121-122)
t=T['ch6-52']['tree']; check('[52] "studying the menu" and "is studying the menu" are VPs; "is studying" is not',is_const(t,'studying the menu','VP') and is_const(t,'is studying the menu','VP') and not is_const(t,'is studying'))
t=T['ch6-53b']['tree']; check('[53b] ellipsis targets: "written an essay" and "have written an essay" are VPs; "should have" is not',is_const(t,'written an essay','VP') and is_const(t,'have written an essay','VP') and not is_const(t,'should have'))
t=T['ch6-d2']['tree']; check('Disc2 three nested VPs below MOD: "have been writing that essay", "been writing that essay", "writing that essay"',all(is_const(t,w,'VP') for w in('have been writing that essay','been writing that essay','writing that essay')))
# Disc1 has exactly the same shape as [52] with PERF for PROG (p.122: "obvious what [50a] must be")
def skel(n):
    if 'word' in n or n.get('gap'): return '_'
    lab='AUX' if n.get('label') in AUX else n.get('label')
    return (lab,tuple(skel(c) for c in kids(n))) if not n.get('triangle') else (lab,'tri')
check('Disc1 [PERF] has the same shape as [52] [PROG]',skel(T['ch6-d1']['tree'])==skel(T['ch6-52']['tree']))
# Assumption 1 (p.123): preceding adverbial modifies the following VP
t=T['ch6-62']['tree']; check('[62] "easily have killed me" is a VP (adverbial + PERF VP); "could easily" is not a constituent',is_const(t,'easily have killed me','VP') and not is_const(t,'could easily'))
t=T['ch6-d3']['tree']; check('Disc3 "quietly reading Simon a story" is a VP',is_const(t,'quietly reading Simon a story','VP'))
# Assumption 2 (p.124): final adverbial modifies the lexical VP
t=T['ch6-66']['tree']; check('[66] "complaining for the fun of it" and "been complaining for the fun of it" are VPs; "been complaining" is not',is_const(t,'complaining for the fun of it','VP') and is_const(t,'been complaining for the fun of it','VP') and not is_const(t,'been complaining'))
# time-adverbial exception (p.124-125): [69] last week modifies the PROG VP; next week the lexical VP
t=T['ch6-69']['tree']; top=t['children'][1]
check('[69] "going to India next week" is a VP; "were going to India next week" is a VP; "were going to India" is NOT a constituent (predicts *last week next week)',is_const(t,'going to India next week','VP') and is_const(t,'were going to India next week','VP') and not is_const(t,'were going to India'))
check('[69] "last week" is the sister of the PROG VP inside a higher VP',top['label']=='VP' and [c['label'] for c in top['children']]==['VP','PP'] and text(top['children'][0])=='were going to India next week' and text(top['children'][1])=='last week')
t=T['ch6-ex1-2']['tree']; top=t['children'][1]
check('Ex1(2) "by tonight" modifies the whole MOD VP "will have filled the pool"',[c['label'] for c in top['children']]==['VP','PP'] and text(top['children'][0])=='will have filled the pool')
t=T['ch6-ex1-3']['tree']; top=t['children'][1]
check('Ex1(3) "now" modifies the PERF VP; "for five hours" modifies the lexical VP "been on court"',text(top['children'][0])=='has been on court for five hours' and text(top['children'][1])=='now' and is_const(t,'been on court for five hours','VP') and is_const(t,'been on court','VP'))
t=T['ch6-ex3a']['tree']; top=t['children'][1]; check('Ex3(a) time NP "this morning" modifies the PROG VP',text(top['children'][0])=='were having a really tedious conversation' and text(top['children'][1])=='this morning')
# passive (p.126-128): by-phrase = adjunct of the lexical VP; object -> subject leaves a gap; [complex] keeps oP; ditransitive: FIRST object promoted
t=T['ch6-78']['tree']; check('[78] "fired by the boss" is a VP (adjunct on lexical VP); "fired" + object gap = VP',is_const(t,'fired by the boss','VP') and is_const(t,'fired','VP'))
t=T['ch6-81']['tree']; vp=[n for n,_ in nodes(t) if n.get('label')=='VP' and any(c.get('label')=='V' for c in kids(n))][0]
check('[81] [complex] passive keeps both complement slots: V + NP(gap) + AP (mad = oP, not sP)',[c.get('label') for c in vp['children']]==['V','NP','AP'] and vp['children'][1]['children'][0].get('gap'))
t=T['ch6-d4']['tree']; vp=[n for n,_ in nodes(t) if n.get('label')=='VP' and any(c.get('label')=='V' for c in kids(n))][0]
check('Disc4 ditransitive passive: the gap is the FIRST NP (iO); the direct object stays in place',[c['label'] for c in vp['children']]==['V','NP','NP'] and vp['children'][1]['children'][0].get('gap') and vp['children'][2].get('triangle'))
t=T['ch6-ex3d']['tree']; vp=[n for n,_ in nodes(t) if n.get('label')=='VP' and any(c.get('label')=='V' for c in kids(n))][0]
check('Ex3(d) [complex] passive: PP "in my pocket" is a sister of V (oP); "by you" is the adjunct',[c['label'] for c in vp['children']]==['V','NP','PP'] and is_const(t,'put in my pocket by you','VP'))
# question + passive (Disc6): two gaps
t=T['ch6-d6']['tree']; check('Disc6 two gaps: one under PERF[pres], one NP gap after the verb',sum(1 for n,_ in nodes(t) if n.get('gap'))==2)
# co-ordination (Ex3e): mother and both conjuncts have the same category
t=T['ch6-ex3e']['tree']; co=[n for n,_ in nodes(t) if n.get('label')=='VP' and [c.get('label') or c.get('word') for c in kids(n)]==['VP','and','VP']]
check('Ex3(e) PASS takes a co-ordinate VP (VP and VP); each conjunct has its own object gap',len(co)==1 and sum(1 for n,_ in nodes(co[0]) if n.get('gap'))==2 and is_const(t,'accepted and quickly published','VP'))
# S-bar rule (p.130): C = daughter of S-bar and sister of S
for i in('ch6-91','ch6-93','ch6-103','ch6-d5','ch6-d6','ch6-ex3c','ch6-ex3d'):
    r=T[i]['tree']; check(f'{i} C is daughter of S-bar and sister of S',r['label']=='S-bar' and [c['label'] for c in r['children']]==['C','S'])
# be behaves like an auxiliary (p.132): [103] lexical be fronts, gap under the V
t=T['ch6-103']['tree']; gp=[p for n,p in nodes(t) if n.get('gap')][0]; check('[103] copula be: the gap is under V[intens,past]',gp['label']=='V' and gp['features']==['intens','past'])
# node fragments
F={f['id']:f['node'] for f in d['node_fragments']}
for i,lab,tn in(('ch6-24','MOD','pres'),('ch6-25','MOD','past'),('ch6-29','PERF','pres'),('ch6-30','PERF','past'),('ch6-36','PROG','pres'),('ch6-37','PROG','past'),('ch6-41','PASS','pres'),('ch6-42','PASS','past')):
    check(f'{i} {lab}[{tn}]',F[i]['label']==lab and F[i]['features']==[tn])
check('[8]/[9] lexical V carries tense feature (not segmented)',F['ch6-8']['features']==['trans','pres'] and F['ch6-9']['features']==['trans','past'])
check('convention_version = V6 and 26 trees',d['convention_version']=='V6' and len(d['trees'])==26)
check('Ex2 has 7 book answers',len(d['exercise_answers_from_book']['ex2']['items'])==7)
print('ALL OK' if ok else 'PROBLEMS')
