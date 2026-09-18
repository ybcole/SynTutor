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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from parse_engine import ParseFailure, analyze, load_models
from matrix import evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('SYNTUTOR_PORT', '8000'))

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


def build_payload(text, sentence_index=0):
    """Deterministic full payload for one user input, targeting ``sentence_index``."""
    analysis = analyze(text, sentence_index=sentence_index)
    result = evaluate(analysis['root'])
    details = result['details']
    summary = result['summary']
    root = analysis['root']
    tokens = analysis['tokens']

    token_line = ' \u00b7 '.join(f"{t['t']}/{t['pos']}" for t in tokens)
    tag_word = summary['explanation']
    label = 'VALID' if summary['valid'] else 'INVALID'

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

    error_ids = [d for d in details.values() if d['status'] == 'error']
    contrastive = _contrastive(summary, details)

    return {
        'meta': {
            'deterministic': True,
            'k': 1,
            'parser': 'benepar_en3',
            'spacy': 'en_core_web_md',
            'backend': 'spaCy + benepar (neural constituency) + rule matrix (XAI)',
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
            'perturbation': None,
            'llm_note': None,
        },
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
    }
    repair = breaks.get(first['constraint'], f'satisfying {first["constraint"]}')
    return (f"Contrastive candidate: the edge '{first['id']}' violates {first['constraint']}; "
            f"the sentence would be licensed after {repair}.")


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
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()

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
        full = os.path.join(ROOT, relpath)
        if not full.startswith(ROOT) or not os.path.isfile(full):
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
                'Run:  pip install spacy benepar transformers<4.47  &&  python -m spacy download en_core_web_md  &&  python -m benepar.download benepar_en3'
            )
            self._json(503, {'error': str(exc), 'hint': hint})
            return
        self._json(200, payload)


def main():
    host = os.environ.get('SYNTUTOR_HOST', '127.0.0.1')
    server = ThreadingHTTPServer((host, PORT), Handler)
    print(f'SynTutor full-stack server on http://{host}:{PORT}')
    print('Endpoints: GET /  \u00b7 GET /api/health \u00b7 POST /api/parse')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nshutting down')


if __name__ == '__main__':
    main()