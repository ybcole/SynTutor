"""Hugging Face Spaces entrypoint (Gradio SDK, ZeroGPU).

SynTutor is a CPU-only NLP backend (spaCy + benepar + rule-matrix XAI). A free
Hugging Face account can only host Gradio Spaces on ZeroGPU, which refuses to
boot unless a launched Gradio app registers at least one ``@spaces.GPU``
function. So we launch a minimal Gradio app, bind a no-op ``@spaces.GPU``
function to a (hidden) event handler to satisfy that check, and attach the real
SynTutor HTTP API to the same FastAPI app Gradio launches. No GPU work is ever
requested, so no ZeroGPU quota is burned.

The real server logic lives in server/app.py and is reused unchanged; the local
``python3 server/app.py`` entrypoint still works for development.
"""

import os

# SSR must be off for a custom/mounted route to be served reliably on HF.
os.environ['GRADIO_SSR_MODE'] = 'false'

import importlib.util
import sys
import threading
import time

import spaces  # noqa: E402,F401  (must precede any torch-importing module)
import gradio as gr  # noqa: E402
from fastapi import Request  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from starlette.responses import Response  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(ROOT, 'server')
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

_spec = importlib.util.spec_from_file_location(
    'syntutor_server', os.path.join(SERVER_DIR, 'app.py')
)
_server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_server)

CORS = {'Access-Control-Allow-Origin': '*'}


# ---------------------------------------------------------------------------
# ZeroGPU placeholder: satisfies the startup scan, never invoked.
# ---------------------------------------------------------------------------
@spaces.GPU(duration=1)
def _zerogpu_noop(value: str = 'ok') -> str:
    """No-op kept only so ZeroGPU's startup scan finds a decorated handler."""
    return value


def _warm_models():
    import parse_engine
    try:
        parse_engine.load_models()
        print('[syntutor] models ready', flush=True)
        return
    except Exception:
        pass
    try:
        parse_engine._load_error = None
        import spacy.cli
        spacy.cli.download('en_core_web_md')
        import benepar
        benepar.download('benepar_en3')
    except Exception as exc:  # noqa: BLE001
        print(f'[syntutor] model download failed: {exc}', flush=True)
    try:
        parse_engine.load_models()
        print('[syntutor] models ready after download', flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f'[syntutor] model load failed: {exc}', flush=True)


threading.Thread(target=_warm_models, daemon=True).start()


with gr.Blocks(title='SynTutor API') as demo:
    gr.Markdown(
        '# SynTutor API\n\n'
        'Deterministic English parse backend (spaCy + benepar + rule matrix).\n\n'
        '- `GET /api/health`\n'
        '- `POST /api/parse` with `{"text": "..."}`\n'
    )
    _probe_in = gr.Textbox(value='ok', visible=False)
    _probe_out = gr.Textbox(visible=False)
    _probe_btn = gr.Button(visible=False)
    _probe_btn.click(fn=_zerogpu_noop, inputs=_probe_in, outputs=_probe_out)


# ---------------------------------------------------------------------------
# Custom API routes, attached to the FastAPI app Gradio launches.
# ---------------------------------------------------------------------------
def _health_payload():
    status = _server._model_status()
    return 200 if status['ready'] else 503, {
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
    }


async def api_health(request: Request):
    code, payload = _health_payload()
    return JSONResponse(payload, status_code=code, headers=CORS)


async def api_parse(request: Request):
    try:
        data = await request.json()
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({'error': f'invalid request payload: {exc}'},
                            status_code=400, headers=CORS)
    text = (data.get('text') or '').strip()
    if not text:
        return JSONResponse({'error': 'empty input',
                             'hint': 'Provide an English sentence in "text".'},
                            status_code=422, headers=CORS)
    try:
        sentence_index = int(data.get('sentence_index', 0))
    except (TypeError, ValueError):
        return JSONResponse({'error': 'sentence_index must be an integer'},
                            status_code=400, headers=CORS)
    if sentence_index < 0:
        return JSONResponse({'error': 'sentence_index must be >= 0'},
                            status_code=400, headers=CORS)
    try:
        payload = _server.build_payload(text, sentence_index=sentence_index)
    except _server.ParseFailure as exc:
        return JSONResponse({'error': str(exc), 'input': text},
                            status_code=422, headers=CORS)
    except Exception as exc:  # noqa: BLE001  (model not available yet)
        hint = _server._model_status().get('error') or (
            'Models may still be downloading; retry shortly.')
        return JSONResponse({'error': str(exc), 'hint': hint},
                            status_code=503, headers=CORS)
    return JSONResponse(payload, status_code=200, headers=CORS)


async def api_options(request: Request):
    return Response(status_code=204, headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
    })


def _mount(app, path, endpoint, methods):
    app.add_api_route(path, endpoint, methods=methods)
    app.router.routes.insert(0, app.router.routes.pop())


def main():
    port = int(os.environ.get('PORT') or os.environ.get('GRADIO_SERVER_PORT') or '7860')
    app, _local_url, _share_url = demo.launch(
        server_name='0.0.0.0',
        server_port=port,
        prevent_thread_lock=True,
        quiet=True,
    )
    _mount(app, '/api/health', api_health, ['GET', 'HEAD'])
    _mount(app, '/api/parse', api_parse, ['POST'])
    _mount(app, '/api/health', api_options, ['OPTIONS'])
    _mount(app, '/api/parse', api_options, ['OPTIONS'])
    print(f'[syntutor] serving on http://0.0.0.0:{port}', flush=True)
    while True:
        time.sleep(3600)


main()
