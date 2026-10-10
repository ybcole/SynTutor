---
title: SynTutor API
emoji: 🌳
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 5.49.0
python_version: '3.12'
app_file: server/hf_space.py
pinned: false
---

# SynTutor API

Deterministic English phrase-structure parsing API (spaCy + benepar + rule-matrix XAI).

Live:

- **Web app (Vercel):** https://syntutor.vercel.app
- **API (this Space):** https://ybcole-syntutor.hf.space

Endpoints:

- `GET  /api/health` — model/pipeline availability
- `POST /api/parse` — `{ "text": "..." }` → JSON tree + node descriptions

Run locally:

```
pip install -r requirements.txt
python -m spacy download en_core_web_md
python -c "import benepar; benepar.download('benepar_en3')"
python3 server/app.py
```
