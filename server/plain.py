"""Turn internal grammar descriptions into classroom English for EFL learners."""

import re


_TAG_PREFIX = re.compile(
    r"^The\s+[A-Za-z$]{1,6}\s+'[^']*'"
    r"(?:\s+(?:inside|in)\s+the\s+[A-Za-z$]{1,6}\s+'[^']*')?"
    r"\s+is flagged:\s*",
    re.I,
)
_SENTENCE_PREFIX = re.compile(r"^In the sentence '[^']*',\s*", re.I)

_TAG_NAMES = {
    'VBP': 'present verb',
    'VBZ': 'he/she/it verb',
    'VBD': 'past verb',
    'VBG': '-ing verb',
    'VBN': 'past participle',
    'VB': 'base verb',
    'MD': 'modal verb',
    'NN': 'noun',
    'NNS': 'plural noun',
    'NNP': 'name',
    'NNPS': 'names',
    'PRP': 'pronoun',
    'PRP$': 'possessive word',
    'JJ': 'adjective',
    'JJR': 'comparative adjective',
    'JJS': 'superlative adjective',
    'RB': 'adverb',
    'RBR': 'comparative adverb',
    'RBS': 'superlative adverb',
    'IN': 'preposition',
    'DT': 'word before a noun',
    'CC': 'linking word',
    'TO': 'to',
    'CD': 'number',
    'SQ': 'question',
    'SBARQ': 'question',
    'SINV': 'word-order pattern',
    'SBAR': 'part of the sentence',
    'NP': 'noun group',
    'VP': 'verb group',
    'ADJP': 'adjective group',
    'ADVP': 'adverb group',
    'PP': 'preposition group',
    'FRAG': 'fragment',
}
_TAG_RE = re.compile(r"\b(" + "|".join(
    sorted(_TAG_NAMES, key=len, reverse=True)) + r")\b")

_REPLACEMENTS = [
    (r"\bthe '-ed' form \(past participle\)", "the past participle (third form)"),
    (r"\bthe '-ed' form\b", "the past participle"),
    (r"\bnon-third-person present\b",
     "present form used with I/you/we/they"),
    (r"\bthird-person singular present form\b", "he/she/it present form"),
    (r"\bthird-person-singular form\b", "he/she/it form"),
    (r"\bthird-person singular\b", "he/she/it"),
    (r"\b3rd person singular\b", "he/she/it"),
    (r"\b3rd person plural\b", "they (plural)"),
    (r"\bpresent participle\b(?!\s*\()", "-ing form"),
    (r"\bpast participle\b(?!\s*\()", "past participle (third form)"),
    (r"\bconstituency tree\b", "sentence structure"),
    (r"\bparse tree\b", "sentence structure"),
    (r"\bnoun phrase\b", "noun group"),
    (r"\bverb phrase\b", "verb group"),
    (r"\badjective phrase\b", "adjective group"),
    (r"\badverb phrase\b", "adverb group"),
    (r"\bprepositional phrase\b", "preposition group"),
    (r"\bdeterminer slot\b", "position before the noun"),
    (r"\bdeterminer\b", "word before a noun"),
    (r"\bauxiliary verb\b", "helper verb"),
    (r"\bauxiliary\b", "helper verb"),
    (r"\bfinite verb\b", "main verb"),
    (r"\bnon-finite\b", "not a full verb"),
    (r"\bfinite\b", "with a tense"),
    (r"\blexical head\b", "main word"),
    (r"\bhead noun\b", "main noun"),
    (r"\bhead verb\b", "main verb"),
    (r"\bcomplement\b", "completing word"),
    # These words are also ordinary family terms. Rewrite only explicit tree terms.
    (r"\bdaughter(?=\s+(?:node|constituent|branch)s?\b)", "child"),
    (r"\bsister(?=\s+(?:node|constituent|branch)s?\b)", "sibling"),
    (r"\bclause\b", "part of the sentence"),
    (r"\bprogressive\b", "-ing form"),
    (r"\bplain form\b", "base form"),
    (r"\btensed form\b", "form with a tense"),
    (r"\btensed verb\b", "verb with a tense"),
    (r"\btensed\b", "with a tense"),
    (r"\blicensed\b", "allowed"),
    (r"\blicenses\b", "allows"),
    (r"\blicense\b", "allow"),
    (r"\bagreement\b", "match"),
    (r"\bagrees\b", "matches"),
    (r"\bagree\b", "match"),
    (r"\bselects\b", "is used with"),
    (r"\bselect\b", "use with"),
    (r"\btransitive\b", "needing an object"),
    (r"\bintransitive\b", "not taking an object"),
    (r"\bhomophone\b", "sound-alike word"),
    (r"\breflexive pronoun\b", "-self/-selves pronoun"),
    (r"\binversion\b", "word order"),
    (r"\bpassive voice\b", "passive"),
    (r"\bpl\b", "plural"),
    (r"\bsg\b", "singular"),
    (r"\bPOS\b", "word type"),
]

