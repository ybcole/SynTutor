#!/usr/bin/env python3
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rule_categories import get_category  # noqa: E402

ROOT = '/Users/angelo/Downloads/SynTutor'
OUT_MD = os.path.join(ROOT, 'docs', 'exhaustive_tree_structure_explanations_v2.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'exhaustive_tree_structure_explanations_v2.json')

# Load data
tree_sheet = json.load(open(os.path.join(ROOT, 'web/content/tree_sheet.json')))
rule_concepts_js = open(os.path.join(ROOT, 'web/js/rule-concepts.js')).read()
concepts = {}
m = re.search(r"RULE_CONCEPTS\s*=\s*\{(.*?)\n\};", rule_concepts_js, re.S)
if m:
    for rid, text in re.findall(r"'([\d.]+)'\s*:\s*'((?:[^'\\]|\\.)*)'", m.group(1)):
        concepts[rid] = text.replace("\\'", "'")
    for rid, text in re.findall(r"'([\d.]+)'\s*:\s*\"((?:[^\"\\]|\\.)*)\"", m.group(1)):
        if rid not in concepts:
            concepts[rid] = text.replace('\\"', '"')

st4 = [s for s in tree_sheet['stages'] if s['id']==4][0]
all_rules = {}
for it in st4['items']:
    if it.get('rule'):
        all_rules[it['rule']] = {
            'name': it['name'],
            'constraint': it.get('constraint'),
            'example': it.get('example'),
            'concept': it.get('concept') or concepts.get(it['rule'], '')
        }

exhaustive = {}

# Start from all existing rules
for rid, info in all_rules.items():
    cat = get_category(rid)
    major = int(rid.split('.')[0])
    
    if major == 1:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"In the constituency tree, '{info['name'].lower()}' must appear in the correct morphological form for its lexical category and syntactic position within its phrase subtree (NP/VP/ADJP/ADVP). The form is licensed by the structural slot in that phrase.",
            'template': f"In the {info['name'].lower()} construction, '{'{word}'} is correctly formed for its position in the relevant phrase subtree as determined by constituency structure."}
    elif major == 2:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Grammatical agreement is a relation between constituents in the tree structure. For {info['name'].lower()}, the dependent must agree with its controller in person/number/gender/features based on head–dependent relations (e.g. subject–predicate in S, anaphor–antecedent, determiner–head noun), not linear order alone.",
            'template': f"In the clause/tree structure, '{'{dependent}'} correctly agrees with '{'{controller}'} based on their hierarchical relation in the constituency tree."}
    elif major == 3:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Within the NP subtree, determiners/articles function as specifiers/daughters of NP selecting the nominal head. For {info['name'].lower()}, the determiner must be compatible with the head noun’s countability and definiteness features in the NP structure.",
            'template': f"In the NP subtree headed by '{'{head_noun}'} ({'{countability}'}), the determiner/article '{'{determiner}'} is correctly selected for this NP’s features."}
    elif major == 4:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Within the NP subtree, nouns appear as heads or complements. For {info['name'].lower()}, the noun form and its relation to determiners/modifiers/complements must satisfy NP constituency requirements.",
            'template': f"In the NP subtree, '{'{noun}'} appears in the correct form/usage for {info['name'].lower()}, properly licensed by its position relative to the NP head and sisters."}
    elif major == 5:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Pronouns occupy NP positions and must satisfy case, agreement, and binding based on their structural position. For {info['name'].lower()}, the pronoun must be licensed by its argument role in the phrase/clause tree and agree with its antecedent where required.",
            'template': f"In its NP position, pronoun '{'{pronoun}'} is correctly case-marked and agrees with antecedent '{'{antecedent}'} according to the clause’s binding structure."}
    elif major == 6:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Verbs project VP subtrees with internal structure (verb complex: auxiliaries + main verb). For {info['name'].lower()}, verb form, tense/aspect, and subcategorization must be correctly realized with appropriate complements/arguments as daughters of VP, matching the verb’s valence.",
            'template': f"In the VP subtree, '{'{verb}'} correctly realizes {info['name'].lower()} with its required arguments/complements licensed by the verb’s subcategorization frame in this structure."}
    elif major == 7:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Adjectives project ADJP, adverbs project ADVP. For {info['name'].lower()}, modifiers appear in correct positions relative to their heads (pre-/post-head) and are properly formed/ordered within the phrase structure.",
            'template': f"In the ADJP/ADVP subtree, '{'{modifier}'} correctly modifies head '{'{head}'} in its proper position as {info['name'].lower()}."}
    elif major == 8:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Prepositions head PP subtrees taking an NP complement. For {info['name'].lower()}, preposition selection and PP structure must be correct, with the preposition projecting PP over its complement NP.",
            'template': f"In the PP subtree headed by preposition '{'{prep}'} with complement NP '{'{np}'}', the construction is correctly formed for {info['name'].lower()}."}
    elif major == 9:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Clause structure is organized as S/SQ/SBARQ with subject–predicate splits. For {info['name'].lower()}, constituents appear in positions licensed by the clause type with correct word order and constituent structure.",
            'template': f"In this clause structure ({'{clause_type}'}), '{info['name'].lower()}' is correctly realized with constituents in positions licensed by constituency."}
    elif major == 10:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Punctuation marks clause/phrase boundaries relative to syntactic structure. For {info['name'].lower()}, punctuation is placed correctly at constituent boundaries.",
            'template': f"Punctuation '{'{punct}'} is correctly placed for {info['name'].lower()} relative to clause/phrase boundaries in the tree."}
    elif major == 11:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"Word choice must fit the syntactic role and semantic requirements of positions in the tree. For {info['name'].lower()}, the lexical item is appropriately selected for its argument/modifier role.",
            'template': f"In its syntactic position in the tree, '{'{word}'} is correctly selected for the role it plays as {info['name'].lower()}."}
    else:
        exhaustive[rid] = {'name': info['name'], 'category': cat,
            'explanation': f"In the relevant phrase or clause subtree, {info['name'].lower()} is correctly realized according to constituency structure requirements.",
            'template': f"The elements of {info['name'].lower()} are correctly positioned and licensed in their tree positions."}

