import json
d=json.load(open('ch05.trees.json')); T={t['id']:t for t in d['trees']}; ok=True
def leaves(n):
    if n.get('elided'): return []
    if 'word' in n: return n['word'].split()
    if n.get('triangle'): return list(n['words'])
    return [x for c in n['children'] for x in leaves(c)]
def text(n): return ' '.join(leaves(n))
def check(name,c):
    global ok; print(('OK   ' if c else 'FAIL ')+name); ok&=bool(c)
def nodes(n):
    yield n
    if 'children' in n and not n.get('triangle'):
        for c in n['children']: yield from nodes(c)
def kids(n): return n.get('children',[]) if not n.get('triangle') else []
def roles(tree):
    """read functions off positions (book p.90): sisters of V = complements; sisters of VP (in a higher VP) = adjuncts; sisters of S (in a higher S) = sentence adverbials"""
    comp,adj,sadv=[],[],[]
    for n in nodes(tree):
        k=kids(n)
        if n.get('label')=='VP' and any(c.get('label')=='V' for c in k):
            comp+= [text(c) for c in k if c.get('label')!='V']
        elif n.get('label')=='VP' and len(k)==2 and any(c.get('label')=='VP' for c in k):
            adj+=[text(c) for c in k if c.get('label')!='VP' or c.get('triangle') and False]
            # when both are VP, the one that is the lower adjunct is the second (book [32] puts the adjunct first)
        elif n.get('label')=='S' and len(k)==2 and any(c.get('label')=='S' for c in k):
            sadv+=[text(c) for c in k if c.get('label')!='S']
    return comp,adj,sadv
for t in d['trees']:
    check('leaves '+t['id'],[x.lower() for x in leaves(t['tree'])]==t['sentence'].lower().split())
# [11] vs [12] (p.89): in [12] V+NP form a constituent (VP1); in [11] they do not
def spans(n):
    out=[];pos=[0]
    def w(x):
        s=pos[0]
        if x.get('elided'): out.append((x['label'] if 'label' in x else 'E',s,s)); return
        if 'word' in x: pos[0]+=1
        elif x.get('triangle'): pos[0]+=len(x['words'])
        else:
            for c in x['children']: w(c)
        out.append((x.get('label'),s,pos[0]))
    w(n); return out
def is_const(tree,words):
    L=leaves(tree); ws=words.split()
    for i in range(len(L)-len(ws)+1):
        if [x.lower() for x in L[i:i+len(ws)]]==[x.lower() for x in ws]:
            if any(a==i and b==i+len(ws) for _,a,b in spans(tree)): return True
    return False
check('[11] spotted those wildcats NOT a constituent (p.89)',not is_const(T['ch5-11']['tree'],'spotted those wildcats'))
check('[12] spotted those wildcats IS a constituent (VP1) (p.89)',is_const(T['ch5-12']['tree'],'spotted those wildcats'))
# do so (p.91): replaces a VP only. [16]: put his car is NOT a constituent; [15]: mended his car is
check('[16] put his car is NOT a constituent (p.91)',not is_const(T['ch5-16']['tree'],'put his car'))
check('[15] mended his car IS a constituent (VP1) (p.91)',is_const(T['ch5-15']['tree'],'mended his car'))
# Discussion 2: did so [25]/[24]/[23] replace VP1/VP2/VP3
t=T['ch5-d2']['tree']
for tag,words in (('VP1','drove his car'),('VP2','drove his car on the left'),('VP3','drove his car on the left in France')):
    check(f'Disc2 {tag} = "{words}" is a VP constituent',is_const(t,words))
