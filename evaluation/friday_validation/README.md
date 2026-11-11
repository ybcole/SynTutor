# SynTutor — Independent Verification and Validation

## Purpose

This directory contains independent QA evidence for SynTutor.

The evaluation covers grammar analysis, diagnostic authority,
HTTP behavior, learner-facing explanations, accessibility,
and selected frontend workflows.

Passing technical tests do not establish grammatical accuracy,
educational effectiveness, security, or WCAG compliance.

## Main documents

- findings.md — documented defects and supporting evidence
- traceability_matrix.md — verification coverage and gaps
- generator_authority_regression.md — NLP and browser findings
- axe_audit.json — automated accessibility results
- axe_incomplete_review.json — checks requiring manual review

## Automated regression tests

### Grammar authority contract

PYTHONPATH=server ../SynTutor/.venv/bin/python \
  -m unittest -v \
  evaluation/friday_validation/test_generator_authority_contract.py

Observed baseline: 2 passed, 2 failed.

### Real HTTP contract

PYTHONPATH=server ../SynTutor/.venv/bin/python \
  -m unittest -v \
  evaluation/friday_validation/test_generator_http.py

Observed baseline: 3 passed, 1 failed.

### Learner-facing browser authority

python evaluation/friday_validation/test_generator_browser_authority.py

Observed baseline: PASS.

### Quiz accessible names

python evaluation/friday_validation/test_quiz_accessible_names.py

Observed baseline: 16 of 16 assessment launch buttons
missing assessment-specific accessible names.
Expected exit status: 1 until QA-012 is corrected.

## Environment

Original evaluation environment:
- Linux Mint, x86-64
- Python virtual environment with Playwright
- Playwright Chromium
- Separate SynTutor checkout and NLP virtual environment

The browser authority test currently assumes a sibling
SynTutor directory containing .venv/bin/python.
Adjust this path before running in another environment.

## Accessibility limitations

axe-core 4.10.3 reported zero automatically detected
WCAG A/AA violations in four tested desktop workspaces.

Color-contrast evaluation was incomplete for some elements.
Manual checks remain necessary.

Keyboard navigation was partially verified.
Full screen-reader, focus-management, and mobile
accessibility audits remain outstanding.

## Regression policy

Known failing tests document existing production issues.
They must not be represented as passing.

Do not add these tests as mandatory passing CI gates until
their underlying issues are resolved or explicitly handled.

## Production ownership

This directory contains independent evaluation artifacts.
It does not implement fixes in SynTutor's production code.
