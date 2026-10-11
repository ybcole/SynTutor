"""Before/after regression for the licensing layer.

Trees are written the way benepar would shape them (no spaCy/benepar needed).
Where the parser's tag for a bad word is uncertain, several variants are listed:
the new layer must catch the error under *every* plausible tagging.

Run:  python test_licensing.py
"""
import re
import sys

import parse_engine as pe
import matrix as new_matrix


def build(ps):
    n = len(re.findall(r'\([^()\s]+ [^()\s]+\)', ps))
    return pe.NodeBuilder().build(pe.parse_parse_string(ps), n)


# (sentence, parse string, expected)  expected: 'bad' | 'good'
CASES = [
    # ---- the user's three examples, under every plausible parser tagging ----
    ('I am stupids.  [NNS]', '(S (NP (PRP I)) (VP (VBP am) (NP (NNS stupids))) (. .))', 'bad'),
    ('I am stupids.  [JJ]', '(S (NP (PRP I)) (VP (VBP am) (ADJP (JJ stupids))) (. .))', 'bad'),
    ('The men are runned. [VBN]', '(S (NP (DT The) (NNS men)) (VP (VBP are) (VP (VBN runned))) (. .))', 'bad'),
    ('The men are runned. [VBD]', '(S (NP (DT The) (NNS men)) (VP (VBP are) (VP (VBD runned))) (. .))', 'bad'),
    ('The men are runned. [JJ]', '(S (NP (DT The) (NNS men)) (VP (VBP are) (ADJP (JJ runned))) (. .))', 'bad'),
    ('The men are runned. [NN]', '(S (NP (DT The) (NNS men)) (VP (VBP are) (NP (NN runned))) (. .))', 'bad'),
    ('I hate those whose believe in me.',
     '(S (NP (PRP I)) (VP (VBP hate) (NP (NP (DT those)) (SBAR (WHNP (WP$ whose)) (S (VP (VBP believe) (PP (IN in) (NP (PRP me)))))))) (. .))', 'bad'),
    ('I hate those whose believe in me. [SBAR under VP]',
     '(S (NP (PRP I)) (VP (VBP hate) (NP (DT those)) (SBAR (WHNP (WP$ whose)) (S (VP (VBP believe) (PP (IN in) (NP (PRP me))))))) (. .))', 'bad'),
    # ---- other open-class / unlisted errors (no blacklist entry exists) ----
    ('Two mans came.', '(S (NP (CD Two) (NNS mans)) (VP (VBD came)) (. .))', 'bad'),
    ('He has two childs.', '(S (NP (PRP He)) (VP (VBZ has) (NP (CD two) (NNS childs))) (. .))', 'bad'),
    ('She is runing.', '(S (NP (PRP She)) (VP (VBZ is) (VP (VBG runing))) (. .))', 'bad'),
    ('He had went home.', '(S (NP (PRP He)) (VP (VBD had) (VP (VBN went) (NP (NN home)))) (. .))', 'bad'),
    ('They were ate.', '(S (NP (PRP They)) (VP (VBD were) (VP (VBN ate))) (. .))', 'bad'),
    ('She laughed happyly.', '(S (NP (PRP She)) (VP (VBD laughed) (ADVP (RB happyly))) (. .))', 'bad'),
    ('The boys who plays are here.',
     '(S (NP (NP (DT The) (NNS boys)) (SBAR (WHNP (WP who)) (S (VP (VBZ plays))))) (VP (VBP are) (ADVP (RB here))) (. .))', 'bad'),
    ('The man who live here is old.',
     '(S (NP (NP (DT The) (NN man)) (SBAR (WHNP (WP who)) (S (VP (VBP live) (ADVP (RB here)))))) (VP (VBZ is) (ADJP (JJ old))) (. .))', 'bad'),
    ('The man which lives here is old.',
     '(S (NP (NP (DT The) (NN man)) (SBAR (WHNP (WDT which)) (S (VP (VBZ lives) (ADVP (RB here)))))) (VP (VBZ is) (ADJP (JJ old))) (. .))', 'bad'),
    # ---- grammatical controls: must NOT be called ungrammatical ----
    ('The clever boy reads a book.', '(S (NP (DT The) (JJ clever) (NN boy)) (VP (VBZ reads) (NP (DT a) (NN book))) (. .))', 'good'),
    ('The men are running.', '(S (NP (DT The) (NNS men)) (VP (VBP are) (VP (VBG running))) (. .))', 'good'),
    ('The children have gone home.', '(S (NP (DT The) (NNS children)) (VP (VBP have) (VP (VBN gone) (NP (NN home)))) (. .))', 'good'),
    ('She tweeted the news quickly.', '(S (NP (PRP She)) (VP (VBD tweeted) (NP (DT the) (NN news)) (ADVP (RB quickly))) (. .))', 'good'),
    ('I hate those who believe in me.',
     '(S (NP (PRP I)) (VP (VBP hate) (NP (NP (DT those)) (SBAR (WHNP (WP who)) (S (VP (VBP believe) (PP (IN in) (NP (PRP me)))))))) (. .))', 'good'),
    ('The boys who play are here.',
     '(S (NP (NP (DT The) (NNS boys)) (SBAR (WHNP (WP who)) (S (VP (VBP play))))) (VP (VBP are) (ADVP (RB here))) (. .))', 'good'),
    ('The man who lives here is old.',
     '(S (NP (NP (DT The) (NN man)) (SBAR (WHNP (WP who)) (S (VP (VBZ lives) (ADVP (RB here)))))) (VP (VBZ is) (ADJP (JJ old))) (. .))', 'good'),
    ('I met a woman whose sister teaches here.',
     '(S (NP (PRP I)) (VP (VBD met) (NP (NP (DT a) (NN woman)) (SBAR (WHNP (WP$ whose) (NN sister)) (S (VP (VBZ teaches) (ADVP (RB here))))))) (. .))', 'good'),
    ('The taller boy ran faster.', '(S (NP (DT The) (JJR taller) (NN boy)) (VP (VBD ran) (ADVP (RBR faster))) (. .))', 'good'),
    ('She has walked home.', '(S (NP (PRP She)) (VP (VBZ has) (VP (VBN walked) (NP (NN home)))) (. .))', 'good'),
    ('The house was painted.', '(S (NP (DT The) (NN house)) (VP (VBD was) (VP (VBN painted))) (. .))', 'good'),
    ('The plan was stopped.', '(S (NP (DT The) (NN plan)) (VP (VBD was) (VP (VBN stopped))) (. .))', 'good'),
    ('They have planned it.', '(S (NP (PRP They)) (VP (VBP have) (VP (VBN planned) (NP (PRP it)))) (. .))', 'good'),
    ('Maria bought a smartphone.  (OOV word)', '(S (NP (NNP Maria)) (VP (VBD bought) (NP (DT a) (NN smartphone))) (. .))', 'good'),
]


