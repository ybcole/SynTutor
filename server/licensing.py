"""SynTutor Stage 5b: positive-evidence licensing.

WHY THIS EXISTS
---------------
Stage 5 (matrix.py + ruleset.py) is a *blacklist*: a sentence is "valid" when no
hand-written rule fires.  That makes absence-of-evidence indistinguishable from
grammaticality, and it inherits benepar's blind spot -- the parser is trained on
grammatical text and will happily give "I am stupids" or "the men are runned" a
clean tree.

This module adds three counter-measures, all deterministic:

1. LEXICAL LICENSING  -- every open-class word must be a form that the lexicon
   actually licenses *for the POS tag the parser gave it*
   (surface in paradigm(lemma, tag)).  ``stupids``, ``runned``, ``mans``,
   ``goed``, ``runing`` fail this no matter how the parser tags them, and no
   per-word blacklist entry is needed.
2. RELATIVE-CLAUSE RULES -- the rulebook entries 2.7 and 5.4 were registered but
   never implemented (``whose believe``, ``the boys who plays``, ``the man which``).
3. TRI-STATE VERDICT  -- "grammatical" now requires positive verification.  Words
   the lexicon cannot vouch for, or a checker that crashed, yield ``unverified``
   instead of silently counting as correct.

``collect_all`` replaces ``ruleset.collect`` and, unlike it, isolates every
checker so one exception can never wipe out all findings.
"""

from itertools import chain

from lemminflect import getAllInflections, getAllLemmas

try:  # package or script-dir import, same convention as matrix.py
    from . import ruleset
except ImportError:  # pragma: no cover
    import ruleset

_lower = ruleset._lower
_leaves = ruleset._leaves
_finding = ruleset._finding
_tree_evidence = ruleset._tree_evidence
_wordlist_evidence = ruleset._wordlist_evidence
_rem = ruleset._rem

# --------------------------------------------------------------------------- #
# Lexical licensing                                                           #
# --------------------------------------------------------------------------- #
PTB2UPOS = {
    'NN': 'NOUN', 'NNS': 'NOUN',
    'VB': 'VERB', 'VBD': 'VERB', 'VBG': 'VERB', 'VBN': 'VERB',
    'VBP': 'VERB', 'VBZ': 'VERB',
    'JJ': 'ADJ', 'JJR': 'ADJ', 'JJS': 'ADJ',
    'RB': 'ADV', 'RBR': 'ADV', 'RBS': 'ADV',
}
ALL_UPOS = ('NOUN', 'VERB', 'ADJ', 'ADV', 'AUX')

# Suffix families.  For a word the lexicon does not list we cannot trust the
# parser's tag (that is the whole problem), so the stem search tries every family
# -- but each family may only match a lemma of a compatible POS, so derivational
# forms (talent+ed, blog+er, smart+ly) are never mistaken for bad inflection.
#   's'       noun plural / verb 3sg / (illegal) adjective plural
#   'verbal'  -ed, -d, -ied, -ing  -> verbs only
#   'cmp'     -er / -est           -> adjectives, and only if tagged JJR/JJS
SUFFIX_FAMILIES = (
    ('ies', 'y', 's'), ('es', '', 's'), ('s', '', 's'),
    ('ied', 'y', 'verbal'), ('ed', '', 'verbal'), ('ed', 'e', 'verbal'),
    ('d', '', 'verbal'), ('ing', '', 'verbal'), ('ing', 'e', 'verbal'),
    ('ier', 'y', 'cmp'), ('er', '', 'cmp'), ('er', 'e', 'cmp'),
    ('iest', 'y', 'cmp'), ('est', '', 'cmp'), ('est', 'e', 'cmp'),
)
FAMILY_UPOS = {'s': ('NOUN', 'VERB', 'ADJ'), 'verbal': ('VERB',), 'cmp': ('ADJ',)}
OPEN_TAGS = {'NN', 'NNS', 'JJ', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}

