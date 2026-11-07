"""ASGI explanation transport, importable without starting a hosted Gradio app."""
import json
from starlette.responses import JSONResponse
from explanations import explain_request

CORS = {'Access-Control-Allow-Origin': '*'}


async def api_explain(request):
    try:
        raw = await request.body()
        if len(raw) > 250_000:
            return JSONResponse({'error': 'request exceeds 250000 bytes'}, status_code=413, headers=CORS)
        return JSONResponse(explain_request(json.loads(raw)), headers=CORS)
    except (ValueError, RecursionError) as exc:
        return JSONResponse({'error': str(exc)}, status_code=400, headers=CORS)
