"""SynTutor backend (Flask): serves the front end and the analysis API.

This replaces the stdlib ``http.server`` in ``app.py`` as the default entry
point. It sends the HTML, JavaScript and CSS from ``web/`` and exposes the same
JSON endpoints (``/api/health`` and ``/api/parse``). All analysis logic lives in
``api.py`` so this file is purely transport.

Run:  python3 server/webapp.py         (then open http://127.0.0.1:8000)
Endpoints:
    GET  /                  static front end (index.html, css, js, content)
    GET  /api/health        model/pipeline availability
    POST /api/parse         {text} -> JSON payload (tree + node descriptions)
"""

import os

from flask import Flask, Response, jsonify, request, send_from_directory

from api import ParseFailure, build_payload, health_payload, word_info

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT, 'web')
PORT = int(os.environ.get('PORT') or os.environ.get('SYNTUTOR_PORT') or '8000')
HOST = os.environ.get('SYNTUTOR_HOST') or ('0.0.0.0' if os.environ.get('PORT') else '127.0.0.1')

# CORS: the frontend may be hosted on a different origin (e.g. Vercel) than this
# API. Restrict with SYNTUTOR_ALLOW_ORIGIN (default '*' for easy setup).
ALLOW_ORIGIN = os.environ.get('SYNTUTOR_ALLOW_ORIGIN', '*')

# Only these top-level frontend entries may be served statically. Anything else
# under ROOT (server/, supabase/, scripts/, migrations, config) stays private.
PUBLIC_TOP = {'index.html', 'login.html', 'css', 'js', 'content'}

MIME = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.ico': 'image/x-icon',
    '.md': 'text/markdown',
}

app = Flask(__name__, static_folder=None)


@app.after_request
def _add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = ALLOW_ORIGIN
    resp.headers['Vary'] = 'Origin'
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory(WEB_DIR, 'index.html', mimetype=MIME['.html'])


@app.route('/api/health')
def health():
    payload = health_payload()
    return jsonify(payload), (200 if payload['ready'] else 503)


@app.route('/api/parse', methods=['POST'])
def parse():
    raw = request.get_data()
    data = request.get_json(silent=True)
    if data is None and raw:
        return jsonify({'error': 'invalid request payload'}), 400
    data = data or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'empty input',
                        'hint': 'Provide an English sentence in "text".'}), 422
    try:
        sentence_index = int(data.get('sentence_index', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'sentence_index must be an integer'}), 400
    if sentence_index < 0:
        return jsonify({'error': 'sentence_index must be >= 0'}), 400

    try:
        payload = build_payload(text, sentence_index=sentence_index)
    except ParseFailure as exc:
        return jsonify({'error': str(exc), 'input': text}), 422
    except Exception as exc:  # noqa: BLE001 - model/back-end unavailable
        hint = (health_payload().get('error') or
                'Run:  pip install spacy benepar transformers==4.46.3  &&  '
                'python -m spacy download en_core_web_md  &&  '
                'python -m benepar.download benepar_en3')
        return jsonify({'error': str(exc), 'hint': hint}), 503
    return jsonify(payload)


@app.route('/api/words', methods=['POST', 'OPTIONS'])
def words():
    if request.method == 'OPTIONS':
        return Response(status=204, headers={
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
    data = request.get_json(silent=True)
    if data is None and request.get_data():
        return jsonify({'error': 'invalid request payload'}), 400
    data = data or {}
    raw = data.get('words')
    if isinstance(raw, str):
        raw = raw.split()
    if not isinstance(raw, list):
        return jsonify({'error': 'provide "words" as a list'}), 422
    return jsonify({'results': word_info(raw[:100])})


@app.route('/api/<path:sub>', methods=['GET', 'POST', 'OPTIONS'])
def api_not_found(sub):  # noqa: ARG001
    if request.method == 'OPTIONS':
        return Response(status=204, headers={
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400',
        })
    return jsonify({'error': 'not found'}), 404


@app.route('/<path:path>')
def static_files(path):
    # Mirror app.py exactly: only PUBLIC_TOP entries are servable.
    parts = os.path.normpath(path).split(os.sep)
    if parts and '..' in parts:
        return jsonify({'error': 'forbidden path'}), 403
    top = parts[0]
    if top not in PUBLIC_TOP:
        return jsonify({'error': 'forbidden path'}), 403
    if not os.path.isfile(os.path.join(WEB_DIR, path)):
        return jsonify({'error': 'not found'}), 404
    mimetype = MIME.get(os.path.splitext(path)[1].lower(), 'application/octet-stream')
    return send_from_directory(WEB_DIR, path, mimetype=mimetype, max_age=0)


@app.route('/<path:path>', methods=['OPTIONS'])
def options(path):  # noqa: ARG001
    return Response(status=204, headers={
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
    })


def main():
    print(f'SynTutor Flask backend on http://{HOST}:{PORT}')
    print('Endpoints: GET /  \u00b7 GET /api/health \u00b7 POST /api/parse')
    app.run(host=HOST, port=PORT, threaded=True, debug=False)


if __name__ == '__main__':
    main()
