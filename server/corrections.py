"""Deterministic correction assembly for SynTutor.

Rule findings carry pedagogical prose.  This module turns the *structured*
edits attached to a remediation (preferred) and a conservative set of prose
patterns (fallback) into one candidate sentence, then validates that candidate
through the same rule matrix before exposing it to the UI.

The contract is deliberately strict: a suggestion is only returned when the
corrected sentence is confirmed grammatical.  A missing correction is better
than a confident wrong one.
"""

from __future__ import annotations

import itertools
import re

_CHANGE = re.compile(
    r"(?:change|replace)\s+'([^']+)'\s+(?:to|with)\s+'([^']+)'", re.I)
_WRITE_NOT = re.compile(
    r"(?:write|use)\s+'([^']+)'\s*,?\s+not\s+'([^']+)'", re.I)
_SHOULD_BE = re.compile(
    r"should\s+be\s+'([^']+)'\s*,?\s+not\s+'([^']+)'", re.I)
_ARROW = re.compile(r"'([^']+)'\s*(?:→|->)\s*'([^']+)'")
_ADD_BEFORE = re.compile(
    r"add\s+'([^']+)'\s+before\s+'([^']+)'", re.I)
_REMOVE = re.compile(r"(?:remove|drop)\s+'([^']+)'", re.I)
_WRITE_INSTEAD = re.compile(
    r"(?:write|use|say)\s+'([^']+)'\s+instead\s+of\s+'([^']+)'", re.I)
_SAY_INSTEAD = re.compile(r"say\s+'([^']+)'\s+instead", re.I)
_WRITE_ONLY = re.compile(
    r"\b(?:write|use)\s+'([^']+)'(?!\s*(?:instead|before|after|to|with|not))",
    re.I)
_USE_INSTEAD_SIMPLE = re.compile(
    r"\b(?:write|use|say)\s+'([^']+)'\s+instead\b(?!\s+of)", re.I)
_MUST_BE = re.compile(r"must be '([^']+)', not '([^']+)'", re.I)
_CHANGE_IT = re.compile(r"change it to '([^']+)'", re.I)


def _token_map(tokens):
    return {t.get('i'): t for t in tokens if t.get('i') is not None
            and isinstance(t.get('start'), int) and isinstance(t.get('end'), int)}


def _span_for(details, node_id, token_map):
    detail = details.get(node_id)
    if not detail:
        return None
    span = detail.get('span') or []
    if len(span) != 2:
        return None
    first, last = span
    start_tok = token_map.get(first)
    end_tok = token_map.get(last - 1)
    if start_tok is None or end_tok is None:
        return None
    return int(start_tok['start']), int(end_tok['end'])


def _match_case(original, replacement):
    if not original or not replacement:
        return replacement
    if original.isupper() and len(original) > 1:
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    if original[:1].islower():
        return replacement[:1].lower() + replacement[1:]
    return replacement


def _find_span(sentence, needle, hint=None):
    """Find ``needle`` as a whole token/phrase, preferring the flagged span.

    Word-boundary matching matters: deleting the article 'a' must not find the
    'a' inside 'have'.
    """
    if not needle:
        return None
    pattern = re.compile(r'(?<!\w)' + re.escape(needle) + r'(?!\w)', re.I)
    regions = []
    if hint:
        lo, hi = hint
        regions.append((lo, hi))
    regions.append((0, len(sentence)))
    for lo, hi in regions:
        m = pattern.search(sentence, lo, hi)
        if m:
            return m.start(), m.end()
    return None


def _lower_tok(token):
    return str(token.get('t') if isinstance(token, dict) else token).lower()


def _neighbor(token_map, char_at, direction):
    if direction < 0:
        rows = [t for t in token_map.values() if int(t['end']) <= char_at]
        return max(rows, key=lambda t: int(t['end']), default=None)
    rows = [t for t in token_map.values() if int(t['start']) >= char_at]
    return min(rows, key=lambda t: int(t['start']), default=None)


