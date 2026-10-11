"""SynTutor rule matrix (docs/matrix.md) expressed as deterministic checks.

This module is the machine-readable twin of ``docs/matrix.md``. Every rule in
that document is registered here with its check method:

    T  tree rule            -- deterministic over the parsed constituency tree
    L  word list/morphology -- deterministic lookup against a curated list
    C  context/meaning      -- cannot be decided deterministically, so a hit is
                               reported as a *suggestion* (never as an error)

For each rule the checker returns an *evidence* record that matches the XAI
table at the bottom of ``docs/matrix.md``:

    T -> the specific nodes/edges in conflict and the rule that fired
    L -> the word-list entry that was looked up (accepted vs. observed form)
    C -> the triggering condition, the evidence per option, and a confidence

Nothing here imports ``server.matrix`` (the dependency runs the other way), so
the checks can be unit-tested and audited in isolation.
"""

METHOD_T = 'T'
METHOD_L = 'L'
METHOD_C = 'C'

# --------------------------------------------------------------------------- #
# The rule book: id -> (name, example error, check method)                     #
# Mirrors docs/matrix.md exactly.                                             #
# --------------------------------------------------------------------------- #
RULEBOOK = {
    # 1. Word forms
    '1.1': ('Regular noun plurals', 'boxs', METHOD_L),
    '1.2': ('Irregular noun plurals', 'childs', METHOD_L),
    '1.3': ('Possessive \u2018s / s\u2019', 'the boys toy', METHOD_T),
    '1.4': ('Verb endings (-s, -ed, -ing)', 'runing', METHOD_L),
    '1.5': ('Irregular past tense', 'goed', METHOD_L),
    '1.6': ('Irregular past participle', 'had went', METHOD_L),
    '1.7': ('Comparative/superlative formation', 'gooder, more tall', METHOD_L),
    '1.8': ('Adverb formation', 'happyly', METHOD_L),
    '1.9': ('Reflexive forms', 'hisself', METHOD_L),
    '1.10': ('Homophones (its/it\u2019s, their/there)', 'Its raining', METHOD_T),
    '1.11': ('Contractions', 'dont', METHOD_L),
    '1.12': ('Spelling', 'recieve', METHOD_L),
    '1.13': ('Numerals and measures', 'two hundreds', METHOD_L),
    # 2. Agreement
    '2.1': ('Subject-verb, simple', 'The boy go', METHOD_T),
    '2.2': ('Subject-verb across intervening phrase', 'The boy with the bags go', METHOD_T),
    '2.3': ('Coordinated subjects (and / or / nor)', 'Tom or Ann are', METHOD_T),
    '2.4': ('Existential there', 'There is books', METHOD_T),
    '2.5': ('Collective and notional nouns', 'The team are', METHOD_C),
    '2.6': ('Questions and inversion', 'Where is the books?', METHOD_T),
    '2.7': ('Relative clauses', 'the boys who plays', METHOD_T),
    '2.8': ('Indefinite pronouns', 'Everyone have', METHOD_T),
    '2.9': ('Quantified subjects', 'A number of / Each of the boys are', METHOD_T),
    '2.10': ('Determiner-noun number', 'these book', METHOD_T),
    '2.11': ('Quantifier-noun', 'less books, much books', METHOD_T),
    '2.12': ('Pronoun-antecedent', 'The girls lost her bag', METHOD_C),
    '2.13': ('Correlatives', 'Either he or I am', METHOD_T),
    '2.14': ('Reflexive-antecedent', 'She hurt himself', METHOD_T),
    # 3. Articles and determiners
    '3.1': ('a/an choice', 'a apple', METHOD_L),
    '3.2': ('Missing article', 'I saw dog', METHOD_T),
    '3.3': ('Unnecessary article', 'She plays the football', METHOD_C),
    '3.4': ('Definite vs indefinite', 'I saw the dog (first mention)', METHOD_C),
    '3.5': ('Stacked determiners', 'the my book', METHOD_T),
    '3.6': ('Determiner with no noun', 'the my', METHOD_T),
    '3.7': ('some/any', 'I don\u2019t have some money', METHOD_T),
    '3.8': ('each/every/all/whole/other/another', 'another books', METHOD_T),
    # 4. Nouns
    '4.1': ('Countable vs uncountable', 'informations, an advice', METHOD_L),
    '4.2': ('Noun as modifier (number)', 'a ten-years plan', METHOD_T),
    '4.3': ('Plural-only / singular -s nouns', 'a scissors, the news are', METHOD_L),
    # 5. Pronouns
    '5.1': ('Case, simple', 'Me go, between you and I', METHOD_T),
    '5.2': ('Case in coordination and comparison', 'Me and him went, taller than I', METHOD_T),
    '5.3': ('Ambiguous reference', 'Tom told Jim he...', METHOD_C),
    '5.4': ('Relative pronoun choice', 'the man which', METHOD_T),
    '5.5': ('Dummy it/there', 'Is raining', METHOD_T),
    '5.6': ('Possessive pronoun vs determiner', 'This is my', METHOD_T),
    '5.7': ('Reflexive vs ordinary pronoun', 'Myself am happy', METHOD_T),
    # 6. Verbs
    '6.1': ('Auxiliary + verb form', 'She can goes', METHOD_T),
    '6.2': ('Finite main verb', 'She going to school', METHOD_T),
    '6.3': ('Missing verb / copula', 'She very happy', METHOD_T),
    '6.4': ('Passive formation', 'The house build', METHOD_T),
    '6.5': ('Intransitive passive', 'It was happened', METHOD_L),
    '6.6': ('Stative verbs in progressive', 'I am knowing', METHOD_L),
    '6.7': ('Tense consistency', 'He said he will come', METHOD_C),
    '6.8': ('Transitivity', 'discuss about, arrived the station', METHOD_L),
    '6.9': ('Gerund vs infinitive', 'enjoy to swim', METHOD_L),
    '6.10': ('to + base form', 'to goes', METHOD_T),
    '6.11': ('Phrasal verbs', 'pick up it', METHOD_L),
    '6.12': ('Modals and semi-modals', 'must to go, use to go', METHOD_T),
    '6.13': ('Question formation', 'Where you are going?', METHOD_T),
    '6.14': ('Negation', 'I don\u2019t have no money', METHOD_T),
    '6.15': ('Imperatives', 'Don\u2019t goes', METHOD_T),
    '6.16': ('Conditionals', 'If I will go', METHOD_T),
    '6.17': ('Subjunctive and wish', 'I wish I was', METHOD_C),
    '6.18': ('Reported speech', 'She said me', METHOD_T),
    '6.19': ('Causatives and perception verbs', 'made me to cry', METHOD_T),
    '6.20': ('Verb + clause patterns', 'suggest him to go', METHOD_L),
    # 7. Adjectives and adverbs
    '7.1': ('Adjective vs adverb', 'runs quick', METHOD_T),
    '7.2': ('Adjective order', 'red big car', METHOD_L),
    '7.3': ('Adverb placement', 'I like very much it', METHOD_T),
    '7.4': ('Participial adjectives', 'I am boring', METHOD_L),
    '7.5': ('Intensifiers and degree', 'enough big, too much good', METHOD_T),
    '7.6': ('Comparative structures', 'more taller, as tall than', METHOD_T),
    '7.7': ('Modifier position', 'the car red', METHOD_T),
    # 8. Prepositions
    '8.1': ('Wrong preposition', 'depends in', METHOD_C),
    '8.2': ('Missing preposition', 'listen music', METHOD_C),
    '8.3': ('Unnecessary preposition', 'discuss about', METHOD_L),
    '8.4': ('Adjective + preposition', 'interested on', METHOD_L),
    '8.5': ('Time and place (in/on/at)', 'on 5 pm', METHOD_L),
    '8.6': ('Preposition + gerund', 'look forward to see', METHOD_T),
    # 9. Sentence structure
    '9.1': ('Fragment', 'Because I was late.', METHOD_T),
    '9.2': ('Missing subject', 'Went to school.', METHOD_T),
    '9.3': ('Run-on / fused sentence', 'I like tea she likes coffee', METHOD_T),
    '9.4': ('Comma splice', 'I came, I saw.', METHOD_T),
    '9.5': ('Double subject', 'My brother he...', METHOD_T),
    '9.6': ('Word order in statements', 'Yesterday went I', METHOD_T),
    '9.7': ('Missing or extra word', 'She is very the happy', METHOD_C),
    '9.8': ('Parallel structure', 'to run, swimming', METHOD_T),
    '9.9': ('Conjunction pairing', 'Although..., but...', METHOD_L),
    '9.10': ('Relative clause formation', 'the man who I saw him', METHOD_T),
    '9.11': ('Dangling / misplaced modifier', 'Walking home, the rain started', METHOD_C),
    '9.12': ('Redundancy', 'return back', METHOD_L),
    '9.13': ('Indirect question word order', 'I wonder where is he', METHOD_T),
    '9.14': ('Clause linking', 'because to see you', METHOD_T),
    '9.15': ('Object order', 'gave to me a book', METHOD_T),
    # 10. Punctuation and orthography
    '10.1': ('Sentence-initial capital', 'the boy runs', METHOD_T),
    '10.2': ('Proper nouns, \u201cI\u201d, days, months', 'i am, monday', METHOD_L),
    '10.3': ('Terminal punctuation', 'missing period/question mark', METHOD_T),
    '10.4': ('Commas', 'series, introductory, clauses', METHOD_T),
    '10.5': ('Apostrophes', 'the 1990\u2019s', METHOD_T),
    '10.6': ('Quotation and dialogue', 'mismatched marks', METHOD_T),
    '10.7': ('Hyphens and dashes', 'a well known author', METHOD_C),
    '10.8': ('Colons and semicolons', 'misuse', METHOD_T),
    '10.9': ('Spacing and repeats', 'the the, space before comma', METHOD_T),
    '10.10': ('Numbers, dates, abbreviations', 'inconsistent format', METHOD_L),
    # 11. Meaning and usage (semantic layer)
    '11.1': ('Confusable words', 'affect/effect, lose/loose', METHOD_C),
    '11.2': ('Collocations', 'do a decision', METHOD_C),
    '11.3': ('Tense-time agreement', 'Yesterday I go', METHOD_C),
    '11.4': ('Selectional restrictions', 'The book eats', METHOD_C),
    '11.5': ('Structural ambiguity', 'PP-attachment', METHOD_C),
    '11.6': ('Register', 'slang in formal writing', METHOD_C),
    '11.7': ('L1 interference / false friends', 'I am agree', METHOD_C),
    '11.8': ('Connector misuse', 'I was tired, however I slept', METHOD_C),
}


def method_of(rule_id):
    entry = RULEBOOK.get(rule_id)
    return entry[2] if entry else None


def all_rule_ids():
    return sorted(RULEBOOK, key=lambda r: tuple(int(p) for p in r.split('.')))


# --------------------------------------------------------------------------- #
# Curated word lists / morphology tables (the "L" layer).                      #
# --------------------------------------------------------------------------- #
CONTRACTIONS = {
    'dont': "don't", 'cant': "can't", 'wont': "won't", 'isnt': "isn't",
    'arent': "aren't", 'wasnt': "wasn't", 'werent': "weren't",
    'doesnt': "doesn't", 'didnt': "didn't", 'couldnt': "couldn't",
    'shouldnt': "shouldn't", 'wouldnt': "wouldn't", 'hasnt': "hasn't",
    'havent': "haven't", 'hadnt': "hadn't", 'im': "I'm", 'ive': "I've",
    'youre': "you're", 'youve': "you've", 'youll': "you'll",
    'theyre': "they're", 'theyve': "they've", 'thats': "that's",
    'whats': "what's", 'wheres': "where's", 'heres': "here's",
    'theres': "there's",
}

REFLEXIVE_FIX = {
    'hisself': 'himself', 'theirselves': 'themselves', 'ourselfs': 'ourselves',
    'themselfs': 'themselves', 'yourselfs': 'yourselves',
    'thereselves': 'themselves', 'theirself': 'themselves', 'theyselves': 'themselves',
    'theirselfes': 'themselves',
}

ADVERB_FIX = {
    'happyly': 'happily', 'easyly': 'easily', 'angryly': 'angrily',
    'luckyly': 'luckily', 'lazyly': 'lazily', 'crazyly': 'crazily',
    'funnyly': 'funnily', 'busyly': 'busily', 'heavyly': 'heavily',
    'noisyly': 'noisily', 'dirtyly': 'dirtily', 'healthyly': 'healthily',
    'simplely': 'simply', 'gentlely': 'gently', 'terriblely': 'terribly',
    'possiblely': 'possibly', 'basicly': 'basically', 'trueely': 'truly',
    'specificly': 'specifically', 'automaticly': 'automatically',
    'dramaticly': 'dramatically',
}

SPELLING_FIX = {
    'recieve': 'receive', 'seperate': 'separate', 'definately': 'definitely',
    'untill': 'until', 'wich': 'which', 'becuase': 'because', 'thier': 'their',
    'freind': 'friend', 'beleive': 'believe', 'acheive': 'achieve',
    'tomorow': 'tomorrow', 'tommorrow': 'tomorrow', 'goverment': 'government',
    'enviroment': 'environment', 'neccessary': 'necessary', 'alot': 'a lot',
    'wierd': 'weird', 'teh': 'the', 'adress': 'address', 'buisness': 'business',
    'calender': 'calendar', 'embarass': 'embarrass', 'existance': 'existence',
    'foriegn': 'foreign', 'grammer': 'grammar', 'independant': 'independent',
    'maintainance': 'maintenance', 'noticable': 'noticeable',
    'occassion': 'occasion', 'publically': 'publicly', 'relevent': 'relevant',
    'rythm': 'rhythm', 'succesful': 'successful', 'occured': 'occurred',
}

VERB_ENDING_FIX = {
    'runing': 'running', 'stoping': 'stopping', 'swiming': 'swimming',
    'begining': 'beginning', 'planing': 'planning', 'refering': 'referring',
    'ocurring': 'occurring', 'writting': 'writing', 'comming': 'coming',
    'geting': 'getting', 'siting': 'sitting', 'droping': 'dropping',
    'stoped': 'stopped', 'droped': 'dropped', 'planed': 'planned',
    'refered': 'referred', 'occurd': 'occurred', 'writed': 'wrote',
}

IRREGULAR_COMPARATIVE = {
    'gooder': 'better', 'badder': 'worse', 'worser': 'worse',
    'littler': 'smaller', 'muchmore': 'more',
}

ORAL_PAST_REGULARIZED = {
    'goed': 'went', 'eated': 'ate', 'drinked': 'drank', 'runned': 'ran',
    'seed': 'saw', 'taked': 'took', 'buyed': 'bought', 'bringed': 'brought',
    'teached': 'taught', 'thinked': 'thought', 'writed': 'wrote',
    'knowed': 'knew', 'catched': 'caught', 'choosed': 'chose',
    'speaked': 'spoke', 'gived': 'gave', 'maked': 'made', 'finded': 'found',
}

IRREGULAR_PART_REGULARIZED = {
    'goed': 'gone', 'eated': 'eaten', 'drinked': 'drunk', 'runned': 'run',
    'taked': 'taken', 'buyed': 'bought', 'bringed': 'brought',
    'teached': 'taught', 'thinked': 'thought', 'writed': 'written',
    'knowed': 'known', 'catched': 'caught', 'choosed': 'chosen',
    'speaked': 'spoken', 'gived': 'given', 'maked': 'made', 'finded': 'found',
}

PAST_AS_PARTICIPLE = {
    'went', 'ate', 'drank', 'ran', 'took', 'bought', 'brought', 'taught',
    'thought', 'wrote', 'knew', 'caught', 'chose', 'spoke', 'gave', 'made',
    'found', 'saw', 'came', 'did', 'got', 'said', 'sold', 'sent', 'sang',
    'sat', 'slept', 'stood', 'stole', 'swam', 'threw', 'wore', 'won',
}

UNCOUNTABLE_PLURAL = {
    'informations', 'advices', 'knowledges', 'furnitures', 'luggages',
    'equipments', 'homeworks', 'evidences', 'softwares', 'moneys',
}

UNCOUNTABLE_SINGULAR = {
    'information', 'advice', 'knowledge', 'furniture', 'luggage', 'equipment',
    'homework', 'evidence', 'software', 'money', 'news', 'research',
}

PLURAL_ONLY = {
    'scissors', 'trousers', 'pants', 'glasses', 'clothes', 'shorts', 'jeans',
    'pyjamas', 'pajamas', 'tongs', 'pliers', 'tweezers',
}

INDEFINITE_PRON = {
    'everyone', 'everybody', 'someone', 'somebody', 'anyone', 'anybody',
    'nobody', 'nothing', 'everything', 'something', 'anything', 'none',
}

STATIVE_PROGRESSIVE = {
    'know', 'believe', 'understand', 'own', 'belong', 'consist', 'contain',
    'mean', 'recognize', 'prefer', 'desire', 'doubt',
}

INTRANSITIVE_VBN = {
    'happened', 'occurred', 'arisen', 'arrived', 'appeared', 'disappeared',
    'vanished', 'existed', 'belonged', 'consisted', 'resulted', 'elapsed',
    'slept', 'worked', 'rained', 'snowed', 'sneezed', 'coughed', 'died',
}

GERUND_VERBS = {
    'enjoy', 'enjoys', 'enjoyed', 'avoid', 'avoids', 'avoided', 'mind',
    'minds', 'minded', 'finish', 'finishes', 'finished', 'consider',
    'considers', 'considered', 'risk', 'risks', 'risked', 'practice',
    'practices', 'practiced', 'imagine', 'imagines', 'imagined', 'deny',
    'denies', 'denied', 'admit', 'admits', 'admitted', 'postpone',
    'postpones', 'postponed', 'quit', 'quits',
}

CLAUSE_PATTERN_VERBS = {'suggest', 'suggests', 'suggested', 'recommend',
                        'recommends', 'recommended', 'propose', 'proposes',
                        'proposed', 'insist', 'insists', 'insisted'}

CAUSATIVE_VERBS = {'make', 'makes', 'made', 'let', 'lets'}

ADJ_PREP_FIX = {
    'interested': {'on': 'in', 'for': 'in', 'about': 'in'},
    'afraid': {'from': 'of', 'with': 'of'},
    'proud': {'for': 'of'},
    'married': {'with': 'to'},
    'good': {'in': 'at'},
    'responsible': {'of': 'for', 'to': 'for'},
    'similar': {'with': 'to'},
    'depend': {'of': 'on'},
}

