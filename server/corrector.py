"""Text-space correction search: the deterministic closure for "no rule fired".

When the acceptability model rejects a sentence but the rule matrix stays
clean (verdict 'unverified'), we do NOT hand-write another syntax rule and we
do NOT trust the parse of the bad sentence. Instead:

1. MLM SWEEP (text space)
   Mask one word at a time, let a masked-language model (distilbert-base-uncased
   by default) propose top-k replacements, and substitute each back into the
   acceptability model until a swap flips it from unacceptable to acceptable.
   That single-token swap IS the error locus (the bad word) and the correction
   (the good word).

2. CLEAN AST PROJECTION (done by the caller, app.py)
   The corrected sentence is grammatical by construction, so the parser + matrix
   license it. The good word's part-of-speech tag in that clean tree is the
   authoritative required tag.

3. MORPHOLOGICAL DIFF (lemminflect)
   Both words are passed through lemminflect. A promotion is only allowed when
   both share a lemma (a morphology/syntax repair: 'lacks'->'lack'),
   never when the MLM made a flat meaning swap ('reddish'->'red').

4. DYNAMIC EXPLANATION
   A template with no LLM and no per-word rule:
   "The sentence structure requires the {Required_Tag_Label} form '{good}',
   but '{bad}' is the {Bad_Tag_Label} form."

This module is optional exactly like the detector: if the MLM cannot be loaded
or a flip cannot be found, ``sweep`` returns None and the caller keeps the
original 'unverified' verdict.
"""

import os
import re
import sys

try:  # package or script-dir import, same convention as matrix.py
    from . import licensing
except ImportError:  # pragma: no cover
    import licensing

_MASK = '[MASK]'
_MLM_MODEL = os.environ.get('SYNTUTOR_MLM_MODEL', 'distilbert-base-uncased')
_TOP_K = int(os.environ.get('SYNTUTOR_MLM_TOP_K', '5'))
_MAX_TOKENS = int(os.environ.get('SYNTUTOR_MLM_MAX_TOKENS', '40'))

_MLM = None
_MLM_ERROR = None
_MLM_ERROR_REPORTED = False

# Plain-English labels for the part-of-speech tags found in the clean tree.
EXTENDED_TAG_LABEL = {
    'VB': 'base', 'VBD': 'past', 'VBG': 'present participle',
    'VBN': 'past participle', 'VBP': 'non-third-person present',
    'VBZ': 'third-person singular present', 'MD': 'modal',
    'NN': 'singular noun', 'NNS': 'plural noun',
    'NNP': 'proper noun', 'NNPS': 'proper plural noun',
    'JJ': 'adjective', 'JJR': 'comparative', 'JJS': 'superlative',
    'RB': 'adverb', 'RBR': 'comparative adverb', 'RBS': 'superlative adverb',
}

# Order in which to hunt for a word inside a lemma's paradigm, most likely
# open-class POS first.
_PARADIGM_TAGS = ['VBZ', 'VBP', 'VBD', 'VBN', 'VBG', 'VB', 'MD',
                  'NNS', 'NN', 'NNP', 'JJ', 'JJR', 'JJS', 'RBR', 'RBS']
_UPOS_ORDER = ('VERB', 'NOUN', 'ADJ', 'ADV', 'AUX')


def load_mlm():
    """Load the masked-language model once, cache it, never crash the app."""
    global _MLM, _MLM_ERROR, _MLM_ERROR_REPORTED
    if _MLM is not None:
        return _MLM
    if _MLM_ERROR is not None:
        if not _MLM_ERROR_REPORTED:
            sys.stderr.write(f'[syntutor] corrector unavailable: {_MLM_ERROR}\n')
            _MLM_ERROR_REPORTED = True
        return None
    try:
        import torch  # noqa: F401  (ensures torch import order)
        from transformers import pipeline
        _MLM = pipeline('fill-mask', model=_MLM_MODEL, device=-1, top_k=_TOP_K)
    except Exception as exc:  # noqa: BLE001 - degraded mode is by design
        _MLM_ERROR = exc
        return None
    return _MLM


def _words(text):
    """Alphabetic word spans of ``text`` (skips punctuation and contractions)."""
    out = []
    for m in re.finditer(r"[A-Za-z]+|[^A-Za-z\s]", text):
        if not m.group().isalpha():
            continue
        if m.start() > 0 and text[m.start() - 1] == "'":
            continue  # inside a contraction (don', 'boy'<s>)
        if m.end() < len(text) and text[m.end()] == "'":
            continue  # possessive/contraction tail (boy<'>s)
        out.append(m)
    return out


