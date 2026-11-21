"""Pre-parser spellchecker.

SynTutor's syntactic matrix expects well-formed tokens: a misspelling can
produce a malformed tree and a spurious rule verdict.  Following the project's
failure-triage policy, typo-level failures are handled *here*, before parsing,
so the matrix stays clean.

The module is deliberately dependency-light.  The lexicon is loaded lazily from,
in order of preference:

1. the ``SYNTUTOR_DICT`` environment variable (a newline-separated word file),
2. the system dictionary (``/usr/share/dict/words``),
3. the 82k-word English frequency dictionary bundled with SymSpell
   (``symspellpy``) -- installed with the project, so it is available on
   Windows and in the Docker image too, where neither of the above exists.

When *no* lexicon can be loaded, ``known_word`` accepts every token instead of
rejecting it: a missing typo check is a far safer failure mode than flagging
valid words as unknown.

Spelling repair is powered by **SymSpell** (``symspellpy``): a fast,
frequency-ranked symmetric-delete lookup against an 82k-word English
dictionary.  When symspellpy is not installed the module silently falls back to
a single-edit (Norvig) corrector, so the pipeline never depends on it being
present.

Exports
-------
known_word(word)        -> bool
unknown_words(text)     -> list[str]
is_typo(text, ...)      -> bool
spelling_candidate(tok) -> bool
best_correction(word)   -> str | None   (confident SymSpell repair)
spell_correct(text)     -> str          (best-effort repair)
preprocess(text)        -> (corrected_text, unknown: list[str])
"""
import os
import re

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")
_DICT_ENV = 'SYNTUTOR_DICT'
_SYSTEM_DICTS = ('/usr/share/dict/words', '/usr/dict/words')

_WORDS = None
_WORDS_BY_LEN = None
_STOP_PUNCT = '.,!?;:"\'()[]{}'


def _load_words():
    global _WORDS
    if _WORDS is not None:
        return _WORDS
    paths = []
    env = os.environ.get(_DICT_ENV)
    if env:
        paths.append(env)
    paths.extend(_SYSTEM_DICTS)
    freq = _frequency_dict_path()
    if freq:
        paths.append(freq)
    words = set()
    for path in paths:
        try:
            with open(path, encoding='utf-8', errors='ignore') as fh:
                for line in fh:
                    # Frequency lists are "word count"; plain word lists are
                    # one word per line.  The first field covers both.
                    parts = line.split()
                    w = parts[0] if parts else ''
                    if w and w.isascii() and w.replace("'", '').isalpha():
                        words.add(w.lower())
            if words:
                break
        except OSError:
            continue
    _WORDS = words
    return _WORDS


def _frequency_dict_path():
    """Path of the 82k-word frequency dictionary shipped with symspellpy."""
    try:
        import symspellpy
        path = os.path.join(os.path.dirname(symspellpy.__file__),
                            'frequency_dictionary_en_82_765.txt')
        if os.path.exists(path):
            return path
    except Exception:  # noqa: BLE001 - optional dependency
        pass
    return None


# --------------------------------------------------------------------------- #
# Spelling-suggestion engine (SymSpell)                                       #
# --------------------------------------------------------------------------- #
# SymSpell (symmetric-delete) does a fast, frequency-ranked dictionary lookup.
# It ships an 82k-word English dictionary with Google-Books frequencies, so it
# repairs the long tail of typos that no hand-written table could cover.  The
# engine is loaded lazily and degrades gracefully to the edit-distance corrector
# when symspellpy (or its dictionary) is unavailable.
_SYMSPELL = None
_SYMSPELL_TRIED = False
_SYMSPELL_MAX_DIST = 2
_SYMSPELL_PREFIX = 7
# A wrong correction is worse than none: only trust a distance-2 fix when the
# candidate is a very common word, and never rewrite short tokens at all.
_MIN_COUNT_DIST2 = 2_000_000


def _get_symspell():
    global _SYMSPELL, _SYMSPELL_TRIED
    if _SYMSPELL_TRIED:
        return _SYMSPELL
    _SYMSPELL_TRIED = True
    path = _frequency_dict_path()
    if not path:
        return None
    try:
        from symspellpy import SymSpell
        engine = SymSpell(max_dictionary_edit_distance=_SYMSPELL_MAX_DIST,
                          prefix_length=_SYMSPELL_PREFIX)
        engine.load_dictionary(path, term_index=0, count_index=1)
        _SYMSPELL = engine
    except Exception:  # noqa: BLE001 - optional dependency
        _SYMSPELL = None
    return _SYMSPELL


