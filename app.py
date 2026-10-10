"""Hugging Face Spaces entrypoint (Gradio SDK, custom HTTP server).

HF runs this file directly; we start the SynTutor API on port 7860 and warm the
NLP models in the background so the first request is fast. The real server lives
in server/app.py and is reused unchanged.
"""

import importlib.util
import os
import sys
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(ROOT, 'server')

os.environ.setdefault('SYNTUTOR_HOST', '0.0.0.0')
os.environ['SYNTUTOR_PORT'] = os.environ.get('PORT', '7860')

if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

_spec = importlib.util.spec_from_file_location(
    'syntutor_server', os.path.join(SERVER_DIR, 'app.py')
)
_server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_server)

# ZeroGPU Spaces refuse to boot unless at least one @spaces.GPU function is
# declared. SynTutor is CPU-only, so this placeholder just satisfies the
# runtime check and is never called.
try:
    import spaces

    @spaces.GPU
    def _zerogpu_placeholder(value: int = 0) -> int:
        return value
except Exception:  # not on ZeroGPU (e.g. local dev) -- ignore
    pass


def _warm_models():
    import parse_engine
    try:
        parse_engine.load_models()
        print('[syntutor] models ready', flush=True)
        return
    except Exception:
        parse_engine._load_error = None
    try:
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

_server.main()