def _edit(span, replacement, detail, confidence, source):
    return {
        'start': span[0],
        'end': span[1],
        'original': '',
        'replacement': replacement,
        'rule_id': detail.get('rule_id'),
        'constraint': detail.get('constraint'),
        'confidence': confidence,
        'source': source,
    }


def _span_for_nodes(details, node_ids, token_map):
    spans = [_span_for(details, nid, token_map) for nid in node_ids]
    spans = [s for s in spans if s]
    if not spans:
        return None
    return min(s[0] for s in spans), max(s[1] for s in spans)


def _from_remediation(detail, sentence, token_map, details):
    rem = detail.get('remediation')
    if not isinstance(rem, dict):
        return []
    edits = []
    groups = (('edits', 0.95, 'structured'),
              ('alternative_edits', 0.82, 'alternative'))
    for key, confidence, source in groups:
        for raw in rem.get(key) or []:
            if not isinstance(raw, dict):
                continue
            if raw.get('nodes'):
                span = _span_for_nodes(details, raw['nodes'], token_map)
            else:
                span = _span_for(details, raw.get('node'), token_map)
            if span is None:
                continue
            if raw.get('delete'):
                edits.append(_edit(span, '', detail, confidence, source))
            elif raw.get('insert_before'):
                point = (span[0], span[0])
                edits.append(_edit(point, str(raw['insert_before']), detail,
                                   confidence, source))
            elif raw.get('insert_after'):
                point = (span[1], span[1])
                edits.append(_edit(point, str(raw['insert_after']), detail,
                                   confidence, source))
            elif raw.get('replacement') is not None:
                edits.append(_edit(span, str(raw['replacement']), detail,
                                   confidence, source))
    return edits


