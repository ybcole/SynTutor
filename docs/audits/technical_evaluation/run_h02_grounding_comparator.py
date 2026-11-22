"""Paired whole-system grounding comparator for SynTutor H02.

Compares two genuinely functional, same-system conditions on the exact same
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

Does NOT modify any frozen evaluation scripts, datasets, or human worksheets.
Outputs exact paired contingency tables, exact two-sided McNemar binomial tests
on published external ground-truth labels, official ERRANT and EXPECT metrics,
and a blank (unfabricated) blinded comparison worksheet for human prose review.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path
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
    det = grounded_view['summary'].get('detector') or detector.classify(text)
    parse_info = grounded_view['parse']
    tokens = parse_info['tokens']
    sentence = parse_info['text']
    acceptable = bool(det and det.get('acceptable'))
    verdict = 'grammatical' if acceptable else 'ungrammatical'
    correction = None
    target_ids: list[int] = []
    explanation = (det.get('explanation') if det else 'No acceptability rating available.')
    if not acceptable and det and det.get('available'):
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
    for (hs, he), (rs, re_) in zip(hyps, refs):
        tp = len(he & re_)
        fp = len(he - re_)
        rows.append({'sentence': rs, 'n_hyp': len(he), 'n_ref': len(re_), 'tp': tp, 'fp': fp})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    batch = json.loads(args.manifest.read_text(encoding='utf-8'))
    if batch['scorer_sha256'] != external.digest(Path(external.__file__)):
        raise ValueError('Frozen external scorer digest changed')
    for name in ('blimp.tar.gz', 'wi-locness-v2.1.tar.gz', 'expect-test.json'):
        if batch['source_sha256'][name] != external.digest(args.sources / name):
            raise ValueError(f'Frozen source digest changed for {name}')

    parse_engine.load_models()
    all_rows = [row for name in ('blimp', 'wi', 'expect') for row in batch[name]]
    sentences = list(dict.fromkeys(row['sentence'] for row in all_rows))

    grounded_views = {}
    grounded_fail = {}
    ungrounded_views = {}
    for text in sentences:
        try:
            view = analysis_api.build_payload(text)
            grounded_views[text] = view
            ungrounded_views[text] = run_ungrounded(text, view)
        except Exception as exc:
            grounded_fail[text] = f'{type(exc).__name__}: {exc}'

    def _grounded_loader(text):
        if text in grounded_fail:
            raise ValueError(grounded_fail[text])
        view = grounded_views[text]
        if view['parse']['sentence_count'] != 1 or view['parse']['text'] != text.strip():
            raise ValueError('application did not analyze the entire scoring item as one sentence')
        return view

    def _ungrounded_loader(text):
        if text in grounded_fail:
            raise ValueError(grounded_fail[text])
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
        pair_key = ':'.join(row['item_id'].split(':')[:2])
        by_pair.setdefault(pair_key, []).append((g_ok, u_ok))

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
    for gr, ur in zip(g_m2_rows, u_m2_rows):
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

    # Generate blank blinded human-review worksheet (NEVER fabricate human ratings)
    rng = random.Random(20261122)
    ws_path = args.output / 'BLINDED_GROUNDED_VS_UNGROUNDED_WORKSHEET.csv'
    key_path = args.output / 'BLINDED_KEY_SEALED.json'
    sealed_key = []
    with ws_path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow([
            'pair_id', 'dataset', 'source_sentence',
            'system_X_verdict', 'system_X_correction', 'system_X_explanation',
            'system_Y_verdict', 'system_Y_correction', 'system_Y_explanation',
            'r1_X_principle_0_1', 'r1_X_application_0_1', 'r1_X_targets_0_1',
            'r1_X_evidence_0_1', 'r1_X_no_false_claim_0_1',
            'r1_Y_principle_0_1', 'r1_Y_application_0_1', 'r1_Y_targets_0_1',
            'r1_Y_evidence_0_1', 'r1_Y_no_false_claim_0_1',
            'r1_preferred_X_Y_tie', 'r1_notes',
        ])
        pid = 0
        for ds_name in ('blimp', 'wi', 'expect'):
            for row in batch[ds_name]:
                s = row['sentence']
                if s not in grounded_views:
                    continue
                gv = grounded_views[s]
                uv = ungrounded_views[s]
                g_exp = gv['learner_analysis'].get('sentence_text') or gv['summary'].get('explanation') or ''
                u_exp = uv['explanation']
                g_tuple = (gv['summary']['verdict'], gv['summary'].get('corrected_sentence') or '', g_exp)
                u_tuple = (uv['verdict'], uv['corrected_sentence'] or '', u_exp)
                if g_tuple == u_tuple:
                    continue
                pid += 1
                flip = rng.choice([True, False])
                sx, sy = (u_tuple, g_tuple) if flip else (g_tuple, u_tuple)
                writer.writerow([f'H02-PAIR-{pid:03d}', ds_name, s, *sx, *sy] + [''] * 12)
                sealed_key.append({
                    'pair_id': f'H02-PAIR-{pid:03d}',
                    'system_X': 'ungrounded' if flip else 'grounded',
                    'system_Y': 'grounded' if flip else 'ungrounded',
                })
    key_path.write_text(json.dumps(sealed_key, indent=2), encoding='utf-8')

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
        'blinded_worksheet': {
            'path': str(ws_path),
            'n_differing_pairs': len(sealed_key),
            'human_annotated': False,
        },
    }
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