def verdict_old(root, text):
    """Baseline: the matrix WITHOUT the licensing layer (rules + tree only)."""
    saved = new_matrix.licensing
    new_matrix.licensing = None
    try:
        s = new_matrix.evaluate(root, text=text)['summary']
    finally:
        new_matrix.licensing = saved
    return 'ungrammatical' if not s['valid'] else 'accepted'


def verdict_new(root, text):
    s = new_matrix.evaluate(root, text=text)['summary']
    return s['verdict'], s


def main():
    rows, bad_old, bad_new, good_ok_old, good_ok_new = [], 0, 0, 0, 0
    n_bad = sum(1 for c in CASES if c[2] == 'bad')
    n_good = len(CASES) - n_bad
    print(f"{'sentence':<52}{'gold':<5}{'BEFORE':<15}{'AFTER':<15}")
    print('-' * 88)
    for label, ps, gold in CASES:
        # strip the annotation, e.g. 'I am stupids.  [NNS]' -> 'I am stupids.'
        text = re.sub(r'\s*[\[(][^\])]*[\])]$', '', label)
        root = build(ps)
        o = verdict_old(root, text)
        n, summ = verdict_new(root, text)
        if gold == 'bad':
            bad_old += o == 'ungrammatical'
            bad_new += n == 'ungrammatical'
            flag = '' if n == 'ungrammatical' else '   <-- STILL MISSED'
        else:
            good_ok_old += o != 'ungrammatical'
            good_ok_new += n != 'ungrammatical'
            flag = '' if n != 'ungrammatical' else '   <-- FALSE POSITIVE'
        print(f"{label:<52}{gold:<5}{o:<15}{n:<15}{flag}")
        if n == 'unverified':
            for f in summ['unverified']:
                pass
    print('-' * 88)
    print(f"Recall on ungrammatical : before {bad_old}/{n_bad}  ->  after {bad_new}/{n_bad}")
    print(f"Good not rejected       : before {good_ok_old}/{n_good}  ->  after {good_ok_new}/{n_good}")
    return 0 if (bad_new == n_bad and good_ok_new == n_good) else 1


if __name__ == '__main__':
    sys.exit(main())