def _from_text(detail, sentence, token_map, details):
    """Conservative extraction from the human-readable remediation prose.

    Only unambiguous "replace X with Y" / "add X before Y" / "drop X" forms
    are used.  Anything vaguer is ignored; the candidate validator is the
    final gate.
    """
    rem = detail.get('remediation')
    rem = rem if isinstance(rem, dict) else {}
    # Only the *suggested* fix is safe to parse: the alternative fix often
    # describes a different rewrite and mixing the two produces Frankenstein
    # sentences (e.g. dropping 'could' while also changing 'helped').
    text = str(rem.get('suggested_fix') or '').strip()
    if not text:
        text = str(detail.get('text') or '').strip()
    if not text:
        return []
    hint = None
    span = detail.get('span') or []
    if len(span) == 2:
        first = token_map.get(span[0])
        last = token_map.get(span[1] - 1)
        if first and last:
            hint = (int(first['start']), int(last['end']))

    edits = []
    surface = str(detail.get('surface') or '')
    found = _find_span(sentence, surface, hint) if surface else None

    def contextual(good):
        """Trim a leading/trailing word that the sentence already supplies."""
        words = good.split()
        if len(words) > 1 and found is not None:
            before = _neighbor(token_map, found[0], -1)
            after = _neighbor(token_map, found[1], 1)
            if before and _lower_tok(before) == words[0].lower():
                return ' '.join(words[1:])
            if after and _lower_tok(after) == words[-1].lower():
                return ' '.join(words[:-1])
        return good

    m = _WRITE_INSTEAD.search(text)
    if m:
        good, bad = contextual(m.group(1)), m.group(2)
        bad_span = _find_span(sentence, bad, hint)
        if bad_span is not None:
            return [_edit(bad_span, _match_case(sentence[bad_span[0]:bad_span[1]], good),
                          detail, 0.76, 'prose')]
    m = _USE_INSTEAD_SIMPLE.search(text)
    if m and surface and found is not None:
        good = contextual(m.group(1))
        return [_edit(found, _match_case(surface, good), detail, 0.74, 'prose')]
    for pat in (_CHANGE, _SHOULD_BE, _WRITE_NOT):
        for m in pat.finditer(text):
            a, b = m.group(1), m.group(2)
            if pat is _WRITE_NOT:
                good, bad = a, b
            else:
                bad, good = a, b
            bad_span = _find_span(sentence, bad, hint)
            if bad_span is None:
                continue
            edits.append(_edit(bad_span,
                               _match_case(sentence[bad_span[0]:bad_span[1]], good),
                               detail, 0.72, 'prose'))
            break
        if edits:
            break
    if not edits:
        m = _MUST_BE.search(text)
        if m:
            good, bad = m.group(1), m.group(2)
            bad_span = _find_span(sentence, bad, hint)
            if bad_span is not None:
                edits.append(_edit(bad_span, _match_case(
                    sentence[bad_span[0]:bad_span[1]], good), detail, 0.74, 'prose'))
    if not edits:
        m = _CHANGE_IT.search(text)
        if m and surface:
            good = m.group(1)
            target = found
            if _lower_tok({'t': surface}) in {'have', 'has', 'had',
                                               'is', 'are', 'was', 'were',
                                               'am', 'be', 'been'}:
                nxt = _neighbor(token_map, found[1], 1) if found else None
                if nxt is not None:
                    target = (int(nxt['start']), int(nxt['end']))
            if target is not None:
                edits.append(_edit(target, good, detail, 0.7, 'prose'))
    if not edits:
        m = _ARROW.finditer(text)
        for hit in m:
            bad, good = hit.group(1), hit.group(2)
            bad_span = _find_span(sentence, bad, hint)
            if bad_span is not None:
                edits.append(_edit(bad_span, _match_case(
                    sentence[bad_span[0]:bad_span[1]], good), detail, 0.7, 'prose'))
                break
    if not edits:
        m = _ADD_BEFORE.search(text)
        if m:
            art, before = m.group(1), m.group(2)
            before_span = _find_span(sentence, before, hint)
            if before_span is not None:
                edits.append(_edit((before_span[0], before_span[0]), art,
                                   detail, 0.7, 'prose'))
    if not edits:
        m = _SAY_INSTEAD.search(text)
        if m:
            good = re.sub(r'^(?:a|an|the)\s+', '', m.group(1), flags=re.I)
            if found is not None and good:
                edits.append(_edit(found, _match_case(surface, good),
                                   detail, 0.78, 'prose'))
    if not edits:
        m = _REMOVE.search(text)
        if m:
            bad = m.group(1)
            bad_span = _find_span(sentence, bad, hint)
            if bad_span is not None:
                edits.append(_edit(bad_span, '', detail, 0.7, 'prose'))
    if not edits:
        m = _WRITE_ONLY.search(text)
        if m and surface and found is not None:
            good = contextual(m.group(1))
            if _lower_tok({'t': good}) in {'many', 'much', 'few', 'little',
                                            'less', 'fewer', 'some', 'any'}:
                prev = _neighbor(token_map, found[0], -1)
                if prev and _lower_tok(prev) in {'much', 'many', 'few', 'little',
                                                 'less', 'fewer'}:
                    found = (int(prev['start']), int(prev['end']))
            edits.append(_edit(found, _match_case(surface, good),
                               detail, 0.68, 'prose'))
    return edits


def _dedupe(edits):
    """Remove exact duplicates but *keep* competing fixes for the same span.

    'a scissors' has two candidates at the same span ('scissor' from the
    determiner rule and 'pair of scissors' from the plural-only rule).  The
    first is ungrammatical, the second is correct, so both must be tried.
    """
    best = {}
    for edit in edits:
        key = (edit['start'], edit['end'], edit['replacement'])
        old = best.get(key)
        if old is None or edit['confidence'] > old['confidence']:
            best[key] = edit
    return sorted(best.values(),
                  key=lambda e: (e['start'], e['end'], e['replacement']))