def spelling_candidate(tok):
    """True when a token is worth spell-checking (lowercase, >= 3 letters)."""
    return _spelling_candidate(tok)


def best_correction(word):
    """Return a confident spelling correction for *word*, or None.

    Words already in the SymSpell dictionary, accented/non-ASCII words, and
    tokens shorter than four letters are never "corrected".  Distance-1 fixes
    are accepted for any checked word; distance-2 fixes only for words of seven
    letters or more whose candidate is a very common word.
    """
    if not word:
        return None
    low = _strip(word).lower()
    # Accented or non-ASCII tokens are left alone: they are usually loanwords
    # ('café') we must not "repair" into an unaccented word.
    if len(low) < 4 or not low.isalpha() or not low.isascii():
        return None
    engine = _get_symspell()
    if engine is None:
        return _best_candidate_fallback(low)
    try:
        from symspellpy import Verbosity
        max_edit = _SYMSPELL_MAX_DIST if len(low) >= 7 else 1
        suggestions = engine.lookup(low, Verbosity.ALL, max_edit_distance=max_edit)
    except Exception:  # noqa: BLE001
        return _best_candidate_fallback(low)
    # If the word is itself in the dictionary, it is not a misspelling -- our
    # own lexicon is simply missing it ('gallery', 'fridge', 'website').
    if any(s.distance == 0 for s in suggestions):
        return None
    # Keep real corrections only: distance 1 for any word, distance 2 only for
    # a very common candidate.  Then prefer a candidate our own lexicon knows.
    keep = [s for s in suggestions
            if s.term != low and 1 <= s.distance <= max_edit
            and (s.distance == 1 or s.count >= _MIN_COUNT_DIST2)]
    if not keep:
        return None
    # Closest edit wins; among equals, prefer a word our lexicon knows, then the
    # most frequent.
    keep.sort(key=lambda s: (s.distance, 0 if known_word(s.term) else 1, -s.count))
    return keep[0].term


def strong_typo_candidate(word):
    """Conservative dictionary evidence for a likely single-edit typo."""
    if len(word) < 4 or not word.isascii() or not word.isalpha() or not word.islower():
        return None
    engine = _get_symspell()
    if engine is None:
        return None
    from symspellpy import Verbosity
    nearest = engine.lookup(word, Verbosity.CLOSEST, max_edit_distance=1)
    if not nearest or nearest[0].distance != 1:
        return None
    best = nearest[0]
    if best.count < _MIN_COUNT_DIST2 or (len(nearest) > 1 and best.count < 10 * nearest[1].count):
        return None
    return best.term


def has_name_evidence(leaf):
    """Protect names when token categories or entity evidence corroborate them."""
    return (leaf.get('fpos') == 'PROPN'
            and (leaf.get('type') in {'NNP', 'NNPS'} or leaf.get('fentity')
                 or any(char.isupper() for char in leaf.get('surface', ''))))


def _strip(word):
    return word.strip(_STOP_PUNCT)


def _morph_variants(word):
    """Cheap morphological reductions so inflections are not called OOV."""
    w = word.lower()
    out = {w}
    if w.endswith("'s") or w.endswith("s'"):
        out.add(w.rstrip("'s"))
    if w.endswith('ies') and len(w) > 4:
        out.add(w[:-3] + 'y')
    if w.endswith('es') and len(w) > 3:
        out.add(w[:-2])
        out.add(w[:-1])
    if w.endswith('s') and len(w) > 3:
        out.add(w[:-1])
    for suf in ('ing', 'edly', 'ed', 'ly', 'er', 'est', 'ness', 'ment'):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            base = w[:-len(suf)]
            out.add(base)
            out.add(base + 'e')
            out.add(base + 'y')
    return out


_IRREGULAR_CLITICS = {"can't", 'won\'t', "shan't", "ain't", "y'all"}
_CLITICS = ("n't", "'ll", "'ve", "'re", "'d", "'m", "'s", "'em")


