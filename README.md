---
title: SynTutor
emoji: 🌳
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 5.49.0
python_version: '3.12'
app_file: server/hf_space.py
pinned: false
---

# SynTutor

An explainable AI tutoring system for English phrase-structure syntax: parse a
sentence into a constituency tree and read deterministic, rule-based
explanations for every relationship (spaCy + benepar + rule-matrix XAI).

**App:** https://syntutor.vercel.app

This Space is only the parsing backend that the app calls; it is not a public
API product. See `docs/ARCHITECTURE.md` for the full system.

Run locally:

```
pip install -r requirements.txt
python -m spacy download en_core_web_md
python -c "import benepar; benepar.download('benepar_en3')"
python3 server/app.py
```
