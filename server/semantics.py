"""SynTutor Stage-11 semantics layer (spec R11).

Deterministic, closed-lexicon semantic checks over the benepar constituent
tree produced by :mod:`parse_engine`.  The rule matrix in :mod:`matrix` is
strictly *read-only* here: ``analyze_semantics`` never mutates ``analysis``
or ``matrix_result``, so the syntax verdict (``summary.valid`` and
``constraints_fired``) is preserved bit-for-bit (audit Gate 1).

Rules implemented
-----------------
* ``R11.2`` / ``R8.1`` — collocations, governed prepositions and light verbs
  (``depend in`` → ``S-PREPOSITION``, ``do a decision`` → ``S-COLLOCATION``).
* ``R11.3`` — tense–time agreement (``Yesterday I go`` → ``S-TENSE-TIME``).
  The check is **clause-scoped**: a deictic anchor and the predicate it clashes
  with must occur in the *same* clause, so a habitual adverb or a time word in
  a subordinate/independent clause can no longer suppress (or invent) a
  mismatch in another clause.  Generic sentences that carry no deictic anchor
  (``The children play in the park every day``) still never fire.
* ``R11.4`` — selectional restrictions (``The book eats the boy`` →
  ``S-SELECTIONAL``).  Entity classes come from explicit closed lexicons, an
  optional deterministic WordNet fallback (:mod:`server.lexicon`), a
  conservative pronoun table, and spaCy NER (a ``PERSON`` named entity marks
  its NP as animate).  A noun whose class no evidence establishes is left
  unclassified and never flagged.
* ``R11.6`` — subject–predicate compatibility (``The number seven is
  hungry`` → ``S-PREDICATE-COMPAT``, status ``warning``).  A copular predicate
  adjective drawn from a small biological-state taxonomy (physiological states
  such as ``hungry``/``thirsty``/``tired``/``exhausted``/``starving`` and
  life/death states ``dead``/``alive``) is checked against the subject's entity
  class.  It is reported as an *advisory* anomaly "under a literal
  interpretation", noting that a figurative/personified reading may be
  intended; unambiguous but idiomatic combinations (a ``dead`` battery, a
  ``thirsty`` plant) are deliberately not reported.
* ``R11.5`` — PP-attachment ambiguity (``The boy saw the man with a
  telescope``).  Two explicit readings are materialised as **deep-copied**
  trees with the PP re-parented and ``span: [start, end)`` (and ``surface``)
  recomputed bottom-up for every affected ancestor.

Finding severities
------------------
``status`` is ``'error'`` for the established, definitive semantic rules
(collocation, tense–time, selectional restriction) and ``'warning'`` for the
advisory literal-interpretation anomaly of R11.6.  Findings never affect the
syntax verdict.

No external ML/HuggingFace dependency: the only inputs are the token stream
and constituent tree of the existing parser; every lexicon below is explicit
and closed.

Return contract
---------------
``analyze_semantics`` returns::

    {
      'status':     'ok',                      # 'ok' | 'unavailable'
      'available':  True,                      # False on a controlled failure
      'findings':  [ {rule, constraint, status, category, text,
                      evidence, suggestion}, ... ],
      'ambiguous': bool,                       # convenience mirror
      'ambiguity': {'ambiguous': bool,         # R11.5
                    'readings': [reading, ...]},
      'tree_variants': [ {attachment, root, pp, np}, ... ],   # legacy/UI
      'summary': {...},
    }

Each ``reading`` has ``label``, ``paraphrase``, ``thematic_roles``, ``tree``
and ``node_details`` (keyed by node id).  ``tree_variants`` is retained as the
non-default alternative in the shape the existing UI already consumes.

When the semantic layer cannot run, :mod:`app` substitutes a schema-consistent
payload with ``status='unavailable'`` and ``available=False`` so a failure is
never mistaken for a clean "no findings" result.
"""

from __future__ import annotations

import copy
import re

try:  # imported as a package member (scripts/audit_x.py) ...
    from server.matrix import (
        LINKING_VERBS,
        _base_form,
        _leaves_list,
        _np_head,
        _singular_noun,
    )
    from server import lexicon
except ImportError:  # ... or as a server-local module (server/app.py)
    from matrix import (
        LINKING_VERBS,
        _base_form,
        _leaves_list,
        _np_head,
        _singular_noun,
    )
    import lexicon

# ── closed lexicons ────────────────────────────────────────────────────────

# Common nouns that denote animate beings (people / animals), listed in their
# singular base form.  This is the highest-confidence override; when a lemma is
# not listed, :func:`_entity_class` may fall back to WordNet and — for proper
# nouns and pronouns — to NER / a conservative pronoun table.
ANIMATE_NOUNS = frozenset({
    # people
    'person', 'people', 'man', 'woman', 'boy', 'girl', 'child', 'baby', 'kid',
    'adult', 'human', 'student', 'pupil', 'teacher', 'professor', 'doctor',
    'nurse', 'patient', 'dentist', 'lawyer', 'judge', 'engineer', 'scientist',
    'researcher', 'artist', 'writer', 'reader', 'singer', 'dancer', 'actor',
    'actress', 'musician', 'friend', 'enemy', 'neighbor', 'brother', 'sister',
    'mother', 'father', 'parent', 'grandmother', 'grandfather', 'uncle',
    'aunt', 'cousin', 'son', 'daughter', 'husband', 'wife', 'spouse',
    'partner', 'girlfriend', 'boyfriend', 'colleague', 'classmate',
    'teammate', 'roommate', 'boss', 'manager', 'employee', 'worker', 'farmer',
    'waiter', 'waitress', 'cook', 'chef', 'driver', 'pilot', 'soldier',
    'officer', 'police', 'king', 'queen', 'prince', 'princess', 'hero',
    'villain', 'thief', 'robber', 'criminal', 'victim', 'witness', 'guest',
    'host', 'customer', 'client', 'merchant', 'vendor', 'stranger', 'citizen',
    'member', 'volunteer', 'angel', 'god', 'goddess',
    # animals
    'dog', 'cat', 'kitten', 'puppy', 'bird', 'fish', 'horse', 'cow', 'bull',
    'ox', 'calf', 'pig', 'sheep', 'goat', 'chicken', 'rooster', 'hen', 'duck',
    'goose', 'turkey', 'rabbit', 'hare', 'mouse', 'rat', 'bear', 'lion',
    'lioness', 'tiger', 'wolf', 'fox', 'deer', 'monkey', 'gorilla',
    'elephant', 'giraffe', 'zebra', 'rhino', 'hippo', 'kangaroo', 'koala',
    'panda', 'snake', 'turtle', 'tortoise', 'frog', 'toad', 'whale',
    'dolphin', 'shark', 'octopus', 'crab', 'lobster', 'shrimp', 'owl',
    'eagle', 'hawk', 'crow', 'sparrow', 'parrot', 'penguin', 'seagull',
    'swan', 'peacock', 'leopard', 'cheetah', 'donkey', 'mule', 'pony',
    'hamster', 'squirrel', 'hedgehog', 'raccoon', 'otter', 'seal', 'walrus',
    'mosquito', 'ant', 'bee', 'wasp', 'beetle', 'butterfly', 'dragonfly',
    'ladybug', 'grasshopper',
})

