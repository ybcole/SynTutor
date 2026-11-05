import json
d=json.load(open('ch04.trees.json')); T={t['id']:t for t in d['trees']}; ok=True
def leaves(n):
    if 'word' in n: return [n['word']]
    if n.get('triangle'): return list(n['words'])
    return [x for c in n['children'] for x in leaves(c)]
def text(n): return ' '.join(leaves(n))
def check(name,c):
    global ok; print(('OK   ' if c else 'FAIL ')+name); ok&=bool(c)
TABLE=d['exercise_answers_from_book']['function_table']
def functions(tree,feature):
    """read functions off positions (CONVENTIONS section 6, book p.79)"""
    vp=[c for c in tree['children'] if c['label']=='VP'][0]
    v=[c for c in vp['children'] if c['label']=='V'][0]; sis=[c for c in vp['children'] if c is not v]
    out=[('S',text([c for c in tree['children'] if c['label']=='NP'][0])),('V',text(v))]
    if feature=='ditrans' and len(sis)==2 and sis[1]['label']=='PP':   # V NP PP: dO + iO (p.73)
        out+=[('dO',text(sis[0])),('iO',text(sis[1]))]
    else:
        out+=list(zip(TABLE[feature],[text(s) for s in sis]))
        if len(sis)!=len(TABLE[feature]): out.append(('MISMATCH',len(sis)))
    return out
for t in d['trees']:
    check('leaves '+t['id'],[x.lower() for x in leaves(t['tree'])]==t['sentence'].lower().split())
for t in d['trees']:
    vp=[c for c in t['tree']['children'] if c['label']=='VP'][0]; v=[c for c in vp['children'] if c['label']=='V'][0]
    check(f"{t['id']} V has feature; complements = those of the book's table (p.79)",
          all(any(x==f for x in v['features']) for f in v['features']) and
          all(len([c for c in vp['children'] if c is not v])==len(TABLE[f]) or (f=='ditrans' and len(vp['children'])==3) for f in v['features']))
exp={'ch4-21':[('S','Phil'),('V','dreads'),('dO','affectionate cats')],
 'ch4-26':[('S','William'),('V','gave'),('dO','Millie'),('dO','some bleach')],}
# book p.72: first NP of [ditrans] = indirect object, second = direct object
f=functions(T['ch4-26']['tree'],'ditrans'); check('[26] iO=Millie dO=some bleach (p.72)',f[2]==('iO','Millie') and f[3]==('dO','some bleach'))
f=functions(T['ch4-32']['tree'],'ditrans'); check('[32] dO=some bleach, iO=to Millie (p.73)',f[2]==('dO','some bleach') and f[3]==('iO','to Millie'))
f=functions(T['ch4-46a']['tree'],'intens'); check('[46a] sP=an auctioneer',f[2]==('sP','an auctioneer'))
f=functions(T['ch4-46b']['tree'],'trans'); check('[46b] dO=an auctioneer',f[2]==('dO','an auctioneer'))
f=functions(T['ch4-51']['tree'],'complex'); check('[51] dO=his own jokes, oP=extremely funny (p.77)',f[2:]==[('dO','his own jokes'),('oP','extremely funny')])
t=T['ch4-52b']['tree']
check('[52b] reading (a) iO=Bill dO=an amusing companion (p.77)',functions(t,'ditrans')[2:]==[('iO','Bill'),('dO','an amusing companion')] )
check('[52b] reading (b) dO=Bill oP=an amusing companion (p.77)',functions(t,'complex')[2:]==[('dO','Bill'),('oP','an amusing companion')])
check('[56] PC=at the falling acrobat',functions(T['ch4-56']['tree'],'prep')[2]==('PC','at the falling acrobat'))
check('[22] intransitive: V is the whole VP',len([c for c in T['ch4-22']['tree']['children'][1]['children']])==1)
# Ex4 trees carry the feature the book names for that sentence type
want={'a':'intens','b':'ditrans','c':'intrans','d':'complex','e':'trans','f':'prep'}
for k,fe in want.items():
    tr=T['ch4-ex4'+k]['tree']; v=[c for c in [c for c in tr['children'] if c['label']=='VP'][0]['children'] if c['label']=='V'][0]
    check(f'Ex4({k}) feature [{fe}]',v['features']==[fe])
# Ex1 answers (p.82): function sequence must match the book's own summary table (p.79) for the verb's feature
for it in d['exercise_answers_from_book']['ex1']['items']:
    seq=[f for f,_ in it['functions'] if f not in('S','V')]
    check(f"Ex1({it['item']}) [{it['feature']}] functions {seq} match table",
          seq==TABLE[it['feature']] or (it['feature']=='ditrans' and sorted(seq)==['dO','iO']))
# Ex4(d) ties to Ex2(c) discussion: 'take' is [complex] with PP as object predicative (p.83)
check('Ex4(d) complex: second complement is a PP (object predicative may be PP, p.76)',functions(T['ch4-ex4d']['tree'],'complex')[3]==('oP','out of office'))
print('ALL OK' if ok else 'PROBLEMS')
