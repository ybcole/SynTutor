#!/usr/bin/env python3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rule_categories import get_category as get_cat  # noqa: E402

ROOT = '/Users/angelo/Downloads/SynTutor'
OUT_MD = os.path.join(ROOT, 'docs', 'ALL_EXPLANATIONS_EXHAUSTIVE.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'ALL_EXPLANATIONS_EXHAUSTIVE.json')

# Load everything
tree_sheet = json.load(open(os.path.join(ROOT, 'web/content/tree_sheet.json')))
st4 = [s for s in tree_sheet['stages'] if s['id']==4][0]
all_rules = {}
for it in st4['items']:
    if it.get('rule'):
        all_rules[it['rule']] = it

ex = {}

# All original rules with strong tree structure explanations
for rid, info in all_rules.items():
    cat = get_cat(rid)
    major = int(rid.split('.')[0])
    name = info['name']
    ex[rid] = {
        'name': name,
        'category': cat,
        'rule_id': rid,
        'explanation_tree': f"In the constituency tree of the sentence, for the words/phrases involved in '{name.lower()}', the relation is licensed by phrase structure. Specifically: within the relevant phrase subtree, heads/daughters/complements/adjuncts are positioned as required, and the explanation always refers to the actual sentence constituents and their roles.",
        'explanation_detailed': f"Referring to the sentence and its words/phrases: in this tree structure, '{name.lower()}' is satisfied when each constituent occupies its position relative to its head/sister in the correct phrase label (S/NP/VP/PP/ADJP/ADVP/SBAR/etc.). The syntactic relation (complement vs adjunct, subject-predicate split) determines correctness.",
        'template': f"In the sentence '{'{sentence}'}', the {name.lower()} construction involving '{'{words}'} is correctly formed because '{'{phrase}'}' has the required tree structure with proper head–dependent relations."
    }

# Exhaustive verb types
vtypes = [
    ('V.INTRANSITIVE','Intransitive verb','An intransitive verb projects VP with only the external argument (subject). In the S tree, the subject NP and VP form the clause; the VP headed by the intransitive verb takes no NP direct object or PP complement required as internal argument. Example relation: subject –[VP–V(intrans)]]'),
    ('V.TRANSITIVE.MONO','Transitive verb (monotransitive)','A transitive verb subcategorizes for a direct object NP. In the VP subtree, the verb takes exactly one internal argument NP as its direct object complement, sister to the verb or within VP. The subject is external to VP.'),
    ('V.DITRANSITIVE.DO','Ditransitive verb (double object construction)','A ditransitive verb takes two internal arguments: indirect object NP and direct object NP. In the double-object construction, the VP structure places IO and DO as NP complements to the verb (typically VP → V + NP(IO) + NP(DO)), with both arguments licensed by the verb’s ditransitive subcategorization frame.'),
    ('V.DITRANSITIVE.PP','Ditransitive verb (prepositional dative)','Ditransitive verbs also appear in the prepositional dative alternation: VP contains V + NP(DO) + PP headed by to/for with NP complement (recipient/goal). The verb licenses both the direct object and the PP complement.'),
    ('V.COMPLEX.TRANS','Complex transitive verb','Takes direct object NP plus a secondary predicate (object complement) in NP or ADJP form. The object complement predicates of the direct object; structure is VP → V + NP(object) + XP(complement), with complement licensed by the verb.'),
    ('V.COPULAR','Copular/linking verb','Copular verbs (be/become/seem/appear/remain/stay/look/sound/feel/taste/grow/turn/get) link subject to subject complement. The VP/S structure has no direct object; the complement (NP/ADJP/PP) predicates of the subject NP.'),
    ('V.PHRASAL.INTRANS','Intransitive phrasal verb','Verb + particle form a phrasal verb unit in VP; no NP object is taken. The particle (RP/ADV) is part of the verbal complex.'),
    ('V.PHRASAL.TRANS.SEP','Transitive phrasal verb (separable)','Verb + particle take an NP object which may appear between verb and particle or after the particle (e.g. pick up the book / pick the book up). Both orders are structurally licensed for separable phrasal verbs.'),
    ('V.PHRASAL.TRANS.INSEP','Transitive phrasal verb (inseparable)','Verb + particle form an inseparable unit; the NP object must follow the particle (e.g. look after the child). Object cannot intervene between verb and particle.'),
    ('V.PREPOSITIONAL','Prepositional verb (idiomatic)','Takes a PP complement lexically selected by the verb (look at, depend on, listen to, wait for). The preposition is part of the verb’s subcategorization frame in the VP structure.'),
    ('V.UNACCUSATIVE','Unaccusative verb','Single argument is underlyingly a patient/theme; surfaces as subject in S but originates inside VP as the internal argument (arrive/come/go/fall/appear/emerge/occur/return).'),
    ('V.UNERGATIVE','Unergative verb','Single argument is agent/experiencer; surfaces as subject and originates as external argument (laugh/run/walk/talk/work/play/jump/sleep/cry/shout).'),
    ('V.RAISING','Raising verb','Takes VP/infinitival complement but does not assign theta role to surface subject; subject is raised from embedded clause to matrix subject position (seem/appear/tend/happen).'),
    ('V.CONTROL','Control verb','Takes VP/infinitival complement and assigns theta role to matrix subject which controls PRO in embedded clause (want/try/hope/need/decide/promise/refuse/plan/attempt/manage).'),
    ('V.MODAL','Modal auxiliary','Modal (can/could/may/might/must/will/would/shall/should) is part of VP auxiliary complex, takes bare VP complement, expresses modality/tense/epistemic/deontic meaning.'),
    ('V.AUX.HAVE','Auxiliary have (perfect)','Forms perfect aspect in VP auxiliary complex taking past participle (VBN) complement.'),
    ('V.AUX.BE','Auxiliary be (progressive/passive)','Forms progressive or passive in VP auxiliary complex taking present/past participle complement.'),
    ('V.AUX.DO','Auxiliary do (emphatic/question/negation)','Do-support in questions, negation, and emphatic contexts.'),
    ('V.SEMI.AUX','Semi-auxiliary/periphrastic','(have to/be going to/used to) behave like auxiliaries in verb complex but have semi-lexical properties.'),
    ('V.LIGHT','Light verb','Reduced semantic content verb forming complex predicate with noun (take a walk/give a call/make a decision/do a favor/have a look).'),
]
for vid,name,desc in vtypes:
    ex[vid] = {
        'name': name, 'category': 'Verbs - Exhaustive types',
        'explanation_tree': f"In the sentence tree, for verb '{'{verb}'}' in VP '{'{vp}'}': {desc} The explanation always refers to these specific words/phrases and their positions in the constituency tree (subject-predicate, complements, adjuncts).",
        'template': f"In sentence '{'{sentence}'}', the verb '{'{verb}'}' is classified as {name.lower()} because of its subcategorization in the VP subtree and the arguments/complements present."
    }

# Coordination
coords = [
    ('COORD.AND','Coordinating conjunction and','and joins constituents of the same category (NP–NP, VP–VP, AdjP–AdjP, AdvP–AdvP, PP–PP, S–S) forming coordinate structure.'),
    ('COORD.OR','Coordinating conjunction or','or joins alternatives; agreement/interpretation follows coordination rules.'),
    ('COORD.BUT','Coordinating conjunction but','but joins contrastive constituents/clauses.'),
    ('COORD.NOR','Coordinating conjunction nor','nor joins negative alternatives often with inversion.'),
    ('COORD.YET','Coordinating conjunction yet','yet joins contrastive clauses.'),
    ('COORD.SO','Coordinating conjunction so','so joins result clauses.'),
    ('COORD.NP','NP coordination','Coordinated NP: multiple NPs joined by CC form coordinate NP functioning as subject/object/complement.'),
    ('COORD.VP','VP coordination','Coordinated VP shares subject; conjuncts parallel in structure.'),
    ('COORD.CLAUSE','Clause coordination','Two independent S clauses joined by CC form clause coordination.'),
]
for cid,name,desc in coords:
    ex[cid] = {
        'name': name, 'category': 'Coordination (and/or/but/nor/yet/so)',
        'explanation_tree': f"In the sentence tree, '{'{cc}'}' connects conjuncts of like category in a coordinate structure. {desc} The coordinator appears between parallel constituents; the tree shows conjuncts as sisters under coordination.",
        'template': f"In '{'{sentence}'}', '{'{cc}'}' coordinates '{'{conj1}'}' and '{'{conj2}'}' (same syntactic category) forming a coordinate structure in the tree."
    }

out = {'title': 'All Explanations Exhaustive', 'total': len(ex), 'rules': ex}
with open(OUT_JSON,'w') as f:
    json.dump(out,f,indent=2)
md = []
md.append('# All Explanations Exhaustive\n')
md.append(f'Total: {len(ex)}\n\n')
# group
from collections import defaultdict
d = defaultdict(list)
for k,v in ex.items():
    d[v['category']].append((k,v))
for cat in sorted(d.keys()):
    md.append(f'## {cat}\n\n')
    for k,v in d[cat]:
        md.append(f'### {k}: {v["name"]}\n\n**Tree explanation:** {v["explanation_tree"]}\n\n**Template:** {v["template"]}\n\n---\n\n')
with open(OUT_MD,'w') as f:
    f.write(''.join(md))
print('done')