# Words lemminflect cannot vouch for but that are unquestionably English:
# quantifiers the parser tags open-class, indefinite compound pronouns, the
# most common irregular plurals, high-frequency adverbs, and a handful of
# abbreviations.  Without this, perfectly clean sentences would degrade to
# 'unverified' (false positives), which is worse than a miss on a typo.
HIGH_FREQ = {
    # quantifiers / determiners benepar tags as NN/JJ
    'many', 'much', 'few', 'couple', 'several', 'both', 'each', 'either',
    'neither', 'all', 'some', 'any', 'enough', 'plenty', 'most', 'more',
    'less', 'least', 'numerous', 'various', 'such', 'several',
    # indefinite compound pronouns
    'everyone', 'everybody', 'everything', 'everywhere',
    'anyone', 'anybody', 'anything', 'anywhere',
    'someone', 'somebody', 'something', 'somewhere',
    'nobody', 'nothing', 'nowhere', 'noone',
    # irregular plurals lemminflect does not license as inflections
    'people', 'children', 'women', 'men', 'mice', 'teeth', 'feet', 'geese',
    # high-frequency adverbs / time words
    'here', 'there', 'now', 'then', 'today', 'tomorrow', 'yesterday', 'home',
    'soon', 'often', 'always', 'already', 'just', 'also', 'still', 'yet',
    'really', 'very', 'well', 'never', 'sometimes', 'usually', 'again',
    'almost', 'nearly', 'only', 'too', 'quite', 'rather', 'maybe', 'perhaps',
    # abbreviations / acronyms
    'tv', 'ok', 'okay',
}

_LEMMA_CACHE = {}
_FORMS_CACHE = {}


def _lemmas(word, upos):
    key = (word, upos)
    if key not in _LEMMA_CACHE:
        found = getAllLemmas(word, upos)
        _LEMMA_CACHE[key] = {lem for lems in found.values() for lem in lems}
    return _LEMMA_CACHE[key]


def _forms(lemma, upos):
    """{PTB tag: set(forms)} -- the full paradigm of ``lemma`` as ``upos``."""
    key = (lemma, upos)
    if key not in _FORMS_CACHE:
        forms = {t: set(fs) for t, fs in getAllInflections(lemma, upos).items()}
        # lemminflect lists only VBD for regular verbs (VBN is identical), so a
        # regular participle would wrongly look "unlicensed".  Fill the gap.
        if 'VBD' in forms and 'VBN' not in forms:
            forms['VBN'] = set(forms['VBD'])
        _FORMS_CACHE[key] = forms
    return _FORMS_CACHE[key]


def _paradigm_text(lemma, upos):
    forms = _forms(lemma, upos)
    seen, ordered = set(), []
    for fs in forms.values():
        for f in sorted(fs):
            if f not in seen:
                seen.add(f)
                ordered.append(f)
    return ordered


def _tag_group(tag):
    # VB and VBP are the same surface form; the parser flips between them freely.
    return ('VB', 'VBP') if tag in ('VB', 'VBP') else (tag,)


def _candidate_stems(low, tag):
    """[(stem, family)] for every way ``low`` could be stem + suffix."""
    out, seen = [], set()
    for suffix, repl, family in SUFFIX_FAMILIES:
        if family == 'cmp' and tag not in ('JJR', 'JJS'):
            continue
        if family != 'cmp' and tag not in OPEN_TAGS:
            continue
        if not low.endswith(suffix) or len(low) - len(suffix) < 2:
            continue
        base = low[:-len(suffix)] + repl
        variants = [base]
        # undouble: runn -> run, stopp -> stop
        if len(base) >= 3 and base[-1] == base[-2] and base[-1] not in 'aeiou':
            variants.append(base[:-1])
        for v in variants:
            if v != low and (v, family) not in seen:
                seen.add((v, family))
                out.append((v, family))
    return out