# Physical/non-animate things.  Used as the expected object class of verbs
# that take a non-edible object (``read``, ``write``, ``wear``).
INANIMATE_OBJECTS = frozenset({
    # texts / information
    'book', 'letter', 'magazine', 'newspaper', 'novel', 'story', 'text',
    'page', 'article', 'email', 'message', 'note', 'poem', 'document',
    'report', 'paper', 'sign', 'sentence', 'word', 'name', 'number', 'list',
    'essay', 'blog', 'post', 'code', 'program', 'script', 'song', 'music',
    'speech', 'news', 'poetry', 'journal', 'diary', 'checklist', 'form',
    # clothing / accessories
    'shirt', 'dress', 'hat', 'coat', 'shoe', 'sock', 'glove', 'scarf',
    'glasses', 'sunglasses', 'watch', 'ring', 'necklace', 'bracelet',
    'earring', 'cap', 'jacket', 'sweater', 'skirt', 'pant', 'trouser',
    'jean', 'short', 'uniform', 'tie', 'belt', 'mask', 'costume', 'makeup',
    'boot', 'sandal', 'sneaker', 'hoodie', 'blouse', 'suit', 'gown',
    # appliances / devices / tools
    'phone', 'computer', 'laptop', 'tablet', 'camera', 'speaker', 'headphone',
    'charger', 'battery', 'cable', 'wire', 'button', 'switch', 'handle',
    'wheel', 'engine', 'machine', 'robot', 'tool', 'hammer', 'nail', 'screw',
    'ladder', 'rope', 'net', 'television', 'radio', 'screen', 'monitor',
    'keyboard', 'mouse', 'printer', 'fan', 'clock', 'lamp', 'light', 'candle',
    'mirror', 'brush', 'comb', 'towel', 'soap', 'umbrella',
    # furniture / household
    'table', 'chair', 'desk', 'bed', 'sofa', 'couch', 'shelf', 'drawer',
    'cupboard', 'fridge', 'oven', 'stove', 'sink', 'toilet', 'shower',
    'blanket', 'pillow', 'curtain', 'carpet', 'rug', 'vase',
    # containers / small objects
    'bag', 'box', 'bottle', 'cup', 'glass', 'plate', 'bowl', 'spoon', 'fork',
    'knife', 'basket', 'bucket', 'jar', 'can', 'packet', 'envelope', 'stamp',
    'folder', 'file', 'sheet', 'notebook', 'pen', 'pencil', 'eraser', 'ruler',
    'card', 'ticket', 'receipt', 'map', 'coin', 'bill', 'money', 'key',
    'wallet', 'purse', 'broom', 'mop',
    # vehicles / places / nature / misc
    'car', 'bus', 'train', 'plane', 'bike', 'bicycle', 'boat', 'ship', 'truck',
    'house', 'building', 'door', 'window', 'wall', 'floor', 'roof', 'garden',
    'tree', 'flower', 'plant', 'stone', 'rock', 'ball', 'toy', 'game',
    'movie', 'film', 'show', 'picture', 'photo', 'image', 'video', 'painting',
    'flag', 'poster', 'banner', 'sticker', 'label', 'tag', 'badge', 'trophy',
    'medal', 'prize', 'gift', 'present', 'parcel', 'package', 'toy',
})

# Foods (singular base forms) — the expected object class of ``eat``.
EDIBLE_NOUNS = frozenset({
    'cake', 'apple', 'bread', 'rice', 'meat', 'fish', 'egg', 'fruit', 'food',
    'cookie', 'pizza', 'sandwich', 'banana', 'orange', 'cheese', 'chicken',
    'soup', 'salad', 'pasta', 'noodle', 'potato', 'tomato', 'carrot', 'cereal',
    'toast', 'butter', 'sugar', 'candy', 'chocolate', 'chip', 'burger',
    'hotdog', 'steak', 'bacon', 'pie', 'muffin', 'donut', 'pancake', 'waffle',
    'grape', 'strawberry', 'blueberry', 'lemon', 'lime', 'peach', 'pear',
    'mango', 'melon', 'watermelon', 'corn', 'bean', 'nut', 'snack', 'meal',
    'breakfast', 'lunch', 'dinner', 'dessert', 'honey', 'jam', 'yogurt',
    'cream', 'biscuit', 'cracker', 'sausage', 'ham', 'turkey', 'beef', 'pork',
    'lamb', 'shrimp', 'crab', 'lobster', 'oyster', 'mushroom', 'onion',
    'garlic', 'pepper', 'salt', 'cabbage', 'lettuce', 'spinach', 'broccoli',
    'pea', 'cucumber', 'pumpkin', 'berry', 'cherry', 'date', 'fig', 'plum',
    'apricot', 'coconut', 'pineapple', 'papaya', 'avocado', 'olive',
})

# Liquids — the expected object class of ``drink``.
DRINKABLE_NOUNS = frozenset({
    'water', 'milk', 'juice', 'tea', 'coffee', 'wine', 'beer', 'soda', 'cola',
    'lemonade', 'milkshake', 'smoothie', 'cider', 'champagne', 'whiskey',
    'whisky', 'vodka', 'rum', 'cocktail', 'latte', 'espresso', 'cocoa',
    'punch', 'nectar', 'liquid',
})

# Abstract entities: things that are not physical objects *or* living beings
# (mathematical objects, ideas, states, times, qualities).  Kept separate from
# INANIMATE_OBJECTS on purpose: an abstract entity is not interchangeable with a
# physical object merely because both are non-animate.  Used by the
# subject–predicate compatibility rule (R11.6) and, for uncertainty handling,
# to tell a *known* entity class apart from an unclassified one.
ABSTRACT_NOUNS = frozenset({
    # mathematical / logical objects
    'number', 'numeral', 'figure', 'digit', 'value', 'quantity', 'amount',
    'sum', 'total', 'product', 'quotient', 'fraction', 'percentage', 'ratio',
    'equation', 'formula', 'theorem', 'proof', 'problem', 'solution',
    'answer', 'question', 'result', 'measure', 'measurement', 'statistic',
    # ideas / information / mental entities
    'idea', 'thought', 'concept', 'notion', 'theory', 'hypothesis', 'belief',
    'opinion', 'view', 'fact', 'truth', 'lie', 'information', 'knowledge',
    'data', 'memory', 'dream', 'hope', 'fear', 'wish', 'desire', 'emotion',
    'feeling', 'mind', 'reason', 'cause', 'effect', 'purpose', 'goal',
    'plan', 'method', 'process', 'system', 'rule', 'law', 'principle',
    'logic', 'meaning', 'word', 'sentence', 'language', 'name', 'symbol',
    'sign', 'signal', 'code', 'message', 'story', 'history',
    # time / states / qualities
    'time', 'moment', 'period', 'future', 'past', 'present', 'change',
    'growth', 'difference', 'similarity', 'relationship', 'connection',
    'chance', 'risk', 'opportunity', 'possibility', 'ability', 'skill',
    'power', 'strength', 'beauty', 'honesty', 'justice', 'freedom',
    'happiness', 'sadness', 'anger', 'joy', 'love', 'hate', 'health',
    'education', 'science', 'mathematics', 'math', 'art', 'music', 'grammar',
    'life', 'death', 'success', 'failure', 'luck', 'fate',
})

