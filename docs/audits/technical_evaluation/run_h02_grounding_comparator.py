"""Paired grounded versus neural-only diagnostic comparison for SynTutor H02.

Compares two system configurations on the exact same
frozen external manifest (BLiMP 116, W&I+LOCNESS 120, EXPECT 169):

  Condition A (Grounded SynTutor):
    Full production analysis_api.build_payload(text) with Linguistic Constraint
    Matrix, Cambridge rule evaluation, Burton-Roberts canonical tree,
    supported_findings() evidence corroboration, CoLA advisory, and re-parse
    validated corrections.

  Condition B (Ungrounded Neural SynTutor):
    Identical spaCy/Benepar parse and identical SynTutor neural acceptability
    detector (RoBERTa-CoLA) + SynTutor masked-language-model perturbation
    corrector (corrector.sweep + morph_diff), WITHOUT Linguistic Constraint
    Matrix / Cambridge rule grounding or supported_findings() corroboration.

This compares subsystems, including their different correction policies.
Outputs exact paired contingency tables, exact two-sided McNemar binomial tests
on published external ground-truth labels, official ERRANT and EXPECT metrics,
and a blank (unfabricated) blinded comparison worksheet for human prose review.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path
from secrets import SystemRandom, token_hex
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SERVER_DIR = ROOT / 'server'
EVAL_DIR = Path(__file__).resolve().parent
for p in (str(SERVER_DIR), str(EVAL_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import analysis_api  # noqa: E402
import corrector  # noqa: E402
import detector  # noqa: E402
import parse_engine  # noqa: E402
import run_phase2_external as external  # noqa: E402


def exact_mcnemar(b: int, c: int) -> dict:
    """Two-sided exact McNemar binomial test on discordant pairs (b, c)."""
    n = b + c
    if n == 0:
        return {'b': b, 'c': c, 'n_discordant': 0, 'p_value': 1.0}
    k = min(b, c)
    # Two-sided exact binomial p-value with p=0.5
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    p_val = min(1.0, 2.0 * tail)
    return {'b': b, 'c': c, 'n_discordant': n, 'p_value': round(p_val, 8)}


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> list[float]:
    if n <= 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / denom
    return [round(max(0.0, center - half), 4), round(min(1.0, center + half), 4)]


def run_ungrounded(text: str, grounded_view: dict) -> dict:
    """Run SynTutor's built-in neural detector + MLM perturbation corrector
    without Matrix/Cambridge/supported_findings grounding."""
    parse_info = grounded_view['parse']
    tokens = parse_info['tokens']
    sentence = parse_info['text']
    det = grounded_view['summary'].get('detector') or detector.classify(sentence)
    acceptable = bool(det and det.get('acceptable'))
    verdict = ('grammatical' if acceptable else 'ungrammatical') if (
        det and det.get('available')) else 'unverified'
    correction = None
    target_ids: list[int] = []
    explanation = (det.get('explanation') if det else 'No acceptability rating available.')
    if verdict == 'ungrammatical':
        spans = [(t['start'], t['end']) for t in tokens if (t['t'] or '').isalpha()]
        located = corrector.sweep(sentence, detector.classify_many, spans=spans)
        if located is not None:
            correction = located.get('corrected_text')
            pos = located.get('position')
            alpha_tokens = [t for t in tokens if (t['t'] or '').isalpha()]
            if pos is not None and 0 <= pos < len(alpha_tokens):
                target_ids = [alpha_tokens[pos]['i']]
            bad, good = located.get('bad'), located.get('good')
            diff = corrector.morph_diff(bad, good) if bad and good else None
            if diff is not None:
                _lem, _bt, bad_lbl, _gt, good_lbl = diff
                explanation = (
                    f"Neural acceptability model flagged the sentence as unacceptable; "
                    f"masked-language-model perturbation suggests replacing '{bad}' "
                    f"({bad_lbl}) with '{good}' ({good_lbl})."
                )
            else:
                explanation = (
                    f"Neural acceptability model flagged the sentence as unacceptable; "
                    f"masked-language-model perturbation suggests replacing '{bad}' with '{good}'."
                )
    findings = []
    if not acceptable and target_ids:
        findings.append({
            'constraint': 'C-UNGROUNDED-NEURAL',
            'text': explanation,
            'target_token_ids': target_ids,
            'related_token_ids': [],
        })
    return {
        'parse': parse_info,
        'verdict': verdict,
        'detector': det,
        'corrected_sentence': correction,
        'explanation': explanation,
        'findings': findings,
    }


def parse_m2_fp_flags(hyp_path: Path, ref_path: Path) -> list[dict]:
    """Per-sentence edit counts comparing hyp M2 against ref M2."""
    def _load(path: Path):
        blocks = path.read_text(encoding='utf-8').strip().split('\n\n')
        out = []
        for blk in blocks:
            lines = [ln for ln in blk.splitlines() if ln.strip()]
            sent = lines[0][2:] if lines else ''
            edits = set()
            for ln in lines[1:]:
                if ln.startswith('A '):
                    parts = ln[2:].split('|||')
                    if parts[1] != 'noop':
                        edits.add((parts[0], parts[2]))
            out.append((sent, edits))
        return out

    hyps = _load(hyp_path)
    refs = _load(ref_path)
    rows = []
    for (hs, he), (rs, re_) in zip(hyps, refs, strict=True):
        if hs != rs:
            raise ValueError('M2 alignment mismatch between hypothesis and reference')
        tp = len(he & re_)
        fp = len(he - re_)
        rows.append({'sentence': rs, 'n_hyp': len(he), 'n_ref': len(re_), 'tp': tp, 'fp': fp})
    return rows


CONCEPTS = ('principle', 'application', 'targets', 'evidence', 'no_false_claim')


def pair_groups(rows):
    groups = {}
    for row in rows:
        key, label = row['item_id'].rsplit(':', 1)
        if label != row['gold_label'] or label in groups.setdefault(key, {}):
            raise ValueError(f'Duplicate or invalid BLiMP pair member: {row["item_id"]}')
        groups[key][label] = row['sentence']
    for key, members in groups.items():
        if set(members) != {'grammatical', 'ungrammatical'} or len(set(members.values())) != 2:
            raise ValueError(f'Incomplete BLiMP pair: {key}')
    return groups


def paired_interval(groups, replications=10000):
    """Percentile interval resampling the supplied groups as intact units."""
    rng = random.Random(20261122)
    draws = sorted(sum(sum(group) for group in sample) / sum(map(len, sample))
                   for _ in range(replications)
                   for sample in [rng.choices(groups, k=len(groups))])
    return [draws[int((replications - 1) * q)] for q in (.025, .975)]


def holm_adjust(tests):
    adjusted, maximum = {}, 0
    for i, (name, p) in enumerate(sorted(tests.items(), key=lambda item: item[1])):
        maximum = max(maximum, min(1, (len(tests) - i) * p))
        adjusted[name] = maximum
    return adjusted


def write_review(output, pairs):
    """Include identical and unavailable pairs so the intake denominator is visible."""
    rng = SystemRandom()
    worksheet = output / 'BLINDED_GROUNDED_VS_UNGROUNDED_WORKSHEET.csv'
    key = output / 'BLINDED_KEY_SEALED.json'
    key_rows = []
    shown = ('availability', 'verdict', 'correction', 'explanation')
    ratings = [f'{arm}_{criterion}_rating' for arm in ('X', 'Y') for criterion in CONCEPTS]
    with worksheet.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(['pair_id', 'source_sentence',
                         *(f'{arm}_{field}' for arm in ('X', 'Y') for field in shown),
                         *ratings, 'notes'])
        for text, ground, neural in rng.sample(pairs, len(pairs)):
            pair_id = token_hex(16)
            arms = [('grounded', ground), ('neural_only', neural)]
            rng.shuffle(arms)
            writer.writerow([pair_id, text, *arms[0][1], *arms[1][1], *[''] * (len(ratings) + 1)])
            key_rows.append({'pair_id': pair_id, 'X': arms[0][0], 'Y': arms[1][0]})
    # Keep the identity map out of the reviewer materials.
    with open(key, 'x', encoding='utf-8', opener=lambda path, flags: os.open(path, flags, 0o600)) as handle:
        json.dump(key_rows, handle, indent=2)
    return {'path': str(worksheet), 'n_total_pairs': len(pairs),
            'n_identical_pairs': sum(x == y for _, x, y in pairs),
            'n_differing_pairs': sum(x != y for _, x, y in pairs),
            'n_both_available': sum(x[0] == y[0] == 'available' for _, x, y in pairs),
            'human_annotated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)

    batch = json.loads(args.manifest.read_text(encoding='utf-8'))
    if batch['scorer_sha256'] != external.digest(Path(external.__file__)):
        raise ValueError('Frozen external scorer digest changed')
    for name in ('blimp.tar.gz', 'wi-locness-v2.1.tar.gz', 'expect-test.json'):
        if batch['source_sha256'][name] != external.digest(args.sources / name):
            raise ValueError(f'Frozen source digest changed for {name}')

    parse_engine.load_models()
    all_rows = [row for name in ('blimp', 'wi', 'expect') for row in batch[name]]
    sentences = list(dict.fromkeys(row['sentence'] for row in all_rows))
    if len(sentences) != len(all_rows):
        raise ValueError('Expected distinct inputs across the frozen sample')
    memberships = pair_groups(batch['blimp'])

    grounded_views = {}
    grounded_fail = {}
    ungrounded_views = {}
    ungrounded_fail = {}
    for text in sentences:
        try:
            view = analysis_api.build_payload(text)
            if view['parse']['sentence_count'] != 1 or view['parse']['text'] != text.strip():
                raise ValueError('application did not analyze the entire scoring item as one sentence')
            grounded_views[text] = view
        except Exception as exc:
            grounded_fail[text] = f'{type(exc).__name__}: {exc}'
            ungrounded_fail[text] = grounded_fail[text]
            continue
        try:
            ungrounded_views[text] = run_ungrounded(text, view)
        except Exception as exc:
            ungrounded_fail[text] = f'{type(exc).__name__}: {exc}'

    def _grounded_loader(text):
        if text in grounded_fail:
            raise ValueError(grounded_fail[text])
        view = grounded_views[text]
        if view['parse']['sentence_count'] != 1 or view['parse']['text'] != text.strip():
            raise ValueError('application did not analyze the entire scoring item as one sentence')
        return view

    def _ungrounded_loader(text):
        if text in ungrounded_fail:
            raise ValueError(ungrounded_fail[text])
        uv = ungrounded_views[text]
        if uv['parse']['sentence_count'] != 1 or uv['parse']['text'] != text.strip():
            raise ValueError('application did not analyze the entire scoring item as one sentence')
        return {
            'parse': uv['parse'],
            'summary': {'verdict': uv['verdict'], 'corrected_sentence': uv['corrected_sentence']},
            'learner_analysis': {'findings': uv['findings']},
        }

    g_dir = args.output / 'grounded'
    u_dir = args.output / 'ungrounded'
    g_dir.mkdir()
    u_dir.mkdir()

    with patch.object(external, 'load_application_sentence', _grounded_loader):
        g_wi = external.score_wi(batch['wi'], g_dir)
        g_expect = external.score_expect(batch['expect'], g_dir)
    with patch.object(external, 'load_application_sentence', _ungrounded_loader):
        u_wi = external.score_wi(batch['wi'], u_dir)
        u_expect = external.score_expect(batch['expect'], u_dir)

    # BLiMP paired item-level & minimal-pair-level McNemar tests
    blimp_counts = {'grounded': Counter(), 'ungrounded': Counter()}
    b_all = c_all = 0
    b_fp = c_fp = 0
    by_pair = {}
    paired_rows = []
    for row in batch['blimp']:
        s = row['sentence']
        gold = row['gold_label']
        gv = grounded_views[s]['summary']['verdict'] if s in grounded_views else 'failure'
        uv = ungrounded_views[s]['verdict'] if s in ungrounded_views else 'failure'
        blimp_counts['grounded'][(gold, gv)] += 1
        blimp_counts['ungrounded'][(gold, uv)] += 1
        g_ok = (gv == gold)
        u_ok = (uv == gold)
        if g_ok and not u_ok:
            b_all += 1
        elif u_ok and not g_ok:
            c_all += 1
        if gold == 'grammatical':
            # Unsound ungrammatical feedback on a grammatical sentence
            g_bad = (gv == 'ungrammatical')
            u_bad = (uv == 'ungrammatical')
            if (not g_bad) and u_bad:
                b_fp += 1
            elif g_bad and (not u_bad):
                c_fp += 1
        pair_key = row['item_id'].rsplit(':', 1)[0]
        by_pair.setdefault(pair_key, []).append((g_ok, u_ok))
        paired_rows.append({'item_id': row['item_id'], 'pair': pair_key,
                            'gold': gold, 'grounded': gv, 'neural_only': uv})

    b_pair = c_pair = g_pair_ok = u_pair_ok = 0
    for pk, items in by_pair.items():
        gp = all(x[0] for x in items)
        up = all(x[1] for x in items)
        g_pair_ok += int(gp)
        u_pair_ok += int(up)
        if gp and not up:
            b_pair += 1
        elif up and not gp:
            c_pair += 1

    # W&I per-sentence FP presence McNemar
    g_m2_rows = parse_m2_fp_flags(g_dir / 'wi-hyp.m2', g_dir / 'wi-ref.m2')
    u_m2_rows = parse_m2_fp_flags(u_dir / 'wi-hyp.m2', u_dir / 'wi-ref.m2')
    b_wi_fp = c_wi_fp = 0
    for gr, ur in zip(g_m2_rows, u_m2_rows, strict=True):
        if gr['sentence'] != ur['sentence']:
            raise ValueError('W&I arms disagree on source order')
        g_has_fp = gr['fp'] > 0
        u_has_fp = ur['fp'] > 0
        if (not g_has_fp) and u_has_fp:
            b_wi_fp += 1
        elif g_has_fp and (not u_has_fp):
            c_wi_fp += 1

    g_exact = blimp_counts['grounded'][('grammatical', 'grammatical')] + blimp_counts['grounded'][('ungrammatical', 'ungrammatical')]
    u_exact = blimp_counts['ungrounded'][('grammatical', 'grammatical')] + blimp_counts['ungrounded'][('ungrammatical', 'ungrammatical')]
    g_fp_n = blimp_counts['grounded'][('grammatical', 'ungrammatical')]
    u_fp_n = blimp_counts['ungrounded'][('grammatical', 'ungrammatical')]

    unavailable = ('unavailable', '', '', '')
    packets = []
    for text in sentences:
        ground, neural = unavailable, unavailable
        if text in grounded_views:
            gv = grounded_views[text]
            learner = gv['learner_analysis']
            prose = [learner.get('sentence_text', ''), *(f['text'] for f in learner['findings'])]
            ground = ('available', gv['summary']['verdict'],
                      (learner.get('revision') or {}).get('text', ''), '\n'.join(filter(None, prose)))
        if text in ungrounded_views:
            uv = ungrounded_views[text]
            prose = (uv['explanation'] or '').replace('Neural acceptability model', 'An acceptability check')
            prose = prose.replace('masked-language-model perturbation', 'the correction search')
            neural = ('available', uv['verdict'], uv['corrected_sentence'] or '', prose)
        packets.append((text, ground, neural))
    worksheet = write_review(args.output, packets)
    (args.output / 'blimp-paired.json').write_text(json.dumps(paired_rows, indent=2), encoding='utf-8')
    (args.output / 'processing-failures.json').write_text(
        json.dumps({'grounded': grounded_fail, 'neural_only': ungrounded_fail}, indent=2), encoding='utf-8')
    fp_groups = []
    for members in memberships.values():
        text = members['grammatical']
        gv = grounded_views.get(text, {}).get('summary', {}).get('verdict')
        uv = ungrounded_views.get(text, {}).get('verdict')
        fp_groups.append([int(uv == 'ungrammatical') - int(gv == 'ungrammatical')])
    tests = {
        'blimp_exact': exact_mcnemar(b_all, c_all),
        'blimp_pair_exact': exact_mcnemar(b_pair, c_pair),
        'blimp_false_positive': exact_mcnemar(b_fp, c_fp),
        'wi_unmatched_edits': exact_mcnemar(b_wi_fp, c_wi_fp),
    }

    summary = {
        'manifest_sha256': external.digest(args.manifest),
        'n_total_inputs': len(sentences),
        'blimp': {
            'n': len(batch['blimp']),
            'grounded_exact': g_exact,
            'grounded_exact_rate': round(g_exact / len(batch['blimp']), 4),
            'grounded_exact_ci95': wilson_ci(g_exact, len(batch['blimp'])),
            'grounded_fp_on_grammatical': g_fp_n,
            'grounded_breakdown': {f'{k[0]}->{k[1]}': v for k, v in sorted(blimp_counts['grounded'].items())},
            'ungrounded_exact': u_exact,
            'ungrounded_exact_rate': round(u_exact / len(batch['blimp']), 4),
            'ungrounded_exact_ci95': wilson_ci(u_exact, len(batch['blimp'])),
            'ungrounded_fp_on_grammatical': u_fp_n,
            'ungrounded_breakdown': {f'{k[0]}->{k[1]}': v for k, v in sorted(blimp_counts['ungrounded'].items())},
            'mcnemar_exact_verdict': exact_mcnemar(b_all, c_all),
            'mcnemar_fp_reduction_on_grammatical': exact_mcnemar(b_fp, c_fp),
            'paired_fp_reduction': (u_fp_n - g_fp_n) / len(memberships),
            'paired_fp_reduction_ci95': paired_interval(fp_groups),
            'minimal_pairs': {
                'n_pairs': len(by_pair),
                'grounded_both_exact': g_pair_ok,
                'ungrounded_both_exact': u_pair_ok,
                'mcnemar_pair_exact': exact_mcnemar(b_pair, c_pair),
            },
        },
        'wi_locness': {
            'grounded': g_wi,
            'ungrounded': u_wi,
            'grounded_sentences_with_fp': sum(r['fp'] > 0 for r in g_m2_rows),
            'ungrounded_sentences_with_fp': sum(r['fp'] > 0 for r in u_m2_rows),
            'mcnemar_fp_sentence_reduction': exact_mcnemar(b_wi_fp, c_wi_fp),
        },
        'expect': {
            'grounded': g_expect,
            'ungrounded': u_expect,
        },
        'holm_adjusted_p': holm_adjust({name: test['p_value'] for name, test in tests.items()}),
        'processing_failures': {'grounded': len(grounded_fail), 'neural_only': len(ungrounded_fail)},
        'blinded_worksheet': worksheet,
    }
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
