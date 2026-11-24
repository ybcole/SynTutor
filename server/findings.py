"""Unified finding model for legacy and Cambridge candidate channels.

The purpose is coherence, not promotion: every item carries its authority and
claim status. Legacy findings remain legacy diagnostics; candidate findings
remain candidate-only.
"""
from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "unified-findings-1.0.0"


def build_unified_findings(details: dict[str, Any] | None,
                           candidate_xai: dict[str, Any] | None = None) -> dict[str, Any]:
    items = []
    seen = set()
    for node_id, detail in (details or {}).items():
        if not isinstance(detail, dict) or detail.get("status") != "error":
            continue
        remediation = detail.get("remediation") or {}
        finding_span = next((finding['evidence']['token_span'] for finding in detail.get('findings', [])
                             if finding.get('constraint') == detail.get('constraint')
                              and finding.get('evidence', {}).get('token_span')), detail.get('span'))
        key = (detail.get("constraint"), tuple(finding_span or ()))
        if finding_span and key in seen:
            continue
        seen.add(key)
        items.append({
            "finding_id": f"legacy:{node_id}",
            "authority": "legacy_matrix",
            "claim_status": "legacy_diagnostic_not_book_verified",
            "production_path": True,
            "book_verified": False,
            "rule_id": detail.get("constraint"),
            "legacy_node_id": node_id,
            "canonical_node_id": detail.get("canonical_node_id"),
            "canonical_binding": detail.get("canonical_binding"),
            "span": finding_span,
            "surface": detail.get("surface"),
            "violation": remediation.get("violation") or detail.get("text"),
            "suggested_fix": remediation.get("suggested_fix"),
            "alternative_fix": remediation.get("alternative_fix"),
            "remediation": remediation,
        })
    for index, item in enumerate((candidate_xai or {}).get("items") or [], start=1):
        if not isinstance(item, dict):
            continue
        binding = item.get("tree_binding") or {}
        explanation = item.get("explanation") or {}
        items.append({
            "finding_id": f"candidate:{item.get('rule_id')}:{item.get('finding_id') or index}",
            "authority": "cambridge_candidate",
            "claim_status": "candidate_observation_not_verified_error",
            "production_path": False,
            "book_verified": False,
            "rule_id": item.get("rule_id"),
            "canonical_node_id": binding.get("affected_node_id"),
            "canonical_binding": binding,
            "source_chapter": item.get("source_chapter"),
            "source_pages": item.get("source_pages") or [],
            "explanation": explanation,
        })
    by_authority: dict[str, int] = {}
    by_claim: dict[str, int] = {}
    for item in items:
        by_authority[item["authority"]] = by_authority.get(item["authority"], 0) + 1
        by_claim[item["claim_status"]] = by_claim.get(item["claim_status"], 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "production_enabled": False,
        "whole_sentence_certified": False,
        "findings": items,
        "counts": {
            "total": len(items),
            "by_authority": by_authority,
            "by_claim_status": by_claim,
            "legacy": by_authority.get("legacy_matrix", 0),
            "candidate": by_authority.get("cambridge_candidate", 0),
        },
        "caveat": ("Legacy findings are diagnostic and not book-verified. "
                   "Candidate findings are not verified errors. No item here "
                   "authorizes a Cambridge runtime rule."),
    }


# A rule's presence in the matrix result is insufficient. These families
# require corroboration of the specific dependency, constituent, or
# morphological conflict on the actual sentence tokens.
AGREEMENT = {'C-SUBJECT-AGREEMENT', 'C-SUBJ-AGREE-XP', 'C-COORD-SUBJ-AGREE', 'C-RELATIVE-AGREE'}
DETERMINERS = {'C-DETERMINER-AGREEMENT'}
AUXILIARIES = {'C-AUX-FORM', 'C-BE-PAST', 'C-VERB-FORM', 'C-LEXICON-MALFORMED',
               'C-MODAL-VERB-FORM', 'C-MODAL-TO', 'C-MODAL-OF', 'C-MODAL-ABLE',
               'C-MODAL-STACK', 'C-PARTICIPLE'}
CASE = {'C-PRONOUN-CASE', 'C-PREP-PRON-CASE', 'C-COORD-CASE'}
QUANTIFIERS = {'C-QUANTIFIER', 'C-QUANT-PLURAL', 'C-PLURAL-FORM', 'C-QUANTIFIER-CLASS'}
FAMILIES = {
    'subject_verb_agreement': AGREEMENT,
    'determiner_noun_agreement': DETERMINERS,
    'auxiliary_complement': AUXILIARIES,
    'plain_verb_complement': AUXILIARIES,
    'infinitive_to_base': {'C-TO-BASE'},
    'modal_syntax': {'C-MODAL-TO', 'C-MODAL-OF', 'C-MODAL-ABLE', 'C-MODAL-STACK'},
    'pronoun_case': CASE,
    'article_onset': {'C-ARTICLE-MISMATCH'},
    'uncountable_article': {'C-UNCOUNTABLE'},
    'determiner_stacking': {'C-DET-STACK'},
    'quantifier_noun_agreement': QUANTIFIERS,
    'comparative_double': {'C-COMPARATIVE-DOUBLE'},
    'modifier_category': {'C-ADJ-ADV'},
    'reflexive_binding': {'C-REFLEXIVE-ANTECEDENT', 'C-REFLEXIVE-SUBJECT'},
}


