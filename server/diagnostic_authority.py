"""Final learner-facing diagnostic reconciliation for SynTutor.

The legacy rule matrix and optional CoLA detector produce *signals*, not a
certification of English grammaticality. This module translates those signals
into an explicit, coverage-aware assessment without suppressing local errors.

Kept dependency-free so it can be tested without loading NLP models.
"""


def reconcile_summary(summary, canonical_status=None):
    """Return a reconciled copy of a legacy API summary.

    ``verdict`` and ``valid`` are retained for compatibility with existing
    clients. New clients should prefer ``diagnostic_assessment.status``;
    a legacy ``grammatical`` verdict means only *no supported error detected*.
    """
    result = dict(summary)
    verdict = result.get('verdict')
    rules = list(result.get('constraints_fired') or [])
    detector = result.get('detector')
    signal = 'unavailable'
    if isinstance(detector, dict) and detector.get('available') is True:
        signal = 'accepts' if detector.get('acceptable') is True else (
            'rejects' if detector.get('acceptable') is False else 'unavailable')

    if verdict == 'ungrammatical' and (rules or result.get('violations')):
        status = 'rule_reported_violation'
        # Preserve the source-linked local diagnostic, even if the model
        # disagrees. It is a *reported* violation, not independent proof.
    elif verdict == 'grammatical' and not rules and not result.get('violations'):
        status = 'no_supported_error'
        result['explanation'] = (
            'No supported grammatical violation was detected by the current '
            'rules. This does not independently verify that the sentence is '
            'grammatically correct.')
        if canonical_status not in (None, 'normalized'):
            result['explanation'] += ' The canonical syntax analysis is unresolved.'
    else:
        status = 'unverified'
        # Fail closed on contradictory or unknown legacy states.
        result['verdict'] = 'unverified'
        result['explanation'] = (
            'SynTutor cannot verify this sentence. The available rules did not '
            'establish a supported grammatical violation.')
        if signal == 'rejects':
            result['explanation'] += (
                ' The acceptability model flagged the sentence, but this '
                'signal alone cannot establish a grammatical error.')
        if result.get('unverified') or result.get('checker_errors'):
            result['explanation'] += ' Some lexical or grammatical checks remain unresolved.'
        if canonical_status not in (None, 'normalized'):
            result['explanation'] += ' The canonical syntax analysis is unresolved.'

    result['diagnostic_assessment'] = {
        'status': status,
        'source': 'legacy_rule_matrix',
        'rule_ids': rules,
        'independently_verified': False,
        'canonical_status': canonical_status,
        'acceptability_signal': signal,
        'model_disagreement': signal == 'rejects' and not rules,
    }
    # A canonical tree or CoLA score must never certify a diagnostic.
    result['book_verified'] = False
    return result
