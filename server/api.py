"""SynTutor analysis core shared by every backend entry point.

Pure request/response logic lives here (no HTTP server): model-status probing
and the hybrid ``build_payload`` that turns a sentence into the tree + rule
matrix + explainer payload. ``app.py`` (stdlib http.server) and ``webapp.py``
(Flask) both import from this module so they cannot drift apart.
"""

from parse_engine import ParseFailure, analyze, load_models
from matrix import evaluate, _rem_from_text
from detector import classify, classify_many, combine
from licensing import _leaves as _tree_leaves
from licensing import _finding
import corrector
import corrections

_MODEL_STATUS = None

INSTALL_HINT = (
    'Run:  pip install spacy benepar transformers==4.46.3  &&  '
    'python -m spacy download en_core_web_md  &&  '
    'python -m benepar.download benepar_en3'
)


def model_status():
    """Probe (once) whether spaCy + benepar are loadable."""
    global _MODEL_STATUS
    if _MODEL_STATUS is None:
        status = {'ready': False, 'spacy': None, 'benepar': None, 'error': None}
        try:
            nlp = load_models()
            status = {
                'ready': True,
                'spacy': (nlp.meta or {}).get('version'),
                'benepar': 'benepar_en3',
                'pipeline': list(nlp.pipe_names),
            }
        except Exception as exc:  # noqa: BLE001
            status['error'] = str(exc)
        _MODEL_STATUS = status
    return _MODEL_STATUS


def health_payload():
    status = model_status()
    return {
        'status': 'ok' if status['ready'] else 'degraded',
        'ready': status['ready'],
        'models': {
            'spacy_model': 'en_core_web_md',
            'parser_model': 'benepar_en3',
        },
        'spacy_version': status.get('spacy'),
        'pipeline': status.get('pipeline'),
        'error': status.get('error'),
        'install_hint': INSTALL_HINT if not status['ready'] else None,
    }


def word_info(words):
    """Validate a list of words against SynTutor's own model.

    A word is "valid" when SynTutor's lexicon (the same dictionary the spelling
    layer uses) knows it, or -- for capitalised/non-alphabetic tokens that the
    lexicon cannot judge -- when spaCy does not mark it out-of-vocabulary. Each
    entry also carries the official spaCy POS tag and, for an invalid word, the
    best spelling candidate so the builder can coach the learner.
    """
    import spellcheck

    result = []
    for raw in words or []:
        w = (raw or '').strip()
        if not w:
            result.append({'word': w, 'valid': False, 'tag': None, 'suggestion': None})
            continue
        valid = spellcheck.known_word(w)
        tag = None
        status = model_status()
        if status['ready'] and status.get('pipeline'):
            try:
                nlp = load_models()
                doc = nlp(w)
                if len(doc):
                    tag = doc[0].tag_
            except Exception:  # noqa: BLE001 - tagging is best-effort
                tag = None
        suggestion = None
        if not valid:
            suggestion = spellcheck.best_correction(w)
        result.append({'word': w, 'valid': bool(valid), 'tag': tag,
                       'suggestion': suggestion})
    return result