_ROLE_NAMES = {
    'auxiliary-verb form': 'helper-verb form',
    'verb head': 'main verb',
    'head noun': 'main noun',
    'existential': 'there is/are',
    'existential there': 'there is/are',
    'noun number': 'singular/plural',
    'quantifier': 'quantity word',
    'quantifier-noun agreement': 'quantity word + noun',
    'determiner stacking': 'extra word before noun',
    'subject-verb agreement link': 'subject-verb match',
    'inversion': 'word order',
    'fragment root': 'incomplete sentence',
    'homophone': 'sound-alike word',
    'causative': 'verb pattern',
    'complement type': 'verb pattern',
    'verb complement': 'verb pattern',
    'unrated': 'word form',
}


# Quoted input/examples are evidence, not instructional terminology.
# Preserve exact spelling and spacing within these spans, including contractions.
_QUOTED_SPAN = re.compile(
    r"""'(?:(?:[^'])|(?<=[A-Za-z])'(?=[A-Za-z]))*'"""
    r"""|"(?:[^"\\]|\\.)*"|“[^”]*”|‘(?:[^’]|(?<=[A-Za-z])’(?=[A-Za-z]))*’"""
)


def _simplify_unquoted(segment):
    segment = _TAG_RE.sub(lambda m: _TAG_NAMES[m.group(1)], segment)
    for pattern, replacement in _REPLACEMENTS:
        segment = re.sub(pattern, replacement, segment, flags=re.I)
    return re.sub(r"\s+", " ", segment)


def _replace_unquoted_terms(value):
    parts = []
    last = 0
    for match in _QUOTED_SPAN.finditer(value):
        parts.append(_simplify_unquoted(value[last:match.start()]))
        parts.append(match.group(0))
        last = match.end()
    parts.append(_simplify_unquoted(value[last:]))
    return "".join(parts)


def _plain_text(text, capitalize=True):
    if not isinstance(text, str):
        return text
    value = text.strip()
    if not value:
        return value
    value = _SENTENCE_PREFIX.sub('', value)
    value = _TAG_PREFIX.sub('', value)
    value = _replace_unquoted_terms(value).strip()
    if capitalize and value and value[0].isalpha():
        value = value[0].upper() + value[1:]
    return value


def plain_text(text):
    return _plain_text(text)


def plain_role(role):
    if not isinstance(role, str):
        return role
    key = role.strip().lower()
    return _ROLE_NAMES.get(key, _plain_text(role, capitalize=False))


def _simplify_remediation(rm, fallback):
    if not isinstance(rm, dict):
        return
    for key in ('violation', 'suggested_fix', 'alternative_fix'):
        if rm.get(key):
            rm[key] = _plain_text(rm[key])
    if not rm.get('violation') and fallback:
        rm['violation'] = fallback


def apply_plain_language(details, summary):
    first_error = None
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        if detail.get('status') != 'error':
            continue
        detail['text'] = _plain_text(detail.get('text'))
        detail['role'] = plain_role(detail.get('role'))
        _simplify_remediation(detail.get('remediation'), detail['text'])
        if first_error is None:
            first_error = detail
        for finding in detail.get('findings', []) or []:
            if not isinstance(finding, dict) or finding.get('status') != 'error':
                continue
            finding['text'] = _plain_text(finding.get('text'))
            finding['role'] = plain_role(finding.get('role'))
            _simplify_remediation(finding.get('remediation'), finding['text'])
    if first_error is not None:
        summary['explanation'] = first_error['text']
    else:
        summary['explanation'] = _plain_text(summary.get('explanation'))
    if summary.get('detector_note'):
        summary['detector_note'] = _plain_text(summary['detector_note'])
    return summary