#!/usr/bin/env python3
"""Offline CI gate for the deterministic rule matrix and correction assembler.

No HTTP server: this catches regressions before deployment.

Checks
  1. every GOLD sentence gets its expected verdict and no checker crash;
  2. every ungrammatical item in scripts/basic_errors.BATTERY is caught;
  3. every control in that battery is accepted;
  4. every assembled correction is itself grammatical, and reports the ones
     that differ from the hand-written control (informational, never a fail).
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from audit_rules import GOLD  # noqa: E402
from basic_errors import BATTERY  # noqa: E402
from server.corrections import assemble, has_actionable  # noqa: E402
from server.matrix import evaluate  # noqa: E402
from server.parse_engine import analyze  # noqa: E402


def judge(text):
    analysis = analyze(text, sentence_index=0)
    result = evaluate(analysis['root'], text=analysis['sentence'])
    return analysis, result['details'], result['summary']


def validate(text):
    try:
        _, details, summary = judge(text)
    except Exception:  # noqa: BLE001
        return False
    if summary.get('verdict') != 'grammatical' or summary.get('checker_errors'):
        return False
    return not any(d.get('status') == 'error' for d in details.values())


def norm(text):
    text = text.lower().strip()
    text = re.sub(r'[.!?]+$', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def main() -> int:
    failures = []
    warnings = []

    print(f'GOLD: {len(GOLD)} sentences')
    for text, expected, why in GOLD:
        _, _, summary = judge(text)
        verdict = summary.get('verdict')
        want = 'grammatical' if expected else 'ungrammatical'
        if verdict != want or summary.get('checker_errors'):
            failures.append(
                f'GOLD {text!r}: expected {want}, got {verdict} '
                f'({why}) checker_errors={summary.get("checker_errors")}')

    print(f'BATTERY: {len(BATTERY)} pairs')
    skipped = 0
    corrected = 0
    differing = []
    missing = []
    for wrong, control, category in BATTERY:
        if wrong == control:
            skipped += 1
            continue
        analysis, details, summary = judge(wrong)
        if summary.get('verdict') != 'ungrammatical' or summary.get('checker_errors'):
            failures.append(
                f'BATTERY miss [{category}] {wrong!r}: '
                f'verdict={summary.get("verdict")} '
                f'checker_errors={summary.get("checker_errors")}')
        control_analysis, control_details, control_summary = judge(control)
        if (control_summary.get('verdict') != 'grammatical'
                or control_summary.get('checker_errors')):
            failures.append(
                f'CONTROL fail [{category}] {control!r}: '
                f'verdict={control_summary.get("verdict")} '
                f'checker_errors={control_summary.get("checker_errors")}')

        result = None
        if summary.get('verdict') != 'grammatical' or has_actionable(details):
            result = assemble(analysis['sentence'], details,
                              analysis['tokens'], validate=validate)
        if result is None:
            missing.append((category, wrong, control))
            continue
        corrected += 1
        fixed = result['corrected_sentence']
        if norm(fixed) != norm(control):
            differing.append((category, wrong, control, fixed))

    print(f'  corrections assembled: {corrected}')
    print(f'  no correction:         {len(missing)}')
    print(f'  differs from control:  {len(differing)}')
    if skipped:
        print(f'  skipped (control listed as error): {skipped}')

    if differing:
        print('\n-- corrections that differ from the hand-written control --')
        for category, wrong, control, fixed in differing:
            print(f'  [{category}]')
            print(f'    input:   {wrong}')
            print(f'    control: {control}')
            print(f'    output:  {fixed}')
    if missing:
        print('\n-- battery items with no validated correction --')
        for category, wrong, _control in missing:
            print(f'  [{category}] {wrong}')

    kinds = Counter()
    for category, wrong, _control in missing:
        kinds[category] += 1
    if kinds:
        print('\n  missing by category:')
        for name, count in kinds.most_common():
            print(f'    {count:2d}  {name}')

    if failures:
        print(f'\nFAILED: {len(failures)} problem(s)')
        for failure in failures:
            print(f'  {failure}')
        return 1
    print('\nOK: gold verdicts, battery detections, controls, and corrections')
    return 0


if __name__ == '__main__':
    sys.exit(main())
