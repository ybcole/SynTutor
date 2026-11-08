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

🔗: https://syntutor.vercel.app

An explainable AI tutoring system for English phrase-structure syntax: parse a
sentence into a constituency tree and read deterministic, rule-based
explanations for every relationship (spaCy + benepar + rule-matrix XAI).

The [M6 canonical Builder](docs/reports/milestone-06-acceptance-2026-11-08.md) supports chapter conventions, constructed-tree evaluation, local drafts/undo and reviewed construction practice. Deploy the backend alongside the frontend; M6 needs no new database migration.

Independent Quizzes now include 16 five-question assessments with 120 original variants, versioned attempt history and best-score XP. See [M5 acceptance](docs/reports/milestone-05-acceptance-2026-11-08.md) and [account deployment steps](docs/assessments/progress-and-deployment.md).

Current project status: [M1–M3](docs/reports/milestones-01-03-acceptance-2026-11-08.md) and [M4 lessons acceptance](docs/reports/milestone-04-acceptance-2026-11-08.md). The Lessons area has 12 versioned source-reviewed units. Device-local progress is available; the owner reports M4/M5 Supabase migrations applied, with hosted sync still needing an account smoke test. Reviewed book evidence is separate from legacy diagnostic feedback; unsupported canonical analyses remain unresolved.

Run locally:

```
pip install -r requirements.txt
python -m spacy download en_core_web_md
python -c "import benepar; benepar.download('benepar_en3')"
python3 server/webapp.py     # Flask backend: serves the front end + /api
```

(The stdlib `http.server` variant is still available as `python3 server/app.py`.)

## Project navigation

- [Repository layout](docs/repository-layout.md)
- [Milestones 01–03 verification](docs/reports/milestones-01-03-audit.md)
- [Authoritative execution plan](docs/planning/syntutor_12_prompt_execution_plan.md) and [checklist](docs/planning/master_checklist.md)
- [Developer documentation](docs/README.md)
- [Research drafts](docs/research/)

The active browser application is in `web/`. Historical root-level browser files
are preserved in `archive/legacy-web/`; they are not a second application entry point.

Current fixes and remaining content gates: [M2–M3 remediation](docs/reports/milestones-02-03-remediation.md).