# VERB TYPES - exhaustive
verb_types = [
    ('VERB.INTRANSITIVE', 'Intransitive verb', 
     "In the VP subtree, an intransitive verb takes no direct object NP complement. The verb projects VP and its arguments are just the subject (external argument); no NP complement is required by its subcategorization frame."),
    ('VERB.TRANSITIVE', 'Transitive verb (monotransitive)',
     "In the VP subtree, a transitive verb takes a direct object NP as its complement daughter. The verb licenses exactly one internal argument (the direct object) in addition to the external subject argument."),
    ('VERB.DITRANSITIVE.DO.IO', 'Ditransitive verb (double object)',
     "In the VP subtree, a ditransitive verb licenses two internal arguments: indirect object NP and direct object NP (double object construction). The VP structure shows both NP complements in the dative alternation’s double-object form, with the IO typically closer to the verb."),
    ('VERB.DITRANSITIVE.PP', 'Ditransitive verb (prepositional dative)',
     "In the VP subtree, the ditransitive verb licenses a direct object NP and a prepositional phrase (PP) complement headed by 'to' or 'for' expressing the goal/recipient. This is the PP variant of the dative alternation, with PP as the second complement."),
    ('VERB.COMPLEX.TRANSITIVE', 'Complex transitive verb',
     "In the VP subtree, a complex transitive verb takes a direct object NP plus a secondary predicate (ADJP, NP, or VP) that predicates of the object. The structure shows object + object-predicate relation within the VP."),
    ('VERB.COPULAR.LINKING', 'Copular/linking verb',
     "Copular verbs (be, become, seem, appear, remain, etc.) project VP/S structures where the subject is linked to a subject complement (NP/ADJP/PP/VP) rather than taking a true direct object. The complement predicates of the subject."),
    ('VERB.PHRASAL.INTRANS', 'Intransitive phrasal verb',
     "In the VP subtree, a particle (adverbial particle) combines with the verb to form a phrasal verb. For intransitive phrasal verbs, no NP object is taken; the particle is part of the verbal complex/unit within VP."),
    ('VERB.PHRASAL.TRANS.SEP', 'Transitive phrasal verb (separable)',
     "In the VP subtree, a transitive phrasal verb allows separation: the NP object may appear between verb and particle, or after the particle. Both orderings are possible for separable phrasal verbs while maintaining object as complement."),
    ('VERB.PHRASAL.TRANS.INSEP', 'Transitive phrasal verb (inseparable)',
     "In the VP subtree, an inseparable transitive phrasal verb keeps the particle immediately after or attached to the verb complex; the NP object follows the particle as complement and cannot intervene between verb and particle."),
    ('VERB.PREPOSITIONAL', 'Prepositional verb (idiomatic)',
     "Prepositional verbs (look at, depend on, listen to) take a PP complement rather than a direct object NP. The preposition is lexically selected by the verb and forms part of the verb’s subcategorization in the VP structure."),
    ('VERB.UNACCUSATIVE', 'Unaccusative verb',
     "Unaccusative verbs (arrive, appear, fall) have a single argument that is underlyingly a direct object/patient but surfaces as subject. In the clause tree, the subject originates inside VP and moves to subject position with no external agent."),
    ('VERB.UNERGATIVE', 'Unergative verb',
     "Unergative verbs (laugh, run, talk) have a single argument that is an agent/experiencer, underlyingly a subject. In VP structure, this argument is external with no internal object/patient."),
    ('VERB.RAISING', 'Raising verb',
     "Raising verbs (seem, appear, tend) take a VP complement but do not assign a theta role to their surface subject; the subject is raised from the embedded clause and agrees with the matrix predicate."),
    ('VERB.CONTROL', 'Control verb',
     "Control verbs (want, try, promise) take a VP/infinitival complement and assign a theta role to their subject; the subject controls the understood subject (PRO) of the embedded infinitive."),
    ('VERB.MODAL.AUX', 'Modal auxiliary',
     "Modals (can, could, must, should, will) form part of the VP auxiliary complex, taking a bare VP complement. They contribute tense/modality/epistemic/deontic meaning without taking full NP arguments as their internal complements."),
    ('VERB.SEMI.AUX', 'Semi-auxiliary/periphrastic',
     "Semi-auxiliaries (have to, be going to, used to) behave like auxiliaries in forming the verb complex but retain some nominal/lexical properties; they project into the VP auxiliary structure with their complements."),
    ('VERB.LIGHT', 'Light verb',
     "Light verbs (take a walk, give a call, make a decision) have reduced semantic content; the nominal element carries the main meaning and forms a complex predicate within VP structure."),
]

