"""SynTutor Stage 5: deterministic Linguistic Constraint Matrix (XAI).

Every parent/child edge E(v_d, v_p) is validated against a hand-authored rule
matrix. A rule fires on a POS-class pair (parent, child) and returns a verdict:

    valid    -> the dependency is licensed by rule R
    error    -> a specific violation, identified by constraint id C-*
    unlisted -> the pair is not captured by the matrix (valid-by-default)

Agreement, auxiliary-form, tense/finiteness, determiner-number, modifier-order
and determiner-stacking checks are deterministic feature functions over the
Penn-style POS tags produced by benepar -- no machine-learned scoring is
involved. The same input always yields the same verdict.
"""

SENTENCE_CLASSES = {'S', 'SINV', 'SQ', 'SBARQ', 'FRAG', 'ROOT'}

NOUN_CLASS = {'NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'NML', 'NX'}
VERB_CLASS = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'AUX'}
ADJ_CLASS = {'JJ', 'JJR', 'JJS'}
ADV_CLASS = {'RB', 'RBR', 'RBS'}
DET_CLASS = {'DT'}
PREP_CLASS = {'IN', 'TO', 'POS', 'RP'}

NOUN_PLURAL = {'NNS', 'NNPS'}
NOUN_SINGULAR = {'NN', 'NNP', 'NML', 'NX'}