EXTRA_PREP = {
    ('discuss', 'about'), ('discusses', 'about'), ('discussed', 'about'),
    ('mention', 'about'), ('mentions', 'about'), ('mentioned', 'about'),
    ('emphasize', 'on'), ('emphasizes', 'on'), ('emphasized', 'on'),
    ('enter', 'into'), ('enters', 'into'), ('entered', 'into'),
    ('answer', 'to'),
}

NEEDS_PREP = {
    'listen': 'to', 'listens': 'to', 'listened': 'to',
    'depend': 'on', 'depends': 'on', 'depended': 'on',
    'rely': 'on', 'relies': 'on', 'relied': 'on',
    'wait': 'for', 'waits': 'for', 'waited': 'for',
    'consist': 'of', 'consists': 'of', 'consisted': 'of',
    'laugh': 'at', 'laughs': 'at', 'laughed': 'at',
    'arrive': 'at', 'arrives': 'at', 'arrived': 'at',
    'belong': 'to', 'belongs': 'to', 'belonged': 'to',
    'apologize': 'to', 'apologizes': 'to', 'apologized': 'to',
}

REDUNDANT_BIGRAMS = {
    ('return', 'back'), ('returns', 'back'), ('returned', 'back'),
    ('repeat', 'again'), ('repeats', 'again'), ('repeated', 'again'),
    ('revert', 'back'), ('reverts', 'back'), ('reverted', 'back'),
    ('combine', 'together'), ('unite', 'together'), ('collaborate', 'together'),
    ('advance', 'forward'), ('free', 'gift'), ('past', 'history'),
    ('new', 'innovation'), ('final', 'outcome'),
}

PREP_GERUND_PHRASES = (
    ('look', 'forward', 'to'),
    ('looking', 'forward', 'to'),
    ('object', 'to'),
    ('objects', 'to'),
    ('opposed', 'to'),
    ('committed', 'to'),
    ('accustomed', 'to'),
    ('used', 'to'),
)

SHORT_MORPH_ADJ = {
    'big', 'tall', 'small', 'fast', 'easy', 'happy', 'simple', 'young',
    'old', 'hard', 'long', 'short', 'large', 'low', 'high', 'slow', 'cheap',
    'rich', 'safe', 'smart', 'quick', 'deep', 'wide', 'thick', 'thin',
}

ADJ_ORDER_CATEGORY = {
    'opinion': {'beautiful', 'ugly', 'nice', 'lovely', 'good', 'bad',
                'wonderful', 'awful', 'delicious', 'important', 'lovely'},
    'size': {'big', 'small', 'large', 'tiny', 'huge', 'little', 'tall',
             'short', 'long', 'enormous'},
    'age': {'old', 'new', 'young', 'ancient', 'modern'},
    'shape': {'round', 'square', 'flat', 'oval'},
    'color': {'red', 'blue', 'green', 'black', 'white', 'yellow', 'brown',
              'orange', 'pink', 'grey', 'gray'},
    'origin': {'french', 'american', 'chinese', 'italian', 'japanese',
               'spanish', 'german', 'korean'},
    'material': {'wooden', 'metal', 'plastic', 'cotton', 'silk', 'gold',
                 'silver', 'leather', 'glass'},
}
ADJ_ORDER_RANK = {w: i for i, (cat, ws) in enumerate(ADJ_ORDER_CATEGORY.items())
                  for w in ws}

DAYS = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday'}
MONTHS = {'january', 'february', 'april', 'june', 'july', 'september',
          'october', 'november', 'december'}

COLLECTIVE_NOUNS = {
    'team', 'staff', 'government', 'family', 'committee', 'group', 'audience',
    'public', 'class', 'crew', 'jury', 'company', 'band', 'crowd',
}

SPORTS = {'football', 'basketball', 'soccer', 'tennis', 'baseball',
          'volleyball', 'chess', 'golf', 'hockey', 'rugby'}

HOMOPHONE_ITS_VERBS = {'raining', 'snowing', 'going', 'coming', 'time',
                       'getting', 'working', 'not', 'been', 'a'}

SUBORDINATORS = {'because', 'when', 'while', 'if', 'although', 'though',
                 'since', 'before', 'after', 'until', 'unless', 'whereas',
                 'as', 'whether', 'whenever', 'wherever'}

# --- rule 1.1 regular/irregular plurals ------------------------------------ #
KNOWN_PLURALS = {
    'boxs': 'boxes', 'childs': 'children', 'mans': 'men', 'womans': 'women',
    'foots': 'feet', 'tooths': 'teeth', 'mouses': 'mice', 'fishs': 'fish',
    'sheeps': 'sheep', 'deers': 'deer', 'people': 'people', 'person': 'people',
    'knifes': 'knives', 'wifes': 'wives', 'leafs': 'leaves',
}
# --- rule 6.5 intransitive verbs (cannot be passivised) -------------------- #
INTRANSITIVE_VERBS = {
    'happen', 'occur', 'arrive', 'come', 'go', 'die', 'sleep', 'fall', 'rise',
    'appear', 'disappear', 'emerge', 'consist', 'belong', 'exist', 'seem',
}
# --- rule 6.8 verbs that need a preposition, not a direct object ----------- #
PREP_REQUIRED_VERBS = {'arrive', 'listen', 'depend', 'consist', 'apologize',
                       'agree', 'belong', 'refer', 'reply'}
# --- rule 10.2 proper nouns ------------------------------------------------- #
DAYS = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday'}
MONTHS = {'january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december'}
# --- rule 7.4 participial adjectives (suggestion) -------------------------- #
PARTICIPIAL_ADJ = {'boring', 'interesting', 'exciting', 'confusing', 'tiring',
                   'annoying', 'surprising', 'frightening', 'embarrassing'}
# --- rule 10.7 hyphenation (suggestion) ------------------------------------ #
HYPHEN_BEFORE_ADJ = {'well', 'much', 'little', 'well-'}
# --- rule 11.1 confusable words (suggestion) -------------------------------- #
CONFUSABLE_VERB = {'effect': 'affect', 'loose': 'lose', 'advise': 'advice'}
# --- rule 11.2 collocations (suggestion) ----------------------------------- #
COLLOCATION_FIX = {
    'do a decision': 'make a decision', 'do a mistake': 'make a mistake',
    'do a choice': 'make a choice', 'make a research': 'do research',
    'make a progress': 'make progress', 'do progress': 'make progress',
    'take a decision': 'make a decision',
}
# --- rule 11.4 selectional restrictions (suggestion) ----------------------- #
HUMAN_ONLY_VERBS = {'eat', 'drink', 'sleep', 'dream', 'eat', 'swallow',
                    'smile', 'laugh', 'walk', 'run', 'think', 'feel'}
INANIMATE_SUBJECTS = {'book', 'table', 'chair', 'house', 'car', 'stone',
                      'weather', 'rain', 'idea', 'plan'}
# --- rule 11.6 register (suggestion) --------------------------------------- #
INFORMAL_WORDS = {'gonna', 'wanna', 'gotta', 'kinda', 'sorta', 'ain\'t',
                  'yeah', 'stuff', 'kids', 'guys', 'lots'}
# --- rule 11.5/11.7 L1 interference (suggestion) --------------------------- #
TO_BE_SURFACES = {'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
DO_HAVE_SURFACES = {'do', 'does', 'did', 'have', 'has', 'had'}

NEGATIONS = {'not', "n't", 'never', 'no'}

BE_SURFACES = {'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
HAVE_SURFACES = {'have', 'has', 'had', 'having'}
DO_SURFACES = {'do', 'does', 'did', 'doing', 'done'}
MODAL_SURFACES = {'will', 'would', 'shall', 'should', 'can', 'could', 'may',
                  'might', 'must'}
FINITE_TYPES = {'VBD', 'VBP', 'VBZ', 'MD'}
PLURAL_FINITE = {'are', 'were', 'have', 'do', 'VBP'}
PRON_SUBJ = {'i', 'we', 'he', 'she', 'they', 'you'}
PRON_OBJ = {'me', 'us', 'him', 'her', 'them', 'you', 'it'}
PRP_PERSON = {
    'i': ('1', 'sg'), 'we': ('1', 'pl'), 'you': ('2', None),
    'he': ('3', 'sg'), 'she': ('3', 'sg'), 'it': ('3', 'sg'),
    'they': ('3', 'pl'),
}
REFLEXIVE_KEY = {
    'myself': ('1', 'sg', None), 'yourself': ('2', None, None),
    'himself': ('3', 'sg', 'm'), 'herself': ('3', 'sg', 'f'),
    'itself': ('3', 'sg', 'n'), 'ourselves': ('1', 'pl', None),
    'yourselves': ('2', 'pl', None), 'themselves': ('3', 'pl', None),
}


# --------------------------------------------------------------------------- #
# Tree helpers                                                                #
# --------------------------------------------------------------------------- #
def _iter_nodes(node):
    yield node
    for c in node.get('children', []):
        yield from _iter_nodes(c)


def _leaves(root):
    return [n for n in _iter_nodes(root) if 'children' not in n]


def _clauses(root):
    return [n for n in _iter_nodes(root)
            if n.get('type') in {'S', 'SQ', 'SINV', 'SBARQ'}]


def _lower(leaf):
    return (leaf.get('surface') or '').lower()


def _num_of(leaf):
    t = leaf.get('type')
    if t in {'NNS', 'NNPS'}:
        return 'pl'
    if t in {'NN', 'NNP', 'NML', 'NX'}:
        return 'sg'
    if t == 'PRP':
        key = PRP_PERSON.get(_lower(leaf))
        return key[1] if key else None
    return None


def _person_of(leaf):
    t = leaf.get('type')
    if t and t.startswith('NN'):
        return '3'
    if t == 'PRP':
        key = PRP_PERSON.get(_lower(leaf))
        return key[0] if key else None
    return None


def _verb_key(leaf):
    t = leaf.get('type')
    s = _lower(leaf)
    if t == 'MD' or s in MODAL_SURFACES:
        return None
    if t == 'VBD':
        return None
    if t == 'VBZ':
        return ('3', 'sg')
    if t == 'VBP':
        return ('*', 'non3sg')
    if s in BE_SURFACES:
        if s in ('is', 'was'):
            return ('3', 'sg')
        if s == 'am':
            return ('1', 'sg')
        return ('*', 'non3sg')
    if s in HAVE_SURFACES:
        return ('3', 'sg') if s == 'has' else ('*', 'non3sg')
    if s in DO_SURFACES:
        return ('3', 'sg') if s == 'does' else ('*', 'non3sg')
    return None


def _agree(skey, vkey):
    if vkey is None or skey is None:
        return True
    if vkey == ('*', 'non3sg'):
        return skey != ('3', 'sg')
    if skey == ('2', None):
        return vkey == ('*', 'non3sg')
    return vkey == skey


def _clause_subject_verb(clause):
    subj, verbs = None, []
    for c in clause.get('children', []):
        if c.get('type') == 'NP' and subj is None:
            subj = c
        for lf in _leaves(c):
            if lf.get('type') in FINITE_TYPES or _lower(lf) in (
                    BE_SURFACES | HAVE_SURFACES | DO_SURFACES | MODAL_SURFACES):
                verbs.append(lf)
    return subj, verbs


def _np_head_leaf(np_node):
    leaves = _leaves(np_node)
    nouns = [lf for lf in leaves if lf.get('type') in
             {'NN', 'NNS', 'NNP', 'NNPS', 'NML', 'NX', 'PRP'}]
    return nouns[-1] if nouns else None


def _finding(rule_id, status, constraint, role, node_id, text, evidence,
             remediation=None):
    method = method_of(rule_id) or METHOD_T
    out = {
        'rule_id': rule_id,
        'method': method,
        'status': status,
        'constraint': constraint,
        'role': role,
        'node_id': node_id,
        'text': text,
        'evidence': evidence,
    }
    if remediation:
        out['remediation'] = remediation
    return out


def _tree_evidence(subtree_id, rule, conflict=None):
    return {'used': 'tree', 'subtree': subtree_id, 'rule': rule,
            'conflict': conflict or []}


def _wordlist_evidence(observed, accepted, source):
    return {'used': 'wordlist', 'lookup': observed, 'accepted': list(accepted),
            'source': source}


def _context_evidence(condition, options, confidence):
    return {'used': 'context', 'condition': condition, 'options': options,
            'confidence': confidence}


def _rem(violation, fix, alt=None, outcome=None):
    return {'violation': violation, 'suggested_fix': fix,
            'alternative_fix': alt, 'targeted_outcome': outcome}


# --------------------------------------------------------------------------- #
# L-layer checks (word list / morphology)                                      #
# --------------------------------------------------------------------------- #
def _check_wordlists(leaves):
    out = []
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        prev = leaves[i - 1] if i else None
        nxt = leaves[i + 1] if i + 1 < len(leaves) else None

        if low == 'nt' or (low in CONTRACTIONS):
            if low == 'nt' and prev is not None:
                fix = _lower(prev) + "'t"
                observed = _lower(prev) + 'nt'
            else:
                fix = CONTRACTIONS.get(low, low)
                observed = lf['surface']
            out.append(_finding('1.11', 'error', 'C-CONTRACTION', 'contraction',
                                lf['id'],
                                f"Missing apostrophe: '{observed}' is an unmarked "
                                f"contraction; write '{fix}'.",
                                _wordlist_evidence(observed, [fix],
                                                   'contraction table'),
                                _rem(f"Unmarked contraction '{observed}'.",
                                     f"Add the apostrophe: '{observed}' \u2192 '{fix}'.",
                                     None, "Contraction written with an apostrophe")))

        if low in REFLEXIVE_FIX:
            fix = REFLEXIVE_FIX[low]
            out.append(_finding('1.9', 'error', 'C-REFLEXIVE-FORM', 'reflexive',
                                lf['id'],
                                f"Reflexive-form error: '{lf['surface']}' is not a "
                                f"standard reflexive; use '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'reflexive table'),
                                _rem(f"Non-standard reflexive '{lf['surface']}'.",
                                     f"Use '{fix}' instead of '{lf['surface']}'.",
                                     None, 'Standard reflexive pronoun')))

        if low in ADVERB_FIX:
            fix = ADVERB_FIX[low]
            out.append(_finding('1.8', 'error', 'C-ADVERB-FORM', 'adverb form',
                                lf['id'],
                                f"Adverb-formation error: '{lf['surface']}' should be "
                                f"'{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'adverb-formation table'),
                                _rem(f"Misspelled adverb '{lf['surface']}'.",
                                     f"Write '{fix}' instead of '{lf['surface']}'.")))

        if low in SPELLING_FIX:
            fix = SPELLING_FIX[low]
            out.append(_finding('1.12', 'error', 'C-SPELLING', 'spelling',
                                lf['id'],
                                f"Misspelling: '{lf['surface']}' \u2192 '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'spelling table'),
                                _rem(f"Misspelled word '{lf['surface']}'.",
                                     f"Correct the spelling to '{fix}'.")))

        if low in VERB_ENDING_FIX:
            fix = VERB_ENDING_FIX[low]
            out.append(_finding('1.4', 'error', 'C-VERB-ENDING', 'verb ending',
                                lf['id'],
                                f"Verb-ending error: '{lf['surface']}' \u2192 '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'verb-ending table'),
                                _rem(f"Misspelled verb form '{lf['surface']}'.",
                                     f"Write '{fix}' instead of '{lf['surface']}'.")))

        if low in UNCOUNTABLE_PLURAL:
            out.append(_finding('4.1', 'error', 'C-UNCOUNTABLE', 'noun number',
                                lf['id'],
                                f"'{lf['surface']}' is an uncountable noun and has no "
                                f"plural form; use the singular '{low.rstrip('s')}'.",
                                _wordlist_evidence(lf['surface'], [low.rstrip('s')],
                                                   'uncountable-noun list')))

        if low in IRREGULAR_COMPARATIVE:
            fix = IRREGULAR_COMPARATIVE[low]
            out.append(_finding('1.7', 'error', 'C-COMPARATIVE-FORM',
                                'comparative form', lf['id'],
                                f"Irregular comparative: '{lf['surface']}' \u2192 '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'irregular-comparative table')))

        if lf.get('type') == 'VBD' and low in ORAL_PAST_REGULARIZED:
            fix = ORAL_PAST_REGULARIZED[low]
            out.append(_finding('1.5', 'error', 'C-VERB-FORM', 'verb form',
                                lf['id'],
                                f"Irregular past-tense error: '{lf['surface']}' \u2192 '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'irregular-past table')))

        if lf.get('type') == 'VBN' and low in PAST_AS_PARTICIPLE:
            out.append(_finding('1.6', 'error', 'C-VERB-FORM', 'verb form',
                                lf['id'],
                                f"Past participle required, but '{lf['surface']}' is the "
                                f"past-tense form.",
                                _wordlist_evidence(lf['surface'],
                                                   [IRREGULAR_PART_REGULARIZED.get(low, '')],
                                                   'participle table')))

        if lf.get('type') == 'VBN' and low in IRREGULAR_PART_REGULARIZED:
            fix = IRREGULAR_PART_REGULARIZED[low]
            out.append(_finding('1.6', 'error', 'C-VERB-FORM', 'verb form',
                                lf['id'],
                                f"Regularized participle after 'have': '{lf['surface']}' "
                                f"\u2192 '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'participle table')))

        if low in UNCOUNTABLE_SINGULAR and prev is not None \
                and _lower(prev) in ('a', 'an'):
            out.append(_finding('4.1', 'error', 'C-UNCOUNTABLE', 'articles',
                                lf['id'],
                                f"'{lf['surface']}' is uncountable and takes no "
                                f"indefinite article; drop '{prev['surface']}'.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [lf['surface']],
                                                   'uncountable-noun list')))

        if low in PLURAL_ONLY and prev is not None and _lower(prev) in ('a', 'an'):
            out.append(_finding('4.3', 'error', 'C-PLURAL-ONLY', 'noun number',
                                lf['id'],
                                f"'{lf['surface']}' is plural-only and cannot follow "
                                f"'{prev['surface']}'; use 'a pair of {lf['surface']}'.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [f"pair of {lf['surface']}"],
                                                   'plural-only noun list')))

        if low == 'news' and nxt is not None and _lower(nxt) in (
                'are', 'were', 'have', 'do'):
            out.append(_finding('4.3', 'error', 'C-PLURAL-ONLY', 'noun number',
                                lf['id'],
                                f"'news' is singular in form and takes a singular verb, "
                                f"not '{nxt['surface']}'.",
                                _wordlist_evidence('news', ['is', 'was'],
                                                   'singular -s noun list')))

        # Scales: two hundreds / three thousands
        if low in ('hundreds', 'thousands', 'millions', 'billions') \
                and prev is not None and (
                    prev.get('type') == 'CD' or _lower(prev).rstrip('s') in
                    {'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                     'eight', 'nine', 'ten', 'eleven', 'twelve'}):
            out.append(_finding('1.13', 'error', 'C-NUMERAL', 'numeral',
                                lf['id'],
                                f"After a number the scale word stays singular: "
                                f"'{prev['surface']} {lf['surface']}' \u2192 "
                                f"'{prev['surface']} {low[:-1]}'.",
                                _wordlist_evidence(lf['surface'], [low[:-1]],
                                                   'numeral-scale rule')))

        # Redundancy
        if prev is not None and (_lower(prev), low) in REDUNDANT_BIGRAMS:
            out.append(_finding('9.12', 'error', 'C-REDUNDANCY', 'redundancy',
                                lf['id'],
                                f"Redundant pair: '{prev['surface']} {lf['surface']}' "
                                f"expresses the same idea twice.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [prev['surface']],
                                                   'redundancy table')))

        # Adjective + preposition
        if low in ADJ_PREP_FIX and nxt is not None \
                and _lower(nxt) in ADJ_PREP_FIX[low]:
            correct = ADJ_PREP_FIX[low][_lower(nxt)]
            out.append(_finding('8.4', 'error', 'C-ADJ-PREP', 'preposition',
                                nxt['id'],
                                f"Preposition selection: '{low} {nxt['surface']}' "
                                f"\u2192 '{low} {correct}'.",
                                _wordlist_evidence(nxt['surface'], [correct],
                                                   'adjective+preposition table')))

        # Extra (unnecessary) preposition
        if prev is not None and (_lower(prev), low) in EXTRA_PREP:
            out.append(_finding('8.3', 'error', 'C-EXTRA-PREP', 'preposition',
                                lf['id'],
                                f"'{prev['surface']}' does not license the preposition "
                                f"'{lf['surface']}'; remove it.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [prev['surface']],
                                                   'verb-preposition table')))

        # Missing preposition (listen music -> listen to music)
        if low in NEEDS_PREP and nxt is not None \
                and nxt.get('type') in {'NN', 'NNS', 'NNP', 'NNPS', 'PRP'}:
            prep = NEEDS_PREP[low]
            out.append(_finding('8.2', 'error', 'C-MISSING-PREP', 'preposition',
                                lf['id'],
                                f"Missing preposition: '{low}' requires '{prep}' before "
                                f"'{nxt['surface']}' \u2192 '{low} {prep} {nxt['surface']}'.",
                                _wordlist_evidence(low, [f"{low} {prep}"],
                                                   'verb-preposition table')))

        # Homophones
        if low in ('its', 'it\u2019s') and nxt is not None \
                and (nxt.get('type') == 'VBG' or _lower(nxt) in HOMOPHONE_ITS_VERBS):
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"Homophone: '{lf['surface']}' here means 'it is' \u2192 "
                                f"'It's {nxt['surface']}'.",
                                _wordlist_evidence(lf['surface'], ["it's"],
                                                   'homophone table')))
        if low == 'their' and nxt is not None and _lower(nxt) in BE_SURFACES:
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"Homophone: '{lf['surface']} {nxt['surface']}' \u2192 "
                                f"'there {nxt['surface']}'.",
                                _wordlist_evidence(f"{lf['surface']} {nxt['surface']}",
                                                   [f"there {nxt['surface']}"],
                                                   'homophone table')))
        if low == 'your' and nxt is not None and _lower(nxt) == 'welcome':
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"Homophone: 'your welcome' \u2192 'you're welcome'.",
                                _wordlist_evidence('your welcome', ["you're welcome"],
                                                   'homophone table')))
        if low == 'then' and prev is not None and _lower(prev) in ('more', 'less',
                                                                   'rather', 'other'):
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"Homophone: '{prev['surface']} then' \u2192 "
                                f"'{prev['surface']} than' (comparison).",
                                _wordlist_evidence(f"{prev['surface']} then",
                                                   [f"{prev['surface']} than"],
                                                   'homophone table')))

        # some in a negative clause (3.7)
        if low == 'some' and nxt is not None and nxt.get('type') in (
                'NN', 'NNS', 'JJ'):
            if any(_lower(x) in NEGATIONS for x in leaves):
                out.append(_finding('3.7', 'error', 'C-SOME-ANY', 'determiner',
                                    lf['id'],
                                    f"In a negative clause, use 'any' rather than "
                                    f"'{lf['surface']}'.",
                                    _tree_evidence(lf['id'], 'negative + some'),
                                    _rem(f"'some' in a negative clause.",
                                         f"Change '{lf['surface']}' to 'any'.")))
    return out


