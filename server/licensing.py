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
import spellcheck

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
    'less', 'least', 'numerous', 'various', 'such', 'other', 'others',
    'another', 'same', 'own', 'next', 'last', 'former', 'latter', 'else',
    'certain', 'different', 'similar', 'single', 'double', 'triple', 'half',
    'whole', 'entire', 'extra', 'further', 'additional',
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
    'tv', 'ok', 'okay', 'pm', 'am', 'etc', 'vs',
}

_HYPHEN_PREFIXES = {
    'ex', 'co', 'non', 'pre', 'post', 're', 'self', 'anti', 'sub', 'multi',
    'semi', 'mid', 'pro', 'vice', 'super', 'inter', 'auto', 'bio', 'eco',
    'geo', 'micro', 'macro', 'mini', 'mega', 'neo', 'pseudo', 'quasi',
    'ultra', 'over', 'under', 'cross', 'counter', 'well', 'long', 'short',
    'full', 'part', 'high', 'low', 'old', 'new', 'second', 'third', 'so',
}

_VALID_DERIVED_WORDS = {
    'oncologist', 'oncologists', 'mentee', 'mentees', 'attendee', 'attendees',
    'interviewee', 'interviewees', 'trainee', 'trainees', 'employee', 'employees',
    'refugee', 'refugees', 'nominee', 'nominees', 'detainee', 'detainees',
    'cardiologist', 'cardiologists', 'neurologist', 'neurologists',
    'dermatologist', 'dermatologists', 'pediatrician', 'pediatricians',
    'psychiatrist', 'psychiatrists', 'optometrist', 'optometrists',
    'anesthesiologist', 'anesthesiologists', 'epidemiologist', 'epidemiologists',
    'wastefulness', 'mindfulness', 'thoughtfulness', 'helplessness',
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


# Standard irregular past participles that lemminflect omits from the VBN
# paradigm of their lemma, so the participle-slot check would misreport them.
EXTRA_PARTICIPLES = {'lit', 'lighted', 'hidden', 'hung', 'shown', 'spelt',
                     'dreamt', 'learnt', 'burnt', 'woken', 'broadcast',
                     'burst', 'slit', 'widened'}
# Directional/locational adverbs the lexicon lists only as nouns or
# prepositions.  They are normal RB terminals, so do not downgrade them to
# "unverified" when the parser tags them RB.
EXTRA_ADVERBS = {
    'inside', 'outside', 'upstairs', 'downstairs', 'overseas', 'underground',
    'ahead', 'abroad', 'back', 'forward', 'backward', 'backwards',
    'forwards', 'upward', 'downward', 'upwards', 'downwards', 'afterward',
    'afterwards', 'sideways', 'lengthwise',
}


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
        non_self = [(lem, u) for (lem, u) in lemmas if lem != low]
        lem, u = sorted(non_self or lemmas)[0]
        return 'tag_mismatch', {'lemma': lem, 'upos': u,
                                'paradigm': _paradigm_text(lem, u)}

    # 2. Listed under a *different* POS only -> the parser's tag is suspect.
    for u in ALL_UPOS:
        if u in tagged_upos:
            continue
        found = _lemmas(low, u)
        if found:
            non_self = [leaf for leaf in found if leaf != low]
            lem = sorted(non_self or found)[0]
            return 'tag_mismatch', {'lemma': lem, 'upos': u,
                                    'paradigm': _paradigm_text(lem, u),
                                    'other_pos': True}

    # 3. Not in the lexicon at all.  Before flagging as a mis-built inflection
    #    of another lemma (e.g., mistaking BrE/loanword 'artistes' for 'artist+es'
    #    or BrE 'colour'/'programmes'/'travelling' as malformed), check exact
    #    dictionary / high-frequency SymSpell membership while never exempting
    #    known ungrammatical forms (pluralized mass nouns, regularized irregulars).
    _KNOWN_BAD_LEX = (
        ruleset.UNCOUNTABLE_PLURAL
        | set(ruleset.ORAL_PAST_REGULARIZED)
        | set(ruleset.IRREGULAR_PART_REGULARIZED)
        | set(ruleset.IRREGULAR_COMPARATIVE)
        | set(ruleset.VERB_ENDING_FIX)
    )
    if low not in _KNOWN_BAD_LEX:
        dict_words = spellcheck._load_words()
        sym_engine = spellcheck._get_symspell()
        sym_count = sym_engine.words.get(low, 0) if sym_engine is not None else 0
        exact_dict = low in dict_words
        regular_s_of_dict_noun = (
            low.endswith('s') and len(low) > 4 and low[:-1] in dict_words
            and tag in ('NNS', 'VBZ', 'NN')
            and not _lemmas(low[:-1], 'ADJ')
        )
        if exact_dict or sym_count >= 200_000 or regular_s_of_dict_noun:
            return 'licensed', {'lemma': low, 'dictionary': True}

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
    # 4. Pluralized comparative adjectives ('smallers', 'olders', 'cheapers',
    #    'biggers') are never valid English plural nouns when the stem is an
    #    inflected JJR comparative adjective with no noun lemma.
    if (tag in ('NNS', 'NN', 'JJ', 'JJR') and low.endswith('ers') and len(low) >= 6):
        stem = low[:-1]  # e.g. 'smaller', 'older', 'cheaper'
        if not _lemmas(stem, 'NOUN'):
            adj_lems = _lemmas(stem, 'ADJ')
            if adj_lems and any(stem in _forms(al, 'ADJ').get('JJR', ()) for al in adj_lems):
                return 'malformed', {'lemma': stem, 'upos': 'ADJ',
                                     'paradigm': _paradigm_text(sorted(adj_lems)[0], 'ADJ')}
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
        if spellcheck.has_name_evidence(lf) or lf.get('contraction_auxiliary'):
            continue
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
        if upos == 'ADV' and low in EXTRA_ADVERBS:
            stats['licensed'] += 1
            continue
        status, info = _classify_leaf(low, tag, upos)

        if status == 'licensed':
            stats['licensed'] += 1
            continue
        # A gerund used as a noun ('dancing', 'cooking') is a licensed NP head
        # even when benepar tags it NN/NNS: the lexicon only lists the VBG form.
        if (status == 'tag_mismatch' and tag in ('NN', 'NNS')
                and info.get('upos') == 'VERB'
                and low in _forms(info['lemma'], 'VERB').get('VBG', ())):
            stats['licensed'] += 1
            continue
        # Valid participial adjectives (past participles 'hidden', 'delighted',
        # 'broken' and present participles 'exciting', 'interesting') tagged JJ
        # by Benepar are standard English adjectives even when lemminflect only
        # lists them under VERB.
        if (status == 'tag_mismatch' and tag == 'JJ'
                and info.get('upos') == 'VERB'):
            vforms = _forms(info['lemma'], 'VERB')
            if (low in vforms.get('VBN', ())
                    or low in vforms.get('VBG', ())
                    or low in EXTRA_PARTICIPLES):
                stats['licensed'] += 1
                continue
        # Valid comparative/superlative flat adverbs ('sell it cheaper', 'run
        # faster', 'speak louder') tagged RBR/RBS by Benepar are licensed when
        # lemminflect lists the surface as a JJR/JJS form of an ADJ lemma.
        if (status == 'tag_mismatch' and tag in ('RBR', 'RBS')
                and info.get('upos') == 'ADJ'):
            adj_tag = 'JJR' if tag == 'RBR' else 'JJS'
            if low in _forms(info['lemma'], 'ADJ').get(adj_tag, ()):
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
            if tagged_forms:
                regular = {stem + 'd', stem + 'ed', stem}
                strong = [f for f in tagged_forms if f not in regular]
                fix = sorted(strong or tagged_forms)[0]
            else:
                fix = None
            if u == 'ADJ' and tag in ('NN', 'NNS', 'JJ'):
                text = (f"The word '{surface}' is not a real word form: "
                        f"'{stem}' is an adjective and takes no '-s'.")
                fix_text = (f"Replace '{surface}' with the bare adjective '{stem}', "
                            f"which takes no '-s': write 'I am {stem}' or "
                            f"'{stem} people' instead.")
            else:
                text = (f"'{surface}' is not a valid form of '{stem}'. "
                        f"Accepted forms: {', '.join(para)}.")
                fix_text = (f"Replace '{surface}' with '{fix}'." if fix
                            else f"Choose the needed form of '{stem}' from: "
                                 f"{', '.join(para)}.")
            out.append(_finding(
                _lex_rule(upos, tag), 'error', 'C-LEXICON-MALFORMED', 'word form',
                lf['id'], text,
                _wordlist_evidence(surface, para,
                                   f"forms of '{stem}' ({u})"),
                _rem(f"'{surface}' is not a correct form of '{stem}'.", fix_text,
                     None, f"{tag} taken from the forms of '{stem}'")))
        elif status == 'tag_mismatch':
            # Hyphenated compound prefix ('ex-boyfriends', 'co-author', 'non-profit')
            # or right-hand stem after a hyphen ('non-stop' -> 'stop' tagged JJ).
            nxt_tok = leaves[i + 1] if i + 1 < len(leaves) else None
            prev_tok = leaves[i - 1] if i > 0 else None
            if (low in _HYPHEN_PREFIXES and nxt_tok is not None
                    and (nxt_tok.get('surface') == '-' or nxt_tok.get('type') == 'HYPH')):
                stats['licensed'] += 1
                continue
            if (prev_tok is not None
                    and (prev_tok.get('surface') == '-' or prev_tok.get('type') == 'HYPH')
                    and tag in ('JJ', 'NN', 'NNS') and info.get('other_pos')):
                stats['licensed'] += 1
                continue
            # Nominalized adjective after 'the' ('in the open', 'the poor', 'the unknown')
            if (tag == 'NN' and info.get('other_pos') and prev == 'the'
                    and _lemmas(low, 'ADJ')):
                stats['licensed'] += 1
                continue
            lem = info['lemma']
            vforms = _forms(lem, 'VERB') if info.get('upos') == 'VERB' else {}
            vbn_set = set(vforms.get('VBN', ())) | ({low} if low in EXTRA_PARTICIPLES else set())
            vbd_set = set(vforms.get('VBD', ()))
            vb_set = set(vforms.get('VB', ()))
            # Valid base/present verb form mistagged as VBD by Benepar after a
            # long relative clause ('those skirts that annoyed Kayla stun Dan'):
            # the surface is a licensed finite present form, not an unverified word.
            if (info.get('upos') == 'VERB' and not info.get('other_pos')
                    and tag == 'VBD' and low in vb_set):
                stats['licensed'] += 1
                continue
            det_prev = prev in {
                'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my',
                'your', 'his', 'her', 'its', 'our', 'their', 'some', 'any',
                'every', 'each', 'many', 'several', 'few', 'no', 'all', 'both',
            }
            nxt_leaf = leaves[i + 1] if i + 1 < len(leaves) else None
            nxt_is_noun = nxt_leaf is not None and nxt_leaf.get('type') in (
                'NN', 'NNS', 'NNP', 'NNPS', 'JJ')
            # 1. Participle slot (have/be + VBN) filled by a non-participle form
            #    ('had went', 'was ate') OR prenominal adjective slot filled by a
            #    strictly simple-past-only verb ('the hid glass', 'the wore hats',
            #    'the broke dishes', 'the took rabbit').
            is_aux_participle = (
                tag == 'VBN' and not info.get('other_pos')
                and prev in (ruleset.BE_SURFACES | ruleset.HAVE_SURFACES)
            )
            is_prenominal_past_for_participle = (
                info.get('upos') == 'VERB'
                and tag in ('JJ', 'VBN', 'VBD')
                and det_prev and nxt_is_noun
                and low in vbd_set and low not in vbn_set
                and low not in vb_set
                and low not in EXTRA_PARTICIPLES
                and not _lemmas(low, 'ADJ')
            )
            is_bare_participle_as_past = (
                info.get('upos') == 'VERB'
                and tag in ('VBD', 'VBP', 'VBZ')
                and prev not in (ruleset.BE_SURFACES | ruleset.HAVE_SURFACES
                                 | ruleset.DO_SURFACES | {'to', 'not', "n't"})
                and (low in vforms.get('VBN', ()) or low in EXTRA_PARTICIPLES)
                and low not in vbd_set and low not in vb_set
                and bool(vbd_set)
            )
            if is_aux_participle:
                if surface.lower() in EXTRA_PARTICIPLES:
                    stats['licensed'] += 1
                    continue
                stats['malformed'] += 1
                raw = sorted(_forms(lem, info['upos']).get('VBN', ()))
                regular = {lem + 'd', lem + 'ed', lem}
                strong = [p for p in raw if p not in regular]
                part = tuple(strong or raw)
                fix_word = part[0] if part else None
                rem = ({
                    'suggested_fix': f"Change '{surface}' to '{fix_word}'.",
                    'edits': [{'node': lf['id'], 'replacement': fix_word}],
                } if fix_word else None)
                out.append(_finding(
                    '1.6', 'error', 'C-LEXICON-MALFORMED', 'verb form', lf['id'],
                    f"After '{leaves[i - 1]['surface']}', the verb needs its past "
                    f"participle form, but '{surface}' is not one"
                    + (f" (use '{fix_word}')." if fix_word else '.'),
                    _wordlist_evidence(surface, part,
                                       f"forms of '{lem}' (VBN)"),
                    remediation=rem))
            elif is_prenominal_past_for_participle:
                stats['malformed'] += 1
                raw_vbn = sorted(vforms.get('VBN', ()))
                if not raw_vbn and lem == 'hide':
                    raw_vbn = ['hidden']
                regular = {lem + 'd', lem + 'ed', lem}
                strong = [p for p in raw_vbn if p not in regular]
                part = tuple(strong or raw_vbn)
                fix_word = part[0] if part else None
                rem = ({
                    'suggested_fix': f"Change '{surface}' to '{fix_word}'.",
                    'edits': [{'node': lf['id'], 'replacement': fix_word}],
                } if fix_word else None)
                out.append(_finding(
                    '1.6', 'error', 'C-VERB-FORM', 'verb form', lf['id'],
                    f"'{surface}' is the simple past form of '{lem}', not the past "
                    f"participle needed before a noun"
                    + (f"; use '{fix_word}' instead." if fix_word else '.'),
                    _wordlist_evidence(surface, part, f"forms of '{lem}' (VBN)"),
                    remediation=rem))
            elif is_bare_participle_as_past:
                stats['malformed'] += 1
                raw_vbd = sorted(vbd_set)
                fix_word = raw_vbd[0] if raw_vbd else None
                rem = ({
                    'suggested_fix': f"Change '{surface}' to '{fix_word}'.",
                    'edits': [{'node': lf['id'], 'replacement': fix_word}],
                } if fix_word else None)
                out.append(_finding(
                    '1.5', 'error', 'C-VERB-FORM', 'verb form', lf['id'],
                    f"'{surface}' is a past participle of '{lem}' and cannot stand "
                    f"alone as the main past-tense verb"
                    + (f"; use '{fix_word}' instead (or add 'has'/'had')." if fix_word else '.'),
                    _wordlist_evidence(surface, tuple(raw_vbd), f"forms of '{lem}' (VBD)"),
                    remediation=rem))
            else:
                stats['unverified'] += 1
                out.append(_finding(
                    '1.12', 'unverified', 'C-LEXICON-TAG-MISMATCH', 'word form',
                    lf['id'],
                    f"'{surface}' is not the word form this sentence needs, but "
                    f"the lexicon lists it only as another form of '{lem}'; its "
                    f"form could not be verified.",
                    _wordlist_evidence(surface, info['paradigm'],
                                       f"forms of '{lem}'")))
        else:  # unknown
            if spellcheck.known_word(low) or low in _VALID_DERIVED_WORDS:
                stats['licensed'] += 1
                continue
            # Hyphenated compound prefix ('non-stop', 'ex-husband', 'co-author')
            # or right-hand stem after a hyphen ('non-stop' -> 'stop' tagged JJ).
            nxt_tok = leaves[i + 1] if i + 1 < len(leaves) else None
            prev_tok = leaves[i - 1] if i > 0 else None
            if (low in _HYPHEN_PREFIXES and nxt_tok is not None
                    and (nxt_tok.get('surface') == '-' or nxt_tok.get('type') == 'HYPH')):
                stats['licensed'] += 1
                continue
            if (prev_tok is not None
                    and (prev_tok.get('surface') == '-' or prev_tok.get('type') == 'HYPH')
                    and (spellcheck.known_word(low) or any(_lemmas(low, u) for u in ALL_UPOS))):
                stats['licensed'] += 1
                continue
            # Regular plural of a known English noun ('oncologists' -> 'oncologist',
            # 'cafes' -> 'cafe')
            if tag == 'NNS' and len(low) >= 4:
                sg_cands = []
                if low.endswith('ies'):
                    sg_cands.append(low[:-3] + 'y')
                if low.endswith('es'):
                    sg_cands.append(low[:-2])
                if low.endswith('s'):
                    sg_cands.append(low[:-1])
                if any(spellcheck.known_word(c) or c in _VALID_DERIVED_WORDS
                       or bool(_lemmas(c, 'NOUN')) for c in sg_cands):
                    stats['licensed'] += 1
                    continue
            # Capitalized proper name mistagged NN at sentence start ('Candice skated...')
            if (tag == 'NN' and surface[:1].isupper() and surface[1:].islower()
                    and len(low) >= 3 and low in ruleset.GENDERED_FIRST_NAMES):
                stats['licensed'] += 1
                continue
            # Confident SymSpell typo repair on a lowercase non-proper word
            # resolves an avoidable 'unverified' into a rule-backed C-SPELLING
            # finding with an executable edit.
            if (surface.islower() and lf.get('fpos') == upos
                    and lf.get('fdep') not in {'compound', 'amod', 'appos'}):
                corr = spellcheck.strong_typo_candidate(low)
                if corr and _lemmas(corr, upos) and spellcheck.known_word(corr):
                    stats['malformed'] += 1
                    out.append(_finding(
                        '1.11', 'error', 'C-SPELLING', 'spelling', lf['id'],
                        f"'{surface}' appears to be misspelled; use '{corr}' instead.",
                        _wordlist_evidence(surface, [corr], 'spelling dictionary'),
                        remediation={
                            'suggested_fix': f"Change '{surface}' to '{corr}'.",
                            'edits': [{'node': lf['id'], 'replacement': corr}],
                        }))
                    continue
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
                                f"'{lf['surface']}' is not a real adverb: adverbs made "
                                f"from adjectives ending in -y take the form "
                                f"'{fix}'.",
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
    'neighbour', 'lady', 'ladies', 'gentleman', 'gentlemen', 'worker', 'workers',
    'administrator', 'administrators', 'professor', 'professors', 'thief',
    'thieves', 'burglar', 'burglars', 'driver', 'drivers', 'nurse', 'nurses',
    'lawyer', 'lawyers', 'judge', 'judges', 'officer', 'officers', 'engineer',
    'engineers', 'scientist', 'scientists', 'researcher', 'researchers',
    'author', 'authors', 'writer', 'writers', 'artist', 'artists', 'singer',
    'singers', 'actor', 'actors', 'actress', 'actresses', 'chef', 'chefs',
    'waiter', 'waiters', 'waitress', 'waitresses', 'manager', 'managers',
    'director', 'directors', 'president', 'presidents', 'king', 'kings',
    'queen', 'queens', 'prince', 'princess', 'boss', 'bosses', 'colleague',
    'colleagues', 'classmate', 'classmates', 'teammate', 'teammates', 'partner',
    'partners', 'husband', 'husbands', 'wife', 'wives', 'son', 'sons',
    'daughter', 'daughters', 'baby', 'babies', 'kid', 'teenager', 'teenagers',
    'adult', 'adults', 'citizen', 'citizens', 'customer', 'customers', 'guest',
    'guests', 'neighbors', 'neighbours', 'passenger', 'passengers', 'patient',
    'patients', 'player', 'players', 'soldier', 'soldiers', 'athlete',
    'athletes', 'clerk', 'clerks', 'guard', 'guards',
}
NONHUMAN_ANTECEDENTS = {
    'book', 'books', 'car', 'cars', 'table', 'tables', 'chair', 'chairs',
    'house', 'houses', 'dog', 'dogs', 'cat', 'cats', 'idea', 'ideas', 'plan',
    'plans', 'city', 'cities', 'phone', 'phones', 'computer', 'computers',
    'movie', 'movies', 'song', 'songs', 'thing', 'things', 'rain', 'weather',
    'stone', 'stones', 'tree', 'trees', 'road', 'roads', 'street', 'streets',
    'building', 'buildings', 'door', 'doors', 'window', 'windows', 'key',
    'keys', 'bag', 'bags', 'box', 'boxes', 'bottle', 'bottles', 'letter',
    'letters', 'message', 'messages', 'story', 'stories', 'problem',
    'problems', 'question', 'questions', 'answer', 'answers', 'reason',
    'reasons', 'event', 'events', 'situation', 'situations', 'company',
    'companies', 'school', 'schools', 'country', 'countries', 'river',
    'rivers', 'mountain', 'mountains', 'garden', 'gardens', 'village',
    'villages', 'file', 'files', 'report', 'reports', 'meeting', 'meetings',
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


def _antecedent_number_evidence(np_node):
    """Return number and the overt words that support it."""
    kids = np_node.get('children', [])
    coordinators = [c for c in kids if c.get('type') in ('CC', 'CONJP', 'UCP')]
    if coordinators:
        if all(_lower(c) == 'and' for c in coordinators):
            return 'pl', coordinators
        # Alternative/disjunctive antecedents do not supply a unique number.
        return None, []
    # Partitive quantifier NPs ('a lot of cafes', 'a number of students',
    # 'a couple of books', 'plenty of options') inherit number from the
    # object of 'of', not from the singular quantifier noun 'lot'/'number'.
    all_lvs = _leaves(np_node)
    if len(all_lvs) >= 4:
        w0, w1, w2 = _lower(all_lvs[0]), _lower(all_lvs[1]), _lower(all_lvs[2])
        if (w0 in ('a', 'an') and w1 in ('lot', 'number', 'couple', 'bunch', 'handful', 'majority', 'minority', 'variety', 'group', 'pair') and w2 == 'of') or (w0 in ('lots', 'plenty', 'dozens', 'hundreds', 'thousands') and w1 == 'of'):
            of_pp = next((c for c in kids if c.get('type') == 'PP'), None)
            if of_pp is not None:
                pp_nouns = [lf for lf in _leaves(of_pp)
                            if lf.get('type') in ('NN', 'NNS', 'NNP', 'NNPS')]
                if pp_nouns:
                    return ruleset._num_of(pp_nouns[-1]), [pp_nouns[-1]]
    excl_ids = {lf['id'] for c in kids if c.get('type') in ('PP', 'SBAR', 'S', 'VP') for lf in _leaves(c)}
    nouns = [lf for lf in _leaves(np_node)
             if lf['id'] not in excl_ids
             and lf.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP')]
    if nouns:
        head = nouns[-1]
        if _lower(head) in {'i', 'you'}:
            return None, []
        return ruleset._num_of(head), [head]
    first = all_lvs[0] if all_lvs else None
    if first is not None:
        w = _lower(first)
        if w in ('those', 'these'):
            return 'pl', [first]
        if w in ('that', 'this'):
            return 'sg', [first]
    return None, []


def _antecedent_animacy(np_node):
    """'human' / 'nonhuman' / None for the head noun of a relative antecedent."""
    pp_ids = {lf['id'] for c in np_node.get('children', [])
              if c.get('type') == 'PP' for lf in _leaves(c)}
    nouns = [lf for lf in _leaves(np_node)
             if lf['id'] not in pp_ids
             and lf.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP')]
    if not nouns:
        return None
    head = nouns[-1]
    low = _lower(head)
    if low in HUMAN_ANTECEDENTS:
        return 'human'
    if low in NONHUMAN_ANTECEDENTS:
        return 'nonhuman'
    if head.get('type') in ('PRP',) and low in {'i', 'me', 'he', 'him', 'she',
                                                 'her', 'we', 'us', 'they',
                                                 'them', 'you'}:
        return 'human'
    # A proper name is more likely a person than a thing, but places and
    # products are also proper names; leave the case unflagged when unsure.
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

    # --- 5.4  relative pronoun choice (who / whom / which) -------------------- #
    handled_pronoun_ids = set()
    for node in _iter(root):
        sibling_kids = node.get('children', [])
        for idx, sbar in enumerate(sibling_kids):
            if sbar.get('type') != 'SBAR':
                continue
            sk = sbar.get('children', [])
            if not sk or sk[0].get('type') != 'WHNP':
                continue
            wh = _leaves(sk[0])
            if not wh:
                continue
            wh_leaf = wh[0]
            wh_low = _lower(wh_leaf)
            if wh_low not in {'who', 'whom', 'which'}:
                continue
            antecedent = next((k for k in reversed(sibling_kids[:idx])
                               if k.get('type') == 'NP'), None)
            if antecedent is None:
                continue
            clause = next((c for c in sk if c.get('type') == 'S'), None)
            subject_gap = bool(clause and clause.get('children')
                               and clause['children'][0].get('type') == 'VP')
            animacy = _antecedent_animacy(antecedent)
            fix = reason = None
            if wh_low in {'who', 'whom'} and animacy == 'nonhuman':
                fix = 'which'
                reason = (f"The antecedent '{antecedent['surface']}' is not a "
                          f"person; use 'which' (or 'that') instead of "
                          f"'{wh_leaf['surface']}'.")
            elif wh_low == 'which' and animacy == 'human':
                fix = 'who' if subject_gap else 'whom'
                reason = (f"The antecedent '{antecedent['surface']}' is a person; "
                          f"use '{fix}' here instead of 'which'.")
            elif wh_low == 'whom' and subject_gap:
                fix = 'who'
                reason = ("The relative pronoun is the subject of the clause; "
                          "use 'who', not 'whom'.")
            handled_pronoun_ids.add(wh_leaf['id'])
            if not fix:
                continue
            out.append(_finding(
                '5.4', 'error', 'C-RELATIVE-PRONOUN', 'relative pronoun',
                wh_leaf['id'], reason,
                _tree_evidence(sbar['id'], 'antecedent NP + SBAR(WHNP ...)',
                               [{'node': antecedent['id']},
                                {'node': wh_leaf['id']}]),
                remediation={
                    'suggested_fix': f"write '{fix}'",
                    'edits': [{'node': wh_leaf['id'], 'replacement': fix}],
                }))

    # Fallback for flat relative clauses without an SBAR node.
    for i, lf in enumerate(leaves):
        if lf['id'] in handled_pronoun_ids or i == 0:
            continue
        low = _lower(lf)
        if low not in ('which', 'who', 'whom'):
            continue
        prev = leaves[i - 1]
        prev_low = _lower(prev)
        fix = reason = None
        if low in ('who', 'whom') and prev_low in NONHUMAN_ANTECEDENTS:
            fix = 'which'
            reason = (f"'{lf['surface']}' refers to people, but "
                      f"'{prev['surface']}' is not a person; use 'which' "
                      f"(or 'that').")
        elif low == 'which' and prev_low in HUMAN_ANTECEDENTS:
            fix = 'who'
            reason = (f"'which' does not refer to people; use 'who' (or 'that') "
                      f"after '{prev['surface']}'.")
        if not fix:
            continue
        out.append(_finding(
            '5.4', 'error', 'C-RELATIVE-PRONOUN', 'relative pronoun', lf['id'],
            reason,
            _tree_evidence(lf['id'], 'antecedent + relative pronoun',
                           [{'node': prev['id']}, {'node': lf['id']}]),
            remediation={
                'suggested_fix': f"write '{fix}'",
                'edits': [{'node': lf['id'], 'replacement': fix}],
            }))

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
            num, witnesses = _antecedent_number_evidence(ante)
            verb = _first_finite(clause['children'][0])
            if num is None or verb is None:
                continue
            vlow = _lower(verb)
            v_sg = verb.get('type') == 'VBZ' or vlow in SG_FINITE
            v_pl = verb.get('type') == 'VBP' or vlow in PL_FINITE
            if (num == 'pl' and v_sg) or (num == 'sg' and v_pl):
                number = 'plural' if num == 'pl' else 'singular'
                reason = (f"The relative pronoun '{wh[0]['surface']}' is the subject within the "
                          f"relative clause and refers to the {number} antecedent '{ante['surface']}'. "
                          f"The verb '{verb['surface']}' carries tense here and needs "
                          f"a form that matches that subject.")
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
                    reason,
                    _tree_evidence(sbar['id'], 'antecedent NP + SBAR(WHNP S(VP))',
                                   [{'node': node['id']} for node in [*witnesses, wh[0], verb]]),
                    _rem(reason,
                         (f"Change '{verb['surface']}' to '{fix}'." if fix
                          else "Make the verb agree with the antecedent."),
                         ([{'node': verb['id'], 'replacement': fix}] if fix else None),
                         'verb agrees with the antecedent of the relative')))
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
    quoted = ruleset._quoted_indices(leaves)
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
    run('ruleset.tree', lambda: ruleset._check_tree(root, clauses, leaves, text, quoted))
    run('ruleset.more', lambda: ruleset._check_more(root, clauses, leaves))
    run('ruleset.context', lambda: ruleset._check_context(root, clauses, leaves))
    run('ruleset.syntax_constraints', lambda: ruleset._check_syntax_constraints(root, clauses, leaves))
    run('ruleset.h02_cgel_constraints', lambda: ruleset._check_h02_cgel_constraints(root, clauses, leaves, text))
    run('ruleset.terminal', lambda: ruleset._check_terminal(root, text))
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
