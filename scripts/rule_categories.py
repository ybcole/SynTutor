"""Shared rule-id -> syllabus category map for the explanation generators.

Kept in one place so the exhaustive-explanation generators cannot drift apart
on which section a rule belongs to.
"""

CATEGORIES = {
    1: 'Word forms',
    2: 'Agreement',
    3: 'Articles and determiners',
    4: 'Nouns',
    5: 'Pronouns',
    6: 'Verbs',
    7: 'Adjectives and adverbs',
    8: 'Prepositions',
    9: 'Sentence structure',
    10: 'Punctuation and orthography',
    11: 'Meaning and usage',
}


def get_category(rid):
    """Syllabus category for a rule id like '6.2' (or the numeric major part)."""
    major = rid if isinstance(rid, int) else int(str(rid).split('.')[0])
    return CATEGORIES.get(major, 'Other')