def _apply(sentence, edits):
    selected = []
    for edit in sorted(edits, key=lambda e: (e['start'], e['end']), reverse=True):
        if selected and edit['end'] > selected[-1]['start']:
            continue
        selected.append(edit)
    out = sentence
    for edit in selected:
        out = out[:edit['start']] + edit['replacement'] + out[edit['end']:]
    if sentence[:1].isupper() and out[:1].islower():
        out = out[:1].upper() + out[1:]
    return out, list(reversed(selected))


def _candidate_sets(edits):
    """Yield edit sets in increasing size, one option per conflicting span."""
    groups = {}
    for edit in edits:
        groups.setdefault((edit['start'], edit['end']), []).append(edit)
    spans = sorted(groups)
    for group in groups.values():
        group.sort(key=lambda e: e['confidence'], reverse=True)
    n = len(spans)
    if n == 0:
        return
    if n <= 5:
        for size in range(1, n + 1):
            combos = list(itertools.combinations(spans, size))
            combos.sort(key=lambda chosen: max(
                groups[s][0]['confidence'] for s in chosen), reverse=True)
            for chosen in combos:
                for options in itertools.product(*(groups[s] for s in chosen)):
                    yield options
        return
    # Too many independent findings: prefer the full set, then each edit.
    for options in itertools.product(*(groups[s] for s in spans)):
        yield options
    for edit in sorted(edits, key=lambda e: e['confidence'], reverse=True):
        yield (edit,)


def has_actionable(details):
    """True when a sentence carries an error or a suggestion with a concrete edit."""
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        if detail.get('status') == 'error':
            return True
        for finding in detail.get('findings') or []:
            if not isinstance(finding, dict):
                continue
            rem = finding.get('remediation')
            rem = rem if isinstance(rem, dict) else {}
            if (finding.get('status') == 'error' or
                    (finding.get('status') == 'suggestion' and rem.get('edits'))):
                return True
    return False


def assemble(sentence, details, tokens, validate=None):
    """Build and validate one corrected sentence.

    ``validate(text) -> bool`` must confirm the candidate is grammatical.
    Returns ``None`` when no confident, validated correction can be built.
    """
    if not sentence or not details:
        return None
    token_map = _token_map(tokens)
    raw = []
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        if detail.get('status') == 'error':
            raw.extend(_from_remediation(detail, sentence, token_map, details))
            raw.extend(_from_text(detail, sentence, token_map, details))
        for finding in detail.get('findings') or []:
            if not isinstance(finding, dict):
                continue
            rem = finding.get('remediation')
            rem = rem if isinstance(rem, dict) else {}
            actionable = (finding.get('status') == 'error' or
                          (finding.get('status') == 'suggestion' and rem.get('edits')))
            if not actionable:
                continue
            raw.extend(_from_remediation(finding, sentence, token_map, details))
            raw.extend(_from_text(finding, sentence, token_map, details))
    edits = _dedupe(raw)
    edits = [e for e in edits
             if sentence[e['start']:e['end']] != e['replacement']]
    if not edits:
        return None

    for combo in _candidate_sets(edits):
        candidate, used = _apply(sentence, list(combo))
        candidate = re.sub(r'\s+', ' ', candidate).strip()
        candidate = re.sub(r'\s+([,.;:!?])', r'\1', candidate)
        if candidate == sentence.strip():
            continue
        if validate is not None and not validate(candidate):
            continue
        for edit in used:
            edit['original'] = sentence[edit['start']:edit['end']]
        return {
            'original_sentence': sentence,
            'corrected_sentence': candidate,
            'edits': used,
            'validated': True,
        }
    return None


def describe(result):
    """One-line summary for the XAI payload / logs."""
    if not result:
        return None
    edits = result.get('edits') or []
    return (f"Verified correction: {result['corrected_sentence']!r} "
            f"({len(edits)} edit{'s' if len(edits) != 1 else ''}).")
