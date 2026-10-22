"""SynTutor Stage 5: deterministic Linguistic Constraint Matrix (XAI).

Every parent/child edge E(v_d, v_p) is validated against a hand-authored rule
matrix. A rule fires on a POS-class pair (parent, child) and returns a verdict:

    valid    -> the dependency is licensed by rule R
    error    -> a specific violation, identified by constraint id C-*
    unlisted -> the pair is not captured by the matrix (valid-by-default)

Agreement, auxiliary-form, tense/finiteness, determiner-number, modifier-order
and determiner-stacking checks are deterministic feature functions over the
Penn-style POS tags produced by benepar -- no machine-learned scoring is
involved. Noun-form validation uses the deterministic ``inflect`` library,
which is a required backend dependency. The same input always yields the same
verdict.
"""

import inflect
import re

try:  # optional: provides exhaustive irregular verb inflection
    from lemminflect import getInflection as _get_inflection
except Exception:  # pragma: no cover
    _get_inflection = None

_DIRE_START = re.compile(
    r'^(?:so\s+)?(?:write|use|change|replace|add|remove|drop|capitalize|move|'
    r'keep|put|choose|correct|make|spell)\b', re.I)

# A directive that names no concrete corrected form is not a usable fix; when a
# rule text reaches us with one of these, the corrected form is read out of the
# description instead of being passed through verbatim.
_VAGUE_FIX = re.compile(
    r"(word form the sentence needs|you really mean|sentence really needs|"
    r"^keep only one|remove the repetition|move it closer|add the subject that|"
    r"only one negation|needs a preposition instead|object should follow the verb|"
    r"move the describing phrase)",
    re.I)

try:  # works both as ``server.matrix`` (package) and ``matrix`` (script dir)
    from . import ruleset
    try:
        from . import licensing
    except Exception:  # lemminflect missing -> degrade to rules-only
        licensing = None
    try:
        from . import master
    except Exception:
        master = None
except ImportError:  # pragma: no cover
    import ruleset
    try:
        import licensing
    except Exception:
        licensing = None
    try:
        import master
    except Exception:
        master = None

SENTENCE_CLASSES = {'S', 'SINV', 'SQ', 'SBARQ', 'FRAG', 'ROOT'}

NOUN_CLASS = {'NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'NML', 'NX'}
COLLECTIVE_NOUNS = {
    'team', 'staff', 'government', 'family', 'committee', 'group', 'audience',
    'public', 'class', 'crew', 'jury', 'company', 'band', 'crowd',
}
VERB_CLASS = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'AUX'}
ADJ_CLASS = {'JJ', 'JJR', 'JJS'}
ADV_CLASS = {'RB', 'RBR', 'RBS'}
DET_CLASS = {'DT'}
PREP_CLASS = {'IN', 'TO', 'POS', 'RP'}

NOUN_PLURAL = {'NNS', 'NNPS'}
NOUN_PLURAL_SET = {'police','people','children','men','women','feet','teeth','mice','data','cattle'}
NOUN_SINGULAR = {'NN', 'NNP', 'NML', 'NX'}

PRP_KEY = {
    'i': ('1', 'sg'), 'we': ('1', 'pl'), 'you': ('2', None),
    'he': ('3', 'sg'), 'she': ('3', 'sg'), 'it': ('3', 'sg'),
    'they': ('3', 'pl'),
}
DET_NUMREQ = {
    'a': 'sg', 'an': 'sg', 'one': 'sg', 'this': 'sg', 'that': 'sg',
    'each': 'sg', 'every': 'sg', 'another': 'sg', 'much': 'sg',
    'these': 'pl', 'those': 'pl', 'both': 'pl', 'many': 'pl', 'several': 'pl',
}
MODALS = {'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must'}
# After 'a', these quantifier adjectives pass the article's number to a later
# head: "a few boxes", "a dozen eggs", "a couple of chairs".
QUANT_AFTER_A = {'few', 'little', 'dozen', 'couple', 'lot', 'number', 'good',
                 'great'}