# Biological / physiological states that can only hold, literally, of a living
# subject.  They are split into two subclasses because their selectional
# profiles differ, and because a mismatch is always an *advisory* R11.6
# warning (personification, metaphor and fiction routinely apply these to
# non-living referents), never a hard error.
#
# * physiological — hunger / fatigue / illness predicates: require an animate
#   subject.  ``starving`` is grouped with ``hungry`` (the same underlying
#   condition) so a clause is never reported twice for the same issue.
# * life — life/death predicates: require a living (animate or organism)
#   subject.  They idiomatically apply to some artifacts ("a dead battery")
#   and are therefore not reported for physical objects.
PHYSIOLOGICAL_STATE_ADJECTIVES = frozenset({
    'hungry', 'thirsty', 'starving',
    'tired', 'sleepy', 'exhausted',
    'pregnant', 'sick',
})
LIFE_STATE_ADJECTIVES = frozenset({'dead', 'alive'})

# Union kept for documentation / backward compatibility.
BIOLOGICAL_STATE_ADJECTIVES = (
    PHYSIOLOGICAL_STATE_ADJECTIVES | LIFE_STATE_ADJECTIVES
)

# adjective subclass -> (human label, the entity class it literally requires)
_BIOLOGICAL_SUBCLASS = {
    'physiological': ('a biological/physiological state', 'animate'),
    'life': ('a life/death state', 'living'),
}

# Verbs with a fixed subject/object selectional profile.  Deliberately small
# and closed so common inanimate subjects of other verbs are never flagged.
AGENTIVE_ACTION_VERBS = frozenset({'eat', 'drink', 'read', 'write', 'wear',
                                   'kill'})

# Verb → (label, expected object class) for the object argument.
_OBJECT_CLASS = {
    'eat': ('edible', EDIBLE_NOUNS),
    'drink': ('drinkable', DRINKABLE_NOUNS),
    'read': ('inanimate', INANIMATE_OBJECTS),
    'write': ('inanimate', INANIMATE_OBJECTS),
    'wear': ('inanimate', INANIMATE_OBJECTS),
    'kill': ('animate', ANIMATE_NOUNS),
}

# Some past-tense forms the matrix base-form helper does not map.
_IRREGULAR_PAST_TO_BASE = {
    'ate': 'eat', 'drank': 'drink', 'ran': 'run', 'sang': 'sing',
    'swam': 'swim', 'spoke': 'speak', 'wrote': 'write', 'saw': 'see',
    'heard': 'hear', 'read': 'read', 'thought': 'think', 'dreamt': 'dream',
    'slept': 'sleep', 'came': 'come', 'went': 'go', 'made': 'make',
    'took': 'take', 'gave': 'give', 'got': 'get', 'said': 'say',
    'found': 'find', 'left': 'leave', 'felt': 'feel', 'kept': 'keep',
    'met': 'meet', 'paid': 'pay', 'put': 'put', 'told': 'tell',
    'wore': 'wear', 'knew': 'know', 'grew': 'grow', 'drew': 'draw',
    'flew': 'fly', 'threw': 'throw', 'drove': 'drive', 'rode': 'ride',
    'chose': 'choose', 'spent': 'spend', 'sent': 'send', 'built': 'build',
    'bought': 'buy', 'caught': 'catch', 'taught': 'teach', 'brought': 'bring',
}

# ── R11.2 / R8.1 lexicons ──────────────────────────────────────────────────

# Verb → the preposition its PP complement must use (closed set of near-fixed
# government patterns; only reported when a PP *is* present but wrong).
GOVERNED_PREPOSITION = {
    'depend': 'on', 'rely': 'on', 'insist': 'on', 'consist': 'of',
    'belong': 'to', 'refer': 'to', 'succeed': 'in', 'apologize': 'for',
    'cope': 'with', 'deal': 'with',
}

# Verb → prepositions that must NOT follow it (redundant / ungrammatical).
REDUNDANT_PREPOSITION = {
    'discuss': frozenset({'about'}),
}

# Verb → the preposition required before a direct object (missing-prep error,
# classic ``listen music`` → ``listen to music``).
OBJECT_PREPOSITION_VERBS = {
    'listen': 'to',
}

# Noun → the light verb it collocates with (classic ``do a decision``,
# ``make homework`` errors).
LIGHT_VERB_NOUN = {
    # make
    'decision': 'make', 'mistake': 'make', 'promise': 'make', 'plan': 'make',
    'choice': 'make', 'effort': 'make', 'progress': 'make',
    'difference': 'make', 'appointment': 'make', 'suggestion': 'make',
    'complaint': 'make', 'call': 'make', 'noise': 'make', 'excuse': 'make',
    # do
    'homework': 'do', 'housework': 'do', 'dishes': 'do', 'laundry': 'do',
    'exercise': 'do', 'business': 'do', 'shopping': 'do', 'research': 'do',
    # take
    'shower': 'take', 'bath': 'take', 'break': 'take', 'nap': 'take',
    'look': 'take', 'photo': 'take', 'picture': 'take', 'risk': 'take',
    'turn': 'take', 'walk': 'take', 'care': 'take', 'notes': 'take',
    # have
    'chat': 'have', 'conversation': 'have', 'meal': 'have', 'lunch': 'have',
    'dinner': 'have', 'breakfast': 'have',
}

# ── R11.3 lexicons ─────────────────────────────────────────────────────────

# Deictic temporal anchors (closed).  Frequency adverbs ("every", "always", …)
# are deliberately NOT cues: genericity is signalled structurally by the
# absence of a deictic anchor in the clause, so no blanket suppression list is
# needed (see :func:`_check_tense_time`).
PAST_TIME_WORDS = frozenset({'yesterday', 'ago'})
FUTURE_TIME_WORDS = frozenset({'tomorrow'})
PRESENT_TIME_WORDS = frozenset({'now'})

_TIME_NOUNS = frozenset({
    'night', 'week', 'month', 'year', 'morning', 'afternoon', 'evening',
    'day', 'weekend', 'summer', 'winter', 'spring', 'fall', 'semester',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
    'sunday',
})

_TIME_PATTERN = re.compile(r'^(last|next)\s+(\w+)$')

_PREP_TAGS = ('IN', 'TO')
_LEXICAL_VERB_TAGS = ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')

# Node-type → human role used by R11.5 ``node_details``.
_ROLE_BY_TYPE = {
    'S': 'clause',
    'SBAR': 'subordinate clause',
    'SBARQ': 'subordinate question',
    'SINV': 'inverted clause',
    'NP': 'noun phrase',
    'NML': 'nominal',
    'VP': 'verb phrase',
    'PP': 'prepositional phrase',
    'ADVP': 'adverb phrase',
    'ADJP': 'adjective phrase',
    'PRT': 'particle',
}


# ── tree helpers ────────────────────────────────────────────────────────────

def _walk(node, parent=None):
    """Yield ``(node, parent)`` pairs depth-first, parents from the graph."""
    yield node, parent
    for child in node.get('children', []):
        yield from _walk(child, node)


def _by_id(root):
    return {node['id']: node for node, _ in _walk(root)}


def _verb_base(leaf):
    """Base form of a lexical verb leaf (handles irregular past forms)."""
    base = _base_form(leaf)
    return _IRREGULAR_PAST_TO_BASE.get(base, base)


