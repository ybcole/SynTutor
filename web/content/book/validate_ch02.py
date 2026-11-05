import json
d=json.load(open('ch02.trees.json')); T={t['id']:t for t in d['trees']}; ok=True
def leaves(n):
    if 'word' in n: return [n['word']]
    if n.get('triangle'): return list(n['words'])
    return [x for c in n['children'] for x in leaves(c)]
def check(name,cond):
    global ok; print(('OK   ' if cond else 'FAIL ')+name); ok&=bool(cond)
def sisters(n):
    out=[]
    def w(x):
        if 'word' in x or x.get('triangle'): return
        ch=x['children']
        if len(ch)==2: out.append((' '.join(leaves(ch[0])),' '.join(leaves(ch[1]))))
        for c in ch: w(c)
    w(n); return out
def sister_of(tree,words):
    for a,b in sisters(tree):
        if a==words: return b
        if b==words: return a
# leaves match sentences
for t in d['trees']:
    s=t.get('sentence')
    if s: check('leaves '+t['id'], [x.lower() for x in leaves(t['tree'])]==s.lower().split())
# S -> NP VP, subject = NP immediately dominated by S (book p.31)
for i,subj,pred in (('ch2-33','Those gigantic ducks','were paddling away furiously'),('ch2-34','The pianist','has rejected the chiropodist')):
    r=T[i]['tree']; np=[c for c in r['children'] if c['label']=='NP'][0]; vp=[c for c in r['children'] if c['label']=='VP'][0]
    check(f'{i} subject=NP under S',' '.join(leaves(np))==subj); check(f'{i} predicate=VP under S',' '.join(leaves(vp))==pred)
# book text counts of sister relations
check('[36] has 3 sister relations (p.32)',len(sisters(T['ch2-36']['tree']))==3)
check('[43] has 2 sister relations (p.35)',len(sisters(T['ch2-43']['tree']))==2)
# [36]: rather's sister is dubious; PHRASE-c sister is jokes; their sister is "rather dubious jokes" (p.32)
t=T['ch2-36']['tree']
check('[36] rather~dubious',sister_of(t,'rather')=='dubious')
check('[36] rather dubious~jokes',sister_of(t,'rather dubious')=='jokes')
check('[36] their~rather dubious jokes',sister_of(t,'their')=='rather dubious jokes')
# [38] their+rather sisters (p.34); [39] rather's sister is "dubious jokes" (p.34)
check('[38] their~rather are sisters',sister_of(T['ch2-38']['tree'],'their')=='rather')
check('[39] rather~dubious jokes',sister_of(T['ch2-39']['tree'],'rather')=='dubious jokes')
check('[42] dubious jokes is a phrase',sister_of(T['ch2-42']['tree'],'their')=='dubious jokes')
# Ex3 (p.41): more modifies 'exciting ideas' in (a), 'exciting' in (b)
check('Ex3a more~exciting ideas',sister_of(T['ch2-ex3a']['tree'],'more')=='exciting ideas')
check('Ex3b more~exciting',sister_of(T['ch2-ex3b']['tree'],'more')=='exciting')
# Ex4 (p.41)
check('Ex4a young~car salesmen',sister_of(T['ch2-ex4a']['tree'],'young')=='car salesmen')
check('Ex4b second-hand~car',sister_of(T['ch2-ex4b']['tree'],'second-hand')=='car')
# Ex5 (p.42)
a,b,c3=T['ch2-ex5a']['tree'],T['ch2-ex5b']['tree'],T['ch2-ex5c']['tree']
check('Ex5a Romanian~history teacher',sister_of(a,'Romanian')=='history teacher')
check('Ex5b Romanian~history',sister_of(b,'Romanian')=='history')
check('Ex5b old~Romanian history',sister_of(b,'old')=='Romanian history')
check('Ex5c Romanian history is a phrase and old~Romanian history teacher',sister_of(c3,'Romanian')=='history' and sister_of(c3,'old')=='Romanian history teacher')
x=T['ch2-ex5-3']['tree']; check('Ex5(3) Old Romanian and history teacher are phrases',('Old Romanian','history teacher') in sisters(x))
# distinct shapes for the 4 Further Ex2 markers
shapes=[json.dumps(T[i]['tree'],sort_keys=True) for i in ('ch2-fex2a','ch2-fex2b','ch2-fex2c','ch2-fex2d')]
check('Further Ex2 four markers all different',len(set(shapes))==4)
print('ALL OK' if ok else 'PROBLEMS')