BE_FORM = {'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
HAVE_FORM = {'have', 'has', 'had', 'having'}
DO_FORM = {'do', 'does', 'did', 'doing', 'done'}

# The tokenizer splits contractions into clitic tokens ("I'm tired" -> "'m").
# Map each back to the auxiliary class it belongs to so copular / perfect /
# modal checks treat them like the full forms.
def _clitic_core(surface):
    s = surface.replace('\u2019', "'").lower()
    if s == "'m":
        return 'be'
    if s in {"'re", "'s"}:
        # "'s" is '"is" (bare is also "has", e.g. "he's gone")
        return 'be'
    if s == "'ve":
        return 'have'
    if s == "'ll" or s == "'d":
        return 'modal'
    return None


CLITIC_SURFACES = {"'m", "'re", "'s", "'ve", "'ll", "'d"}

# Possessive determiners that can never head an NP (unlike the standalone
# possessive pronouns 'mine/yours/ours/theirs/hers/his').
POSS_DET_PLAIN = {'my', 'your', 'our', 'their', 'its'}
# Ambiguous surfaces excluded from POSS_DET_PLAIN on purpose:
#   'her' | 'his'  -- also standalone possessive pronouns / object pronoun

# Determinatives that double as standalone (anaphoric) pronoun heads of an NP:
# "This is good.", "These are mine.", "Each is important."
DEMONSTRATIVE_STANDALONE = {'this', 'that', 'these', 'those',
                            'each', 'some', 'one', 'all', 'several', 'any',
                            'either', 'neither', 'another', 'many',
                            'much', 'more', 'most', 'less', 'few', 'little',
                            'both', 'half', 'enough', 'plenty'}

PRON_SUBJ_PLAIN = {'i', 'we', 'he', 'she', 'they'}
PRONOUN_SURFACES = {
    'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours', 'you', 'your',
    'yours', 'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its',
    'they', 'them', 'their', 'theirs', 'myself', 'yourself', 'himself',
    'herself', 'itself', 'ourselves', 'yourselves', 'themselves',
}
PRON_OBJ_PLAIN = {'me', 'us', 'him', 'her', 'them'}

# Adjectives that legitimately follow a verb / copula without an -ly form
# (fixed predicate adjectives and idiomatic flat adverbs): 'was closed',
# 'went wrong', 'next to X', 'came late', 'is open/out'.
PRED_ADJ_EXEMPT = {'next', 'out', 'open', 'wrong', 'late', 'closed', 'lit',
                   'well', 'ill', 'alone', 'alive', 'awake', 'asleep',
                   'afraid', 'ready', 'sure', 'gone', 'far', 'full'}

# Possessive pronouns that the parser may tag as singular nouns.
POSS_PRON_SURFACES = {'mine', 'yours', 'hers', 'ours', 'theirs'}

# Words spelled with a leading vowel letter that nevertheless take 'a'
# (consonant /j/, /w/ sound): a university, a union, a one-time ...
A_SOUND_CONST_WORDS = {
    'university', 'unit', 'union', 'universe', 'unity', 'user', 'useful',
    'unique', 'unicorn', 'usual', 'utensil', 'ukelele', 'ukulele',
    'euro', 'europe', 'european', 'ewe', 'one', 'once',
}
# Words spelled with a leading 'h' whose h is silent, taking 'an':
# an hour, an honest boy ...
AN_SILENT_H_WORDS = {'hour', 'honest', 'honour', 'honor', 'heir', 'herb', 'homage'}

# Flat adverbs that a strict grammar tutor expects in -ly form after an
# action verb: "He runs quick." -> "He runs quickly."
ASTRAY_FLAT_ADV = {'quick', 'slow', 'good', 'bad', 'real', 'nice', 'easy',
                   'terrible', 'beautiful'}

# Linking/copular verbs that license a predicate adjective after the verb.
LINKING_VERBS = (BE_FORM | {'seem', 'appear', 'look', 'feel', 'taste', 'sound',
                            'smell', 'become', 'remain', 'stay', 'turn', 'grow',
                            'prove', 'get'})
# The same verbs in their inflected / written forms, so "She feels tired."
# is not mistaken for "she feels tiredly" (the adjective-complement reading is
# legal after every form of a linking verb).
# Split contraction tails (you re, they ve, I m) are tokenizer artifacts; the
# following adjective is still a predicate adjective, not an adverb.
CONTRACTION_TAILS = {
    're', "'re", 's', "'s", 'm', "'m", 'll', "'ll", 've', "'ve",
    'd', "'d", 't', "'t",
}

LINKING_VERB_FORMS = (LINKING_VERBS |
                      {'feels', 'felt', 'feeling', 'seems', 'seemed', 'seeming',
                       'appears', 'appeared', 'appearing', 'looks', 'looked',
                       'looking', 'tastes', 'tasted', 'tasting', 'sounds',
                       'sounded', 'sounding', 'smells', 'smelled', 'smelling',
                       'becomes', 'became', 'becoming', 'remains', 'remained',
                       'remaining', 'stays', 'stayed', 'staying', 'turns',
                       'turned', 'turning', 'grew', 'grows', 'growing',
                       'proves', 'proved', 'proving', 'gets', 'got', 'getting'})

# Nouns that license a bare (article-less) singular argument: mass nouns,
# gerundial/activity nominals and common institutional/abstract nouns.
NONCOUNT_NOUNS = {
    'water', 'milk', 'juice', 'rice', 'bread', 'cheese', 'meat', 'sugar',
    'salt', 'oil', 'soup', 'coffee', 'tea', 'air', 'snow', 'rain', 'gold',
    'silver', 'paper', 'wood', 'furniture', 'information', 'advice',
    'luggage', 'baggage', 'equipment', 'news', 'knowledge', 'research',
    'traffic', 'money', 'cash', 'time', 'work', 'homework', 'housework',
    'weather', 'electricity', 'internet', 'darkness', 'sunshine',
    'grass', 'sand', 'dirt', 'soil', 'land', 'fire', 'ice', 'steam',
    'smoke', 'dust', 'mud', 'cotton', 'wool', 'steel', 'iron', 'plastic',
    # gerundial / activity nominals
    'reading', 'swimming', 'running', 'jogging', 'dancing', 'hiking',
    'writing', 'cooking', 'baking', 'fishing', 'hunting', 'shopping',
    'sightseeing', 'camping', 'skating', 'skiing', 'cycling', 'walking',
    # abstract / umbrella nouns commonly used bare
    'truth', 'honesty', 'education', 'health', 'happiness', 'freedom',
    'justice', 'love', 'hate', 'nature', 'history', 'grammar', 'art',
    'music', 'sports', 'mathematics', 'math', 'science', 'physics',
    'society', 'democracy', 'defense', 'peace', 'morale', 'spirit',
    'stationery', 'accommodation', 'equality', 'patience', 'courage',
    'anger', 'happiness',
    'food', 'fun', 'bread', 'butter', 'cheese', 'eggs', 'meat', 'fish',
    'chicken', 'beef', 'pork', 'rice', 'noodles', 'pasta', 'soup',
    'cake', 'candy', 'chocolate', 'ice cream', 'sushi', 'pizza',
    # sports/activities
    'soccer', 'football', 'basketball', 'tennis', 'baseball', 'hockey',
    'volleyball', 'golf', 'rugby', 'swimming', 'running', 'jogging',
    'cycling', 'skiing', 'football', 'cricket', 'badminton', 'music',
    'chess', 'geography', 'chemistry', 'biology', 'ecology', 'economics',
    'politics', 'statistics', 'linguistics', 'gymnastics', 'athletics',
    'fashion', 'literature', 'philosophy', 'psychology',
    # workplace / abstract mass nouns flagged by the corpus
    'progress', 'help', 'cooperation', 'assistance', 'support', 'staff',
    'paperwork', 'feedback', 'homework', 'housework', 'workload',
    # materials often used with bare singular determiners
    'flour', 'soap', 'shampoo', 'vinegar', 'beer', 'whiskey',
    'concrete', 'cement', 'brick',
    # gerundial / activity nominals
    'jumping', 'think', 'calling', 'teaching', 'crying', 'laughing',
    'singing', 'talking', 'running', 'swim', 'reading', 'writing',
    'smoking',
}
BARE_ARG_NOUNS = {
    'home', 'school', 'work', 'bed', 'church', 'town', 'court', 'class',
    'college', 'breakfast', 'lunch', 'dinner', 'supper', 'brunch', 'schoolwork',
    'tv', 'television', 'radio',  # 'watch TV' is idiomatic without an article
}
# Words the parser may tag as NN but which never take an article: indefinite
# pronouns (everyone, somebody, ...) and bare temporal/deictic adverbs.
ARTICLE_EXEMPT = {
    'everyone', 'everybody', 'someone', 'somebody', 'anyone', 'anybody',
    'nobody', 'nothing', 'everything', 'something', 'anything', 'none',
    'yesterday', 'today', 'tomorrow', 'tonight', 'now', 'then', 'here',
    'there',
}

VERB_FORM_LABEL = {
    'VB': 'base', 'VBD': 'past', 'VBG': 'present participle',
    'VBN': 'past participle', 'VBP': 'non-third-person present',
    'VBZ': 'third-person singular present', 'MD': 'modal',
}
NONFINITE = {'VB', 'VBG', 'VBN'}

CHECK_LABELS = {
    'C-MLM-ANOMALY': 'Word-Form Anomaly (model-located correction)',
    'C-SUBJECT-AGREEMENT': 'Subject\u2013Verb Agreement',
    'C-PREDICATE': 'Subject\u2013Verb Agreement',
    'C-DETERMINER-AGREEMENT': 'Determiner\u2013Noun Agreement',
    'C-DETERMINER': 'Determiner\u2013Noun Agreement',
    'C-AUX-FORM': 'Auxiliary Verb-Form Selection',
    'C-AUXILIARY': 'Auxiliary Verb-Form Selection',
    'C-TENSE-FINITE': 'needs a complete verb',
    'C-MOD-POS': 'Modifier Before Head Noun',
    'C-DET-STACK': 'Single Determiner per NP',
    'C-HEAD-NOUN': 'Head Noun Identification',
    'C-HEAD-VERB': 'Head Verb Identification',
    'C-INFINITIVAL-COMPLEMENT': 'Non-finite to-infinitive Complement',
    'C-INFINITIVAL-MARKER': 'Infinitival Marker to',
    'C-COMPARATIVE-DOUBLE': 'Double Comparative',
    'C-HEAD-PREPOSITION': 'Head Preposition Identification',
    'C-HEAD-ADJECTIVE': 'Head Adjective Identification',
    'C-HEAD-ADVERBIAL': 'Head Adverbial Identification',
    'C-PUNCT': 'Sentence Punctuation',
    'C-ROOT': 'Sentence Root Structure',
    'C-SUBJECT-ROLE': 'Clause Subject Role',
    'C-CLAUSE-PREDICATE': 'Clause Predicate',
    'C-CLAUSE-SUBJECT': 'Clause Subject Role',
    'C-PRONOUN-CASE': 'Pronoun Case (nominative vs. objective)',
    'C-ADJ-ADV': 'Adjective\u2013Adverb Confusion',
    'C-ADJ-ORDER': 'Adjective Order',
    'C-COMPARATIVE-STRUCT': 'Comparative/Superlative Structure',
    'C-INTENSIFIER': 'Intensifier Placement/Choice',
    'C-ARTICLE': 'Article/Determiner Omission',
    'C-ARTICLE-MISMATCH': 'a\u2013an Article Selection',
    'C-CAPITALIZATION': 'Sentence Capitalization',
    'C-QUANTIFIER': 'Quantifier\u2013Noun Agreement',
    'C-SMALL-CLAUSE': 'Small Clause (object complement)',
    'C-SMALL-CLAUSE-PREDICATE': 'Small Clause Predicate',
    'C-ADVERBIAL-COMPLEMENT': 'Adverbial Complement',
    'C-VERB-FORM': 'Verb Form',
    'C-NOUN-FORM': 'Noun Form',
    'C-CONTRACTION': 'Contractions',
    'C-REFLEXIVE-FORM': 'Reflexive Forms',
    'C-ADVERB-FORM': 'Adverb Formation',
    'C-SPELLING': 'Spelling',
    'C-VERB-ENDING': 'Verb Endings',
    'C-UNCOUNTABLE': 'Countable vs Uncountable',
    'C-COMPARATIVE-FORM': 'Comparative/Superlative Formation',
    'C-PLURAL-ONLY': 'Plural-only / Singular -s Nouns',
    'C-NUMERAL': 'Numerals and Measures',
    'C-REDUNDANCY': 'Redundancy',
    'C-ADJ-PREP': 'Adjective + Preposition',
    'C-EXTRA-PREP': 'Unnecessary Preposition',
    'C-MISSING-PREP': 'Missing Preposition',
    'C-HOMOPHONE': 'Homophones',
    'C-SOME-ANY': 'some/any',
    'C-EXISTENTIAL': 'Existential there',
    'C-INDEFINITE-AGREE': 'Indefinite Pronoun Agreement',
    'C-REFLEXIVE-ANTECEDENT': 'Reflexive\u2013Antecedent',
    'C-TO-BASE': 'to + base form',
    'C-MODAL-TO': 'Modals and Semi-modals',
    'C-CAUSATIVE-TO': 'Causatives and Perception Verbs',
    'C-PHRASAL-ORDER': 'Phrasal Verbs',
    'C-GERUND-INFINITIVE': 'Gerund vs Infinitive',
    'C-VERB-CLAUSE-PATTERN': 'Verb + Clause Patterns',
    'C-INTRANSITIVE-PASSIVE': 'Intransitive Passive',
    'C-STATIVE-PROGRESSIVE': 'Stative Verbs in Progressive',
    'C-PREP-GERUND': 'Preposition + Gerund',
    'C-CONJUNCTION-PAIR': 'Conjunction Pairing',
    'C-TERMINAL-PUNCT': 'Terminal Punctuation',
    'C-SPACING-REPEAT': 'Spacing and Repeats',
    'C-APOSTROPHE': 'Apostrophes',
    'C-QUOTATION': 'Quotation and Dialogue',
    'C-COLLECTIVE': 'Collective and Notional Nouns',
    'C-PRON-ANTECEDENT': 'Pronoun\u2013Antecedent',
    'C-UNNECESSARY-ARTICLE': 'Unnecessary Article',
    'C-SUBJUNCTIVE': 'Subjunctive and wish',
    'C-TENSE-TIME': 'Tense\u2013time Agreement',
    'C-CONNECTOR': 'Connector Misuse',
    'C-PLURAL-FORM': 'Regular/Irregular Noun Plural',
    'C-DET-NOUN-AGREE': 'Determiner\u2013Noun Number',
    'C-COORD-CASE': 'Pronoun Case in Coordination',
    'C-DUMMY-IT': 'Dummy it/there',
    'C-TRANSITIVITY': 'Verb Transitivity',
    'C-COORD-SUBJ-AGREE': 'Coordinated Subject\u2013Verb Agreement',
    'C-NOUN-MODIFIER-NUMBER': 'Singular Noun Modifier',
    'C-ADVERB-PLACEMENT': 'Adverb Placement',
    'C-WRONG-PREPOSITION': 'Wrong Preposition Choice',
    'C-TIME-PLACE-PREP': 'in/on/at with Time and Place',
    'C-FRAGMENT': 'Sentence Fragment',
    'C-RESUMPTIVE-RELATIVE': 'Resumptive Pronoun in Relative Clause',
    'C-CLAUSE-LINKING': 'Clause Linking (subordinator + to-infinitive)',
    'C-OBJECT-ORDER': 'Object Order in Ditransitive Verbs',
    'C-SENTENCE-CAPITAL': 'Sentence-initial Capitalization',
    'C-DOUBLE-NEGATIVE': 'Double Negation',
    'C-IMPERATIVE-VERB': 'Imperative Verb Form',
    'C-CONDITIONAL-WILL': 'Conditional Tense',
    'C-REPORTED-SPEECH': 'Reported Speech',
    'C-RUNON': 'Run-on / Fused Sentence',
    'C-EXTRA-WORD': 'Missing or Extra Word',
    'C-PROPER-NOUN': 'Proper Nouns and \u201cI\u201d',
    'C-PARTICIPIAL': 'Participial Adjectives',
    'C-TENSE-CONSISTENCY': 'Tense Consistency',
    'C-HYPHEN': 'Hyphens and Dashes',
    'C-CONFUSABLE': 'Confusable Words',
    'C-COLLOCATION': 'Collocations',
    'C-SELECTIONAL': 'Selectional Restrictions',
    'C-REGISTER': 'Register',
    'C-L1-INTERFERENCE': 'L1 Interference / False Friends',
    'C-NUMBER-AGREE': 'Quantified Subject Agreement',
    'C-SUBJ-AGREE-XP': 'Subject-Verb Agreement Across a Phrase',
    'C-POSSESSIVE': 'Possessive Pronoun vs Determiner',
    'C-NUMERAL-FORMAT': 'Numbers, Dates, Abbreviations',
    'C-CORRELATIVE-AGREE': 'Correlative Agreement',
    'C-POSSESSIVE-S': "Possessive 's / s'",
    'C-DANGLING': 'Dangling / Misplaced Modifier',
    'C-INTRO-COMMA': 'Commas',
    'C-PUNCT': 'Colons and Semicolons',
    'C-PRON-AMBIG': 'Ambiguous Reference',
    'C-PP-ATTACH': 'Structural Ambiguity (PP-attachment)',
    'C-PASSIVE': 'Passive Formation',
    'C-WORD-ORDER': 'Word Order in Statements',
    'C-FIRST-MENTION': 'Definite vs Indefinite',
    'C-LEXICON-MALFORMED': 'Word Form Licensed by Lexicon',
    'C-LEXICON-UNKNOWN': 'Unrecognised Word (unverified)',
    'C-LEXICON-TAG-MISMATCH': 'Parser Tag vs Lexicon (unverified)',
    'C-RELATIVE-AGREE': 'Relative Clause Agreement',
    'C-RELATIVE-POSSESSIVE': "Relative 'whose' Needs a Noun",
    'C-RELATIVE-PRONOUN': 'Relative Pronoun Choice (who/which)',
}

# Constraint id -> (matrix.md rule id, check method). The method decides how the
# XAI layer explains the verdict (T: tree subtree, L: word-list lookup,
# C: condition + options + confidence, shown as a suggestion).
CONSTRAINT_RULE = {
    'C-SUBJECT-AGREEMENT': ('2.1', 'T'),
    'C-PREDICATE': ('2.1', 'T'),
    'C-DETERMINER-AGREEMENT': ('2.10', 'T'),
    'C-DETERMINER': ('3.6', 'T'),
    'C-DET-STACK': ('3.5', 'T'),
    'C-HEAD-NOUN': ('3.6', 'T'),
    'C-NOUN-FORM': ('1.2', 'L'),
    'C-NOUN-ADJUNCT': ('4.2', 'T'),
    'C-MOD-POS': ('7.7', 'T'),
    'C-NP-POSTMODIFIER': ('7.7', 'T'),
    'C-NP-REDUCED-RELATIVE': ('9.10', 'T'),
    'C-NP-RELATIVE': ('2.7', 'T'),
    'C-COORDINATOR': ('2.3', 'T'),
    'C-HEAD-VERB': ('6.2', 'T'),
    'C-INFINITIVAL-COMPLEMENT': ('6.10', 'T'),
    'C-INFINITIVAL-MARKER': ('6.10', 'T'),
    'C-AUXILIARY': ('6.1', 'T'),
    'C-AUX-COMPLEMENT': ('6.1', 'T'),
    'C-AUX-FORM': ('6.1', 'T'),
    'C-TENSE-FINITE': ('6.2', 'T'),
    'C-DIRECT-OBJECT': ('9.15', 'T'),
    'C-ADJUNCT': ('8.5', 'L'),
    'C-PREDICATE-ADJECTIVE': ('7.1', 'T'),
    'C-ADVERBIAL': ('7.3', 'T'),
    'C-CLAUSAL-COMPLEMENT': ('6.20', 'L'),
    'C-PARTICLE': ('6.11', 'L'),
    'C-HEAD-PREPOSITION': ('8.1', 'C'),
    'C-PREP-OBJECT': ('8.5', 'L'),
    'C-HEAD-ADJECTIVE': ('7.1', 'T'),
    'C-INTENSIFIER': ('7.5', 'T'),
    'C-ADJ-ORDER': ('7.2', 'L'),
    'C-COMPARATIVE-STRUCT': ('7.6', 'T'),
    'C-PARTICIPLE-MODIFIER': ('7.4', 'L'),
    'C-HEAD-ADVERBIAL': ('7.3', 'T'),
    'C-CLAUSE-SUBJECT': ('2.1', 'T'),
    'C-CLAUSE-PREDICATE': ('9.14', 'T'),
    'C-CLAUSAL-ADVERBIAL': ('9.14', 'T'),
    'C-RELATIVE-CLAUSE': ('2.7', 'T'),
    'C-RELATIVE-HEAD': ('5.4', 'T'),
    'C-RELATIVE-PRONOUN': ('5.4', 'T'),
    'C-RELATIVE-NOUN': ('5.4', 'T'),
    'C-COMPLEMENTIZER': ('9.14', 'T'),
    'C-NP-COMPOUND': ('4.2', 'T'),
    'C-PUNCT': ('10.3', 'T'),
    'C-ROOT': ('9.1', 'T'),
    'C-CAPITALIZATION': ('10.1', 'T'),
    'C-PRONOUN-CASE': ('5.1', 'T'),
    'C-ADJ-ADV': ('7.1', 'T'),
    'C-ARTICLE': ('3.2', 'T'),
    'C-ARTICLE-MISMATCH': ('3.1', 'L'),
    'C-QUANTIFIER': ('2.11', 'T'),
    'C-SMALL-CLAUSE': ('9.15', 'T'),
    'C-SMALL-CLAUSE-PREDICATE': ('7.1', 'T'),
    'C-ADVERBIAL-COMPLEMENT': ('7.3', 'T'),
    'C-VERB-FORM': ('1.5', 'L'),
    'C-COMPARATIVE-DOUBLE': ('7.6', 'T'),
    'C-UNLISTED': (None, 'T'),
    'C-CONTRACTION': ('1.11', 'L'),
    'C-REFLEXIVE-FORM': ('1.9', 'L'),
    'C-ADVERB-FORM': ('1.8', 'L'),
    'C-SPELLING': ('1.12', 'L'),
    'C-VERB-ENDING': ('1.4', 'L'),
    'C-UNCOUNTABLE': ('4.1', 'L'),
    'C-COMPARATIVE-FORM': ('1.7', 'L'),
    'C-PLURAL-ONLY': ('4.3', 'L'),
    'C-NUMERAL': ('1.13', 'L'),
    'C-REDUNDANCY': ('9.12', 'L'),
    'C-ADJ-PREP': ('8.4', 'L'),
    'C-EXTRA-PREP': ('8.3', 'L'),
    'C-MISSING-PREP': ('8.2', 'C'),
    'C-HOMOPHONE': ('1.10', 'T'),
    'C-SOME-ANY': ('3.7', 'T'),
    'C-EXISTENTIAL': ('2.4', 'T'),
    'C-INDEFINITE-AGREE': ('2.8', 'T'),
    'C-REFLEXIVE-ANTECEDENT': ('2.14', 'T'),
    'C-TO-BASE': ('6.10', 'T'),
    'C-MODAL-TO': ('6.12', 'T'),
    'C-CAUSATIVE-TO': ('6.19', 'T'),
    'C-PHRASAL-ORDER': ('6.11', 'L'),
    'C-GERUND-INFINITIVE': ('6.9', 'L'),
    'C-VERB-CLAUSE-PATTERN': ('6.20', 'L'),
    'C-INTRANSITIVE-PASSIVE': ('6.5', 'L'),
    'C-STATIVE-PROGRESSIVE': ('6.6', 'L'),
    'C-PREP-GERUND': ('8.6', 'T'),
    'C-CONJUNCTION-PAIR': ('9.9', 'L'),
    'C-TERMINAL-PUNCT': ('10.3', 'T'),
    'C-SPACING-REPEAT': ('10.9', 'T'),
    'C-APOSTROPHE': ('10.5', 'T'),
    'C-QUOTATION': ('10.6', 'T'),
    'C-COLLECTIVE': ('2.5', 'C'),
    'C-PRON-ANTECEDENT': ('2.12', 'C'),
    'C-UNNECESSARY-ARTICLE': ('3.3', 'C'),
    'C-SUBJUNCTIVE': ('6.17', 'C'),
    'C-TENSE-TIME': ('11.3', 'C'),
    'C-CONNECTOR': ('11.8', 'C'),
    'C-PLURAL-FORM': ('1.1', 'L'),
    'C-DET-NOUN-AGREE': ('3.8', 'L'),
    'C-COORD-CASE': ('5.2', 'T'),
    'C-DUMMY-IT': ('5.5', 'T'),
    'C-TRANSITIVITY': ('6.8', 'L'),
    'C-DOUBLE-NEGATIVE': ('6.14', 'T'),
    'C-IMPERATIVE-VERB': ('6.15', 'T'),
    'C-CONDITIONAL-WILL': ('6.16', 'T'),
    'C-REPORTED-SPEECH': ('6.18', 'T'),
    'C-RUNON': ('9.3', 'T'),
    'C-EXTRA-WORD': ('9.7', 'T'),
    'C-PROPER-NOUN': ('10.2', 'L'),
    'C-PARTICIPIAL': ('7.4', 'L'),
    'C-TENSE-CONSISTENCY': ('6.7', 'C'),
    'C-HYPHEN': ('10.7', 'C'),
    'C-CONFUSABLE': ('11.1', 'C'),
    'C-COLLOCATION': ('11.2', 'C'),
    'C-SELECTIONAL': ('11.4', 'C'),
    'C-REGISTER': ('11.6', 'C'),
    'C-L1-INTERFERENCE': ('11.7', 'C'),
    'C-NUMBER-AGREE': ('2.9', 'T'),
    'C-SUBJ-AGREE-XP': ('2.2', 'T'),
    'C-POSSESSIVE': ('5.6', 'T'),
    'C-NUMERAL-FORMAT': ('10.10', 'L'),
    'C-CORRELATIVE-AGREE': ('2.13', 'T'),
    'C-POSSESSIVE-S': ('1.3', 'T'),
    'C-DANGLING': ('9.11', 'C'),
    'C-INTRO-COMMA': ('10.4', 'T'),
    'C-PUNCT': ('10.8', 'T'),
    'C-PRON-AMBIG': ('5.3', 'C'),
    'C-PP-ATTACH': ('11.5', 'C'),
    'C-PASSIVE': ('6.4', 'T'),
    'C-WORD-ORDER': ('9.6', 'T'),
    'C-FIRST-MENTION': ('3.4', 'C'),
    'C-LEXICON-MALFORMED': ('1.12', 'L'),
    'C-LEXICON-UNKNOWN': ('1.12', 'L'),
    'C-LEXICON-TAG-MISMATCH': ('1.12', 'L'),
    'C-RELATIVE-AGREE': ('2.7', 'T'),
    'C-RELATIVE-POSSESSIVE': ('5.4', 'T'),
    'C-RELATIVE-PRONOUN': ('5.4', 'T'),
}


IRREGULAR_PLURAL = {
    'child': 'children', 'man': 'men', 'woman': 'women', 'foot': 'feet',
    'tooth': 'teeth', 'mouse': 'mice', 'person': 'people', 'goose': 'geese',
    'ox': 'oxen', 'leaf': 'leaves', 'life': 'lives', 'wife': 'wives',
    'knife': 'knives', 'shelf': 'shelves', 'wolf': 'wolves', 'half': 'halves',
    'calf': 'calves', 'loaf': 'loaves', 'thief': 'thieves', 'sheep': 'sheep',
    'fish': 'fish', 'deer': 'deer', 'series': 'series', 'species': 'species',
}

# Productive morphology rules used for suggestions. These are intentionally
# suffix-based rather than a list of every noun in the language. The output
# is the preferred form; regular alternatives remain valid because number is
# determined from the parser's NOUN tag, not from this suggestion helper.
LATIN_PLURAL_SUFFIXES = (
    ('ctus', 'cti'),   # cactus/cacti
    ('ngus', 'ngi'),   # fungus/fungi
    ('dius', 'dii'),   # radius/radii
    ('ulus', 'uli'),   # stimulus/stimuli
    ('ndex', 'ndices'),# index/indices
    ('trix', 'trices'),# matrix/matrices
    ('sis', 'ses'),    # analysis/analyses, thesis/theses
)

_INFLECT = inflect.engine()

IRREGULAR_VBN = {
    'be': 'been', 'beat': 'beaten', 'bend': 'bent', 'bite': 'bitten',
    'break': 'broken', 'bring': 'brought', 'build': 'built', 'buy': 'bought',
    'catch': 'caught', 'choose': 'chosen', 'come': 'come', 'cut': 'cut',
    'do': 'done', 'drink': 'drunk', 'drive': 'driven', 'eat': 'eaten',
    'fall': 'fallen', 'feel': 'felt', 'fight': 'fought', 'find': 'found',
    'fly': 'flown', 'forget': 'forgotten', 'forgive': 'forgiven',
    'freeze': 'frozen', 'get': 'gotten', 'give': 'given', 'go': 'gone',
    'grow': 'grown', 'have': 'had', 'hear': 'heard', 'hit': 'hit',
    'hold': 'held', 'keep': 'kept', 'know': 'known', 'lead': 'led',
    'leave': 'left', 'lend': 'lent', 'let': 'let', 'lose': 'lost',
    'make': 'made', 'mean': 'meant', 'meet': 'met', 'pay': 'paid',
    'put': 'put', 'read': 'read', 'ride': 'ridden', 'ring': 'rung',
    'rise': 'risen', 'run': 'run', 'say': 'said', 'see': 'seen',
    'sell': 'sold', 'send': 'sent', 'sing': 'sung', 'sink': 'sunk',
    'sit': 'sat', 'sleep': 'slept', 'speak': 'spoken', 'spend': 'spent',
    'stand': 'stood', 'steal': 'stolen', 'swim': 'swum', 'take': 'taken',
    'teach': 'taught', 'tell': 'told', 'think': 'thought', 'throw': 'thrown',
    'understand': 'understood', 'wear': 'worn', 'win': 'won', 'write': 'written',
    'become': 'become', 'wake': 'woken', 'awake': 'awoken', 'light': 'lit',
}

IRREGULAR_PAST = {
    'be': 'was', 'begin': 'began', 'break': 'broke', 'bring': 'brought',
    'buy': 'bought', 'catch': 'caught', 'choose': 'chose', 'come': 'came',
    'do': 'did', 'drink': 'drank', 'drive': 'drove', 'eat': 'ate',
    'fall': 'fell', 'feel': 'felt', 'find': 'found', 'fly': 'flew',
    'forget': 'forgot', 'forgive': 'forgave', 'freeze': 'froze',
    'get': 'got', 'give': 'gave', 'go': 'went', 'grow': 'grew',
    'have': 'had', 'hear': 'heard', 'keep': 'kept', 'know': 'knew',
    'leave': 'left', 'lend': 'lent', 'lose': 'lost', 'make': 'made',
    'mean': 'meant', 'meet': 'met', 'pay': 'paid', 'read': 'read',
    'ride': 'rode', 'ring': 'rang', 'rise': 'rose', 'run': 'ran',
    'say': 'said', 'see': 'saw', 'sell': 'sold', 'send': 'sent',
    'sing': 'sang', 'sink': 'sank', 'sit': 'sat', 'sleep': 'slept',
    'speak': 'spoke', 'spend': 'spent', 'stand': 'stood', 'steal': 'stole',
    'swim': 'swam', 'take': 'took', 'teach': 'taught', 'tell': 'told',
    'think': 'thought', 'throw': 'threw', 'understand': 'understood',
    'wear': 'wore', 'win': 'won', 'write': 'wrote', 'become': 'became',
}


def _preserve_case(source, word):
    """Apply the capitalization of ``source`` to a replacement word."""
    if source and source[0].isupper():
        return word[0].upper() + word[1:]
    return word


def _edit(start, end, text):
    """Token-level correction on the target sentence: replace tokens
    [start, end) with ``text``. start == end inserts before token ``start``;
    text == '' deletes. Token indices are relative to the analysed sentence,
    the same coordinate system the node spans use."""
    return {'start': start, 'end': end, 'text': text}


def _base_form(leaf):
    """Approximate a lexical base form from the observed surface and POS."""
    word = leaf['surface'].lower()
    pos = leaf['type']
    if word in BE_FORM:
        return 'be'
    if word in HAVE_FORM:
        return 'have'
    if word in DO_FORM:
        return 'do'
    if pos in VERB_CLASS:
        lem = _verb_lemma(word)
        if lem:
            return lem
    for base in IRREGULAR_VBN:
        if word in {base + 'd', base + 'ed'}:
            return base
    if pos == 'VBZ':
        if word.endswith('ies'):
            return word[:-3] + 'y'
        if word.endswith('es'):
            return word[:-2]
        if word.endswith('s'):
            return word[:-1]
    if pos == 'VBG' and word.endswith('ing') and len(word) > 4:
        stem = word[:-3]
        return stem + 'e' if stem.endswith(('v', 'c')) else stem
    if pos in {'VBD', 'VBN'}:
        reverse = {value: key for key, value in IRREGULAR_VBN.items()}
        if word in reverse:
            return reverse[word]
        if word.endswith('ied'):
            return word[:-3] + 'y'
        if word.endswith('ed') and len(word) > 3:
            return word[:-2]
    return word


def _verb_lemma(low):
    """Best-effort lexical base form for a verb surface (irregular-aware).

    A surface may have several verb lemmas (``saw`` -> ``see``/``saw``,
    ``fell`` -> ``fall``/``fell``).  The true base is the candidate that is
    *not* the surface itself; when several remain, the one whose past or
    participle form reproduces the surface wins.
    """
    if not low:
        return None
    try:
        if licensing is not None:
            lemmas = licensing._lemmas(low, 'VERB')
            if lemmas:
                cands = set(lemmas)
                pool = {c for c in cands if c != low} or cands
                for c in sorted(pool):
                    if _past_form(c) == low or _vbn_form(c) == low:
                        return c
                return sorted(pool)[0]
    except Exception:  # pragma: no cover - degraded mode
        pass
    return None


def _past_form(base):
    """Base verb -> simple past (e.g. eat->ate, kick->kicked)."""
    w = base.lower()
    if w in IRREGULAR_PAST:
        return IRREGULAR_PAST[w]
    if _get_inflection is not None:
        try:
            inf = _get_inflection(w, tag='VBD')
            if inf:
                return inf[0]
        except Exception:  # pragma: no cover
            pass
    if w.endswith('e'):
        return w + 'd'
    if w.endswith('y') and len(w) > 1 and w[-2] not in 'aeiou':
        return w[:-1] + 'ied'
    return w + 'ed'


def _plural_noun(word):
    w = word.lower()
    if w in IRREGULAR_PLURAL:
        return IRREGULAR_PLURAL[w]
        return IRREGULAR_PLURAL[w]
    for singular_suffix, plural_suffix in LATIN_PLURAL_SUFFIXES:
        if w.endswith(singular_suffix) and len(w) > len(singular_suffix):
            return w[:-len(singular_suffix)] + plural_suffix
    if w.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return w + 'es'
    if len(w) > 1 and w[-1] == 'y' and w[-2] not in 'aeiou':
        return w[:-1] + 'ies'
    return w + 's'


def _singular_noun(leaf):
    """Approximate the singular form from the observed noun surface."""
    word = leaf['surface'].lower()
    if word in IRREGULAR_PLURAL.values():
        reverse = {value: key for key, value in IRREGULAR_PLURAL.items()}
        return reverse[word]
    # A regular -es plural of an -us noun (cactuses, buses, statuses) must be
    # resolved before the classical -is -> -es rule below.
    if word.endswith('uses') and len(word) > 4:
        return word[:-2]
    # Common over-regularization of -is nouns: analysises, thesises.
    if word.endswith('ises') and len(word) > 4:
        return word[:-2]
    for singular_suffix, plural_suffix in LATIN_PLURAL_SUFFIXES:
        if plural_suffix == 'ses':
            continue
        if word.endswith(plural_suffix) and len(word) > len(plural_suffix):
            return word[:-len(plural_suffix)] + singular_suffix
    if _INFLECT is not None:
        candidate = _INFLECT.singular_noun(word)
        if candidate and _INFLECT.compare_nouns(candidate, word) == 's:p':
            return candidate
        if word.endswith('ses'):
            candidate = word[:-2] + 'is'
            if _INFLECT.compare_nouns(candidate, word) == 's:p':
                return candidate
    # Classical plurals ending in -i are especially common in learner input
    # and have no reliable word-by-word exception list.
    if word.endswith('i') and len(word) > 2 and word[-2] in 'cglnmdt':
        return word[:-1] + 'us'
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith('es'):
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


# Learner-irregular but correct plural forms that generic inflectors cannot be
# trusted to recognise (crises, appendices, nuclei, ...). They must never be
# reported as "not a normal plural".
ACCEPTED_PLURALS = {
    'crises', 'theses', 'analyses', 'bases', 'diagnoses', 'synopses',
    'parentheses', 'hypotheses', 'oases', 'axes', 'indices', 'appendices',
    'matrices', 'vertices', 'formulae', 'larvae', 'radii', 'cacti', 'fungi',
    'nuclei', 'stimuli', 'alumni', 'curricula', 'errata', 'addenda', 'bacteria',
    'criteria', 'phenomena', 'media', 'data', 'centa', 'genera', 'viscera',
}


def _noun_form_issue(leaf):
    """Return (singular, expected_plural) for a malformed plural, else None.

    ``inflect`` supplies both productive rules and its maintained lexical
    exceptions. Comparing the observed plural with the library's accepted
    singular/plural relation avoids rejecting legitimate alternatives such as
    ``cactuses`` and ``persons``.
    """
    if leaf['type'] not in NOUN_PLURAL | NOUN_SINGULAR:
        return None
    observed = _lower(leaf['surface'])
    if observed in ACCEPTED_PLURALS or observed in POSS_PRON_SURFACES:
        return None
    singular = _singular_noun(leaf)
    if not singular or singular == observed or singular is False:
        return None
    # Do not permit a regular suffix on an already-irregular plural:
    # "men" and "women" are complete plural forms, so "mens"/"womens"
    # are malformed even though a generic inflector may accept them.
    if singular in IRREGULAR_PLURAL.values() and observed != singular:
        return singular, singular
    if _INFLECT.compare_nouns(singular, observed) == 's:p':
        return None
    expected = _INFLECT.plural(singular)
    if not expected or expected == observed:
        return None
    return singular, expected


def _third_present(base):
    """Base verb -> 3rd-person singular present (e.g. run->runs, be->is)."""
    w = base.lower()
    if w == 'be':
        return 'is'
    if w == 'have':
        return 'has'
    if w == 'do':
        return 'does'
    if w == 'go':
        return 'goes'
    if w.endswith(('s', 'x', 'z', 'ch', 'sh', 'o')):
        return w + 'es'
    if len(w) > 1 and w[-1] == 'y' and w[-2] not in 'aeiou':
        return w[:-1] + 'ies'
    return w + 's'


def _nonthird_present(base):
    """Base verb -> non-3rd-person singular present (e.g. run->run, be->are)."""
    w = base.lower()
    return 'are' if w == 'be' else w


def _agree_form(leaf, subject_key_):
    """The form of ``leaf`` that agrees with the subject, preserving tense.

    A past-tense 'be' must stay past ('We was' -> 'We were', not 'We are'),
    and a first-person subject needs 'am', not the generic non-3sg 'are'.
    """
    surface = leaf['surface'].lower()
    base = _base_form(leaf)
    past = leaf.get('type') == 'VBD' or surface in {
        'was', 'were', 'had', 'did'}
    if base == 'be':
        if past:
            return 'was' if subject_key_ in (('1', 'sg'), ('3', 'sg')) else 'were'
        if subject_key_ == ('1', 'sg'):
            return 'am'
        if subject_key_ == ('3', 'sg'):
            return 'is'
        return 'are'
    if base == 'have':
        if past:
            return 'had'
        return 'has' if subject_key_ == ('3', 'sg') else 'have'
    if base == 'do':
        if past:
            return 'did'
        return 'does' if subject_key_ == ('3', 'sg') else 'do'
    if past:
        return surface
    return (_third_present(base) if subject_key_ == ('3', 'sg')
            else _nonthird_present(base))


def _agree_tag(leaf, subject_key_):
    base = _base_form(leaf)
    if leaf.get('type') == 'VBD' or leaf['surface'].lower() in {
            'was', 'were', 'had', 'did'}:
        return 'VBD'
    if base == 'be':
        return 'VBZ' if subject_key_ == ('3', 'sg') else 'VBP'
    return 'VBZ' if subject_key_ == ('3', 'sg') else 'VBP'


def _vbn_form(base):
    """Base verb -> past participle (e.g. eat->eaten, kick->kicked)."""
    w = base.lower()
    if w in IRREGULAR_VBN:
        return IRREGULAR_VBN[w]
    if _get_inflection is not None:
        try:
            inf = _get_inflection(w, tag='VBN')
            if inf:
                return inf[0]
        except Exception:  # pragma: no cover
            pass
    if w.endswith('e'):
        return w + 'd'
    return w + 'ed'


def _vbg_form(base):
    """Base verb -> present participle (e.g. run->running, make->making)."""
    w = base.lower()
    if w == 'be':
        return 'being'
    if w in ('lie', 'die', 'tie'):
        return w[:-1] + 'ying'
    if w.endswith('e') and not w.endswith('ee'):
        return w[:-1] + 'ing'
    vowels = sum(w.count(v) for v in 'aeiou')
    if len(w) >= 3 and w[-1] not in 'aeiouwxy' and w[-2] in 'aeiou' \
            and w[-3] not in 'aeiou' and vowels == 1:
        return w + w[-1] + 'ing'
    return w + 'ing'


def _regularized_form(base):
    word = base.lower()
    return word + 'd' if word.endswith('e') else word + 'ed'


def _is_valid_verb_form(leaf):
    """Reject regularized spellings of irregular forms and past-as-participle use."""
    word = leaf['surface'].lower()
    pos = leaf['type']
    if pos == 'VBD':
        return word not in {
            _regularized_form(base)
            for base in IRREGULAR_PAST
        }
    if pos == 'VBN':
        if word == 'got':
            # British-English 'have got' uses 'got' as the past participle.
            return True
        if word in IRREGULAR_PAST.values() and word not in IRREGULAR_VBN.values():
            return False
        return word not in {
            _regularized_form(base)
            for base in IRREGULAR_VBN
        }
    return True


def _replace_subject_head(subj, subj_head, new_head_word):
    """Subject surface with its (trailing) head noun swapped for ``new_head_word``."""
    words = subj['surface'].split()
    if words and words[-1] == subj_head['surface']:
        return ' '.join(words[:-1] + [_preserve_case(subj_head['surface'], new_head_word)])
    return _preserve_case(subj_head['surface'], new_head_word)


def _rule_for(node):
    """Formal production rule realized by this node (e.g. NP -> DT + NN)."""
    if 'children' in node:
        return f"{node['type']} \u2192 " + ' + '.join(c['type'] for c in node['children'])
    return f"{node['type']} \u2192 '{node['surface']}'"


def _checks_for(detail, details):
    """Deterministic checklist of the matrix checks that apply to a node.

    Built from the node's own edge verdict (and, for internal nodes, the
    verdicts of its immediate constituents) so a learner sees exactly which
    rule checks pass or fail at this level.
    """
    checks = []
    ok_own = detail['status'] != 'error'

    def add(label, ok):
        if not any(c['check'] == label for c in checks):
            checks.append({'check': label, 'ok': ok})

    named = CHECK_LABELS.get(detail['constraint'])
    if named:
        add(named, ok_own)
    elif detail['constraint'] != 'C-UNLISTED':
        add(f"Rule membership ({detail['constraint']})", ok_own)
    else:
        add('Matrix coverage (unrated \u00b7 valid-by-default)', ok_own)
    for child_id in detail.get('children_ids', []):
        cd = details.get(child_id)
        if not cd:
            continue
        child_named = CHECK_LABELS.get(cd['constraint'])
        if child_named:
            add(child_named, cd['status'] != 'error')
    return checks


def _lower(surface):
    return surface.lower()


_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:!?%])")
_CLITIC_SPACE = re.compile(r"\s+('(?:s|re|ve|ll|d|m|t))\b")