def _main_verb_leaf(node):
    """The lexical (non-modal) verb leaf of a phrase — the last one, so
    ``will do`` resolves to ``do`` and ``has eaten`` to ``eaten``."""
    cands = [lf for lf in _leaves_list(node) if lf['type'] in _LEXICAL_VERB_TAGS]
    return cands[-1] if cands else None


def _first_prep(pp_node):
    for lf in _leaves_list(pp_node):
        if lf['type'] in _PREP_TAGS:
            return lf
    return None


def _subject_of(s_node, vp_node):
    """The NP immediately preceding the VP (the clause subject)."""
    subject = None
    for child in s_node.get('children', []):
        if child is vp_node:
            break
        if child['type'] == 'NP':
            subject = child
    return subject


def _clause_vp(s_node):
    return next((c for c in s_node.get('children', []) if c['type'] == 'VP'),
                None)


def _finding(rule, constraint, category, text, evidence, suggestion,
             status='error'):
    """Build one semantic finding.

    ``confidence_label`` is deliberately **qualitative**, not a numeric
    probability: ``Direct Rule Match`` for a definitive deterministic-rule
    violation and ``Advisory Suggestion`` for a hedged literal-interpretation
    warning.  There is no trained/probabilistic model in the feedback path, so
    no numeric confidence is ever emitted.
    """
    return {
        'rule': rule,
        'constraint': constraint,
        'status': status,
        'category': category,
        'text': text,
        'evidence': evidence,
        'suggestion': suggestion,
        'confidence_label': ('Advisory Suggestion' if status == 'warning'
                             else 'Direct Rule Match'),
        'provenance': f'deterministic rule {rule} ({constraint})',
    }


# ── R11.2 / R8.1  collocations, governed prepositions & light verbs ─────────

def _check_collocations(root, findings):
    for node, _ in _walk(root):
        if node['type'] != 'VP':
            continue
        head = _main_verb_leaf(node)
        if head is None:
            continue
        base = _verb_base(head)
        leaves = _leaves_list(node)
        children = node.get('children', [])

        # (a) governed preposition: the verb requires a specific preposition.
        if base in GOVERNED_PREPOSITION:
            expected = GOVERNED_PREPOSITION[base]
            for child in children:
                if child['type'] != 'PP':
                    continue
                prep = _first_prep(child)
                if prep is not None and prep['surface'].lower() != expected:
                    findings.append(_finding(
                        'R11.2', 'S-PREPOSITION', 'governed preposition',
                        f"Governed preposition: the verb '{head['surface']}' "
                        f"requires '{expected}', not '{prep['surface']}'.",
                        {
                            'verb': head['surface'],
                            'verb_span': head['span'],
                            'expected_preposition': expected,
                            'observed_preposition': prep['surface'],
                        },
                        f"replace '{prep['surface']}' with '{expected}'",
                    ))

        # (a2) redundant preposition (``discuss about``).
        if base in REDUNDANT_PREPOSITION:
            banned = REDUNDANT_PREPOSITION[base]
            for child in children:
                if child['type'] != 'PP':
                    continue
                prep = _first_prep(child)
                if prep is not None and prep['surface'].lower() in banned:
                    findings.append(_finding(
                        'R11.2', 'S-PREPOSITION', 'redundant preposition',
                        f"Redundant preposition: '{head['surface']}' takes a "
                        f"direct object, so '{prep['surface']}' must be "
                        f"dropped.",
                        {
                            'verb': head['surface'],
                            'verb_span': head['span'],
                            'redundant_preposition': prep['surface'],
                        },
                        f"delete '{prep['surface']}' after "
                        f"'{head['surface']}'",
                    ))

        # (a3) missing required preposition (``listen music``).
        if base in OBJECT_PREPOSITION_VERBS:
            required = OBJECT_PREPOSITION_VERBS[base]
            obj = next((c for c in children if c['type'] == 'NP'), None)
            has_required = any(
                child['type'] == 'PP'
                and (p := _first_prep(child)) is not None
                and p['surface'].lower() == required
                for child in children
            )
            if obj is not None and not has_required:
                findings.append(_finding(
                    'R11.2', 'S-PREPOSITION', 'missing preposition',
                    f"Missing preposition: '{head['surface']}' requires "
                    f"'{required}' before its object '{obj['surface']}'.",
                    {
                        'verb': head['surface'],
                        'verb_span': head['span'],
                        'required_preposition': required,
                        'object': obj['surface'],
                    },
                    f"insert '{required}' after '{head['surface']}'",
                ))

        # (b) light-verb collocations: ``do``/``make`` + object noun.  ``have``
        #     and ``take`` are deliberately *not* flagged: they freely substitute
        #     for the canonical light verb ("have a plan", "take a break"), so
        #     treating them as errors would be a false positive.  Perfect /
        #     progressive / passive VPs are not collocation contexts.
        if (base in ('make', 'do')
                and not any(l['type'] in ('VBG', 'VBN') for l in leaves)):
            obj = next((c for c in children if c['type'] == 'NP'), None)
            if obj is not None:
                obj_head = _np_head(obj)
                if obj_head is not None:
                    noun = obj_head['surface'].lower()
                    noun_sing = _singular_noun(obj_head).lower()
                    expected_verb = LIGHT_VERB_NOUN.get(
                        noun, LIGHT_VERB_NOUN.get(noun_sing)
                    )
                    if expected_verb is not None and expected_verb != base:
                        findings.append(_finding(
                            'R11.2', 'S-COLLOCATION', 'collocation',
                            f"Light-verb collocation: '{base} "
                            f"{obj['surface']}' does not collocate; the noun "
                            f"'{noun}' takes '{expected_verb}'.",
                            {
                                'verb': base,
                                'verb_span': head['span'],
                                'object': noun,
                                'expected_verb': expected_verb,
                            },
                            f"use '{expected_verb}' instead of '{base}'",
                        ))


# ── R11.3  tense–time agreement ────────────────────────────────────────────

# A deictic temporal anchor and the predicate it clashes with must belong to the
# same clause, so the tense–time check is evaluated per clause.  This replaces
# the earlier "any habitual marker anywhere suppresses the whole sentence"
# rule, which let a frequency adverb in a *subordinate* clause hide a genuine
# mismatch in the main clause (and vice-versa).  Genericity is now signalled
# structurally: a clause with no deictic anchor is simply never flagged.
_CLAUSE_TYPES = frozenset({'S'})            # clauses this rule inspects
_CLAUSE_BARRIERS = frozenset({'S', 'SINV', 'SQ', 'SBARQ', 'SBAR'})


def _clause_local_nodes(clause):
    """Depth-first walk of ``clause`` that never descends into a nested clause.

    A nested clause (subordinate/complement/relative ``S``, or a coordinated
    clause) is inspected on its own, so a time word or frequency adverb inside
    it can neither suppress nor invent a finding in the enclosing clause.
    """
    for child in clause.get('children', []):
        if 'children' in child and child['type'] in _CLAUSE_BARRIERS:
            continue
        yield child
        if 'children' in child:
            yield from _clause_local_nodes(child)


