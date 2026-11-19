"""Serve SynTutor's Flask API as a single Vercel Python function."""

import os
from pathlib import Path
import sys
from threading import Lock
from urllib.parse import parse_qs


ROOT = Path(__file__).resolve().parents[1]
models = ROOT / 'vercel_models'
if models.is_dir():
    os.environ['NLTK_DATA'] = str(models / 'nltk')
    os.environ['HF_HUB_CACHE'] = str(models / 'hub')
    os.environ['HF_HUB_OFFLINE'] = '1'
os.environ.setdefault('OMP_NUM_THREADS', '1')

sys.path.insert(0, str(ROOT / 'server'))
from webapp import app  # noqa: E402


API_PATHS = frozenset(
    f'/api/{endpoint}'
    for endpoint in ('health', 'parse', 'words', 'evaluate', 'explain', 'repair-check')
)
flask_wsgi = app.wsgi_app
inference_lock = Lock()


def api_wsgi(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path == '/api/nlp':
        route = parse_qs(environ.get('QUERY_STRING', '')).get('__syntutor_route', [''])[0]
        path = f'/api/{route}'
    if path not in API_PATHS:
        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return [b'{"error":"not found"}']
    environ['PATH_INFO'] = path
    # Share one set of model weights and bound inference memory per instance.
    with inference_lock:
        return flask_wsgi(environ, start_response)


app.wsgi_app = api_wsgi
