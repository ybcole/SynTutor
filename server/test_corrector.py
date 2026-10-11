"""Regression for server/corrector.py -- the text-space correction search.

The MLM + acceptability models are stubbed out so the test runs offline and
deterministically; the morphology diff and dynamic template run against the
real lemminflect-backed licensing layer.

Run:  python test_corrector.py
"""
import os
import sys

os.environ['SYNTUTOR_MLM_MODEL'] = 'stub-mlm'

import corrector  # noqa: E402


class StubMLM:
    """Mimics the fill-mask pipeline output for the few masked contexts used."""

    TABLES = {
        'They are stupid and [MASK] good learners.':
            [{'token_str': 'lack', 'score': 0.90},
             {'token_str': 'go', 'score': 0.10}],
        'I [MASK] him yesterday.':
            [{'token_str': 'saw', 'score': 0.95},
             {'token_str': 'see', 'score': 0.04}],
        'They [MASK] good learners.':
            [{'token_str': 'are', 'score': 0.8}, {'token_str': 'is', 'score': 0.2}],
        'He [MASK] to school yesterday.':
            [{'token_str': 'went', 'score': 0.5}, {'token_str': 'ran', 'score': 0.2}],
        'We [MASK] seen the movie.':
            [{'token_str': 'have', 'score': 0.9}],
    }

    def __call__(self, masked, top_k=5):
        return list(self.TABLES.get(masked, [{'token_str': 'zzz', 'score': 0.01}]))[:top_k]


def stub_rank(cands):
    out = []
    for c in cands:
        if ' lack ' in c or ' lack.' in c or c.startswith('They lack'):
            out.append({'acceptable': True, 'label': 'acceptable',
                        'acceptable_prob': 0.9})
        elif ' saw ' in c or 'saw him' in c:
            out.append({'acceptable': True, 'label': 'acceptable',
                        'acceptable_prob': 0.88})
        elif ' are ' in c or ' are.' in c or c.startswith('They are'):
            out.append({'acceptable': True, 'label': 'acceptable',
                        'acceptable_prob': 0.97})
        elif ' ran ' in c:
            out.append({'acceptable': True, 'label': 'acceptable',
                        'acceptable_prob': 0.9})
        else:
            out.append({'acceptable': False, 'label': 'unacceptable',
                        'acceptable_prob': 0.2})
    return out


def case(lbl, ok):
    print(f"{lbl:<66} {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    corrector.load_mlm = lambda: StubMLM()
    ok = True

    # --- the sweep finds the exact locus + correction ----------------------- #
    loc = corrector.sweep('They are stupid and lacks good learners.',
                          stub_rank, spans=[(20, 25)])
    ok &= case("lacks -> lack (locus word, flip found)", loc is not None)
    if loc:
        ok &= case("bad is 'lacks', good is 'lack'",
                   loc['bad'] == 'lacks' and loc['good'] == 'lack')

    loc = corrector.sweep('I seen him yesterday.', stub_rank, spans=[(2, 6)])
    ok &= case("seen -> saw (irregular past)", loc is not None
               and loc['bad'] == 'seen' and loc['good'] == 'saw')

    # --- a flat meaning swap must NOT be accepted as a correction ----------- #
    # The only stub candidate for this context is 'have' itself (a no-op),
    # which the sweep must skip rather than treat as a correction.
    loc = corrector.sweep('We have seen the movie.', stub_rank,
                          spans=[(3, 7)])
    ok &= case("no-op candidate is skipped (no correction invented)",
               loc is None)

    # --- the morphology diff reads verb + noun paradigms correctly ---------- #
    d = corrector.morph_diff('lacks', 'lack', good_tag='VBP')
    ok &= case("lacks/lack diff labels VBZ/VBP",
               d is not None and d[1] == 'VBZ' and d[3] == 'VBP')
    d = corrector.morph_diff('seen', 'saw', good_tag='VBD')
    ok &= case("seen/saw share lemma 'see': VBN -> VBD",
               d is not None and d[0] == 'see' and d[1] == 'VBN' and d[3] == 'VBD')
    d = corrector.morph_diff('books', 'book', good_tag='NNS')
    ok &= case("books/book reads as noun-number (no pref: VBP/VBZ swap)",
               d is not None and d[1] == 'NNS' and d[3] == 'NN')
    d = corrector.morph_diff('reddish', 'red', good_tag='JJ')
    ok &= case("reddish/red are NOT two forms of one lemma",
               d is None)

    # --- template renders without an LLM ------------------------------------- #
    t = corrector.template('lacks', 'lack',
                           'non-third-person present',
                           'third-person singular present')
    ok &= case("template string",
               "the non-third-person present form 'lack'" in t
               and "'lacks' is the third-person singular present form" in t)

    print('-' * 72)
    print('corrector regression: PASS' if ok else 'corrector regression: FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())