def _contraction_ok(core):
    low = core.replace('\u2019', "'")
    if low in _IRREGULAR_CLITICS:
        return True
    for clitic in _CLITICS:
        if low.endswith(clitic) and len(low) > len(clitic):
            stem = low[:-len(clitic)]
            if stem and known_word(stem):
                return True
    return False


def known_word(word):
    """True if the token (or a plausible inflection of it) is in the lexicon."""
    if not word:
        return True
    if not word[0].isalpha():
        return True
    words = _load_words()
    core = _strip(word).lower()
    if not core:
        return True
    if "'" in core or '\u2019' in core:
        if _contraction_ok(core):
            return True
    if not words:
        # No lexicon at all (no dictionary, no symspellpy): accept by
        # default.  spaCy's *blank* vocabulary marks every token OOV, so
        # consulting it here would reject valid words like "is".
        return True
    for variant in _morph_variants(core):
        if variant in words:
            return True
    engine = _get_symspell()
    if engine is not None and engine.words.get(core, 0) >= 1_000_000:
        return True
    return False


def _spelling_candidate(tok):
    """Only flag lowercase-initial tokens.

    Capitalised tokens are assumed to be proper nouns or sentence-initial
    words; flagging them as typos would punish names (Rose, Kendra, ...)."""
    return len(tok) >= 3 and tok[0].islower()


def unknown_words(text):
    seen = []
    for tok in _WORD_RE.findall(text or ''):
        if _spelling_candidate(tok) and not known_word(tok):
            seen.append(tok)
    return seen


def is_typo(text, threshold=0.15, min_tokens=3):
    toks = [t.lower() for t in _WORD_RE.findall(text or '') if len(t) >= 3]
    if len(toks) < min_tokens:
        return False
    cands = [t for t in _WORD_RE.findall(text or '') if _spelling_candidate(t)]
    if len(cands) < min_tokens:
        return False
    unknown = sum(1 for t in cands if not known_word(t))
    return unknown / len(cands) >= threshold


