# Generator Diagnostic Authority — Independent Regression

Date: 2026-11-11
Branch: qa/friday-validation
Environment: Linux Mint; Python 3.12.3; real NLP pipeline

## Reproduction

Command:

PYTHONPATH=server ../SynTutor/.venv/bin/python -m unittest -v evaluation/friday_validation/test_generator_authority_contract.py

Result: 4 tests executed; 2 passed; 2 failed.

## Failed assertions

### R01 — Incorrect modal-form explanation

Input: Can she swims?

Observed: The legacy explanation describes two full clauses joined
without punctuation or a conjunction.

Expected: Identify the invalid inflected verb following the modal.

Existing finding: QA-009.
Assessment: Confirmed linguistic diagnostic defect.

### R02 — Unsupported categorical assurance

Input: The birds sing.

Observed: The legacy explanation categorically declares grammatical
correctness, while book_verified is false and XAI reports
whole_sentence_certified=false with status NOT_EVALUATED.

Existing related finding: QA-003.
Assessment: Diagnostic authority contract concern.

Qualification: Missing XAI certification alone does not disprove
the legacy matrix result. The test's assurance requirement must be
reviewed against an explicit, agreed diagnostic authority contract.

## Passed assertions

- These book are heavy. produces These books are heavy.
- A normalized Burton-Roberts tree remains distinct from XAI
  whole-sentence certification.

## Limitations

These are four targeted assertions over three sentences.
They do not establish overall grammatical accuracy, recall,
precision, correction validity, or learner outcomes.

The two failing tests are known regression checks, not suitable
as mandatory passing CI gates until the defects and contracts
are addressed.

## Real browser investigation — 2026-11-11

Input: Can she swims?

Environment: Actual Flask server and Chromium, with external
authentication dependencies stubbed.

Observed:
- POST /api/parse returned HTTP 200.
- Legacy diagnostic incorrectly described a run-on sentence.
- Burton-Roberts analysis status was normalized.
- Incorrect run-on advice was not immediately visible.
- Selecting the canonical word node "swims" triggered
  POST /api/explain, returning HTTP 200.
- The learner-facing explanation was:
  "swims" is the verb in "swims". It expresses the action,
  event or state described there.
- The incorrect run-on advice was not displayed in that pane.
- The raw parser canvas remained hidden.

Assessment:
- QA-009 is confirmed in the internal pipeline and HTTP API.
- The tested frontend explanation route did not promote the
  incorrect legacy diagnosis.
- The generic word explanation does not teach the modal
  verb-form restriction, reinforcing QA-001.
- Other frontend interactions remain untested.

Next requirement:
Provide an evidence-grounded explanation of the relevant
grammatical relationship when supported. Otherwise communicate
the limits of available diagnostic evidence without making
unsupported grammatical claims.
