#!/usr/bin/env python3
"""Syntax-tree learning master sheet.

Chronological + exhaustive reference for the Syntax Builder quiz: every part of
SynTutor's own analysis, in the order the pipeline produces it.

  Stage 1  Tokenizer      spaCy word tokens
  Stage 2  POS tagger     lexical tags (NN, VBZ, IN, ...)  -> benepar leaves
  Stage 3  Parser         phrase structure (NP, VP, PP, ...) -> benepar tree
  Stage 4  Rule matrix    SynTutor's own grammar constraints (C-* -> rule ids)

Everything is pulled from the live code (server/, web/) so the sheet never drifts
from the model.

  npm run tree:sheet        # -> docs/tree_sheet.md + docs/tree_sheet.json
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

OUT_MD = os.path.join(ROOT, 'docs', 'tree_sheet.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'tree_sheet.json')
OUT_WEB = os.path.join(ROOT, 'web', 'content', 'tree_sheet.json')


def _read(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as fh:
        return _unescape(fh.read())


def _unescape(s):
    r"""Decode JS \uXXXX escapes pulled from source literals."""
    return re.sub(
        r'\\u([0-9a-fA-F]{4})',
        lambda m: chr(int(m.group(1), 16)),
        s,
    )


# ── Stage 2: lexical POS tags (benepar leaves) ─────────────────────────────
# Descriptions are the Penn Treebank glosses; coverage is every tag the parser
# can attach to a leaf.
POS_TAGS = [
    ('CC', 'Coordinating conjunction', 'and, but, or'),
    ('CD', 'Cardinal number', 'one, 42, 1990'),
    ('DT', 'Determiner', 'the, a, an, this, some'),
    ('EX', 'Existential there', 'There is a cat.'),
    ('FW', 'Foreign word', 'bonjour, etc.'),
    ('IN', 'Preposition / subordinating conjunction', 'in, of, that, if'),
    ('JJ', 'Adjective', 'quick, happy'),
    ('JJR', 'Adjective, comparative', 'quicker, happier'),
    ('JJS', 'Adjective, superlative', 'quickest, happiest'),
    ('LS', 'List item marker', '1., A.'),
    ('MD', 'Modal', 'can, will, must, should'),
    ('NN', 'Noun, singular / mass', 'cat, water, idea'),
    ('NNS', 'Noun, plural', 'cats, ideas'),
    ('NNP', 'Proper noun, singular', 'Alice, London'),
    ('NNPS', 'Proper noun, plural', 'Americans, Beatles'),
    ('PDT', 'Predeterminer', 'all the, both the'),
    ('POS', 'Possessive ending', "John's, the cat's"),
    ('PRP', 'Personal pronoun', 'I, he, she, it, they'),
    ('PRP$', 'Possessive pronoun', 'my, your, his, her, its, their'),
    ('RB', 'Adverb', 'quickly, very, not'),
    ('RBR', 'Adverb, comparative', 'quicker, more'),
    ('RBS', 'Adverb, superlative', 'quickest, most'),
    ('RP', 'Particle', 'up (give up), off (turn off)'),
    ('SYM', 'Symbol', '+, %, $, ='),
    ('TO', 'to', 'to go, to eat'),
    ('UH', 'Interjection', 'oh, wow, hey'),
    ('VB', 'Verb, base form', 'go, be, run'),
    ('VBD', 'Verb, past tense', 'went, was, ran'),
    ('VBG', 'Verb, gerund / present participle', 'going, running'),
    ('VBN', 'Verb, past participle', 'gone, run, written'),
    ('VBP', 'Verb, non-3rd person singular present', 'go, run, are'),
    ('VBZ', 'Verb, 3rd person singular present', 'goes, runs, is'),
    ('WDT', 'Wh-determiner', 'which, that, whatever'),
    ('WP', 'Wh-pronoun', 'who, whom, what'),
    ('WP$', 'Possessive wh-pronoun', "whose"),
    ('WRB', 'Wh-adverb', 'when, where, how'),
    ('HYPH', 'Hyphen', 'well-known'),
    ('#', 'Pound sign', '#10, #hashtag'),
    ('$', 'Currency symbol', '$5, €3'),
    ('-NONE-', 'Trace / empty category', '(deleted filler)'),
    ('.', 'Sentence-final punctuation', '. ? !'),
    (',', 'Comma', ','),
    (':', 'Colon / semicolon / dash', ': ; -'),
    (';', 'Semicolon', '; run-on fix'),
    ("'", 'Opening / closing quote', "' \""),
    ('"', 'Double quote', '"quoted"'),
    ('(', 'Opening bracket', '( ['),
    (')', 'Closing bracket', ') ]'),
]

# ── Stage 3: phrase-structure nodes (benepar constituents) ─────────────────
PHRASE_NODES = [
    ('S', 'Clause (sentence)', 'Subject + predicate: "The cat sat."'),
    ('NP', 'Noun phrase', 'the big cat, a student of physics'),
    ('VP', 'Verb phrase', 'is running, has eaten the cake'),
    ('PP', 'Prepositional phrase', 'in the garden, of physics'),
    ('ADJP', 'Adjective phrase', 'very happy, fond of music'),
    ('ADVP', 'Adverb phrase', 'very quickly, in the morning'),
    ('SBAR', 'Subordinate clause', 'because he left, which I saw'),
    ('SBARQ', 'Direct question', 'What did you say?'),
    ('SINV', 'Inverted clause', 'Never have I seen such a thing.'),
    ('SQ', 'Yes/no question fragment', 'Is it raining?'),
    ('FRAG', 'Fragment', 'Hello there. What a day!'),
    ('NML', 'Nominalized expression', 'the rich, the young'),
    ('WHNP', 'Wh-noun phrase', 'which book, who left'),
    ('WHADVP', 'Wh-adverb phrase', 'when, where, how'),
    ('WHADJP', 'Wh-adjective phrase', 'how tall, however old'),
    ('WHPP', 'Wh-prepositional phrase', 'to whom, for what'),
    ('QP', 'Quantifier phrase', 'more than five, about 20'),
    ('NX', 'Nominal expression', 'the man in black'),
    ('CONJP', 'Conjunction phrase', 'but rather, as well as'),
    ('UCP', 'Unlike-coordinated phrase', 'men and tigers'),
    ('LST', 'List', '1. apples 2. pears'),
    ('INTJ', 'Interjection node', 'Wow! Hey!'),
    ('PRT', 'Particle node', 'give up, turn off'),
    ('X', 'Unclassified', '(unanalyzable material)'),
]

# ── Rule matrix stage: constraint -> human name ────────────────────────────
# Loaded from the catalog so names match the quiz exactly.
def load_catalog():
    """Parse web/js/quiz/catalog.js -> {rule_id: rule_name} without a JS engine.

    Optional: RULEBOOK (server/ruleset.py) is the authoritative source of rule
    names, so if the quiz catalog is absent this simply returns {}."""
    path = os.path.join(ROOT, 'web', 'js', 'quiz', 'catalog.js')
    if not os.path.isfile(path):
        return {}
    src = _read('web/js/quiz/catalog.js')
    names = {}
    # entries look like: { id: '2.1', rule: 'Subject-verb agreement', ... }
    for m in re.finditer(
        r"\{\s*id:\s*'([^']+)'\s*,\s*rule:\s*'([^']*)'", src
    ):
        names[m.group(1)] = m.group(2)
    return names


def load_rulebook():
    """RULEBOOK from server/ruleset.py -> {rule_id: (name, example, method)}."""
    src = _read('server/ruleset.py')
    m = re.search(r'RULEBOOK\s*=\s*\{(.*?)\n\}', src, re.S)
    if not m:
        return {}
    out = {}
    for rid, name, example, method in re.findall(
        r"'([\d.]+)'\s*:\s*\('([^']*)'\s*,\s*'([^']*)'\s*,\s*(\w+)\)", m.group(1)
    ):
        out[rid] = (name, example, method)
    return out


def load_concepts():
    """RULE_CONCEPTS from web/js/rule-concepts.js -> {rule_id: text}."""
    path = os.path.join(ROOT, 'web', 'js', 'rule-concepts.js')
    if not os.path.isfile(path):
        return {}
    src = _unescape(open(path, encoding='utf-8').read())
    m = re.search(r'RULE_CONCEPTS\s*=\s*\{(.*?)\n\};', src, re.S)
    if not m:
        return {}
    out = {}
    for rid, text in re.findall(r"'([\d.]+)'\s*:\s*'((?:[^'\\]|\\.)*)'", m.group(1)):
        out[rid] = text.replace("\\'", "'")
    # Double-quoted values (used when the text contains apostrophes).
    for rid, text in re.findall(r"'([\d.]+)'\s*:\s*\"((?:[^\"\\]|\\.)*)\"", m.group(1)):
        out.setdefault(rid, text.replace('\\"', '"'))
    return out


def load_constraints():
    """(C_CONSTRAINT, rule_id, layer) from matrix.py + ruleset.py + licensing.py.

    matrix.py maps them in CONSTRAINT_RULE; the ruleset layer fires extra
    constraints directly inside _finding(...) calls, so both are scanned.
    """
    pairs = {}  # constraint -> (rule_id, layer)

    m = re.search(r'CONSTRAINT_RULE\s*=\s*\{(.*?)\n\}', _read('server/matrix.py'), re.S)
    if m:
        for constraint, rule_id in re.findall(
            r"'(C-[A-Z0-9-]+)'\s*:\s*\((?:'([^']+)'|None)", m.group(1)
        ):
            pairs[constraint] = (rule_id or '', 'T')

    # _finding('9.4', 'error', 'C-COMMA-SPLICE', ...) in ruleset.py
    ruleset = _read('server/ruleset.py')
    for rule_id, constraint in re.findall(
        r"_finding\(\s*'([\d.]+)'\s*,\s*'[^']*'\s*,\s*'(C-[A-Z0-9-]+)'", ruleset
    ):
        pairs.setdefault(constraint, (rule_id, 'T'))

    # licensing.py uses a positional tuple helper (_lex_finding style)
    licensing = _read('server/licensing.py')
    for rule_id, constraint in re.findall(
        r"'(C-[A-Z0-9-]+)'[^)\n]{0,120}?'([\d.]{1,5})'", licensing
    ):
        pairs.setdefault(constraint, (rule_id, 'L'))
    for rule_id, constraint in re.findall(
        r"_finding\(\s*'([\d.]+)'\s*,\s*'[^']*'\s*,\s*'(C-[A-Z0-9-]+)'", licensing
    ):
        pairs.setdefault(constraint, (rule_id, 'L'))

    return [(c, rid, layer) for c, (rid, layer) in sorted(pairs.items())]


def build():
    catalog = load_catalog()
    rulebook = load_rulebook()
    concepts = load_concepts()
    constraints = load_constraints()

    rules = []
    seen_rules = set()
    for constraint, rule_id, layer in constraints:
        name, example, method = rulebook.get(rule_id, ('', '', ''))
        rules.append({
            'constraint': constraint,
            'rule': rule_id,
            'name': name or catalog.get(rule_id, ''),
            'example': example,
            'method': method,
            'layer': layer,
            'concept': concepts.get(rule_id, ''),
        })
        if rule_id:
            seen_rules.add(rule_id)

    # Every catalog/RULEBOOK rule must appear even if it fires no C-* constraint
    # (coverage check + rows for rules detected structurally).
    for rid in sorted(set(rulebook) | set(catalog)):
        if rid in seen_rules:
            continue
        name, example, method = rulebook.get(rid, ('', '', ''))
        rules.append({
            'constraint': '',
            'rule': rid,
            'name': name or catalog.get(rid, ''),
            'example': example,
            'method': method,
            'layer': 'T',
            'concept': concepts.get(rid, ''),
        })

    # Order by rule id numerically (the natural syllabus order), then constraint.
    def key(r):
        if not r['rule']:
            return (999, 0, r['constraint'])
        try:
            sec, num = r['rule'].split('.')
            return (int(sec), int(num), r['constraint'])
        except ValueError:
            return (999, 0, r['constraint'])
    rules.sort(key=key)

    stages = [
        {
            'id': 1,
            'title': 'Tokenizer',
            'engine': 'spaCy (en_core_web_md)',
            'summary': 'Splits raw text into word tokens, keeping punctuation separate.',
            'count': None,
            'items': [],
        },
        {
            'id': 2,
            'title': 'Part-of-speech tagger',
            'engine': 'spaCy -> benepar leaves',
            'summary': 'Tags every token with a lexical category (NN, VBZ, IN, ...). These become the leaves of the tree.',
            'count': len(POS_TAGS),
            'items': [
                {'tag': t, 'name': n, 'example': e} for t, n, e in POS_TAGS
            ],
        },
        {
            'id': 3,
            'title': 'Constituency parser',
            'engine': 'benepar (benepar_en3)',
            'summary': 'Groups tokens into phrase nodes (NP, VP, PP, ...) bottom-up until one root node spans the sentence.',
            'count': len(PHRASE_NODES),
            'items': [
                {'tag': t, 'name': n, 'example': e} for t, n, e in PHRASE_NODES
            ],
        },
        {
            'id': 4,
            'title': 'Rule matrix (SynTutor)',
            'engine': 'server/matrix.py + server/licensing.py + server/ruleset.py',
            'summary': 'SynTutor\'s own analysis: walks the tree and fires grammar constraints. Each maps to a numbered rule.',
            'count': len(rules),
            'items': rules,
        },
    ]

    meta = {
        'generatedAt': __import__('datetime').date.today().isoformat(),
        'stageCount': len(stages),
        'posTagCount': len(POS_TAGS),
        'phraseNodeCount': len(PHRASE_NODES),
        'ruleCount': len({r['rule'] for r in rules if r['rule']}),
        'constraintCount': len(rules),
        'totalItems': sum(
            s['count'] for s in stages if s['count'] is not None
        ) + 1,  # + tokenizer stage (implicit)
    }
    sheet = {'meta': meta, 'stages': stages}
    # The learner-facing concept for each rule comes from rule-concepts.js and is
    # already plain language.  We deliberately do not fold in the older
    # "exhaustive" explanations, which were written in heavy syntactic jargon.
    return sheet


def write_md(sheet):
    L = []
    L.append('# Syntax Tree Learning Master Sheet')
    L.append('')
    L.append('> Chronological + exhaustive: every part of SynTutor\'s analysis,')
    L.append('> in the order the pipeline produces it. 1:1 with the model.')
    L.append('')
    m = sheet['meta']
    L.append(f"*Generated {m['generatedAt']}  •  "
             f"{m['posTagCount']} POS tags  •  "
             f"{m['phraseNodeCount']} phrase nodes  •  "
             f"{m['ruleCount']} rules  •  "
             f"{m['constraintCount']} constraints*")
    L.append('')
    L.append('---')
    L.append('')

    for stage in sheet['stages']:
        L.append(f"## Stage {stage['id']}: {stage['title']}")
        L.append('')
        L.append(f"*Engine: {stage['engine']}*")
        L.append('')
        L.append(stage['summary'])
        L.append('')
        if not stage['items']:
            L.append('_Tokenization is implicit — every word below is a token._')
            L.append('')
            continue
        if stage['id'] in (2, 3):
            L.append('| Tag | Meaning | Example |')
            L.append('|-----|---------|---------|')
            for it in stage['items']:
                L.append(f"| `{it['tag']}` | {it['name']} | {it['example']} |")
            L.append('')
        else:
            L.append('| Rule | Constraint | Name | Layer |')
            L.append('|------|-----------|------|-------|')
            for it in stage['items']:
                rid = f"`{it['rule']}`" if it['rule'] else '—'
                L.append(f"| {rid} | `{it['constraint']}` | {it['name'] or '—'} | {it['layer']} |")
            L.append('')
        L.append('---')
        L.append('')

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true', help='print JSON to stdout')
    args = ap.parse_args()

    sheet = build()
    if args.json:
        print(json.dumps(sheet, indent=2, ensure_ascii=False))
        return

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(sheet, fh, indent=2, ensure_ascii=False)
    os.makedirs(os.path.dirname(OUT_WEB), exist_ok=True)
    with open(OUT_WEB, 'w', encoding='utf-8') as fh:
        json.dump(sheet, fh, ensure_ascii=False, separators=(',', ':'))
    write_md(sheet)

    m = sheet['meta']
    print(f"[tree:sheet] {m['posTagCount']} POS tags, {m['phraseNodeCount']} phrase "
          f"nodes, {m['ruleCount']} rules, {m['constraintCount']} constraints "
          f"-> docs/tree_sheet.md + docs/tree_sheet.json + web/content/tree_sheet.json")


if __name__ == '__main__':
    main()