for vid, name, expl in verb_types:
    exhaustive[vid] = {'name': name, 'category': 'Verbs',
        'explanation': f"In the VP subtree structure: {expl} The verb’s valence and the internal structure of VP determine the positions of complements/arguments.",
        'template': f"In the VP subtree headed by '{'{verb}'} ({name}), the arguments/complements appear in positions licensed by this verb type within the VP structure."}

# COORDINATION - critical for "and"
coord = [
    ('COORD.CC', 'Coordinating conjunction (and/or/but/nor/yet/so)',
     "Coordinating conjunctions (CC: and, or, but, nor, yet, so) connect constituents of like category (NP–NP, VP–VP, AdjP–AdjP, AdvP–AdvP, PP–PP, or clauses S–S) into a coordinate structure. The conjunction is the coordinator linking the conjuncts."),
    ('COORD.NP', 'NP coordination',
     "Two or more NP conjuncts joined by a coordinating conjunction form a coordinated NP. The coordinate NP can function as subject/object/complement, and agreement with the verb follows coordination rules (and -> plural in most cases, or/nor -> agreement with nearer conjunct)."),
    ('COORD.VP', 'VP coordination',
     "VP conjuncts joined by and/or/but form a coordinated VP. Both VPs share the same subject (in canonical cases) and are sisters under a higher node or coordinated at VP level."),
    ('COORD.ADJ', 'Adjective phrase coordination',
     "ADJP conjuncts joined by coordinating conjunction form a coordinated ADJP, functioning as a single modifier/complement."),
    ('COORD.ADV', 'Adverb phrase coordination',
     "ADVP conjuncts joined by coordinating conjunction form a coordinated ADVP."),
    ('COORD.PP', 'Prepositional phrase coordination',
     "PP conjuncts joined by coordinating conjunction form a coordinated PP."),
    ('COORD.CLAUSE', 'Clause coordination',
     "Two independent clauses (S) joined by a coordinating conjunction (and/but/or/so/yet) form a coordinate structure at clause level (coordination of sentences/clauses). Each conjunct is a complete clause tree."),
    ('COORD.GAPPING', 'Coordination with gapping',
     "In coordination, material may be elided from non-initial conjuncts (gapping). The remaining elements are licensed by parallel structure in the coordinate tree."),
]

