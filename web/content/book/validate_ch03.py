import json
d=json.load(open('ch03.trees.json')); T={t['id']:t for t in d['trees']}; ok=True
def leaves(n):
    if 'word' in n: return [n['word']]
    if n.get('triangle'): return list(n['words'])
    return [x for c in n['children'] for x in leaves(c)]
def check(name,c):
    global ok; print(('OK   ' if c else 'FAIL ')+name); ok&=bool(c)
def walk(n):
    yield n
    if 'children' in n and not n.get('triangle'):
        for c in n['children']: yield from walk(c)
for t in d['trees']:
    check('leaves '+t['id'],[x.lower() for x in leaves(t['tree'])]==t['sentence'].lower().split())
# book p.61: the mother and the sisters of a co-ordinator all have the same category label
COORD={'and','but','or'}
for t in d['trees']:
    for n in walk(t['tree']):
        ch=n.get('children',[])
        if any(c.get('word') in COORD for c in ch if 'word' in c):
            labs={c.get('label') for c in ch if 'word' not in c}
            check(f"{t['id']} coordination: mother {n['label']} = sisters {labs}",labs=={n['label']})
# p.52-53: names/pronouns are full NPs; p.57 PP forms
check('[14] NP>name>Max',T['ch3-14']['tree']=={'label':'NP','children':[{'label':'name','children':[{'word':'Max'}]}]})
check('[18] NP>pronoun>they',T['ch3-18']['tree']['children'][0]['label']=='pronoun')
check('[19a] PP>P>there',T['ch3-19a']['tree']['children'][0]['label']=='P')
check('[19b] PP = P + NP triangle',[c['label'] for c in T['ch3-19b']['tree']['children']]==['P','NP'] and T['ch3-19b']['tree']['children'][1].get('triangle'))
# p.60-61: in [40b] too modifies the co-ordinate A (DEG + A over A and A)
t=T['ch3-40b']['tree']; check('[40b] DEG + co-ordinate A',[c['label'] for c in t['children']]==['DEG','A'] and any(c.get('word')=='and' for c in t['children'][1]['children']))
check('[40a] 2 APs, first a simple A',len([c for c in T['ch3-40a']['tree']['children'] if 'label' in c])==2)
# p.61: [41a] lexical co-ordination (Ps) vs [41b] phrasal (PPs)
check('[41a] PP = coordP + NP',[c['label'] for c in T['ch3-41a']['tree']['children']]==['P','NP'])
check('[41b] PP and PP',[c.get('label',c.get('word')) for c in T['ch3-41b']['tree']['children']]==['PP','and','PP'])
# p.56 (summary of 'more obviously artificial'): AP = AdvP + A; AdvP = deg + Adv
t=T['ch3-text-b']['tree']; check('AP = AdvP + A',[c['label'] for c in t['children']]==['AdvP','A'] and [c['label'] for c in t['children'][0]['children']]==['DEG','Adv'])
# p.64/65: Ex4 hint: very touchy is an AP inside so very touchy
t=T['ch3-ex4']['tree']; check('Ex4 AP = DEG + AP(DEG A)',[c['label'] for c in t['children']]==['DEG','AP'] and ' '.join(leaves(t['children'][1]))=='very touchy')
# Ex3(d),(e) (p.64): S = NP VP ; subject NP immediately under S (Ch2 rule still holds)
t=T['ch3-ex3d']['tree']; check('Ex3d S>NP,VP with co-ordinate VP',[c['label'] for c in t['children']]==['NP','VP'])
t=T['ch3-ex3e']['tree']; check('Ex3e co-ordinate S',[c.get('label',c.get('word')) for c in t['children']]==['S','and','S'])
# [7] p.51: only one noun heads; N sits directly over tactics, NP over the whole
t=T['ch3-7']['tree']; check('[7] NP top, N over tactics',t['label']=='NP' and t['children'][1]['children'][1]=={'label':'N','children':[{'word':'tactics'}]})
# Exercise answers sanity (p.63): heads are words of their NPs
A=d['exercise_answers_from_book']['ex2']
check('Ex2 each head occurs in its NP',all(h in n.split() for n,h in zip(A['NPs'],A['heads'])))
print('ALL OK' if ok else 'PROBLEMS')