def _temporal_markers(clause):
    """Return ``[(polarity, node)]`` for anchors *local* to ``clause``."""
    markers = []
    for node in _clause_local_nodes(clause):
        if 'children' in node:
            if node['type'] == 'NP':
                m = _TIME_PATTERN.match(node['surface'].lower())
                if m and m.group(2) in _TIME_NOUNS:
                    markers.append(
                        ('past' if m.group(1) == 'last' else 'future', node)
                    )
            continue
        word = node['surface'].lower()
        if word in PAST_TIME_WORDS:
            markers.append(('past', node))
        elif word in FUTURE_TIME_WORDS:
            markers.append(('future', node))
        elif word in PRESENT_TIME_WORDS:
            markers.append(('present', node))
    return markers


def _clause_tense(vp):
    """Past / present / future (or None) reading of a VP."""
    leaves = _leaves_list(vp)
    words = {l['surface'].lower() for l in leaves}
    if words & {'will', 'shall'}:
        return 'future'
    if words & {'was', 'were', 'had'}:
        return 'past'
    if words & {'am', 'is', 'are', 'has', 'have'}:
        return 'present'
    head = _main_verb_leaf(vp)
    if head is not None:
        if head['type'] == 'VBD':
            return 'past'
        if head['type'] in ('VBP', 'VBZ', 'VB'):
            return 'present'
    return None


# polarity → tenses it clashes with
_TENSE_CLASH = {
    'past': ('present', 'future'),
    'future': ('past',),
    'present': ('past',),
}


def _check_tense_time(root, findings):
    """Clause-scoped tense–time agreement (R11.3).

    Every ``S`` clause is checked independently.  A predicate with no tense
    (non-finite or verbless clause) is skipped, and a clause with no deictic
    temporal anchor is skipped — so generic/habitual sentences such as
    ``The children play in the park every day`` never fire.  When an anchor and
    the predicate it clashes with *are* in the same clause the mismatch is
    reported, regardless of any frequency adverb elsewhere in the sentence.
    """
    for clause, _ in _walk(root):
        if clause['type'] not in _CLAUSE_TYPES:
            continue
        vp = _clause_vp(clause)
        if vp is None:
            continue
        tense = _clause_tense(vp)
        if tense is None:
            continue
        for polarity, node in _temporal_markers(clause):
            if tense not in _TENSE_CLASH.get(polarity, ()):  # noqa: SIM118
                continue
            label = {'past': 'past-time', 'future': 'future-time',
                     'present': 'present-time'}[polarity]
            required = {'past': 'past-tense', 'future': 'future-tense',
                        'present': 'present-tense'}[polarity]
            findings.append(_finding(
                'R11.3', 'S-TENSE-TIME', 'tense–time agreement',
                f"Tense–time mismatch: the {label} word '{node['surface']}' is "
                f"incompatible with a {tense} predicate ('{vp['surface']}').",
                {
                    'time_word': node['surface'],
                    'time_span': node['span'],
                    'clause_tense': tense,
                    'predicate': vp['surface'],
                },
                f"use a {required} predicate to match '{node['surface']}'",
            ))


# ── R11.4  entity classification & selectional restrictions ────────────────

def _nominal_head_lemma(np_node):
    """Singular lemma of an argument NP, or None when it is a pronoun / proper
    noun / headless (those have no *lexical* lemma; classification for them is
    handled separately by :func:`_np_entity_class`)."""
    head = _np_head(np_node)
    if head is None or head['type'] in ('PRP', 'NNP', 'NNPS'):
        return None
    return _singular_noun(head).lower()


def _explicit_class(lemma):
    """Entity class of a lemma from the explicit project lexicons only."""
    if lemma in ANIMATE_NOUNS:
        return 'animate'
    if lemma in ABSTRACT_NOUNS:
        return 'abstract'
    if lemma in INANIMATE_OBJECTS:
        return 'inanimate'
    if lemma in EDIBLE_NOUNS or lemma in DRINKABLE_NOUNS:
        return 'inanimate'
    return None


def _entity_class(lemma):
    """Entity class of a common-noun lemma, or ``None`` when unclassified.

    Precedence: explicit project lexicons (highest confidence) → optional,
    deterministic WordNet fallback (:mod:`server.lexicon`) → ``None``.

    ``None`` means "no available evidence establishes a class".  It is
    deliberately *not* collapsed into "inanimate": an unclassified noun never
    supports a finding, which keeps the lexicons open-world and avoids turning
    every unknown word into a semantic error.
    """
    if lemma is None:
        return None
    return _explicit_class(lemma) or lexicon.wordnet_class(lemma)


# Backwards-compatible alias (documented as the subject-class helper).
_subject_class = _entity_class


def _known_entity(lemma):
    """True when an *explicit* lexicon establishes the noun's entity class.

    Object compatibility uses the explicit closed whitelists only: the
    ``read``/``write``/``wear`` object sets are not exhaustive, so an object
    that merely has a WordNet class (e.g. ``software``) must not be turned into
    a definitive selectional error.
    """
    return _explicit_class(lemma) is not None


def _person_entity(head, tokens):
    """True when the token at ``head`` is part of a spaCy ``PERSON`` entity."""
    if not tokens:
        return False
    start = head['span'][0]
    for tok in tokens:
        if tok.get('i') == start:
            return (tok.get('ent') or '').upper() == 'PERSON'
    return False


def _np_entity_class(np_node, tokens=None):
    """Entity class of an argument NP from all available evidence.

    * common noun → explicit lexicon then WordNet;
    * personal pronoun → the conservative feature table (:mod:`server.lexicon`);
    * proper noun → a spaCy ``PERSON`` named entity marks it animate; any other
      proper noun stays unclassified (a name may denote anything, so it is
      never assumed inanimate);
    * anything else → ``None``.
    """
    head = _np_head(np_node)
    if head is None:
        return None
    if head['type'] in ('PRP', 'PRP$'):
        return lexicon.pronoun_class(head['surface'])
    if head['type'] in ('NNP', 'NNPS'):
        return 'animate' if _person_entity(head, tokens) else None
    lemma = _nominal_head_lemma(np_node)
    if lemma is None:
        return None
    return _entity_class(lemma)


def _check_selectional(root, findings, tokens=None):
    """Animate-subject / class-appropriate-object checks for a closed set of
    consumption & action verbs (``eat, drink, read, write, wear, kill``)."""
    s_node = root if root['type'] == 'S' else None
    if s_node is None:
        return
    vp = _clause_vp(s_node)
    if vp is None:
        return
    head = _main_verb_leaf(vp)
    if head is None or head['type'] in ('VBG', 'VBN'):
        return                                   # progressive / passive
    base = _verb_base(head)
    if base not in AGENTIVE_ACTION_VERBS:
        return

    # (1) subject must be animate — but only when its class is *known*.
    subj = _subject_of(s_node, vp)
    if subj is not None:
        subj_head = _np_head(subj)
        subj_class = _np_entity_class(subj, tokens)
        if subj_class in ('inanimate', 'abstract'):
            subj_lemma = _nominal_head_lemma(subj)
            noun = subj_lemma or (subj_head['surface'] if subj_head else '?')
            findings.append(_finding(
                'R11.4', 'S-SELECTIONAL', 'selectional restriction',
                f"Selectional restriction: '{subj['surface']}' is not "
                f"animate, but '{head['surface']}' requires an animate "
                f"subject/agent.",
                {
                    'role': 'subject',
                    'subject': subj_head['surface'] if subj_head else '?',
                    'noun': noun,
                    'verb': head['surface'],
                    'verb_span': head['span'],
                },
                f"use an animate agent as the subject of "
                f"'{head['surface']}'",
            ))

    # (2) object must belong to the verb's expected class
    class_name, allowed = _OBJECT_CLASS[base]
    obj = next((c for c in vp.get('children', []) if c['type'] == 'NP'), None)
    if obj is None:
        return
    obj_head = _np_head(obj)
    obj_lemma = _nominal_head_lemma(obj)
    if obj_lemma is None:
        return
    if obj_lemma in allowed:
        return
    if base == 'kill' and obj_lemma == 'time':       # idiom ``kill time``
        return
    if not _known_entity(obj_lemma):
        return                       # unclassified noun: no unsupported finding
    findings.append(_finding(
        'R11.4', 'S-SELECTIONAL', 'selectional restriction',
        f"Selectional restriction: '{obj_head['surface']}' cannot be the "
        f"object of '{head['surface']}' (expected {class_name}).",
        {
            'role': 'object',
            'object': obj_head['surface'],
            'noun': obj_lemma,
            'verb': head['surface'],
            'verb_span': head['span'],
            'expected_class': class_name,
        },
        f"use {'an' if class_name[0] in 'aeiou' else 'a'} {class_name} "
        f"object with '{head['surface']}'",
    ))


