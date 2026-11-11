# SynTutor — Independent V&V Traceability Matrix

Status: Initial evidence-based inventory; not a coverage certification.

| ID | Requirement area | Existing test evidence | Independent result | Remaining verification |
|---|---|---|---|---|
| V01 | API validation and transport | API, Flask and stdlib contract tests | 34 passed | Real request-path coverage |
| V02 | Parsing and canonical syntax trees | Parser runtime tests | 9 passed | Independently reviewed tree accuracy |
| V03 | Grammar detection and XAI | Backend tests and Friday QA | 31/47 targeted QA checks passed | Real end-to-end diagnostic consistency |
| V04 | Suggested corrections | JS correction and backend tests | Existing JS test passed | Meaning-preserving, independently valid repairs |
| V05 | Lessons | Core, database and browser tests | Passed locally | Educational validity and hosted synchronization |
| V06 | Quizzes and assessments | Core, database and browser tests | Passed locally | Independent question-answer validation |
| V07 | Tree Builder | Core and browser tests | Passed locally | Broader constructions and accessibility |
| V08 | Accounts and persistence | Browser/database test scripts | Not run locally | Real authentication and account isolation |
| V09 | Security | Selected database authorization tests | Partial local evidence | Broader application security assessment |
| V10 | Accessibility | Selected browser interaction checks | Not independently audited | Keyboard, screen reader and WCAG assessment |
| V11 | Performance and reliability | Existing runtime checks | Not benchmarked locally | Latency, concurrency and resource measurements |
| V12 | CI and deployment | Two GitHub Actions workflows | Recent successful PR runs observed | Regression coverage and deployment verification |

## Evidence rules

- A passing test verifies only its stated assertions.
- Mocked and real integrations must be distinguished.
- A missing test does not establish a product defect.
- Findings require reproducible evidence and independent review.
- Coverage claims require explicit denominators and methodology.
