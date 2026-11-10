# CGEL Phase A: operational commands

Phase A baseline checks:

    python tools/migrate_diagnostics.py --check
    python tools/validate_cgel_rules.py
    python tools/ledger.py check --allow-unprocessed
    python -m unittest -v tools.test_cgel_infrastructure

The coverage completion check, python tools/ledger.py check, intentionally fails while any page is unprocessed. Use python tools/ledger.py report to report status. Chapter-specific strict gate: python tools/ledger.py check --chapter 3. Mark verified pages with existing supporting report: python tools/ledger.py mark --chapter 3 --pages 74-75 --status extracted --evidence sources/cambridge/chapter_03/CHAPTER_03_REPORT.md. An existing report alone is not proof of comprehensive coverage.

Approval: python tools/bulk_owner_approve.py --chapter 3 is a dry run; --apply changes eligible NEEDS_REVIEW rules only after source-page and exception checks, strict ledger validation, machine-readable diagnostic validation, XAI-PRE contracts, basic errors, coverage corpus and evaluator, and the server tests pass. It does NOT enable new Cambridge rules in the runtime allow-list. Do not fabricate source reviews or mark unfinished pages extracted. Existing protocol 1.0 rules carry diagnostic:null. New protocol 1.1 constraints require a complete diagnostic. All content remains in English; textbook passages/PDFs must not be committed.