def build_payload(text, sentence_index=0):
    """Hybrid payload for one user input, targeting ``sentence_index``.

    Two channels: the rule matrix explains (deterministic), and a CoLA
    acceptability model detects (trained). A sentence is grammatical only if
    both accept; a rules-clean but model-rejected sentence is UNVERIFIED, and
    the model's reasoning is surfaced because the rules cannot explain it.
    """
    analysis = analyze(text, sentence_index=sentence_index)
    result = evaluate(analysis['root'], text=analysis['sentence'])
    details = result['details']
    summary = result['summary']
    root = analysis['root']
    tokens = analysis['tokens']

    det = classify(analysis['sentence'])
    perturbation = None
    if det is not None:
        summary = combine(summary, det)
        # Text-space correction search: the rules could not explain the model's
        # rejection, so locate the single-token swap that restores acceptability
        # and derive the explanation from the morphological delta (corrector).
        if (summary.get('verdict') == 'unverified'
                and not det['acceptable'] and det.get('available')
                and not summary.get('suggested')):
            span_zero = (analysis['sentences'][analysis['sentence_index']]['start']
                         if analysis['sentences'] else 0)
            spans = [(t['start'] - span_zero, t['end'] - span_zero)
                     for t in tokens if (t['t'] or '').isalpha()]
            located = corrector.sweep(
                analysis['sentence'], classify_many, spans=spans)
            if located is not None:
                promoted = _apply_correction(
                    located, root, details, summary, analysis['sentence'], det)
                if promoted is not None:
                    perturbation = promoted

    correction = None
    if (summary.get('verdict') != 'grammatical'
            or corrections.has_actionable(details)):
        correction = corrections.assemble(
            analysis['sentence'], details, tokens,
            validate=_validate_correction)
        if correction is not None:
            summary['correction'] = correction
            summary['corrected_sentence'] = correction['corrected_sentence']

    token_line = ' \u00b7 '.join(f"{t['t']}/{t['pos']}" for t in tokens)
    tag_word = summary['explanation']
    label = {'grammatical': 'VALID', 'ungrammatical': 'INVALID',
             'unverified': 'UNVERIFIED'}.get(summary.get('verdict'),
                                             'VALID' if summary['valid'] else 'INVALID')

    basic_lines = [
        f"Input: {analysis['sentence']}",
        f"Neural parse (benepar_en3): {analysis['parse_string']}",
        f"Token stream: {token_line}",
        f"Constraint matrix: {summary['valid_edges']} validated \u00b7 "
        f"{summary['violated_edges']} violated \u00b7 {summary['unrated_edges']} unrated",
        f"Verdict: {label}",
        f"   {tag_word}",
        'Deterministic matrix over the benepar tree; identical inputs always produce identical verdicts.',
    ]
    if 'detector' in summary:
        det_m = summary['detector']
        basic_lines.append(
            f"Hybrid detection ({det_m['model']}): {det_m['label']} "
            f"(p(acceptable)={det_m['acceptable_prob']:.2f})")
        basic_lines.append(f"   {summary['detector_note']}")
        if summary.get('verdict') == 'unverified' and det_m['label'] == 'unacceptable':
            basic_lines.append(
                'The matrix could not explain the rejection, so the verdict stays '
                'UNVERIFIED rather than UNGRAMMATICAL.')
    elif summary.get('unverified'):
        basic_lines.append(
            'Detection channel offline - verdict reflects the rule matrix only.')

    if perturbation:
        basic_lines.append(f"MLM correction search: {perturbation['note']}")
    if correction is not None:
        basic_lines.append(corrections.describe(correction))

    # Sentence-level truth gating: a node may be structurally well formed while
    # the sentence as a whole is not.  Never show a green "valid" badge on an
    # ungrammatical/unverified sentence; keep the structural description as
    # neutral instead.  UIs should key on display_status.
    verdict = summary.get('verdict')
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        raw_status = detail.get('status')
        if raw_status == 'error':
            detail['display_status'] = 'error'
        elif raw_status == 'valid' and verdict == 'grammatical':
            detail['display_status'] = 'valid'
        else:
            detail['display_status'] = 'neutral'

    contrastive = _contrastive(summary, details)
    pipeline = _pipeline_narration(analysis, summary, details)
    concepts = _rule_concepts(details, summary)

    return {
        'meta': {
            'deterministic': 'detector' not in summary,
            'k': 1,
            'parser': 'benepar_en3',
            'spacy': 'en_core_web_md',
            'backend': ('spaCy + benepar (neural constituency) + rule matrix (XAI) '
                        '+ CoLA acceptability model (hybrid)'
                        if 'detector' in summary else
                        'spaCy + benepar (neural constituency) + rule matrix (XAI)'),
            'sentence_count': analysis['sentence_count'],
            'target_sentence': analysis['sentence_index'] + 1,
        },
        'parse': {
            'text': analysis['sentence'],
            'sentence_count': analysis['sentence_count'],
            'sentences': analysis['sentences'],
            'tokens': tokens,
            'parse_string': analysis['parse_string'],
        },
        'tree': root,
        'nodes': analysis['nodes'],
        'node_details': details,
        'summary': summary,
        'explainers': {
            'basic': '\n'.join(basic_lines),
            'contrastive': contrastive,
            'surprisal': None,
            'perturbation': perturbation['note'] if perturbation else None,
            'correction': corrections.describe(correction),
            'llm_note': None,
            'pipeline': pipeline,
            'concepts': concepts,
        },
    }