# ── R11.6  subject–predicate semantic compatibility ─────────────────────────

def _is_copula(leaf):
    """True when a verb leaf is a copular/linking verb (it may take a
    predicate adjective)."""
    surface = leaf['surface'].lower()
    if surface in LINKING_VERBS or surface in ('be', 'been', 'being'):
        return True
    return _verb_base(leaf) in LINKING_VERBS


def _vp_copula(vp_node):
    """The copular/linking leaf of a VP, or None.

    Scanning the leaves (rather than only ``_main_verb_leaf``) keeps predicate
    checks working when the predicate contains a second, non-finite verb — e.g.
    ``is hungry and starving``, whose last verb leaf is a ``VBG``.
    """
    return next((lf for lf in _leaves_list(vp_node) if _is_copula(lf)), None)


# A predicative state can surface as an adjective (``is hungry``) or as a
# participle that the POS tagger treats as a verb (``is starving`` VBG,
# ``is exhausted`` VBN).  Only participles whose lemma is in the biological
# taxonomy are collected, so ordinary passives are unaffected.
_PREDICATIVE_VERB_TAGS = ('VBG', 'VBN')


def _predicate_adjectives(vp_node):
    """State leaves of the predicates that are direct VP children.

    Collects ``JJ``/``JJR``/``JJS`` leaves of an ``ADJP`` predicate, plus the
    small set of biological-state ``VBG`` participles (``starving``) whether
    they occur inside an ``ADJP`` (``hungry and starving``) or as the head of a
    dependent ``VP`` (``is starving``).
    """
    out = []
    for child in vp_node.get('children', []):
        if child['type'] == 'ADJP':
            out.extend(lf for lf in _leaves_list(child)
                       if lf['type'] in ('JJ', 'JJR', 'JJS')
                       or (lf['type'] in _PREDICATIVE_VERB_TAGS
                           and lf['surface'].lower()
                           in BIOLOGICAL_STATE_ADJECTIVES))
        elif child['type'] == 'VP':
            out.extend(lf for lf in _leaves_list(child)
                       if lf['type'] in _PREDICATIVE_VERB_TAGS
                       and lf['surface'].lower() in BIOLOGICAL_STATE_ADJECTIVES)
    return out


def _biological_subclass(surface):
    """The biological-state subclass of an adjective surface, or ``None``."""
    surface = (surface or '').lower()
    if surface in PHYSIOLOGICAL_STATE_ADJECTIVES:
        return 'physiological'
    if surface in LIFE_STATE_ADJECTIVES:
        return 'life'
    return None


# subclass -> entity classes that make a *literal* reading anomalous.
#   physiological needs an animate agent: abstracts and artifacts are anomalous,
#     but a merely 'living' organism (a plant) is not flagged — "a thirsty
#     plant" is a normal idiomatic usage.
#   life/death needs a living entity: only abstracts are anomalous; artifacts
#     are exempt because life-state words idiomatically apply to them ("a dead
#     battery"), and living/animate subjects are fine.
_BIOLOGICAL_INCOMPATIBLE = {
    'physiological': frozenset({'abstract', 'inanimate'}),
    'life': frozenset({'abstract'}),
}


def _check_subject_predicate(root, findings, tokens=None):
    """Advisory (R11.6) compatibility check for ``<subject> is <state>``.

    Reports a *warning* — never a syntax error — when a biological-state
    predicate adjective is applied to a subject whose entity class makes a
    *literal* reading anomalous.  The message is framed as an anomaly "under a
    literal interpretation" and points at a possible figurative/fictional
    (personified) reading; it never claims the sentence is objectively
    meaningless or ungrammatical.

    The subject's class may come from an explicit lexicon, the WordNet
    fallback, a conservative pronoun table, or spaCy ``PERSON`` NER.  Subjects
    with no established class are left untouched, as is every adjective outside
    the biological-state taxonomy.  At most one finding is emitted per
    (clause, subclass), so ``hungry`` and ``starving`` in the same clause do not
    produce redundant findings for the same underlying issue.
    """
    s_node = root if root['type'] == 'S' else None
    if s_node is None:
        return
    vp = _clause_vp(s_node)
    if vp is None:
        return
    head = _main_verb_leaf(vp)
    if head is None or _vp_copula(vp) is None:
        return
    subj = _subject_of(s_node, vp)
    if subj is None:
        return
    subj_head = _np_head(subj)
    subj_class = _np_entity_class(subj, tokens)
    if subj_class is None:
        return

    # Group the predicate adjectives by biological subclass, preserving the
    # left-to-right surface order and de-duplicating repeated words.
    grouped = {}
    for adj in _predicate_adjectives(vp):
        sub = _biological_subclass(adj['surface'])
        if sub is None:
            continue
        bucket = grouped.setdefault(sub, [])
        if all(a['surface'].lower() != adj['surface'].lower() for a in bucket):
            bucket.append(adj)

    for sub, adjs in grouped.items():
        if subj_class not in _BIOLOGICAL_INCOMPATIBLE[sub]:
            continue
        klass = 'abstract' if subj_class == 'abstract' else 'non-living'
        article = 'an' if klass == 'abstract' else 'a'
        surfaces = [a['surface'] for a in adjs]
        listed = ', '.join(f"'{s}'" for s in surfaces)
        required = 'animate' if sub == 'physiological' else 'living'
        descr = ('a biological/physiological state' if sub == 'physiological'
                 else 'a life/death state')
        findings.append(_finding(
            'R11.6', 'S-PREDICATE-COMPAT', 'subject–predicate compatibility',
            f"Anomalous under a literal interpretation: '{subj['surface']}' "
            f"denotes {article} {klass} entity, but the predicate '{vp['surface']}' "
            f"describes {descr} ({listed}) that requires a living, "
            f"{'animate' if required == 'animate' else 'animate-or-living'} "
            'subject.',
            {
                'subject': subj['surface'],
                'subject_head': subj_head['surface'] if subj_head else subj_class,
                'subject_class': subj_class,
                'predicate': vp['surface'],
                'adjective': surfaces[0],
                'adjectives': surfaces,
                'subclass': sub,
                'required_class': required,
                'rule': f"biological-state ({sub}) predicate requires an "
                        f"{'animate' if required == 'animate' else 'living'} "
                        'subject',
            },
            'if a literal reading is intended, use an animate subject; '
            'otherwise the sentence may be intended figuratively or fictionally '
            '(personification)',
            status='warning',
        ))