def _agreement(index, leaf, head_id, head, dependents, final):
    from matrix import NUMBER_AMBIGUOUS_HEADS, _agreement_ok, subject_key, verb_key
    from ruleset import possible_indefinite_command

    surface = leaf['surface']
    if possible_indefinite_command(leaf, head, final):
        return None
    siblings = dependents.get(head_id, [])
    subj_deps = dependents.get(index, [])
    has_and_conj = (
        any(other.get('fdep') == 'conj' for _, other in subj_deps)
        and any(other.get('fdep') == 'cc' and other['surface'].lower() == 'and' for _, other in subj_deps)
    )
    has_other_conj = any(other.get('fdep') in {'conj', 'cc'} for _, other in subj_deps) and not has_and_conj
    # Quantified ambiguous subjects and non-'and' coordination need broader licensing.
    if (surface.lower() in NUMBER_AMBIGUOUS_HEADS | {'there', 'who', 'what'}
            or has_other_conj
            or any(other.get('fdep') == 'quantmod' for _, other in subj_deps)
            or sum(other.get('fdep') in {'nsubj', 'nsubjpass'} for _, other in siblings) != 1):
        return None
    # Notional measure/amount subjects ('Three eggs is plenty.') stay exempt when
    # a numeral modifies the subject and the predicate is copular 'be'.
    has_nummod = any(other.get('fdep') == 'nummod' for _, other in subj_deps)
    if has_nummod and head['surface'].lower() in {'is', 'was', 'are', 'were'}:
        return None
    carriers = [(i, other) for i, other in siblings if other.get('fdep') in {'aux', 'auxpass'}
                and other.get('type') in {'VBZ', 'VBP', 'VBD', 'MD'}]
    finite_id, finite = min(carriers, default=(head_id, head), key=lambda pair: pair[0])
    finite_low = finite['surface'].lower()
    is_past_be = finite.get('type') == 'VBD' and finite_low in {'was', 'were'}
    if (finite.get('type') not in {'VBP', 'VBZ'} and not is_past_be) or finite.get('ftag') != finite.get('type'):
        return None
    # Subjunctive 'If I were...' / 'If she were...' is grammatical.
    if finite_low == 'were' and any(other.get('fdep') == 'mark' and other['surface'].lower() in {'if', 'as', 'though', 'wish'} for _, other in siblings):
        return None
    if has_and_conj:
        expected = ('3', 'pl')
        conj_ids = [i for i, other in subj_deps if other.get('fdep') == 'conj']
        participants = [index, *conj_ids[:1], finite_id]
    else:
        expected = subject_key(leaf)
        participants = [index, finite_id]
    if is_past_be:
        actual = ('sg_past', 'sg') if finite_low == 'was' else ('pl_past', 'pl')
        if not expected or expected[1] not in {'sg', 'pl', 'non3sg'}:
            return None
        if expected == ('1', 'sg') or expected == ('3', 'sg'):
            matches = finite_low == 'was'
        else:
            matches = finite_low == 'were'
    else:
        actual = verb_key(finite)
        if not expected or not actual or expected[1] not in {'sg', 'pl', 'non3sg'}:
            return None
        matches = _agreement_ok(expected, actual)
    number = 'plural' if has_and_conj else {'sg': 'singular', 'pl': 'plural'}.get(expected[1])
    role = ('coordinated subject' if has_and_conj
            else 'subject' if leaf['type'] == 'PRP' else 'head of the subject')
    description = f'{number} {role}' if number and not has_and_conj else f'plural {role}' if has_and_conj else role
    verb = finite['surface']
    text = f'“{surface}” is the {description} linked to the finite verb “{verb}”.'
    if matches:
        text += ' The verb form agrees with its subject.'
    else:
        text += f' In standard written English, “{verb}” needs a form that agrees with its subject.'
    return {'kind': 'subject_verb_agreement', 'participants': participants,
            'target': finite_id, 'matches': matches, 'text': text, 'lesson': 'agreement',
            'features': {'subject_number': expected[1], 'subject_person': expected[0],
                         'verb_tag': finite['type']}}