def _pipeline_narration(analysis, summary, details):
    """The 4-stage story (tokenize -> POS -> parse -> rules) for one sentence.

    Same vocabulary and order as the Syntax-Tree Quiz and the Syntax Builder, so
    the tutor, the quiz, and the builder all describe a sentence identically.
    """
    tokens = analysis['tokens']
    stages = [
        {
            'id': 1,
            'title': 'Tokenizer',
            'summary': f"{len(tokens)} token(s): "
                       + ' \u00b7 '.join(t['t'] for t in tokens),
        },
        {
            'id': 2,
            'title': 'Part-of-speech tagger',
            'summary': ' \u00b7 '.join(f"{t['t']}/{t['pos']}" for t in tokens),
        },
        {
            'id': 3,
            'title': 'Constituency parser',
            'summary': analysis['parse_string'],
        },
        {
            'id': 4,
            'title': 'Rule matrix',
            'summary': (f"{summary['valid_edges']} validated \u00b7 "
                        f"{summary['violated_edges']} violated \u00b7 "
                        f"{summary['unrated_edges']} unrated"),
        },
    ]
    return {
        'stages': stages,
        'verdict': summary.get('verdict'),
        'constraints_fired': summary.get('constraints_fired', []),
    }


def _rule_concepts(details, summary):
    """Concept text (from tree_sheet.json) for every rule that fired.

    Gives the *why* behind each violation using the same concept that the tree
    quiz teaches, keyed by rule id.
    """
    try:
        from . import master
    except Exception:  # noqa: BLE001
        try:
            import master
        except Exception:  # noqa: BLE001
            return []
    seen = {}
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        rid = detail.get('rule_id')
        status = detail.get('status')
        if rid and status in ('error', 'unverified'):
            seen.setdefault(rid, detail.get('text', ''))
        for finding in detail.get('findings', []) or []:
            frid = finding.get('rule_id')
            if frid:
                seen.setdefault(frid, finding.get('text', ''))
    out = []
    for rid, text in seen.items():
        out.append({
            'rule': rid,
            'concept': master.concept(rid),
            'note': text,
        })
    return out


def _validate_correction(candidate):
    """A correction is only exposed when the matrix and detector both accept it."""
    try:
        analysis = analyze(candidate, sentence_index=0)
        summary = evaluate(analysis['root'], text=analysis['sentence'])['summary']
        if summary.get('verdict') != 'grammatical' or summary.get('checker_errors'):
            return False
        det = classify(analysis['sentence'])
        if det is not None and det.get('available') and not det.get('acceptable'):
            return False
        return True
    except Exception:  # noqa: BLE001 - a failed candidate is simply skipped
        return False