def _pretty(surface):
    """Tidy a parse surface for quoting inside an explanation."""
    text = re.sub(r'\s+', ' ', str(surface or '')).strip()
    text = _SPACE_BEFORE_PUNCT.sub(r'\1', text)
    text = _CLITIC_SPACE.sub(r"\1", text)
    text = text.replace(" n't", "n't")
    return text


def _strip_preface(text, sentence):
    """Drop the repeated "In the sentence '...', " scaffolding.

    The sentence is still referenced by the quoted words and phrases inside
    the explanation itself; only the boilerplate prefix is removed.
    """
    text = str(text or '')
    prefix = f"In the sentence '{sentence}', "
    if text.startswith(prefix):
        text = text[len(prefix):].strip()
        if text:
            text = text[0].upper() + text[1:]
    return text


def _rem_from_text(text, surface=''):
    """Build a {What's wrong / How to fix it} card from a rule finding text.

    Rule texts are written as "what is wrong; how to fix it", so the last
    '; ' that starts a directive ("Change 'x' to 'y'.", "Use 'z'.", ...)
    is the split point.  Non-directive '; ' inside quoted replacements is
    ignored.  Failing that, a final directive sentence becomes the fix and
    everything before it the problem.  When a rule text only *describes* the
    problem, the corrected form is read out of the description (an
    "instead of 'x'", a "must be capitalized as 'x'", a "remove ..."
    instruction, ...) so the fix always names the form to write.
    """
    def cap(s):
        return s[:1].upper() + s[1:] if s else s

    def card(fix, violation=None):
        return {'violation': (violation if violation is not None
                              else text).strip(),
                'suggested_fix': cap(fix.strip().rstrip('.')),
                'alternative_fix': None, 'targeted_outcome': None}

    best = -1
    fix_start = -1
    start = 0
    while True:
        idx = text.find('; ', start)
        if idx == -1:
            break
        after = text[idx + 2:].lstrip()
        if _DIRE_START.match(after):
            best = idx
            fix_start = idx + 2
        start = idx + 2
    if best == -1:
        colon = re.compile(r':\s+((?:so\s+)?(?:write|use|change|replace|add|'
                           r'remove|drop|capitalize|move|keep|put|choose|correct|'
                           r'make|spell)\b)', re.I)
        for m in colon.finditer(text):
            best = m.start()
            fix_start = m.start(1)
    if best != -1:
        fix = text[fix_start:].strip().rstrip('.')
        if not _VAGUE_FIX.search(fix):
            return {'violation': text[:best].strip(),
                    'suggested_fix': cap(fix),
                    'alternative_fix': None, 'targeted_outcome': None}
    # --- no explicit directive: read the corrected form out of the description ---
    m = re.search(r"instead of '([^']+)'", text)
    if m and surface:
        return card(f"Change '{surface}' to '{m.group(1)}'.")
    m = re.search(r"change (?:it|them|the \w+|'[^']+') to '([^']+)'", text, re.I)
    if m and surface:
        return card(f"Change '{surface}' to '{m.group(1)}'.")
    if 'must be capitalized' in text:
        m = re.search(r"as '([^']+)'", text) or re.search(r"'([^']+)'$", text.strip())
        if m and surface:
            return card(f"Change '{surface}' to '{m.group(1)}'.")
    m = re.search(r"use '([^']+)', not '([^']+)'", text)
    if m:
        return card(f"Write '{m.group(1)}' instead of '{m.group(2)}'.")
    m = re.search(r"must be '([^']+)', not '([^']+)'", text)
    if m:
        return card(f"Change '{m.group(2)}' to '{m.group(1)}'.")
    if re.search(r'No article is needed', text) and surface:
        return card(f"Remove '{surface}'.")
    if re.search(r'repetition|repeats it|subject twice|same idea twice|'
                 r'express the same idea', text):
        quoted = [q.strip("'") for q in re.findall(r"'[^']*'", text)]
        if len(quoted) >= 2:
            return card(f"Remove one of the repeated words: keep "
                        f"'{quoted[0]}' or '{quoted[-1]}', not both.")
        return card(f"Remove the repeated word '{surface}'." if surface
                    else 'Remove the repeated word.')
    if re.search(r'two negatives|one negation', text):
        return card('Use only one negative word here'
                    + (f" — remove '{surface}'." if surface else '.'))
    m = re.search(r"should not be followed by the plural '([^']+)'", text)
    if m:
        sing = _preserve_case(m.group(1), _singular_noun({'surface': m.group(1)}))
        return card(f"Change '{m.group(1)}' to the singular '{sing}'.")
    if re.search(r'should be plural', text) and surface:
        plur = _preserve_case(surface, _plural_noun(_singular_noun({'surface': surface})))
        return card(f"Change '{surface}' to the plural '{plur}'.")
    if re.search(r'needs a preposition|does not take a direct object', text) and surface:
        return card(f"Add a preposition after '{surface}' (for example "
                    f"'{surface} to ...').")
    if re.search(r'object (?:comes before the verb|should follow the verb)', text):
        return card(f"Move the object so it comes after the verb"
                    + (f", e.g. after '{surface}'." if surface else '.'))
    if re.search(r'has a verb but no subject|add the subject', text):
        return card('Add the subject that does the action, before the verb '
                    "(for example, start with 'she' or 'they').")
    if re.search(r'wrong place|move it closer', text):
        m = re.search(r"modifier in '([^']+)'", text)
        if m:
            return card(f"Move the describing phrase in '{m.group(1)}' so it sits "
                        'right next to the word it describes.')
        return card('Move the phrase so it sits right next to the word it '
                    'describes.')
    if re.search(r'does not end with', text):
        return card("Add the missing end punctuation ('.', '!' or '?').")
    m = re.search(r"reflexive '([^']+)' does not match the subject '([^']+)'", text)
    if m:
        refl = {'i': 'myself', 'he': 'himself', 'she': 'herself', 'it': 'itself',
                'we': 'ourselves', 'they': 'themselves', 'you': 'yourself'}
        target = refl.get(m.group(2).lower())
        if target:
            return card(f"Change '{m.group(1)}' to '{target}'.")
        subject_of = {'myself': 'I', 'ourselves': 'we', 'himself': 'he',
                      'herself': 'she', 'itself': 'it', 'themselves': 'they',
                      'yourself': 'you'}
        t2 = subject_of.get(m.group(1).lower())
        if t2:
            return card(f"Change '{m.group(1)}' to the subject form '{t2}'.")
    if re.search(r'do not agree', text) and surface:
        return card(f"Change '{surface}' to the form that agrees with the subject.")

    # --- describe-only text: fall back to a plain split, then a quoted target ---
    plain = text.rfind('; ')
    if plain != -1:
        fix = text[plain + 2:].strip().rstrip('.')
        if not _VAGUE_FIX.search(fix):
            return {'violation': text[:plain].strip(),
                    'suggested_fix': cap(fix),
                    'alternative_fix': None, 'targeted_outcome': None}
    segments = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(segments) > 1 and _DIRE_START.match(segments[-1]):
        return {'violation': ' '.join(segments[:-1]),
                'suggested_fix': cap(segments[-1].rstrip('.')),
                'alternative_fix': None, 'targeted_outcome': None}
    paren = re.search(r'\((use|write|change|replace|try)\s+([^)]+)\)', text)
    if paren:
        before = text[:paren.start()].rstrip()
        if not before.endswith(('.', '!', '?')):
            before += '.'
        return {'violation': before.strip(),
                'suggested_fix': cap(f"{paren.group(1)} {paren.group(2)}".strip().rstrip('.')),
                'alternative_fix': None, 'targeted_outcome': None}
    quoted = [q.strip("'") for q in re.findall(r"'[^']*'", text)]
    others = [q for q in quoted if surface and q.lower() != surface.lower()]
    if surface and others:
        return card(f"Change '{surface}' to '{others[-1]}'.")
    if surface:
        return {'violation': text,
                'suggested_fix': f"Change '{surface}' to the correct form.",
                'alternative_fix': None, 'targeted_outcome': None}
    # Last resort: turn the error text itself into an actionable fix.
    return {'violation': text,
            'suggested_fix': 'Review the highlighted word and correct it so the rule above '
                             'is satisfied.',
            'alternative_fix': None, 'targeted_outcome': None}


def num_of(leaf):
    """Grammatical number of a nominal leaf, or None if unmarked."""
    pos = leaf['type']
    surface = _lower(leaf.get('surface',''))
    if pos in NOUN_PLURAL or surface in NOUN_PLURAL_SET:
        return 'pl'
    if pos in NOUN_SINGULAR:
        return 'sg'
    if pos == 'PRP':
        key = PRP_KEY.get(_lower(leaf['surface']))
        return key[1] if key else None
    return None


def person_of(leaf):
    pos = leaf['type']
    if pos.startswith('NN'):
        return '3'
    if pos == 'PRP':
        key = PRP_KEY.get(_lower(leaf['surface']))
        return key[0] if key else None
    return None


def subject_key(leaf):
    if person_of(leaf) is None:
        return None
    return (person_of(leaf), num_of(leaf))


def verb_key(leaf):
    """Agreement key of a finite verb leaf: ('3','sg'), ('*','non3sg'), or None
    (person-neutral: past tense/modals).

    The surface form of 'be'/'have'/'do' is checked *before* the POS fallbacks:
    benepar tags 'was'/'were' as VBD, so a bare ``pos == 'VBD' -> None`` short-
    circuit would make past-tense 'be' agreement invisible ('The pile were').
    """
    pos = leaf['type']
    surface = _lower(leaf['surface'])
    if pos == 'MD':
        return None
    if surface == 'was':
        return ('13', 'sg')
    if surface in ('is', 'has', 'does'):
        return ('3', 'sg')
    if surface == 'am':
        return ('1', 'sg')
    if surface in ('are', 'were', 'have', 'do'):
        return ('*', 'non3sg')
    if pos == 'VBZ':
        return ('3', 'sg')
    if pos == 'VBP':
        return ('*', 'non3sg')
    return None


# Context that licenses the counterfactual subjunctive 'were' with a singular
# subject ('if I were you', 'I wish I were there').  Agreement must not fire on
# these, or a grammatical subjunctive would be reported as a number error.
SUBJUNCTIVE_WERE = re.compile(
    r"\b(if|wish|wishes|wished|as\s+if|as\s+though|suppose|supposing|unless|"
    r"imagine)\b", re.I)