PRP_KEY = {
    'i': ('1', 'sg'), 'we': ('1', 'pl'), 'you': ('2', None),
    'he': ('3', 'sg'), 'she': ('3', 'sg'), 'it': ('3', 'sg'),
    'they': ('3', 'pl'),
}
DET_NUMREQ = {
    'a': 'sg', 'an': 'sg', 'one': 'sg', 'this': 'sg', 'that': 'sg',
    'each': 'sg', 'every': 'sg', 'another': 'sg', 'much': 'sg',
    'these': 'pl', 'those': 'pl', 'both': 'pl', 'many': 'pl', 'several': 'pl',
}
MODALS = {'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must'}
BE_FORM = {'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
HAVE_FORM = {'have', 'has', 'had', 'having'}
DO_FORM = {'do', 'does', 'did', 'doing', 'done'}

# Possessive determiners that can never head an NP (unlike the standalone
# possessive pronouns 'mine/yours/ours/theirs/hers/his').
POSS_DET_PLAIN = {'my', 'your', 'our', 'their', 'its'}
# Ambiguous surfaces excluded from POSS_DET_PLAIN on purpose:
#   'her' | 'his'  -- also standalone possessive pronouns / object pronoun

# Determinatives that double as standalone (anaphoric) pronoun heads of an NP:
# "This is good.", "These are mine.", "Each is important."
DEMONSTRATIVE_STANDALONE = {'this', 'that', 'these', 'those',
                            'each', 'some', 'one', 'all', 'several', 'any'}

PRON_SUBJ_PLAIN = {'i', 'we', 'he', 'she', 'they'}
PRON_OBJ_PLAIN = {'me', 'us', 'him', 'her', 'them'}

# Words spelled with a leading vowel letter that nevertheless take 'a'
# (consonant /j/, /w/ sound): a university, a union, a one-time ...
A_SOUND_CONST_WORDS = {
    'university', 'unit', 'union', 'universe', 'unity', 'user', 'useful',
    'unique', 'unicorn', 'usual', 'utensil', 'ukelele', 'ukulele',
    'euro', 'europe', 'european', 'ewe', 'one', 'once',
}
# Words spelled with a leading 'h' whose h is silent, taking 'an':
# an hour, an honest boy ...
AN_SILENT_H_WORDS = {'hour', 'honest', 'honour', 'honor', 'heir', 'herb', 'homage'}

# Flat adverbs that a strict grammar tutor expects in -ly form after an
# action verb: "He runs quick." -> "He runs quickly."
ASTRAY_FLAT_ADV = {'quick', 'slow', 'good', 'bad', 'real', 'nice', 'easy',
                   'terrible', 'beautiful'}

# Linking/copular verbs that license a predicate adjective after the verb.
LINKING_VERBS = (BE_FORM | {'seem', 'appear', 'look', 'feel', 'taste', 'sound',
                            'smell', 'become', 'remain', 'stay', 'turn', 'grow',
                            'prove', 'get'})

# Nouns that license a bare (article-less) singular argument: mass nouns,
# gerundial/activity nominals and common institutional/abstract nouns.
NONCOUNT_NOUNS = {
    'water', 'milk', 'juice', 'rice', 'bread', 'cheese', 'meat', 'sugar',
    'salt', 'oil', 'soup', 'coffee', 'tea', 'air', 'snow', 'rain', 'gold',
    'silver', 'paper', 'wood', 'furniture', 'information', 'advice',
    'luggage', 'baggage', 'equipment', 'news', 'knowledge', 'research',
    'traffic', 'money', 'cash', 'time', 'work', 'homework', 'housework',
    'weather', 'electricity', 'internet', 'darkness', 'sunshine',
    # gerundial / activity nominals
    'reading', 'swimming', 'running', 'jogging', 'dancing', 'hiking',
    'writing', 'cooking', 'baking', 'fishing', 'hunting', 'shopping',
    'sightseeing', 'camping', 'skating', 'skiing', 'cycling', 'walking',
    # abstract / umbrella nouns commonly used bare
    'truth', 'honesty', 'education', 'health', 'happiness', 'freedom',
    'justice', 'love', 'hate', 'nature', 'history', 'grammar', 'art',
    'music', 'sports', 'mathematics', 'math', 'science', 'physics',
    'society', 'democracy', 'defense', 'food', 'fun',
}
BARE_ARG_NOUNS = {
    'home', 'school', 'work', 'bed', 'church', 'town', 'court', 'class',
    'college', 'breakfast', 'lunch', 'dinner', 'supper', 'brunch', 'schoolwork',
}

VERB_FORM_LABEL = {
    'VB': 'base', 'VBD': 'past', 'VBG': 'present participle',
    'VBN': 'past participle', 'VBP': 'non-third-person present',
    'VBZ': 'third-person singular present', 'MD': 'modal',
}
NONFINITE = {'VB', 'VBG', 'VBN'}

CHECK_LABELS = {
    'C-SUBJECT-AGREEMENT': 'Subject\u2013Verb Agreement',
    'C-PREDICATE': 'Subject\u2013Verb Agreement',
    'C-DETERMINER-AGREEMENT': 'Determiner\u2013Noun Agreement',
    'C-DETERMINER': 'Determiner\u2013Noun Agreement',
    'C-AUX-FORM': 'Auxiliary Verb-Form Selection',
    'C-AUXILIARY': 'Auxiliary Verb-Form Selection',
    'C-TENSE-FINITE': 'Clause Finiteness (finite predicate required)',
    'C-MOD-POS': 'Modifier Before Head Noun',
    'C-DET-STACK': 'Single Determiner per NP',
    'C-HEAD-NOUN': 'Head Noun Identification',
    'C-HEAD-VERB': 'Head Verb Identification',
    'C-INFINITIVAL-COMPLEMENT': 'Non-finite to-infinitive Complement',
    'C-INFINITIVAL-MARKER': 'Infinitival Marker to',
    'C-COMPARATIVE-DOUBLE': 'Double Comparative',
    'C-HEAD-PREPOSITION': 'Head Preposition Identification',
    'C-HEAD-ADJECTIVE': 'Head Adjective Identification',
    'C-HEAD-ADVERBIAL': 'Head Adverbial Identification',
    'C-PUNCT': 'Sentence Punctuation',
    'C-ROOT': 'Sentence Root Structure',
    'C-SUBJECT-ROLE': 'Clause Subject Role',
    'C-CLAUSE-PREDICATE': 'Clause Predicate',
    'C-CLAUSE-SUBJECT': 'Clause Subject Role',
    'C-PRONOUN-CASE': 'Pronoun Case (nominative vs. objective)',
    'C-ADJ-ADV': 'Adjective\u2013Adverb Confusion',
    'C-ARTICLE': 'Article/Determiner Omission',
    'C-ARTICLE-MISMATCH': 'a\u2013an Article Selection',
    'C-CAPITALIZATION': 'Sentence Capitalization',
    'C-QUANTIFIER': 'Quantifier\u2013Noun Agreement',
    'C-SMALL-CLAUSE': 'Small Clause (object complement)',
    'C-SMALL-CLAUSE-PREDICATE': 'Small Clause Predicate',
    'C-ADVERBIAL-COMPLEMENT': 'Adverbial Complement',
    'C-VERB-FORM': 'Verb Form',
}


IRREGULAR_PLURAL = {
    'child': 'children', 'man': 'men', 'woman': 'women', 'foot': 'feet',
    'tooth': 'teeth', 'mouse': 'mice', 'person': 'people', 'goose': 'geese',
    'ox': 'oxen', 'leaf': 'leaves', 'life': 'lives', 'wife': 'wives',
    'knife': 'knives', 'shelf': 'shelves', 'wolf': 'wolves', 'half': 'halves',
    'calf': 'calves', 'loaf': 'loaves', 'thief': 'thieves', 'sheep': 'sheep',
    'fish': 'fish', 'deer': 'deer', 'series': 'series', 'species': 'species',
}

IRREGULAR_VBN = {
    'be': 'been', 'beat': 'beaten', 'bend': 'bent', 'bite': 'bitten',
    'break': 'broken', 'bring': 'brought', 'build': 'built', 'buy': 'bought',
    'catch': 'caught', 'choose': 'chosen', 'come': 'come', 'cut': 'cut',
    'do': 'done', 'drink': 'drunk', 'drive': 'driven', 'eat': 'eaten',
    'fall': 'fallen', 'feel': 'felt', 'fight': 'fought', 'find': 'found',
    'fly': 'flown', 'forget': 'forgotten', 'forgive': 'forgiven',
    'freeze': 'frozen', 'get': 'gotten', 'give': 'given', 'go': 'gone',
    'grow': 'grown', 'have': 'had', 'hear': 'heard', 'hit': 'hit',
    'hold': 'held', 'keep': 'kept', 'know': 'known', 'lead': 'led',
    'leave': 'left', 'lend': 'lent', 'let': 'let', 'lose': 'lost',
    'make': 'made', 'mean': 'meant', 'meet': 'met', 'pay': 'paid',
    'put': 'put', 'read': 'read', 'ride': 'ridden', 'ring': 'rung',
    'rise': 'risen', 'run': 'run', 'say': 'said', 'see': 'seen',
    'sell': 'sold', 'send': 'sent', 'sing': 'sung', 'sink': 'sunk',
    'sit': 'sat', 'sleep': 'slept', 'speak': 'spoken', 'spend': 'spent',
    'stand': 'stood', 'steal': 'stolen', 'swim': 'swum', 'take': 'taken',
    'teach': 'taught', 'tell': 'told', 'think': 'thought', 'throw': 'thrown',
    'understand': 'understood', 'wear': 'worn', 'win': 'won', 'write': 'written',
    'become': 'become',
}

IRREGULAR_PAST = {
    'be': 'was', 'begin': 'began', 'break': 'broke', 'bring': 'brought',
    'buy': 'bought', 'catch': 'caught', 'choose': 'chose', 'come': 'came',
    'do': 'did', 'drink': 'drank', 'drive': 'drove', 'eat': 'ate',
    'fall': 'fell', 'feel': 'felt', 'find': 'found', 'fly': 'flew',
    'forget': 'forgot', 'forgive': 'forgave', 'freeze': 'froze',
    'get': 'got', 'give': 'gave', 'go': 'went', 'grow': 'grew',
    'have': 'had', 'hear': 'heard', 'keep': 'kept', 'know': 'knew',
    'leave': 'left', 'lend': 'lent', 'lose': 'lost', 'make': 'made',
    'mean': 'meant', 'meet': 'met', 'pay': 'paid', 'read': 'read',
    'ride': 'rode', 'ring': 'rang', 'rise': 'rose', 'run': 'ran',
    'say': 'said', 'see': 'saw', 'sell': 'sold', 'send': 'sent',
    'sing': 'sang', 'sink': 'sank', 'sit': 'sat', 'sleep': 'slept',
    'speak': 'spoke', 'spend': 'spent', 'stand': 'stood', 'steal': 'stole',
    'swim': 'swam', 'take': 'took', 'teach': 'taught', 'tell': 'told',
    'think': 'thought', 'throw': 'threw', 'understand': 'understood',
    'wear': 'wore', 'win': 'won', 'write': 'wrote', 'become': 'became',
}


def _preserve_case(source, word):
    """Apply the capitalization of ``source`` to a replacement word."""
    if source and source[0].isupper():
        return word[0].upper() + word[1:]
    return word


def _base_form(leaf):
    """Approximate a lexical base form from the observed surface and POS."""
    word = leaf['surface'].lower()
    pos = leaf['type']
    for base in IRREGULAR_VBN:
        if word in {base + 'd', base + 'ed'}:
            return base
    if pos == 'VBZ':
        if word in {'is', 'has', 'does'}:
            return {'is': 'be', 'has': 'have', 'does': 'do'}[word]
        if word.endswith('ies'):
            return word[:-3] + 'y'
        if word.endswith('es'):
            return word[:-2]
        if word.endswith('s'):
            return word[:-1]
    if pos == 'VBG' and word.endswith('ing') and len(word) > 4:
        stem = word[:-3]
        return stem + 'e' if stem.endswith(('v', 'c')) else stem
    if pos in {'VBD', 'VBN'}:
        reverse = {value: key for key, value in IRREGULAR_VBN.items()}
        if word in reverse:
            return reverse[word]
        if word.endswith('ied'):
            return word[:-3] + 'y'
        if word.endswith('ed') and len(word) > 3:
            return word[:-2]
    return word


def _plural_noun(word):
    w = word.lower()
    if w in IRREGULAR_PLURAL:
        return IRREGULAR_PLURAL[w]
    if w.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return w + 'es'
    if len(w) > 1 and w[-1] == 'y' and w[-2] not in 'aeiou':
        return w[:-1] + 'ies'
    return w + 's'


def _singular_noun(leaf):
    """Approximate the singular form from the observed noun surface."""
    word = leaf['surface'].lower()
    if word in IRREGULAR_PLURAL.values():
        reverse = {value: key for key, value in IRREGULAR_PLURAL.items()}
        return reverse[word]
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith('es'):
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def _third_present(base):
    """Base verb -> 3rd-person singular present (e.g. run->runs, be->is)."""
    w = base.lower()
    if w == 'be':
        return 'is'
    if w == 'have':
        return 'has'
    if w == 'do':
        return 'does'
    if w == 'go':
        return 'goes'
    if w.endswith(('s', 'x', 'z', 'ch', 'sh', 'o')):
        return w + 'es'
    if len(w) > 1 and w[-1] == 'y' and w[-2] not in 'aeiou':
        return w[:-1] + 'ies'
    return w + 's'


def _nonthird_present(base):
    """Base verb -> non-3rd-person singular present (e.g. run->run, be->are)."""
    w = base.lower()
    return 'are' if w == 'be' else w


def _vbn_form(base):
    """Base verb -> past participle (e.g. eat->eaten, kick->kicked)."""
    w = base.lower()
    if w in IRREGULAR_VBN:
        return IRREGULAR_VBN[w]
    if w.endswith('e'):
        return w + 'd'
    return w + 'ed'


def _vbg_form(base):
    """Base verb -> present participle (e.g. run->running, make->making)."""
    w = base.lower()
    if w == 'be':
        return 'being'
    if w in ('lie', 'die', 'tie'):
        return w[:-1] + 'ying'
    if w.endswith('e'):
        return w[:-1] + 'ing'
    return w + 'ing'


def _regularized_form(base):
    word = base.lower()
    return word + 'd' if word.endswith('e') else word + 'ed'


def _is_valid_verb_form(leaf):
    """Reject regularized spellings of irregular forms and past-as-participle use."""
    word = leaf['surface'].lower()
    pos = leaf['type']
    if pos == 'VBD':
        return word not in {
            _regularized_form(base)
            for base in IRREGULAR_PAST
        }
    if pos == 'VBN':
        if word in IRREGULAR_PAST.values() and word not in IRREGULAR_VBN.values():
            return False
        return word not in {
            _regularized_form(base)
            for base in IRREGULAR_VBN
        }
    return True


def _replace_subject_head(subj, subj_head, new_head_word):
    """Subject surface with its (trailing) head noun swapped for ``new_head_word``."""
    words = subj['surface'].split()
    if words and words[-1] == subj_head['surface']:
        return ' '.join(words[:-1] + [_preserve_case(subj_head['surface'], new_head_word)])
    return _preserve_case(subj_head['surface'], new_head_word)


def _rule_for(node):
    """Formal production rule realized by this node (e.g. NP -> DT + NN)."""
    if 'children' in node:
        return f"{node['type']} \u2192 " + ' + '.join(c['type'] for c in node['children'])
    return f"{node['type']} \u2192 '{node['surface']}'"


def _checks_for(detail, details):
    """Deterministic checklist of the matrix checks that apply to a node.

    Built from the node's own edge verdict (and, for internal nodes, the
    verdicts of its immediate constituents) so a learner sees exactly which
    rule checks pass or fail at this level.
    """
    checks = []
    ok_own = detail['status'] != 'error'

    def add(label, ok):
        if not any(c['check'] == label for c in checks):
            checks.append({'check': label, 'ok': ok})

    named = CHECK_LABELS.get(detail['constraint'])
    if named:
        add(named, ok_own)
    membership = (f"Rule membership ({detail['constraint']})" if detail['constraint'] != 'C-UNLISTED'
                  else 'Matrix coverage (unrated \u00b7 valid-by-default)')
    add(membership, ok_own)
    for child_id in detail.get('children_ids', []):
        cd = details.get(child_id)
        if not cd:
            continue
        child_named = CHECK_LABELS.get(cd['constraint'])
        if child_named:
            add(child_named, cd['status'] != 'error')
    return checks


def _lower(surface):
    return surface.lower()


def num_of(leaf):
    """Grammatical number of a nominal leaf, or None if unmarked."""
    pos = leaf['type']
    if pos in NOUN_PLURAL:
        return 'pl'
    if pos in NOUN_SINGULAR:
        return 'sg'
    if pos == 'PRP':
        key = PRP_KEY.get(_lower(leaf['surface']))
        return key[1] if key else None
    return None


def person_of(leaf):
    pos = leaf['type']
    if pos.startswith('NN'):
        return '3'
    if pos == 'PRP':
        key = PRP_KEY.get(_lower(leaf['surface']))
        return key[0] if key else None
    return None


def subject_key(leaf):
    if person_of(leaf) is None:
        return None
    return (person_of(leaf), num_of(leaf))


def verb_key(leaf):
    """Agreement key of a finite verb leaf: ('3','sg'), ('*','non3sg'), or None
    (person-neutral: past tense/modals)."""
    pos = leaf['type']
    surface = _lower(leaf['surface'])
    if pos == 'MD':
        return None
    if pos == 'VBD':
        return None
    if pos == 'VBZ':
        return ('3', 'sg')
    if pos == 'VBP':
        return ('*', 'non3sg')
    if surface in BE_FORM:
        if surface in ('is', 'was'):
            return ('3', 'sg')
        if surface == 'am':
            return ('1', 'sg')
        return ('*', 'non3sg')
    if surface in HAVE_FORM:
        return ('3', 'sg') if surface == 'has' else ('*', 'non3sg')
    if surface in DO_FORM:
        return ('3', 'sg') if surface == 'does' else ('*', 'non3sg')
    return None


def agree(subject_leaf, verb_leaf):
    """True iff the subject leaf and (finite) verb leaf agree. Deterministic."""
    vk = verb_key(verb_leaf)
    if vk is None:
        return True
    sk = subject_key(subject_leaf)
    if sk is None:
        return True
    if vk == ('*', 'non3sg'):
        return sk != ('3', 'sg')
    if sk == ('2', None):
        return vk == ('*', 'non3sg')
    return vk == sk


def _leaves_list(node, out=None):
    if out is None:
        out = []
    if 'children' not in node:
        out.append(node)
        return out
    for c in node['children']:
        _leaves_list(c, out)
    return out


def _indefinite_article(word):
    """Deterministic 'a'/'an' choice for a (head) word, with phonetic
    exceptions for silent-h and vowel-letter-with-consonant-sound words."""
    w = word.lower().lstrip('\'\"\u2018\u2019\u201c\u201d')
    if not w:
        return 'a'
    if w in AN_SILENT_H_WORDS:
        return 'an'
    if w[0] in 'aeiou' and w not in A_SOUND_CONST_WORDS:
        return 'an'
    return 'a'


def _np_head(node):
    """Head-word pick for an NP, excluding possessive determiners from the noun
    candidates and (only when a determinative is present) falling back to a
    trailing nominal-accepting adjective ('my favorite', 'the rich')."""
    leaves = _leaves_list(node)
    nonposs_nouns = [lf for lf in leaves
                     if lf['type'] in NOUN_CLASS
                     and _lower(lf.get('surface', '')) not in POSS_DET_PLAIN]
    if nonposs_nouns:
        return nonposs_nouns[-1]
    determinatives = [lf for lf in leaves
                      if lf['type'] in DET_CLASS or lf['type'] == 'PRP$'
                      or _lower(lf.get('surface', '')) in POSS_DET_PLAIN]
    if determinatives:
        adjs = [lf for lf in leaves if lf['type'] in ADJ_CLASS]
        if adjs:
            return adjs[-1]
    return None


def _np_determinatives(node):
    """List of determinative leaves inside an NP (DT, PRP$, or a bare
    possessive-determiner surface typed as PRP)."""
    return [lf for lf in _leaves_list(node)
            if lf['type'] in DET_CLASS or lf['type'] == 'PRP$'
            or _lower(lf.get('surface', '')) in POSS_DET_PLAIN]


def _needs_indefinite_article_error(np_node):
    """Error message if a bare singular common noun heads an argument NP, else
    None. Mass/abstract/activity/institutional nouns are exempt."""
    head = _np_head(np_node)
    if head is None or head['type'] != 'NN':
        return None
    base = _base_form(head)
    surface = _lower(head['surface'])
    if base in NONCOUNT_NOUNS or base in BARE_ARG_NOUNS \
            or surface in NONCOUNT_NOUNS or surface in BARE_ARG_NOUNS:
        return None
    if is_coordinated(np_node):
        return None
    if _np_determinatives(np_node):
        return None
    leaves = _leaves_list(np_node)
    idx = next((i for i, lf in enumerate(leaves) if lf['id'] == head['id']), None)
    if idx and _lower(leaves[idx - 1]['surface']) in {'next', 'last', 'this', 'that'}:
        return None
    art = _indefinite_article(head['surface'])
    return (f"Noun '{head['surface']}' is a singular count noun and requires a "
            f"determiner in this argument position; add '{art}' (or an article "
            f"such as 'the'/'this') before it.")


def _object_pronoun_error(np_node, verb_leaf):
    """Error message if an NP in an argument position is headed by a nominative
    pronoun (it should be objective after an action verb), else None."""
    if verb_leaf is None or _lower(verb_leaf['surface']) in BE_FORM:
        return None
    h = _np_head(np_node)
    if h is None or h['type'] != 'PRP':
        return None
    surf = _lower(h['surface'])
    if surf not in PRON_SUBJ_PLAIN:
        return None
    target = {'i': 'me', 'we': 'us', 'he': 'him', 'she': 'her', 'they': 'them'}[surf]
    return (f"Pronoun-case violation: '{h['surface']}' is the nominative form, but this "
            f"argument follows the verb '{verb_leaf['surface']}' and must be objective \u2014 "
            f"use '{target}'.")


def phrase_head(node):
    """Deterministic head-word pick for a constituent, or None."""
    label = node['type']
    leaves = _leaves_list(node)
    if label in {'NP', 'NML', 'NX'}:
        return _np_head(node)
    if label == 'VP':
        cands = [lf for lf in leaves if lf['type'] in VERB_CLASS]
        return cands[0] if cands else None
    if label in {'PP', 'PRTP'}:
        cands = [lf for lf in leaves if lf['type'] in PREP_CLASS]
        return cands[0] if cands else None
    if label in {'ADJP'}:
        cands = [lf for lf in leaves if lf['type'] in ADJ_CLASS]
        return cands[-1] if cands else None
    if label in {'ADVP'}:
        cands = [lf for lf in leaves if lf['type'] in ADV_CLASS]
        return cands[0] if cands else None
    if label in SENTENCE_CLASSES:
        cands = [lf for lf in leaves if lf['type'] in VERB_CLASS]
        return cands[0] if cands else None
    return None


def clause_subject_and_verb(s_node):
    subj = None
    vp = None
    for child in s_node['children']:
        if child['type'] == 'NP' and subj is None:
            subj = child
        if child['type'] == 'VP' and vp is None:
            vp = child
    return subj, vp


def is_coordinated(node):
    """True if the constituent is a coordination (joins two or more conjuncts).

    A subject NP containing a coordinating conjunction (CC/UCP/CONJP) is
    plural in English regardless of the number of any single conjunct head,
    e.g. 'Jaisen and Kielle' (plural) vs 'Jaisen' (singular).
    """
    if 'children' not in node:
        return False
    return any(c['type'] in {'CC', 'CONJP', 'UCP'} for c in node['children'])


def _agreement_ok(skey, vkey):
    """Agreement test for a subject key and a finite-verb key (deterministic)."""
    if vkey is None or skey is None:
        return True
    if vkey == ('*', 'non3sg'):
        return skey != ('3', 'sg')
    if skey == ('2', None):
        return vkey == ('*', 'non3sg')
    return vkey == skey


class MatrixEvaluator:
    """Deterministic edge evaluation of a node graph."""

    def __init__(self):
        self.details = {}

    def evaluate(self, root):
        self.details = {}
        self._walk(root)
        self._root_level(root)
        for detail in self.details.values():
            detail['checks'] = _checks_for(detail, self.details)
            if detail['status'] == 'error':
                remediation = self._remediate(root, detail)
                if remediation:
                    detail['remediation'] = remediation
        return {'details': self.details, 'summary': self._summarize(root)}

    def _walk(self, node, grandparent=None):
        if 'children' in node:
            for child in node['children']:
                self.details[child['id']] = self._edge(node, child, grandparent)
                self._walk(child, node)

    def _edge(self, parent, child, grandparent=None):
        if child.get('punct'):
            self._detail(child, parent, 'terminal punctuation', 'C-PUNCT', 'valid',
                         'Terminal punctuation; not subject to grammatical constraints.')
            return self.details[child['id']]
        verdict = self._classify(parent, child, grandparent)
        self._detail(child, parent, self._role_for(verdict[1]),
                     verdict[1], verdict[0], verdict[2])
        return self.details[child['id']]

    def _classify(self, parent, child, grandparent=None):
        pt, ct = parent['type'], child['type']
        if pt == 'S':
            if ct == 'NP':
                return self._s_subject(parent, child)
            if ct == 'VP':
                return self._s_predicate(parent, child)
            if ct == 'ADJP':
                return ('valid', 'C-SMALL-CLAUSE-PREDICATE',
                        f"Adjective phrase '{child['surface']}' is the predicate of a "
                        'small-clause complement.')
            if ct == 'ADVP':
                return ('valid', 'C-CLAUSAL-ADVERBIAL',
                        f"Adverbial phrase '{child['surface']}' modifies the clause; licensed at sentence level.")
            if ct == 'PP':
                return ('valid', 'C-CLAUSAL-ADVERBIAL',
                        f"Prepositional phrase '{child['surface']}' is an adjunct modifying the clause.")
            if ct == 'SBAR':
                return ('valid', 'C-CLAUSAL-COMPLEMENT',
                        f"Clause '{child['surface']}' functions as a clausal constituent of the sentence.")
        if pt == 'NP':
            return self._np_rule(parent, child, grandparent)
        if pt == 'VP':
            return self._vp_rule(parent, child)
        if pt == 'PP':
            if ct in PREP_CLASS:
                return ('valid', 'C-HEAD-PREPOSITION',
                        f"Preposition '{child['surface']}' heads the PP.")
            if ct == 'NP':
                h = phrase_head(parent)
                head = h['surface'] if h else '?'
                onp = _np_head(child)
                if onp is not None and onp['type'] == 'PRP' and \
                        _lower(onp['surface']) in PRON_SUBJ_PLAIN:
                    target = {'i': 'me', 'we': 'us', 'he': 'him',
                              'she': 'her', 'they': 'them'}[_lower(onp['surface'])]
                    return ('error', 'C-PRONOUN-CASE',
                            f"Pronoun-case violation: '{onp['surface']}' is the nominative "
                            f"form, but the object of the preposition '{head}' must be "
                            f"objective \u2014 use '{target}'.")
                return ('valid', 'C-PREP-OBJECT',
                        f"NP '{child['surface']}' is the object of the preposition '{head}'.")
        if pt == 'ADJP':
            if ct in ADJ_CLASS:
                return ('valid', 'C-HEAD-ADJECTIVE',
                        f"'{child['surface']}' heads the adjective phrase.")
            if ct in {'RBR', 'RBS'}:
                for sibling in parent['children']:
                    if sibling['type'] in {'JJR', 'JJS'}:
                        return ('error', 'C-COMPARATIVE-DOUBLE',
                                f"Double comparative/superlative: '{child['surface']}' (degree "
                                f"marker) duplicates the morphological "
                                f"{'comparative' if sibling['type'] == 'JJR' else 'superlative'} "
                                f"'{sibling['surface']}'; drop one of them.")
                return ('valid', 'C-INTENSIFIER',
                        f"Degree marker '{child['surface']}' scopes over the adjective phrase.")
            if ct in ADV_CLASS:
                return ('valid', 'C-INTENSIFIER',
                        f"Intensifier '{child['surface']}' scopes over the adjective phrase.")
            if ct in {'VBN', 'VBG'}:
                return ('valid', 'C-PARTICIPLE-MODIFIER',
                        f"Participle '{child['surface']}' modifies the adjective phrase.")
        if pt == 'ADVP':
            if ct in ADJ_CLASS:
                return ('error', 'C-ADJ-ADV',
                        f"Adjective\u2013adverb confusion: '{child['surface']}' is an adjective "
                        f"({ct}), but an adverb phrase requires an adverb (use "
                        f"'{self._adverbial_form(child['surface'])}').")
            if ct == 'NP':
                return ('valid', 'C-ADVERBIAL-COMPLEMENT',
                        f"NP '{child['surface']}' is a temporal/measure complement inside the "
                        'adverbial phrase.')
            if ct in ADV_CLASS or ct == 'ADVP':
                return ('valid', 'C-HEAD-ADVERBIAL',
                        f"Adverbial '{child['surface']}' heads/extends the adverb phrase.")
            if ct == 'CC':
                return ('valid', 'C-COORDINATOR',
                        f"Coordinator '{child['surface']}' joins adverbial conjuncts.")
        if pt == 'SBAR':
            if ct == 'S':
                return ('valid', 'C-RELATIVE-CLAUSE',
                        f"Clause '{child['surface']}' is the complement of the "
                        'relative/complementizer construction.')
            if ct == 'IN':
                return ('valid', 'C-COMPLEMENTIZER',
                        f"Complementizer '{child['surface']}' introduces the subordinate clause.")
            if ct in {'WHNP', 'WHPP', 'WHADVP', 'WADVP', 'WPP'}:
                return ('valid', 'C-RELATIVE-HEAD',
                        f"Wh-phrase '{child['surface']}' heads the relative clause.")
        if pt == 'WHNP':
            if ct in {'WP', 'WDT', 'WP$'}:
                return ('valid', 'C-RELATIVE-PRONOUN',
                        f"Relative pronoun '{child['surface']}' heads the wh-phrase.")
            if ct in NOUN_CLASS:
                return ('valid', 'C-RELATIVE-NOUN',
                        f"Noun '{child['surface']}' is the nominal head of the wh-phrase.")
        if pt in {'WHPP', 'WHADVP', 'WADVP', 'WPP'}:
            return ('valid', 'C-RELATIVE-HEAD',
                    f"Wh-phrase '{child['surface']}' extends the relative-clause structure.")
        if pt in SENTENCE_CLASSES and pt != 'S':
            if ct == 'NP':
                return ('valid', 'C-CLAUSE-SUBJECT',
                        f"NP '{child['surface']}' is the subject of the clause.")
            if ct == 'VP':
                return ('valid', 'C-CLAUSE-PREDICATE',
                        f"VP '{child['surface']}' is the predicate of the clause.")
        return self._unlisted(parent, child)

    @staticmethod
    def _unlisted(parent, child):
        return ('unlisted', 'C-UNLISTED',
                f"Edge {child['type']} \u2192 {parent['type']} has no dedicated rule in the matrix; "
                'reported as unrated (valid-by-default).')

    @staticmethod
    def _s_subject(parent, child):
        return ('valid', 'C-SUBJECT-ROLE',
                f"NP '{child['surface']}' functions as the clause subject; "
                'subject-verb agreement is evaluated on the predicate edge.')

    def _s_predicate(self, parent, child):
        subj, _vp = clause_subject_and_verb(parent)
        vp_head = phrase_head(child)
        if vp_head is None:
            return ('error', 'C-TENSE-FINITE',
                    f"Clause '{parent['surface']}' has no finite predicate verb.")
        if vp_head['type'] in NONFINITE:
            if child['children'] and child['children'][0].get('type') == 'TO':
                return ('valid', 'C-INFINITIVAL-COMPLEMENT',
                        f"VP '{child['surface']}' is the non-finite to-infinitive complement of "
                        'the clause; no finite form is required here.')
            return ('error', 'C-TENSE-FINITE',
                    f"Predicate verb '{vp_head['surface']}' is "
                    f"{VERB_FORM_LABEL.get(vp_head['type'], 'non-finite')}; "
                    'a main clause requires a finite verb.')
        if subj is None:
            return ('valid', 'C-PREDICATE',
                    f"Predicate '{child['surface']}' licenses the clause (no subject edge to agree with).")
        subj_head = phrase_head(subj)
        if subj_head is None:
            return ('valid', 'C-PREDICATE',
                    f"Predicate '{child['surface']}' licenses the clause.")
        if subj_head['type'] == 'PRP' and _lower(subj_head['surface']) in PRON_OBJ_PLAIN:
            target = {'me': 'I', 'us': 'we', 'him': 'he', 'her': 'she',
                      'them': 'they'}[_lower(subj_head['surface'])]
            return ('error', 'C-PRONOUN-CASE',
                    f"Pronoun-case violation: '{subj_head['surface']}' is the objective form, "
                    f"but the clause subject must be nominative \u2014 use '{target}'.")
        coordinated = is_coordinated(subj)
        skey = ('3', 'pl') if coordinated else subject_key(subj_head)
        vkey = verb_key(vp_head)
        subj_label = '3rd person plural' if coordinated else self._subj_label(subj_head)
        if _agreement_ok(skey, vkey):
            return ('valid', 'C-PREDICATE',
                    f"Subject '{subj['surface']}' ({subj_label}) and predicate verb "
                    f"'{vp_head['surface']}' ({self._verb_label(vp_head)}) agree in person and number.")
        return ('error', 'C-SUBJECT-AGREEMENT',
                f"Subject-verb agreement violated: subject '{subj['surface']}' is "
                f"{subj_label}, but predicate verb '{vp_head['surface']}' is "
                f"{self._verb_label(vp_head)}.")

    @staticmethod
    def _subj_label(head):
        pos = head['type']
        if pos == 'PRP':
            return {
                ('1', 'sg'): '1st person singular', ('1', 'pl'): '1st person plural',
                ('2', None): '2nd person', ('3', 'sg'): '3rd person singular',
                ('3', 'pl'): '3rd person plural',
            }.get(subject_key(head), 'a pronoun')
        if pos in NOUN_PLURAL:
            return '3rd person plural'
        return '3rd person singular'

    @staticmethod
    def _verb_label(head):
        surface = _lower(head['surface'])
        form = VERB_FORM_LABEL.get(head['type'], head['type'])
        if head['type'] == 'MD':
            return 'a modal auxiliary'
        if surface in BE_FORM or surface in HAVE_FORM or surface in DO_FORM:
            return f"{form} ({surface})"
        return form

    def _np_rule(self, parent, child, grandparent=None):
        ct = child['type']
        head = _np_head(parent)
        if ct in DET_CLASS or ct == 'PRP$' or _lower(child.get('surface', '')) in POSS_DET_PLAIN:
            determinatives = _np_determinatives(parent)
            if len(determinatives) > 1:
                return ('error', 'C-DET-STACK',
                        f"'{child['surface']}' stacks a second determiner in this NP; "
                        'an NP has at most one determinative position.')
            if head is None:
                if _lower(child.get('surface', '')) in DEMONSTRATIVE_STANDALONE:
                    return ('valid', 'C-DETERMINER',
                            f"Demonstrative/quantifier '{child['surface']}' stands alone as the "
                            'pronoun head of this NP; license accepted.')
                return ('error', 'C-HEAD-NOUN',
                        f"'{child['surface']}' is a determiner/possessive, but this NP has no "
                        'nominal head; a determiner must modify a noun (or nominalized '
                        "adjective). Add a noun after the determiner.")
            if ct in DET_CLASS:
                return self._det_num(parent, child, head)
            return ('valid', 'C-DETERMINER',
                    f"Genitive determiner '{child['surface']}' marks possession of the NP.")
        if ct in NOUN_CLASS:
            if head is not None and child['id'] == head['id']:
                num = num_of(child)
                if child['type'] == 'NN' and (grandparent is not None
                                              and grandparent['type'] in {'S', 'SINV', 'SQ',
                                                                          'SBARQ', 'VP'}):
                    need = _needs_indefinite_article_error(parent)
                    if need is not None:
                        return ('error', 'C-ARTICLE', need)
                return ('valid', 'C-HEAD-NOUN',
                        f"Noun '{child['surface']}' ({num or 'unmarked'}) is the head of the NP.")
            return ('valid', 'C-NOUN-ADJUNCT',
                    f"Noun '{child['surface']}' modifies the NP head "
                    f"('{head['surface'] if head else '?'}').")
        if ct in ADJ_CLASS or ct == 'ADJP':
            if ct in ADJ_CLASS and _lower(child.get('surface', '')) in \
                    {'less', 'fewer', 'much', 'many', 'little', 'few'}:
                return self._quantifier_check(parent, child, head)
            return self._modifier_pos(parent, child)
        if ct in {'CD', 'PDT', 'QP'}:
            return self._modifier_pos(parent, child)
        if ct == 'PP':
            return ('valid', 'C-NP-POSTMODIFIER',
                    f"PP '{child['surface']}' postmodifies the NP headed by "
                    f"'{head['surface'] if head else '?'}'.")
        if ct == 'VP':
            return ('valid', 'C-NP-REDUCED-RELATIVE',
                    f"VP '{child['surface']}' is a reduced relative clause postmodifying the NP.")
        if ct in {'SBAR', 'S'}:
            return ('valid', 'C-NP-RELATIVE',
                    f"Clause '{child['surface']}' is a relative clause modifying the NP.")
        if ct == 'CC':
            return ('valid', 'C-COORDINATOR',
                    f"Coordinator '{child['surface']}' joins NP conjuncts.")
        if ct in {'NP', 'NML', 'NX'}:
            return ('valid', 'C-NP-COMPOUND',
                    f"NP '{child['surface']}' supplies the internal structure of the NP.")
        return self._unlisted(parent, child)

    @staticmethod
    def _quantifier_check(parent, child, head):
        word = _lower(child['surface'])
        if head is None:
            return ('error', 'C-QUANTIFIER',
                    f"Quantifier '{child['surface']}' has no count/mass noun to modify.")
        base = _base_form(head)
        num = num_of(head)
        # selection map: word -> required number (None = number-neutral)
        requires = {'less': 'sg', 'much': 'sg', 'little': 'sg',
                    'fewer': 'pl', 'many': 'pl', 'few': 'pl'}
        req = requires[word]
        paired = {'less': 'fewer', 'fewer': 'less', 'much': 'many', 'many': 'much',
                  'little': 'few', 'few': 'little'}[word]
        if num is not None and req != num:
            return ('error', 'C-QUANTIFIER',
                    f"Quantifier-noun agreement violated: '{child['surface']}' selects "
                    f"{'singular/mass' if req == 'sg' else 'plural count'} nouns, but the "
                    f"head noun '{head['surface']}' is {num}; use '{paired}' before "
                    f"{'plural count' if req == 'sg' else 'mass/singular'} nouns.")
        return ('valid', 'C-QUANTIFIER',
                f"Quantifier '{child['surface']}' agrees with the head noun "
                f"'{head['surface']}' ({num or 'unmarked'}).")

    @staticmethod
    def _det_num(parent, child, head):
        det = _lower(child['surface'])
        numreq = DET_NUMREQ.get(det)
        num = num_of(head) if head is not None else None
        child_num = f"'{head['surface']}'" if head else 'the head noun'
        if numreq is not None and num is not None and numreq in ('sg', 'pl') and numreq != num:
            return ('error', 'C-DETERMINER-AGREEMENT',
                    f"Determiner-noun agreement violated: determiner '{child['surface']}' selects "
                    f"number {numreq}, but the head noun '{head['surface']}' is {num}.")
        if det in ('a', 'an'):
            leaves = _leaves_list(parent)
            idx = next((i for i, lf in enumerate(leaves) if lf['id'] == child['id']), None)
            if idx is not None and idx + 1 < len(leaves):
                nxt = leaves[idx + 1]['surface']
                need = _indefinite_article(nxt)
                if need != det:
                    return ('error', 'C-ARTICLE-MISMATCH',
                            f"Article-selection error: '{child['surface']}' precedes "
                            f"'{nxt}', which starts with a "
                            f"{'vowel sound' if need == 'an' else 'consonant sound'}; "
                            f"use '{'an' if need == 'an' else 'a'}' instead.")
        if numreq is not None and num is not None:
            return ('valid', 'C-DETERMINER',
                    f"Determiner '{child['surface']}' (number {numreq}) agrees with head noun "
                    f"'{head['surface']}' ({num}).")
        return ('valid', 'C-DETERMINER',
                f"Determiner '{child['surface']}' is number-neutral (or {child_num} is unmarked); "
                'no number conflict.')

    @staticmethod
    def _modifier_pos(parent, child):
        head = phrase_head(parent)
        if head is not None and child['span'][0] > head['span'][0]:
            return ('error', 'C-MOD-POS',
                    f"Modifier placement: '{child['surface']}' appears after the head noun "
                    f"'{head['surface']}'; NP modifiers must precede their head.")
        return ('valid', 'C-MOD-POS',
                f"Modifier '{child['surface']}' precedes the head noun "
                f"'{head['surface'] if head else '?'}'; position licensed.")

    def _vp_rule(self, parent, child):
        ct = child['type']
        head = phrase_head(parent)
        if ct in VERB_CLASS:
            if self._aux_class(child):
                return self._aux_check(parent, child)
            if head is not None and child['id'] == head['id']:
                return self._verb_head(parent, child)
        if ct in NOUN_CLASS:
            return ('error', 'C-HEAD-VERB',
                    f"A VP must be headed by a verb, but '{child['surface']}' is a noun "
                    f"({ct}); the parser could not find a verb head in '{parent['surface']}'.")
        if ct == 'VP':
            return ('valid', 'C-AUX-COMPLEMENT',
                    f"VP '{child['surface']}' is the complement of the auxiliary structure.")
        if ct == 'NP':
            obj_pron = _object_pronoun_error(child, head)
            if obj_pron is not None:
                return ('error', 'C-PRONOUN-CASE', obj_pron)
            return ('valid', 'C-DIRECT-OBJECT',
                    f"NP '{child['surface']}' is the direct object of "
                    f"'{head['surface'] if head else 'the verb'}'.")
        if ct == 'PP':
            return ('valid', 'C-ADJUNCT',
                    f"PP '{child['surface']}' is an oblique/adjunct modifier of the VP.")
        if ct == 'ADJP':
            if self._vp_predicate_adj_err(parent, child):
                return ('error', 'C-ADJ-ADV',
                        f"Adjective\u2013adverb confusion: '{child['surface']}' is an adjective "
                        f"phrase used after action verb '{head['surface'] if head else 'the verb'}', "
                        f"which is not a linking verb; use the adverb form "
                        f"('{self._adverbial_form(child['surface'].split()[-1])}') instead.")
            return ('valid', 'C-PREDICATE-ADJECTIVE',
                    f"Adjective phrase '{child['surface']}' is a predicate/object complement.")
        if ct == 'ADVP':
            adv = phrase_head(child)
            if adv is not None and _lower(adv['surface']) in ASTRAY_FLAT_ADV:
                return ('error', 'C-ADJ-ADV',
                        f"Adjective\u2013adverb confusion: '{adv['surface']}' is a flat "
                        f"adjective form; use the adverb '{self._adverbial_form(adv['surface'])}' "
                        f"after action verb '{head['surface'] if head else 'the verb'}'.")
            return ('valid', 'C-ADVERBIAL',
                    f"Adverbial '{child['surface']}' modifies the VP.")
        if ct == 'SBAR':
            return ('valid', 'C-CLAUSAL-COMPLEMENT',
                    f"Clause '{child['surface']}' is the complement of the VP.")
        if ct == 'S':
            return ('valid', 'C-SMALL-CLAUSE',
                    f"Clause '{child['surface']}' is a small-clause/object complement of the "
                    f"verb '{head['surface'] if head else 'the verb'}'.")
        if ct == 'TO':
            return ('valid', 'C-INFINITIVAL-MARKER',
                    f"Marker 'to' introduces the non-finite infinitive verb phrase.")
        if ct == 'RP':
            return ('valid', 'C-PARTICLE',
                    f"Particle '{child['surface']}' completes a phrasal verb construction.")
        return self._unlisted(parent, child)

    @staticmethod
    def _vp_predicate_adj_err(vp_node, adjp_child):
        """True when an ADJP complement of the VP is not licensed: the verb is a
        plain action verb (not linking/copular) and there is no object NP that the
        adjective could be complementing."""
        head = phrase_head(vp_node)
        if head is None or _lower(head['surface']) in LINKING_VERBS:
            return False
        earlier = [c for c in vp_node['children']
                   if c['id'] != adjp_child['id']
                   and c['span'][0] < adjp_child['span'][0]]
        if any(c['type'] == 'NP' for c in earlier):
            return False
        return True

    @staticmethod
    def _adverbial_form(word):
        w = word.lower()
        special = {'good': 'well', 'hard': 'hard', 'fast': 'fast', 'late': 'late',
                   'early': 'early', 'long': 'long', 'straight': 'straight',
                   'high': 'high', 'low': 'low', 'deep': 'deeply'}
        if w in special:
            return special[w]
        if w.endswith('ic'):
            return w + 'ally'
        if w == 'true':
            return 'truly'
        if w == 'whole':
            return 'wholly'
        if w.endswith('y'):
            return w[:-1] + 'ily'
        if w.endswith('le') and len(w) > 2 and w[-3] not in 'aeiou':
            return w[:-1] + 'y'
        return w + 'ly'

    @staticmethod
    def _verb_head(parent, child):
        role = 'finite' if child['type'] in {'VBZ', 'VBP', 'VBD', 'MD'} else 'non-finite'
        if not _is_valid_verb_form(child):
            expected = 'past tense' if child['type'] == 'VBD' else 'past participle'
            return ('error', 'C-VERB-FORM',
                    f"Verb '{child['surface']}' is not a valid {expected} form; "
                    'use the lexical form required by the verb.')
        return ('valid', 'C-HEAD-VERB',
                f"Verb '{child['surface']}' ({VERB_FORM_LABEL.get(child['type'], role)}) is the "
                f"{role} head of the VP.")

    @staticmethod
    def _aux_class(child):
        return child['type'] in {'MD', 'AUX'} or \
            _lower(child.get('surface', '')) in (MODALS | BE_FORM | HAVE_FORM | DO_FORM)

    def _aux_check(self, parent, child):
        surface = _lower(child['surface'])
        if child['type'] in {'MD', 'AUX'} or surface in MODALS:
            cls = 'modal'
        elif surface in BE_FORM:
            cls = 'be'
        elif surface in HAVE_FORM:
            cls = 'have'
        elif surface in DO_FORM:
            cls = 'do'
        else:
            return self._verb_head(parent, child)
        verb_node = self._following_verb(parent, child)
        if verb_node is None:
            return self._verb_head(parent, child)
        if not _is_valid_verb_form(verb_node):
            expected = 'the past participle' if cls == 'have' else 'a valid participle'
            return ('error', 'C-VERB-FORM',
                    f"Verb-form violation: '{verb_node['surface']}' is not {expected}; "
                    f"do not use a regularized or past-tense form after '{child['surface']}'.")
        required = {'modal': 'the base form', 'do': 'the base form',
                    'have': 'the past participle',
                    'be': 'a participle (progressive or passive)'}[cls]
        ok_forms = {'modal': {'VB'}, 'do': {'VB'},
                    'have': {'VBN'}, 'be': {'VBG', 'VBN'}}
        got = VERB_FORM_LABEL.get(verb_node['type'], verb_node['type'])
        if verb_node['type'] in ok_forms[cls]:
            return ('valid', 'C-AUXILIARY',
                    f"Auxiliary '{child['surface']}' ({cls}) is correctly followed by "
                    f"'{verb_node['surface']}' ({got}).")
        return ('error', 'C-AUX-FORM',
                f"Auxiliary verb-form violated: '{child['surface']}' ({cls}) requires "
                f"{required}, but the next verb '{verb_node['surface']}' is {got}.")

    @staticmethod
    def _following_verb(parent, aux_child):
        after = [c for c in parent['children'] if c['id'] != aux_child['id']]
        for c in after:
            verb_leaves = _leaves_list(c)
            if verb_leaves and verb_leaves[0]['type'] in VERB_CLASS:
                return verb_leaves[0]
        return None

    # ------------------------------------------------------------------ #
    # Case B: remediation for invalid nodes (deterministic correction)    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_node(root, nid):
        stack = [root]
        while stack:
            node = stack.pop()
            if node['id'] == nid:
                return node
            stack.extend(node.get('children', []))
        return None

    def _remediate(self, root, detail):
        """Deterministic, pedagogical correction guide for an invalid node.

        Returns a dict {violation, suggested_fix, alternative_fix, targeted_outcome}
        for the constraints the matrix can remediate, else None.
        """
        cid = detail['constraint']
        node = self._find_node(root, detail['id'])
        parent = self._find_node(root, detail['parent']) if detail.get('parent') else None
        if node is None:
            return None
        if cid == 'C-SUBJECT-AGREEMENT':
            return self._rem_agreement(node, parent)
        if cid == 'C-DETERMINER-AGREEMENT':
            return self._rem_det(node, parent)
        if cid == 'C-AUX-FORM':
            return self._rem_aux(node, parent)
        if cid == 'C-DET-STACK':
            return self._rem_det_stack(node, parent)
        if cid == 'C-MOD-POS':
            return self._rem_mod_pos(node, parent)
        if cid == 'C-PRONOUN-CASE':
            return self._rem_pronoun_case(node, parent)
        if cid == 'C-ADJ-ADV':
            return self._rem_adj_adv(node, parent)
        if cid == 'C-ARTICLE':
            return self._rem_article(node, parent)
        if cid == 'C-ARTICLE-MISMATCH':
            return self._rem_article_mismatch(node, parent)
        if cid == 'C-CAPITALIZATION':
            return self._rem_capitalization(node)
        if cid == 'C-QUANTIFIER':
            return self._rem_quantifier(node, parent)
        if cid == 'C-HEAD-VERB':
            return self._rem_vp_head_noun(node, parent)
        if cid == 'C-COMPARATIVE-DOUBLE':
            return self._rem_double_comparative(node, parent)
        if cid == 'C-HEAD-NOUN':
            return self._rem_head_noun(node, parent)
        if cid == 'C-TENSE-FINITE':
            if detail['role'] == 'fragment root':
                return self._rem_fragment(node)
            return self._rem_finite_verb(node, parent)
        return self._rem_generic(detail)

    def _rem_agreement(self, node, parent):
        subj, vp = clause_subject_and_verb(parent)
        vp_head = phrase_head(node) if vp is None else phrase_head(vp)
        subj_head = phrase_head(subj)
        if subj is None or subj_head is None or vp_head is None:
            return None
        coordinated = is_coordinated(subj)
        sk = ('3', 'pl') if coordinated else subject_key(subj_head)
        subj_label = '3rd person plural' if coordinated else self._subj_label(subj_head)
        verb_surface = vp_head['surface']
        verb_label = self._verb_label(vp_head)
        violation = (f"Subject\u2013Verb Agreement Conflict: the subject '{subj['surface']}' is "
                     f"{subj_label}, but the predicate verb '{verb_surface}' is {verb_label}.")
        if sk == ('3', 'sg'):
            target = _preserve_case(verb_surface, _third_present(_base_form(vp_head)))
            target_pos = 'VBZ'
        else:
            target = _preserve_case(verb_surface, _nonthird_present(_base_form(vp_head)))
            target_pos = 'VBP'
        suggested = (f"Change '{verb_surface}' to '{target}' "
                     f"({'third-person singular present' if target_pos == 'VBZ' else 'non-third-person present'}) "
                     f"so it agrees with the {subj_label} subject '{subj['surface']}'.")
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': self._subject_fix_alternative(subj, subj_head, vp_head),
            'targeted_outcome': (f"Subject NP ({subj_label}) + verb {target_pos} "
                                 f"instead of Subject NP ({subj_label}) + verb {vp_head['type']}"),
        }

    @staticmethod
    def _subject_fix_alternative(subj, subj_head, vp_head):
        """Alternative agreement fix: adjust the subject to match the verb."""
        verb_surface = vp_head['surface']
        if is_coordinated(subj):
            if verb_key(vp_head) == ('3', 'sg'):
                if person_of(subj_head) == '3':
                    head_word = _preserve_case(subj_head['surface'], _singular_noun(subj_head))
                else:
                    head_word = 'she/he'
                return (f"Or rewrite with a single singular subject so it agrees with "
                        f"'{verb_surface}': drop the conjunction and use just "
                        f"'{head_word}' instead of the coordinate subject '{subj['surface']}'.")
            return None
        if verb_key(vp_head) == ('3', 'sg'):
            if subj_head['type'] == 'PRP':
                swap = {
                    'they': 'he or she', 'we': 'I', 'they\'re': 'he or she is',
                }.get(_base_form(subj_head))
                if swap is None:
                    return None
                return (f"Or change the subject pronoun '{subj_head['surface']}' to "
                        f"'{swap}' so it agrees with '{verb_surface}'.")
            singular = _replace_subject_head(subj, subj_head, _singular_noun(subj_head))
            return (f"Or change the subject so it agrees with '{verb_surface}': use "
                    f"'{singular}' (singular) instead of '{subj['surface']}'.")
        plural = _plural_noun(_singular_noun(subj_head))
        if subj_head['type'] == 'PRP':
            swap = {'they': 'they', 'we': 'we', 'he': 'he or she'}.get(_base_form(subj_head))
            return (f"Or keep the subject '{subj['surface']}' and change the verb instead, so "
                    f"the pair agrees.")
        return (f"Or change the subject to plural so it agrees with '{verb_surface}': use "
                f"'{_preserve_case(subj_head['surface'], plural)}' instead of "
                f"'{subj['surface']}'.")

    def _rem_det(self, node, parent):
        head = phrase_head(parent) if parent else None
        if head is None:
            return None
        numreq = DET_NUMREQ.get(node['surface'].lower())
        num = num_of(head)
        if numreq not in ('sg', 'pl') or num is None or numreq == num:
            return None
        det_s = node['surface']
        noun_s = head['surface']
        violation = (f"Determiner\u2013Noun Agreement Conflict: the determiner '{det_s}' selects "
                     f"number {numreq}, but the head noun '{noun_s}' is {num}.")
        if numreq == 'pl':
            fix_noun = _preserve_case(noun_s, _plural_noun(_singular_noun(head)))
            suggested = (f"Change '{noun_s}' to the plural '{fix_noun}' so it matches the "
                         f"plural determiner '{det_s}'.")
            alternative = (f"Or change the determiner to a singular one (e.g. 'this', 'that', "
                           f"'a', 'an') so it matches the singular noun '{noun_s}'.")
            outcome = f"DT (number: {numreq}) + NNS instead of DT (number: {numreq}) + {head['type']}"
        else:  # numreq == 'sg', noun plural
            fix_noun = _preserve_case(noun_s, _singular_noun(head))
            suggested = (f"Change '{noun_s}' to the singular '{fix_noun}' so it matches the "
                         f"singular determiner '{det_s}'.")
            alternative = (f"Or change the determiner to a plural one (e.g. 'these', 'those') "
                           f"so it matches the plural noun '{noun_s}'.")
            outcome = f"DT (number: {numreq}) + NN instead of DT (number: {numreq}) + {head['type']}"
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': alternative,
            'targeted_outcome': outcome,
        }

    def _rem_aux(self, node, parent):
        surface = node['surface'].lower()
        if node['type'] in {'MD', 'AUX'} or surface in MODALS:
            cls = 'modal'
        elif surface in BE_FORM:
            cls = 'be'
        elif surface in HAVE_FORM:
            cls = 'have'
        elif surface in DO_FORM:
            cls = 'do'
        else:
            return None
        verb = self._following_verb(parent, node) if parent else None
        if verb is None or parent is None:
            return None
        got_label = VERB_FORM_LABEL.get(verb['type'], verb['type'])
        base = _base_form(verb)
        aux_s = node['surface']
        v_s = verb['surface']
        required = ('the base form' if cls in ('modal', 'do')
                    else 'the past participle' if cls == 'have'
                    else 'a participle (progressive or passive)')
        violation = (f"Auxiliary Verb-Form Conflict: the auxiliary '{aux_s}' requires the main "
                     f"verb in {required}, but '{v_s}' is {got_label}.")
        if cls in ('modal', 'do'):
            target = _preserve_case(v_s, base)
            suggested = (f"Change '{v_s}' to the base form '{target}' after "
                         f"'{aux_s}' ({'modal' if cls == 'modal' else 'do\u2011form'} auxiliary).")
            if cls == 'modal':
                alternative = (f"Or drop the modal '{aux_s}' and keep a finite verb, e.g. "
                               f"'{_preserve_case(v_s, _third_present(base))}' when the subject "
                               f"is third-person singular.")
            else:
                alternative = (f"Or rephrase to avoid 'do' + '{v_s}' (e.g. use a simple finite "
                               f"present or past verb).")
            outcome = f"MD/AUX + VB instead of MD/AUX + {verb['type']}"
        elif cls == 'have':
            target = _preserve_case(v_s, _vbn_form(base))
            suggested = (f"Change '{v_s}' to the past participle '{target}' after '{aux_s}', "
                         f"because a 'have'-form auxiliary requires a past participle.")
            alternative = None
            outcome = f"AUX(have) + VBN instead of AUX(have) + {verb['type']}"
        else:  # be
            target = _preserve_case(v_s, _vbg_form(base))
            suggested = (f"Change '{v_s}' to the present participle '{target}' after '{aux_s}' "
                         f"(or keep a past participle for a passive sentence).")
            alternative = None
            outcome = f"AUX(be) + VBG/VBN instead of AUX(be) + {verb['type']}"
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': alternative,
            'targeted_outcome': outcome,
        }

    def _rem_det_stack(self, node, parent):
        if parent is None:
            return None
        dets = [c for c in parent['children']
        if c['type'] in DET_CLASS or c['type'] == 'PRP$']
        if len(dets) < 2:
            return None
        keep = dets[0]['surface']
        extras = ', '.join(f"'{d['surface']}'" for d in dets[1:])
        return {
            'violation': (f"Determiner-Stacking Conflict: the NP '{parent['surface']}' contains "
                          f"more than one determiner."),
            'suggested_fix': f"Remove the extra determiner(s) {extras} and keep '{keep}'.",
            'alternative_fix': (f"Or merge the determiners into one (e.g. use a single "
                                f"possessive or quantifier instead of several)."),
            'targeted_outcome': "DT + NP (single determinative) instead of DT + DT + NP",
        }

    def _rem_mod_pos(self, node, parent):
        head = phrase_head(parent) if parent else None
        if head is None:
            return None
        return {
            'violation': (f"Modifier Placement Conflict: '{node['surface']}' appears after the "
                          f"head noun '{head['surface']}'."),
            'suggested_fix': (f"Move '{node['surface']}' so it precedes the head noun: NP "
                              f"modifiers come before their head (e.g. '{node['surface']} "
                              f"{head['surface']}')."),
            'alternative_fix': None,
            'targeted_outcome': f"Modifier + {head['type']} (head-final order) instead of "
                                f"{head['type']} + modifier",
        }

    def _rem_head_noun(self, node, parent):
        if parent is None:
            return None
        det_s = node['surface'] if node is not None else 'a determiner'
        return {
            'violation': (f"Head Noun Conflict: the NP '{parent['surface']}' contains the "
                          f"determiner/possessive '{det_s}' but no noun can head it."),
            'suggested_fix': (f"Add the noun that '{det_s}' modifies so the NP has a head, "
                              f"e.g. write '{det_s} idea' instead of using '{det_s}' alone."),
            'alternative_fix': (f"Or replace the whole phrase with a proper name or noun "
                                f"phrase that can stand as the argument."),
            'targeted_outcome': f"NP \u2192 {parent['type']} + NN instead of a bare determiner phrase",
        }

    @staticmethod
    def _pronoun_target(surf, objective_needed):
        if objective_needed:
            return {'i': 'me', 'we': 'us', 'he': 'him', 'she': 'her',
                    'they': 'them'}.get(surf)
        return {'me': 'I', 'us': 'we', 'him': 'he', 'her': 'she',
                'them': 'they'}.get(surf)

    def _rem_pronoun_case(self, node, parent):
        head = phrase_head(node) if node else None
        if head is None or head['type'] != 'PRP':
            return None
        surf = _lower(head['surface'])
        objective_needed = parent is not None and parent['type'] not in SENTENCE_CLASSES
        target = self._pronoun_target(surf, objective_needed)
        if target is None:
            return None
        position = 'object' if objective_needed else 'subject'
        demand = 'objective' if objective_needed else 'nominative'
        return {
            'violation': (f"Pronoun Case Conflict: '{head['surface']}' appears in {position} "
                          f"position but is the '{'objective' if not objective_needed else 'nominative'}' "
                          f"form."),
            'suggested_fix': (f"Change '{head['surface']}' to the {demand} form '{target}' "
                              f"because the {position} of a clause/preposition must be {demand}. "
                              f"(Write '{target}' instead of '{head['surface']}'.)"),
            'alternative_fix': (f"Or rewrite so the pronoun is not in {position} position "
                                f"(e.g. use a noun phrase instead of a pronoun)."),
            'targeted_outcome': f"PRP ({demand}) instead of PRP ({'objective' if not objective_needed else 'nominative'})",
        }

    def _rem_adj_adv(self, node, parent):
        if node is None:
            return None
        if node['type'] == 'ADJP':
            adj = phrase_head(node) or (node.get('children') or [None])[0]
            if adj is None:
                return None
            adv = self._adverbial_form(adj['surface'])
            wrong, right = adj['surface'], adv
        elif node['type'] == 'ADVP':
            adv_leaf = phrase_head(node)
            if adv_leaf is None:
                return None
            wrong, right = adv_leaf['surface'], self._adverbial_form(adv_leaf['surface'])
        else:  # adjective leaf inside an adverb phrase
            wrong, right = node['surface'], self._adverbial_form(node['surface'])
        return {
            'violation': (f"Adjective\u2013Adverb Confusion: '{wrong}' is an adjective form used "
                          f"where an adverb is required."),
            'suggested_fix': (f"Change '{wrong}' to the adverb '{right}' to modify the verb "
                              f"(verbs are modified by adverbs, not adjectives)."),
            'alternative_fix': (f"Or rephrase with an adjective predicated of the subject, e.g. "
                                f"change the verb so the adjective modifies a noun instead."),
            'targeted_outcome': "ADVP \u2192 RB (adverb) instead of ADVP/ADJP \u2192 JJ (adjective)",
        }

    def _rem_article(self, node, parent):
        if node is None:
            return None
        art = _indefinite_article(node['surface'])
        return {
            'violation': (f"Article Omission Conflict: the singular count noun "
                          f"'{node['surface']}' is used without a determiner in an argument "
                          f"position."),
            'suggested_fix': (f"Insert the indefinite article '{art}' before "
                              f"'{node['surface']}' \u2192 '{art} {node['surface']}'."),
            'alternative_fix': (f"Or use a definite/other determiner: 'the {node['surface']}', "
                                f"'this {node['surface']}', 'my {node['surface']}'."),
            'targeted_outcome': f"DT + NN (determined noun) instead of bare NN",
        }

    def _rem_article_mismatch(self, node, parent):
        if parent is None:
            return None
        leaves = _leaves_list(parent)
        idx = next((i for i, lf in enumerate(leaves) if lf['id'] == node['id']), None)
        if idx is None or idx + 1 >= len(leaves):
            return None
        nxt = leaves[idx + 1]['surface']
        need = _indefinite_article(nxt)
        if need == node['surface'].lower() or need not in ('a', 'an'):
            return None
        return {
            'violation': (f"Article Selection Conflict: '{node['surface']}' precedes "
                          f"'{nxt}', which starts with a "
                          f"{'vowel sound' if need == 'an' else 'consonant sound'}."),
            'suggested_fix': (f"Change '{node['surface']}' to '{'an' if need == 'an' else 'a'}' "
                              f"so the article matches the following sound "
                              f"(\u2192 '{need} {nxt} ...')."),
            'alternative_fix': None,
            'targeted_outcome': f"DT ({need}) + noun instead of DT ({node['surface']}) + noun",
        }

    @staticmethod
    def _rem_capitalization(node):
        words = node['surface'].split()
        if not words or not words[0]:
            return None
        first = words[0]
        rewritten = first[0].upper() + first[1:]
        return {
            'violation': (f"Capitalization Conflict: the sentence begins with lowercase "
                          f"'{first}'."),
            'suggested_fix': (f"Capitalize the first letter: '{first}' \u2192 '{rewritten}', "
                              f"so the sentence reads '{rewritten + ' ' + ' '.join(words[1:])}'."),
            'alternative_fix': None,
            'targeted_outcome': "Sentence-initial capital letter",
        }

    @staticmethod
    def _rem_quantifier(node, parent):
        word = _lower(node['surface'])
        if word not in ('less', 'fewer') or parent is None:
            return None
        head = _np_head(parent)
        noun_s = head['surface'] if head else 'the noun'
        if word == 'less':
            suggested = (f"Change '{node['surface']}' to 'fewer' because '{noun_s}' is a "
                         f"plural count noun: '{node['surface']} {noun_s}' \u2192 'fewer {noun_s}'.")
            alternative = (f"Or use an uncountable noun so '{node['surface']}' is licensed, "
                           f"e.g. '{node['surface']} information'.")
            outcome = f"fewer + NNS instead of less + {head['type'] if head else 'NNS'}"
        else:
            suggested = (f"Change '{node['surface']}' to 'less' because '{noun_s}' is a "
                         f"singular/uncountable noun: '{node['surface']} {noun_s}' \u2192 "
                         f"'less {noun_s}'.")
            alternative = (f"Or make the noun plural count, so 'fewer' is licensed: "
                           f"'{_plural_noun(_singular_noun(head))}'.")
            outcome = f"less + NN instead of fewer + {head['type'] if head else 'NN'}"
        return {
            'violation': (f"Quantifier\u2013Noun Agreement Conflict: '{node['surface']}' does "
                          f"not match the noun '{noun_s}'."),
            'suggested_fix': suggested,
            'alternative_fix': alternative,
            'targeted_outcome': outcome,
        }

    def _rem_double_comparative(self, node, parent):
        if parent is None:
            return None
        marker = node['surface'] if node is not None else 'more'
        sibling = None
        for c in parent['children']:
            if c['type'] in {'JJR', 'JJS'}:
                sibling = c
                break
        if sibling is None:
            return None
        return {
            'violation': (f"Double-Comparative Conflict: '{marker}' + '{sibling['surface']}' "
                          f"both express {'comparative' if sibling['type'] == 'JJR' else 'superlative'}."),
            'suggested_fix': (f"Use only the morphological form: '{sibling['surface']}' "
                              f"(drop '{marker}')."),
            'alternative_fix': (f"Or use only the degree marker on the positive form: "
                                f"'{marker} {sibling['surface'][1:]}' is not needed \u2014 prefer "
                                f"'{sibling['surface']}'."),
            'targeted_outcome': f"JJR/JJS alone instead of RBR/RBS + JJR/JJS",
        }

    def _rem_vp_head_noun(self, node, parent):
        noun_s = node['surface'] if node is not None else '?'
        return {
            'violation': (f"Verb-Head Conflict: the VP '{parent['surface'] if parent else ''}' "
                          f"is headed by the noun '{noun_s}' instead of a verb."),
            'suggested_fix': (f"Provide a real verb in the predicate: supply an auxiliary + "
                              f"participle (e.g. replace the noun '{noun_s}' with the matching "
                              f"verb form) so the VP is headed by a verb."),
            'alternative_fix': f"Write a full VP \u2192 V (verb) + complements instead of V \u2192 {node['type'] if node else 'NN'}.",
            'targeted_outcome': "VP \u2192 verb-headed structure",
        }

    def _rem_finite_verb(self, node, parent):
        vp_head = phrase_head(node) if node else None
        if vp_head is None:
            return None
        h = vp_head['surface']
        base = _base_form(vp_head)
        got = VERB_FORM_LABEL.get(vp_head['type'], vp_head['type'])
        finite = _preserve_case(h, _third_present(base))
        violation = (f"Clause Finiteness Conflict: the predicate verb '{h}' is {got}; a main "
                     f"clause requires a finite (tensed) verb.")
        if vp_head['type'] == 'VBG':
            suggested = (f"Make the clause finite: add the auxiliary 'is' before '{h}' "
                         f"(\u2192 'is {h}'), or change '{h}' to a finite form such as "
                         f"'{finite}'.")
            outcome = f"AUX(VBZ) + VBG (or a VBZ head) instead of {vp_head['type']}"
        elif vp_head['type'] == 'VBN':
            suggested = (f"Make the clause finite: add a finite form of 'be' before '{h}' "
                         f"(e.g. 'is {h}') for the passive, or use a finite auxiliary + "
                         f"participle.")
            outcome = f"AUX(VBZ) + VBN instead of {vp_head['type']}"
        else:  # VB base
            suggested = (f"Make '{h}' finite: change it to '{finite}' (third-person singular "
                         f"present) when the subject is singular, or add a finite auxiliary.")
            outcome = f"VBZ/VBP head instead of {vp_head['type']}"
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': None,
            'targeted_outcome': outcome,
        }

    def _rem_fragment(self, node):
        words = node['surface'].split()
        stripped = ' '.join(w for w in words
                            if not all(ch in '.,;:!?\u2018\u2019\u201c\u201d' for ch in w))
        example = f"'{stripped} runs.'" if stripped else "e.g. 'The boy runs.'"
        return {
            'violation': (f"Clause Finiteness Conflict: the input parses as a {node['type']} "
                          f"fragment, not a full clause \u2014 it has no finite predicate verb."),
            'suggested_fix': (f"Add a finite predicate verb to complete the clause: restructure "
                              f"the root so it is S \u2192 NP + VP, e.g. {example}."),
            'alternative_fix': None,
            'targeted_outcome': f"root S (NP + VP) instead of a {node['type']} fragment",
        }

    def _rem_generic(self, detail):
        label = CHECK_LABELS.get(detail['constraint'], detail['constraint'])
        return {
            'violation': detail['text'],
            'suggested_fix': (f"Adjust this constituent so that the {label} check is satisfied; "
                              f"see the focused Violation Breakdown above."),
            'alternative_fix': None,
            'targeted_outcome': None,
        }

    def _root_level(self, root):
        if root['type'] in SENTENCE_CLASSES:
            words = root['surface'].split()
            first = words[0] if words else ''
            if first and first[0].isalpha() and first[0].islower():
                self._detail(root, None, 'sentence capitalization', 'C-CAPITALIZATION',
                             'error',
                             f"The sentence begins with the lowercase word '{first}'; "
                             'sentences must start with a capital letter.')
                return
            self._detail(root, None, 'sentence root', 'C-ROOT', 'valid',
                         f"Root {root['type']} spans the full sentence '{root['surface']}'.")
            return
        self._detail(root, None, 'fragment root', 'C-TENSE-FINITE', 'error',
                     f"This input parses as a {root['type']} fragment, not a full clause (S). "
                     'The clause has no finite predicate verb, so the sentence is incomplete.')

    def _detail(self, node, parent, role, constraint, status, text):
        self.details[node['id']] = {
            'id': node['id'],
            'type': node['type'],
            'pos': node.get('pos'),
            'surface': node.get('surface', ''),
            'span': node['span'],
            'parent': parent['id'] if parent else None,
            'rule': _rule_for(node),
            'children_ids': [c['id'] for c in node['children']] if 'children' in node else [],
            'children': [{'id': c['id'], 'type': c['type'], 'surface': c.get('surface')}
                         for c in node['children']] if 'children' in node else [],
            'role': role,
            'constraint': constraint,
            'status': status,
            'text': text,
        }

    def _role_for(self, constraint):
        return {
            'C-SUBJECT-ROLE': 'clause subject',
            'C-PREDICATE': 'clause predicate',
            'C-SUBJECT-AGREEMENT': 'subject-verb agreement link',
            'C-HEAD-NOUN': 'head noun',
            'C-NOUN-ADJUNCT': 'noun adjunct',
            'C-DETERMINER': 'determiner',
            'C-DETERMINER-AGREEMENT': 'determiner-noun agreement link',
            'C-DET-STACK': 'determiner stacking',
            'C-MOD-POS': 'NP modifier position',
            'C-NP-POSTMODIFIER': 'postmodifier',
            'C-NP-REDUCED-RELATIVE': 'reduced relative clause',
            'C-NP-RELATIVE': 'relative clause',
            'C-COORDINATOR': 'coordinator',
            'C-HEAD-VERB': 'verb head',
            'C-INFINITIVAL-COMPLEMENT': 'infinitival complement',
            'C-INFINITIVAL-MARKER': 'infinitival marker',
            'C-AUXILIARY': 'auxiliary verb',
            'C-AUX-COMPLEMENT': 'auxiliary complement',
            'C-AUX-FORM': 'auxiliary-verb form',
            'C-TENSE-FINITE': 'finite predicate',
            'C-DIRECT-OBJECT': 'direct object',
            'C-ADJUNCT': 'VP modifier',
            'C-PREDICATE-ADJECTIVE': 'predicate adjective',
            'C-ADVERBIAL': 'adverbial modifier',
            'C-CLAUSAL-COMPLEMENT': 'clausal complement',
            'C-PARTICLE': 'verb particle',
            'C-HEAD-PREPOSITION': 'head preposition',
            'C-PREP-OBJECT': 'prepositional object',
            'C-HEAD-ADJECTIVE': 'head adjective',
            'C-INTENSIFIER': 'intensifier',
            'C-PARTICIPLE-MODIFIER': 'participle modifier',
            'C-HEAD-ADVERBIAL': 'head adverbial',
            'C-CLAUSE-SUBJECT': 'clause subject',
            'C-CLAUSE-PREDICATE': 'clause predicate',
            'C-CLAUSAL-ADVERBIAL': 'clausal adverbial',
            'C-RELATIVE-CLAUSE': 'relative/complement clause',
            'C-RELATIVE-HEAD': 'relative-clause head',
            'C-RELATIVE-PRONOUN': 'relative pronoun',
            'C-RELATIVE-NOUN': 'wh-phrase nominal head',
            'C-COMPLEMENTIZER': 'complementizer',
            'C-NP-COMPOUND': 'NP-internal phrase',
            'C-PUNCT': 'terminal punctuation',
            'C-ROOT': 'sentence root',
            'C-CAPITALIZATION': 'sentence capitalization',
            'C-PRONOUN-CASE': 'pronoun case',
            'C-ADJ-ADV': 'adjective-adverb confusion',
            'C-ARTICLE': 'article omission',
            'C-ARTICLE-MISMATCH': 'article selection',
            'C-QUANTIFIER': 'quantifier-noun agreement',
            'C-SMALL-CLAUSE': 'small-clause complement',
            'C-SMALL-CLAUSE-PREDICATE': 'small-clause predicate',
            'C-ADVERBIAL-COMPLEMENT': 'adverbial complement',
            'C-COMPARATIVE-DOUBLE': 'double comparative',
            'C-UNLISTED': 'unrated edge',
        }.get(constraint, 'unrated')

    def _summarize(self, root):
        edges = [d for nid, d in self.details.items() if nid != root['id']]
        valid = [d for d in edges if d['status'] == 'valid']
        errors = [d for d in edges if d['status'] == 'error']
        unlisted = [d for d in edges if d['status'] == 'unlisted']
        root_detail = self.details.get(root['id'])
        root_error = root_detail is not None and root_detail['status'] == 'error'
        violations = list(errors)
        if root_error:
            violations.append(root_detail)
        if root_error:
            message = root_detail['text']
        elif errors:
            message = errors[0]['text']
        else:
            message = (f"All {len(valid)} validated edge(s) are licensed by the matrix; "
                       'the sentence is grammatical.')
        return {
            'valid': len(violations) == 0,
            'valid_edges': len(valid),
            'violated_edges': len(errors),
            'violations': [d['id'] for d in errors],
            'unrated_edges': len(unlisted),
            'constraints_fired': sorted({d['constraint'] for d in violations}),
            'root_error': root_error,
            'explanation': message,
        }


def evaluate(root):
    return MatrixEvaluator().evaluate(root)