def _apply_correction(located, root, details, summary, sentence, det):
    """Promote a located single-token correction to a deterministic finding.

    Promotes only when the corrected sentence is *confirmed* grammatical by the
    rule matrix (so the "good" word's tag comes from a clean, gold-projected
    tree) and the two words are provably two forms of one lemma (so a flat
    meaning swap like reddish->red is never turned into a condemnation).  Two
    confidence margins guard against a noisy classifier falsely "fixing" a
    grammatical sentence: the original must be rejected by a clear margin and
    the flip must be accepted by a clear margin.
    """
    bad, good = located['bad'], located['good']
    corrected = located['corrected_text']
    if det.get('acceptable_prob', 0.5) >= 0.45:
        return None
    if located.get('cola_p', 0.0) < 0.6:
        return None
    try:
        clean = analyze(corrected, sentence_index=0)
    except Exception:  # noqa: BLE001 - keep the original unverified verdict
        return None
    cres = evaluate(clean['root'], text=clean['sentence'])
    if not cres['summary']['valid'] or cres['summary'].get('root_error') \
            or any(d['status'] == 'error' for d in cres['details'].values()):
        return None

    orig_leaves = _tree_leaves(root)
    clean_leaves = _tree_leaves(clean['root'])
    if len(orig_leaves) != len(clean_leaves):
        return None
    position = located['position']
    if position >= len(orig_leaves):
        return None
    good_tag = clean_leaves[position].get('type')
    bad_id = orig_leaves[position]['id']

    diff = corrector.morph_diff(bad, good, good_tag=good_tag)
    if diff is None:
        return None
    _lemma, _bad_tag, bad_label, _good_tag_l, good_label = diff
    required_label = corrector.EXTENDED_TAG_LABEL.get(good_tag, '') or good_label
    core = corrector.template(bad, good, required_label, bad_label)
    bad_detail = details.get(bad_id) or {}
    parent = details.get(bad_detail.get('parent') or '') if bad_detail else None
    where = ''
    if parent is not None:
        where = f" inside the {parent.get('type')} '{parent.get('surface', '')}'"
    text = (f"The word '{bad}'{where} is used where the structure requires "
            f"the {required_label} form. {core}")
    remediation = (f"Replace '{bad}' with '{good}' "
                   f"({required_label or 'the required form'}).")

    finding = _finding(
        '11.4', 'error', 'C-MLM-ANOMALY', 'word form', bad_id, text,
        {'used': 'mlm', 'lookup': bad, 'accepted': [good],
         'source': (f"masked-language-model sweep ({corrector._MLM_MODEL}) "
                    f"+ acceptability flip (p(acceptable)={located['cola_p']:.2f})")},
        remediation)
    detail = details.get(bad_id) or details.get(root['id'], {})
    finding['id'] = f"{bad_id}:11.4"
    detail.setdefault('findings', []).append(finding)
    detail['status'] = 'error'
    detail['text'] = text
    detail['remediation'] = _rem_from_text(text, bad)
    details[bad_id] = detail

    summary['flagged'] = True
    summary['verdict'] = 'ungrammatical'
    summary['valid'] = False
    summary['violated_edges'] = summary.get('violated_edges', 0) + 1
    summary['violations'] = list(summary.get('violations') or [])
    if bad_id not in summary['violations']:
        summary['violations'].append(bad_id)
    summary['constraints_fired'] = list(summary.get('constraints_fired') or [])
    if 'C-MLM-ANOMALY' not in summary['constraints_fired']:
        summary['constraints_fired'].append('C-MLM-ANOMALY')
    summary['explanation'] = text

    note = (f"masking '{bad}' and substituting '{good}' restores "
            f"acceptability (p(acceptable)={located['cola_p']:.2f}); the "
            f"corrected sentence passed the rule matrix (projected tag of "
            f"'{good}' = {good_tag}), so the verdict is promoted to "
            f"UNGRAMMATICAL. {text}")
    return {
        'note': note,
        'method': 'masked-language-model text-space sweep',
        'bad': bad, 'good': good,
        'bad_pos': bad_label, 'good_pos': good_tag,
        'corrected_sentence': corrected,
        'cola_p': located['cola_p'],
    }


def _contrastive(summary, details):
    if summary['valid'] and not summary.get('root_error'):
        return ('No grammatical alternative is observed: every edge is licensed, so no repair is '
                'needed. The sentence is fully determined by the matrix.')
    errors = [d for d in details.values() if d['status'] == 'error']
    if not errors:
        return 'No edge violation to repair.'
    first = errors[0]
    breaks = {
        'C-SUBJECT-AGREEMENT': 'making the predicate verb agree with the subject',
        'C-DETERMINER-AGREEMENT': 'switching the determiner to the number forced by its noun',
        'C-DET-STACK': 'removing one of the stacked determiners',
        'C-MOD-POS': 'moving the modifier before its head noun',
        'C-AUX-FORM': 'using the verb form required by the auxiliary',
        'C-TENSE-FINITE': 'adding a finite predicate verb',
        'C-MLM-ANOMALY': 'replacing the anomalous word with the form the structure requires',
    }
    repair = breaks.get(first['constraint'])
    surface = first.get('surface', '') or first['id']
    if repair is None:
        repair = (f"fixing the flagged word '{surface}' so the "
                  f"constraint '{first['constraint']}' is satisfied")
    return (f"A repair appears possible: the word '{surface}' is the point of "
            f"the violation, and the sentence would be licensed after {repair}.")
