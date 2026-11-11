# SynTutor — Independent System-Wide V&V Baseline

## Scope
Independent verification of existing SynTutor test suites.
This baseline does not certify complete system correctness.

## Environment
- OS: Linux Mint
- Python: 3.12.3
- Node.js: 24.22.0
- Repository: SynTutor-qa
- Branch: qa/friday-validation
- Python environment: ../SynTutor/.venv
- Node dependencies: installed using npm ci

## Independently reproduced results

| Area | Result |
|---|---|
| Backend API/transport contracts | 34/34 passed |
| Real-parser integration | 9/9 passed |
| Tree Builder core | Passed |
| Lessons and database tests | Passed |
| Assessments and database tests | Passed |
| Syntax-tree quiz content audit | Passed |
| Explanation evidence contracts | Passed |
| Correction module | Passed |
| Independent targeted QA | 31 passed, 16 failed |

## Evidence limitations

- Passing tests establish only their asserted behavior.
- Many API contract tests use mocked components.
- Parser-backed tests exercise real models but mock
  selected classification and correction components.
- Existing Node.js scripts do not all report test counts.
- Local versions differ from GitHub Actions versions.
- Hosted account synchronization remains unverified.
- Source-extraction coverage is not software test coverage.
- Linguistic validity requires independently reviewed labels.
- Security, accessibility, and performance require separate tests.

## Next engineering priorities

1. Create a feature-to-test traceability matrix.
2. Independently verify end-to-end learner workflows.
3. Establish reproducible full-pipeline grammar/XAI tests.
4. Validate authentication, authorization, and persistence.
5. Assess accessibility, security, and performance.
6. Integrate independently verified regressions into CI.
7. Produce versioned, reproducible quality reports.

## Conclusion

The existing test infrastructure is substantial.
Independent evaluation has identified targeted failures
not resolved by successful baseline test execution.

Further work must prioritize unverified behavior and
measurable risk reduction rather than duplicate tests.