# Subject heads whose grammatical number is genuinely ambiguous ('none of the
# goals were' and 'none of the goals was' are both standard).  Agreement is not
# enforced against these, so a plural verb is never reported as an error.
NUMBER_AMBIGUOUS_HEADS = {
    'none', 'rest', 'half', 'all', 'lot', 'lots', 'plenty', 'more', 'most',
    'some', 'part', 'portion', 'remainder', 'majority', 'minority', 'couple',
    'dozen', 'number', 'variety', 'range', 'series',
}


MANDATIVE_VERBS = {
    'insist', 'insists', 'insisted', 'demand', 'demands', 'demanded',
    'suggest', 'suggests', 'suggested', 'require', 'requires', 'required',
    'recommend', 'recommends', 'recommended', 'propose', 'proposes',
    'proposed', 'request', 'requests', 'requested', 'ask', 'asks', 'asked',
    'order', 'orders', 'ordered', 'command', 'commands', 'commanded',
    'urge', 'urges', 'urged', 'mandate', 'mandates', 'mandated', 'stipulate',
    'stipulates', 'stipulated', 'prefer', 'prefers', 'preferred', 'desire',
    'desires', 'desired', 'important', 'essential', 'necessary', 'vital',
    'imperative', 'crucial',
    'maintain', 'maintains', 'maintained', 'argue', 'argues', 'argued',
    'contend', 'contends', 'contended', 'assert', 'asserts', 'asserted',
}


SMALLCLAUSE_LICENSORS = {
    'make', 'makes', 'made', 'let', 'lets', 'have', 'has', 'had', 'help',
    'helps', 'helped', 'see', 'saw', 'seen', 'hear', 'heard', 'watch',
    'watched', 'feel', 'felt', 'notice', 'noticed', 'observe', 'observed',
}


def _gov_verb(grandparent, sbar_gov):
    """Surface form of the verb governing a complement clause, if identifiable."""
    if not grandparent:
        return ''
    gov = sbar_gov.get(grandparent.get('id'))
    if gov:
        return gov
    if grandparent.get('type') == 'VP':
        head = phrase_head(grandparent)
        if head is not None:
            return _lower(head.get('surface', ''))
    return ''


def _gov_licenses_base(grandparent, sbar_gov):
    """True when the clause's governing verb licenses a bare base form, so the
    base verb must not be treated as a finite agreement target."""
    gov = _gov_verb(grandparent, sbar_gov)
    return gov in MANDATIVE_VERBS or gov in SMALLCLAUSE_LICENSORS


def agree(subject_leaf, verb_leaf):
    """True iff the subject leaf and (finite) verb leaf agree. Deterministic."""
    vk = verb_key(verb_leaf)
    if vk is None:
        return True
    sk = subject_key(subject_leaf)
    if sk is None:
        return True
    if vk == ('13', 'sg'):
        return sk in (('1', 'sg'), ('3', 'sg'))
    if vk == ('*', 'non3sg'):
        return sk != ('3', 'sg')
    if sk == ('2', None):
        return vk == ('*', 'non3sg')
    return vk == sk


def _leaves_list(node, out=None):
    if out is None:
        out = []
    if 'children' not in node:
        out.append(node)
        return out
    for c in node['children']:
        _leaves_list(c, out)
    return out


def _indefinite_article(word):
    """Deterministic 'a'/'an' choice for a (head) word, with phonetic
    exceptions for silent-h and vowel-letter-with-consonant-sound words."""
    w = word.lower().lstrip('\'\"\u2018\u2019\u201c\u201d')
    if not w:
        return 'a'
    if w in AN_SILENT_H_WORDS:
        return 'an'
    if w[0] in 'aeiou' and w not in A_SOUND_CONST_WORDS:
        return 'an'
    return 'a'


def _np_head(node):
    """Head-word pick for an NP, excluding possessive determiners from the noun
    candidates and (only when a determinative is present) falling back to a
    trailing nominal-accepting adjective ('my favorite', 'the rich')."""
    leaves = _leaves_list(node)
    nonposs_nouns = [lf for lf in leaves
                     if (lf['type'] in NOUN_CLASS or lf['type'] == 'CD')
                     and _lower(lf.get('surface', '')) not in POSS_DET_PLAIN]
    if nonposs_nouns:
        return nonposs_nouns[-1]
    determinatives = [lf for lf in leaves
                      if lf['type'] in DET_CLASS or lf['type'] == 'PRP$'
                      or _lower(lf.get('surface', '')) in POSS_DET_PLAIN]
    if determinatives:
        adjs = [lf for lf in leaves if lf['type'] in ADJ_CLASS]
        if adjs:
            return adjs[-1]
    return None


def _np_determinatives(node):
    """List of determinative leaves inside an NP (DT, PRP$, or a bare
    possessive-determiner surface typed as PRP)."""
    return [lf for lf in _leaves_list(node)
            if lf['type'] in DET_CLASS or lf['type'] == 'PRP$'
            or _lower(lf.get('surface', '')) in POSS_DET_PLAIN]


def _needs_indefinite_article_error(np_node, parent_vp=None):
    """Error message if a bare singular common noun heads an argument NP, else
    None. Mass/abstract/activity/institutional nouns are exempt."""
    head = _np_head(np_node)
    if head is None or head['type'] != 'NN':
        return None
    base = _base_form(head)
    surface = _lower(head['surface'])
    if surface in POSS_PRON_SURFACES:
        return None
    if base in NONCOUNT_NOUNS or base in BARE_ARG_NOUNS \
            or surface in NONCOUNT_NOUNS or surface in BARE_ARG_NOUNS:
        return None
    if base in ARTICLE_EXEMPT or surface in ARTICLE_EXEMPT:
        return None
    if is_coordinated(np_node):
        return None
    if _np_determinatives(np_node):
        return None
    leaves = _leaves_list(np_node)
    if leaves:
        # exempt if NP contains a POS
        if any(lf.get('type') == 'POS' for lf in leaves):
            return None
        # leading quantifier/numeral
        first = leaves[0]
        if first.get('type') == 'CD':
            return None
        if _lower(first.get('surface','')) in {'one','two','three','four','five','six','seven','eight','nine','ten','some','any','many','few','several','both','all','most','each','every','another','no','such','what','which','whose'}:
            return None
    # possessive NP as child
    for ch in np_node.get('children', []):
        if ch.get('type') in {'NP','NML','NX'}:
            chleaves = _leaves_list(ch)
            if any(lf.get('type') == 'POS' for lf in chleaves):
                return None
    idx = next((i for i, lf in enumerate(leaves) if lf['id'] == head['id']), None)
    if idx and _lower(leaves[idx - 1]['surface']) in {'next', 'last', 'this', 'that'}:
        return None
    art = _indefinite_article(head['surface'])
    return (f"'{head['surface']}' is a singular noun that names one countable thing, so it "
            f"needs a little word like 'a' or 'the' before it. Add '{art}' (or 'the'/'this').")


def _object_pronoun_error(np_node, verb_leaf):
    """Error message if an NP in an argument position is headed by a nominative
    pronoun (it should be objective after an action verb), else None."""
    if verb_leaf is None or _lower(verb_leaf['surface']) in BE_FORM:
        return None
    h = _np_head(np_node)
    if h is None or h['type'] != 'PRP':
        return None
    surf = _lower(h['surface'])
    if surf not in PRON_SUBJ_PLAIN:
        return None
    target = ruleset.PRONOUN_SUBJECT_TO_OBJECT[surf]
    return (f"The phrase '{np_node['surface']}' is the object of the verb "
            f"'{verb_leaf['surface']}', so it needs the object form. Change "
            f"'{h['surface']}' to '{target}'.")


def phrase_head(node):
    """Deterministic head-word pick for a constituent, or None."""
    label = node['type']
    leaves = _leaves_list(node)
    if label in {'NP', 'NML', 'NX'}:
        return _np_head(node)
    if label == 'VP':
        cands = [lf for lf in leaves if lf['type'] in VERB_CLASS]
        return cands[0] if cands else None
    if label in {'PP', 'PRTP'}:
        cands = [lf for lf in leaves if lf['type'] in PREP_CLASS]
        return cands[0] if cands else None
    if label in {'ADJP'}:
        cands = [lf for lf in leaves if lf['type'] in ADJ_CLASS]
        return cands[-1] if cands else None
    if label in {'ADVP'}:
        cands = [lf for lf in leaves if lf['type'] in ADV_CLASS]
        return cands[0] if cands else None
    if label in SENTENCE_CLASSES:
        cands = [lf for lf in leaves if lf['type'] in VERB_CLASS]
        return cands[0] if cands else None
    return None


def subject_head(node):
    """Head noun of a subject NP, ignoring nouns buried inside a following PP
    (so 'The boy with the bags' resolves to 'boy', enabling rule 2.2) or a
    relative/complement clause (so 'The man who I saw' resolves to 'man', not
    the pronoun inside the clause)."""
    leaves = _leaves_list(node)
    pp_ids = set()
    for ch in node.get('children', []):
        if ch.get('type') in ('PP', 'SBAR'):
            for lf in _leaves_list(ch):
                pp_ids.add(lf['id'])
    cands = [lf for lf in leaves
             if lf['id'] not in pp_ids and lf['type'] in NOUN_CLASS]
    if cands:
        return cands[-1]
    return phrase_head(node)


def clause_subject_and_verb(s_node):
    subj = None
    vp = None
    fallback = None
    for child in s_node['children']:
        if child['type'] == 'NP':
            if fallback is None:
                fallback = child
            head = _np_head(child)
            if head is not None and _lower(head.get('surface', '')) in {
                    'today', 'yesterday', 'tomorrow', 'tonight', 'now',
                    'later', 'then', 'soon'}:
                continue
            if subj is None:
                subj = child
        if child['type'] == 'VP' and vp is None:
            vp = child
    if subj is None:
        subj = fallback
    return subj, vp


def is_coordinated(node):
    """True if the constituent is a coordination (joins two or more conjuncts).

    A subject NP containing a coordinating conjunction (CC/UCP/CONJP) is
    plural in English regardless of the number of any single conjunct head,
    e.g. 'Jaisen and Kielle' (plural) vs 'Jaisen' (singular).
    """
    if 'children' not in node:
        return False
    return any(c['type'] in {'CC', 'CONJP', 'UCP'} for c in node['children'])


def _agreement_ok(skey, vkey):
    """Agreement test for a subject key and a finite-verb key (deterministic)."""
    if vkey is None or skey is None:
        return True
    if vkey == ('13', 'sg'):
        return skey in (('1', 'sg'), ('3', 'sg'))
    if vkey == ('*', 'non3sg'):
        return skey != ('3', 'sg')
    if skey == ('2', None):
        return vkey == ('*', 'non3sg')
    return vkey == skey


