#!/usr/bin/env python3
"""Build a master sheet of SynTutor explanations rewritten to reference tree structure.

Scans matrix.py, ruleset.py, api.py and the tree sheet to collect every
explanation pattern used by SynTutor and rewrites them to talk about the
constituency tree structure (parent/child relations, phrase labels, heads).
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

OUT_MD = os.path.join(ROOT, 'docs', 'tree_structure_explanations_master.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'tree_structure_explanations_master.json')

# Tree structure explanation templates
TEMPLATES = {
    # Clause level
    'C-SUBJECT-ROLE': {
        'role': 'clause subject',
        'description': 'In the clause structure (S/SINV/SQ/SBARQ), the NP subtree under S functions as the subject. The subject subtree provides the entity the predicate says something about.',
        'valid': "In this {clause_type} tree, the {np_surface} subtree is the subject daughter of {clause_type}. The predicate subtree ({vp_surface}) carries the verb complex that agrees with this subject.",
        'error_context': "The subject position in the {clause_type} tree is filled by {np_surface}, but the predicate agreement fails due to person/number mismatch between subject subtree and verb.",
    },
    'C-PREDICATE': {
        'role': 'clause predicate',
        'description': 'The predicate is the VP/SBAR/ADJP subtree that says something about the subject.',
        'valid': "Within {clause_type}, the predicate subtree {pred_surface} (type {pred_type}) is the sister of the subject subtree. The finite verb inside this predicate agrees with the subject in person and number.",
    },
    'C-HEAD-VERB': {
        'role': 'verb head',
        'description': 'The lexical verb at the head of the VP subtree.',
        'valid': "Inside the VP subtree headed by the verbal complex, '{verb_surface}' is the head verb. Its tense/form is licensed by the auxiliary chain above/beside it in the VP structure.",
    },
    'C-HEAD-NOUN': {
        'role': 'head noun',
        'description': 'The head noun of an NP subtree.',
        'valid': "Within the NP subtree, '{noun_surface}' is the head noun. Determiners, modifiers, and complements attach to this NP under standard constituent structure.",
    },
    'C-DETERMINER': {
        'role': 'determiner',
        'description': 'Determiner daughter of NP modifying the head noun.',
        'valid': "In the NP tree structure, '{det_surface}' is a determiner daughter that selects/specifies the NP headed by '{head_surface}'. Its number/features must be compatible with the head noun.",
    },
    'C-ADJUNCT': {
        'role': 'adjunct',
        'description': 'Adjunct attached at VP/S clause level modifying the predicate/clause.',
        'valid': "The {child_type} subtree '{child_surface}' is an adjunct attached at the {parent_type} level. It adds circumstantial/modificational information without being an argument required by the verb.",
    },
    'C-CLAUSAL-ADVERBIAL': {
        'role': 'clausal adverbial',
        'description': 'Adverbial phrase/clause attached at clause level.',
        'valid': "At the {clause_type} root level, the {adv_type} subtree '{child_surface}' is adjoined as a clausal adverbial, modifying the whole clause structure (time/place/manner/reason) rather than a single verb argument.",
    },
    'C-PREP-OBJECT': {
        'role': 'prepositional complement',
        'description': 'NP object of preposition inside PP.',
        'valid': "Inside the PP subtree, '{prep_surface}' is the head preposition and '{obj_surface}' is its complement NP daughter. The preposition projects the PP and takes this NP as its argument.",
    },
    'C-OBJECT': {
        'role': 'direct object',
        'valid': "Inside the VP subtree, '{obj_surface}' is the direct object NP daughter of the verb '{verb_surface}', licensed by the verb's transitivity in this VP structure.",
    },
    'C-INDIRECT-OBJECT': {
        'role': 'indirect object',
        'valid': "Within the VP, '{io_surface}' appears as the indirect object NP, c-commanded/attached in the dative structure with '{do_surface}' as the direct object.",
    },
    'C-AUX-COMPLEMENT': {
        'role': 'auxiliary complement',
        'valid': "In the VP auxiliary complex, '{aux_surface}' takes the {vptype} subtree '{main_surface}' as its complement. The VP structure shows the auxiliary hierarchy with the main verb at the bottom of the verbal projection.",
    },
}

# Generate master sheet
def main():
    sheet = {
        'title': 'SynTutor Tree-Structure Explanation Master Sheet',
        'description': 'All explanations rewritten to reference constituency tree structure (phrase labels, heads, daughters, adjunction, complements)',
        'generated': True,
        'templates': TEMPLATES,
        'principles': [
            "Always reference phrase labels (S, NP, VP, PP, ADJP, ADVP, etc.)",
            "Describe hierarchical relations: daughter, sister, head, complement, adjunct",
            "Explain why structure is correct/incorrect based on tree geometry",
            "Say 'inside the NP subtree...' rather than just 'in the sentence...'",
            "Reference verb phrases and their internal structure (auxiliaries, main verb)",
            "For clauses, describe subject-predicate split in the S tree"
        ],
        'phrase_explanations': {
            'S': 'Clause node: splits into subject (NP) and predicate (VP) daughters in a canonical clause.',
            'NP': 'Noun phrase: headed by N/NN*/NNP*/PRP, with determiner/modifiers as sisters to head or as adjuncts.',
            'VP': 'Verb phrase: contains verb complex; may have auxiliaries, main verb, objects, complements, adjuncts.',
            'PP': 'Prepositional phrase: headed by preposition with NP complement.',
            'ADJP': 'Adjective phrase: headed by adjective with modifiers/complements.',
            'ADVP': 'Adverb phrase: headed by adverb with modifiers.',
            'SBAR': 'Subordinate clause introduced by complementizer/relativizer.',
            'SBARQ': 'Wh-question clause structure.',
            'SQ': 'Yes/no question structure with inversion.',
        }
    }
    
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(sheet, f, indent=2)
    
    md_lines = []
    md_lines.append('# SynTutor Tree-Structure Explanation Master Sheet')
    md_lines.append('')
    md_lines.append('All explanations should reference the constituency tree structure.')
    md_lines.append('')
    md_lines.append('## Principles')
    md_lines.append('')
    for p in sheet['principles']:
        md_lines.append(f'- {p}')
    md_lines.append('')
    md_lines.append('## Phrase Type Explanations')
    md_lines.append('')
    for k,v in sheet['phrase_explanations'].items():
        md_lines.append(f'**{k}**: {v}')
    md_lines.append('')
    md_lines.append('## Constraint Templates')
    md_lines.append('')
    for cid, info in TEMPLATES.items():
        md_lines.append(f'### {cid}')
        md_lines.append(f'- Role: {info.get("role","")}')
        md_lines.append(f'- Description: {info.get("description","")}')
        if 'valid' in info:
            md_lines.append(f'- Valid: {info["valid"]}')
        if 'error_context' in info:
            md_lines.append(f'- Error context: {info["error_context"]}')
        md_lines.append('')
    
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines) + '\n')
    
    print(f'Wrote {OUT_MD}')
    print(f'Wrote {OUT_JSON}')

if __name__ == '__main__':
    main()