# ── R11.5  PP-attachment ambiguity ──────────────────────────────────────────

def structure_fingerprint(node):
    """Deterministic structural serialization (type + spans + leaf order)."""
    if 'children' not in node:
        return f"{node['type']}:{node['surface']}"
    inner = ','.join(structure_fingerprint(c) for c in node['children'])
    return f"({node['type']};{node['span'][0]}-{node['span'][1]}[{inner}])"


def _recompute(node):
    """Bottom-up repair of ``span`` and ``surface`` after re-parenting."""
    if 'children' not in node:
        return node['surface']
    surfaces = [_recompute(c) for c in node['children']]
    node['span'] = [node['children'][0]['span'][0],
                    node['children'][-1]['span'][1]]
    node['surface'] = ' '.join(surfaces)
    return node['surface']


def _relocate(root, pp_id, from_id, to_id, after_id):
    """Deep-copy ``root`` and move the PP ``pp_id`` from ``from_id`` to
    ``to_id`` (after ``after_id`` when given), then repair spans/surfaces."""
    tree = copy.deepcopy(root)
    nodes = _by_id(tree)
    pp = nodes[pp_id]
    src = nodes[from_id]
    dst = nodes[to_id]
    src['children'] = [c for c in src['children'] if c['id'] != pp_id]
    if after_id is None:
        dst['children'].append(pp)
    else:
        idx = next((i for i, c in enumerate(dst['children'])
                    if c['id'] == after_id), len(dst['children']) - 1)
        dst['children'].insert(idx + 1, pp)
    _recompute(tree)
    return tree


def _find_pp_attachment(root):
    """Locate the first object-NP/PP pair whose attachment is ambiguous.

    Returns ``{vp, np, pp, default}`` where ``default`` is ``'VP'`` when the
    parser put the PP on the verb phrase, else ``'NP'``.
    """
    for node, _ in _walk(root):
        if node['type'] != 'VP':
            continue
        children = node.get('children', [])
        for i, child in enumerate(children):
            if (child['type'] == 'PP' and i > 0
                    and children[i - 1]['type'] == 'NP'):
                return {'vp': node, 'np': children[i - 1], 'pp': child,
                        'default': 'VP'}
        for child in children:
            if child['type'] != 'NP':
                continue
            grand = child.get('children', [])
            if len(grand) > 1 and grand[-1]['type'] == 'PP':
                return {'vp': node, 'np': child, 'pp': grand[-1],
                        'default': 'NP'}
    return None


def _node_details(tree, pp_id, pp_role, pp_note):
    details = {}
    for node, parent in _walk(tree):
        is_pp = node['id'] == pp_id
        if is_pp:
            role, note = pp_role, pp_note
        elif 'children' in node:
            role, note = _ROLE_BY_TYPE.get(node['type'], node['type']), None
        else:
            role, note = 'token', None
        details[node['id']] = {
            'id': node['id'],
            'type': node['type'],
            'surface': node['surface'],
            'span': list(node['span']),
            'parent': parent['id'] if parent is not None else None,
            'role': role,
            'note': note,
        }
    return details


def _pp_reading(built_tree, pp_id, label, paraphrase, roles,
                pp_role, pp_note):
    return {
        'label': label,
        'paraphrase': paraphrase,
        'thematic_roles': roles,
        'tree': built_tree,
        'node_details': _node_details(built_tree, pp_id, pp_role, pp_note),
    }


def _pp_preposition(pp_node):
    prep = _first_prep(pp_node)
    return prep['surface'].lower() if prep is not None else ''


def _pp_readings(prep, subject, verb_surface, verb_base, obj_surface,
                 pp_obj_surface, pp_surface):
    """Candidate ``(vp_reading, np_reading)`` interpretations for a PP.

    The interpretations are hedged *candidates*, never assertions: which one is
    intended depends on the preposition and on world knowledge the deterministic
    parser does not model.  Exactly two primary readings are produced — one
    adjunct (verb-phrase) reading and one modifier (noun-phrase) reading — for
    the prepositions the system models:

    * ``with``      → instrument / accompaniment (VP) vs. possession (NP);
    * ``in``/``at``/``on`` → location / setting (VP) vs. location (NP);
    * ``for``       → purpose / beneficiary (VP) vs. purpose (NP);
    * anything else → neutral candidate wording (no interpretation claimed).

    Returns two dicts with ``label``, ``paraphrase``, ``roles``, ``pp_role`` and
    ``pp_note`` keys; the label text is stable so the UI pills stay fixed.
    """
    subj = subject or 'the subject'
    obj_surface = obj_surface or ''
    ref = f"'{pp_obj_surface}'"
    # After a modal "may" the verb must be in its base form.
    vb = verb_base or verb_surface
    # The NP reading's Theme combines the object with its postmodifying PP. Build
    # it defensively: never leave a trailing space, and never re-append a PP the
    # object surface already ends with (which would duplicate the phrase).
    theme = obj_surface
    if pp_surface and not theme.endswith(pp_surface):
        theme = f'{theme} {pp_surface}'.strip()
    vp = {
        'label': 'Verb-phrase reading',
        'paraphrase': '',
        'roles': {'Agent': subject, 'Action': verb_surface,
                  'Patient': obj_surface},
        'pp_role': 'VP adjunct',
        'pp_note': '',
    }
    np = {
        'label': 'Noun-phrase reading',
        'paraphrase': '',
        'roles': {'Agent': subject, 'Action': verb_surface,
                  'Theme': theme},
        'pp_role': 'NP postmodifier',
        'pp_note': '',
    }

    if prep == 'with':
        vp['label'] = 'Verb-phrase reading — instrument / accompaniment'
        vp['paraphrase'] = (
            f"One candidate reading: the PP is an adjunct of the verb. It may "
            f"name the instrument — {subj} may use {ref} to {vb} "
            f"{obj_surface} — or the accompaniment — {subj} may "
            f"{vb} {obj_surface} together with {ref}."
        )
        vp['pp_role'] = 'VP adjunct (instrument / accompaniment)'
        vp['pp_note'] = (
            'The PP attaches to the verb phrase. Whether it is an instrument or '
            'an accompanier depends on the verb and on context the parser does '
            'not model.'
        )
        vp['roles']['Instrument_or_Accompaniment'] = pp_surface
        np['label'] = 'Noun-phrase reading — possession / attribute'
        np['paraphrase'] = (
            f"Another candidate reading: the PP modifies the preceding noun. It "
            f"may describe a property — {obj_surface} that is with / has "
            f"{ref} — rather than the action."
        )
        np['pp_role'] = 'NP postmodifier (possession / attribute)'
        np['pp_note'] = (
            'The PP attaches to the noun phrase; it then describes the object '
            'rather than the action.'
        )
    elif prep in ('in', 'at', 'on'):
        vp['label'] = 'Verb-phrase reading — location / setting of the action'
        vp['paraphrase'] = (
            f"One candidate reading: the PP is an adjunct of the verb and "
            f"locates the action — {subj} may {vb} {obj_surface} "
            f"{pp_surface}."
        )
        vp['pp_role'] = 'VP adjunct (location / setting)'
        vp['pp_note'] = (
            'The PP attaches to the verb phrase; it then gives the place or '
            'setting in which the action happens.'
        )
        vp['roles']['Location'] = pp_surface
        np['label'] = 'Noun-phrase reading — location of the object'
        np['paraphrase'] = (
            f"Another candidate reading: the PP modifies the preceding noun and "
            f"locates the object — {obj_surface} that is {pp_surface}."
        )
        np['pp_role'] = 'NP postmodifier (location)'
        np['pp_note'] = (
            'The PP attaches to the noun phrase; it then gives the location of '
            'the object rather than of the action.'
        )
    elif prep == 'for':
        vp['label'] = 'Verb-phrase reading — purpose / beneficiary'
        vp['paraphrase'] = (
            f"One candidate reading: the PP is an adjunct of the verb and "
            f"states a purpose or beneficiary — {subj} may {vb} "
            f"{obj_surface} for {ref}."
        )
        vp['pp_role'] = 'VP adjunct (purpose / beneficiary)'
        vp['pp_note'] = (
            'The PP attaches to the verb phrase; it then gives the purpose of '
            'the action or the person/thing it benefits.'
        )
        vp['roles']['Purpose_or_Beneficiary'] = pp_surface
        np['label'] = 'Noun-phrase reading — intended for / attributed to'
        np['paraphrase'] = (
            f"Another candidate reading: the PP modifies the preceding noun — "
            f"{obj_surface} that is intended for {ref}."
        )
        np['pp_role'] = 'NP postmodifier (purpose / beneficiary)'
        np['pp_note'] = (
            'The PP attaches to the noun phrase; it then describes the object.'
        )
    else:
        vp['paraphrase'] = (
            f"One candidate reading: the PP may be an adjunct of the verb — "
            f"{subj} may {vb} {obj_surface} {pp_surface}."
        )
        vp['pp_role'] = 'VP adjunct'
        vp['pp_note'] = (
            'The PP could attach to the verb phrase, but the interpretation '
            'depends on the preposition and on context the parser does not model.'
        )
        np['paraphrase'] = (
            f"Another candidate reading: the PP may modify the preceding noun — "
            f"{obj_surface} {pp_surface}."
        )
        np['pp_role'] = 'NP postmodifier'
        np['pp_note'] = (
            'The PP could attach to the noun phrase; the intended reading is not '
            'determinable from the parse alone.'
        )
    return vp, np