def _classify_leaf(low, tag, upos):
    """Return (status, info).

    status: 'licensed' | 'tag_mismatch' | 'malformed' | 'unknown'
    """
    tagged_upos = ('VERB', 'AUX') if upos == 'VERB' else (upos,)

    # 1. Is the surface a listed inflection of some lemma under the tagged POS?
    lemmas = {(lem, u) for u in tagged_upos for lem in _lemmas(low, u)}
    if lemmas:
        for lem, u in lemmas:
            f = _forms(lem, u)
            if any(low in f.get(t, ()) for t in _tag_group(tag)):
                return 'licensed', {'lemma': lem}
        lem, u = sorted(lemmas)[0]
        return 'tag_mismatch', {'lemma': lem, 'upos': u,
                                'paradigm': _paradigm_text(lem, u)}

    # 2. Listed under a *different* POS only -> the parser's tag is suspect.
    for u in ALL_UPOS:
        if u in tagged_upos:
            continue
        found = _lemmas(low, u)
        if found:
            lem = sorted(found)[0]
            return 'tag_mismatch', {'lemma': lem, 'upos': u,
                                    'paradigm': _paradigm_text(lem, u),
                                    'other_pos': True}

    # 3. Not in the lexicon at all.  Does it look like a *mis-built* inflection of
    #    a word the lexicon does know?  (stupid+s, run+ned, child+s, go+ed ...)
    malformed = []
    for stem, family in _candidate_stems(low, tag):
        order = [upos] + [u for u in ('VERB', 'NOUN', 'ADJ') if u != upos]
        for u in order:
            if u not in FAMILY_UPOS[family]:
                continue
            if stem in _lemmas(stem, u):
                allowed = set(chain.from_iterable(_forms(stem, u).values()))
                if low in allowed:
                    return 'licensed', {'lemma': stem, 'regular': True}
                malformed.append((stem, u))
    if malformed:
        stem, u = malformed[0]
        return 'malformed', {'lemma': stem, 'upos': u,
                             'paradigm': _paradigm_text(stem, u)}
    return 'unknown', {}


def _lex_rule(upos, tag):
    if upos == 'NOUN':
        return '1.1'
    if upos == 'VERB':
        return '1.6' if tag == 'VBN' else '1.5' if tag == 'VBD' else '1.4'
    if upos == 'ADJ':
        return '1.7'
    return '1.8'


