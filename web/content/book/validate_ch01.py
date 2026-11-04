import json
d=json.load(open('ch01.trees.json'))
def leaves(n):
    if 'word' in n: return [] if n.get('ellipsis') else [n['word']]
    if n.get('triangle'): return n['words']
    return [w for c in n['children'] for w in leaves(c)]
def nodes(n,path=()):
    if 'word' in n: return
    yield path,n
    if not n.get('triangle'):
        for i,c in enumerate(n['children']): yield from nodes(c,path+(i,))
def spans(n):
    out=[];pos=[0]
    def walk(x):
        s=pos[0]
        if 'word' in x:
            if not x.get('ellipsis'): pos[0]+=1
        elif x.get('triangle'): pos[0]+=len(x['words'])
        else:
            for c in x['children']: walk(c)
        out.append((x.get('label'),s,pos[0]))
    walk(n); return out
ok=True
# 1. leaves match sentence
for t in d['trees']+d['no_book_tree_needs_derivation']:
    s=t.get('sentence')
    if s and 'beside a stream that' not in s and t['tree'].get('label')!='PHRASE-a':
        L=leaves(t['tree'])
        if L!=s.split(): ok=False; print('LEAF MISMATCH',t.get('id',t.get('ex')),L)
# 2. Ex1 via "one node dominates all and only these words"
ex1=[t for t in d['trees'] if t['id']=='ch1-ex1'][0]['tree']
sp=spans(ex1); order=leaves(ex1)
def is_const(words):
    idx=sorted(order.index(w) for w in words)
    if idx!=list(range(idx[0],idx[-1]+1)): return False
    return any(s==idx[0] and e==idx[-1]+1 and (e-s)>=1 for _,s,e in sp)
def expand(x):
    names={'E':['c','d'],'C':['e','f','g','h'],'D':['a','b'],'F':['e','f']}
    out=[]
    for w in x: out+=names.get(w,[w])
    return out
for k,seq in d['exercise_answers_from_book']['ex1']['sequences'].items():
    got=is_const(expand(seq)); want=d['exercise_answers_from_book']['ex1']['answers'][k]
    print('Ex1',k,got,want,'OK' if got==want else 'FAIL'); ok&=(got==want)
# 3. Ex2 immediate constituents
def lab(c): return c.get('label') or c['word']
for N,want in d['exercise_answers_from_book']['ex2']['answers'].items():
    node=[n for _,n in nodes(ex1) if n['label']==N][0]
    got=[lab(c) for c in node['children']]; print('Ex2',N,got,'OK' if got==want else 'FAIL'); ok&=(got==want)
# 4. Ch1 [35]: 'a stream that had dried up' must NOT be a constituent; [34]: it must be, 'beside a' must not
t34=[t for t in d['trees'] if t['id']=='ch1-34'][0]['tree']; t35=[t for t in d['trees'] if t['id']=='ch1-35'][0]['tree']
def const_in(tree,words):
    L=leaves(tree);i=L.index(words[0]);s,e=i,i+len(words)
    return L[s:e]==words and any(a==s and b==e for _,a,b in spans(tree))
c1=const_in(t34,"a stream that had dried up".split()); c2=const_in(t34,["beside","a"]); c3=const_in(t35,"a stream that had dried up".split())
print('[34] a stream that had dried up:',c1,'(book: True)'); print('[34] beside a:',c2,'(book: False)'); print('[35] a stream that had dried up:',c3,'(book: False)')
ok&=(c1 and not c2 and not c3)
# 5. Ex6: each analysis' immediate constituents of the sentence (counts per the book)
for k,n in (('a',2),('b',2),('c',3)):
    t=[x for x in d['trees'] if x['id']=='ch1-ex6'+k][0]['tree']; print('Ex6',k,'IC of Sentence =',len(t['children']),'(book:',n,')'); ok&=(len(t['children'])==n)
print('ALL OK' if ok else 'PROBLEMS')