def _recast(word, orig):
    """Apply the original token's casing pattern onto the MLM replacement."""
    if orig.isupper():
        return word.upper()
    if orig[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def _shared_lemma(bad, good):
    """A lemma both words inflect from, or None if the swap is a flat meaning change."""
    for u in _UPOS_ORDER:
        bit = ('VERB', 'AUX') if u == 'VERB' else (u,)
        lb = set()
        for uu in bit:
            lb |= licensing._lemmas(bad, uu)
        lg = set()
        for uu in bit:
            lg |= licensing._lemmas(good, uu)
        if lb & lg:
            return sorted(lb & lg)[0]
    return None


def _preferred_upos(good_tag):
    """The open-class UPOS whose paradigm the clean tree already vouched for."""
    return licensing.PTB2UPOS.get(good_tag)


def morph_diff(bad, good, good_tag=None):
    """Deterministic morphology diff between the bad and the good word.

    Returns (shared_lemma, bad_tag, bad_label, good_tag, good_label) or None
    when the two words are not two forms of one lemma.  ``good_tag`` is the
    clean-tree tag of the good word (authoritative); its UPOS is searched
    first so e.g. 'books'->'book' is read as a noun-number fix, not a verb
    paradigm swap.
    """
    lemma = _shared_lemma(bad, good)
    if lemma is None:
        return None
    order = []
    pref = _preferred_upos(good_tag)
    if pref:
        order.append(pref)
    order += [u for u in _UPOS_ORDER if u != pref]
    for u in order:
        forms = licensing._forms(lemma, u)
        bad_tag = good_tag_l = None
        for tag in _PARADIGM_TAGS:
            cells = forms.get(tag, ())
            if bad_tag is None and any(bad == f or bad.lower() == f.lower() for f in cells):
                bad_tag = tag
            if good_tag_l is None and any(good == f or good.lower() == f.lower() for f in cells):
                good_tag_l = tag
            if bad_tag and good_tag_l:
                return (lemma, bad_tag, EXTENDED_TAG_LABEL.get(bad_tag, ''),
                        good_tag_l, EXTENDED_TAG_LABEL.get(good_tag_l, ''))
    return None


def sweep(text, rank, spans=None, max_tokens=None, top_k=None):
    """Find one single-token swap that flips the acceptability model to 'yes'.

    ``rank`` must accept a list of candidate sentences and return an aligned
    list of detector outcome dicts (or None entries).  ``spans`` are the
    (start, end) offsets -- relative to ``text`` -- of the word positions to
    try, in order; position i in ``spans`` lines up with token i in the parse.
    Returns a locator dict, or None if the MLM is out or no flip exists.
    """
    mlm = load_mlm()
    if mlm is None or not callable(rank):
        return None
    if spans is None:
        spans = [(m.start(), m.end()) for m in _words(text)]
    if not spans:
        return None
    max_tokens = max_tokens or _MAX_TOKENS
    top_k = top_k or _TOP_K

    for idx, (s, e) in enumerate(spans[:max_tokens]):
        orig = text[s:e]
        masked = text[:s] + _MASK + text[e:]
        try:
            hyps = mlm(masked, top_k=top_k)
        except Exception:  # noqa: BLE001 - one bad mask must not abort the sweep
            continue
        if not hyps:
            continue
        cands, meta = [], []
        for h in hyps:
            good = _recast(h.get('token_str') or '', orig)
            if not good or good == orig:
                continue
            # Only morphology repairs promote (lacks->lack).  A flat meaning
            # swap (He->I) that happens to flip the classifier must not consume
            # the search -- keep scanning for the word-form correction.
            if _shared_lemma(orig, good) is None:
                continue
            cands.append(text[:s] + good + text[e:])
            meta.append(h)
        if not cands:
            continue
        outs = rank(cands)
        for j, h in enumerate(meta):
            out = outs[j] if outs and j < len(outs) else None
            if out is None:
                continue
            if out.get('acceptable'):
                return {
                    'position': idx,
                    'bad': orig,
                    'good': _recast(h['token_str'], orig),
                    'good_mlm_score': h.get('score'),
                    'cola_acceptable': True,
                    'cola_p': out.get('acceptable_prob'),
                    'corrected_text': cands[j],
                }
    return None


def template(bad, good, required_label='', bad_label=''):
    """The dynamic explanation string (no LLM, no per-word rule)."""
    if required_label and bad_label:
        return (f"The sentence structure requires the {required_label} form "
                f"'{good}', but '{bad}' is the {bad_label} form.")
    return (f"The acceptability model locates the anomaly in the word '{bad}'; "
            f"the structure requires '{good}' here.")