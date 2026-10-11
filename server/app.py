"""SynTutor backend: serves the static front end and the /api/parse endpoint.

Run:  python3 server/app.py            (then open http://127.0.0.1:8000)
Endpoints:
    GET  /                  static front end (index.html, css, js)
    GET  /api/health        model/pipeline availability
    POST /api/parse         {text} -> JSON payload (tree + node descriptions)
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from parse_engine import ParseFailure, analyze, load_models
from matrix import evaluate, _rem_from_text
from detector import classify, classify_many, combine
from licensing import _leaves as _tree_leaves
from licensing import _finding
import corrector
try:  # package context (imported as server.app)
    from server.semantics import analyze_semantics
except ImportError:  # script context (python3 server/app.py)
    from semantics import analyze_semantics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT, 'web')
PORT = int(os.environ.get('PORT') or os.environ.get('SYNTUTOR_PORT') or '8000')

# CORS: the frontend may be hosted on a different origin (e.g. Vercel) than this
# API. Restrict with SYNTUTOR_ALLOW_ORIGIN (default '*' for easy setup).
ALLOW_ORIGIN = os.environ.get('SYNTUTOR_ALLOW_ORIGIN', '*')

# Only these top-level frontend entries may be served statically. Anything else
# under ROOT (server/, supabase/, scripts/, migrations, config) stays private.
PUBLIC_TOP = {'index.html', 'login.html', 'css', 'js'}

MIME = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.ico': 'image/x-icon',
    '.md': 'text/markdown; charset=utf-8',
}

_MODEL_STATUS = None


def _model_status():
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


def _unavailable_semantics():
    """Schema-consistent semantic payload for a controlled analysis failure.

    Mirrors the live contract (:func:`server.semantics.analyze_semantics`) but
    marks the layer ``unavailable`` so the frontend can distinguish "completed
    with no findings" from "could not be completed" and never silently shows a
    failed analysis as an all-clear.
    """
    return {
        'status': 'unavailable',
        'available': False,
        'findings': [],
        'ambiguous': False,
        'ambiguity': None,
        'tree_variants': [],
        'summary': {
            'status': 'unavailable',
            'available': False,
            'valid': None,
            'findings': 0,
            'errors': 0,
            'warnings': 0,
            'constraints_fired': [],
            'ambiguous_attachments': [],
            'tree_variants': 0,
            'explanation': 'semantic analysis unavailable',
        },
    }


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
                and not det['acceptable'] and det.get('available')):
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
                    perturbation = promoted['perturbation']

    # Semantic layer (spec R11).  Purely additive and never fatal: a failure is
    # logged server-side with a traceback and replaced by an explicitly
    # ``unavailable`` payload, so an unexpected semantic error can never break
    # the syntax response (nor masquerade as a clean "no findings" result).
    try:
        semantics = analyze_semantics(analysis, result)
        semantics.setdefault('status', 'ok')
        semantics.setdefault('available', True)
        if 'ambiguity' not in semantics:
            semantics['ambiguity'] = (
                semantics.get('tree_variants') or None
            )
    except Exception:  # noqa: BLE001
        print('SynTutor: analyze_semantics failed:\n'
              + traceback.format_exc(), file=sys.stderr)
        semantics = _unavailable_semantics()

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

    error_ids = [d for d in details.values() if d['status'] == 'error']
    contrastive = _contrastive(summary, details)

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
        'semantics': semantics,
        'explainers': {
            'basic': '\n'.join(basic_lines),
            'contrastive': contrastive,
            'surprisal': None,
            'perturbation': perturbation['note'] if perturbation else None,
            'llm_note': None,
        },
    }


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
    text = corrector.template(bad, good, required_label, bad_label)
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


class Handler(BaseHTTPRequestHandler):
    server_version = 'SynTutor/2.0'

    def log_message(self, fmt, *args):
        sys.stderr.write('[syntutor] %s - %s\n' % (self.address_string(), fmt % args))

    def _send(self, code, body, ctype='application/json'):
        data = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Access-Control-Allow-Origin', ALLOW_ORIGIN)
        self.send_header('Vary', 'Origin')
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', ALLOW_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', '0')
        self.send_header('Access-Control-Allow-Origin', ALLOW_ORIGIN)
        self.end_headers()

    def _json(self, code, payload):
        self._send(code, json.dumps(payload, ensure_ascii=False))

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html'):
            self._serve_file('index.html')
            return
        if path == '/api/health':
            status = _model_status()
            code = 200 if status['ready'] else 503
            self._json(code, {
                'status': 'ok' if status['ready'] else 'degraded',
                'ready': status['ready'],
                'models': {
                    'spacy_model': 'en_core_web_md',
                    'parser_model': 'benepar_en3',
                },
                'spacy_version': status.get('spacy'),
                'pipeline': status.get('pipeline'),
                'error': status.get('error'),
                'install_hint': ('python3 -m spacy download en_core_web_md && '
                                 "python3 -c \"import benepar; benepar.download('benepar_en3')\"")
                if not status['ready'] else None,
            })
            return
        self._serve_file(path.lstrip('/'))

    def _serve_file(self, rel):
        relpath = os.path.normpath(rel)
        top = relpath.split(os.sep)[0]
        if relpath.startswith('..') or os.path.isabs(relpath) or top not in PUBLIC_TOP:
            self._json(403, {'error': 'forbidden path'})
            return
        full = os.path.join(WEB_DIR, relpath)
        if not full.startswith(WEB_DIR) or not os.path.isfile(full):
            self._json(404, {'error': 'not found'})
            return
        ext = os.path.splitext(full)[1].lower()
        ctype = MIME.get(ext, 'application/octet-stream')
        with open(full, 'rb') as fh:
            self._send(200, fh.read(), ctype)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != '/api/parse':
            self._json(404, {'error': 'not found'})
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b'{}'
            data = json.loads(body.decode('utf-8'))
        except Exception as exc:  # noqa: BLE001
            self._json(400, {'error': f'invalid request payload: {exc}'})
            return
        text = (data.get('text') or '').strip()
        if not text:
            self._json(422, {'error': 'empty input', 'hint': 'Provide an English sentence in "text".'})
            return
        try:
            sentence_index = int(data.get('sentence_index', 0))
        except (TypeError, ValueError):
            self._json(400, {'error': 'sentence_index must be an integer'})
            return
        if sentence_index < 0:
            self._json(400, {'error': 'sentence_index must be >= 0'})
            return
        try:
            payload = build_payload(text, sentence_index=sentence_index)
        except ParseFailure as exc:
            self._json(422, {'error': str(exc), 'input': text})
            return
        except Exception as exc:  # model not available
            hint = _model_status().get('error') or (
                'Run:  pip install spacy benepar transformers==4.46.3  &&  python -m spacy download en_core_web_md  &&  python -m benepar.download benepar_en3'
            )
            self._json(503, {'error': str(exc), 'hint': hint})
            return
        self._json(200, payload)


def main():
    default_host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    host = os.environ.get('SYNTUTOR_HOST', default_host)
    server = ThreadingHTTPServer((host, PORT), Handler)
    print(f'SynTutor full-stack server on http://{host}:{PORT}')
    print('Endpoints: GET /  \u00b7 GET /api/health \u00b7 POST /api/parse')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nshutting down')


if __name__ == '__main__':
    main()