# --------------------------------------------------------------------------- #
# T-layer checks (tree structure)                                             #
# --------------------------------------------------------------------------- #
def _check_tree(root, clauses, leaves, text=None):
    out = []
    # Clause-level structural rules (missing subject/copula, double subject,
    # question formation) apply to matrix clauses only -- relative, small and
    # infinitival clauses legitimately have no overt subject.
    top_ids = {root['id']}
    for c in root.get('children', []):
        if c.get('type') in {'S', 'SQ', 'SINV', 'SBARQ'}:
            top_ids.add(c['id'])

    # 2.4 Existential there
    for clause in clauses:
        cl = _leaves(clause)
        for i, lf in enumerate(cl):
            if _lower(lf) == 'there' and lf.get('type') in ('EX', 'PRP', 'RB'):
                nxt = cl[i + 1] if i + 1 < len(cl) else None
                if nxt is not None and _lower(nxt) in ('is', 'was', 'are', 'were'):
                    after = [x for x in cl[i + 2:] if x.get('type') in
                             {'NN', 'NNS', 'NNP', 'NNPS'}]
                    head = after[0] if after else None
                    if head is not None:
                        be_sg = _lower(nxt) in ('is', 'was')
                        noun_pl = head.get('type') in ('NNS', 'NNPS')
                        if be_sg and noun_pl:
                            out.append(_finding('2.4', 'error', 'C-EXISTENTIAL',
                                                'existential there', nxt['id'],
                                                f"Existential agreement: 'there {nxt['surface']}' "
                                                f"but the following noun '{head['surface']}' is "
                                                f"plural; use 'there are'.",
                                                _tree_evidence(clause['id'], 'there + be + NP')))
                        elif (not be_sg) and not noun_pl:
                            out.append(_finding('2.4', 'error', 'C-EXISTENTIAL',
                                                'existential there', nxt['id'],
                                                f"Existential agreement: 'there {nxt['surface']}' "
                                                f"but '{head['surface']}' is singular; use "
                                                f"'there is'.",
                                                _tree_evidence(clause['id'], 'there + be + NP')))

    # 2.8 Indefinite pronoun agreement
    for clause in clauses:
        cl = _leaves(clause)
        for i, lf in enumerate(cl):
            if _lower(lf) in INDEFINITE_PRON:
                for nxt in cl[i + 1:]:
                    vk = _verb_key(nxt)
                    if nxt.get('type') in FINITE_TYPES or _lower(nxt) in (
                            BE_SURFACES | HAVE_SURFACES | DO_SURFACES):
                        if vk == ('*', 'non3sg'):
                            out.append(_finding('2.8', 'error', 'C-INDEFINITE-AGREE',
                                                'subject-verb agreement', nxt['id'],
                                                f"'{lf['surface']}' is singular, but "
                                                f"'{nxt['surface']}' is plural.",
                                                _tree_evidence(clause['id'], 'indefinite + finite',
                                                               [{'node': lf['id']},
                                                                {'node': nxt['id']}])))
                        break

    # 2.14 Reflexive-antecedent
    for clause in clauses:
        cl = _leaves(clause)
        for i, lf in enumerate(cl):
            if _lower(lf) in REFLEXIVE_KEY:
                subj = None
                for cand in cl[:i]:
                    if cand.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP'):
                        subj = cand
                        break
                if subj is None:
                    continue
                rp, rn, rg = REFLEXIVE_KEY[_lower(lf)]
                sp, sn = _person_of(subj), _num_of(subj)
                bad = False
                if sn and rn and sn != rn:
                    bad = True
                elif sp and rp and sp != rp:
                    bad = True
                elif sp == '3' and sn == 'sg' and rg:
                    gender = {'he': 'm', 'she': 'f', 'it': 'n'}.get(_lower(subj))
                    if gender and gender != rg:
                        bad = True
                if bad:
                    out.append(_finding('2.14', 'error', 'C-REFLEXIVE-ANTECEDENT',
                                        'reflexive agreement', lf['id'],
                                        f"The reflexive '{lf['surface']}' does not match "
                                        f"the subject '{subj['surface']}'.",
                                        _tree_evidence(clause['id'], 'subject ... reflexive',
                                                       [{'node': subj['id']},
                                                        {'node': lf['id']}])))

    # 5.7 Reflexive as subject (Myself am happy)
    for clause in clauses:
        subj = None
        for c in clause.get('children', []):
            if c.get('type') == 'NP':
                subj = c
                break
        if subj is None:
            continue
        head = _np_head_leaf(subj)
        if head is not None and _lower(head) in REFLEXIVE_KEY:
            out.append(_finding('5.7', 'error', 'C-REFLEXIVE-SUBJECT', 'subject',
                                head['id'],
                                f"'{head['surface']}' is a reflexive and cannot be the "
                                f"clause subject; use a personal pronoun "
                                f"(e.g. 'I') instead.",
                                _tree_evidence(clause['id'], 'reflexive subject')))

    # 6.3 Missing copula (She very happy)
    for clause in clauses:
        if clause.get('type') != 'S' or clause['id'] not in top_ids:
            continue
        types = [c.get('type') for c in clause.get('children', [])]
        if 'VP' in types:
            continue
        has_subject = 'NP' in types or 'SBAR' in types
        predicate = [t for t in types if t in ('ADJP', 'ADVP', 'PP')]
        if has_subject and predicate and not any(
                lf.get('type') in FINITE_TYPES for lf in _leaves(clause)):
            out.append(_finding('6.3', 'error', 'C-COPULA', 'predicate',
                                clause['id'],
                                f"The clause '{clause['surface']}' has a subject and a "
                                f"predicate but no verb; supply a form of 'be' "
                                f"(e.g. 'is'/'was').",
                                _tree_evidence(clause['id'], 'S -> NP + predicate, no VP')))

    # 9.5 Double subject (My brother he runs)
    for clause in clauses:
        if clause['id'] not in top_ids:
            continue
        kids = clause.get('children', [])
        for i in range(len(kids) - 2):
            if kids[i].get('type') == 'NP' and kids[i + 1].get('type') in ('PRP', 'NP') \
                    and kids[i + 2].get('type') == 'VP':
                first_head = _np_head_leaf(kids[i])
                if first_head is not None and _lower(first_head) in {
                        'today', 'yesterday', 'tomorrow', 'tonight', 'now',
                        'later', 'then', 'soon', 'here', 'there'}:
                    continue
                prp_leaf = kids[i + 1]
                if kids[i + 1].get('type') == 'NP':
                    prp_leaf = _np_head_leaf(kids[i + 1])
                else:
                    prp_leaf = _leaves(kids[i + 1])
                    prp_leaf = prp_leaf[0] if prp_leaf else None
                if prp_leaf is not None and _lower(prp_leaf) in PRON_SUBJ \
                        and 'CC' not in [c.get('type') for c in kids[i].get('children', [])]:
                    out.append(_finding('9.5', 'error', 'C-DOUBLE-SUBJECT', 'subject',
                                        prp_leaf['id'],
                                        f"Double subject: '{kids[i]['surface']} "
                                        f"{prp_leaf['surface']}' repeats the subject; keep "
                                        f"only one.",
                                        _tree_evidence(clause['id'], 'NP + PRP + VP')))

    # 9.2 Missing subject (Went to school)
    for clause in clauses:
        kids = clause.get('children', [])
        types = [c.get('type') for c in kids]
        if clause.get('type') not in ('S',):
            continue
        if clause['id'] not in top_ids:
            continue
        if 'NP' in types or 'SBAR' in types:
            continue
        if 'VP' not in types:
            continue
        cl = _leaves(clause)
        first_verb = next((lf for lf in cl if lf.get('type') in
                           ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD')), None)
        if first_verb is not None and first_verb.get('type') == 'VB' \
                and cl and cl[0]['id'] == first_verb['id']:
            continue  # imperative
        out.append(_finding('9.2', 'error', 'C-MISSING-SUBJECT', 'subject',
                            clause['id'],
                            f"The clause '{clause['surface']}' has no subject; add the "
                            f"subject the verb requires.",
                            _tree_evidence(clause['id'], 'S -> VP (no subject)')))

    # 2.6 / 6.13 Question structure and subject-verb agreement
    for clause in clauses:
        if clause.get('type') not in ('SBARQ', 'SQ'):
            continue
        if clause['id'] not in top_ids:
            continue
        kids = clause.get('children', [])
        types = [c.get('type') for c in kids]
        if clause.get('type') == 'SBARQ' and 'S' in types and 'SQ' not in types:
            out.append(_finding('6.13', 'error', 'C-QUESTION-INVERSION',
                                'inversion', clause['id'],
                                "A wh-question needs subject-auxiliary inversion "
                                "(e.g. 'Where are you going?').",
                                _tree_evidence(clause['id'], 'SBARQ -> S (no SQ)')))
        cl = _leaves(clause)
        verb = next((lf for lf in cl if lf.get('type') in
                     ('VBD', 'VBP', 'VBZ', 'MD') or _lower(lf) in BE_SURFACES), None)
        if verb is None:
            continue
        after = [lf for lf in cl if lf['span'][0] > verb['span'][0]
                 and lf.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP')]
        if after:
            head = after[0]
            skey = (('3', 'pl') if head.get('type') in ('NNS', 'NNPS')
                    else (_person_of(head), _num_of(head)))
            if not _agree(skey, _verb_key(verb)):
                out.append(_finding('2.6', 'error', 'C-SUBJECT-AGREEMENT',
                                    'subject-verb agreement', verb['id'],
                                    f"Question agreement: the subject "
                                    f"'{head['surface']}' and the verb "
                                    f"'{verb['surface']}' do not agree.",
                                    _tree_evidence(clause['id'], 'question subject + verb',
                                                   [{'node': head['id']},
                                                    {'node': verb['id']}])))

    # 9.13 Indirect question word order (I wonder where is he)
    for clause in _iter_nodes(root):
        if clause.get('type') != 'SBAR':
            continue
        for child in clause.get('children', []):
            if child.get('type') not in ('S', 'SQ'):
                continue
            cl = _leaves(child)
            if not cl:
                continue
            if cl[0].get('type') in FINITE_TYPES or _lower(cl[0]) in BE_SURFACES:
                if any(_lower(x) in PRON_SUBJ for x in cl[1:]):
                    out.append(_finding('9.13', 'error', 'C-INDIRECT-Q-ORDER',
                                        'word order', cl[0]['id'],
                                        "An embedded (indirect) question uses statement "
                                        "order (subject before verb), not inversion.",
                                        _tree_evidence(child['id'], 'SBAR -> S starting with verb')))

    # 9.4 Comma splice / fused sentence
    tops = _leaves(root)
    for i, lf in enumerate(tops):
        if lf.get('type') != ',':
            continue
        before = tops[:i]
        after = tops[i + 1:]
        before_verbs = [x for x in before if x.get('type') in FINITE_TYPES
                        or _lower(x) in (BE_SURFACES | HAVE_SURFACES | DO_SURFACES | MODAL_SURFACES)]
        after_verbs = [x for x in after if x.get('type') in FINITE_TYPES
                       or _lower(x) in (BE_SURFACES | HAVE_SURFACES | DO_SURFACES | MODAL_SURFACES)]
        if not before_verbs or not after_verbs:
            continue
        first_words = [_lower(x) for x in before[:3]]
        if any(w in SUBORDINATORS for w in first_words):
            continue
        if before[0].get('type') in ('IN', 'TO', 'PP') or _lower(before[0]) in SUBORDINATORS:
            continue
        if before and _lower(before[-1]) in {'and', 'but', 'or', 'nor', 'so',
                                             'yet', 'for'}:
            continue
        if after and _lower(after[0]) in {'and', 'but', 'or', 'nor', 'so',
                                          'yet', 'for', 'however', 'therefore',
                                          'moreover', 'nevertheless',
                                          'furthermore', 'thus', 'hence',
                                          'otherwise', 'meanwhile'}:
            continue
        out.append(_finding('9.4', 'error', 'C-COMMA-SPLICE', 'punctuation',
                            lf['id'],
                            "Comma splice: two independent clauses are joined by a comma "
                            "alone; use a semicolon, a period, or a conjunction.",
                            _tree_evidence(lf['id'], 'clause , clause')))

    # 9.8 Parallel structure (to run, swimming)
    for i, lf in enumerate(tops):
        if lf.get('type') == 'TO' and i + 1 < len(tops) and tops[i + 1].get('type') == 'VB':
            for j in range(i + 2, len(tops)):
                x = tops[j]
                if x.get('type') in FINITE_TYPES or x.get('type') in ('VB', 'TO'):
                    break
                xlow = _lower(x)
                if x.get('type') == 'VBG' or xlow.endswith('ing'):
                    out.append(_finding('9.8', 'error', 'C-PARALLEL', 'parallelism',
                                        x['id'],
                                        f"Items in a list must share a form; "
                                        f"'{tops[i + 1]['surface']}' (base) and "
                                        f"'{x['surface']}' (gerund) do not match.",
                                        _tree_evidence(lf['id'], 'to VB + VBG')))
                    break

    # 6.10 to + base form
    for i, lf in enumerate(leaves):
        if lf.get('type') == 'TO' and i + 1 < len(leaves):
            nxt = leaves[i + 1]
            finite = nxt.get('type') in ('VBD', 'VBZ', 'VBP') \
                or nxt.get('ftag') in ('VBD', 'VBZ', 'VBP') \
                or nxt.get('fpos') == 'AUX' \
                or _lower(nxt).endswith(('ies', 'es'))
            if finite:
                out.append(_finding('6.10', 'error', 'C-TO-BASE', 'infinitive',
                                    nxt['id'],
                                    f"'to' must be followed by the base form, not "
                                    f"'{nxt['surface']}' ({nxt['type'].lower()}).",
                                    _tree_evidence(lf['id'], 'TO + finite verb',
                                                   [{'node': lf['id']},
                                                    {'node': nxt['id']}]),
                                    _rem(f"'{nxt['surface']}' after 'to'.",
                                         f"Use the base form after 'to' instead of "
                                         f"'{nxt['surface']}'.")))
        # 6.12 modal + to
        if (_lower(lf) in MODAL_SURFACES or lf.get('type') == 'MD') \
                and i + 1 < len(leaves) and leaves[i + 1].get('type') == 'TO':
            out.append(_finding('6.12', 'error', 'C-MODAL-TO', 'modal',
                                lf['id'],
                                f"A modal verb takes no 'to': drop 'to' after "
                                f"'{lf['surface']}'.",
                                _tree_evidence(lf['id'], 'MD + TO')))

    # 6.19 Causative + to (make/let + pronoun object + to + VB)
    for i, lf in enumerate(leaves):
        if _lower(lf) in CAUSATIVE_VERBS and lf.get('type') in ('VBD', 'VBZ', 'VBP', 'VB'):
            j = i + 1
            obj = None
            while j < len(leaves) and _lower(leaves[j]) not in ('to',) \
                    and leaves[j].get('type') not in FINITE_TYPES:
                if leaves[j].get('type') == 'PRP' and _lower(leaves[j]) in PRON_OBJ:
                    obj = leaves[j]
                j += 1
            if obj is not None and j < len(leaves) and leaves[j].get('type') == 'TO':
                out.append(_finding('6.19', 'error', 'C-CAUSATIVE-TO', 'causative',
                                    obj['id'],
                                    f"After causative '{lf['surface']}', the object takes a "
                                    f"bare infinitive: drop 'to' before "
                                    f"'{leaves[j + 1]['surface'] if j + 1 < len(leaves) else 'the verb'}'.",
                                    _tree_evidence(lf['id'], 'make/let + NP + TO')))

    # 6.11 Phrasal verb pronoun order: V + RP + pronoun
    for i, lf in enumerate(leaves):
        if lf.get('type') == 'RP' and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'PRP' \
                and _lower(leaves[i + 1]) in PRON_OBJ:
            out.append(_finding('6.11', 'error', 'C-PHRASAL-ORDER', 'phrasal verb',
                                lf['id'],
                                f"With a pronoun object the particle comes last: "
                                f"'{lf['surface']} {leaves[i + 1]['surface']}' \u2192 "
                                f"'{leaves[i + 1]['surface']} {lf['surface']}'.",
                                _wordlist_evidence('V + up/it', ['pick it up'],
                                                   'phrasal-verb order')))

    # 6.9 Gerund vs infinitive
    for i, lf in enumerate(leaves):
        if _lower(lf) in GERUND_VERBS and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'TO':
            out.append(_finding('6.9', 'error', 'C-GERUND-INFINITIVE',
                                'complement type', lf['id'],
                                f"'{lf['surface']}' takes a gerund, not a to-infinitive; "
                                f"use 'enjoying' rather than 'to enjoy'.",
                                _wordlist_evidence(lf['surface'], [lf['surface'] + 'ing'],
                                                   'gerund-taking verbs')))

    # 6.20 Verb + clause pattern (suggest him to go)
    for i, lf in enumerate(leaves):
        if _lower(lf) in CLAUSE_PATTERN_VERBS and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'PRP' \
                and i + 2 < len(leaves) and leaves[i + 2].get('type') == 'TO':
            out.append(_finding('6.20', 'error', 'C-VERB-CLAUSE-PATTERN',
                                'complement clause', lf['id'],
                                f"'{lf['surface']}' does not take an object + to-infinitive; "
                                f"use '{lf['surface']} that he go' or "
                                f"'{lf['surface']} going'.",
                                _wordlist_evidence(lf['surface'],
                                                   [lf['surface'] + ' that ...'],
                                                   'verb + clause patterns')))

    # 6.5 Intransitive passive / 6.6 stative progressive
    for i, lf in enumerate(leaves):
        if _lower(lf) in BE_SURFACES and i + 1 < len(leaves):
            nxt = leaves[i + 1]
            if nxt.get('type') == 'VBN' and _lower(nxt) in INTRANSITIVE_VBN:
                out.append(_finding('6.5', 'error', 'C-INTRANSITIVE-PASSIVE',
                                    'voice', nxt['id'],
                                    f"'{nxt['surface']}' is intransitive and has no "
                                    f"passive; use the active voice.",
                                    _wordlist_evidence(nxt['surface'],
                                                       [f"active: '{nxt['surface']}'"],
                                                       'intransitive-verb list')))
            if nxt.get('type') == 'VBG' and _lower(nxt)[:-3] in STATIVE_PROGRESSIVE:
                out.append(_finding('6.6', 'error', 'C-STATIVE-PROGRESSIVE',
                                    'aspect', nxt['id'],
                                    f"'{nxt['surface']}' is a stative verb and is not "
                                    f"used in the progressive; use the simple form.",
                                    _wordlist_evidence(nxt['surface'],
                                                       [_lower(nxt)[:-3] + 's'],
                                                       'stative-verb list')))

    # 8.6 Preposition + gerund
    lows = [_lower(lf) for lf in leaves]
    for phrase in PREP_GERUND_PHRASES:
        plen = len(phrase)
        for i in range(len(lows) - plen):
            if tuple(lows[i:i + plen]) == phrase:
                after = i + plen
                if after < len(leaves) and leaves[after].get('type') == 'VB':
                    out.append(_finding('8.6', 'error', 'C-PREP-GERUND',
                                        'preposition + gerund', leaves[after]['id'],
                                        f"After the prepositional 'to' in "
                                        f"'{' '.join(phrase)}', use a gerund "
                                        f"('the-ing' form), not '{leaves[after]['surface']}'.",
                                        _tree_evidence(leaves[i]['id'],
                                                       'P + to + VBG')))

    # 9.9 Conjunction pairing (although ... but)
    lows_set = set(lows)
    if 'although' in lows_set and 'but' in lows_set:
        idx = next(i for i, x in enumerate(lows) if x == 'but')
        out.append(_finding('9.9', 'error', 'C-CONJUNCTION-PAIR', 'conjunction',
                            leaves[idx]['id'],
                            "Use either 'although' or 'but', not both, to link the "
                            "clauses.",
                            _wordlist_evidence('although ... but', ['although ...'],
                                               'conjunction-pairing table')))

    # 10.3 Terminal punctuation
    raw = (text or root.get('surface') or '').rstrip()
    if raw and raw[-1] not in '.?!':
        out.append(_finding('10.3', 'error', 'C-TERMINAL-PUNCT', 'punctuation',
                            root['id'],
                            "The sentence does not end with a terminal mark "
                            "('.', '?' or '!').",
                            _tree_evidence(root['id'], 'sentence boundary')))

    # 10.9 Spacing and repeats (function-word doubling)
    for i in range(1, len(leaves)):
        a, b = _lower(leaves[i - 1]), _lower(leaves[i])
        if a == b and a in {'the', 'a', 'an', 'of', 'to', 'in', 'on', 'is',
                            'was', 'are', 'and', 'or', 'very', 'my', 'your',
                            'his', 'her', 'its', 'our', 'their'}:
            out.append(_finding('10.9', 'error', 'C-SPACING-REPEAT', 'spacing',
                                leaves[i]['id'],
                                f"Repeated word '{leaves[i]['surface']}'.",
                                _tree_evidence(leaves[i]['id'], 'token i == token i+1')))

    # 10.5 Apostrophe (decade)
    import re as _re
    surface = (text if text else (root.get('surface') or ''))
    for m in _re.finditer(r"\b(\d{4})'s\b", surface):
        if m.group(1).endswith('0'):
            out.append(_finding('10.5', 'error', 'C-APOSTROPHE', 'apostrophe',
                                leaves[0]['id'],
                                f"Decades are written without an apostrophe: "
                                f"'{m.group(0)}' \u2192 '{m.group(1)}s'.",
                                _tree_evidence(leaves[0]['id'], 'decade apostrophe')))

    # 10.6 Quotation marks (unbalanced)
    if surface.count('"') % 2 == 1 or surface.count('\u201c') != surface.count('\u201d'):
        out.append(_finding('10.6', 'error', 'C-QUOTATION', 'quotation',
                            root['id'],
                            "Unbalanced quotation marks.",
                            _tree_evidence(root['id'], 'matching quotes')))

    return out


def _check_adjective_adverb(leaves):
    out = []
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        nxt = leaves[i + 1] if i + 1 < len(leaves) else None
        # 7.2 Adjective order (opinion < size < age < shape < colour < origin < material)
        if lf.get('type') in ('JJ', 'JJR', 'JJS') and nxt is not None \
                and nxt.get('type') in ('JJ', 'JJR', 'JJS'):
            r1 = ADJ_ORDER_RANK.get(low)
            r2 = ADJ_ORDER_RANK.get(_lower(nxt))
            if r1 is not None and r2 is not None and r1 > r2:
                out.append(_finding('7.2', 'error', 'C-ADJ-ORDER', 'adjective order',
                                    lf['id'],
                                    f"Adjective order: '{lf['surface']} {nxt['surface']}' "
                                    f"should be '{nxt['surface']} {lf['surface']}'.",
                                    _wordlist_evidence(
                                        f"{lf['surface']} {nxt['surface']}",
                                        [f"{nxt['surface']} {lf['surface']}"],
                                        'adjective-order categories')))
        # 7.5 enough big / too much good
        if low == 'enough' and nxt is not None and nxt.get('type') in (
                'JJ', 'JJR', 'JJS'):
            out.append(_finding('7.5', 'error', 'C-INTENSIFIER', 'intensifier',
                                lf['id'],
                                f"'enough' follows the adjective: "
                                f"'{nxt['surface']} enough', not 'enough {nxt['surface']}'.",
                                _tree_evidence(lf['id'], 'enough + JJ')))
        if low == 'much' and i >= 1 and _lower(leaves[i - 1]) == 'too' \
                and nxt is not None and nxt.get('type') in ('JJ', 'JJR', 'JJS'):
            out.append(_finding('7.5', 'error', 'C-INTENSIFIER', 'intensifier',
                                lf['id'],
                                f"'{nxt['surface']}' is a gradable adjective; use "
                                f"'too {nxt['surface']}', not 'too much {nxt['surface']}'.",
                                _tree_evidence(lf['id'], 'too much + JJ')))
        # 7.6 as tall than
        if low == 'as' and nxt is not None and nxt.get('type') in ('JJ', 'JJR', 'JJS'):
            for k in range(i + 2, min(i + 5, len(leaves))):
                if _lower(leaves[k]) == 'than':
                    out.append(_finding('7.6', 'error', 'C-COMPARATIVE-STRUCT',
                                        'comparative', leaves[k]['id'],
                                        f"Use 'as \u2026 as', not 'as \u2026 than'.",
                                        _tree_evidence(lf['id'], 'as ADJ than')))
                    break
        # 7.6 more tall (analytic + morphological)
        if low in ('more', 'most') and nxt is not None and nxt.get('type') == 'JJ' \
                and _lower(nxt) in SHORT_MORPH_ADJ:
            cmp_form = _lower(nxt) + ('er' if low == 'more' else 'est')
            out.append(_finding('7.6', 'error', 'C-COMPARATIVE-STRUCT',
                                'comparative', nxt['id'],
                                f"'{nxt['surface']}' takes the morphological form "
                                f"'{cmp_form}', not '{low} {nxt['surface']}'.",
                                _wordlist_evidence(f"{low} {nxt['surface']}",
                                                   [cmp_form],
                                                   'short-adjective comparative rule')))
    return out


# --------------------------------------------------------------------------- #
# Additional deterministic T/L rules from docs/matrix.md                       #
# --------------------------------------------------------------------------- #
def _check_more(root, clauses, leaves):
    out = []
    lows = [_lower(x) for x in leaves]

    # 1.1 / 1.2 plural forms (word list)
    for lf in leaves:
        low = _lower(lf)
        if lf.get('type') in ('NNS', 'NN') and low in KNOWN_PLURALS:
            # 'person/people' only wrong in the singular-replaced sense; skip base
            fix = KNOWN_PLURALS[low]
            if low == fix:
                continue
            if low == 'person' and lf.get('type') == 'NN':
                continue  # 'a person' is correct; only 'persons' is odd
            out.append(_finding('1.1', 'error', 'C-PLURAL-FORM', 'noun number',
                                lf['id'],
                                f"Wrong plural/singular form '{lf['surface']}'; "
                                f"use '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'plural-forms table')))

    # 3.8 each / every / another / whole + plural noun
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        if low in {'another', 'each', 'every', 'whole'} and i + 1 < len(leaves):
            nxt = leaves[i + 1]
            if nxt.get('type') in ('NNS', 'NNPS'):
                out.append(_finding('3.8', 'error', 'C-DET-NOUN-AGREE',
                                    'determiner', lf['id'],
                                    f"'{lf['surface']}' takes a singular count noun, "
                                    f"not the plural '{nxt['surface']}'.",
                                    _wordlist_evidence(f"{lf['surface']} {nxt['surface']}",
                                                       [f"{lf['surface']} <singular noun>"],
                                                       'determiner\u2013noun number')))

    # 5.2 coordinate subject in objective case (Me and him went)
    top_ids = {root['id']}
    for c in root.get('children', []):
        if c.get('type') in ('S', 'SQ', 'SINV', 'SBARQ'):
            top_ids.add(c['id'])
    for clause in clauses:
        if clause['id'] not in top_ids:
            continue
        subj = None
        for c in clause.get('children', []):
            if c.get('type') == 'NP':
                subj = c
                break
        if subj is None:
            continue
        sub_leaves = _leaves(subj)
        if not any(x.get('type') == 'CC' for x in sub_leaves):
            continue
        cl = sub_leaves
        if cl and cl[0].get('type') == 'PRP' \
                and _lower(cl[0]) in {'me', 'him', 'her', 'us', 'them'}:
            fix = {'me': 'I', 'him': 'he', 'her': 'she', 'us': 'we',
                   'them': 'they'}[_lower(cl[0])]
            out.append(_finding('5.2', 'error', 'C-COORD-CASE', 'pronoun case',
                                cl[0]['id'],
                                f"Subject pronouns take the nominative case: "
                                f"'{cl[0]['surface']}' \u2192 '{fix}'.",
                                _tree_evidence(clause['id'], 'coordinate NP subject',
                                               [{'node': cl[0]['id']}])))

    # 5.5 dummy it/there (Is raining)
    for clause in clauses:
        if clause.get('type') != 'S':
            continue
        kids = clause.get('children', [])
        if any(c.get('type') in ('NP', 'SBAR') for c in kids):
            continue
        cl = _leaves(clause)
        if len(cl) >= 2 and _lower(cl[0]) in ('is', 'was', 'are', 'were',
                                              'seems', 'seemed') \
                and cl[1].get('type') in ('VBG', 'VBN', 'JJ'):
            out.append(_finding('5.5', 'error', 'C-DUMMY-IT', 'subject',
                                clause['id'],
                                f"Add the dummy subject 'It' (e.g. 'It is "
                                f"{cl[1]['surface']}').",
                                _tree_evidence(clause['id'], 'VP with no subject')))

    # 6.5 intransitive passive (was happened)
    for i, lf in enumerate(leaves):
        if _lower(lf) in BE_SURFACES and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'VBN':
            vbn = _lower(leaves[i + 1])
            stem = vbn[:-2] if vbn.endswith('ed') else vbn
            if stem in INTRANSITIVE_VERBS or vbn in ('happened', 'occurred',
                                                     'died'):
                out.append(_finding('6.5', 'error', 'C-INTRANSITIVE-PASSIVE',
                                    'voice', lf['id'],
                                    f"'{leaves[i + 1]['surface']}' is intransitive and "
                                    'cannot be used in the passive.',
                                    _wordlist_evidence(
                                        f"{lf['surface']} {leaves[i + 1]['surface']}",
                                        [], 'intransitive-verb list')))

    # 6.8 verbs needing a preposition, not a direct object (arrived the station)
    for i, lf in enumerate(leaves):
        base = _lower(lf)
        cands = {base}
        if base.endswith('ed'):
            cands.update({base[:-1], base[:-2]})
        if base.endswith('ing'):
            cands.update({base[:-3], base[:-3] + 'e'})
        if base.endswith('es'):
            cands.add(base[:-2])
        elif base.endswith('s'):
            cands.add(base[:-1])
        if (cands & PREP_REQUIRED_VERBS) and i + 1 < len(leaves):
            nxt = leaves[i + 1]
            if nxt.get('type') in ('DT', 'NN', 'NNS', 'NNP', 'PRP') \
                    and _lower(nxt) not in ('home', 'here', 'there', 'abroad',
                                            'up', 'down', 'in', 'out',
                                            'back', 'away'):
                out.append(_finding('6.8', 'error', 'C-TRANSITIVITY',
                                    'transitivity', lf['id'],
                                    f"'{lf['surface']}' does not take a direct object; "
                                    'a preposition is required.',
                                    _wordlist_evidence(lf['surface'], [],
                                                       'verb transitivity list')))

    # 6.14 double negation
    for clause in clauses:
        cl = _leaves(clause)
        negs = [x for x in cl if _lower(x) in {'not', 'no', 'nothing', 'nobody',
                                               'none', 'never', 'nowhere',
                                               "n't", 'nt'}]
        if len(negs) >= 2:
            out.append(_finding('6.14', 'error', 'C-DOUBLE-NEGATIVE', 'negation',
                                clause['id'],
                                'Two negatives in one clause; standard English '
                                'uses a single negation.',
                                _tree_evidence(clause['id'], 'neg + neg',
                                               [{'node': negs[0]['id']},
                                                {'node': negs[1]['id']}])))

    # 6.15 imperative don't + finite verb
    for i, lf in enumerate(leaves):
        if _lower(lf) in ('do', 'does', 'did') and i + 2 < len(leaves) \
                and _lower(leaves[i + 1]) in ("n't", 'nt', 'not'):
            v = leaves[i + 2]
            if _lower(v) in ('goes', 'went', 'has', 'does', 'is', 'was') \
                    or v.get('type') in ('VBZ', 'VBD'):
                out.append(_finding('6.15', 'error', 'C-IMPERATIVE-VERB',
                                    'imperative', v['id'],
                                    'After an imperative negator use the base form.',
                                    _tree_evidence(lf['id'], "do + n't + finite")))

    # 6.16 conditional with 'will' (If I will go)
    for i, lf in enumerate(leaves):
        if _lower(lf) == 'if':
            window = [_lower(x) for x in leaves[i + 1:i + 4]]
            hit = next((w for w in window if w in ('will', 'would')), None)
            if hit:
                out.append(_finding('6.16', 'error', 'C-CONDITIONAL-WILL',
                                    'conditional', leaves[i]['id'],
                                    f"Use the present tense in an 'if'-clause, not "
                                    f"'{hit}'.",
                                    _tree_evidence(lf['id'], 'if + will')))

    # 6.18 reported speech (She said me)
    for i, lf in enumerate(leaves):
        if _lower(lf) in ('said', 'say') and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) in PRON_OBJ \
                and _lower(leaves[i + 1]) not in ('it',):
            out.append(_finding('6.18', 'error', 'C-REPORTED-SPEECH',
                                'reported speech', lf['id'],
                                f"'{lf['surface']}' takes 'to' before the recipient: "
                                f"'{lf['surface']} to {leaves[i + 1]['surface']}'.",
                                _tree_evidence(lf['id'], 'say + object pronoun')))

    # 9.3 run-on / fused sentence (two finite clauses with no linker)
    BRIDGE_VERBS = {'think', 'know', 'say', 'says', 'said', 'believe', 'hope',
                    'wish', 'hear', 'see', 'feel', 'guess', 'suppose',
                    'remember', 'forget', 'decide', 'expect', 'find', 'notice',
                    'imagine', 'agree', 'doubt', 'deny', 'admit', 'promise',
                    'claim', 'state', 'reply', 'answer', 'understand',
                    'realize', 'tell', 'told', 'wonder', 'ask', 'explain',
                    'mention'}
    WH_WORDS = {'who', 'whom', 'whose', 'which', 'that', 'where', 'when',
                'why', 'how', 'whether', 'if', 'what'}
    seen_marker = False
    for i, lf in enumerate(leaves):
        if _lower(lf) in WH_WORDS or _lower(lf) in SUBORDINATORS:
            seen_marker = True
            continue
        if lf.get('type') not in FINITE_TYPES:
            continue
        if _lower(lf) in BRIDGE_VERBS:
            seen_marker = True
            continue
        if seen_marker:
            continue
        for j in range(i + 1, len(leaves)):
            x = leaves[j]
            if _lower(x) in WH_WORDS or _lower(x) in SUBORDINATORS \
                    or x.get('type') in ('CC', ',', ';', ':', '.'):
                break
            if x.get('type') in FINITE_TYPES:
                between = leaves[i + 1:j]
                if any(b.get('type') in ('PRP', 'NN', 'NNS', 'NNP') for b in between):
                    out.append(_finding('9.3', 'error', 'C-RUNON',
                                        'sentence boundary', x['id'],
                                        "Run-on sentence: two finite clauses are "
                                        "joined without punctuation or a conjunction.",
                                        _tree_evidence(x['id'], 'finite ... finite',
                                                       [{'node': lf['id']},
                                                        {'node': x['id']}])))
                break

    # 9.7 extra word (very the happy)
    for i, lf in enumerate(leaves):
        if _lower(lf) in ('very', 'really', 'so', 'too') and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'DT':
            out.append(_finding('9.7', 'error', 'C-EXTRA-WORD', 'word order',
                                leaves[i + 1]['id'],
                                f"Unexpected determiner after '{lf['surface']}'.",
                                _tree_evidence(lf['id'], 'adverb + determiner')))

    # 2.9 quantified subject: 'the number of X' takes a singular verb
    for i in range(len(leaves) - 2):
        if _lower(leaves[i]) == 'the' and _lower(leaves[i + 1]) == 'number' \
                and _lower(leaves[i + 2]) == 'of':
            for lf in leaves[i + 3:]:
                if lf.get('type') == 'VBP' or _lower(lf) in ('are', 'were'):
                    out.append(_finding('2.9', 'error', 'C-NUMBER-AGREE',
                                        'agreement', lf['id'],
                                        "'The number of' takes a singular verb "
                                        "(only 'a number of' takes a plural).",
                                        _tree_evidence(leaves[i + 1]['id'],
                                                       'the number of + plural verb')))
                    break
                if lf.get('type') in ('VBZ',) or _lower(lf) in ('is', 'was'):
                    break

    # 10.2 proper nouns, I, days, months
    for lf in leaves:
        surface = lf.get('surface') or ''
        low = surface.lower()
        if surface == 'i':
            out.append(_finding('10.2', 'error', 'C-PROPER-NOUN', 'capitalization',
                                lf['id'], "The pronoun 'I' is always capitalized.",
                                _wordlist_evidence('i', ['I'], 'capitalization list')))
        elif low in DAYS or (low in MONTHS and low not in {'may', 'march',
                                                           'august'}):
            if surface[:1].islower():
                out.append(_finding('10.2', 'error', 'C-PROPER-NOUN',
                                    'capitalization', lf['id'],
                                    f"'{surface}' (day/month) must be capitalized "
                                    f"as '{surface.capitalize()}'.",
                                    _wordlist_evidence(surface, [surface.capitalize()],
                                                       'day/month list')))

    # 5.6 possessive determiner with no noun (This is my)
    POSS_DET = {'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    for i, lf in enumerate(leaves):
        if lf.get('type') == 'PRP$' and _lower(lf) in POSS_DET \
                and (i + 1 == len(leaves)
                     or leaves[i + 1].get('type') in ('.', ',', '!', '?', ';', ':')):
            out.append(_finding('5.6', 'error', 'C-POSSESSIVE', 'determiner',
                                lf['id'],
                                f"The possessive determiner '{lf['surface']}' needs a "
                                'noun; a possessive pronoun stands alone instead '
                                f"(e.g. 'mine'/'yours').",
                                _wordlist_evidence(lf['surface'],
                                                   ['mine', 'yours', 'his', 'hers',
                                                    'ours', 'theirs'],
                                                   'possessive determiner/pronoun table')))

    # 10.10 numbers, dates, abbreviations (ordinal suffix)
    import re as _re2
    for lf in leaves:
        surface = lf.get('surface') or ''
        m = _re2.fullmatch(r'(\d+)(st|nd|rd|th)', surface.lower())
        if not m:
            continue
        num, suffix = int(m.group(1)), m.group(2)
        if 10 <= num % 100 <= 20:
            correct = 'th'
        else:
            correct = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
        if suffix != correct:
            out.append(_finding('10.10', 'error', 'C-NUMERAL-FORMAT',
                                'numeral format', lf['id'],
                                f"Wrong ordinal suffix: '{surface}' \u2192 "
                                f"'{num}{correct}'.",
                                _wordlist_evidence(surface, [f"{num}{correct}"],
                                                   'ordinal-suffix rule')))

    # 2.13 correlatives (either/neither ... or/nor) agree with nearest subject
    for clause in clauses:
        np = None
        for c in clause.get('children', []):
            if c.get('type') == 'NP':
                np = c
                break
        if np is None:
            continue
        nleaves = _leaves(np)
        if not any(x.get('type') == 'CC' for x in nleaves):
            continue
        if not any(_lower(x) in ('either', 'neither') for x in nleaves):
            continue
        nearest = None
        for x in nleaves:
            if x.get('type') in ('PRP', 'NN', 'NNS', 'NNP', 'NNPS'):
                nearest = x
        if nearest is None or nearest.get('type') != 'PRP':
            continue
        vp = None
        for c in clause.get('children', []):
            if c.get('type') == 'VP':
                vp = c
        if vp is None:
            continue
        vhead = None
        for x in _leaves(vp):
            if x.get('type') in FINITE_TYPES or x.get('type') in ('VBZ', 'VBP', 'VBD'):
                vhead = x
                break
        if vhead is None:
            continue
        nlow, vlow = _lower(nearest), _lower(vhead)
        if nlow == 'i' and vlow not in ('am', 'was'):
            out.append(_finding('2.13', 'error', 'C-CORRELATIVE-AGREE', 'agreement',
                                vhead['id'],
                                f"With correlatives, the verb agrees with the nearest "
                                f"subject '{nearest['surface']}': use 'am', not "
                                f"'{vhead['surface']}'.",
                                _tree_evidence(nearest['id'],
                                               'nearest subject + verb')))
        elif nlow in ('he', 'she', 'it') and vlow in ('are', 'were'):
            out.append(_finding('2.13', 'error', 'C-CORRELATIVE-AGREE', 'agreement',
                                vhead['id'],
                                f"With correlatives, the verb agrees with the nearest "
                                f"subject '{nearest['surface']}': use 'is/was', not "
                                f"'{vhead['surface']}'.",
                                _tree_evidence(nearest['id'],
                                               'nearest subject + verb')))

    # 1.3 possessive 's missing (the boys toy)
    ANIMATE_PLURAL = {'boys', 'girls', 'men', 'women', 'children', 'students',
                      'teachers', 'friends', 'parents', 'brothers', 'sisters',
                      'kids', 'babies', 'people'}
    NOUN_TAGS = ('NN', 'NNS', 'NNP', 'NNPS')
    for node in _iter_nodes(root):
        ch = node.get('children', [])
        for a, b in zip(ch, ch[1:]):
            if a.get('type') != 'NP' or b.get('type') != 'NP':
                continue
            aleaves = _leaves(a)
            bleaves = _leaves(b)
            ahead = aleaves[-1] if aleaves else None
            bhead = bleaves[-1] if bleaves else None
            if ahead is None or bhead is None:
                continue
            if ahead.get('type') != 'NNS' or _lower(ahead) not in ANIMATE_PLURAL:
                continue
            if bhead.get('type') not in NOUN_TAGS:
                continue
            if any(x.get('type') == 'DT' for x in bleaves):
                continue
            out.append(_finding('1.3', 'error', 'C-POSSESSIVE-S', 'possessive',
                                ahead['id'],
                                f"Possessive needed: '{ahead['surface']}' + "
                                f"'{bhead['surface']}' \u2192 "
                                f"'{ahead['surface']}\u2019 {bhead['surface']}'.",
                                _wordlist_evidence(f"{ahead['surface']} {bhead['surface']}",
                                                   [f"{ahead['surface']}\u2019 {bhead['surface']}"],
                                                   'possessive \u2019s rule')))

    # 9.11 dangling / misplaced modifier (Walking home, the rain started)
    for node in _iter_nodes(root):
        ch = node.get('children', [])
        for i, c in enumerate(ch):
            if c.get('type') not in ('S', 'SBAR'):
                continue
            cleaves = _leaves(c)
            if not cleaves or cleaves[0].get('type') != 'VBG':
                continue
            if i + 1 >= len(ch):
                continue
            nxt = ch[i + 1]
            if nxt.get('type') == ',' or (nxt.get('type') == 'NP'):
                msubj = None
                for m in ch[i + 1:]:
                    if m.get('type') == 'NP':
                        msubj = m
                        break
                if msubj is None:
                    continue
                mhead = _leaves(msubj)[-1] if _leaves(msubj) else None
                if mhead is not None and _lower(mhead) in INANIMATE_SUBJECTS:
                    out.append(_finding('9.11', 'suggestion', 'C-DANGLING',
                                        'modifier', cleaves[0]['id'],
                                        f"The opener '{cleaves[0]['surface']} ...' describes "
                                        'the subject of the main clause, but '
                                        f"'{mhead['surface']}' cannot perform it.",
                                        _context_evidence(
                                            f"participial opener vs subject '{mhead['surface']}'",
                                            [{'option': 'revise the opener',
                                              'evidence': 'the subject cannot do the action'},
                                             {'option': 'move the modifier',
                                              'evidence': 'attach it to the doer'}],
                                            0.55)))
                break

    # 10.4 missing comma after an introductory connector
    CONNECTORS = {'however', 'therefore', 'moreover', 'furthermore',
                  'nevertheless', 'nonetheless', 'meanwhile', 'otherwise',
                  'besides', 'consequently', 'thus', 'hence', 'additionally'}
    for clause in clauses:
        cleaves = _leaves(clause)
        if len(cleaves) >= 2 and _lower(cleaves[0]) in CONNECTORS \
                and cleaves[1].get('type') in ('PRP', 'DT', 'NNP', 'NNPS', 'NNS'):
            out.append(_finding('10.4', 'error', 'C-INTRO-COMMA', 'punctuation',
                                cleaves[0]['id'],
                                f"An introductory connector is followed by a comma: "
                                f"'{cleaves[0]['surface']}, ...'.",
                                _wordlist_evidence(cleaves[0]['surface'],
                                                   [f"{cleaves[0]['surface']},"],
                                                   'punctuation rule')))

    # 10.8 semicolon misused to join list items inside an NP
    for node in _iter_nodes(root):
        if node.get('type') != 'NP':
            continue
        for lf in _leaves(node):
            if (lf.get('surface') or '') == ';':
                out.append(_finding('10.8', 'error', 'C-PUNCT', 'punctuation',
                                    lf['id'],
                                    "A semicolon joins independent clauses; use a comma "
                                    'for items in a list.',
                                    _wordlist_evidence(';', [','], 'punctuation rule')))
                break

    # 6.4 passive formation (inanimate subject + by-phrase without be)
    for clause in clauses:
        subj = None
        vp = None
        for c in clause.get('children', []):
            if c.get('type') == 'NP' and subj is None:
                subj = c
            if c.get('type') == 'VP' and vp is None:
                vp = c
        if subj is None or vp is None:
            continue
        subleaves = _leaves(subj)
        subhead = subleaves[-1] if subleaves else None
        if subhead is None or _lower(subhead) not in INANIMATE_SUBJECTS:
            continue
        vpleaves = _leaves(vp)
        if not vpleaves:
            continue
        if any(_lower(x) in TO_BE_SURFACES for x in vpleaves):
            continue
        has_by = any(_lower(x) == 'by' for x in vpleaves)
        verb = vpleaves[0]
        if has_by and verb.get('type') in ('VBD', 'VB', 'VBN'):
            out.append(_finding('6.4', 'error', 'C-PASSIVE', 'voice',
                                verb['id'],
                                f"Passive voice needs 'be' + past participle: "
                                f"'{subhead['surface']} was {verb['surface']}' "
                                '(or a correct participle).',
                                _tree_evidence(verb['id'],
                                               'be + VBN + by-phrase')))

    # 9.6 word order in statements (object NP before the verb)
    TIME_WORDS = {'today', 'yesterday', 'tomorrow', 'tonight', 'now', 'later',
                  'then', 'soon'}
    for clause in clauses:
        ch = clause.get('children', [])
        if any(c.get('type') == ',' for c in ch):
            continue
        vp_pos = [i for i, c in enumerate(ch) if c.get('type') == 'VP']
        if not vp_pos:
            continue
        vfirst = vp_pos[0]
        pre = [ch[i] for i, c in enumerate(ch)
               if c.get('type') == 'NP' and i < vfirst]
        if len(pre) >= 2:
            heads = []
            for np in pre:
                nl = _leaves(np)
                heads.append(_lower(nl[-1]) if nl else '')
            if all(h not in TIME_WORDS for h in heads):
                vp = ch[vfirst]
                vl = _leaves(vp)
                out.append(_finding('9.6', 'error', 'C-WORD-ORDER', 'word order',
                                    vl[0]['id'] if vl else vp['id'],
                                    'In a statement the object follows the verb; this '
                                    'looks like object-before-verb order.',
                                    _tree_evidence(vp['id'],
                                                   'object NP + VP')))
                break

    # 2.3 coordinated subjects (and / or / nor) agree with the predicate verb
    top_ids = {root['id']}
    for c in root.get('children', []):
        if c.get('type') in ('S', 'SQ', 'SINV', 'SBARQ'):
            top_ids.add(c['id'])
    for clause in clauses:
        if clause.get('type') != 'S' or clause['id'] not in top_ids:
            continue
        subj = vp = None
        for c in clause.get('children', []):
            if c.get('type') == 'NP' and subj is None:
                subj = c
            elif c.get('type') == 'VP' and vp is None:
                vp = c
        if subj is None or vp is None:
            continue
        sleaves = _leaves(subj)
        ccs = [x for x in sleaves if x.get('type') == 'CC']
        if not ccs:
            continue
        conj = _lower(ccs[0])
        vhead = None
        for x in _leaves(vp):
            if x.get('type') in ('VBZ', 'VBP') or _lower(x) in (
                    BE_SURFACES | HAVE_SURFACES | DO_SURFACES):
                vhead = x
                break
        if vhead is None:
            continue
        vkey = _verb_key(vhead)
        vlow = _lower(vhead)
        heads = [x for x in sleaves
                 if x.get('type') in ('NN', 'NNS', 'NNP', 'NNPS', 'PRP')]
        if len(heads) < 2:
            continue
        if conj in ('and', '&'):
            joined = ' '.join(_lower(x) for x in sleaves)
            if joined in {'bread and butter', 'peanut butter and jelly',
                          'fish and chips', 'gin and tonic'}:
                continue
            if vkey == ('3', 'sg') or vlow in ('is', 'was', 'has', 'does'):
                out.append(_finding('2.3', 'error', 'C-COORD-SUBJ-AGREE',
                                    'subject-verb agreement', vhead['id'],
                                    f"A coordinated subject is plural: "
                                    f"'{subj['surface']}' needs a plural verb, not "
                                    f"'{vhead['surface']}'.",
                                    _tree_evidence(ccs[0]['id'],
                                                   'NP CC NP + singular verb',
                                                   [{'node': ccs[0]['id']},
                                                    {'node': vhead['id']}])))
        elif conj in ('or', 'nor'):
            near = heads[-1]
            nkey = None
            if near.get('type') in ('NNS', 'NNPS'):
                nkey = ('3', 'pl')
            elif near.get('type') in ('NN', 'NNP', 'NML', 'NX'):
                nkey = ('3', 'sg')
            elif near.get('type') == 'PRP':
                nkey = PRP_PERSON.get(_lower(near))
            if nkey is None:
                continue
            if nkey[1] == 'sg' and vkey in (('*', 'non3sg'), ('3', 'pl')):
                out.append(_finding('2.3', 'error', 'C-COORD-SUBJ-AGREE',
                                    'subject-verb agreement', vhead['id'],
                                    f"With 'or'/'nor' the verb agrees with the "
                                    f"nearest subject '{near['surface']}': use the "
                                    f"singular form, not '{vhead['surface']}'.",
                                    _tree_evidence(near['id'],
                                                   'nearest NP + verb',
                                                   [{'node': near['id']},
                                                    {'node': vhead['id']}])))
            elif nkey[1] == 'pl' and (vkey == ('3', 'sg')
                                      or vlow in ('is', 'was', 'has', 'does')):
                out.append(_finding('2.3', 'error', 'C-COORD-SUBJ-AGREE',
                                    'subject-verb agreement', vhead['id'],
                                    f"With 'or'/'nor' the verb agrees with the "
                                    f"nearest subject '{near['surface']}' (plural).",
                                    _tree_evidence(near['id'],
                                                   'nearest NP + verb',
                                                   [{'node': near['id']},
                                                    {'node': vhead['id']}])))

    # 4.2 noun as modifier must be singular (a ten-years plan)
    MEASURE_SG = {'years': 'year', 'months': 'month', 'weeks': 'week',
                  'days': 'day', 'hours': 'hour', 'minutes': 'minute',
                  'miles': 'mile', 'meters': 'meter', 'metres': 'metre',
                  'kilometers': 'kilometer', 'feet': 'foot', 'inches': 'inch',
                  'pounds': 'pound', 'dollars': 'dollar', 'percents': 'percent'}
    for node in _iter_nodes(root):
        if node.get('type') != 'NP':
            continue
        nleaves = _leaves(node)
        for idx in range(len(nleaves) - 1):
            a, b = nleaves[idx], nleaves[idx + 1]
            if a.get('type') in ('NNS', 'NNPS') \
                    and b.get('type') in ('NN', 'NNP') \
                    and _lower(a) in MEASURE_SG:
                fix = MEASURE_SG[_lower(a)]
                out.append(_finding('4.2', 'error', 'C-NOUN-MODIFIER-NUMBER',
                                    'noun modifier', a['id'],
                                    f"An attributive noun is singular: "
                                    f"'{a['surface']} {b['surface']}' \u2192 "
                                    f"'{fix} {b['surface']}'.",
                                    _tree_evidence(node['id'],
                                                   'plural modifier + head noun',
                                                   [{'node': a['id']},
                                                    {'node': b['id']}])))
                break

    # 7.3 adverb placement: verb + adverbial + pronoun object (I like very much it)
    for node in _iter_nodes(root):
        if node.get('type') != 'VP':
            continue
        kids = node.get('children', [])
        for i, k in enumerate(kids[:-1]):
            if k.get('type') not in ('ADVP', 'PRT'):
                continue
            if i > 0 and kids[i - 1].get('type') not in (
                    'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'VP'):
                continue
            nxt = kids[i + 1]
            if nxt.get('type') != 'NP':
                continue
            nhead = _np_head_leaf(nxt)
            if nhead is None or nhead.get('type') != 'PRP':
                continue
            out.append(_finding('7.3', 'error', 'C-ADVERB-PLACEMENT',
                                'adverb position', k['id'],
                                f"The adverbial '{k['surface']}' sits between the "
                                f"verb and its pronoun object; move it after "
                                f"'{nhead['surface']}' "
                                f"(e.g. '... {nhead['surface']} {k['surface']}').",
                                _tree_evidence(node['id'],
                                               'V + ADVP + PRP object',
                                               [{'node': k['id']},
                                                {'node': nhead['id']}])))
            break

    # 8.5 wrong in/on/at for time and place (on 5 pm)
    DAY_WORDS = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                 'saturday', 'sunday'}
    MONTH_WORDS = {'january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november',
                   'december'}
    PART_DAY = {'morning', 'afternoon', 'evening'}
    CLOCK = {'pm', 'am', "o'clock", "o' clock", 'clock'}
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        if low not in ('in', 'on', 'at'):
            continue
        nxt = leaves[i + 1] if i + 1 < len(leaves) else None
        if nxt is None:
            continue
        w = _lower(nxt)
        after = [_lower(x) for x in leaves[i + 1:i + 4]]
        is_clock = nxt.get('type') == 'CD' or any(a in CLOCK for a in after)
        tgt = None
        if low == 'at' and w in DAY_WORDS:
            tgt = 'on'
        elif low == 'at' and w in MONTH_WORDS:
            tgt = 'in'
        elif low == 'in' and w in DAY_WORDS:
            tgt = 'on'
        elif low == 'on' and w in MONTH_WORDS:
            tgt = 'in'
        elif low == 'on' and is_clock:
            tgt = 'at'
        elif low == 'in' and is_clock:
            tgt = 'at'
        elif low == 'on' and w in ('night', 'noon', 'midnight'):
            tgt = 'at'
        elif low == 'in' and w in ('night', 'noon', 'midnight'):
            tgt = 'at'
        elif low == 'at' and w in PART_DAY:
            tgt = 'in'
        elif low == 'on' and w in PART_DAY and 'of' not in after[1:]:
            tgt = 'in'
        if tgt:
            out.append(_finding('8.5', 'error', 'C-TIME-PLACE-PREP',
                                'preposition choice', nxt['id'],
                                f"For a time expression, '{low} {w}...' is not "
                                f"standard; use '{tgt}'.",
                                _wordlist_evidence(f"{low} {w}",
                                                   [f"{tgt} {w}"],
                                                   'in/on/at time table')))
            continue
        # 'in/on/at' + next/last + time word takes no preposition (in next Monday)
        nxt2 = leaves[i + 2] if i + 2 < len(leaves) else None
        if nxt2 is not None and w in ('next', 'last'):
            w2 = _lower(nxt2)
            if w2 in DAY_WORDS or w2 in MONTH_WORDS or w2 in (
                    'week', 'month', 'year', 'weekend', 'summer', 'winter',
                    'spring', 'fall'):
                out.append(_finding('8.5', 'error', 'C-TIME-PLACE-PREP',
                                    'preposition choice', nxt['id'],
                                    f"'{low} {w} {w2}' takes no preposition: use "
                                    f"'{w} {w2}'.",
                                    _wordlist_evidence(f"{low} {w} {w2}",
                                                       [f"{w} {w2}"],
                                                       'in/on/at time table')))

    # 9.1 fragment: a subordinate clause standing alone (Because I was late.)
    if root.get('type') == 'SBAR':
        out.append(_finding('9.1', 'error', 'C-FRAGMENT', 'sentence structure',
                            root['id'],
                            "This is a subordinate clause with no main clause "
                            "(a fragment). Add a main clause to complete the "
                            "sentence.",
                            _tree_evidence(root['id'],
                                           'SBAR without a matrix S')))

    # 9.10 relative clause with a resumptive object pronoun (the man who I saw him)
    RELP = {'who', 'whom', 'which', 'that'}
    for node in _iter_nodes(root):
        if node.get('type') != 'SBAR':
            continue
        kids = node.get('children', [])
        whnp = kids[0] if kids and kids[0].get('type') == 'WHNP' else None
        if whnp is None:
            continue
        wl = _leaves(whnp)
        if not wl or _lower(wl[0]) not in RELP:
            continue
        clause = next((c for c in kids if c.get('type') == 'S'), None)
        if clause is None or not clause.get('children'):
            continue
        ck = clause.get('children', [])
        subj = next((c for c in ck if c.get('type') == 'NP'), None)
        if subj is None:
            continue
        vp = next((c for c in ck if c.get('type') == 'VP'), None)
        if vp is None:
            continue
        obj = None
        for c in vp.get('children', []):
            if c.get('type') == 'NP':
                h = _np_head_leaf(c)
                if h is not None and h.get('type') == 'PRP' \
                        and _lower(h) in ('me', 'us', 'him', 'her', 'them'):
                    obj = h
                    break
        if obj is None:
            continue
        out.append(_finding('9.10', 'error', 'C-RESUMPTIVE-RELATIVE',
                            'relative clause', obj['id'],
                            f"Resumptive pronoun '{obj['surface']}': the relative "
                            f"pronoun '{wl[0]['surface']}' already fills the object "
                            'slot, so the noun should not be repeated.',
                            _tree_evidence(node['id'],
                                           'SBAR(WHNP S(NP VP NP-PRP))',
                                           [{'node': wl[0]['id']},
                                            {'node': obj['id']}])))

    # 9.14 subordinator + to-infinitive clause without a subject (because to see you)
    WH_TRIG = {'when', 'where', 'why', 'how', 'whether', 'what', 'who',
               'whom', 'whose', 'which', 'as'}
    for node in _iter_nodes(root):
        if node.get('type') != 'SBAR':
            continue
        kids = node.get('children', [])
        if len(kids) < 2 or kids[0].get('type') != 'IN':
            continue
        if _lower(kids[0]) in WH_TRIG:
            continue
        sc = kids[1]
        if sc.get('type') != 'S':
            continue
        sk = [c for c in sc.get('children', [])
              if c.get('type') in ('NP', 'VP')]
        if not sk or sk[0].get('type') != 'VP':
            continue
        vp = sk[0]
        inc = kids[0]
        vpl = [c.get('type') for c in vp.get('children', [])]
        if 'TO' in vpl or (_leaves(vp) and _leaves(vp)[0].get('type') == 'TO'):
            out.append(_finding('9.14', 'error', 'C-CLAUSE-LINKING',
                                'clause joining', inc['id'],
                                f"'{inc['surface']}' introduces a finite "
                                "clause; a bare 'to'-infinitive (with no subject) "
                                "cannot follow it directly.",
                                _tree_evidence(sc['id'],
                                               'IN + S(VP(TO ...))',
                                               [{'node': inc['id']},
                                                {'node': vp['id']}])))

    # 9.15 ditransitive verb + to/for + pronoun, then the object (gave to me a book)
    DITRANSITIVE = {'give', 'gives', 'gave', 'given', 'send', 'sends', 'sent',
                    'show', 'shows', 'showed', 'shown', 'tell', 'tells',
                    'told', 'teach', 'teaches', 'taught', 'bring', 'brings',
                    'brought', 'offer', 'offers', 'offered', 'lend', 'lends',
                    'lent', 'hand', 'hands', 'handed', 'pass', 'passes',
                    'passed', 'buy', 'buys', 'bought', 'sell', 'sells',
                    'sold', 'write', 'writes', 'wrote', 'written', 'read',
                    'reads', 'pay', 'pays', 'paid', 'owe', 'owes', 'owed'}
    for node in _iter_nodes(root):
        if node.get('type') != 'VP':
            continue
        kids = node.get('children', [])
        for i, k in enumerate(kids):
            if k.get('type') != 'PP':
                continue
            kl = _leaves(k)
            if not kl or _lower(kl[0]) not in ('to', 'for'):
                continue
            if i == 0:
                continue
            verb = kids[i - 1]
            if _lower(verb) not in DITRANSITIVE:
                continue
            pobj = _np_head_leaf(k)
            if pobj is None or pobj.get('type') != 'PRP':
                continue
            nxt = kids[i + 1] if i + 1 < len(kids) else None
            if nxt is None or nxt.get('type') != 'NP':
                continue
            out.append(_finding('9.15', 'error', 'C-OBJECT-ORDER',
                                'object order', verb['id'],
                                f"Object-order error: the direct object should "
                                f"come right after the verb (e.g. '{verb['surface']} "
                                f"{pobj['surface']} «noun»') or after the whole "
                                f"prepositional phrase.",
                                _tree_evidence(node['id'],
                                               'V + PP(to/for + PRP) + NP',
                                               [{'node': verb['id']},
                                                {'node': pobj['id']}])))

    # 10.1 sentence-initial capitalization (the boy runs)
    first = None
    for n in _iter_nodes(root):
        if 'surface' not in n:
            continue
        if n.get('type') in ('``', '"', "'", '(', '[', 'SYM'):
            continue
        first = n
        break
    if first is not None:
        surf = first.get('surface') or ''
        if surf[:1].isalpha() and surf[:1].islower():
            low = surf.lower()
            if low not in ('i',) and low not in DAYS and low not in MONTH_WORDS:
                out.append(_finding('10.1', 'error', 'C-SENTENCE-CAPITAL',
                                    'capitalization', first['id'],
                                    f"Sentences begin with a capital letter: "
                                    f"'{surf}' \u2192 "
                                    f"'{surf[0].upper() + surf[1:]}'.",
                                    _tree_evidence(root['id'],
                                                   'sentence-initial token',
                                                   [{'node': first['id']}])))

    return out


# --------------------------------------------------------------------------- #
# Basic high-frequency surface errors (the "learners' English" layer).         #
# Deterministic token-stream checks for the most common mistakes: modals,      #
# existential 'there', numerals before singulars, many/much, preposition +     #
# subject pronoun, the it's/its and there/their/your homophones, -ing vs       #
# to-infinitive, 'since' with a non-perfect tense, and stacked/mismatched      #
# forms.  Each finding maps onto an existing RULEBOOK id.                       #
# --------------------------------------------------------------------------- #
MODAL_SURFACES = {'can', 'could', 'may', 'might', 'must', 'shall', 'should',
                  'will', 'would'}
TRUE_PREPS = {'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'of',
              'about', 'over', 'under', 'between', 'among', 'against',
              'without', 'through', 'into', 'onto', 'off', 'out', 'up', 'down',
              'around', 'along', 'across', 'beside', 'behind', 'below', 'above',
              'near', 'past', 'during', 'towards', 'toward', 'upon', 'beyond',
              'except', 'despite', 'within'}
SUBJECT_PRON = {'i', 'we', 'he', 'she', 'they'}
# Numeral / plural-requiring quantifiers (not mass: much / little / less).
PLURALIZERS = {'many', 'several', 'various', 'numerous', 'both'}
# Verbs that take a gerund, never a to-infinitive.
GERUND_TAKERS = {'enjoy', 'finish', 'mind', 'avoid', 'consider', 'suggest',
                 'keep', 'practice', 'quit', 'imagine', 'admit', 'deny',
                 'mention', 'miss', 'postpone', 'resist', 'appreciate',
                 'delay', 'discuss', 'dislike', 'recall', 'recommend'}
# Indefinite pronouns that are always singular.
INDEF_SINGULAR = {'everyone', 'everybody', 'anyone', 'anybody', 'someone',
                  'somebody', 'nobody'}
NONSTANDARD_ADV = {'fastly', 'succesfully'}
# Stative verbs in the progressive ('He is liking this book.').
STATIVE_ING = {'liking', 'knowing', 'wanting', 'needing', 'meaning',
               'believing', 'understanding', 'remembering', 'forgetting',
               'realizing', 'recognizing', 'preferring', 'hating', 'belonging',
               'owning', 'seeming', 'existing', 'mattering', 'consisting',
               'containing', 'depending', 'doubting', 'agreeing', 'deserving',
               'resembling'}
BE_SURFACES_LEAF = {'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
WH_WORDS = {'where', 'when', 'how', 'why', 'what', 'which', 'who', 'whom'}
WH_AUX = {'is', 'are', 'was', 'were', 'do', 'does', 'did', 'have', 'has', 'had'}
SUBJ_PRON_BARE = {'i', 'he', 'she', 'we', 'they'}


def _inflected(lemma):
    forms = {lemma, lemma + 's', lemma + 'ed', lemma + 'ing'}
    if lemma.endswith('y'):
        forms.update({lemma[:-1] + 'ies', lemma[:-1] + 'ied'})
    elif lemma.endswith('e'):
        forms.update({lemma[:-1] + 'd', lemma[:-1] + 'ing'})
    elif lemma.endswith('s') or lemma.endswith('x') or lemma.endswith('z') \
            or lemma.endswith('ch') or lemma.endswith('sh'):
        forms.add(lemma + 'es')
    else:
        forms.add(lemma + 'es')
    return forms


def _base_of(low):
    """Best-effort base form for a verb surface ending in -s / -ed / -ing."""
    if low.endswith('ies'):
        return low[:-3] + 'y'
    if low.endswith('ing'):
        return low[:-3]
    if low.endswith('ed'):
        return low[: -1] if low.endswith('ied') else low[:-2]
    if low.endswith('es'):
        return low[:-2]
    if low.endswith('s'):
        return low[:-1]
    return low


def _is_3sg_marked(nlow):
    """True when a surface ending in -s is the parser-normalised 3rd-singular of
    a verb (benepar happily retags 'must goes' so 'goes' looks like a bare VB)."""
    if not nlow.endswith('s') or nlow in ('is', 'has', 'does', 'was'):
        return False
    try:
        from licensing import _lemmas
        bases = _lemmas(nlow, 'VERB')
        return bool(bases) and nlow not in bases
    except Exception:  # pragma: no cover - licensing unavailable -> heuristic
        return True


def _check_basic(root, clauses, leaves):
    out = []
    lows = [_lower(x) for x in leaves]
    verb_tags = ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')

    # --- 6.1 / 6.12 modals --------------------------------------------------- #
    for i, lf in enumerate(leaves):
        low = lows[i]
        if low not in MODAL_SURFACES or i + 1 >= len(leaves):
            continue
        nxt = leaves[i + 1]
        nt = nxt.get('type')
        nlow = _lower(nxt)
        if nt in ('VBZ', 'VBP') or (nt == 'VB' and _is_3sg_marked(nlow)):
            lemma = _base_of(nlow) if _is_3sg_marked(nlow) else nlow
            out.append(_finding(
                '6.1', 'error', 'C-MODAL-VERB-FORM', 'verb form', nxt['id'],
                f"The modal '{lf['surface']}' takes the bare infinitive, but "
                f"'{nxt['surface']}' is a 3rd-singular form; use '{lemma}'.",
                _wordlist_evidence(f"{low} {nlow}", [f"{low} {lemma}"],
                                   'modal + base verb')))
        elif nlow == 'to':
            n2 = _lower(leaves[i + 2]) if i + 2 < len(leaves) else '...'
            out.append(_finding(
                '6.12', 'error', 'C-MODAL-TO', 'verb form', nxt['id'],
                f"The modal '{lf['surface']}' is followed by the bare infinitive, "
                f"not 'to {n2}'.",
                _tree_evidence(nxt['id'], 'MD + to', [{'node': nxt['id']}])))
        elif nlow in MODAL_SURFACES:
            out.append(_finding(
                '6.12', 'error', 'C-MODAL-STACK', 'verb form', nxt['id'],
                f"English modals do not stack: drop one of '{lf['surface']}' / "
                f"'{nxt['surface']}'.",
                _tree_evidence(nxt['id'], 'MD + MD', [{'node': nxt['id']}])))

    # --- 2.4 existential 'there' + have/has ---------------------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] != 'there' or i + 2 >= len(leaves):
            continue
        n1, n2 = _lower(leaves[i + 1]), _lower(leaves[i + 2])
        if n1 in ('have', 'has', 'had') and n2 != 'been':
            fix = {'have': 'are', 'has': 'is', 'had': 'were'}[n1]
            out.append(_finding(
                '2.4', 'error', 'C-EXISTENTIAL-VERB', 'existential',
                leaves[i + 1]['id'],
                f"The existential construction uses 'be': 'There {fix} ...', "
                f"not 'There {n1} ...'.",
                _wordlist_evidence(f"there {n1}", [f"there {fix}"],
                                   'existential there + be')))

    # --- 2.10 / 2.11 numeral & quantifier before a singular noun ------------- #
    for i, lf in enumerate(leaves):
        low = lows[i]
        pl = lf.get('type') == 'CD' or low in PLURALIZERS
        if not pl or i + 1 >= len(leaves):
            continue
        if i > 0 and leaves[i - 1].get('type') in (
                'NN', 'NNS', 'NNP', 'NNPS', 'CD'):
            continue  # 'page five' / identifier reading
        j = i + 1
        while j < len(leaves) and leaves[j].get('type') in ('JJ', 'JJR', 'JJS'):
            j += 1
        if j >= len(leaves):
            continue
        nxt = leaves[j]
        if nxt.get('type') == 'IN':
            continue  # 'many of the ...'
        if nxt.get('type') == 'NNS':
            continue
        if nxt.get('type') == 'NN':
            rule = '2.10' if lf.get('type') == 'CD' else '2.11'
            art = ('the numeral' if lf.get('type') == 'CD' else f"'{low}'")
            out.append(_finding(
                rule, 'error', 'C-QUANT-PLURAL', 'noun number', nxt['id'],
                f"After {art} '{lf['surface']}' the noun must be plural: "
                f"'{nxt['surface']}' \u2192 '{nxt['surface']}s'.",
                _wordlist_evidence(f"{low} {_lower(nxt)}",
                                   [f"{low} {_lower(nxt)}s"],
                                   'numeral/quantifier + plural noun')))

    # --- 2.11 many/much/less with the wrong noun class ----------------------- #
    for i, lf in enumerate(leaves):
        low = lows[i]
        if i + 1 >= len(leaves):
            continue
        nxt = leaves[i + 1]
        nt, nlow = nxt.get('type'), _lower(nxt)
        if low == 'much' and nt == 'NNS':
            out.append(_finding(
                '2.11', 'error', 'C-QUANTIFIER-CLASS', 'quantifier', nxt['id'],
                f"'much' combines with mass nouns, not count plural '{nxt['surface']}'; "
                f"use 'many'.",
                _wordlist_evidence(f"much {nlow}", [f"many {nlow}"],
                                   'much (mass) vs many (count)')))
        elif low == 'many' and nt == 'NN':
            out.append(_finding(
                '2.11', 'error', 'C-QUANTIFIER-CLASS', 'quantifier', nxt['id'],
                f"'many' combines with plural count nouns, not singular "
                f"'{nxt['surface']}'; use 'much' (or a plural noun).",
                _wordlist_evidence(f"many {nlow}", [f"much {nlow}"],
                                   'many (count) vs much (mass)')))
        elif low == 'less' and nt == 'NNS':
            out.append(_finding(
                '2.11', 'error', 'C-QUANTIFIER-CLASS', 'quantifier', nxt['id'],
                f"'less' is for mass nouns; with count plural '{nxt['surface']}' "
                f"use 'fewer'.",
                _wordlist_evidence(f"less {nlow}", [f"fewer {nlow}"],
                                   'less (mass) vs fewer (count)')))

    # --- 5.1 preposition + subject-form pronoun ------------------------------ #
    for i, lf in enumerate(leaves):
        if lows[i] in TRUE_PREPS and i + 1 < len(leaves):
            nxt = _lower(leaves[i + 1]).rstrip('.,;:!?')
            if nxt in SUBJECT_PRON:
                obj = {'i': 'me', 'we': 'us', 'he': 'him', 'she': 'her',
                       'they': 'them'}[nxt]
                out.append(_finding(
                    '5.1', 'error', 'C-PREP-PRON-CASE', 'pronoun case',
                    leaves[i + 1]['id'],
                    f"The object of the preposition '{lf['surface']}' must be "
                    f"objective: '{nxt}' \u2192 '{obj}'.",
                    _tree_evidence(lf['id'],
                                   'preposition + nominative pronoun',
                                   [{'node': lf['id']},
                                    {'node': leaves[i + 1]['id']}])))

    # --- 1.10 homophones: there/their, its/it's, your/you're ------------------ #
    DT_WORDS = {'a', 'an', 'the', 'this', 'that', 'my', 'your', 'his', 'her',
                'our', 'their', 'its', 'some', 'any', 'no', 'every'}
    for i, lf in enumerate(leaves):
        low = lows[i]
        nxt = leaves[i + 1] if i + 1 < len(leaves) else None
        if nxt is None:
            continue
        nt, nlow = nxt.get('type'), _lower(nxt)
        # there vs their: 'there' + noun (right after a verb or sentence start)
        if low == 'there' and nt in ('NN', 'NNS', 'NNP', 'NNPS') \
                and nlow not in ('is', 'are', 'was', 'were'):
            prev_ok = i == 0 or (i > 0 and leaves[i - 1].get('type') in verb_tags
                                 or _lower(leaves[i - 1]) == 'to')
            if prev_ok:
                out.append(_finding(
                    '1.10', 'error', 'C-HOMOPHONE', 'spelling', lf['id'],
                    f"Possessive 'their' was spelled '{lf['surface']}': "
                    f"'{lf['surface']} {nxt['surface']}' \u2192 "
                    f"'their {nxt['surface']}'.",
                    _tree_evidence(lf['id'], 'there + NN (possessive slot)',
                                   [{'node': lf['id']}, {'node': nxt['id']}])))
        # its vs it's
        elif low == 'its' and (nlow in DT_WORDS or nt in verb_tags + ('MD',)):
            out.append(_finding(
                '1.10', 'error', 'C-HOMOPHONE', 'spelling', lf['id'],
                f"'it's' (it is) was written '{lf['surface']}': a possessive "
                f"'its' has no apostrophe and takes no following verb/article.",
                _tree_evidence(lf['id'], 'its + verb/article (it is slot)',
                               [{'node': lf['id']}])))
        # your vs you're
        elif low == 'your' and (nlow in ('a', 'an', 'the') or nt in verb_tags
                                or nlow in ('going', 'wanting')):
            out.append(_finding(
                '1.10', 'error', 'C-HOMOPHONE', 'spelling', lf['id'],
                f"'you're' (you are) was written '{lf['surface']}': the "
                f"possessive 'your' takes a noun, not a verb/article.",
                _tree_evidence(lf['id'], 'your + verb/article (you are slot)',
                               [{'node': lf['id']}])))

    # --- 2.8 indefinite pronouns take a singular verb -------------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] not in INDEF_SINGULAR or i + 1 >= len(leaves):
            continue
        nlow = _lower(leaves[i + 1])
        if nlow in ('are', 'were', 'have', 'do'):
            sg = {'are': 'is', 'were': 'was', 'have': 'has', 'do': 'does'}[nlow]
            out.append(_finding(
                '2.8', 'error', 'C-INDEF-AGREE', 'subject-verb agreement',
                leaves[i + 1]['id'],
                f"'{lf['surface']}' is always singular: use '{sg}', not "
                f"'{nlow}'.",
                _wordlist_evidence(f"{low} {nlow}", [f"{low} {sg}"],
                                   'indefinite pronoun + singular verb')))

    # --- 6.9 gerund vs to-infinitive (enjoy, finish, ...; want + -ing) -------- #
    gerund_forms = set()
    for v in GERUND_TAKERS:
        gerund_forms |= _inflected(v)
    for i, lf in enumerate(leaves):
        low = lows[i]
        if low in gerund_forms and i + 2 < len(leaves):
            nln = _lower(leaves[i + 1])
            if nln == 'to':
                n2 = _lower(leaves[i + 2])
                out.append(_finding(
                    '6.9', 'error', 'C-GERUND-INFIN', 'verb complement',
                    leaves[i + 1]['id'],
                    f"'{lf['surface']}' takes a gerund: use "
                    f"'{lf['surface']} {n2}ing' "
                    f"(not '{lf['surface']} to {n2}').",
                    _wordlist_evidence(f"{low} to {n2}",
                                       [f"{low} {n2}ing"],
                                       'gerund-taking verb')))
            elif leaves[i + 1].get('type') == 'VB':
                out.append(_finding(
                    '6.9', 'error', 'C-GERUND-INFIN', 'verb complement',
                    leaves[i + 1]['id'],
                    f"'{lf['surface']}' takes a gerund: use "
                    f"'{lf['surface']} {nln}ing' (not '{low} {nln}').",
                    _wordlist_evidence(f"{low} {nln}", [f"{low} {nln}ing"],
                                       'gerund-taking verb')))
        elif low in ('want', 'wants', 'wanted', 'wanting'):
            if leaves[i + 1].get('type') == 'VBG':
                vbg = _lower(leaves[i + 1])
                out.append(_finding(
                    '6.9', 'error', 'C-GERUND-INFIN', 'verb complement',
                    leaves[i + 1]['id'],
                    f"'want' takes a to-infinitive: "
                    f"'{low} to {_base_of(vbg)}', not "
                    f"'{low} {vbg}'.",
                    _wordlist_evidence(f"{low} {vbg}",
                                       [f"{low} to {_base_of(vbg)}"],
                                       'want + to-infinitive')))

    # --- 8.6 preposition + to-infinitive; 'look forward to' ------------------- #
    for i, lf in enumerate(leaves):
        if i + 1 >= len(leaves):
            continue
        low = lows[i]
        nln = _lower(leaves[i + 1])
        if low == 'at' and nln == 'to':
            out.append(_finding(
                '8.6', 'error', 'C-PREP-GERUND', 'verb complement',
                leaves[i + 1]['id'],
                f"After the preposition 'at' use the gerund: 'good at {'singing'}' "
                f"is 'at + -ing', not 'at to ...'.",
                _tree_evidence(lf['id'], 'preposition + to-infinitive',
                               [{'node': lf['id']},
                                {'node': leaves[i + 1]['id']}])))
        if low in ('look', 'looks', 'looked') and nln == 'forward' \
                and i + 2 < len(leaves) and _lower(leaves[i + 2]) == 'to' \
                and i + 3 < len(leaves) \
                and leaves[i + 3].get('type') in ('VB', 'VBZ'):
            nxtv = _lower(leaves[i + 3])
            out.append(_finding(
                '8.6', 'error', 'C-PREP-GERUND', 'verb complement',
                leaves[i + 3]['id'],
                f"After 'look forward to' use the gerund: "
                f"'{nxtv}ing' (not 'to {nxtv}').",
                _wordlist_evidence(f"look forward to {nxtv}",
                                   [f"look forward to {nxtv}ing"],
                                   'look forward to + gerund')))

    # --- 11.3 'since' needs (have/had) + past participle ---------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] != 'since':
            continue
        have_in = any(_lower(x) in ('have', 'has', 'had')
                      for x in leaves[max(0, i - 3):i])
        if have_in:
            continue
        present_finite = None
        for k in range(i - 1, max(-1, i - 5), -1):
            tag = leaves[k].get('type')
            if tag in ('VBZ', 'VBP') or _lower(leaves[k]) in (
                    'am', 'is', 'are', 'do', 'does'):
                present_finite = leaves[k]
                break
        if present_finite is not None:
            out.append(_finding(
                '11.3', 'error', 'C-TENSE-SINCE', 'tense',
                present_finite['id'],
                f"With 'since' a perfect tense is required: 'have/has (been) + "
                f"past participle since ...', not the present "
                f"'{present_finite['surface']}'.",
                _tree_evidence(present_finite['id'], 'present verb + since',
                               [{'node': present_finite['id']},
                                {'node': lf['id']}])))

    # --- 6.6 stative verb in the progressive ---------------------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] not in STATIVE_ING:
            continue
        for k in range(max(0, i - 2), i):
            if _lower(leaves[k]) in BE_SURFACES_LEAF:
                verb = lows[i][:-3]  # 'liking' -> 'like'
                out.append(_finding(
                    '6.6', 'error', 'C-STATIVE-PROG', 'verb form', lf['id'],
                    f"'{lf['surface']}' is a stative verb: it does not take the "
                    f"progressive. Use the simple form, e.g. '{verb}' / "
                    f"'{verb}s'.",
                    _wordlist_evidence(f"{_lower(leaves[k])} {lows[i]}",
                                       [verb, verb + 's'],
                                       'stative verb + no progressive')))
                break

    # --- 9.13 indirect question word order ------------------------------------ #
    for i, lf in enumerate(leaves):
        if lows[i] not in WH_WORDS or i == 0 or i + 2 >= len(leaves):
            continue
        if _lower(leaves[i + 1]) not in WH_AUX:
            continue
        if leaves[i + 2].get('type') in ('VB', 'VBG', 'VBN', 'MD'):
            continue  # wh-word is the subject: 'I know who is coming' (valid)
        out.append(_finding(
            '9.13', 'error', 'C-INDIRECT-WH-INVERSION', 'word order',
            leaves[i + 1]['id'],
            f"An indirect question keeps statement order: "
            f"'{leaves[i + 1]['surface']}' must follow the subject here "
            f"('... {leaves[i + 2]['surface']} {leaves[i + 1]['surface']} ...').",
            _tree_evidence(leaves[i + 1]['id'], 'wh + aux + subject (inverted)',
                           [{'node': lf['id']}, {'node': leaves[i + 1]['id']}])))

    # --- 8.1 arrive + 'to' ----------------------------------------------------- #
    ARRIVE_FORM = {'arrive', 'arrives', 'arrived', 'arriving'}
    for i, lf in enumerate(leaves):
        if lows[i] in ARRIVE_FORM and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) == 'to':
            out.append(_finding(
                '8.1', 'error', 'C-PREP-CHOICE', 'preposition', lf['id'],
                f"'arrive' takes 'at' (or 'in' for a country/city), not 'to': "
                f"'{low} to' \u2192 'arrive at'.",
                _wordlist_evidence(f"{lows[i]} to",
                                   [f"arrive at", f"arrive in"],
                                   'verb + preposition')))

    # --- 6.3 'please to' -------------------------------------------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] == 'please' and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) == 'to':
            out.append(_finding(
                '6.3', 'error', 'C-PLEASE-TO', 'verb form', lf['id'],
                f"An imperative with 'please' takes the bare verb: drop 'to' "
                f"('please {leaves[i + 2]['surface'] if i + 2 < len(leaves) else 'sit'}' "
                f"), not 'please to ...'.",
                _tree_evidence(lf['id'], 'please + to',
                               [{'node': lf['id']}, {'node': leaves[i + 1]['id']}])))

    # --- 7.4 participial adjective: -ing + 'in' -------------------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] in PARTICIPIAL_ADJ and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) == 'in':
            ed = lows[i][:-3] + 'ed' if not lows[i].endswith('ing') else \
                (lows[i][:-4] + 'ied' if lows[i][:-3].endswith('y')
                 else lows[i][:-3] + 'ed')
            out.append(_finding(
                '7.4', 'error', 'C-PARTICIPIAL-ADJ', 'adjective form', lf['id'],
                f"'{lf['surface']} in' describes a person; use the -ed form "
                f"'{ed} in' (e.g. 'interested in'), or rephrase with the "
                f"-ing adjective for the thing itself.",
                _wordlist_evidence(f"{lows[i]} in", [f"{ed} in"],
                                   'participial adjective (-ing/-ed)')))

    # --- 2.1 'we/they/you was' --------------------------------------------------- #
    for i, lf in enumerate(leaves):
        if _lower(lf) in ('we', 'they', 'you') and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) == 'was':
            out.append(_finding(
                '2.1', 'error', 'C-WAS-WERE', 'subject-verb agreement',
                leaves[i + 1]['id'],
                f"'{lf['surface']}' takes 'were', not 'was'.",
                _wordlist_evidence(f"{lows[i]} was", [f"{lows[i]} were"],
                                   'was/were agreement')))

    # --- 1.6 bare VBN as simple past ('I seen him') ----------------------------- #
    # Both VBN tokens and VBN-only surfaces the parser retags VBD.
    VBN_ONLY = {'seen', 'done', 'gone', 'eaten', 'beaten', 'given', 'taken',
                'written', 'broken', 'known', 'thrown', 'driven', 'grown',
                'chosen', 'spoken', 'woken', 'fallen', 'blown', 'forgotten',
                'bitten', 'hidden'}
    for i, lf in enumerate(leaves):
        tag = lf.get('type')
        is_participle = tag == 'VBN' or (tag == 'VBD' and lows[i] in VBN_ONLY)
        if is_participle and i > 0 \
                and leaves[i - 1].get('type') == 'PRP' \
                and _lower(leaves[i - 1]) in SUBJ_PRON_BARE:
            try:
                from licensing import _lemmas
                base = sorted(_lemmas(lows[i], 'VERB'))[0] if _lemmas(
                    lows[i], 'VERB') else lows[i]
            except Exception:  # pragma: no cover
                base = lows[i]
            out.append(_finding(
                '1.6', 'error', 'C-VBN-SIMPLE-PAST', 'verb form', lf['id'],
                f"'{lf['surface']}' is a past participle, not a simple-past "
                f"form. After the subject pronoun '{leaves[i - 1]['surface']}' "
                f"use the simple-past form of '{base}' (or a perfect with "
                f"'have {lows[i]}').",
                _wordlist_evidence(f"{_lower(leaves[i - 1])} {lows[i]}",
                                   [f"{base} (simple past)",
                                    f"have {lows[i]}"],
                                   'bare past participle')))

    # --- 1.9 reflexive / 7.1 nonstandard-adverb forms -------------------------- #
    for i, lf in enumerate(leaves):
        low = lows[i]
        if low in REFLEXIVE_FIX:
            out.append(_finding(
                '1.9', 'error', 'C-REFLEXIVE-FORM', 'reflexive pronoun',
                lf['id'],
                f"'{lf['surface']}' \u2192 '{REFLEXIVE_FIX[low]}'.",
                _wordlist_evidence(lf['surface'], [REFLEXIVE_FIX[low]],
                                   'reflexive forms')))
        elif lf.get('type') in ('RB', 'RBR', 'RBS') and low in NONSTANDARD_ADV:
            fix = 'fast' if low == 'fastly' else (low[:-2] if low.endswith('ly')
                                                  else low + 'ly')
            out.append(_finding(
                '7.1', 'error', 'C-ADJ-ADV', 'adverb form', lf['id'],
                f"'{lf['surface']}' is not a standard adverb; use "
                f"'{fix}'.",
                _wordlist_evidence(lf['surface'], [fix],
                                   'standard adverb forms')))

    return out


# --------------------------------------------------------------------------- #
# C-layer checks (context/meaning) -- always suggestions                       #
# --------------------------------------------------------------------------- #
def _check_context(root, clauses, leaves):
    out = []
    lows = [_lower(lf) for lf in leaves]

    # 2.5 Collective noun + plural verb
    for i, lf in enumerate(leaves):
        if _lower(lf) in COLLECTIVE_NOUNS:
            for nxt in leaves[i + 1:]:
                if nxt.get('type') in FINITE_TYPES or _lower(nxt) in BE_SURFACES:
                    if _verb_key(nxt) == ('*', 'non3sg'):
                        out.append(_finding('2.5', 'suggestion', 'C-COLLECTIVE',
                                            'notional agreement', lf['id'],
                                            f"'{lf['surface']}' can take a singular verb in "
                                            f"American English; 'is' may read better than "
                                            f"'{nxt['surface']}'.",
                                            _context_evidence(
                                                f"collective noun '{lf['surface']}' + plural verb",
                                                [{'option': 'singular verb',
                                                  'evidence': 'US usage prefers the team is'},
                                                 {'option': 'plural verb',
                                                  'evidence': 'UK usage allows the team are'}],
                                                0.6)))
                    break

    # 2.12 Pronoun-antecedent (plural antecedent, singular gendered pronoun)
    plural_antecedent = None
    for i, lf in enumerate(leaves):
        if lf.get('type') == 'NNS' and plural_antecedent is None:
            plural_antecedent = lf
        elif plural_antecedent is not None and _lower(lf) in (
                'he', 'she', 'him', 'his', 'her') and lf.get('type') in (
                'PRP', 'PRP$'):
            out.append(_finding('2.12', 'suggestion', 'C-PRON-ANTECEDENT',
                                'reference', lf['id'],
                                f"'{lf['surface']}' is singular but the nearest "
                                f"antecedent '{plural_antecedent['surface']}' is plural; "
                                f"check agreement.",
                                _context_evidence(
                                    f"plural NP '{plural_antecedent['surface']}' + "
                                    f"'{lf['surface']}'",
                                    [{'option': 'their/theirs',
                                      'evidence': 'agrees with the plural antecedent'},
                                     {'option': 'he/she',
                                      'evidence': 'only if a singular antecedent is intended'}],
                                    0.5)))
            break

    # 3.3 Unnecessary article (play the + sport)
    for i, lf in enumerate(leaves):
        if _lower(lf) in ('play', 'plays', 'played', 'playing') and i + 2 < len(leaves):
            if _lower(leaves[i + 1]) in ('the', 'a', 'an') \
                    and _lower(leaves[i + 2]) in SPORTS:
                out.append(_finding('3.3', 'suggestion', 'C-UNNECESSARY-ARTICLE',
                                    'articles', leaves[i + 1]['id'],
                                    f"No article is needed before the game name: "
                                    f"'play {leaves[i + 2]['surface']}'.",
                                    _context_evidence(
                                        f"play + '{leaves[i + 1]['surface']}' + sport",
                                        [{'option': f"play {leaves[i + 2]['surface']}",
                                          'evidence': 'games take no article'},
                                         {'option': f"play the {leaves[i + 2]['surface']}",
                                          'evidence': 'only if a specific one is meant'}],
                                        0.6)))

    # 6.17 Subjunctive / wish
    for i, lf in enumerate(leaves):
        if _lower(lf) == 'wish' and i + 2 < len(leaves):
            if _lower(leaves[i + 1]) in ('i', 'he', 'she', 'it') \
                    and _lower(leaves[i + 2]) == 'was':
                out.append(_finding('6.17', 'suggestion', 'C-SUBJUNCTIVE', 'mood',
                                    leaves[i + 2]['id'],
                                    f"After 'wish', use 'were', not 'was'.",
                                    _context_evidence('wish + was',
                                                      [{'option': 'were',
                                                        'evidence': 'irrealis/subjunctive'},
                                                       {'option': 'was',
                                                        'evidence': 'indicative, less standard here'}],
                                                      0.7)))

    # 11.3 Tense-time agreement
    past_time = {'yesterday', 'ago'}
    present_time = {'tomorrow'}
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        if low in past_time:
            for nxt in leaves:
                if nxt.get('type') in ('VBP', 'VBZ'):
                    out.append(_finding('11.3', 'suggestion', 'C-TENSE-TIME',
                                        'tense', nxt['id'],
                                        f"'{low}' refers to past time, but '{nxt['surface']}' "
                                        f"is present tense.",
                                        _context_evidence(
                                            f"past-time adverb '{low}' + present '{nxt['surface']}'",
                                            [{'option': 'past tense',
                                              'evidence': 'matches the past-time adverb'},
                                             {'option': 'present tense',
                                              'evidence': 'only for timeless statements'}],
                                            0.6)))
                    break
        if low in present_time:
            for nxt in leaves:
                if nxt.get('type') == 'VBD':
                    out.append(_finding('11.3', 'suggestion', 'C-TENSE-TIME',
                                        'tense', nxt['id'],
                                        f"'{low}' refers to future time, but "
                                        f"'{nxt['surface']}' is past tense.",
                                        _context_evidence(
                                            f"future-time adverb '{low}' + past '{nxt['surface']}'",
                                            [{'option': 'future form',
                                              'evidence': 'matches the future-time adverb'},
                                             {'option': 'past tense',
                                              'evidence': 'only for reported past'}],
                                            0.6)))
                    break

    # 11.8 Connector misuse (comma + however joining two clauses)
    surface = root.get('surface') or ''
    if ', however' in surface.lower() and ';' not in surface:
        out.append(_finding('11.8', 'suggestion', 'C-CONNECTOR', 'connector',
                            root['id'],
                            "'however' is a conjunctive adverb; link the clauses with a "
                            "semicolon or a full stop, not just a comma.",
                            _context_evidence(
                                "comma + however across two clauses",
                                [{'option': '; however,',
                                  'evidence': 'two independent clauses need a semicolon'},
                                 {'option': '. However,',
                                  'evidence': 'or start a new sentence'}],
                                0.65)))

    # 7.4 Participial adjective (I am boring)
    for i, lf in enumerate(leaves):
        if _lower(lf) in BE_SURFACES and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) in PARTICIPIAL_ADJ:
            # Only fire if the subject is an experiencer pronoun (I/he/she/we/they/you)
            # otherwise it's a correct attributive/causative use
            subj = None
            # find subject of the clause this BE belongs to
            for clause in clauses:
                if i < len(leaves):  # rough; easier: check clause has be
                    c_leaves = _leaves(clause)
                    if lf in c_leaves:  # has be
                        for c in clause.get('children', []):
                            if c.get('type') in ('NP',):
                                subj = c
                                break
                        break
            subj_exp = False
            if subj is not None:
                sh = _leaves(subj)
                if sh:
                    ssubj = _lower(sh[-1]) if sh[-1].get('type') == 'PRP' or sh[-1].get('type') in ('PRP$','NN','NNS') else _lower(sh[0])
                    if sh[-1].get('type') == 'PRP':
                        ssubj = _lower(sh[-1])
                    # experiencer first/third person pronouns
                    if _lower(sh[-1]) in ('i','he','she','we','they','you'):
                        subj_exp = True
            if not subj_exp:
                continue  # correct for inanimate/third-party subjects
            out.append(_finding('7.4', 'suggestion', 'C-PARTICIPIAL',
                                'adjective', leaves[i + 1]['id'],
                                f"'{leaves[i + 1]['surface']}' describes the effect on "
                                f"others; for your own feeling use "
                                f"'{leaves[i + 1]['surface'][:-3]}ed'.",
                                _context_evidence(
                                    f"be + '{leaves[i + 1]['surface']}'",
                                    [{'option': leaves[i + 1]['surface'][:-3] + 'ed',
                                      'evidence': 'describes the experiencer'},
                                     {'option': leaves[i + 1]['surface'],
                                      'evidence': 'describes the cause'}],
                                    0.55)))

    # 6.7 Tense consistency (He said he will come)
    seen_past = any(lf.get('type') == 'VBD' or _lower(lf) == 'said' for lf in leaves)
    if seen_past:
        for i, lf in enumerate(leaves):
            if _lower(lf) in ('will', 'shall') and any(
                    x.get('type') == 'VBD' for x in leaves[:i]):
                out.append(_finding('6.7', 'suggestion', 'C-TENSE-CONSISTENCY',
                                    'tense', lf['id'],
                                    'A past reporting verb usually takes a past/non-future '
                                    "form (backshift to 'would').",
                                    _context_evidence(
                                        'past verb + will',
                                        [{'option': 'would',
                                          'evidence': 'backshift after a past verb'},
                                         {'option': 'will',
                                          'evidence': 'if the fact still holds'}],
                                        0.6)))
                break

    # 10.7 Hyphenation (well known)
    for i, lf in enumerate(leaves):
        if _lower(lf) in HYPHEN_BEFORE_ADJ and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') in ('JJ', 'VBN', 'VBG') \
                and _lower(lf) in ('well',):
            out.append(_finding('10.7', 'suggestion', 'C-HYPHEN', 'hyphenation',
                                lf['id'],
                                f"Compound modifiers before a noun are often hyphenated: "
                                f"'{lf['surface']}-{leaves[i + 1]['surface']}'.",
                                _context_evidence(
                                    f"'{lf['surface']}' + adjective",
                                    [{'option': f"{lf['surface']}-{leaves[i + 1]['surface']}",
                                      'evidence': 'compound modifier (hyphenated)'},
                                     {'option': f"{lf['surface']} {leaves[i + 1]['surface']}",
                                      'evidence': 'predicate position (no hyphen)'}],
                                    0.55)))

    # 11.1 Confusable words (effect/loose as verbs)
    for i, lf in enumerate(leaves):
        low = _lower(lf)
        if low in CONFUSABLE_VERB and i >= 1 and _lower(leaves[i - 1]) in (
                {'to', 'will', 'would', 'can', 'could', 'may', 'might', 'must'}
                | TO_BE_SURFACES):
            out.append(_finding('11.1', 'suggestion', 'C-CONFUSABLE', 'word choice',
                                lf['id'],
                                f"'{lf['surface']}' may be the wrong confusable; "
                                f"the verb is '{CONFUSABLE_VERB[low]}'.",
                                _context_evidence(
                                    f"verb context for '{low}'",
                                    [{'option': CONFUSABLE_VERB[low],
                                      'evidence': 'verb sense'},
                                     {'option': low,
                                      'evidence': 'noun/adjective sense'}],
                                    0.55)))

    # 11.2 Collocations (do a decision)
    words = [_lower(x) for x in leaves]
    joined = ' '.join(words)
    for phrase, fix in COLLOCATION_FIX.items():
        if phrase in joined:
            out.append(_finding('11.2', 'suggestion', 'C-COLLOCATION',
                                'collocation', root['id'],
                                f"Unnatural collocation '{phrase}'; use '{fix}'.",
                                _context_evidence(
                                    f"verb-noun collocation '{phrase}'",
                                    [{'option': fix, 'evidence': 'standard collocation'},
                                     {'option': phrase, 'evidence': 'non-standard'}],
                                    0.6)))

    # 11.4 Selectional restrictions (The book eats)
    for clause in clauses:
        subj = next((c for c in clause.get('children', []) if c.get('type') == 'NP'),
                    None)
        if subj is None:
            continue
        head = _np_head_leaf(subj)
        if head is None or _lower(head) not in INANIMATE_SUBJECTS:
            continue
        for lf in _leaves(clause):
            vlow = _lower(lf)
            vstem = vlow[:-2] if vlow.endswith('ed') else (
                vlow[:-3] + 'e' if vlow.endswith('ing') else (
                    vlow[:-1] if vlow.endswith('s') else vlow))
            if vlow in HUMAN_ONLY_VERBS or vstem in HUMAN_ONLY_VERBS:
                out.append(_finding('11.4', 'suggestion', 'C-SELECTIONAL',
                                    'selectional', lf['id'],
                                    f"'{head['surface']}' cannot perform the human "
                                    f"action '{lf['surface']}'.",
                                    _context_evidence(
                                        f"inanimate subject '{head['surface']}' + "
                                        f"'{lf['surface']}'",
                                        [{'option': 'animate subject',
                                          'evidence': 'required by the verb'},
                                         {'option': 'different verb',
                                          'evidence': 'fits an inanimate subject'}],
                                        0.6)))
                break

    # 11.6 Register (informal words)
    for lf in leaves:
        low = _lower(lf)
        if low in INFORMAL_WORDS:
            out.append(_finding('11.6', 'suggestion', 'C-REGISTER', 'register',
                                lf['id'],
                                f"'{lf['surface']}' is informal; prefer a formal "
                                'equivalent in academic writing.',
                                _context_evidence(
                                    'informal vocabulary',
                                    [{'option': 'formal synonym',
                                      'evidence': 'matches an academic register'},
                                     {'option': lf['surface'],
                                      'evidence': 'informal register'}],
                                    0.6)))

    # 11.7 L1 interference (I am agree)
    for i, lf in enumerate(leaves):
        if _lower(lf) in TO_BE_SURFACES and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) in ('agree', 'disagree'):
            out.append(_finding('11.7', 'suggestion', 'C-L1-INTERFERENCE',
                                'L1 interference', leaves[i + 1]['id'],
                                f"'{leaves[i + 1]['surface']}' is a verb, not an "
                                "adjective: use 'I agree', not 'I am agree'.",
                                _context_evidence(
                                    "be + verb",
                                    [{'option': 'I agree',
                                      'evidence': 'agree is lexical verb'},
                                     {'option': 'I am agree',
                                      'evidence': 'L1 transfer pattern'}],
                                    0.65)))

    # 5.3 ambiguous pronoun reference (Tom told Jim he...)
    nnp_idx = [i for i, lf in enumerate(leaves)
               if lf.get('type') == 'NNP' and _lower(lf) != 'i']
    if len(nnp_idx) >= 2:
        second = nnp_idx[1]
        for i in range(second + 1, len(leaves)):
            lf = leaves[i]
            if lf.get('type') == 'PRP' and _lower(lf) in (
                    'he', 'she', 'they', 'him', 'her', 'them', 'it'):
                out.append(_finding('5.3', 'suggestion', 'C-PRON-AMBIG',
                                    'reference', lf['id'],
                                    f"'{lf['surface']}' could refer to more than one "
                                    'of the people just mentioned; make the reference '
                                    'explicit.',
                                    _context_evidence(
                                        f"pronoun '{lf['surface']}' + multiple names",
                                        [{'option': 'name the referent',
                                          'evidence': 'two antecedents are available'},
                                         {'option': 'rephrase',
                                          'evidence': 'removes the ambiguity'}],
                                        0.5)))
                break

    # 8.1 Wrong preposition after a verb (She depends in her family)
    VERB_PREPS = {'depend': ['on', 'upon'],
                  'depends': ['on', 'upon'],
                  'depended': ['on', 'upon'],
                  'consist': ['of'],
                  'consists': ['of'],
                  'consisted': ['of'],
                  'belong': ['to'],
                  'belongs': ['to'],
                  'belonged': ['to'],
                  'listen': ['to'],
                  'listens': ['to'],
                  'listened': ['to'],
                  'rely': ['on', 'upon'],
                  'relies': ['on', 'upon'],
                  'replied': ['to'],
                  'marry': ['to'],
                  'marries': ['to'],
                  'married': ['to'],
                  'wait': ['for'],
                  'waits': ['for'],
                  'waited': ['for']}
    for i, lf in enumerate(leaves[:-1]):
        opts = VERB_PREPS.get(_lower(lf))
        if opts is None:
            continue
        nxt = leaves[i + 1]
        if nxt.get('type') not in ('IN', 'TO') or _lower(nxt) in opts:
            continue
        out.append(_finding('8.1', 'suggestion', 'C-WRONG-PREPOSITION',
                            'preposition choice', nxt['id'],
                            f"'{lf['surface']}' takes "
                            f"{'one of' if len(opts) > 1 else ''} "
                            f"'{'/'.join(opts)}', "
                            f"not '{nxt['surface']}'.",
                            _context_evidence(
                                f"verb '{lf['surface']}' + '{nxt['surface']}'",
                                [{'option': f"{lf['surface']} "
                                            f"{'/'.join(opts)}",
                                  'evidence': 'standard collocation'},
                                 {'option': f"{lf['surface']} {nxt['surface']}",
                                  'evidence': 'non-standard collocation'}],
                                0.7)))

    # 11.5 PP-attachment ambiguity (I saw the man with the telescope)
    PERCEPTION = {'saw', 'see', 'seen', 'heard', 'hear', 'watched', 'watch',
                  'noticed', 'notice', 'felt', 'feel', 'found', 'find'}
    for clause in clauses:
        vp = None
        for c in clause.get('children', []):
            if c.get('type') == 'VP':
                vp = c
                break
        if vp is None:
            continue
        vl = _leaves(vp)
        if not vl or _lower(vl[0]) not in PERCEPTION:
            continue
        ch = vp.get('children', [])
        for a, b in zip(ch, ch[1:]):
            if a.get('type') == 'NP' and b.get('type') == 'PP':
                bface = _leaves(b)
                if bface and _lower(bface[0]) in ('with', 'from', 'for', 'on', 'in'):
                    out.append(_finding('11.5', 'suggestion', 'C-PP-ATTACH',
                                        'ambiguity', bface[0]['id'],
                                        f"The phrase '{b['surface']}' could modify either "
                                        f"'{vl[0]['surface']}' or '{a['surface']}'.",
                                        _context_evidence(
                                            f"'{b['surface']}' after verb + object NP",
                                            [{'option': 'attach to the verb',
                                              'evidence': 'describes the action'},
                                             {'option': 'attach to the object',
                                              'evidence': 'describes the noun'}],
                                            0.5)))
                    break

    # 3.4 definite article likely first mention (I saw the dog)
    SIGHT = {'saw', 'see', 'seen', 'met', 'meet', 'found', 'find', 'bought',
             'buy', 'made', 'make', 'wrote', 'write'}
    for clause in clauses:
        vp = None
        for c in clause.get('children', []):
            if c.get('type') == 'VP':
                vp = c
                break
        if vp is None:
            continue
        vl = _leaves(vp)
        if not vl or _lower(vl[0]) not in SIGHT:
            continue
        for c in vp.get('children', []):
            if c.get('type') != 'NP':
                continue
            nl = _leaves(c)
            if len(nl) >= 2 and _lower(nl[0]) == 'the' and nl[-1].get('type') == 'NN':
                # skip if anaphoric cues present (again, same, before, also, other)
                textlow = (root.get('surface') or '').lower()
                if any(w in textlow for w in (' again', ' the same', ' before', ' also', ' another', ' other', ' earlier', ' last time')):
                    continue
                out.append(_finding('3.4', 'suggestion', 'C-FIRST-MENTION',
                                    'article', nl[0]['id'],
                                    f"If '{c['surface']}' is mentioned for the first "
                                    f"time, 'a/an' usually fits better than 'the'.",
                                    _context_evidence(
                                        f"definite NP '{c['surface']}' with a first-mention verb",
                                        [{'option': 'a/an',
                                          'evidence': 'introduces a new referent'},
                                         {'option': 'the',
                                          'evidence': 'refers to a known referent'}],
                                        0.5)))
                break

    return out


def collect(text, root):
    """Return all rule findings for a parsed sentence as a list of dicts."""
    leaves = _leaves(root)
    clauses = _clauses(root)
    findings = []
    findings.extend(_check_wordlists(leaves))
    findings.extend(_check_adjective_adverb(leaves))
    findings.extend(_check_tree(root, clauses, leaves, text))
    findings.extend(_check_more(root, clauses, leaves))
    findings.extend(_check_context(root, clauses, leaves))
    return findings