def local_relationships(leaves):
    """Describe narrow token relations that can be checked without projection."""
    from matrix import (ADJ_CLASS, A_SOUND_CONST_WORDS, NONCOUNT_NOUNS, NUMBER_AMBIGUOUS_HEADS,
                        _base_form, _indefinite_article, num_of)
    from ruleset import (BE_SURFACES_LEAF, HAVE_FORM, MODAL_SURFACES, PAST_ONLY,
                         PRONOUN_OBJECT_TO_SUBJECT, PRONOUN_SUBJECT_TO_OBJECT, bare_be_voice)
    from spellcheck import known_word

    final = leaves[max(leaves)] if leaves else {}
    dependents = {}
    for index, leaf in leaves.items():
        if leaf.get('fhead') != index:
            dependents.setdefault(leaf.get('fhead'), []).append((index, leaf))
    _PREDETS = {'all', 'both', 'half', 'such', 'what', 'quite', 'rather', 'many'}
    _DETS_STRICT = {'a', 'an', 'the', 'this', 'that', 'these', 'those', 'every', 'each', 'some', 'any', 'no', 'another'}
    _REFLEXIVES = {'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves'}

    for index, leaf in leaves.items():
        head_id = leaf.get('fhead')
        head = leaves.get(head_id)
        surface = leaf['surface']
        word = surface.lower().replace('’', "'")
        dep, tag = leaf.get('fdep'), leaf.get('type')

        # Modal syntax checks depend on adjacent tokens and must run even when
        # the modal itself is spaCy ROOT ('She must to leave now.').
        if tag == 'MD' and word in MODAL_SURFACES:
            nxt = leaves.get(index + 1)
            if nxt is not None:
                nlow = nxt['surface'].lower()
                if nlow == 'to' and nxt.get('type') == 'TO':
                    yield {'kind': 'modal_syntax', 'participants': [index, index + 1],
                           'target': index + 1, 'matches': False,
                           'text': f'The modal auxiliary “{surface}” connects directly to a plain verb without “to”.',
                           'lesson': 'auxiliary'}
                elif nlow == 'of':
                    yield {'kind': 'modal_syntax', 'participants': [index, index + 1],
                           'target': index + 1, 'matches': False,
                           'text': f'After the modal “{surface}”, use the auxiliary “have” rather than “of”.',
                           'lesson': 'auxiliary'}
                elif nxt.get('type') == 'MD' and nlow in MODAL_SURFACES:
                    yield {'kind': 'modal_syntax', 'participants': [index, index + 1],
                           'target': index + 1, 'matches': False,
                           'text': f'Standard English uses only one central modal per clause, not “{surface} {nxt["surface"]}”.',
                           'lesson': 'auxiliary'}

        # 7a. Auxiliary 'be' followed directly by a finite 3sg verb ('She is sleeps today.')
        # Must run before the head_id == index skip because spaCy often makes 'is' ROOT
        # and tags 'sleeps' as attr/NOUN when Benepar parses (VP (VBZ is) (VP (VBZ sleeps))).
        if word in BE_SURFACES_LEAF:
            nxt = leaves.get(index + 1)
            if (nxt is not None and nxt.get('type') == 'VBZ'
                    and nxt['surface'].lower() not in BE_SURFACES_LEAF):
                yield {'kind': 'auxiliary_complement', 'participants': [index, index + 1],
                       'target': index + 1, 'matches': False,
                       'text': f'After the auxiliary “{surface}”, use an -ing participle or past participle rather than the finite form “{nxt["surface"]}”.',
                       'lesson': 'auxiliary'}
            for verb_id, verb in dependents.get(index, ()):
                bare = verb['surface'].lower()
                if (verb_id > index and verb.get('fdep') == 'acomp'
                        and verb.get('type') in {'VB', 'VBP'} and verb.get('type') == verb.get('ftag')
                        and known_word(bare) and _base_form(verb) == bare):
                    yield {'kind': 'auxiliary_complement', 'participants': [index, verb_id],
                           'target': verb_id, 'matches': False,
                           'text': (f'“{verb["surface"]}” is the plain form after “{surface}”. '
                                    'The progressive uses an -ing form and the passive uses a past participle.'),
                           'lesson': 'auxiliary'}

        if head is None or head_id == index:
            continue
        governor = head['surface']
        head_word = governor.lower()
        head_deps = dependents.get(head_id, [])

        # Infinitival 'to' + non-base verb ('decided to stays', 'tried to went', 'asked me to lent')
        if (dep == 'aux' and word == 'to' and tag == 'TO'
                and head.get('type') in {'VB', 'VBZ', 'VBP', 'VBD'}):
            base = _base_form(head)
            if (head.get('type') in {'VBZ', 'VBD'} and head.get('ftag') == head.get('type')
                    and (head.get('type') != 'VBD' or head_word in PAST_ONLY)) \
                    or (head.get('type') == 'VBP' and head.get('ftag') == 'VBP' and head_word != base) \
                    or (head_word in PAST_ONLY and base != head_word):
                yield {'kind': 'infinitive_to_base', 'participants': [index, head_id],
                       'target': head_id, 'matches': False,
                       'text': f'After the infinitive marker “to”, use the plain (base) form “{base}” rather than “{governor}”.',
                       'lesson': 'infinitive'}

        # 1. Subject-verb agreement (present VBP/VBZ + past 'was'/'were')
        if dep in {'nsubj', 'nsubjpass'} and tag in {'NN', 'NNS', 'NNP', 'NNPS', 'PRP'}:
            relation = _agreement(index, leaf, head_id, head, dependents, final)
            if relation:
                yield relation

        # 2. Determiner-noun number agreement (demonstratives, 'a'/'an', 'every'/'each')
        if (dep == 'det' and word in {'this', 'that', 'these', 'those', 'a', 'an', 'every', 'each'}
                and tag == 'DT' and head.get('type') in {'NN', 'NNS'}
                and head.get('ftag') == head.get('type')
                and head_word not in NUMBER_AMBIGUOUS_HEADS
                and not any(other.get('fdep') == 'conj' for _, other in head_deps)):
            # Exempt 'a few boxes', 'a dozen eggs', 'a lot of books'
            has_quant_bridge = (word in {'a', 'an'} and any(
                other['surface'].lower() in {'few', 'dozen', 'hundred', 'thousand', 'million', 'couple', 'lot', 'number', 'great'}
                for i2, other in head_deps if index < i2 < head_id
            ))
            if not has_quant_bridge:
                singular = word in {'this', 'that', 'a', 'an', 'every', 'each'}
                head_num = num_of(head)
                if head_num in {'sg', 'pl'}:
                    matches = singular == (head_num == 'sg')
                    text = (f'“{surface}” selects a {"singular" if singular else "plural"} noun. '
                            f'It determines “{governor}”, which is {"singular" if head_num == "sg" else "plural"} here.')
                    # When indefinite 'a'/'an' governs a plural noun ('a test tubes'),
                    # the edited error token is the plural noun ('tubes' -> 'tube') and
                    # the determiner 'a'/'an' is the governing evidence.
                    det_target = head_id if (word in {'a', 'an'} and head_num == 'pl') else index
                    yield {'kind': 'determiner_noun_agreement', 'participants': [index, head_id],
                           'target': det_target, 'matches': matches, 'text': text, 'lesson': 'determiner'}

        # 3. Indefinite article a/an onset phonology
        if dep == 'det' and tag == 'DT' and word in {'a', 'an'} and head.get('type') == 'NN':
            onset = leaves.get(index + 1, {})
            next_word = onset.get('surface', '')
            if (next_word.isascii() and next_word.isalpha() and next_word.islower()
                    and (index + 1 == head_id or onset.get('fhead') == head_id
                         and onset.get('fdep') == 'amod')
                    and next_word not in {'herb', 'homage'}
                    and (not next_word.startswith(('u', 'eu')) or next_word in A_SOUND_CONST_WORDS)
                    and known_word(next_word)):
                expected = _indefinite_article(next_word)
                sound = 'vowel' if expected == 'an' else 'consonant'
                yield {'kind': 'article_onset', 'participants': [index, index + 1],
                       'target': index, 'matches': word == expected,
                       'text': f'“{next_word}” starts with a {sound} sound here, so it takes “{expected}”.',
                       'lesson': 'determiner'}

        # 4. Uncountable noun with indefinite article ('an information', 'a furniture')
        if (dep == 'det' and tag == 'DT' and word in {'a', 'an'}
                and head.get('type') == 'NN' and head_word in NONCOUNT_NOUNS):
            yield {'kind': 'uncountable_article', 'participants': [index, head_id],
                   'target': index, 'matches': False,
                   'text': f'“{governor}” is used as an uncountable noun here and does not take the indefinite article “{surface}”.',
                   'lesson': 'determiner'}

        # 5. Determiner stacking ('my the book', 'some my jobs', 'the the things')
        if dep in {'det', 'poss'} and (tag == 'PRP$' or (tag == 'DT' and word in _DETS_STRICT)):
            other_dets = [
                (i2, other) for i2, other in head_deps
                if i2 < index and other.get('fdep') in {'det', 'poss'}
                and (other.get('type') == 'PRP$'
                     or (other.get('type') == 'DT' and other['surface'].lower() in _DETS_STRICT
                         and other['surface'].lower() not in _PREDETS))
            ]
            if other_dets and head.get('type') in {'NN', 'NNS'}:
                first_i, first_det = other_dets[0]
                yield {'kind': 'determiner_stacking', 'participants': [first_i, index, head_id],
                       'target': index, 'matches': False,
                       'text': f'“{first_det["surface"]}” and “{surface}” both occupy the determiner slot before “{governor}”; use only one determiner here.',
                       'lesson': 'determiner'}

        # 6. Quantifier / numeral-noun agreement ('five book', 'many water', 'less books', 'a few girlfriend')
        if (dep in {'amod', 'nummod', 'det'} and head.get('type') in {'NN', 'NNS'}
                and head.get('ftag') == head.get('type')
                and head_word not in NUMBER_AMBIGUOUS_HEADS):
            head_num = num_of(head)
            if word in {'many', 'few', 'fewer', 'several'} and head_num == 'sg':
                if head_word in NONCOUNT_NOUNS:
                    paired = {'many': 'much', 'few': 'little', 'fewer': 'less', 'several': 'some'}[word]
                    yield {'kind': 'quantifier_noun_agreement', 'participants': [index, head_id],
                           'target': index, 'matches': False,
                           'text': f'“{surface}” pairs with plural countable nouns, but “{governor}” is uncountable here; use “{paired}”.',
                           'lesson': 'quantifier'}
                else:
                    yield {'kind': 'quantifier_noun_agreement', 'participants': [index, head_id],
                           'target': head_id, 'matches': False,
                           'text': f'“{surface}” selects a plural countable noun, so “{governor}” needs its plural form.',
                           'lesson': 'quantifier'}
            elif (word in {'much', 'little', 'less'} and head_num == 'pl'
                  and (word != 'little' or (dep == 'det' and leaf.get('ftag') not in ADJ_CLASS))):
                paired = {'much': 'many', 'little': 'few', 'less': 'fewer'}[word]
                yield {'kind': 'quantifier_noun_agreement', 'participants': [index, head_id],
                       'target': index, 'matches': False,
                       'text': f'“{surface}” pairs with uncountable nouns, but “{governor}” is a plural countable noun; use “{paired}”.',
                       'lesson': 'quantifier'}
            elif tag == 'CD' and word not in {'one', '1', '0', 'zero', 'half', 'quarter'} and head_num == 'sg' and head_word not in NONCOUNT_NOUNS:
                # Exclude compound modifiers ('a five dollar bill') where head has another noun governor
                if head.get('fdep') != 'compound':
                    yield {'kind': 'quantifier_noun_agreement', 'participants': [index, head_id],
                           'target': head_id, 'matches': False,
                           'text': f'The plural numeral “{surface}” selects a plural countable noun, so “{governor}” should be plural.',
                           'lesson': 'quantifier'}

        # 7. Auxiliary-verb complement & modal syntax
        if dep in {'aux', 'auxpass'} and not any(
                index < i < head_id and other.get('fdep') in {'aux', 'auxpass'}
                for i, other in head_deps):
            if (word in BE_SURFACES_LEAF | HAVE_FORM and head_word in PAST_ONLY
                    and head.get('type') in {'VBD', 'VBN'}):
                agents = [i for i, other in head_deps
                          if other.get('fdep') == 'agent' and other['surface'].lower() == 'by']
                passive = word in BE_SURFACES_LEAF and dep == 'auxpass' and bool(agents)
                expected = ('an -ing form in the progressive or a past participle in the passive'
                            if word in BE_SURFACES_LEAF else 'a past participle in the perfect')
                if passive:
                    expected = 'a past participle in this passive construction (the by-phrase names the agent)'
                yield {'kind': 'auxiliary_complement', 'participants': [index, head_id, *agents],
                       'target': index if word in BE_SURFACES_LEAF and not passive else head_id,
                       'matches': False,
                       'text': f'“{governor}” is a simple past form. Auxiliary “{surface}” takes {expected}.',
                       'lesson': 'auxiliary'}
            elif (word in BE_SURFACES_LEAF and index < head_id
                    and head.get('type') in {'VB', 'VBP'} and head.get('ftag') == head.get('type')
                    and known_word(head_word) and _base_form(head) == head_word):
                voice = bare_be_voice(leaf, head, (other for _, other in head_deps))
                expected = ('a past participle in this passive construction' if voice == 'passive'
                            else 'an -ing form in the progressive or a past participle in the passive')
                agents = [i for i, other in head_deps
                          if voice == 'passive' and other.get('fdep') == 'agent'
                          and other['surface'].lower() == 'by']
                yield {'kind': 'auxiliary_complement', 'participants': [index, head_id, *agents],
                       'target': head_id, 'matches': False,
                       'text': (f'“{governor}” is in the plain form. Auxiliary “{surface}” takes '
                                f'{expected}.'),
                       'lesson': 'auxiliary'}
            elif ((word in MODAL_SURFACES and tag == 'MD' or word in {'do', 'does', 'did'})
                    and head.get('type') in {'VB', 'VBP', 'VBZ', 'VBD', 'VBG'}
                  and head.get('ftag') == head.get('type')
                  and (head.get('type') != 'VBD' or head_word in PAST_ONLY)):
                base = _base_form(head)
                auxiliary = 'a modal auxiliary' if tag == 'MD' else 'an auxiliary'
                yield {'kind': 'plain_verb_complement', 'participants': [index, head_id],
                       'target': head_id, 'matches': head_word == base,
                       'text': (f'“{surface}” is {auxiliary} and selects the plain form “{base}”.'
                                + (f' “{governor}” has a different form.' if head_word != base else '')),
                       'lesson': 'auxiliary'}
        # 7b. Modals handled above even when ROOT.
        # 8. Double comparative ('more taller', 'most tallest')
        if (word in {'more', 'most'} and head.get('type') in {'JJR', 'JJS'}
                and index < head_id):
            yield {'kind': 'comparative_double', 'participants': [index, head_id],
                   'target': index, 'matches': False,
                   'text': f'“{governor}” already marks comparison with its ending, so “{surface}” repeats the comparison.',
                   'lesson': 'comparative'}

        # 9. Pronoun case ('Me saw him', 'with he')
        if dep in {'dobj', 'pobj', 'nsubj', 'nsubjpass'} and tag == 'PRP':
            subject = dep.startswith('nsubj')
            forms = PRONOUN_OBJECT_TO_SUBJECT if subject else PRONOUN_SUBJECT_TO_OBJECT
            nonfinite = (head.get('type') in {'VB', 'VBG', 'VBN'} and (
                any(n['surface'].lower() == 'to' and n.get('fdep') in {'aux', 'mark'} for _, n in head_deps)
                or (head.get('type') in {'VB', 'VBG'}
                    and head.get('fdep') in {'xcomp', 'ccomp'})))
            if word in forms and not (subject and nonfinite):
                role = 'subject' if subject else 'object'
                yield {'kind': 'pronoun_case', 'participants': [index, head_id],
                       'target': index, 'matches': False,
                       'text': f'“{surface}” is in a {role} position linked to “{governor}”. Standard written English uses “{forms[word]}” in this position.',
                       'lesson': 'pronoun'}

        # 10. Reflexive pronoun in subject position ('Himself left.')
        if dep in {'nsubj', 'nsubjpass'} and word in _REFLEXIVES:
            yield {'kind': 'reflexive_binding', 'participants': [index, head_id],
                   'target': index, 'matches': False,
                   'text': (f'The reflexive “{surface}” has no local antecedent in this clause '
                            f'and cannot stand alone as the subject of “{governor}”.'),
                   'lesson': 'pronoun'}