for cid, name, expl in coord:
    exhaustive[cid] = {'name': name, 'category': 'Sentence structure',
        'explanation': f"At the constituency level: {expl} The coordinate structure shows conjuncts and coordinator as sisters under a coordination node, maintaining parallel syntactic categories.",
        'template': f"In this coordinate structure, '{'{conj1}'} and '{'{conj2}'} are conjuncts of the same category joined by coordinating conjunction '{'{cc}'} ({name}), forming a parallel structure in the tree."}

# Other overlooked categories
extras = [
    ('REL.CLAUSE', 'Relative clause',
     "A relative clause (SBAR/CP) modifies an NP, introduced by a relativizer (who/which/that/where/whose). The relativizer relates the clause to the antecedent NP in the tree structure."),
    ('APPOSITIVE', 'Appositive',
     "An appositive NP appears adjacent to another NP, providing additional identification. In the tree, the appositive is often a sister/adjunct to the head NP."),
    ('PARENTHETICAL', 'Parenthetical',
     "Parentheticals are inserted elements not integrated into the core clause structure; they appear as adjuncts/interruptions in the tree."),
    ('EXPLETIVE.THERE', 'Expletive there',
     "'There' in existential constructions is an expletive with no referential meaning, occupying subject position of S while the true logical subject appears post-verbally."),
    ('IT.CLEFT', 'Cleft/it-cleft',
     "It-clefts and wh-clefts are marked structures that focus constituents; the cleft structure affects clause organization."),
    ('INVERSION.Q', 'Subject–aux inversion (questions)',
     "In yes/no questions (SQ), the auxiliary inverts with the subject NP. In wh-questions (SBARQ), the wh-phrase moves to specifier position with subject–aux inversion in the clause."),
    ('NEGATION', 'Negation',
     "Negation (not/n't) appears in the VP auxiliary complex or as part of negated elements; its position affects scope within the clause structure."),
    ('TAG.QUESTION', 'Tag question',
     "Tag questions attach a short question at the end of the clause, with reversed polarity relative to the main clause."),
    ('ELLIPSIS.VP', 'VP ellipsis',
     "VP ellipsis omits a VP under identity with an antecedent VP, licensed by auxiliaries/modals in the clause structure."),
]

for eid, name, expl in extras:
    exhaustive[eid] = {'name': name, 'category': 'Sentence structure',
        'explanation': f"{expl} These structures appear as specific configurations in the constituency tree with characteristic phrase labels and relations.",
        'template': f"In this structure, '{'{element}'} realizes {name.lower()} in its proper tree position relative to the clause/phrase structure."}

# Merge any remaining from original
remaining = sorted(set(all_rules.keys()) - set(exhaustive.keys()))
for rid in remaining:
    info = all_rules[rid]
    cat = get_category(rid)
    exhaustive[rid] = {'name': info['name'], 'category': cat,
        'explanation': f"Within the relevant phrase or clause subtree, {info['name'].lower()} is correctly realized according to constituency structure requirements, with proper licensing by heads and structural positions.",
        'template': f"The elements of {info['name'].lower()} are correctly positioned and licensed in their tree positions within the constituency structure."}

