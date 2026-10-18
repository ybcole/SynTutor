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

from parse_engine import ParseFailure
from api import build_payload, model_status as _model_status, word_info

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT, 'web')
PORT = int(os.environ.get('PORT') or os.environ.get('SYNTUTOR_PORT') or '8000')

# CORS: the frontend may be hosted on a different origin (e.g. Vercel) than this
# API. Restrict with SYNTUTOR_ALLOW_ORIGIN (default '*' for easy setup).
ALLOW_ORIGIN = os.environ.get('SYNTUTOR_ALLOW_ORIGIN', '*')

# Only these top-level frontend entries may be served statically. Anything else
# under ROOT (server/, supabase/, scripts/, migrations, config) stays private.
PUBLIC_TOP = {'index.html', 'login.html', 'css', 'js', 'content'}

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
        if path not in ('/api/parse', '/api/words'):
            self._json(404, {'error': 'not found'})
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b'{}'
            data = json.loads(body.decode('utf-8'))
        except Exception as exc:  # noqa: BLE001
            self._json(400, {'error': f'invalid request payload: {exc}'})
            return

        if path == '/api/words':
            raw = data.get('words')
            if isinstance(raw, str):
                raw = raw.split()
            if not isinstance(raw, list):
                self._json(422, {'error': 'provide "words" as a list'})
                return
            self._json(200, {'results': word_info(raw[:100])})
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