class MatrixEvaluator:
    """Deterministic edge evaluation of a node graph."""

    def __init__(self):
        self.details = {}
        self.checker_errors = []
        self.lex_stats = {}
        self._text = ''

    def _sc(self):
        """The sentence being explained, tidied for quotation."""
        return _pretty(self._text)

    @staticmethod
    def _p(node):
        """A node's surface, tidied for quotation."""
        if not isinstance(node, dict):
            return _pretty(node)
        return _pretty(node.get('surface', ''))


    def evaluate(self, root, text=None):
        self.details = {}
        self._text = text or root.get('surface', '')
        # Map each complement SBAR to the verb governing it, so a subjunctive
        # base form can be recognised only when the *governing* verb is
        # mandative (not an unrelated word elsewhere in the sentence).
        self._sbar_gov = {}

        def _scan(node):
            if node.get('type') == 'VP':
                head = phrase_head(node)
                gv = _lower(head.get('surface', '')) if head else ''
                for c in node.get('children', []):
                    if c.get('type') == 'SBAR':
                        self._sbar_gov[c['id']] = gv
            for c in node.get('children', []):
                _scan(c)

        _scan(root)
        self.checker_errors = []
        self.lex_stats = {}
        self._quoted_ids = self._quote_leaf_ids(root)
        self._walk(root)
        self._root_level(root)
        self._merge_findings(root, text)
        for detail in self.details.values():
            cid = detail['constraint']
            rule_id, method = CONSTRAINT_RULE.get(cid, (None, 'T'))
            detail.setdefault('rule_id', rule_id)
            detail.setdefault('method', method)
            detail.setdefault('evidence', self._evidence(root, detail))
            detail.setdefault('findings', [])
            detail['checks'] = _checks_for(detail, self.details)
            if detail['status'] == 'error' and 'remediation' not in detail:
                remediation = self._remediate(root, detail)
                if not remediation:
                    # No constraint-specific repair exists for this error. Derive a
                    # repair from the error text so every detected error carries a
                    # suggested fix the user can act on (never leave an error with
                    # no suggested fix).
                    remediation = _rem_from_text(detail.get('text', ''),
                                                 detail.get('surface', ''))
                # Guarantee a usable, non-empty suggested fix on every error.
                if not remediation.get('suggested_fix'):
                    surf = detail.get('surface') or ''
                    remediation['suggested_fix'] = (
                        f"Change '{surf}' to the word form the sentence needs."
                        if surf else 'Fix the highlighted issue.')
                detail['remediation'] = remediation
        return {'details': self.details, 'summary': self._summarize(root)}

    def _merge_findings(self, root, text):
        """Run the docs/matrix.md rule set and attach findings to their nodes."""
        text = text if text is not None else root.get('surface', '')
        # Every checker runs in isolation; a crash is recorded and degrades the
        # verdict to 'unverified' instead of silently turning into "no errors".
        if licensing is not None:
            findings, self.checker_errors, self.lex_stats = \
                licensing.collect_all(text, root)
        else:  # licensing layer unavailable -> rules/tree only
            findings = ruleset.collect(text, root)
            self.checker_errors = []
            self.lex_stats = {}
        own_error_ids = {nid for nid, d in self.details.items()
                         if isinstance(d, dict) and d.get('status') == 'error'}
        for finding in findings:
            nid = finding.get('node_id')
            detail = self.details.get(nid) if nid else None
            if detail is None:
                detail = self.details.get(root['id'])
            if detail is None:
                continue
            item = dict(finding)
            item['id'] = f"{nid}:{finding.get('rule_id')}"
            if master is not None:
                item['concept'] = master.concept(finding.get('rule_id'))
            detail.setdefault('findings', []).append(item)
            if finding['status'] == 'error':
                # The front end keys token colouring on the node's own status,
                # so a rule finding must also mark its node as an error or the
                # tree renders green despite an INVALID verdict.
                if nid in own_error_ids:
                    detail.setdefault('_own_error', True)
                detail.setdefault('_finding_errors', True)
                # Remember what the matrix itself thought of this node: only a
                # node the matrix already flagged may lend its rewrite to the
                # finding (see the merge below).
                detail.setdefault('_matrix_status', detail['status'])
                detail['status'] = 'error'
        for detail in self.details.values():
            if not detail.pop('_finding_errors', None):
                continue
            errs = [f for f in detail.get('findings', [])
                    if f['status'] == 'error']
            own_error = detail.pop('_own_error', False)
            err = next((f for f in errs
                        if f.get('rule_id') and f.get('rule_id') == detail.get('rule_id')),
                       None)
            if err is None:
                err = next((f for f in errs
                            if f.get('constraint') == detail.get('constraint')),
                           None)
            if err is None:
                if own_error:
                    continue
                err = errs[0] if errs else None
            if err is None:
                continue
            detail['text'] = err['text']
            if err.get('constraint'):
                detail['constraint'] = err['constraint']
            if err.get('role'):
                detail['role'] = err['role']
            rem = err.get('remediation')
            merged = (rem if isinstance(rem, dict)
                      else _rem_from_text(err['text'], detail.get('surface', '')))
            # A finding knows how to describe the problem but not how to rewrite
            # the sentence, so the structural edit the matrix computed for this
            # node is carried over when the finding does not supply one. Only a
            # node the matrix flagged itself may lend its rewrite: a finding
            # that merely reuses a constraint id must never inherit an
            # unrelated correction.
            if detail.pop('_matrix_status', None) == 'error':
                matrix_rem = self._remediate(root, detail) or {}
                for key in ('edit', 'alternative_edit'):
                    if not merged.get(key) and matrix_rem.get(key):
                        merged[key] = matrix_rem[key]
            detail['remediation'] = merged

    def _evidence(self, root, detail):
        """Generic evidence record matching the XAI table in docs/matrix.md."""
        method = detail.get('method')
        if method == 'L':
            return {'used': 'wordlist', 'lookup': detail.get('surface', ''),
                    'accepted': [], 'source': f"rule {detail.get('rule_id')}"}
        if method == 'C':
            return {'used': 'context', 'condition': detail.get('text', ''),
                    'options': [], 'confidence': 0.5}
        parent = self._find_node(root, detail['parent']) if detail.get('parent') else None
        conflict = [{'node': detail['id']}]
        if parent is not None:
            conflict.append({'node': parent['id']})
        return {'used': 'tree', 'subtree': detail['id'],
                'rule': detail.get('rule'), 'conflict': conflict}


    def _walk(self, node, grandparent=None):
        if 'children' in node:
            for child in node['children']:
                self.details[child['id']] = self._edge(node, child, grandparent)
                self._walk(child, node)

    def _quote_leaf_ids(self, node):
        """Id of every leaf falling between a pair of straight double quotes."""
        ids = set()
        inside = False
        for lf in _leaves_list(node):
            if lf.get('surface') == '"':
                inside = not inside
                continue
            if inside:
                ids.add(lf['id'])
        return ids

    def _edge(self, parent, child, grandparent=None):
        if child.get('punct'):
            self._detail(child, parent, 'terminal punctuation', 'C-PUNCT', 'valid',
                         f"The mark '{self._p(child)}' shows where "
                         f"'{self._p(parent)}' ends.")
            return self.details[child['id']]
        leaves = _leaves_list(child)
        if leaves:
            if all(lf['id'] in self._quoted_ids for lf in leaves):
                self._detail(child, parent, 'quoted text', 'C-QUOTE', 'valid',
                             f"The words '{self._p(child)}' are a quotation inside "
                             f"'{self._p(parent)}'. They are someone's exact words, "
                             'so we do not check the grammar inside the quotation.')
                return self.details[child['id']]
        verdict = self._classify(parent, child, grandparent)
        self._detail(child, parent, self._role_for(verdict[1]),
                     verdict[1], verdict[0], verdict[2])
        return self.details[child['id']]

    def _classify(self, parent, child, grandparent=None):
        pt, ct = parent['type'], child['type']
        if pt == 'S':
            if ct == 'NP':
                return self._s_subject(parent, child)
            if ct == 'VP':
                return self._s_predicate(parent, child, grandparent)
            if ct == 'ADJP':
                return ('valid', 'C-SMALL-CLAUSE-PREDICATE',
                        f"The word '{self._p(child)}' describes the subject "
                        f"in '{self._p(parent)}'.")
            if ct == 'ADVP':
                return ('valid', 'C-CLAUSAL-ADVERBIAL',
                        f"The words '{self._p(child)}' add extra "
                        f"information to the whole sentence '{self._p(parent)}'.")
            if ct == 'PP':
                return ('valid', 'C-CLAUSAL-ADVERBIAL',
                        f"The words '{self._p(child)}' add extra information "
                        f"to the whole sentence '{self._p(parent)}'.")
            if ct == 'SBAR':
                return ('valid', 'C-CLAUSAL-COMPLEMENT',
                        f"The words '{self._p(child)}' go with the sentence "
                        f"'{self._p(parent)}' and complete its meaning.")
        if pt == 'NP':
            return self._np_rule(parent, child, grandparent)
        if pt == 'VP':
            return self._vp_rule(parent, child)
        if pt == 'PP':
            if ct == 'CC':
                return ('valid', 'C-COORDINATOR',
                        f"The word '{self._p(child)}' joins the two parts on "
                        'either side of it into one.')
            if ct in PREP_CLASS:
                return ('valid', 'C-HEAD-PREPOSITION',
                        f"The word '{self._p(child)}' links the words after it "
                        f"to the rest of the sentence in '{self._p(parent)}'.")
            if ct == 'NP':
                h = phrase_head(parent)
                head = h['surface'] if h else '?'
                onp = _np_head(child)
                if onp is not None and onp['type'] == 'PRP' and \
                        _lower(onp['surface']) in PRON_SUBJ_PLAIN:
                    target = ruleset.PRONOUN_SUBJECT_TO_OBJECT[_lower(onp['surface'])]
                    return ('error', 'C-PRONOUN-CASE',
                            f"'{onp['surface']}' is a subject form, but it comes after the "
                            f"preposition '{head}'. Change '{onp['surface']}' to '{target}'.")
                return ('valid', 'C-PREP-OBJECT',
                        f"After the word '{head}', we expect a noun. Here it is "
                        f"'{self._p(child)}'; together they make "
                        f"'{self._p(parent)}'.")
        if pt == 'ADJP':
            if ct in ADJ_CLASS:
                return ('valid', 'C-HEAD-ADJECTIVE',
                        f"The describing word '{self._p(child)}' is the main word "
                        f"of '{self._p(parent)}'. The other words there add detail "
                        'about it.')
            if ct in {'RBR', 'RBS'}:
                for sibling in parent['children']:
                    if sibling['type'] in {'JJR', 'JJS'}:
                        return ('error', 'C-COMPARATIVE-DOUBLE',
                                f"The word '{self._p(child)}' and the adjective "
                                f"'{self._p(sibling)}' are both in '{self._p(parent)}', "
                                f"but '{self._p(sibling)}' already shows the comparison, "
                                'so the comparison is marked twice. Keep only one of '
                                'them.')
                return ('valid', 'C-INTENSIFIER',
                        f"The word '{self._p(child)}' makes "
                        f"'{self._p(parent)}' stronger.")
            if ct in ADV_CLASS:
                return ('valid', 'C-INTENSIFIER',
                        f"The word '{self._p(child)}' makes "
                        f"'{self._p(parent)}' stronger.")
            if ct in {'VBN', 'VBG'}:
                return ('valid', 'C-PARTICIPLE-MODIFIER',
                        f"The word '{self._p(child)}' describes "
                        f"'{self._p(parent)}'.")
        if pt == 'ADVP':
            if ct in ADJ_CLASS:
                if _lower(child.get('surface', '')) in PRED_ADJ_EXEMPT:
                    return ('valid', 'C-ADJ-FIXED',
                            f"In '{self._p(parent)}', the word "
                            f"'{self._p(child)}' always keeps this form.")
                return ('error', 'C-ADJ-ADV',
                        f"'{child['surface']}' is an adjective, but an adverb is needed here. "
                        f"Change '{child['surface']}' to "
                        f"'{self._adverbial_form(child['surface'])}'.")
            if ct == 'NP':
                return ('valid', 'C-ADVERBIAL-COMPLEMENT',
                        f"The words '{self._p(child)}' give a time or an amount "
                        f"inside '{self._p(parent)}'.")
            if ct in ADV_CLASS or ct == 'ADVP':
                return ('valid', 'C-HEAD-ADVERBIAL',
                        f"'{self._p(child)}' tells us how, when or where "
                        'something happens.')
            if ct == 'CC':
                return ('valid', 'C-COORDINATOR',
                        f"The word '{self._p(child)}' joins two describing words "
                        'into one.')
        if pt == 'SBAR':
            if ct == 'S':
                return ('valid', 'C-RELATIVE-CLAUSE',
                        f"'{self._p(child)}' is the main part of "
                        f"'{self._p(parent)}'.")
            if ct == 'IN':
                return ('valid', 'C-COMPLEMENTIZER',
                        f"The word '{self._p(child)}' starts the part "
                        f"'{self._p(parent)}' and joins it to the sentence.")
            if ct in {'WHNP', 'WHPP', 'WHADVP', 'WADVP', 'WPP'}:
                return ('valid', 'C-RELATIVE-HEAD',
                        f"The word '{self._p(child)}' starts '{self._p(parent)}' "
                        'and links it to what comes before.')
        if pt == 'WHNP':
            if ct in {'WP', 'WDT', 'WP$'}:
                return ('valid', 'C-RELATIVE-PRONOUN',
                        f"The word '{self._p(child)}' starts '{self._p(parent)}' "
                        'and connects it to the noun it describes.')
            if ct in NOUN_CLASS:
                return ('valid', 'C-RELATIVE-NOUN',
                        f"The noun '{self._p(child)}' is the main word of "
                        f"'{self._p(parent)}', which the question word asks about.")
        if pt in {'WHPP', 'WHADVP', 'WADVP', 'WPP'}:
            return ('valid', 'C-RELATIVE-HEAD',
                    f"The word '{self._p(child)}' starts the question "
                    f"'{self._p(parent)}' and comes first in it.")
        if pt in SENTENCE_CLASSES:
            if ct == 'CC':
                return ('valid', 'C-COORDINATOR',
                        f"The word '{self._p(child)}' joins two sentences into "
                        'one and keeps them equal.')
            if pt != 'S':
                if ct == 'NP':
                    return ('valid', 'C-CLAUSE-SUBJECT',
                            f"'{self._p(child)}' is the subject of "
                            f"'{self._p(parent)}' — the person or thing it is about.")
                if ct == 'VP':
                    return ('valid', 'C-CLAUSE-PREDICATE',
                            f"'{self._p(child)}' is the verb part of "
                            f"'{self._p(parent)}' — it tells what the subject "
                            'does or is.')
        return self._unlisted(parent, child)

    def _unlisted(self, parent, child):
        return ('unlisted', 'C-UNLISTED',
                f"The words '{self._p(child)}' are part of "
                f"'{self._p(parent)}'. There is no special rule for this pair, so "
                'it is accepted.')

    def _s_subject(self, parent, child):
        return ('valid', 'C-SUBJECT-ROLE',
                f"'{self._p(child)}' is the subject of "
                f"'{self._p(parent)}' — the person or thing the sentence is "
                'about.')

    def _s_predicate(self, parent, child, grandparent=None):
        subj, _vp = clause_subject_and_verb(parent)
        # If the subject is immediately followed by a comma, the actual subject
        # is likely the next NP preceding the VP (dislocation). Recompute with
        # the correct subject.
        if subj is not None:
            _kids = parent.get('children', [])
            for _i, _k in enumerate(_kids):
                if _k is subj and _i + 1 < len(_kids) \
                        and _kids[_i + 1].get('type') in (',', ':'):
                    # Look for a later NP that is followed by VP
                    for _j in range(_i + 2, len(_kids)):
                        _ck = _kids[_j]
                        if _ck.get('type') == 'NP':
                            subj = _ck
                            break
                    break
        vp_head = phrase_head(child)
        if vp_head is None:
            return ('error', 'C-TENSE-FINITE',
                    f"The sentence '{self._p(parent)}' has a subject but no verb, so "
                    'it is not complete. Add a verb.')
        if vp_head['type'] in NONFINITE:
            if child['children'] and child['children'][0].get('type') == 'TO':
                return ('valid', 'C-INFINITIVAL-COMPLEMENT',
                        f"The words '{self._p(child)}' name an action after 'to'. "
                        'They have no time of their own; the main verb shows the '
                        'time.')
            # A bare base-form verb with an overt subject in a finite subordinate
            # clause ("... that the boy walk to school") still has to agree with
            # its subject.  Only skip this when the clause is subjunctive or
            # otherwise licensed by a mandative verb ("... that he be on time").
            base_with_subject = (
                vp_head['type'] == 'VB' and subj is not None
                and not _gov_licenses_base(grandparent, self._sbar_gov))
            if not base_with_subject:
                if subj is None:
                    return ('valid', 'C-PREDICATE',
                            f"The words '{self._p(child)}' are a command. There is "
                            'no subject, so the plain form is correct.')
                if grandparent is not None and grandparent['type'] in {
                        'VP', 'SBAR', 'PP', 'S', 'SINV', 'SQ', 'SBARQ', 'NP'}:
                    return ('valid', 'C-SMALL-CLAUSE',
                            f"The words '{self._p(child)}' are inside "
                            f"'{self._p(grandparent)}'. They have no time of their "
                            'own; the main verb shows the time.')
        if subj is None:
            return ('valid', 'C-PREDICATE',
                    f"The words '{self._p(child)}' are the verb part of "
                    f"'{self._p(parent)}'. There is no subject, so there is nothing "
                    'to match.')
        subj_head = subject_head(subj)
        if subj_head is None:
            return ('valid', 'C-PREDICATE',
                    f"The words '{self._p(child)}' are the verb part of "
                    f"'{self._p(parent)}'. The subject is not a single word, so "
                    'this is accepted.')
        # A fronted phrase set off by a comma ('Thanks to this, every task was
        # finished') is a topic/adverbial, not the subject, so agreement must not
        # be checked against it.
        _kids = parent.get('children', [])
        for _i, _k in enumerate(_kids):
            if _k is subj and _i + 1 < len(_kids) \
                    and _kids[_i + 1].get('type') in (',', ':'):
                return ('valid', 'C-SUBJECT-ROLE',
                        f"'{self._p(subj)}' comes before the verb with a comma. "
                        'It is extra information at the front, not the subject '
                        'the verb must match.')
        # Number-ambiguous subject heads ('none of the goals were') accept either
        # a singular or a plural verb, so they are never a number error.
        if _lower(subj_head.get('surface', '')) in NUMBER_AMBIGUOUS_HEADS:
            return ('valid', 'C-PREDICATE',
                    f"The subject '{self._p(subj)}' can be seen as one thing or "
                    f"many, so the verb '{vp_head['surface']}' is correct either "
                    'way.')
        if subj_head['type'] == 'PRP' and _lower(subj_head['surface']) in PRON_OBJ_PLAIN:
            target = ruleset.PRONOUN_OBJECT_TO_SUBJECT[_lower(subj_head['surface'])]
            return ('error', 'C-PRONOUN-CASE',
                    f"'{subj_head['surface']}' is used as the subject of "
                    f"'{self._p(subj)}', but it is the object form. Change it to "
                    f"the subject form '{target}'.")
        coordinated = is_coordinated(subj)
        skey = ('3', 'pl') if coordinated else subject_key(subj_head)
        vkey = verb_key(vp_head)
        if vp_head['type'] == 'VB' and subj is not None \
                and not _gov_licenses_base(grandparent, self._sbar_gov):
            # base form after an overt subject = present, non-3rd-person
            # (finite) rather than a non-finite small clause.
            vkey = ('*', 'non3sg')
        subj_label = '3rd person plural' if coordinated else self._subj_label(subj_head)
        # Handle correlative 'either...or' / 'neither...nor' - agreement with nearest (rightmost) conjunct
        subleaves = _leaves_list(subj)
        correlative = coordinated and any((_lower(l.get('surface','')) if hasattr(l,'get') or isinstance(l,dict) else _lower(str(l))) in ('or','nor') for l in subleaves)
        correlative_b = coordinated and any((_lower(l.get('surface','')) if hasattr(l,'get') or isinstance(l,dict) else _lower(str(l))) in ('not',) for l in subleaves) \
            and any((_lower(l.get('surface','')) if hasattr(l,'get') or isinstance(l,dict) else _lower(str(l))) == 'but' for l in subleaves)
        if correlative or correlative_b:
            # find nearest nominal before verb - look for last PRP/NN in subject
            last_nom = None
            for lf in reversed(subleaves):
                if lf.get('type') in ('PRP','NN','NNS','NNP','NNPS') and _lower(lf.get('surface','')) not in ('either','neither'):
                    last_nom = lf; break
            if last_nom is not None:
                k = subject_key(last_nom)
                if k is not None:
                    skey = k
                    subj_label = self._subj_label(last_nom)
        # quantifier forcing on the full subject NP
        force_pl = False
        force_sg = False
        subleaves = _leaves_list(subj)
        if subleaves:
            surf0 = _lower(subleaves[0]['surface'])
            surf1 = _lower(subleaves[1]['surface']) if len(subleaves) > 1 else ''
            surf2 = _lower(subleaves[2]['surface']) if len(subleaves) > 2 else ''
            # a number of / the number of
            if surf0 == 'a' and 'number' in surf1:
                force_pl = True
            if surf0 == 'a' and surf1 == 'number':
                force_pl = True  # handle both
            if 'number' in (surf0 + ' ' + surf1 + ' ' + surf2):
                if surf0 == 'a':
                    force_pl = True
                if surf0 == 'the':
                    force_sg = True
            # each/every/neither/either/one
            if not correlative and surf0 in ('each','every','neither','either','one'):
                force_sg = True
            # a lot/couple of etc
            if (surf0 in ('a','an') and surf1 in ('lot','couple','few','little','majority')):
                force_pl = True
            if surf0 in ('many','several','plenty','most'):
                force_pl = True
        if force_pl:
            skey = ('3', 'pl')
            subj_label = '3rd person plural'
        if force_sg:
            p = skey[0] if skey else '3'
            skey = (p, 'sg')
            subj_label = self._subj_label({'type': 'PRP', 'surface': 'I'}) if p == '1' else ('3rd person singular' if p == '3' else self._subj_label(subj_head))
        # Counterfactual subjunctive 'were' ('if I were', 'I wish I were') is
        # correct with any subject, so it is never a number error.
        if _lower(vp_head['surface']) == 'were' \
                and SUBJUNCTIVE_WERE.search(self._text or ''):
            return ('valid', 'C-PREDICATE',
                    "The verb 'were' here is used for an unreal situation "
                    "('if I were', 'I wish I were'), so it is correct with any "
                    'subject.')
        # coordinated predicates: every finite conjunct verb must agree with the
        # subject too ('They are stupid and lacks manners.' -> 'lacks' is wrong).
        for h in self._coordinated_predicate_heads(child, vp_head):
            if not _agreement_ok(skey, verb_key(h)):
                sk = skey
                target = (_preserve_case(h['surface'], _third_present(_base_form(h)))
                          if sk == ('3', 'sg') else
                          _preserve_case(h['surface'], _nonthird_present(_base_form(h))))
                return ('error', 'C-SUBJECT-AGREEMENT',
                        f"The verb '{h['surface']}' is the second verb joined to "
                        f"'{self._p(child)}', and it must match the subject "
                        f"'{self._p(subj)}'. Change it to '{target}'.")
        if _agreement_ok(skey, vkey):
            return ('valid', 'C-PREDICATE',
                    f"The subject '{self._p(subj)}' and the verb "
                    f"'{vp_head['surface']}' go together correctly.")
        subj_leaf = _np_head(subj) or phrase_head(subj)
        if subj_leaf is not None and _lower(subj_leaf.get('surface', '')) in COLLECTIVE_NOUNS:
            return ('valid', 'C-COLLECTIVE',
                    f"The subject '{self._p(subj)}' has the group word "
                    f"'{subj_leaf['surface']}', which can mean one group or its "
                    'members, so the verb is accepted.')
        has_pp = any(c.get('type') == 'PP' for c in subj.get('children', []))
        if has_pp:
            target = (_preserve_case(vp_head['surface'], _third_present(_base_form(vp_head)))
                      if skey == ('3', 'sg') else
                      _preserve_case(vp_head['surface'], _nonthird_present(_base_form(vp_head))))
            return ('error', 'C-SUBJ-AGREE-XP',
                    f"The subject '{self._p(subj)}' has extra words after its main "
                    'noun, but they do not change whether it is one thing or many. '
                    f"The verb '{vp_head['surface']}' does not match, so change it "
                    f"to '{target}'.")
        target = (_preserve_case(vp_head['surface'], _third_present(_base_form(vp_head)))
                  if skey == ('3', 'sg') else
                  _preserve_case(vp_head['surface'], _nonthird_present(_base_form(vp_head))))
        return ('error', 'C-SUBJECT-AGREEMENT',
                f"The subject '{self._p(subj)}' has the main word "
                f"'{subj_head['surface']}' ({subj_label}), but the verb "
                f"'{vp_head['surface']}' does not match it. Change "
                f"'{vp_head['surface']}' to '{target}'.")

    def _coordinated_predicate_heads(self, vp, primary):
        """Finite verb heads of predicate-coordination conjuncts other than the
        primary head. Covers nested '... are stupid and lacks manners' (VP (VP ..)
        (CC and) (VP ..)) and flat '... runs and plays football'
        (VP (VBZ ..) (CC and) (VBZ ..))."""
        heads = []
        kids = vp.get('children', []) if isinstance(vp, dict) else []
        if not isinstance(kids, list) or not kids:
            return heads
        if not any(k.get('type') == 'CC' for k in kids):
            return heads
        seen = {primary['id']} if primary is not None else set()
        for k in kids:
            kid_type = k.get('type') if isinstance(k, dict) else None
            if kid_type == 'VP':
                h = phrase_head(k)
                if h is not None and h.get('type') in VERB_CLASS \
                        and h.get('id') not in seen:
                    heads.append(h)
                    seen.add(h['id'])
            elif kid_type in ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD') \
                    and k.get('id') not in seen:
                heads.append(k)
                seen.add(k['id'])
        return heads

    @staticmethod
    def _subj_label(head):
        pos = head['type']
        if pos == 'PRP':
            return {
                ('1', 'sg'): '1st person singular', ('1', 'pl'): '1st person plural',
                ('2', None): '2nd person', ('3', 'sg'): '3rd person singular',
                ('3', 'pl'): '3rd person plural',
            }.get(subject_key(head), 'a pronoun')
        if pos in NOUN_PLURAL:
            return '3rd person plural'
        return '3rd person singular'

    @staticmethod
    def _verb_label(head):
        surface = _lower(head['surface'])
        form = VERB_FORM_LABEL.get(head['type'], head['type'])
        if head['type'] == 'MD':
            return 'a modal auxiliary'
        if surface in BE_FORM or surface in HAVE_FORM or surface in DO_FORM:
            return f"{form} ({surface})"
        return form

    def _np_rule(self, parent, child, grandparent=None):
        ct = child['type']
        head = _np_head(parent)
        if ct in DET_CLASS or ct == 'PRP$' or _lower(child.get('surface', '')) in POSS_DET_PLAIN:
            determinatives = _np_determinatives(parent)
            if len(determinatives) > 1:
                if any((lf.get('surface') or '').strip() == '-'
                       for lf in _leaves_list(parent)):
                    return ('valid', 'C-DETERMINER',
                            f"'{self._p(child)}' is inside the hyphenated group "
                            f"'{self._p(parent)}', so it is not a second word before "
                            'the noun.')
                return ('error', 'C-DET-STACK',
                        f"'{self._p(parent)}' has more than one little word before "
                        f"the noun, and '{self._p(child)}' is one of them. A noun "
                        'needs only one; remove one of them.')
            if head is None:
                if _lower(child.get('surface', '')) in {
                        'i', 'you', 'we', 'they', 'he', 'she', 'it'}:
                    return ('valid', 'C-HEAD-NOUN',
                            f"'{self._p(child)}' is the subject here, so it is not a "
                            'word before a noun.')
                if _lower(child.get('surface', '')) in DEMONSTRATIVE_STANDALONE:
                    return ('valid', 'C-DETERMINER',
                            f"'{self._p(child)}' can stand alone as the whole group "
                            f"'{self._p(parent)}' with no noun after it, which is "
                            'allowed.')
                return ('error', 'C-HEAD-NOUN',
                        f"The word '{self._p(child)}' comes before "
                        f"'{self._p(parent)}', but there is no noun for it to "
                        f"describe. Add a noun after '{self._p(child)}'.")
            if ct in DET_CLASS:
                return self._det_num(parent, child, head)
            return ('valid', 'C-DETERMINER',
                    f"The word '{self._p(child)}' comes before the noun in "
                    f"'{self._p(parent)}' and shows who it belongs to.")
        if ct in NOUN_CLASS:
            if head is not None and child['id'] == head['id']:
                noun_issue = _noun_form_issue(child)
                if noun_issue is not None:
                    singular, expected = noun_issue
                    return ('error', 'C-NOUN-FORM',
                            f"The noun '{self._p(child)}' is the main word of "
                            f"'{self._p(parent)}', but '{self._p(child)}' is not the "
                            f"normal plural of '{singular}'. Change it to '{expected}'.")
                num = num_of(child)
                if (child['type'] == 'NN'
                        and _lower(child['surface']) not in PRONOUN_SURFACES
                        and (grandparent is not None
                             and grandparent['type'] in {'S', 'SINV', 'SQ',
                                                         'SBARQ', 'VP'})):
                    need = _needs_indefinite_article_error(parent)
                    if need is not None:
                        return ('error', 'C-ARTICLE', need)
                head_kind = 'pronoun' if child['type'] == 'PRP' else 'noun'
                return ('valid', 'C-HEAD-NOUN',
                        f"The {head_kind} '{self._p(child)}' is the main word of "
                        f"'{self._p(parent)}'. It tells us whether the group of words "
                        'means one thing or many.')
            return ('valid', 'C-NOUN-ADJUNCT',
                    f"In '{self._p(parent)}', the word '{self._p(child)}' describes "
                    f"the noun '{self._p(head) if head else '?'}' (it tells us what "
                    'kind). It is not a second main noun.')
        if ct in ADJ_CLASS or ct == 'ADJP':
            if ct in ADJ_CLASS and _lower(child.get('surface', '')) in \
                    {'less', 'fewer', 'much', 'many', 'little', 'few'}:
                return self._quantifier_check(parent, child, head)
            return self._modifier_pos(parent, child)
        if ct in {'CD', 'PDT', 'QP'}:
            return self._modifier_pos(parent, child)
        if ct == 'PP':
            return ('valid', 'C-NP-POSTMODIFIER',
                    f"The words '{self._p(child)}' come after the noun in "
                    f"'{self._p(parent)}' and tell us more about it.")
        if ct == 'VP':
            return ('valid', 'C-NP-REDUCED-RELATIVE',
                    f"The words '{self._p(child)}' come after the noun in "
                    f"'{self._p(parent)}' and describe it, without a word like "
                    "'that' or 'which'.")
        if ct in {'SBAR', 'S'}:
            return ('valid', 'C-NP-RELATIVE',
                    f"The words '{self._p(child)}' come after the noun in "
                    f"'{self._p(parent)}' and describe it. They have their own "
                    'subject and verb.')
        if ct == 'CC':
            return ('valid', 'C-COORDINATOR',
                    f"The word '{self._p(child)}' joins the two nouns in "
                    f"'{self._p(parent)}' into one.")
        if ct in {'NP', 'NML', 'NX'}:
            return ('valid', 'C-NP-COMPOUND',
                    f"The words '{self._p(child)}' are part of the larger group "
                    f"'{self._p(parent)}'.")
        return self._unlisted(parent, child)

    def _quantifier_check(self, parent, child, head):
        word = _lower(child['surface'])
        if head is None:
            return ('error', 'C-QUANTIFIER',
                    f"The word '{self._p(child)}' is in '{self._p(parent)}', but "
                    'there is no noun for it to describe.')
        base = _base_form(head)
        num = num_of(head)
        # selection map: word -> required number (None = number-neutral)
        requires = {'less': 'sg', 'much': 'sg', 'little': 'sg',
                    'fewer': 'pl', 'many': 'pl', 'few': 'pl'}
        req = requires[word]
        paired = {'less': 'fewer', 'fewer': 'less', 'much': 'many', 'many': 'much',
                  'little': 'few', 'few': 'little'}[word]
        if num is not None and req != num:
            return ('error', 'C-QUANTIFIER',
                    f"'{self._p(child)}' goes with "
                    f"{'words you cannot count (like water)' if req == 'sg' else 'words you can count (like books)'}, "
                    f"but '{self._p(head)}' is not one. Use '{paired}' instead.")
        return ('valid', 'C-QUANTIFIER',
                f"The word '{self._p(child)}' and the noun '{self._p(head)}' go "
                'together correctly.')

    def _det_num(self, parent, child, head):
        det = _lower(child['surface'])
        numreq = DET_NUMREQ.get(det)
        num = num_of(head) if head is not None else None
        child_num = f"'{head['surface']}'" if head else 'the head noun'
        if numreq is not None and num is not None and numreq in ('sg', 'pl') and numreq != num:
            # "a few boxes", "a dozen eggs", "a little rice" are grammatical:
            # from a + quantifier adjective the head noun's number is not bound by
            # the article.
            leaves = _leaves_list(parent)
            idx = next((i for i, lf in enumerate(leaves) if lf['id'] == child['id']), None)
            after = _lower(leaves[idx + 1]['surface']) if \
                (idx is not None and idx + 1 < len(leaves)) else ''
            if det in ('a', 'an') and after in QUANT_AFTER_A:
                numreq = None
            else:
                return ('error', 'C-DETERMINER-AGREEMENT',
                        f"'{self._p(child)}' goes with "
                        f"{'one thing' if numreq == 'sg' else 'more than one thing'}, "
                        f"but '{self._p(head)}' is "
                        f"{'one thing' if num == 'sg' else 'more than one'}. Change "
                        'one of them so they match.')
        if det in ('a', 'an'):
            leaves = _leaves_list(parent)
            idx = next((i for i, lf in enumerate(leaves) if lf['id'] == child['id']), None)
            if idx is not None and idx + 1 < len(leaves):
                nxt = leaves[idx + 1]['surface']
                need = _indefinite_article(nxt)
                if need != det:
                    return ('error', 'C-ARTICLE-MISMATCH',
                            f"The article '{self._p(child)}' comes before '{nxt}' in "
                            f"'{self._p(parent)}', but '{nxt}' starts with a "
                            f"{'vowel' if need == 'an' else 'consonant'} sound. Change "
                            f"'{self._p(child)}' to '{need}'.")
        if numreq is not None and num is not None:
            return ('valid', 'C-DETERMINER',
                    f"The word '{self._p(child)}' and the noun "
                    f"'{self._p(head)}' in '{self._p(parent)}' both point to one "
                    'thing or to more than one, so they match.')
        return ('valid', 'C-DETERMINER',
                f"The word '{self._p(child)}' comes before the noun "
                f"'{self._p(head) if head else 'of the group'}' in "
                f"'{self._p(parent)}'.")

    def _modifier_pos(self, parent, child):
        head = phrase_head(parent)
        if head is None:
            return ('valid', 'C-MOD-POS',
                    f"'{self._p(child)}' is the main word of "
                    f"'{self._p(parent)}'. There is no noun after it, so it carries "
                    'the meaning here.')
        if child['span'][0] > head['span'][0]:
            return ('error', 'C-MOD-POS',
                    f"The word '{self._p(child)}' comes after the noun "
                    f"'{self._p(head)}' in '{self._p(parent)}', but it should come "
                    f"before it. Move '{self._p(child)}' in front of "
                    f"'{self._p(head)}'.")
        return ('valid', 'C-MOD-POS',
                f"'{self._p(child)}' comes before the noun "
                f"'{self._p(head) if head else '?'}' in '{self._p(parent)}', which "
                'is the right place for it.')

    def _vp_rule(self, parent, child):
        ct = child['type']
        head = phrase_head(parent)
        if ct in VERB_CLASS:
            if self._aux_class(child):
                return self._aux_check(parent, child)
            if head is not None and child['id'] == head['id']:
                return self._verb_head(parent, child)
        if ct in NOUN_CLASS:
            return ('error', 'C-HEAD-VERB',
                    f"'{self._p(parent)}' needs a verb as its main word, but "
                    f"'{self._p(child)}' is a noun. Use a verb here.")
        if ct == 'VP':
            return ('valid', 'C-AUX-COMPLEMENT',
                    f"'{self._p(child)}' is the main verb of the sentence. It works "
                    f"together with the helping word in '{self._p(parent)}'.")
        if ct == 'NP':
            obj_pron = _object_pronoun_error(child, head)
            if obj_pron is not None:
                return ('error', 'C-PRONOUN-CASE', obj_pron)
            return ('valid', 'C-DIRECT-OBJECT',
                    f"'{self._p(child)}' is the object of the verb "
                    f"'{self._p(head) if head else '?'}' in '{self._p(parent)}'. It "
                    'is the thing the action happens to.')
        if ct == 'PP':
            return ('valid', 'C-ADJUNCT',
                    f"'{self._p(child)}' tells us more about the action in "
                    f"'{self._p(parent)}' — such as when, where or how. It is not "
                    'the object.')
        if ct == 'ADJP':
            if self._vp_predicate_adj_err(parent, child):
                return ('error', 'C-ADJ-ADV',
                        f"'{self._p(child)}' comes after the verb "
                        f"'{self._p(head) if head else '?'}' in '{self._p(parent)}', "
                        'but that verb shows an action, not a state. Use the '
                        f"adverb "
                        f"'{self._adverbial_form(child['surface'].split()[-1])}' to "
                        'describe the action.')
            return ('valid', 'C-PREDICATE-ADJECTIVE',
                    f"'{self._p(child)}' comes after the verb in "
                    f"'{self._p(parent)}' and describes the subject.")
        if ct == 'ADVP':
            adv = phrase_head(child)
            if adv is not None and _lower(adv['surface']) in ASTRAY_FLAT_ADV:
                return ('error', 'C-ADJ-ADV',
                        f"'{adv['surface']}' is an adjective, but it describes the action of "
                        f"'{head['surface'] if head else 'the verb'}'. Change "
                        f"'{adv['surface']}' to the adverb "
                        f"'{self._adverbial_form(adv['surface'])}'.")
            return ('valid', 'C-ADVERBIAL',
                    f"'{self._p(child)}' tells us how, when or where the verb "
                    f"'{self._p(head) if head else '?'}' happens.")
        if ct == 'SBAR':
            return ('valid', 'C-CLAUSAL-COMPLEMENT',
                    f"'{self._p(child)}' goes with the verb in "
                    f"'{self._p(parent)}' and completes its meaning.")
        if ct == 'S':
            return ('valid', 'C-SMALL-CLAUSE',
                    f"'{self._p(child)}' goes with the verb in "
                    f"'{self._p(parent)}' and tells us more about the object of "
                    f"'{self._p(head) if head else '?'}'.")
        if ct == 'TO':
            return ('valid', 'C-INFINITIVAL-MARKER',
                    f"The word '{self._p(child)}' comes before a verb to name an "
                    f"action in '{self._p(parent)}'.")
        if ct == 'RP':
            return ('valid', 'C-PARTICLE',
                    f"'{self._p(child)}' goes with the verb "
                    f"'{self._p(head) if head else '?'}' in '{self._p(parent)}' to "
                    'make a phrasal verb.')
        return self._unlisted(parent, child)

    @staticmethod
    def _vp_predicate_adj_err(vp_node, adjp_child):
        """True when an ADJP complement of the VP is not licensed: the verb is a
        plain action verb (not linking/copular) and there is no object NP that the
        adjective could be complementing."""
        head = phrase_head(vp_node)
        if head is None:
            return False
        if _lower(head['surface']) in LINKING_VERB_FORMS:
            return False
        if _clitic_core(head['surface']) == 'be':
            return False
        if _lower(head['surface']) in CONTRACTION_TAILS:
            return False
        adj_leaves = _leaves_list(adjp_child)
        if any(_lower(lf['surface']) in PRED_ADJ_EXEMPT for lf in adj_leaves):
            return False
        earlier = [c for c in vp_node['children']
                   if c['id'] != adjp_child['id']
                   and c['span'][0] < adjp_child['span'][0]]
        if any(c['type'] == 'NP' for c in earlier):
            return False
        return True


    @staticmethod
    def _adverbial_form(word):
        w = word.lower()
        special = {'good': 'well', 'hard': 'hard', 'fast': 'fast', 'late': 'late',
                   'early': 'early', 'long': 'long', 'straight': 'straight',
                   'high': 'high', 'low': 'low', 'deep': 'deeply'}
        if w in special:
            return special[w]
        if w.endswith('ic'):
            return w + 'ally'
        if w == 'true':
            return 'truly'
        if w == 'whole':
            return 'wholly'
        if w.endswith('y'):
            return w[:-1] + 'ily'
        if w.endswith('le') and len(w) > 2 and w[-3] not in 'aeiou':
            return w[:-1] + 'y'
        return w + 'ly'

    def _verb_head(self, parent, child):
        if not _is_valid_verb_form(child):
            expected = 'past tense' if child['type'] == 'VBD' else 'past participle'
            low = _lower(child.get('surface', ''))
            base = _verb_lemma(low) or _base_form(child)
            target = _past_form(base) if expected == 'past tense' else _vbn_form(base)
            return ('error', 'C-VERB-FORM',
                    f"'{self._p(child)}' is the verb in '{self._p(parent)}', but it "
                    f"is not the correct {expected} form. Change it to '{target}'.")
        return ('valid', 'C-HEAD-VERB',
                f"The verb '{self._p(child)}' is the main action word in "
                f"'{self._p(parent)}'.")

    @staticmethod
    def _aux_class(child):
        return child['type'] in {'MD', 'AUX'} or \
            _lower(child.get('surface', '')) in (MODALS | BE_FORM | HAVE_FORM | DO_FORM) \
            or _clitic_core(child.get('surface', '')) is not None

    def _aux_check(self, parent, child):
        surface = _lower(child['surface'])
        clitic = _clitic_core(child['surface'])
        if child['type'] in {'MD', 'AUX'} or surface in MODALS or clitic == 'modal':
            cls = 'modal'
        elif surface in BE_FORM or clitic == 'be':
            cls = 'be'
        elif surface in HAVE_FORM or clitic == 'have':
            cls = 'have'
        elif surface in DO_FORM:
            cls = 'do'
        else:
            return self._verb_head(parent, child)
        verb_node = self._following_verb(parent, child)
        if verb_node is None:
            return self._verb_head(parent, child)
        if cls == 'have' and _lower(verb_node.get('surface', '')) == 'got':
            return ('valid', 'C-AUX-COMPLEMENT',
                    f"'{self._p(child)} {self._p(verb_node)}' means 'possess', so it is "
                    'correct here.')
        if not _is_valid_verb_form(verb_node):
            expected = 'the past participle' if cls == 'have' else 'an -ing or -ed form'
            low = _lower(verb_node.get('surface', ''))
            base = _verb_lemma(low) or _base_form(verb_node)
            target = _vbn_form(base) if cls in ('have', 'be') else base
            return ('error', 'C-VERB-FORM',
                    f"After '{self._p(child)}', the verb must be {expected}, but "
                    f"'{self._p(verb_node)}' is not. Change it to '{target}'.")
        required = {'modal': 'the plain form', 'do': 'the plain form',
                    'have': 'the past participle',
                    'be': 'an -ing or -ed form'}[cls]

        def gloss():
            if cls == 'modal':
                return (f"'{self._p(child)}' shows that the action is possible, "
                        'necessary or allowed. The verb after it stays in its plain '
                        'form.')
            if cls == 'have':
                return (f"'{self._p(child)} {self._p(verb_node)}' shows an action that "
                        'was already finished before another time.')
            if cls == 'be':
                if verb_node.get('type') == 'VBG':
                    return (f"'{self._p(child)} {self._p(verb_node)}' shows an action "
                            'happening now or around now.')
                return (f"'{self._p(child)} {self._p(verb_node)}' shows an action done "
                        'to the subject.')
            return (f"'{self._p(child)} {self._p(verb_node)}' is used to ask a "
                    "question, say 'no', or add emphasis.")

        base_word = _base_form(verb_node)
        expected_word = {'modal': base_word, 'do': base_word,
                         'have': _vbn_form(base_word),
                         'be': _vbg_form(base_word)}[cls]
        # Invariant verbs (come/cut/put/read...) can be tagged VBN by the
        # parser even when they realise the plain form after do/modal.
        if _lower(verb_node.get('surface', '')) == expected_word:
            return ('valid', 'C-AUXILIARY', gloss())
        ok_forms = {'modal': {'VB'}, 'do': {'VB'},
                    'have': {'VBN'}, 'be': {'VBG', 'VBN'}}
        if verb_node['type'] in ok_forms[cls]:
            return ('valid', 'C-AUXILIARY', gloss())
        base = _base_form(verb_node)
        target = {'modal': base, 'do': base,
                  'have': _vbn_form(base),
                  'be': _vbg_form(base)}[cls]
        return ('error', 'C-AUX-FORM',
                f"After '{self._p(child)}', the verb must be {required}, but "
                f"'{self._p(verb_node)}' is not. Change it to '{target}'.")

    @staticmethod
    def _following_verb(parent, aux_child):
        after = [c for c in parent['children'] if c['id'] != aux_child['id']]
        for c in after:
            verb_leaves = _leaves_list(c)
            if verb_leaves and verb_leaves[0]['type'] in VERB_CLASS:
                return verb_leaves[0]
        return None

    # ------------------------------------------------------------------ #
    # Case B: remediation for invalid nodes (deterministic correction)    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_node(root, nid):
        stack = [root]
        while stack:
            node = stack.pop()
            if node['id'] == nid:
                return node
            stack.extend(node.get('children', []))
        return None

    def _remediate(self, root, detail):
        """Deterministic, pedagogical correction guide for an invalid node.

        Always returns a dict (never None) so every error detail carries a
        suggested fix the learner can act on. Falls back to _rem_generic when
        no specific handler applies or a handler cannot produce a fix.
        """
        cid = detail['constraint']
        node = self._find_node(root, detail['id'])
        parent = self._find_node(root, detail['parent']) if detail.get('parent') else None
        if node is None:
            return self._rem_generic(detail)
        if cid == 'C-SUBJECT-AGREEMENT':
            rem = self._rem_agreement(node, parent)
        elif cid == 'C-DETERMINER-AGREEMENT':
            rem = self._rem_det(node, parent)
        elif cid == 'C-NOUN-FORM':
            rem = self._rem_noun_form(node, parent)
        elif cid == 'C-AUX-FORM':
            rem = self._rem_aux(node, parent)
        elif cid == 'C-DET-STACK':
            rem = self._rem_det_stack(node, parent)
        elif cid == 'C-MOD-POS':
            rem = self._rem_mod_pos(node, parent)
        elif cid == 'C-PRONOUN-CASE':
            rem = self._rem_pronoun_case(node, parent)
        elif cid == 'C-ADJ-ADV':
            rem = self._rem_adj_adv(node, parent)
        elif cid == 'C-ARTICLE':
            rem = self._rem_article(node, parent)
        elif cid == 'C-ARTICLE-MISMATCH':
            rem = self._rem_article_mismatch(node, parent)
        elif cid == 'C-CAPITALIZATION':
            rem = self._rem_capitalization(node)
        elif cid == 'C-QUANTIFIER':
            rem = self._rem_quantifier(node, parent)
        elif cid == 'C-HEAD-VERB':
            # The whole tree is needed to read the word before the noun (the
            # auxiliary that fixes the verb form: 'is' -> -ing, 'to' -> plain).
            rem = self._rem_vp_head_noun(node, parent, root)
        elif cid == 'C-COMPARATIVE-DOUBLE':
            rem = self._rem_double_comparative(node, parent)
        elif cid == 'C-HEAD-NOUN':
            rem = self._rem_head_noun(node, parent)
        elif cid == 'C-TENSE-FINITE':
            if detail['role'] == 'fragment root':
                rem = self._rem_fragment(node)
            else:
                rem = self._rem_finite_verb(node, parent)
                if rem is None and node is not None:
                    # The phrase has no verb head at all ("He decided to
                    # stays."): repair the word that has to become the verb,
                    # using the form-aware rewrite from C-HEAD-VERB (after
                    # "to" the plain form is required).
                    leaves = _leaves_list(node)
                    for i, lf in enumerate(leaves):
                        if (i and lf['type'] in (NOUN_CLASS - {'PRP'})
                                and _lower(leaves[i - 1].get('surface', '')) == 'to'):
                            rem = self._rem_vp_head_noun(lf, node, root)
                            break
        else:
            rem = self._rem_generic(detail)
        if rem is None or not rem.get('suggested_fix'):
            rem = self._rem_generic(detail)
        return rem

    def _rem_agreement(self, node, parent):
        subj, vp = clause_subject_and_verb(parent)
        vp_head = phrase_head(node) if vp is None else phrase_head(vp)
        if subj is None:
            return None
        subj_head = subject_head(subj)
        if subj_head is None or vp_head is None:
            return None
        coordinated = is_coordinated(subj)
        sk = ('3', 'pl') if coordinated else subject_key(subj_head)
        # A singular determiner overrides the number of a plural-looking head:
        # 'Every students are' has a singular subject, so the verb must be 'is'.
        det = next((c for c in subj.get('children', [])
                    if c.get('type') == 'DT'), None)
        if det is not None and _lower(det.get('surface', '')) in {
                'every', 'each', 'neither', 'either', 'one', 'this', 'that',
                'another'}:
            sk = ('3', 'sg')
            coordinated = False
        subj_label = '3rd person plural' if coordinated else self._subj_label(subj_head)
        verb_surface = vp_head['surface']
        verb_label = self._verb_label(vp_head)
        violation = (f"The subject '{subj['surface']}' is {subj_label}, but the verb "
                     f"'{verb_surface}' is {verb_label}, so they do not match.")
        target = _preserve_case(verb_surface, _agree_form(vp_head, sk))
        target_pos = _agree_tag(vp_head, sk)
        if target_pos == 'VBZ':
            form_desc = 'the third-person singular present form'
        else:
            form_desc = f"the form used with plural subjects like '{subj_head['surface']}'"
        suggested = (f"Change '{verb_surface}' to '{target}' ({form_desc}) "
                     f"so it matches the {subj_label} subject '{subj['surface']}'.")
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': self._subject_fix_alternative(subj, subj_head, vp_head),
            'targeted_outcome': (f"Subject ({subj_label}) + verb {target_pos} "
                                 f"instead of Subject ({subj_label}) + verb {vp_head['type']}"),
            'edits': [{'node': vp_head['id'], 'replacement': target}],
            'edit': _edit(vp_head['span'][0], vp_head['span'][1], target),
            'alternative_edit': self._subject_alt_edit(subj, subj_head, vp_head),
        }

    def _subject_alt_edit(self, subj, subj_head, vp_head):
        """Deterministic edit for the alternative subject-based agreement repair.

        The subject is changed so that it agrees with the verb that is already
        there: a third-person singular verb needs a singular subject, any other
        verb needs a plural one. The verb keeps its form, so the rewrite stays
        a single, contiguous edit.
        """
        if subj is None or subj_head is None or vp_head is None:
            return None
        if is_coordinated(subj):
            if verb_key(vp_head) != ('3', 'sg'):
                return None
            # A paired subject becomes one singular subject.
            if subj_head['type'] == 'PRP':
                word = 'he or she'
            else:
                word = _preserve_case(subj_head['surface'], _singular_noun(subj_head))
            return _edit(subj['span'][0], subj['span'][1], word)
        vkey = verb_key(vp_head)
        if vkey == ('3', 'sg'):
            if subj_head['type'] == 'PRP':
                swap = {'they': 'he or she', 'we': 'he or she'}.get(_base_form(subj_head))
                if swap is None:
                    return None
                return _edit(subj_head['span'][0], subj_head['span'][1],
                             _preserve_case(subj_head['surface'], swap))
            return _edit(subj_head['span'][0], subj_head['span'][1],
                         _preserve_case(subj_head['surface'], _singular_noun(subj_head)))
        if subj_head['type'] == 'PRP':
            return None
        plural = _plural_noun(_singular_noun(subj_head))
        return _edit(subj_head['span'][0], subj_head['span'][1],
                     _preserve_case(subj_head['surface'], plural))

    @staticmethod
    def _subject_fix_alternative(subj, subj_head, vp_head):
        """Alternative agreement fix: adjust the subject to match the verb."""
        verb_surface = vp_head['surface']
        if is_coordinated(subj):
            if verb_key(vp_head) == ('3', 'sg'):
                if subj_head['type'] == 'PRP':
                    head_word = 'he or she'
                else:
                    head_word = _preserve_case(subj_head['surface'], _singular_noun(subj_head))
                return (f"Or use a single singular subject with '{verb_surface}': drop the "
                        f"conjunction and keep just '{head_word}' instead of the paired "
                        f"subject '{subj['surface']}'.")
            return None
        if verb_key(vp_head) == ('3', 'sg'):
            if subj_head['type'] == 'PRP':
                swap = {
                    'they': 'he or she', 'we': 'he or she', 'they\'re': 'he or she is',
                }.get(_base_form(subj_head))
                if swap is None:
                    return None
                return (f"Or change the subject pronoun '{subj_head['surface']}' to "
                        f"'{swap}' so it matches '{verb_surface}'.")
            singular = _replace_subject_head(subj, subj_head, _singular_noun(subj_head))
            return (f"Or change the subject to the singular '{singular}' instead of "
                    f"'{subj['surface']}', so it matches '{verb_surface}'.")
        plural = _plural_noun(_singular_noun(subj_head))
        if subj_head['type'] == 'PRP':
            swap = {'they': 'they', 'we': 'we', 'he': 'he or she'}.get(_base_form(subj_head))
            return (f"Or keep the subject '{subj['surface']}' and change the verb instead, so "
                    f"the two match.")
        return (f"Or change the subject to the plural "
                f"'{_preserve_case(subj_head['surface'], plural)}' instead of "
                f"'{subj['surface']}', so it matches '{verb_surface}'.")

    def _rem_det(self, node, parent):
        head = phrase_head(parent) if parent else None
        if head is None:
            return None
        numreq = DET_NUMREQ.get(node['surface'].lower())
        num = num_of(head)
        if numreq not in ('sg', 'pl') or num is None or numreq == num:
            return None
        det_s = node['surface']
        noun_s = head['surface']
        violation = (f"'{det_s}' goes with {'singular' if numreq == 'sg' else 'plural'} nouns, "
                     f"but the noun '{noun_s}' is {num}, so they do not match.")
        if numreq == 'pl':
            fix_noun = _preserve_case(noun_s, _plural_noun(_singular_noun(head)))
            suggested = (f"Change '{noun_s}' to the plural '{fix_noun}' so it matches "
                         f"'{det_s}'.")
            alternative = (f"Or change '{det_s}' to a singular word like 'this' or 'a' so it "
                           f"matches the singular noun '{noun_s}'.")
            outcome = f"'{det_s}' + plural noun instead of '{det_s}' + '{noun_s}'"
        else:  # numreq == 'sg', noun plural
            fix_noun = _preserve_case(noun_s, _singular_noun(head))
            suggested = (f"Change '{noun_s}' to the singular '{fix_noun}' so it matches "
                         f"'{det_s}'.")
            alternative = (f"Or change '{det_s}' to a plural word like 'these' or 'those' so "
                           f"it matches the plural noun '{noun_s}'.")
            outcome = f"'{det_s}' + singular noun instead of '{det_s}' + '{noun_s}'"
        alt_map = ({'this': 'these', 'that': 'those', 'every': 'all',
                    'each': 'all', 'another': 'other'}
                   if numreq == 'sg' else
                   {'these': 'this', 'those': 'that', 'many': 'a',
                    'several': 'a', 'both': 'each'})
        alt = alt_map.get(det_s.lower())
        alt_edits = ([{'node': node['id'],
                       'replacement': _preserve_case(det_s, alt)}]
                     if alt else [])
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': alternative,
            'targeted_outcome': outcome,
            'edits': [{'node': head['id'], 'replacement': fix_noun}],
            'alternative_edits': alt_edits,
            'edit': _edit(head['span'][0], head['span'][1], fix_noun),
            'alternative_edit': _edit(node['span'][0], node['span'][1],
                                     _preserve_case(node['surface'],
                                                    'these' if numreq == 'sg' else 'this')),
        }

    @staticmethod
    def _rem_noun_form(node, parent=None):
        issue = _noun_form_issue(node)
        if issue is None:
            return None
        singular, expected = issue
        observed = node['surface']
        if expected == singular:
            correction = (f"Change '{observed}' to '{_preserve_case(observed, expected)}'; "
                          f"'{singular}' is already the complete plural form.")
        else:
            correction = (f"Change '{observed}' to '{_preserve_case(observed, expected)}'; "
                          f"the normal plural of '{singular}' is '{expected}'.")
        fix_word = _preserve_case(observed, expected)
        # The alternative repair swaps the plural for the singular, so a numeral
        # in front of it has to go as well ("two mans" -> "a man").
        alt_edit = _edit(node['span'][0], node['span'][1],
                         _preserve_case(observed, singular))
        if parent is not None:
            numeral = next((lf for lf in _leaves_list(parent) if lf['type'] == 'CD'), None)
            if numeral is not None:
                alt_edit = _edit(numeral['span'][0], node['span'][1],
                                 f"{_preserve_case(numeral['surface'], 'a')} "
                                 f"{_preserve_case(observed, singular)}")
        return {
            'violation': (f"'{observed}' is not the normal plural of '{singular}'."),
            'suggested_fix': correction,
            'alternative_fix': (f"Or use the singular noun '{_preserve_case(observed, singular)}' "
                                "with a singular word like 'a' or 'this'."),
            'targeted_outcome': f"'{singular}' with a correct plural form",
            'edits': [{'node': node['id'], 'replacement': fix_word}],
            'edit': _edit(node['span'][0], node['span'][1],
                          _preserve_case(observed, expected)),
            'alternative_edit': alt_edit,
        }

    def _rem_aux(self, node, parent):
        surface = node['surface'].lower()
        if node['type'] in {'MD', 'AUX'} or surface in MODALS:
            cls = 'modal'
        elif surface in BE_FORM:
            cls = 'be'
        elif surface in HAVE_FORM:
            cls = 'have'
        elif surface in DO_FORM:
            cls = 'do'
        else:
            return None
        verb = self._following_verb(parent, node) if parent else None
        if verb is None or parent is None:
            return None
        got_label = VERB_FORM_LABEL.get(verb['type'], verb['type'])
        base = _verb_lemma(_lower(verb.get('surface', ''))) or _base_form(verb)
        aux_s = node['surface']
        v_s = verb['surface']
        required = ('the plain form' if cls in ('modal', 'do')
                    else "the '-ed' form (past participle)" if cls == 'have'
                    else "the '-ing' form")
        violation = (f"'{aux_s}' is a helping word that must be followed by {required}, "
                     f"but the next verb '{v_s}' is {got_label}.")
        if cls in ('modal', 'do'):
            target = _preserve_case(v_s, base)
            auxiliary_kind = 'modal' if cls == 'modal' else 'do-form'
            suggested = (f"Change '{v_s}' to the plain form '{target}' so it follows "
                         f"'{aux_s}' ({auxiliary_kind}).")
            if cls == 'modal':
                alternative = (f"Or drop '{aux_s}' and use a tensed verb like "
                               f"'{_preserve_case(v_s, _third_present(base))}' (when the "
                               'subject is third-person singular) or the past form.')
            else:
                alternative = (f"Or rephrase so '{v_s}' stands alone as a tensed verb "
                               f"(for example, past or present) instead of using 'do'.")
            outcome = f"'{aux_s}' + '{target}' instead of '{aux_s}' + '{v_s}'"
        elif cls == 'have':
            target = _preserve_case(v_s, _vbn_form(base))
            suggested = (f"Change '{v_s}' to '{target}' after '{aux_s}', because a 'have' "
                          "word is followed by the '-ed' form (past participle).")
            alternative = None
            outcome = f"'{aux_s}' + '{target}' instead of '{aux_s}' + '{v_s}'"
        else:  # be
            target = _preserve_case(v_s, _vbg_form(base))
            suggested = (f"Change '{v_s}' to the '-ing' form '{target}' after '{aux_s}' "
                          f"(or use the '-ed' form for a passive sentence).")
            alternative = (f"Or drop '{aux_s}' and use the simple present "
                            f"'{_preserve_case(v_s, base)}'.")
            outcome = f"'{aux_s}' + '{target}' instead of '{aux_s}' + '{v_s}'"
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': alternative,
            'targeted_outcome': outcome,
            'edits': [{'node': verb['id'], 'replacement': target}],
            'edit': _edit(verb['span'][0], verb['span'][1], target),
            'alternative_edit': (
                _edit(node['span'][0], verb['span'][1],
                      _preserve_case(verb['surface'], _third_present(base)))
                if cls in ('modal', 'do') else None
            ),
        }

    def _rem_det_stack(self, node, parent):
        if parent is None:
            return None
        dets = [c for c in parent['children']
        if c['type'] in DET_CLASS or c['type'] == 'PRP$']
        if len(dets) < 2:
            return None
        keep = dets[0]['surface']
        extras = ', '.join(f"'{d['surface']}'" for d in dets[1:])
        return {
            'violation': (f"The phrase '{parent['surface']}' has more than one determiner "
                          f"({keep} and {extras})."),
            'suggested_fix': f"Remove {extras} and keep '{keep}'.",
            'alternative_fix': (f"Or keep a different one instead: drop '{keep}' and keep "
                                f"{extras}, so only one determiner remains."),
            'targeted_outcome': "One determiner in the phrase",
            'edits': [{'node': d['id'], 'delete': True} for d in dets[1:]],
            'edit': _edit(dets[1]['span'][0], dets[1]['span'][1], ''),
            'alternative_edit': _edit(dets[0]['span'][0], dets[0]['span'][1], ''),
        }

    def _rem_mod_pos(self, node, parent):
        head = phrase_head(parent) if parent else None
        if head is None:
            return None

        # Moving the modifier in front of the head is a single token-range
        # rewrite: replace "head ... modifier" with "modifier head".
        edit = None
        if node['span'][0] == head['span'][1]:      # modifier directly after head
            edit = _edit(head['span'][0], node['span'][1],
                         f"{node['surface']} {head['surface']}")

        return {
            'violation': (f"'{node['surface']}' comes after the noun '{head['surface']}', but "
                          "it should come before it."),
            'suggested_fix': (f"Move '{node['surface']}' in front of '{head['surface']}': "
                              f"'{node['surface']} {head['surface']}'."),
            'alternative_fix': None,
            'targeted_outcome': f"'{node['surface']}' before '{head['surface']}'",
            'edit': edit,
        }

    def _rem_head_noun(self, node, parent):
        if parent is None:
            return None
        # The rule fires on the determiner that has no noun to go with. Other
        # node kinds can wear the same constraint id (e.g. a possessive
        # pronoun); the specific repair still applies to them, but only a
        # determiner gets the noun-inserting edit.
        can_insert = (node is not None
                      and (node['type'] in DET_CLASS or node['type'] == 'PRP'))
        det_s = node['surface'] if node is not None else 'a determiner'
        adj_leaves = [lf for lf in _leaves_list(parent)
                      if lf['type'] in ADJ_CLASS]
        if adj_leaves:
            target = f"{det_s} {adj_leaves[0]['surface']} book"
        else:
            target = f"{det_s} book"
        return {
            'violation': (f"'{det_s}' is used without a noun, but '{parent['surface']}' "
                          'has no noun for it.'),
            'suggested_fix': (f"Add the noun you mean after '{det_s}' — for example, "
                              f"write '{target}' instead of just '{det_s}'."),
            'alternative_fix': (f"Or name the person or thing directly, e.g. 'Maya' "
                                f"instead of '{det_s}'."),
            'targeted_outcome': f"'{det_s}' followed by a noun",
            'edit': (_edit(node['span'][1], node['span'][1],
                           (adj_leaves[0]['surface'] + ' one') if adj_leaves else 'one')
                     if can_insert else None),
        }

    @staticmethod
    def _pronoun_target(surf, objective_needed):
        if objective_needed:
            return {'i': 'me', 'we': 'us', 'he': 'him', 'she': 'her',
                    'they': 'them'}.get(surf)
        return {'me': 'I', 'us': 'we', 'him': 'he', 'her': 'she',
                'them': 'they'}.get(surf)

    def _rem_pronoun_case(self, node, parent):
        # A subject-case error is flagged on the VP (the whole predicate sits in
        # the subject slot), so the pronoun to repair is the clause subject's.
        if node is not None and node['type'] == 'VP' and parent is not None \
                and parent['type'] in SENTENCE_CLASSES:
            subj, _vp = clause_subject_and_verb(parent)
            head = phrase_head(subj) if subj else None
        else:
            head = phrase_head(node) if node else None
        if head is None or head['type'] != 'PRP':
            return None
        objective_needed = parent is not None and parent['type'] not in SENTENCE_CLASSES
        target = self._pronoun_target(_lower(head['surface']), objective_needed)
        if target is None:
            return None
        position = 'the object' if objective_needed else 'the subject'
        demand = 'an object' if objective_needed else 'a subject'
        return {
            'violation': (f"'{head['surface']}' is the wrong form for {position}. "
                          f"(It is the "
                          f"{'subject' if not objective_needed else 'object'} form.)"),
            'suggested_fix': (f"Change '{head['surface']}' to '{target}', because a pronoun "
                              f"used as {demand} needs the '{demand}' form."),
            'alternative_fix': (f"Or use the person's name or another noun in place of "
                                f"'{head['surface']}' instead."),
            'targeted_outcome': f"'{target}' instead of '{head['surface']}'",
            'edits': [{'node': head['id'], 'replacement': target}],
            'edit': _edit(head['span'][0], head['span'][1],
                          _preserve_case(head['surface'], target)),
        }

    def _rem_adj_adv(self, node, parent):
        if node is None:
            return None
        leaf = None
        if node['type'] == 'ADJP':
            adj = phrase_head(node) or (node.get('children') or [None])[0]
            if adj is None:
                return None
            leaf = adj
            wrong, right = adj['surface'], self._adverbial_form(adj['surface'])
        elif node['type'] == 'ADVP':
            adv_leaf = phrase_head(node)
            if adv_leaf is None:
                return None
            leaf = adv_leaf
            wrong, right = adv_leaf['surface'], self._adverbial_form(adv_leaf['surface'])
        else:  # adjective leaf inside an adverb phrase
            leaf = node
            wrong, right = node['surface'], self._adverbial_form(node['surface'])
        if node['type'] == 'ADJP':
            edit_node = adj['id']
        elif node['type'] == 'ADVP':
            edit_node = adv_leaf['id']
        else:
            edit_node = node['id']
        return {
            'violation': (f"'{wrong}' is an adjective, but an adverb is needed here."),
            'suggested_fix': (f"Change '{wrong}' to the adverb '{right}', because this word "
                              'describes how an action is done.'),
            'alternative_fix': (f"Or rephrase so '{wrong}' describes a noun instead of a verb "
                                f"(for example by using a 'be'-type verb like 'seem' before it)."),
            'targeted_outcome': f"'{right}' instead of '{wrong}'",
            'edits': [{'node': edit_node, 'replacement': right}],
            'edit': (_edit(leaf['span'][0], leaf['span'][1], _preserve_case(wrong, right))
                     if 'children' not in leaf else None),
        }

    def _rem_article(self, node, parent):
        if node is None:
            return None
        if node['type'] not in NOUN_CLASS:
            return None
        # The article belongs in front of the whole noun phrase when the phrase
        # opens with modifiers: in "spare instrument" it is the phrase's first
        # word ("a spare instrument"), not the noun, that decides a/an. Naming
        # the noun there would produce "a instrument". A phrase that opens with
        # something else (a stray pronoun, an existential "there") has no safe
        # single-token insertion, so the fix stays a written instruction.
        first = _leaves_list(parent)[0] if parent else None
        leads = first is not None and first['id'] == node['id']
        modifier = (first is not None and not leads
                    and (first['type'] in ADJ_CLASS
                         or first['type'] in (NOUN_CLASS - {'PRP'})
                         or first['type'] in {'VBG', 'VBN'}))
        if modifier:
            target = first['surface']
            phrase = parent['surface']
            target_at = parent['span'][0]
        else:
            target = node['surface']
            phrase = node['surface']
            target_at = node['span'][0]
        art = _indefinite_article(target)
        edit = None
        edit_node = first['id'] if modifier else node['id']
        if modifier or leads:
            if target_at == 0 and first['type'] not in {'NNP', 'NNPS'}:
                # The phrase opens the sentence, so the new determiner carries
                # the capital letter and the first word loses it.
                fixed_phrase = f"{art.capitalize()} {phrase[0].lower() + phrase[1:]}"
                edit = _edit(0, 1, fixed_phrase)
            else:
                fixed_phrase = f"{art} {phrase}"
                edit = _edit(target_at, target_at, art)
            shown = fixed_phrase
        else:
            # No safe insertion point: keep the instruction, skip the preview.
            shown = f"{art} {node['surface']}"
        return {
            'violation': (f"'{node['surface']}' is a singular noun that names one countable "
                          "thing, but it is used without a little word like 'a' or 'the' before "
                          'it.'),
            'suggested_fix': f"Add '{art}' before '{target}' \u2192 '{shown}'.",
            'alternative_fix': (f"Or use another word before it: 'the {node['surface']}', "
                                f"'this {node['surface']}', or 'my {node['surface']}'."),
            'targeted_outcome': f"'{node['surface']}' with a determiner before it",
            'edits': [{'node': edit_node, 'insert_before': art}],
            'edit': edit,
        }

    def _rem_article_mismatch(self, node, parent):
        if parent is None:
            return None
        leaves = _leaves_list(parent)
        idx = next((i for i, lf in enumerate(leaves) if lf['id'] == node['id']), None)
        if idx is None or idx + 1 >= len(leaves):
            return None
        nxt = leaves[idx + 1]['surface']
        need = _indefinite_article(nxt)
        if need == node['surface'].lower() or need not in ('a', 'an'):
            return None
        return {
            'violation': (f"'{node['surface']}' is the wrong word before '{nxt}', because "
                          f"'{nxt}' starts with a "
                          f"{'vowel' if need == 'an' else 'consonant'} sound."),
            'suggested_fix': (f"Change '{node['surface']}' to '{need}': "
                              f"'{need} {nxt}'."),
            'alternative_fix': None,
            'targeted_outcome': f"'{need}' instead of '{node['surface']}'",
            'edits': [{'node': node['id'], 'replacement': need}],
            'edit': _edit(node['span'][0], node['span'][1],
                          _preserve_case(node['surface'], need)),
        }

    @staticmethod
    def _rem_capitalization(node):
        words = node['surface'].split()
        if not words or not words[0]:
            return None
        first = words[0]
        rewritten = first[0].upper() + first[1:]
        leaves = _leaves_list(node)
        edit_node = leaves[0]['id'] if leaves else node['id']
        return {
            'violation': (f"The sentence begins with '{first}' without a capital letter."),
            'suggested_fix': (f"Capitalize the first letter: '{first}' \u2192 '{rewritten}', "
                              f"so the sentence reads '{rewritten + ' ' + ' '.join(words[1:])}'."),
            'alternative_fix': None,
            'targeted_outcome': "The sentence starts with a capital letter",
            'edits': [{'node': edit_node, 'replacement': rewritten}],
            'edit': _edit(0, 1, rewritten),
        }

    @staticmethod
    def _rem_quantifier(node, parent):
        word = _lower(node['surface'])
        if word not in ('less', 'fewer') or parent is None:
            return None
        head = _np_head(parent)
        noun_s = head['surface'] if head else 'the noun'
        if word == 'less':
            suggested = (f"Change '{node['surface']}' to 'fewer', because '{noun_s}' is a "
                         f"plural noun you can count: '{node['surface']} {noun_s}' \u2192 "
                         f"'fewer {noun_s}'.")
            alternative = (f"Or change the noun so it is not countable, letting '{node['surface']}' "
                           f"stay \u2014 for example use the singular '{head['surface']}' as a "
                           'mass noun.')
            outcome = f"'fewer {noun_s}' instead of 'less {noun_s}'"
        else:
            suggested = (f"Change '{node['surface']}' to 'less', because '{noun_s}' is a "
                         f"singular noun that is not counted: '{node['surface']} {noun_s}' \u2192 "
                         f"'less {noun_s}'.")
            alternative = (f"Or make '{noun_s}' plural and countable, so 'fewer' works: "
                           f"'{_plural_noun(_singular_noun(head))}'.")
            outcome = f"'less {noun_s}' instead of 'fewer {noun_s}'"

        new_word = 'fewer' if word == 'less' else 'less'

        return {
            'violation': (f"'{node['surface']}' does not match the noun '{noun_s}'."),
            'suggested_fix': suggested,
            'alternative_fix': alternative,
            'targeted_outcome': outcome,
            'edits': [{'node': node['id'],
                       'replacement': 'fewer' if word == 'less' else 'less'}],
            'edit': _edit(node['span'][0], node['span'][1],
                          _preserve_case(node['surface'], new_word)),
            'alternative_edit': (
                _edit(head['span'][0], head['span'][1],
                      _preserve_case(head['surface'],
                                     _plural_noun(_singular_noun(head))))
                if word == 'fewer' and head is not None else None
            ),
        }

    def _rem_double_comparative(self, node, parent):
        if parent is None:
            return None
        marker = node['surface'] if node is not None else 'more'
        sibling = None
        for c in parent['children']:
            if c['type'] in {'JJR', 'JJS'}:
                sibling = c
                break
        if sibling is None:
            return None
        plain = sibling['surface']
        if plain.endswith('est'):
            plain = plain[:-3]
        elif plain.endswith('er'):
            plain = plain[:-2]
        return {
            'violation': (f"'{marker}' and '{sibling['surface']}' both show that something is "
                          f"{'more of a quality' if sibling['type'] == 'JJR' else 'the most'}, "
                          'so the comparison is said twice.'),
            'suggested_fix': (f"Keep just '{sibling['surface']}' and drop '{marker}'."),
            'alternative_fix': (f"Or keep '{marker}' and write the plain form: "
                                f"'{marker} {plain}' instead of '{sibling['surface']}'."),
            'targeted_outcome': f"'{sibling['surface']}' alone (no '{marker}')",
            'edits': [{'node': node['id'], 'delete': True}],
            'edit': _edit(node['span'][0], node['span'][1], ''),
            # No alternative rewrite: keeping the marker needs a plain-form
            # adjective ("more good than before" is not English), so dropping
            # the marker is the only sound repair.
            'alternative_edit': None,
        }

    def _rem_vp_head_noun(self, node, parent, root=None):
        noun_s = node['surface'] if node is not None else '?'
        phrase_s = parent['surface'] if parent else ''
        base = _lower(noun_s)
        if base.endswith('ies') and len(base) > 3:
            base = base[:-3] + 'y'
        elif base.endswith('es') and len(base) > 3:
            base = base[:-2]
        elif base.endswith('s') and len(base) > 2 and base not in {'is', 'has', 'does'}:
            base = base[:-1]
        # The word right before the noun fixes the verb form that is needed:
        # after 'is/are/was/were' it is the '-ing' form, after 'to' the plain
        # form, and so on.  That auxiliary is a sibling of the VP in the tree,
        # so read it from the whole sentence's leaves.
        prev = ''
        if node is not None and root is not None:
            for lf in _leaves_list(root):
                if lf['span'][1] <= node['span'][0]:
                    prev = _lower(lf.get('surface', ''))
                else:
                    break
        if prev in BE_FORM:
            target = _preserve_case(noun_s, _vbg_form(base))
            fix = (f"Change '{noun_s}' to '{target}' (the '-ing' form), because "
                   f"after '{prev}' the verb takes '-ing'.")
        elif prev in HAVE_FORM:
            target = _preserve_case(noun_s, _vbn_form(base))
            fix = (f"Change '{noun_s}' to '{target}' (the '-ed' form), because "
                   f"after '{prev}' the verb takes '-ed'.")
        elif prev == 'to' or prev in DO_FORM or prev in MODALS:
            target = _preserve_case(noun_s, base)
            fix = (f"Change '{noun_s}' to the plain form '{target}', because after "
                   f"'{prev}' the verb keeps its plain form.")
        else:
            target = _preserve_case(noun_s, _third_present(base)) if base else noun_s
            if target.lower() == noun_s.lower() and base:
                target = _preserve_case(noun_s, base)
            fix = (f"Change '{noun_s}' to the verb '{target}', because this part of "
                   'the sentence must have a verb (an action word).')
        return {
            'violation': (f"'{noun_s}' is a noun, but '{phrase_s}' needs a verb "
                          '(an action word) here.'),
            'suggested_fix': fix,
            'alternative_fix': 'Or use a different verb if your sentence means a '
                               'different action.',
            'targeted_outcome': f"a verb in place of the noun '{noun_s}'",
        }

    def _rem_finite_verb(self, node, parent):
        vp_head = phrase_head(node) if node else None
        if vp_head is None:
            return None
        h = vp_head['surface']
        base = _base_form(vp_head)
        got = VERB_FORM_LABEL.get(vp_head['type'], vp_head['type'])
        finite = _preserve_case(h, _third_present(base))
        violation = (f"The main verb '{h}' is {got}; a sentence needs a verb with a "
                     'time (present or past).')
        if vp_head['type'] == 'VBG':
            suggested = (f"Change '{h}' to a full verb like '{finite}', or add the "
                         f"helping word 'is' before it: 'is {h}'.")
            outcome = f"'{h}' changed to '{finite}' or 'is {h}'"
        elif vp_head['type'] == 'VBN':
            suggested = (f"Add a form of 'be' before '{h}' for a passive sentence: "
                         f"'is {h}'; or change '{h}' to a full verb like '{finite}'.")
            outcome = f"'{h}' changed to 'is {h}' or '{finite}'"
        else:  # VB base
            suggested = (f"Change '{h}' to '{finite}' (for a singular subject like 'he' "
                         f"or 'she'), or add 'does' before it: 'does {h}'.")
            outcome = f"'{h}' changed to '{finite}' or 'does {h}'"
        return {
            'violation': violation,
            'suggested_fix': suggested,
            'alternative_fix': None,
            'targeted_outcome': outcome,
            'edit': (
                _edit(vp_head['span'][0], vp_head['span'][0], 'is')
                if vp_head['type'] in ('VBG', 'VBN')
                else _edit(vp_head['span'][0], vp_head['span'][1], finite)
            ),
        }

    def _rem_fragment(self, node):
        words = node['surface'].split()
        stripped = ' '.join(w for w in words
                            if not all(ch in '.,;:!?\u2018\u2019\u201c\u201d' for ch in w))
        example = f"'{stripped} runs.'" if stripped else "'The boy runs.'"
        return {
            'violation': (f"This input reads as a {node['type']}, not a full sentence, because "
                          'it has no verb in a tensed form.'),
            'suggested_fix': (f"Add a verb so it becomes a full sentence — for "
                              f"example {example}"),
            'alternative_fix': None,
            'targeted_outcome': "A complete sentence with a subject and a verb",
        }

    def _rem_generic(self, detail):
        return _rem_from_text(detail['text'], detail.get('surface', ''))

    def _root_level(self, root):
        if root['type'] in SENTENCE_CLASSES:
            words = root['surface'].split()
            first = words[0] if words else ''
            if first and first[0].isalpha() and first[0].islower():
                self._detail(root, None, 'sentence capitalization', 'C-CAPITALIZATION',
                             'error',
                             f"The sentence begins with '{first}' in lower case. A "
                             'sentence must start with a capital letter.')
                return
            self._detail(root, None, 'sentence root', 'C-ROOT', 'valid',
                         f"The whole sentence '{self._p(root)}' has a subject and a "
                         'verb, so it is a complete sentence.')
            return
        self._detail(root, None, 'fragment root', 'C-TENSE-FINITE', 'error',
                     f"This input '{self._p(root)}' has no subject and verb, so it is "
                     'not a complete sentence.')

    def _detail(self, node, parent, role, constraint, status, text):
        text = _strip_preface(text, self._sc())
        self.details[node['id']] = {
            'id': node['id'],
            'type': node['type'],
            'pos': node.get('pos'),
            'surface': node.get('surface', ''),
            'span': node['span'],
            'parent': parent['id'] if parent else None,
            'rule': _rule_for(node),
            'children_ids': [c['id'] for c in node['children']] if 'children' in node else [],
            'children': [{'id': c['id'], 'type': c['type'], 'surface': c.get('surface')}
                         for c in node['children']] if 'children' in node else [],
            'role': role,
            'constraint': constraint,
            'status': status,
            'text': text,
            'findings': [],
        }

    def _role_for(self, constraint):
        return {
            'C-SUBJECT-ROLE': 'clause subject',
            'C-PREDICATE': 'the verb part of the clause',
            'C-SUBJECT-AGREEMENT': 'subject-verb agreement link',
            'C-HEAD-NOUN': 'head noun',
            'C-NOUN-FORM': 'noun form',
            'C-NOUN-ADJUNCT': 'noun adjunct',
            'C-DETERMINER': 'determiner',
            'C-DETERMINER-AGREEMENT': 'determiner-noun agreement link',
            'C-DET-STACK': 'determiner stacking',
            'C-MOD-POS': 'NP modifier position',
            'C-NP-POSTMODIFIER': 'postmodifier',
            'C-NP-REDUCED-RELATIVE': 'reduced relative clause',
            'C-NP-RELATIVE': 'relative clause',
            'C-COORDINATOR': 'coordinator',
            'C-HEAD-VERB': 'verb head',
            'C-INFINITIVAL-COMPLEMENT': 'infinitival complement',
            'C-INFINITIVAL-MARKER': 'infinitival marker',
            'C-AUXILIARY': 'auxiliary verb',
            'C-AUX-COMPLEMENT': 'auxiliary complement',
            'C-AUX-FORM': 'auxiliary-verb form',
            'C-TENSE-FINITE': 'complete verb',
            'C-DIRECT-OBJECT': 'direct object',
            'C-ADJUNCT': 'VP modifier',
            'C-PREDICATE-ADJECTIVE': 'describing word after the verb',
            'C-ADVERBIAL': 'adverbial modifier',
            'C-CLAUSAL-COMPLEMENT': 'clausal complement',
            'C-PARTICLE': 'verb particle',
            'C-HEAD-PREPOSITION': 'head preposition',
            'C-PREP-OBJECT': 'prepositional object',
            'C-HEAD-ADJECTIVE': 'head adjective',
            'C-INTENSIFIER': 'intensifier',
            'C-PARTICIPLE-MODIFIER': 'participle modifier',
            'C-HEAD-ADVERBIAL': 'head adverbial',
            'C-CLAUSE-SUBJECT': 'clause subject',
            'C-CLAUSE-PREDICATE': 'the verb part',
            'C-CLAUSAL-ADVERBIAL': 'clausal adverbial',
            'C-RELATIVE-CLAUSE': 'relative/complement clause',
            'C-RELATIVE-HEAD': 'relative-clause head',
            'C-RELATIVE-PRONOUN': 'relative pronoun',
            'C-RELATIVE-NOUN': 'wh-phrase nominal head',
            'C-COMPLEMENTIZER': 'complementizer',
            'C-NP-COMPOUND': 'NP-internal phrase',
            'C-PUNCT': 'terminal punctuation',
            'C-ROOT': 'sentence root',
            'C-CAPITALIZATION': 'sentence capitalization',
            'C-PRONOUN-CASE': 'pronoun case',
            'C-ADJ-ADV': 'adjective-adverb confusion',
            'C-ARTICLE': 'article omission',
            'C-ARTICLE-MISMATCH': 'article selection',
            'C-QUANTIFIER': 'quantifier-noun agreement',
            'C-SMALL-CLAUSE': 'small-clause complement',
            'C-SMALL-CLAUSE-PREDICATE': 'describing word in the clause',
            'C-ADVERBIAL-COMPLEMENT': 'adverbial complement',
            'C-COMPARATIVE-DOUBLE': 'double comparative',
            'C-UNLISTED': 'unrated edge',
        }.get(constraint, 'unrated')

    def _summarize(self, root):
        edges = [d for nid, d in self.details.items() if nid != root['id']]
        valid = [d for d in edges if d['status'] == 'valid']
        errors = [d for d in edges if d['status'] == 'error']
        unlisted = [d for d in edges if d['status'] == 'unlisted']
        root_detail = self.details.get(root['id'])
        root_error = root_detail is not None and root_detail['status'] == 'error'
        error_findings = []
        suggestions = []
        unverified = []
        for detail in self.details.values():
            for finding in detail.get('findings', []):
                if finding['status'] == 'error':
                    error_findings.append(finding)
                elif finding['status'] == 'suggestion':
                    suggestions.append(finding)
                elif finding['status'] == 'unverified':
                    unverified.append(finding)
        violations = list(errors) + error_findings
        if root_error:
            violations.append(root_detail)
        if root_error:
            message = root_detail['text']
        elif errors:
            message = errors[0]['text']
        elif error_findings:
            message = error_findings[0]['text']
        elif unverified or self.checker_errors:
            message = (f"The rules found no definite mistake in "
                       f"'{root['surface']}', but {len(unverified)} word(s) could not be "
                       'confirmed and the check ran into an issue, so this sentence cannot '
                       'yet be marked fully grammatical.')
        else:
            message = (f"'{root['surface']}' is grammatical: every word is used in an "
                       'allowed way.')
        if violations:
            verdict = 'ungrammatical'
        elif unverified or self.checker_errors:
            verdict = 'unverified'
        else:
            verdict = 'grammatical'
        content = self.lex_stats.get('content', 0)
        return {
            # 'valid' keeps its old meaning (no violation found).  UIs should now
            # key on 'verdict' so "unverified" is not shown as a green tick.
            'verdict': verdict,
            'lexical_coverage': (round(self.lex_stats.get('licensed', 0) / content, 3)
                                 if content else None),
            'unverified': [f.get('id') for f in unverified],
            'checker_errors': list(self.checker_errors),
            'valid': len(violations) == 0,
            'valid_edges': len(valid),
            'violated_edges': len(errors) + len(error_findings),
            'violations': [d.get('id') for d in violations],
            'unrated_edges': len(unlisted),
            'suggested': len(suggestions),
            'suggestions': [f.get('id') for f in suggestions],
            'constraints_fired': sorted({d['constraint'] for d in violations}),
            'root_error': root_error,
            'explanation': message,
        }


def evaluate(root, text=None):
    return MatrixEvaluator().evaluate(root, text=text)