def _edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits if b for c in letters]
    inserts = [a + c + b for a, b in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def _best_candidate_fallback(word):
    """Edit-distance fallback used only when SymSpell is unavailable."""
    words = _load_words()
    if not words:
        return None
    candidates = [c for c in _edits1(word) if known_word(c)]
    if not candidates:
        return None
    literal = [c for c in candidates if c in words]
    return sorted(literal or candidates)[0]


def _best_candidate(word):
    return best_correction(word) or _best_candidate_fallback(word)


def spell_correct(text):
    """Return text with high-confidence misspellings repaired."""
    if not text:
        return text
    out = []
    last = 0
    for m in _WORD_RE.finditer(text):
        tok = m.group(0)
        if len(tok) < 3 or known_word(tok):
            continue
        cand = best_correction(tok)
        if cand is None:
            continue
        if tok[0].isupper():
            cand = cand.capitalize()
        out.append(text[last:m.start()])
        out.append(cand)
        last = m.end()
    out.append(text[last:])
    return ''.join(out)


def preprocess(text):
    """Convenience wrapper: (corrected_text, remaining_unknown_words)."""
    corrected = spell_correct(text)
    return corrected, unknown_words(corrected)


if __name__ == '__main__':
    import sys
    for line in sys.argv[1:] or ['I have tecnologies and siences .']:
        corrected, unknown = preprocess(line)
        print(f'{line!r} -> {corrected!r}  unknown={unknown}')


def uncertain_function_word_candidates(word, next_type=None):
    """Return plausible closed-class determiner readings for an uncertain token."""
    low = (word or '').lower()
    if not low.isascii() or not low.isalpha() or len(low) < 3:
        return []
    ordered_forms = (
        'the', 'this', 'that', 'these', 'those',
        'his', 'her', 'its', 'our', 'your', 'their', 'my',
        'whose', 'which', 'what',
    )
    singular_only = {'this', 'that', 'a', 'an'}
    plural_only = {'these', 'those'}
    low_consonants = [c for c in low if c not in 'aeiou']
    candidates = []
    for form in ordered_forms:
        if form == low:
            continue
        if next_type in {'NN', 'NNP'} and form in plural_only:
            continue
        if next_type in {'NNS', 'NNPS'} and form in singular_only:
            continue
        vowel_deleted = any(
            low == form[:i] + form[i + 1:]
            for i, ch in enumerate(form) if ch in 'aeiou'
        )
        transposed = any(
            low == form[:i] + form[i + 1] + form[i] + form[i + 2:]
            for i in range(len(form) - 1)
        )
        same_prefix_sub = (
            len(low) == len(form) >= 3
            and low[:2] == form[:2]
            and sum(a != b for a, b in zip(low, form)) == 1
        )
        consonant_skeleton = (
            len(low_consonants) >= 2
            and low[0] == form[0]
            and low_consonants == [c for c in form if c not in 'aeiou']
        )
        if vowel_deleted or transposed or same_prefix_sub or consonant_skeleton:
            candidates.append(form)
    return candidates


def uncertain_function_words(analysis):
    """Identify an unresolved orthographic reading in a closed grammatical slot.

    A possible omitted vowel or common transposition can explain the token, but
    the surrounding phrase often permits several completions (or a proper name).
    Report the uncertainty without silently rewriting the candidate text.
    """
    forms = {'a', 'an', 'the', 'this', 'that', 'these', 'those', 'my', 'your',
             'his', 'her', 'its', 'our', 'their', 'whose', 'which', 'what'}
    transposed_dets = {'teh', 'hte', 'tihs', 'taht', 'tey'}
    rows = []
    seen_ids = set()
    nodes = analysis.get('nodes')
    if not isinstance(nodes, dict):
        return rows
    leaves = sorted(
        (n for n in nodes.values() if not n.get('children') and not n.get('punct')
         and n.get('span') and len(n['span']) == 2),
        key=lambda n: n['span'][0],
    )
    by_idx = {n['span'][0]: n for n in leaves}
    for node in leaves:
        idx = node['span'][0]
        word = node['surface']
        if not word.isascii() or not word.isalpha() or len(word) < 3 or word.isupper():
            continue
        low = word.lower()
        if low in forms:
            continue
        nxt = by_idx.get(idx + 1)
        vowel_elision = any(
            low == form[:i] + form[i + 1:] for form in forms
            for i, char in enumerate(form) if char in 'aeiou'
        )
        if (vowel_elision and not known_word(word)
                and node.get('type') in {'DT', 'PRP$'}
                and (not has_name_evidence(node)
                     or (nxt is not None and nxt.get('type') in {'NN', 'NNS', 'JJ'}))):
            seen_ids.add(idx)
            rows.append({'token_id': idx, 'surface': word})
            continue
        if (low in transposed_dets and not node.get('fentity')
                and (node.get('type') in {'DT', 'PRP$'}
                     or (nxt is not None and nxt.get('type') in {'NN', 'NNS', 'JJ'}
                         and node.get('fdep') in {'det', 'compound', 'amod'}))):
            seen_ids.add(idx)
            rows.append({'token_id': idx, 'surface': word})
    return rows


def unresolved_spelling_tokens(analysis):
    """Return tokens in a candidate/corrected parse whose spelling remains uncertain.

    Combines uncertain closed-class determiners (e.g. 'Ths', 'Teh') with any
    remaining unedited lowercase tokens that have a clear dictionary typo
    candidate, while protecting capitalized proper names and known words.
    """
    rows = list(uncertain_function_words(analysis))
    seen = {row['token_id'] for row in rows}
    nodes = analysis.get('nodes')
    if not isinstance(nodes, dict):
        return rows
    by_idx = {
        n['span'][0]: n
        for n in nodes.values()
        if not n.get('children') and n.get('span') and len(n['span']) == 2
    }
    for node in sorted(by_idx.values(), key=lambda n: n['span'][0]):
        if node.get('punct') or has_name_evidence(node):
            continue
        span = node['span']
        if span[0] in seen:
            continue
        word = node.get('surface', '')
        if not word.isascii() or not word.isalpha() or not word.islower() or len(word) < 4:
            continue
        nxt = by_idx.get(span[0] + 1)
        nxt_surface = nxt.get('surface', '') if nxt else ''
        if nxt_surface and (nxt_surface.startswith(("'", '\u2019')) or nxt_surface.lower() == "n't"):
            if known_word(word + nxt_surface):
                continue
        if not known_word(word) and strong_typo_candidate(word):
            seen.add(span[0])
            rows.append({'token_id': span[0], 'surface': word})
    rows.sort(key=lambda r: r['token_id'])
    return rows