def check_lexicon(leaves, skip_ids=frozenset()):
    """Lexical licensing over all open-class leaves.

    Returns (findings, stats).  ``skip_ids`` are leaves another rule already
    flagged as errors (avoids double-reporting the same word).
    """
    out = []
    stats = {'content': 0, 'licensed': 0, 'unverified': 0, 'malformed': 0}
    for i, lf in enumerate(leaves):
        tag = lf.get('type')
        surface = lf.get('surface') or ''
        upos = PTB2UPOS.get(tag)
        # A *lower-case* word the parser calls a proper noun is just an unknown
        # word wearing a costume: check it as a common noun.
        if tag in ('NNP', 'NNPS') and surface[:1].islower():
            upos, tag = 'NOUN', ('NNS' if tag == 'NNPS' else 'NN')
        if upos is None or not surface.isalpha():
            continue
        stats['content'] += 1
        low = surface.lower()
        if low in HIGH_FREQ:
            stats['licensed'] += 1
            continue
        status, info = _classify_leaf(low, tag, upos)

        if status == 'licensed':
            stats['licensed'] += 1
            continue
        if lf['id'] in skip_ids:
            stats['malformed'] += 1
            continue

        prev = _lower(leaves[i - 1]) if i else ''
        if status == 'malformed':
            stats['malformed'] += 1
            stem, u, para = info['lemma'], info['upos'], info['paradigm']
            tagged_forms = _forms(stem, u).get(tag)
            fix = sorted(tagged_forms)[0] if tagged_forms else None
            if u == 'ADJ' and tag in ('NN', 'NNS', 'JJ'):
                text = (f"'{surface}' is not a word form: '{stem}' is an adjective "
                        f"and takes no plural -s.")
                fix_text = (f"Use the bare adjective '{stem}' "
                            f"(e.g. 'I am {stem}'), or add a noun: '{stem} people'.")
            else:
                text = (f"'{surface}' is not a valid form of '{stem}'. "
                        f"Accepted forms: {', '.join(para)}.")
                fix_text = (f"Use '{fix}' ({tag})." if fix
                            else f"Choose the form you need from: {', '.join(para)}.")
            out.append(_finding(
                _lex_rule(upos, tag), 'error', 'C-LEXICON-MALFORMED', 'word form',
                lf['id'], text,
                _wordlist_evidence(surface, para,
                                   f"lexicon paradigm of '{stem}' ({u})"),
                _rem(f"'{surface}' is not in the paradigm of '{stem}'.", fix_text,
                     None, f"{tag} drawn from the paradigm of '{stem}'")))
        elif status == 'tag_mismatch':
            lem = info['lemma']
            # Participle slot (have/be + VBN) filled by a non-participle form:
            # 'had went', 'was ate'.  The aux makes the slot unambiguous.
            if (tag == 'VBN' and not info.get('other_pos')
                    and prev in (ruleset.BE_SURFACES | ruleset.HAVE_SURFACES)):
                stats['malformed'] += 1
                part = sorted(_forms(lem, info['upos']).get('VBN', ()))
                out.append(_finding(
                    '1.6', 'error', 'C-LEXICON-MALFORMED', 'verb form', lf['id'],
                    f"After '{leaves[i - 1]['surface']}' a past participle is "
                    f"required, but '{surface}' is not one"
                    + (f" (use '{part[0]}')." if part else '.'),
                    _wordlist_evidence(surface, part,
                                       f"lexicon paradigm of '{lem}' (VBN)")))
            else:
                stats['unverified'] += 1
                out.append(_finding(
                    '1.12', 'unverified', 'C-LEXICON-TAG-MISMATCH', 'word form',
                    lf['id'],
                    f"'{surface}' was tagged {tag}, but the lexicon lists it only "
                    f"as another form/part of speech; the parse may have "
                    f"normalised an error.",
                    _wordlist_evidence(surface, info['paradigm'],
                                       f"lexicon paradigm of '{lem}'")))
        else:  # unknown
            stats['unverified'] += 1
            out.append(_finding(
                '1.12', 'unverified', 'C-LEXICON-UNKNOWN', 'spelling', lf['id'],
                f"'{surface}' is not in the lexicon, so its form could not be "
                f"verified (misspelling, name, or new word).",
                _wordlist_evidence(surface, [], 'lexicon (not found)')))

        # Adverb formation: happyly -> happily (adjective + -ly on a -y stem).
        # Handled here because the lexicon cannot derive adverbs.
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        if lf.get('type') in ('RB', 'RBR', 'RBS') and low.endswith('yly') \
                and lf['id'] not in skip_ids \
                and not any(f['node_id'] == lf['id'] and f['status'] == 'error'
                            for f in out):
            fix = low[:-3] + 'ily'
            out.append(_finding('1.8', 'error', 'C-ADVERB-FORM', 'adverb form',
                                lf['id'],
                                f"Adverb-formation error: '{lf['surface']}' "
                                f"\u2192 '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   '-y adjective + -ly rule')))
    return out, stats


# --------------------------------------------------------------------------- #
# Relative clauses: rules 2.7 and 5.4 (registered in RULEBOOK, never coded)    #
# --------------------------------------------------------------------------- #
HUMAN_ANTECEDENTS = {
    'man', 'men', 'woman', 'women', 'boy', 'boys', 'girl', 'girls', 'person',
    'people', 'persons', 'child', 'children', 'teacher', 'teachers', 'student',
    'students', 'friend', 'friends', 'doctor', 'doctors', 'mother', 'father',
    'brother', 'sister', 'parents', 'kids', 'someone', 'anyone', 'everyone',
    'everybody', 'somebody', 'anybody', 'nobody', 'those', 'neighbor',
    'neighbour', 'lady', 'gentleman', 'worker', 'workers',
}
NONHUMAN_ANTECEDENTS = {
    'book', 'books', 'car', 'cars', 'table', 'chair', 'house', 'houses', 'dog',
    'cat', 'idea', 'ideas', 'plan', 'plans', 'city', 'phone', 'computer',
    'movie', 'song', 'thing', 'things', 'rain', 'weather', 'stone',
}
VERB_START = {'VB', 'VBD', 'VBP', 'VBZ', 'MD', 'IN', 'TO'}
SG_FINITE = {'is', 'was', 'has', 'does'}
PL_FINITE = {'are', 'were', 'have', 'do'}
SWAP_NUMBER = {'is': 'are', 'are': 'is', 'was': 'were', 'were': 'was',
               'has': 'have', 'have': 'has', 'does': 'do', 'do': 'does'}


def _parent_map(root):
    parents = {}
    stack = [root]
    while stack:
        node = stack.pop()
        for c in node.get('children', []):
            parents[c['id']] = node
            stack.append(c)
    return parents


def _antecedent_number(np_node):
    """'sg' / 'pl' / None for the NP a relative clause modifies."""
    kids = np_node.get('children', [])
    if any(c.get('type') in ('CC', 'CONJP', 'UCP') for c in kids):
        return 'pl'
    pp_ids = {lf['id'] for c in kids if c.get('type') == 'PP' for lf in _leaves(c)}
    nouns = [lf for lf in _leaves(np_node)
             if lf['id'] not in pp_ids
             and lf.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP')]
    if nouns:
        return ruleset._num_of(nouns[-1])
    first = _leaves(np_node)[0] if _leaves(np_node) else None
    if first is not None:
        w = _lower(first)
        if w in ('those', 'these'):
            return 'pl'
        if w in ('that', 'this'):
            return 'sg'
    return None


def _first_finite(vp):
    for lf in _leaves(vp):
        if lf.get('type') in ('VBZ', 'VBP') or _lower(lf) in SG_FINITE | PL_FINITE:
            return lf
        if lf.get('type') in ('VBD', 'MD'):
            return None  # person/number-neutral
    return None


def check_relatives(root):
    out = []
    leaves = _leaves(root)
    parents = _parent_map(root)

    # --- 5.4  'whose' must be followed by the noun it possesses -------------- #
    for i, lf in enumerate(leaves):
        if _lower(lf) != 'whose' or i == 0 or i + 1 >= len(leaves):
            continue
        prev, nxt = leaves[i - 1], leaves[i + 1]
        relative_use = prev.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'DT') \
            or _lower(prev) in HUMAN_ANTECEDENTS
        if relative_use and nxt.get('type') in VERB_START:
            out.append(_finding(
                '5.4', 'error', 'C-RELATIVE-POSSESSIVE', 'relative pronoun',
                lf['id'],
                f"'whose' is a possessive relative: it must be followed by the noun "
                f"it possesses ('{prev['surface']} whose friends {nxt['surface']} "
                f"...'). Here it is followed directly by the verb '{nxt['surface']}'.",
                _tree_evidence(lf['id'], 'WHNP(WP$) with no possessed noun',
                               [{'node': lf['id']}, {'node': nxt['id']}]),
                _rem(f"'whose' + verb '{nxt['surface']}' has no possessed noun.",
                     f"To refer to the people themselves use 'who': "
                     f"'{prev['surface']} who {nxt['surface']} ...'.",
                     f"Or keep 'whose' and supply the noun: "
                     f"'{prev['surface']} whose [noun] {nxt['surface']} ...'.",
                     'WHNP(WP who) + S(VP) or WHNP(WP$ whose + NN) + S')))

    # --- 5.4  who / which choice ---------------------------------------------- #
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        if low not in ('which', 'who') or i == 0:
            continue
        prev = _lower(leaves[i - 1])
        if low == 'which' and prev in HUMAN_ANTECEDENTS:
            out.append(_finding(
                '5.4', 'error', 'C-RELATIVE-PRONOUN', 'relative pronoun', lf['id'],
                f"'which' does not refer to people; use 'who' (or 'that') after "
                f"'{leaves[i - 1]['surface']}'.",
                _tree_evidence(lf['id'], 'human antecedent + which',
                               [{'node': leaves[i - 1]['id']}, {'node': lf['id']}])))
        elif low == 'who' and prev in NONHUMAN_ANTECEDENTS:
            out.append(_finding(
                '5.4', 'error', 'C-RELATIVE-PRONOUN', 'relative pronoun', lf['id'],
                f"'who' refers to people; use 'which' (or 'that') after "
                f"'{leaves[i - 1]['surface']}'.",
                _tree_evidence(lf['id'], 'non-human antecedent + who',
                               [{'node': leaves[i - 1]['id']}, {'node': lf['id']}])))

    # --- 2.7  subject-gap relative: verb agrees with the antecedent ------------ #
    for node in _iter(root):
        kids = node.get('children', [])
        for idx, sbar in enumerate(kids):
            if sbar.get('type') != 'SBAR':
                continue
            sk = sbar.get('children', [])
            if not sk or sk[0].get('type') != 'WHNP':
                continue
            wh = _leaves(sk[0])
            if not wh or wh[0].get('type') not in ('WP', 'WDT'):
                continue  # 'whose' handled above
            clause = next((c for c in sk if c.get('type') == 'S'), None)
            if clause is None or not clause.get('children') \
                    or clause['children'][0].get('type') != 'VP':
                continue  # object-gap relative: the clause has its own subject
            ante = next((k for k in reversed(kids[:idx])
                         if k.get('type') == 'NP'), None)
            if ante is None:
                continue
            num = _antecedent_number(ante)
            verb = _first_finite(clause['children'][0])
            if num is None or verb is None:
                continue
            vlow = _lower(verb)
            v_sg = verb.get('type') == 'VBZ' or vlow in SG_FINITE
            v_pl = verb.get('type') == 'VBP' or vlow in PL_FINITE
            if (num == 'pl' and v_sg) or (num == 'sg' and v_pl):
                if vlow in SWAP_NUMBER:
                    fix = SWAP_NUMBER[vlow]
                else:
                    lem = next(iter(sorted(_lemmas(vlow, 'VERB'))), None)
                    want = 'VBP' if num == 'pl' else 'VBZ'
                    forms = _forms(lem, 'VERB').get(want, ()) if lem else ()
                    fix = sorted(forms)[0] if forms else None
                out.append(_finding(
                    '2.7', 'error', 'C-RELATIVE-AGREE', 'relative clause',
                    verb['id'],
                    f"The relative pronoun '{wh[0]['surface']}' takes its number "
                    f"from the antecedent '{ante['surface']}' "
                    f"({'plural' if num == 'pl' else 'singular'}), but the verb "
                    f"'{verb['surface']}' is "
                    f"{'singular' if v_sg else 'plural'}.",
                    _tree_evidence(sbar['id'], 'antecedent NP + SBAR(WHNP S(VP))',
                                   [{'node': ante['id']}, {'node': verb['id']}]),
                    _rem(f"'{ante['surface']} {wh[0]['surface']} {verb['surface']}': "
                         f"antecedent and verb disagree.",
                         (f"Change '{verb['surface']}' to '{fix}'." if fix
                          else "Make the verb agree with the antecedent."),
                         None, 'verb agrees with the antecedent of the relative')))
    return out


def _iter(node):
    yield node
    for c in node.get('children', []):
        yield from _iter(c)


# --------------------------------------------------------------------------- #
# Entry point: isolated checkers (replaces ruleset.collect)                    #
# --------------------------------------------------------------------------- #
def collect_all(text, root):
    """Run every checker in isolation.

    Returns (findings, checker_errors, lex_stats).  A crashing checker is
    reported in ``checker_errors`` (and downgrades the verdict to 'unverified')
    instead of silently discarding every other finding.
    """
    leaves = _leaves(root)
    clauses = ruleset._clauses(root)
    findings, errors = [], []

    def run(name, fn):
        try:
            findings.extend(fn())
        except Exception as exc:  # noqa: BLE001 - isolation is the point
            errors.append({'checker': name, 'error': f'{type(exc).__name__}: {exc}'})

    run('ruleset.wordlists', lambda: ruleset._check_wordlists(leaves))
    run('ruleset.basic', lambda: ruleset._check_basic(root, clauses, leaves))
    run('ruleset.adjective_adverb', lambda: ruleset._check_adjective_adverb(leaves))
    run('ruleset.tree', lambda: ruleset._check_tree(root, clauses, leaves, text))
    run('ruleset.more', lambda: ruleset._check_more(root, clauses, leaves))
    run('ruleset.context', lambda: ruleset._check_context(root, clauses, leaves))
    run('licensing.relatives', lambda: check_relatives(root))

    flagged = {f['node_id'] for f in findings if f['status'] == 'error'}
    stats = {'content': 0, 'licensed': 0, 'unverified': 0, 'malformed': 0}
    try:
        lex, stats = check_lexicon(leaves, skip_ids=flagged)
        findings.extend(lex)
    except Exception as exc:  # noqa: BLE001
        errors.append({'checker': 'licensing.lexicon',
                       'error': f'{type(exc).__name__}: {exc}'})
    return findings, errors, stats