def _pp_ambiguity(root):
    """Build the R11.5 ambiguity object for ``root`` (or a null result).

    The object always carries exactly **two** primary readings (a VP-adjunct and
    an NP-modifier candidate) and a ``scope`` note stating that the comparison is
    not exhaustive.  The original tree is never mutated.
    """
    found = _find_pp_attachment(root)
    if found is None:
        return {'ambiguous': False, 'readings': [], 'tree_variants': []}

    vp, np_node, pp = found['vp'], found['np'], found['pp']
    default = found['default']

    # Both readings as deep copies (the original tree is never mutated).
    if default == 'VP':
        vp_tree = copy.deepcopy(root)
        np_tree = _relocate(root, pp['id'], vp['id'], np_node['id'], None)
    else:
        vp_tree = _relocate(root, pp['id'], np_node['id'], vp['id'],
                            np_node['id'])
        np_tree = copy.deepcopy(root)

    # Reuse the parser's own strings for the paraphrase / roles.
    s_node = root if root['type'] == 'S' else None
    subject = ''
    if s_node is not None:
        subj_np = _subject_of(s_node, _clause_vp(s_node))
        if subj_np is not None:
            subject = subj_np['surface']
    verb_leaf = _main_verb_leaf(vp)
    verb_surface = verb_leaf['surface'] if verb_leaf is not None else ''
    verb_base = _verb_base(verb_leaf) if verb_leaf is not None else ''
    obj_surface = np_node['surface']
    pp_surface = pp['surface']
    pp_obj = next((c for c in pp.get('children', []) if c['type'] == 'NP'),
                  None)
    pp_obj_surface = pp_obj['surface'] if pp_obj is not None else pp_surface
    prep = _pp_preposition(pp)

    readings = _pp_readings(prep, subject, verb_surface, verb_base,
                            obj_surface, pp_obj_surface, pp_surface)
    vp_desc, np_desc = readings
    vp_reading = _pp_reading(
        vp_tree, pp['id'], vp_desc['label'], vp_desc['paraphrase'],
        vp_desc['roles'], vp_desc['pp_role'], vp_desc['pp_note'],
    )
    np_reading = _pp_reading(
        np_tree, pp['id'], np_desc['label'], np_desc['paraphrase'],
        np_desc['roles'], np_desc['pp_role'], np_desc['pp_note'],
    )

    if default == 'VP':
        legacy = {'attachment': 'NP-attached', 'root': np_tree,
                  'pp': pp_surface, 'np': obj_surface}
    else:
        legacy = {'attachment': 'VP-attached', 'root': vp_tree,
                  'pp': pp_surface, 'np': obj_surface}

    return {
        'ambiguous': True,
        'readings': [vp_reading, np_reading],
        'tree_variants': [legacy],
        'preposition': prep,
        'scope': ('Two primary readings are compared — a verb-phrase (adjunct) '
                  'reading and a noun-phrase (modifier) reading. This is not an '
                  'exhaustive list of every possible analysis; the readings are '
                  'candidates, not assertions.'),
    }


# ── public entry point ──────────────────────────────────────────────────────

def analyze_semantics(analysis, matrix_result):
    """Run the deterministic semantic layer over one parse.

    Parameters
    ----------
    analysis : dict
        Output of ``parse_engine.analyze`` (``root``, ``nodes``, ``tokens``).
    matrix_result : dict
        Output of ``matrix.evaluate`` (``details``, ``summary``).  Read-only.

    Returns
    -------
    dict
        ``{status, available, findings, ambiguous, ambiguity, tree_variants,
        summary}`` with ``status='ok'``.  The original tree and matrix result are
        never mutated (Gate 1).
    """
    root = analysis['root']
    tokens = analysis.get('tokens')
    findings = []
    _check_collocations(root, findings)
    _check_tense_time(root, findings)
    _check_selectional(root, findings, tokens)
    _check_subject_predicate(root, findings, tokens)
    ambiguity = _pp_ambiguity(root)

    fired = sorted({f['constraint'] for f in findings})
    summary = {
        'status': 'ok',
        'available': True,
        'valid': not findings,
        'findings': len(findings),
        'errors': sum(1 for f in findings if f['status'] == 'error'),
        'warnings': sum(1 for f in findings if f['status'] == 'warning'),
        'constraints_fired': fired,
        'ambiguous_attachments': (
            [v['attachment'] for v in ambiguity['tree_variants']]
        ),
        'tree_variants': len(ambiguity['tree_variants']),
        'explanation': (
            'no semantic finding' if not findings
            else '; '.join(f['constraint'] for f in findings)
        ),
    }
    return {
        'status': 'ok',
        'available': True,
        'findings': findings,
        'ambiguous': ambiguity['ambiguous'],
        'ambiguity': ambiguity,
        'tree_variants': ambiguity['tree_variants'],
        'summary': summary,
    }