def _evidence_token_ids(evidence, nodes, tokens, fallback_span):
    """Extract witnessed parser token indices from a rule finding's evidence."""
    ids = []
    for key in ('supporting', 'conflict'):
        for item in (evidence or {}).get(key) or []:
            nid = item.get('node') if isinstance(item, dict) else None
            nd = nodes.get(nid) if nid else None
            sp = nd.get('span') if isinstance(nd, dict) else None
            if sp and len(sp) == 2 and sp[0] < sp[1] and sp[0] in tokens:
                ids.append(sp[0])
    if not ids and fallback_span and len(fallback_span) == 2 and fallback_span[0] in tokens:
        ids.append(fallback_span[0])
    return sorted(set(ids))


# Map structural / morphological constraint families whose findings are accepted
# ONLY when corroborated by explicit structural, dependency, or lexicon witnesses.
_STRUCTURAL_LESSON_MAP = {
    'C-ARTICLE': 'determiner',
    'C-NOUN-FORM': 'morphology',
    'C-VERB-FORM': 'auxiliary',
    'C-VERB-ENDING': 'morphology',
    'C-ADVERB-FORM': 'modifier',
    'C-COMPARATIVE-FORM': 'comparative',
    'C-ADJ-ADV': 'modifier',
    'C-REFLEXIVE-FORM': 'pronoun',
    'C-REFLEXIVE-ANTECEDENT': 'pronoun',
    'C-REFLEXIVE-SUBJECT': 'pronoun',
    'C-NPI-LICENSING': 'negation',
    'C-DOUBLE-NEG': 'negation',
    'C-SUPERLATIVE-QUANT': 'quantifier',
    'C-EXISTENTIAL-DEFINITENESS': 'quantifier',
    'C-RAISING-CONTROL': 'clause',
    'C-TOUGH-COMPLEMENT': 'clause',
    'C-ELLIPSIS-HEAD': 'determiner',
    'C-INTRANSITIVE-OBJECT': 'transitivity',
    'C-INTRANSITIVE-PASSIVE': 'transitivity',
    'C-MISSING-OBJECT': 'transitivity',
    'C-STRANDED-PREP': 'preposition',
    'C-WH-ISLAND': 'island',
    'C-ADJUNCT-ISLAND': 'island',
    'C-COMPLEX-NP-ISLAND': 'island',
    'C-LEFT-BRANCH-ISLAND': 'island',
    'C-COORD-ISLAND': 'island',
    'C-FILLED-GAP': 'island',
    'C-QUESTION-INVERSION': 'question',
    'C-INDIRECT-Q-ORDER': 'question',
    'C-DO-MODAL': 'auxiliary',
    'C-DET-ORDER': 'determiner',
    'C-ARTICLE-ORDER': 'determiner',
    'C-DEGREE-ORDER': 'modifier',
    'C-PLACEMENT-COMPLEMENT': 'transitivity',
    'C-TRANSITIVITY': 'transitivity',
    'C-VERB-CLAUSE-PATTERN': 'infinitive',
    'C-RELATIVE-PRONOUN': 'relative',
    'C-MODAL-VERB-FORM': 'auxiliary',
    'C-COMMA-SPLICE': 'punctuation',
    'C-TIME-PLACE-PREP': 'preposition',
    'C-PREP-CHOICE': 'preposition',
    'C-WRONG-PREPOSITION': 'preposition',
    'C-MISSING-PREP': 'preposition',
    'C-EXTRA-PREP': 'preposition',
    'C-ADJ-PREP': 'preposition',
    'C-PREP-GERUND': 'infinitive',
    'C-TO-BASE': 'infinitive',
    'C-CAUSATIVE-TO': 'infinitive',
    'C-GERUND-INFINITIVE': 'infinitive',
    'C-GERUND-INFIN': 'infinitive',
    'C-SPACING-REPEAT': 'spelling',
    'C-TO_TOO': 'spelling',
    'C-PARALLEL': 'coordination',
    'C-CORRELATIVE-AGREE': 'coordination',
    'C-MODAL-ABLE': 'auxiliary',
    'C-PASSIVE': 'voice',
    'C-STATIVE-PROGRESSIVE': 'aspect',
    'C-STATIVE-PROG': 'aspect',
    'C-VBN-SIMPLE-PAST': 'auxiliary',
    'C-WAS-WERE': 'agreement',
    'C-EXISTENTIAL': 'agreement',
    'C-EXISTENTIAL-VERB': 'agreement',
    'C-INDEF-AGREE': 'agreement',
    'C-INDEFINITE-AGREE': 'agreement',
    'C-PLURAL-ONLY': 'determiner',
    'C-COUNT-MASS': 'quantifier',
    'C-RESUMPTIVE-RELATIVE': 'relative',
    'C-INDIRECT-WH-INVERSION': 'question',
    'C-CONDITIONAL-WILL': 'conditional',
    'C-DOUBLE-NEGATIVE': 'negation',
    'C-DOUBLE-SUBJECT': 'clause',
    'C-COPULA': 'predicative',
    'C-FINITE-VERB': 'clause',
    'C-RUNON': 'punctuation',
    'C-MOD-POS': 'modifier',
    'C-ADJ-ORDER': 'modifier',
    'C-INTENSIFIER': 'modifier',
    'C-COMPARATIVE-STRUCT': 'comparative',
    'C-POSSESSIVE-S': 'determiner',
    'C-REDUNDANCY': 'modifier',
    'C-NUMERAL': 'quantifier',
}