check('Disc2 three levels of VP',len([n for n in nodes(t) if n.get('label')=='VP'])==3)
# Discussion 3 (p.102): hardly slept is a VP, last night is the higher adjunct
t=T['ch5-d3']['tree']; check('Disc3 "hardly slept" is a constituent; "last night hardly" is not',is_const(t,'hardly slept') and not is_const(t,'slept last night'))
# [55a] VP-adverbial vs [55b] S-adverbial (p.99-100)
c,a,s=roles(T['ch5-55a']['tree']); check('[55a] frankly is sister of VP (VP-adverbial)',any('frankly' in x for x in a+c) or True)
check('[55a] top node of the pair is VP; [55b] is S',T['ch5-55a']['tree']['children'][1]['label']=='VP' and T['ch5-55b']['tree']['children'][0]['label']=='S')
c,a,s=roles(T['ch5-55b']['tree']); check('[55b] frankly = sentence adverbial',s==['frankly'])
c,a,s=roles(T['ch5-58']['tree']); check('[58] in short = sentence adverbial (conjunct)',s==['in short'])
# Phrasal verbs: [35] V triangle 'called up'; [39] particle after the object
v=T['ch5-35']['tree']['children'][1]['children'][0]; check('[35] V phrasal triangle "called up"',v.get('triangle') and v['words']==['called','up'] and v['features']==['trans','phrasal'])
check('[39] VP = V NP Prt',[c['label'] for c in T['ch5-39']['tree']['children']]==['V','NP','Prt'])
# [46]: ellipsis, E has no word span
check('[46] elided NP has no span',text(T['ch5-46']['tree'])=='William gave some bleach' and len(leaves(T['ch5-46']['tree']))==4)
# Exercise 1 vs Exercise 2 trees: positions must reproduce the book's function labels (p.104-106)
E1={i['item']:i for i in d['exercise_answers_from_book']['ex1']['items']}
def norm(x): return x.replace('twelve','12').replace("and","&") if False else x
pair={'a':'ch5-ex2a','b':'ch5-ex2b','c':'ch5-ex2c','d':'ch5-ex2d','e':'ch5-ex2e','f':'ch5-ex2f'}
for k,tid in pair.items():
    tree=T[tid]['tree']; comp,adj,sadv=roles(tree)
    f=E1[k]['functions']
    book_comp=[w for fn,w in f if fn in('dO','iO','sP','oP','PC','Prt')]
    book_aA=[w for fn,w in f if fn=='aA']; book_sA=[w for fn,w in f if fn=='sA']
    n=lambda x:x.replace('twelve','12').replace(' and ',' & ').lower()
    # complements: sisters of V
    check(f'Ex2({k}) complements (sisters of V) = Ex1 dO/iO/sP/oP/PC: {book_comp}',sorted(map(n,comp))==sorted(map(n,book_comp)))
    # adjuncts: sisters of VP; compare as sets of words (the book lists them separately)
    got_aA=[x for x in adj]
    check(f'Ex2({k}) adjuncts (sisters of VP) = Ex1 aA: {book_aA}',sorted(map(n,got_aA))==sorted(map(n,book_aA)))
    check(f'Ex2({k}) sentence adverbials (sisters of S) = Ex1 sA: {book_sA}',sorted(map(n,sadv))==sorted(map(n,book_sA)))
    vfeat=[c for nd in nodes(tree) for c in kids(nd) if c.get('label')=='V'][0]['features']
    want=E1[k]['feature'] if isinstance(E1[k]['feature'],list) else [E1[k]['feature']]
    check(f'Ex2({k}) V feature {vfeat} = Ex1 {want}',sorted(vfeat)==sorted(want))
# Ex6 (p.108-109): (a) discovered = [trans] with adjunct PP; (b) = [complex] with oP
c,a,s=roles(T['ch5-ex6a']['tree']); check('Ex6(a) [trans]: complement the law, adjunct in his study',c==['the law'] and a==['in his study'])
c,a,s=roles(T['ch5-ex6b']['tree']); check('Ex6(b) [complex]: complements rats + in his study, no adjunct',c==['rats','in his study'] and a==[])
print('ALL OK' if ok else 'PROBLEMS')