out = {
    'title': 'Exhaustive Tree-Structure Explanations v2 (All Rules + Verb Types + Coordination)',
    'total_rules': len(exhaustive),
    'all_rules_covered': True,
    'includes_verb_types': True,
    'includes_coordination': True,
    'includes_extras': True,
    'principles': [
        "Every explanation must reference the sentence/words/phrase and their positions in the constituency tree",
        "Use syntactic terminology: daughter, sister, head, complement, adjunct, modifier, specifier, coordinator, conjunct",
        "Reference phrase labels (S, NP, VP, PP, ADJP, ADVP, SBAR, SBARQ, SQ, CP)",
        "Explain structure: 'inside the NP/VP subtree...', 'as sister to the head...', 'as complement of...'",
        "Cover all verb valences: intransitive, transitive, ditransitive (double object & PP), complex transitive, copular, phrasal (separable/inseparable), prepositional, unaccusative/unergative, raising/control, modals/semi-auxiliaries, light verbs",
        "Cover coordination at all levels (NP/VP/AdjP/AdvP/PP/clause) with coordinating conjunctions and/or/but/nor/yet/so; explain parallel structure",
        "Explain subject–predicate split in clauses and agreement determined by heads/relations",
        "Explain in syntax/lexicon terms appropriate to constituency grammar"
    ],
    'rules': exhaustive
}

os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
with open(OUT_JSON, 'w') as f:
    json.dump(out, f, indent=2)

lines = []
lines.append('# Exhaustive Tree-Structure Explanations v2')
lines.append(f'\n**Total: {len(exhaustive)} entries (all system rules + verb types + coordination + extras)**\n')
lines.append('## Principles\n')
for p in out['principles']:
    lines.append(f'- {p}')
lines.append('\n')

cats = {}
for rid, info in sorted(exhaustive.items(), key=lambda x: (x[0][:4] != 'VERB' and x[0][:5] != 'COORD' and x[0][:4] != 'REL.' and x[0] not in ['APPOSITIVE','PARENTHETICAL','EXPLETIVE.THERE','IT.CLEFT','INVERSION.Q','NEGATION','TAG.QUESTION','ELLIPSIS.VP'], x[0])):
    c = info['category']
    if c not in cats: cats[c] = []
    cats[c].append((rid, info))

# Add special sections first
lines.append('## Verb Types (Exhaustive)\n')
for rid, info in sorted([(k,v) for k,v in exhaustive.items() if k.startswith('VERB.')]):
    lines.append(f'### {rid}: {info["name"]}\n**Tree-Structure Explanation:**\n\n{info["explanation"]}\n\n**Usage Template:**\n\n{info["template"]}\n\n---\n\n')

lines.append('## Coordination (and/or/but/nor/yet/so)\n')
for rid, info in sorted([(k,v) for k,v in exhaustive.items() if k.startswith('COORD.')]):
    lines.append(f'### {rid}: {info["name"]}\n**Tree-Structure Explanation:**\n\n{info["explanation"]}\n\n**Usage Template:**\n\n{info["template"]}\n\n---\n\n')

lines.append('## Relative Clauses, Appositives, Inversion, etc.\n')
for rid in ['REL.CLAUSE','APPOSITIVE','PARENTHETICAL','EXPLETIVE.THERE','IT.CLEFT','INVERSION.Q','NEGATION','TAG.QUESTION','ELLIPSIS.VP']:
    if rid in exhaustive:
        info = exhaustive[rid]
        lines.append(f'### {rid}: {info["name"]}\n**Tree-Structure Explanation:**\n\n{info["explanation"]}\n\n**Usage Template:**\n\n{info["template"]}\n\n---\n\n')

for cat in ['Word forms', 'Agreement', 'Articles and determiners', 'Nouns', 'Pronouns', 
           'Verbs', 'Adjectives and adverbs', 'Prepositions', 'Sentence structure', 
           'Punctuation and orthography', 'Meaning and usage', 'Other']:
    if cat not in cats: continue
    lines.append(f'## {cat} (Rules)\n')
    for rid, info in sorted(cats[cat], key=lambda x: [int(p) for p in x[0].split('.') if p.isdigit()]):
        if rid.startswith(('VERB.','COORD.')): continue
        lines.append(f'### Rule {rid}: {info["name"]}\n**Tree-Structure Explanation:**\n\n{info["explanation"]}\n\n**Usage Template:**\n\n{info["template"]}\n\n---\n\n')

with open(OUT_MD, 'w') as f:
    f.write('\n'.join(lines))

print(f'Wrote {OUT_MD}')
print(f'Wrote {OUT_JSON}')
print(f'Total: {len(exhaustive)}')