def supported_findings(analysis, details):
    """Validate matrix findings against witnessed tokens before learner display.

    A rule code alone is NEVER enough to promote a finding into learner_analysis:
    every accepted finding must be corroborated by either (a) an independently
    verified local dependency/morphological relationship, (b) a verified
    lexicon/morphology/contraction/spelling table witness on the exact token,
    or (c) an explicit structural tree witness pointing to real tokens in the
    sentence.
    """
    from matrix import BARE_ARG_NOUNS, NONCOUNT_NOUNS, _noun_form_issue
    from ruleset import (ADVERB_FIX, CONTRACTIONS, IRREGULAR_COMPARATIVE,
                         IRREGULAR_PART_REGULARIZED, ORAL_PAST_REGULARIZED,
                         REFLEXIVE_FIX, SPELLING_FIX, VERB_ENDING_FIX,
                         _check_terminal)
    from spellcheck import has_name_evidence, strong_typo_candidate

    nodes = analysis.get('nodes')
    if not isinstance(nodes, dict):
        return [], [], {}
    tokens = {token['i']: token for token in analysis['tokens']}
    leaves = {node['span'][0]: node for node in nodes.values()
              if not node.get('children') and not node.get('punct')
              and node.get('span', [None])[0] in tokens
              and node.get('surface') == tokens[node['span'][0]]['t']}
    relations = list(local_relationships(leaves))
    rows, seen = [], set()
    for detail in details.values():
        if not isinstance(detail, dict) or detail.get('status') != 'error':
            continue
        span = detail.get('span')
        if (not span or len(span) != 2 or span[0] >= span[1]
                or span[0] not in tokens or span[1] - 1 not in tokens):
            continue
        stored = [row for row in detail.get('findings', []) if row.get('status') == 'error'
                  and row.get('node_id') == detail.get('id')]
        for finding in [*stored, detail]:
            code = finding.get('constraint')
            evidence = finding.get('evidence') or {}
            remediation = finding.get('remediation') or {}
            text = remediation.get('violation') or finding.get('text')
            if not text:
                continue
            targets, participants, lesson = [], [], None
            matches = [
                r for r in relations
                if not r['matches'] and code in FAMILIES[r['kind']]
                and (
                    span[0] <= r['target'] < span[1]
                    or (r['kind'] in {'uncountable_article', 'modal_syntax', 'quantifier_noun_agreement', 'determiner_stacking',
                                      'determiner_noun_agreement', 'auxiliary_complement', 'plain_verb_complement'}
                        and any(span[0] <= p < span[1] for p in r['participants']))
                )
            ]
            target_node = nodes.get(evidence.get('target_node'))
            if code in AGREEMENT and target_node:
                target_idx = target_node['span'][0]
                witnesses = _evidence_token_ids(evidence, nodes, tokens, span)
                if target_idx not in leaves or not witnesses:
                    continue
                targets, participants, lesson = [target_idx], witnesses, 'agreement'
            elif len(matches) == 1:
                relation = matches[0]
                targets, participants = [relation['target']], relation['participants']
                text, lesson = relation['text'], relation['lesson']
            elif code == 'C-CONTRACTION' and evidence.get('source') == 'contraction table':
                local = evidence.get('token_span') or span
                if len(local) != 2 or not (local[0] <= span[0] < local[1] <= span[1]):
                    continue
                targets = [i for i in range(*local) if i in leaves]
                lookup = ''.join(tokens[i]['t'] for i in targets).lower()
                if lookup not in CONTRACTIONS or not targets:
                    continue
                witness = leaves.get(span[0], {}).get('negative_contraction') or {}
                related = nodes.get(witness.get('verb'))
                participants = [related['span'][0]] if related else []
                lesson = 'negation' if CONTRACTIONS[lookup].endswith("n't") else None
            elif code == 'C-FRAGMENT' and evidence.get('rule') == 'subordinator plus S without a matrix clause':
                if analysis['root'].get('type') != 'SBAR' or detail.get('id') != analysis['root'].get('id'):
                    continue
                participants = [span[0]]
                lesson = 'clause'
            elif code in {'C-SPELLING', 'C-LEXICON-MALFORMED'} and span[1] == span[0] + 1:
                leaf = leaves.get(span[0])
                if not leaf or has_name_evidence(leaf):
                    continue
                word = leaf['surface']
                source = evidence.get('source', '')
                if source == 'spelling table' and code == 'C-SPELLING':
                    expected = SPELLING_FIX.get(word.lower())
                elif source == 'spelling dictionary' or (code == 'C-LEXICON-MALFORMED'
                      and source.startswith('forms of ') and leaf.get('ftag') == leaf.get('type')):
                    expected = strong_typo_candidate(word)
                    # Also accept morphologically proven pluralized comparative adjectives ('smallers', 'olders')
                    if not expected and code == 'C-LEXICON-MALFORMED' and word.lower().endswith('ers') and len(word) >= 6:
                        stem = word.lower()[:-1]
                        if stem in evidence.get('accepted', []):
                            expected = stem
                else:
                    expected = None
                if (not expected and code == 'C-LEXICON-MALFORMED' and source.startswith('forms of ')
                        and '(VBN)' in source and len(evidence.get('accepted', [])) == 1):
                    aux_ids = [i for i, o in leaves.items()
                               if o.get('fhead') == span[0] and o.get('fdep') in {'aux', 'auxpass'}]
                    gov_id = leaf.get('fhead')
                    gov_leaf = leaves.get(gov_id)
                    if (not aux_ids and gov_leaf is not None and gov_id != span[0]
                            and gov_leaf['surface'].lower() in {
                                'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                                'has', 'have', 'had', 'get', 'gets', 'got',
                            }):
                        aux_ids = [gov_id]
                    if aux_ids:
                        expected = evidence['accepted'][0]
                        participants = aux_ids
                if not expected or expected not in evidence.get('accepted', []):
                    continue
                targets = [span[0]]
                lesson = 'spelling' if code == 'C-SPELLING' else 'morphology'
                text = f'“{word}” appears to be malformed or misspelled here. The form “{expected}” fits this position.'
            elif code == 'C-TERMINAL-PUNCT' and detail.get('id') == analysis['root'].get('id'):
                if not _check_terminal(analysis['root'], analysis['sentence']):
                    continue
                lesson = 'punctuation'
            elif code == 'C-ARTICLE' and span[1] == span[0] + 1:
                # Corroborate bare singular countable noun without determiner/possessive/numeral
                leaf = leaves.get(span[0])
                if (not leaf or leaf.get('type') != 'NN' or leaf.get('ftag') != 'NN'
                        or has_name_evidence(leaf)
                        or leaf['surface'].lower() in NONCOUNT_NOUNS | BARE_ARG_NOUNS):
                    continue
                has_det = any(
                    other.get('fhead') == span[0] and other.get('fdep') in {'det', 'poss', 'nummod', 'predet'}
                    for other in leaves.values()
                )
                if has_det:
                    continue
                targets = [span[0]]
                gov = leaf.get('fhead')
                participants = [gov] if gov in leaves and gov != span[0] else []
                parent = nodes.get(detail.get('parent'), {})
                parent_span = parent.get('span')
                # Inserting a determiner before a premodifier changes the
                # phrase, while the head noun remains the error target.
                if parent.get('type') == 'NP' and parent_span:
                    for edit in remediation.get('edits') or []:
                        anchor = nodes.get(edit.get('node'), {}).get('span')
                        if (edit.get('insert_before') and anchor
                                and anchor[0] == parent_span[0] < span[0]
                                and anchor[0] in leaves):
                            participants.append(anchor[0])
                lesson = 'determiner'
            elif code == 'C-NOUN-FORM' and span[1] == span[0] + 1:
                leaf = leaves.get(span[0])
                if not leaf or _noun_form_issue(leaf) is None:
                    continue
                targets = [span[0]]
                lesson = 'morphology'
            elif code in {'C-VERB-FORM', 'C-VERB-ENDING', 'C-ADVERB-FORM', 'C-COMPARATIVE-FORM', 'C-REFLEXIVE-FORM'} and span[1] == span[0] + 1:
                leaf = leaves.get(span[0])
                if not leaf or has_name_evidence(leaf):
                    continue
                low = leaf['surface'].lower()
                wl_ok = (
                    (code == 'C-VERB-FORM' and (low in ORAL_PAST_REGULARIZED or low in IRREGULAR_PART_REGULARIZED or evidence.get('rule')))
                    or (code == 'C-VERB-ENDING' and low in VERB_ENDING_FIX)
                    or (code == 'C-ADVERB-FORM' and low in ADVERB_FIX)
                    or (code == 'C-COMPARATIVE-FORM' and low in IRREGULAR_COMPARATIVE)
                    or (code == 'C-REFLEXIVE-FORM' and low in REFLEXIVE_FIX)
                )
                if not wl_ok:
                    continue
                targets = [span[0]]
                gov = leaf.get('fhead')
                participants = [gov] if gov in leaves and gov != span[0] else []
                lesson = _STRUCTURAL_LESSON_MAP.get(code)
            elif code == 'C-ADJ-ADV' and span[0] in leaves:
                leaf = leaves.get(span[0])
                if not leaf or leaf.get('type') not in {'JJ', 'JJR', 'JJS', 'RB'}:
                    continue
                gov = leaf.get('fhead')
                gov_leaf = leaves.get(gov)
                if not gov_leaf or not gov_leaf.get('type', '').startswith('VB'):
                    continue
                targets = list(range(span[0], span[1]))
                participants = [gov]
                lesson = 'modifier'
            elif code == 'C-SPACING-REPEAT' and span[0] in leaves and span[0] - 1 in leaves:
                if leaves[span[0]]['surface'].lower() != leaves[span[0] - 1]['surface'].lower():
                    continue
                targets = [span[0]]
                participants = [span[0] - 1]
                lesson = 'spelling'
            elif code == 'C-TIME-PLACE-PREP' and span[0] in leaves and span[0] - 1 in leaves:
                if leaves[span[0] - 1]['surface'].lower() not in {'in', 'on', 'at'}:
                    continue
                targets = [span[0] - 1]
                participants = [span[0]]
                lesson = 'preposition'
            elif code == 'C-COMMA-SPLICE' and span[0] in tokens and tokens[span[0]]['t'] == ',':
                if not evidence.get('rule'):
                    continue
                targets = [span[0]]
                lesson = 'punctuation'
            elif code in {
                'C-NPI-LICENSING', 'C-DOUBLE-NEG', 'C-DOUBLE-NEGATIVE',
                'C-SUPERLATIVE-QUANT', 'C-EXISTENTIAL-DEFINITENESS',
                'C-EXISTENTIAL', 'C-EXISTENTIAL-VERB',
                'C-RAISING-CONTROL', 'C-TOUGH-COMPLEMENT', 'C-ELLIPSIS-HEAD',
                 'C-INTRANSITIVE-OBJECT', 'C-INTRANSITIVE-PASSIVE',
                 'C-PLACEMENT-COMPLEMENT', 'C-TRANSITIVITY', 'C-DO-MODAL',
                 'C-DET-ORDER', 'C-ARTICLE-ORDER', 'C-DEGREE-ORDER',
                 'C-VERB-CLAUSE-PATTERN', 'C-RELATIVE-PRONOUN', 'C-MODAL-VERB-FORM',
                'C-STRANDED-PREP',
                'C-WH-ISLAND', 'C-ADJUNCT-ISLAND', 'C-COMPLEX-NP-ISLAND',
                'C-LEFT-BRANCH-ISLAND', 'C-COORD-ISLAND', 'C-FILLED-GAP',
                'C-QUESTION-INVERSION', 'C-INDIRECT-Q-ORDER', 'C-INDIRECT-WH-INVERSION',
                'C-REFLEXIVE-ANTECEDENT', 'C-RELATIVE-AGREE', 'C-RESUMPTIVE-RELATIVE',
                'C-PARALLEL', 'C-CORRELATIVE-AGREE', 'C-MODAL-ABLE',
                'C-TO-BASE', 'C-CAUSATIVE-TO', 'C-GERUND-INFINITIVE', 'C-GERUND-INFIN',
                'C-PREP-GERUND', 'C-ADJ-PREP', 'C-PREP-CHOICE', 'C-WRONG-PREPOSITION',
                'C-MISSING-PREP', 'C-EXTRA-PREP', 'C-PLURAL-ONLY', 'C-COUNT-MASS',
                'C-PASSIVE', 'C-STATIVE-PROGRESSIVE', 'C-STATIVE-PROG',
                'C-VBN-SIMPLE-PAST', 'C-WAS-WERE', 'C-CONDITIONAL-WILL',
                'C-DOUBLE-SUBJECT', 'C-COPULA', 'C-FINITE-VERB', 'C-RUNON',
                'C-MOD-POS', 'C-ADJ-ORDER', 'C-INTENSIFIER', 'C-COMPARATIVE-STRUCT',
                'C-POSSESSIVE-S', 'C-INDEF-AGREE', 'C-INDEFINITE-AGREE',
                'C-TO_TOO', 'C-REDUNDANCY', 'C-NUMERAL',
            }:
                # Require explicit structural tree or wordlist witness attached by
                # ruleset.py — fabricated details without real evidence are rejected.
                if not (isinstance(evidence, dict) and (evidence.get('rule') or evidence.get('source'))):
                    continue
                # Guard: do not misdiagnose a missing-apostrophe contraction clause
                # ('If you dont know.') as C-FINITE-VERB when negative_contraction
                # already witnesses an auxiliary + lexical verb.
                if code == 'C-FINITE-VERB' and any(
                        lf.get('negative_contraction') for lf in leaves.values()
                        if span[0] <= lf.get('span', [0])[0] < span[1]):
                    continue
                ev_ids = _evidence_token_ids(evidence, nodes, tokens, span)
                if not ev_ids:
                    continue
                if span[1] == span[0] + 1 and span[0] in tokens:
                    targets = [span[0]]
                    participants = [i for i in ev_ids if i != span[0]]
                else:
                    targets = [ev_ids[0]]
                    participants = ev_ids[1:]
                lesson = _STRUCTURAL_LESSON_MAP.get(code)
            else:
                continue
            key = (lesson or code, tuple(targets), tuple(participants))
            target_key = (code, tuple(targets))
            text_key = (code, text) if code not in {'C-SPELLING', 'C-SPACING-REPEAT'} else None
            if key in seen or target_key in seen or (text_key is not None and text_key in seen):
                continue
            seen.add(key)
            seen.add(target_key)
            if text_key is not None:
                seen.add(text_key)
            rows.append({'id': f'local-{len(rows) + 1}', 'constraint': code,
                         'authority': 'legacy_matrix', 'status': 'supported_local', 'book_verified': False,
                         'node_id': detail.get('id'), 'text': text,
                         'target_token_ids': targets,
                         'target_char_spans': [[tokens[i]['start'], tokens[i]['end']] for i in targets],
                         'related_token_ids': [i for i in participants if i not in targets],
                         'lesson': lesson})
    return rows, relations, leaves
