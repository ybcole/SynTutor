"""SynTutor rule matrix (docs/matrix.md) expressed as deterministic checks.

This module is the machine-readable twin of ``docs/matrix.md``. Every rule in
that document is registered here with its check method:

    T  tree rule            -- deterministic over the parsed constituency tree
    L  word list/morphology -- deterministic lookup against a curated list
    C  context/meaning      -- normally reported as a suggestion; only a
                               high-confidence contradiction is an error

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

# Perfect-auxiliary heads that license the past-participle checks below. A
# plain past-tense verb elsewhere in a sentence is never forced to a
# participle, and a correctly-formed same-shape participle ("have been") is
# not reported.
HAVE_FORM = {'have', 'has', 'had', 'having'}

PAST_PARTICIPLE_OF = {
    'went': 'gone', 'ate': 'eaten', 'drank': 'drunk', 'ran': 'run',
    'took': 'taken', 'bought': 'bought', 'brought': 'brought',
    'taught': 'taught', 'thought': 'thought', 'wrote': 'written',
    'knew': 'known', 'caught': 'caught', 'chose': 'chosen', 'spoke': 'spoken',
    'gave': 'given', 'made': 'made', 'found': 'found', 'saw': 'seen',
    'came': 'come', 'did': 'done', 'got': 'got', 'said': 'said',
    'sold': 'sold', 'sent': 'sent', 'sang': 'sung', 'sat': 'sat',
    'slept': 'slept', 'stood': 'stood', 'stole': 'stolen', 'swam': 'swum',
    'threw': 'thrown', 'wore': 'worn', 'won': 'won',
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

# Words that can follow the verbs above without being their object, so the
# "missing preposition" rule must not fire on them (arrived home / yesterday).
BARE_OBJECTS = {
    'yesterday', 'today', 'tomorrow', 'tonight', 'now', 'later', 'soon',
    'early', 'late', 'home', 'here', 'there', 'back', 'ahead', 'abroad',
}

# '-ing' words that are not gerunds, so parallelism/gerund rules skip them.
ING_NONVERBS = {
    'during', 'morning', 'evening', 'thing', 'nothing', 'something',
    'anything', 'everything', 'spring', 'string', 'king', 'ring', 'bring',
    'sing', 'sting', 'swing', 'wing', 'cling', 'fling', 'sling', 'wring',
    'ceiling', 'evening', 'darling', 'underling', 'sibling', 'offing',
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
                 'as', 'whether', 'whenever', 'wherever', 'once'}

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
HUMAN_ONLY_PARTICIPLES = {'eating', 'drinking', 'sleeping', 'dreaming',
                          'swallowing', 'smiling', 'laughing', 'walking',
                          'running', 'thinking', 'feeling', 'sitting'}
INANIMATE_SUBJECTS = {'book', 'table', 'chair', 'house', 'car', 'stone',
                      'weather', 'rain', 'idea', 'plan', 'sky', 'phone', 'bus'}
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


def _quoted_indices(leaves):
    """Indices of leaves that sit between a pair of straight double quotes."""
    quoted = set()
    inside = False
    for i, lf in enumerate(leaves):
        if (lf.get('surface') or '') == '"':
            inside = not inside
            continue
        if inside:
            quoted.add(i)
    return quoted


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
                                f"The word '{observed}' is a contraction but is "
                                f"missing its apostrophe; write it as '{fix}'.",
                                _wordlist_evidence(observed, [fix],
                                                   'contraction table'),
                                _rem(f"'{observed}' is a contraction missing its apostrophe.",
                                     f"Add the apostrophe: '{observed}' \u2192 '{fix}'.",
                                     None, "The word is written as '{fix}'")))

        if low in REFLEXIVE_FIX:
            fix = REFLEXIVE_FIX[low]
            out.append(_finding('1.9', 'error', 'C-REFLEXIVE-FORM', 'reflexive',
                                lf['id'],
                                f"The word '{lf['surface']}' is not a standard "
                                f"reflexive pronoun; use '{fix}' instead.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'reflexive table'),
                                _rem(f"'{lf['surface']}' is not a standard reflexive pronoun.",
                                     f"Use '{fix}' instead of '{lf['surface']}'.",
                                     None, 'Standard reflexive pronoun')))

        if low in ADVERB_FIX:
            fix = ADVERB_FIX[low]
            out.append(_finding('1.8', 'error', 'C-ADVERB-FORM', 'adverb form',
                                lf['id'],
                                f"'{lf['surface']}' is not a correct adverb form; use "
                                f"'{fix}' instead.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'adverb-formation table'),
                                _rem(f"'{lf['surface']}' is not a correct adverb form.",
                                     f"Write '{fix}' instead of '{lf['surface']}'.")))

        if low in SPELLING_FIX:
            fix = SPELLING_FIX[low]
            out.append(_finding('1.12', 'error', 'C-SPELLING', 'spelling',
                                lf['id'],
                                f"'{lf['surface']}' is misspelled; write it as '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'spelling table'),
                                _rem(f"'{lf['surface']}' is misspelled.",
                                     f"Correct the spelling to '{fix}'.")))

        if low in VERB_ENDING_FIX:
            fix = VERB_ENDING_FIX[low]
            out.append(_finding('1.4', 'error', 'C-VERB-ENDING', 'verb ending',
                                lf['id'],
                                f"'{lf['surface']}' is a misspelled verb form; "
                                f"write it as '{fix}'.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'verb-ending table'),
                                _rem(f"'{lf['surface']}' is a misspelled verb form.",
                                     f"Write '{fix}' instead of '{lf['surface']}'.")))

        if low in UNCOUNTABLE_PLURAL:
            out.append(_finding('4.1', 'error', 'C-UNCOUNTABLE', 'noun number',
                                lf['id'],
                                f"'{lf['surface']}' is an uncountable noun, so in this "
                                f"sentence it has no plural form; use the singular "
                                f"'{low.rstrip('s')}'.",
                                _wordlist_evidence(lf['surface'], [low.rstrip('s')],
                                                   'uncountable-noun list')))

        if low in IRREGULAR_COMPARATIVE:
            fix = IRREGULAR_COMPARATIVE[low]
            out.append(_finding('1.7', 'error', 'C-COMPARATIVE-FORM',
                                'comparative form', lf['id'],
                                f"'{lf['surface']}' is not the correct comparative form; "
                                f"use '{fix}' instead.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'irregular-comparative table')))

        if lf.get('type') == 'VBD' and low in ORAL_PAST_REGULARIZED:
            fix = ORAL_PAST_REGULARIZED[low]
            out.append(_finding('1.5', 'error', 'C-VERB-FORM', 'verb form',
                                lf['id'],
                                f"'{lf['surface']}' is not the correct past-tense form; "
                                f"use '{fix}' instead.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'irregular-past table')))

        if prev is not None and _lower(prev) in HAVE_FORM \
                and lf.get('type') == 'VBD' and low in PAST_AS_PARTICIPLE:
            part = PAST_PARTICIPLE_OF.get(low, low)
            out.append(_finding('1.6', 'error', 'C-VERB-FORM', 'verb form',
                                lf['id'],
                                f"This sentence needs the past participle of the verb, "
                                f"but '{lf['surface']}' is the past-tense form; "
                                f"use '{part}' instead.",
                                _wordlist_evidence(lf['surface'],
                                                   [part],
                                                   'participle table')))

        if prev is not None and _lower(prev) in HAVE_FORM \
                and lf.get('type') == 'VBN' and low in IRREGULAR_PART_REGULARIZED:
            fix = IRREGULAR_PART_REGULARIZED[low]
            out.append(_finding('1.6', 'error', 'C-VERB-FORM', 'verb form',
                                lf['id'],
                                f"After the word 'have', '{lf['surface']}' is not the "
                                f"correct participle form; use '{fix}' instead.",
                                _wordlist_evidence(lf['surface'], [fix],
                                                   'participle table')))

        if low in UNCOUNTABLE_SINGULAR and prev is not None \
                and _lower(prev) in ('a', 'an'):
            out.append(_finding('4.1', 'error', 'C-UNCOUNTABLE', 'articles',
                                lf['id'],
                                f"The word '{lf['surface']}' is uncountable and cannot "
                                f"follow the article '{prev['surface']}'; remove "
                                f"'{prev['surface']}' in this sentence.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [lf['surface']],
                                                   'uncountable-noun list')))

        if low in PLURAL_ONLY and prev is not None and _lower(prev) in ('a', 'an'):
            out.append(_finding('4.3', 'error', 'C-PLURAL-ONLY', 'noun number',
                                lf['id'],
                                f"The word '{lf['surface']}' is only used as a plural and "
                                f"cannot follow '{prev['surface']}' in this sentence; "
                                f"say 'a pair of {lf['surface']}' instead.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [f"pair of {lf['surface']}"],
                                                   'plural-only noun list')))

        if low == 'news' and nxt is not None and _lower(nxt) in (
                'are', 'were', 'have', 'do'):
            out.append(_finding('4.3', 'error', 'C-PLURAL-ONLY', 'noun number',
                                lf['id'],
                                f"The word 'news' is singular even though it ends in 's', "
                                f"so in this sentence it does not go with the verb "
                                f"'{nxt['surface']}'.",
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
                                f"After a number the scale word '{lf['surface']}' in this "
                                f"sentence stays singular: write "
                                f"'{prev['surface']} {low[:-1]}' instead of "
                                f"'{prev['surface']} {lf['surface']}'.",
                                _wordlist_evidence(lf['surface'], [low[:-1]],
                                                   'numeral-scale rule')))

        # Redundancy
        if prev is not None and (_lower(prev), low) in REDUNDANT_BIGRAMS:
            out.append(_finding('9.12', 'error', 'C-REDUNDANCY', 'redundancy',
                                lf['id'],
                                f"The words '{prev['surface']}' and '{lf['surface']}' in "
                                f"this sentence express the same idea twice; keep "
                                f"only one.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [prev['surface']],
                                                   'redundancy table')))

        # Adjective + preposition
        if low in ADJ_PREP_FIX and nxt is not None \
                and _lower(nxt) in ADJ_PREP_FIX[low]:
            correct = ADJ_PREP_FIX[low][_lower(nxt)]
            out.append(_finding('8.4', 'error', 'C-ADJ-PREP', 'preposition',
                                nxt['id'],
                                f"'{low}' takes the preposition '{correct}', not "
                                f"'{nxt['surface']}'; write '{low} {correct}', not "
                                f"'{low} {nxt['surface']}'.",
                                _wordlist_evidence(nxt['surface'], [correct],
                                                   'adjective+preposition table')))

        # Extra (unnecessary) preposition
        if prev is not None and (_lower(prev), low) in EXTRA_PREP:
            out.append(_finding('8.3', 'error', 'C-EXTRA-PREP', 'preposition',
                                lf['id'],
                                f"The preposition '{lf['surface']}' is unnecessary after "
                                f"'{prev['surface']}'; remove '{lf['surface']}'.",
                                _wordlist_evidence(f"{prev['surface']} {lf['surface']}",
                                                   [prev['surface']],
                                                   'verb-preposition table')))

        # Missing preposition (listen music -> listen to music)
        if low in NEEDS_PREP and nxt is not None \
                and nxt.get('type') in {'NN', 'NNS', 'NNP', 'NNPS', 'PRP'} \
                and _lower(nxt) not in BARE_OBJECTS:
            prep = NEEDS_PREP[low]
            out.append(_finding('8.2', 'error', 'C-MISSING-PREP', 'preposition',
                                lf['id'],
                                f"'{low}' needs the preposition '{prep}' before the word "
                                f"'{nxt['surface']}': write '{low} {prep} {nxt['surface']}' "
                                f"in this sentence.",
                                _wordlist_evidence(low, [f"{low} {prep}"],
                                                   'verb-preposition table')))

        # Homophones
        if low in ('its', 'it\u2019s') and nxt is not None \
                and (nxt.get('type') == 'VBG' or _lower(nxt) in HOMOPHONE_ITS_VERBS):
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"The word '{lf['surface']}' in this sentence means "
                                f"'it is', so write 'it\u2019s' before "
                                f"'{nxt['surface']}'.",
                                _wordlist_evidence(lf['surface'], ["it's"],
                                                   'homophone table')))
        if low == 'their' and nxt is not None and _lower(nxt) in BE_SURFACES:
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"Before the verb '{nxt['surface']}', the word "
                                f"'{lf['surface']}' should be spelled 'there': "
                                f"write 'there {nxt['surface']}'.",
                                _wordlist_evidence(f"{lf['surface']} {nxt['surface']}",
                                                   [f"there {nxt['surface']}"],
                                                   'homophone table')))
        if low == 'your' and nxt is not None and _lower(nxt) == 'welcome':
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"The phrase 'your welcome' in this sentence should be "
                                f"spelled 'you're welcome'.",
                                _wordlist_evidence('your welcome', ["you're welcome"],
                                                   'homophone table')))
        if low == 'then' and prev is not None and _lower(prev) in ('more', 'less',
                                                                   'rather', 'other'):
            out.append(_finding('1.10', 'error', 'C-HOMOPHONE', 'homophone',
                                lf['id'],
                                f"The word 'then' after '{prev['surface']}' is a "
                                f"comparison; write '{prev['surface']} than' in this "
                                f"sentence.",
                                _wordlist_evidence(f"{prev['surface']} then",
                                                   [f"{prev['surface']} than"],
                                                   'homophone table')))

        # some in a negative clause (3.7)
        if low == 'some' and nxt is not None and nxt.get('type') in (
                'NN', 'NNS', 'JJ'):
            if any(_lower(x) in NEGATIONS for x in leaves):
                out.append(_finding('3.7', 'error', 'C-SOME-ANY', 'determiner',
                                    lf['id'],
f"This sentence is negative, so use 'any' instead of "
                                f"'{lf['surface']}'.",
                                    _tree_evidence(lf['id'], 'negative + some'),
                                    _rem(f"'{lf['surface']}' is used in a negative sentence.",
                                         f"Change '{lf['surface']}' to 'any'.")))
    return out


# --------------------------------------------------------------------------- #
# T-layer checks (tree structure)                                             #
# --------------------------------------------------------------------------- #
def _check_tree(root, clauses, leaves, text=None, quoted=None):
    out = []
    # Clause-level structural rules (missing subject/copula, double subject,
    # question formation) apply to matrix clauses only -- relative, small and
    # infinitival clauses legitimately have no overt subject.
    top_ids = {root['id']}
    for c in root.get('children', []):
        if c.get('type') in {'S', 'SQ', 'SINV', 'SBARQ'}:
            top_ids.add(c['id'])

    # Own leaves of each clause (its subtree minus any nested clause), so a
    # rule looking for a clause's subject never reaches into a deeper clause
    # (e.g. 'I think that she prepared herself' must bind 'herself' to 'she').
    _clause_lvs = {}
    _clause_sizes = {}
    for _cl in clauses:
        _lv = _leaves(_cl)
        _clause_lvs[_cl['id']] = _lv
        _clause_sizes[_cl['id']] = len(_lv)
    _leaf_owner = {}
    for _cl in clauses:
        _cid = _cl['id']
        for _lf in _clause_lvs[_cid]:
            _cur = _leaf_owner.get(_lf['id'])
            if _cur is None or _clause_sizes[_cid] < _clause_sizes[_cur]:
                _leaf_owner[_lf['id']] = _cid

    def _own_leaves(clause):
        cid = clause['id']
        return [lf for lf in _clause_lvs[cid] if _leaf_owner.get(lf['id']) == cid]

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
                                                f"In this sentence, 'there {nxt['surface']}' is followed "
                                                f"by the plural noun '{head['surface']}'; write "
                                                f"'there are' instead.",
                                                _tree_evidence(clause['id'], 'there + be + NP')))
                        elif (not be_sg) and not noun_pl:
                            out.append(_finding('2.4', 'error', 'C-EXISTENTIAL',
                                                'existential there', nxt['id'],
                                                f"In this sentence, 'there {nxt['surface']}' is followed "
                                                f"by the singular noun '{head['surface']}'; write "
                                                f"'there is' instead.",
                                                _tree_evidence(clause['id'], 'there + be + NP')))

    # 2.8 Indefinite pronoun agreement
    for clause in clauses:
        cl = _leaves(clause)
        for i, lf in enumerate(cl):
            if _lower(lf) in INDEFINITE_PRON:
                # Only an indefinite pronoun in subject position governs the
                # clause verb.  If a finite/aux verb already appeared earlier in
                # this clause the pronoun is an object ("... that puzzled
                # everyone"), so it must not be matched with a later verb.
                if any(x.get('type') in FINITE_TYPES
                       or _lower(x) in (BE_SURFACES | HAVE_SURFACES | DO_SURFACES | MODAL_SURFACES)
                       for x in cl[:i]):
                    continue
                for nxt in cl[i + 1:]:
                    vk = _verb_key(nxt)
                    if nxt.get('type') in FINITE_TYPES or _lower(nxt) in (
                            BE_SURFACES | HAVE_SURFACES | DO_SURFACES):
                        if vk == ('*', 'non3sg'):
                            out.append(_finding('2.8', 'error', 'C-INDEFINITE-AGREE',
                                                'subject-verb agreement', nxt['id'],
                                                f"'{lf['surface']}' is singular, so it needs a singular "
                                                f"verb; '{nxt['surface']}' is plural and does not "
                                                f"agree with it.",
                                                _tree_evidence(clause['id'], 'indefinite + finite',
                                                               [{'node': lf['id']},
                                                                {'node': nxt['id']}])))
                        break

    # 2.14 Reflexive-antecedent
    for clause in clauses:
        cl = _own_leaves(clause)
        # The antecedent is the clause's own subject, not merely the first noun
        # leaf (which may sit inside a fronted adverbial PP, e.g. "In the quiet
        # hours before dawn, she prepared herself ..." -> subject is 'she').
        subj = None
        for cand in clause.get('children', []):
            if cand.get('type') == 'NP':
                subj = _np_head_leaf(cand)
                if subj is not None:
                    break
        if subj is None:
            for cand in cl:
                if cand.get('type') == 'PRP':
                    subj = cand
                    break
        for i, lf in enumerate(cl):
            if _lower(lf) in REFLEXIVE_KEY:
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
                                        f"The reflexive '{lf['surface']}' does not match the "
                                        f"subject '{subj['surface']}' in this sentence.",
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
                                f"'{head['surface']}' is a reflexive pronoun and cannot "
                                f"be the subject of this clause; use a personal "
                                f"pronoun such as 'I' or 'he' instead.",
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
                                f"The clause '{clause['surface']}' names a subject and a "
                                f"predicate but has no verb; add a form of 'be' "
                                f"such as '{'is'}' or '{'was'}'.",
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
                                        f"'{kids[i]['surface']} "
                                        f"{prp_leaf['surface']}' in this sentence says the "
                                        f"subject twice; keep only one of them.",
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
        # A subordinate clause whose own leaves contain an overt pronoun
        # ('Provided that it was raining' parses as a bare VP node) does have a
        # subject; the parse simply buries it, so do not report a missing one.
        if any(lf.get('type') == 'PRP' for lf in cl):
            continue
        first_verb = next((lf for lf in cl if lf.get('type') in
                           ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD')), None)
        if first_verb is not None and (first_verb.get('type') in ('VB', 'VBG', 'VBN')
                                       or _lower(first_verb) in
                                       ('do', 'does', 'did')):
            continue  # imperative or participial phrase (no finite verb)
        out.append(_finding('9.2', 'error', 'C-MISSING-SUBJECT', 'subject',
                            clause['id'],
                            f"The clause '{clause['surface']}' has a verb but no "
                            f"subject; add the subject that the verb requires.",
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
                                "A wh-question like this one needs the subject and "
                                "the auxiliary verb to change places, for example "
                                "'where are you going?'.",
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
                                    f"In this question, the subject "
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
                                        "An embedded question like this one keeps normal "
                                        "statement order, with the subject before the "
                                        "verb; it should not be inverted.",
                                        _tree_evidence(child['id'], 'SBAR -> S starting with verb')))

    # 9.4 Comma splice / fused sentence
    tops = _leaves(root)
    for i, lf in enumerate(tops):
        if lf.get('type') != ',':
            continue
        if quoted and i in quoted:
            continue  # comma inside a quoted utterance
        if (tops[:i] and tops[i - 1].get('surface', '') in ('"', '\u201c', '\u201d')) \
                or (i + 1 < len(tops)
                    and tops[i + 1].get('surface', '') in ('"', '\u201c', '\u201d')):
            continue  # comma adjacent to a quotation mark (dialogue tag)
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
        # A comma that opens a non-restrictive subordinate parenthetical that a
        # later comma closes ("..., while the music played, that ...") is not a
        # comma splice; the second clause after it is still licensed.
        later_comma = next((k for k in range(i + 1, len(tops))
                            if tops[k].get('type') == ','), None)
        if later_comma is not None:
            seg = tops[i + 1:later_comma]
            seg_low = [_lower(x) for x in seg[:4]]
            seg_finite = any(x.get('type') in FINITE_TYPES or _lower(x) in
                             (BE_SURFACES | HAVE_SURFACES | DO_SURFACES |
                              MODAL_SURFACES) for x in seg)
            if seg_finite and seg_low and (seg_low[0] in SUBORDINATORS
                                           or seg_low[0] in
                                           ('just', 'even', 'especially',
                                            'particularly', 'only')):
                continue
        if any(_lower(x) in ('which', 'who', 'whom', 'whose', 'that')
               for x in before):
            continue
        if before[0].get('type') in ('IN', 'TO', 'PP') or _lower(before[0]) in SUBORDINATORS:
            continue
        if before and _lower(before[-1]) in {'and', 'but', 'or', 'nor', 'so',
                                             'yet', 'for'}:
            continue
        if after and (_lower(after[0]) in {'and', 'but', 'or', 'nor', 'so',
                                           'yet', 'for', 'however', 'therefore',
                                           'moreover', 'nevertheless',
                                           'furthermore', 'thus', 'hence',
                                           'otherwise', 'meanwhile', 'even',
                                           'that', 'which', 'who', 'whom',
                                           'whose'}
                      or _lower(after[0]) in SUBORDINATORS):
            # A coordinator or subordinator after the comma means the second
            # part is not an independent clause, so this is not a comma splice
            # (e.g. "... , because the manager who called had insisted.").
            continue
        clause_a = ' '.join(x.get('surface', '') for x in before).rstrip().rstrip(' .')
        clause_b = ' '.join(x.get('surface', '') for x in after).rstrip().rstrip(' .')
        out.append(_finding('9.4', 'error', 'C-COMMA-SPLICE', 'punctuation',
                            lf['id'],
                            f"This sentence joins two complete clauses with a comma "
                            f"alone; put a semicolon between them: "
                            f"'{clause_a}; {clause_b}'.",
                            _tree_evidence(lf['id'], 'clause , clause')))

    # 9.8 Parallel structure (to run, swimming)
    for i, lf in enumerate(tops):
        if quoted and i in quoted:
            continue
        if lf.get('type') == 'TO' and i + 1 < len(tops) and tops[i + 1].get('type') == 'VB':
            for j in range(i + 2, len(tops)):
                x = tops[j]
                if quoted and j in quoted:
                    continue
                if x.get('type') in FINITE_TYPES or x.get('type') in ('VB', 'TO'):
                    break
                xlow = _lower(x)
                is_gerund = x.get('type') == 'VBG' or (
                    x.get('type') in ('NN', 'NNS') and xlow.endswith('ing'))
                follows_list_separator = j > 0 and tops[j - 1].get('type') in (',', 'CC')
                if is_gerund and follows_list_separator and xlow not in ING_NONVERBS:
                    match = _base_of(_lower(x))
                    out.append(_finding('9.8', 'error', 'C-PARALLEL', 'parallelism',
                                        x['id'],
                                        f"Everything in this list should take the same form, but "
                                        f"'{tops[i + 1]['surface']}' is a base verb while "
                                        f"'{x['surface']}' ends in 'ing'; change "
                                        f"'{x['surface']}' to '{match}' to match "
                                        f"'{tops[i + 1]['surface']}'.",
                                        _tree_evidence(lf['id'], 'to VB + list separator + gerund')))
                    break

    # 6.10 to + base form
    for i, lf in enumerate(leaves):
        if lf.get('type') == 'TO' and i + 1 < len(leaves):
            nxt = leaves[i + 1]
            finite = nxt.get('type') in ('VBD', 'VBZ', 'VBP') \
                or nxt.get('ftag') in ('VBD', 'VBZ', 'VBP') \
                or _lower(nxt) in MODAL_SURFACES \
                or _lower(nxt).endswith(('ies', 'es'))
            if finite:
                base = {'is': 'be', 'are': 'be', 'was': 'be', 'were': 'be',
                        'am': 'be', 'been': 'be', 'has': 'have', 'had': 'have',
                        'does': 'do', 'did': 'do'}.get(_lower(nxt)) \
                    or _base_of(_lower(nxt))
                out.append(_finding('6.10', 'error', 'C-TO-BASE', 'infinitive',
                                    nxt['id'],
                                    f"After 'to' in this sentence the verb must be in its "
                                    f"base form, but '{nxt['surface']}' is not.",
                                    _tree_evidence(lf['id'], 'TO + finite verb',
                                                   [{'node': lf['id']},
                                                    {'node': nxt['id']}]),
                                    _rem(f"'{nxt['surface']}' follows 'to' in this sentence.",
                                         f"Write '{base}' after 'to' instead of "
                                         f"'{nxt['surface']}'.")))
        # 6.12 modal + to
        if (_lower(lf) in MODAL_SURFACES or lf.get('type') == 'MD') \
                and _lower(lf) != 'ought' \
                and i + 1 < len(leaves) and leaves[i + 1].get('type') == 'TO':
            out.append(_finding('6.12', 'error', 'C-MODAL-TO', 'modal',
                                lf['id'],
                                f"The modal '{lf['surface']}' takes the verb directly "
                                f"without 'to'; drop 'to' here.",
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
                                    f"After the verb '{lf['surface']}', the object takes a "
                                    f"bare verb without 'to'; drop 'to' before "
                                    f"'{leaves[j + 1]['surface'] if j + 1 < len(leaves) else 'the verb'}'.",
                                    _tree_evidence(lf['id'], 'make/let + NP + TO')))

    # 6.11 Phrasal verb pronoun order: V + RP + pronoun
    for i, lf in enumerate(leaves):
        if lf.get('type') == 'RP' and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'PRP' \
                and _lower(leaves[i + 1]) in PRON_OBJ:
            out.append(_finding('6.11', 'error', 'C-PHRASAL-ORDER', 'phrasal verb',
                                lf['id'],
                                f"With the pronoun object '{leaves[i + 1]['surface']}', "
                                f"the particle comes last: write "
                                f"'{leaves[i + 1]['surface']} {lf['surface']}' "
                                f"instead of '{lf['surface']} {leaves[i + 1]['surface']}'.",
                                _wordlist_evidence('V + up/it', ['pick it up'],
                                                   'phrasal-verb order')))

    # 6.9 Gerund vs infinitive
    for i, lf in enumerate(leaves):
        if _lower(lf) in GERUND_VERBS and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'TO':
            ger = _vbg_of(_base_of(_lower(leaves[i + 2]))) \
                if i + 2 < len(leaves) else 'the -ing form'
            out.append(_finding('6.9', 'error', 'C-GERUND-INFINITIVE',
                                'complement type', lf['id'],
                                f"'{lf['surface']}' takes a gerund (the 'ing' form), not "
                                f"a 'to' + verb; write "
                                f"'{lf['surface']} {ger}' "
                                f"instead of '{lf['surface']} to {_lower(leaves[i + 2]) if i + 2 < len(leaves) else '...'}'.",
                                _wordlist_evidence(lf['surface'], [ger],
                                                   'gerund-taking verbs')))

    # 6.20 Verb + clause pattern (suggest him to go)
    for i, lf in enumerate(leaves):
        if _lower(lf) in CLAUSE_PATTERN_VERBS and i + 1 < len(leaves) \
                and leaves[i + 1].get('type') == 'PRP' \
                and i + 2 < len(leaves) and leaves[i + 2].get('type') == 'TO':
            base = _base_of(_lower(leaves[i + 3])) if i + 3 < len(leaves) \
                else 'go'
            ger = _vbg_of(base)
            subj = {'him': 'he', 'her': 'she', 'them': 'they', 'me': 'I',
                    'us': 'we', 'you': 'you', 'it': 'it'}.get(
                        _lower(leaves[i + 1]), 'they')
            out.append(_finding('6.20', 'error', 'C-VERB-CLAUSE-PATTERN',
                                'complement clause', lf['id'],
                                f"'{lf['surface']}' does not take an object and then a "
                                f"'to' + verb form; write "
                                f"'{lf['surface']} that {subj} {base}' "
                                f"or '{lf['surface']} {ger}' "
                                f"instead.",
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
                                    f"'{nxt['surface']}' cannot be used in the passive "
                                    f"because it is intransitive; use the active voice.",
                                    _wordlist_evidence(nxt['surface'],
                                                       [f"active: '{nxt['surface']}'"],
                                                       'intransitive-verb list')))
            if nxt.get('type') == 'VBG' and _lower(nxt)[:-3] in STATIVE_PROGRESSIVE:
                out.append(_finding('6.6', 'error', 'C-STATIVE-PROGRESSIVE',
                                    'aspect', nxt['id'],
                                    f"'{nxt['surface']}' is a stative verb, which in this "
                                    f"sentence is not used in the progressive; "
                                    f"use the simple form instead.",
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
                    ger = _vbg_of(_base_of(_lower(leaves[after])))
                    out.append(_finding('8.6', 'error', 'C-PREP-GERUND',
                                        'preposition + gerund', leaves[after]['id'],
                                        f"After the prepositional 'to' in "
                                        f"'{' '.join(phrase)}', the verb takes the 'ing' "
                                        f"form; write '{ger}', not "
                                        f"'{leaves[after]['surface']}'.",
                                        _tree_evidence(leaves[i]['id'],
                                                       'P + to + VBG')))

    # 9.9 Conjunction pairing (although ... but)
    lows_set = set(lows)
    if 'although' in lows_set and 'but' in lows_set \
            and not ('not' in lows_set and 'only' in lows_set):
            idx = next(i for i, x in enumerate(lows) if x == 'but')
            out.append(_finding('9.9', 'error', 'C-CONJUNCTION-PAIR', 'conjunction',
                                leaves[idx]['id'],
                                "This sentence links its two clauses with both "
                                "'although' and 'but'; use one of them, not both.",
                                _wordlist_evidence('although ... but', ['although ...'],
                                                   'conjunction-pairing table')))

    # 10.3 Terminal punctuation
    raw = (text or root.get('surface') or '').rstrip()
    while raw and raw[-1] in '"\u201d\u2019\')]':
        raw = raw[:-1].rstrip()
    if raw and raw[-1] not in '.?!':
        out.append(_finding('10.3', 'error', 'C-TERMINAL-PUNCT', 'punctuation',
                            root['id'],
                            "This sentence does not end with '.', '?' or '!'; put the "
                            "right end mark after the last word \u2014 a period ('.') "
                            "for a statement.",
                            _tree_evidence(root['id'], 'sentence boundary')))

    # 10.9 Spacing and repeats (function-word doubling)
    for i in range(1, len(leaves)):
        a, b = _lower(leaves[i - 1]), _lower(leaves[i])
        if a == b and a in {'the', 'a', 'an', 'of', 'to', 'in', 'on', 'is',
                            'was', 'are', 'and', 'or', 'very', 'my', 'your',
                            'his', 'her', 'its', 'our', 'their'}:
            out.append(_finding('10.9', 'error', 'C-SPACING-REPEAT', 'spacing',
                                leaves[i]['id'],
                                f"The word '{leaves[i]['surface']}' is written twice in a "
                                f"row; remove the second one.",
                                _tree_evidence(leaves[i]['id'], 'token i == token i+1')))

    # 10.5 Apostrophe (decade)
    import re as _re
    surface = (text if text else (root.get('surface') or ''))
    for m in _re.finditer(r"\b(\d{4})'s\b", surface):
        if m.group(1).endswith('0'):
            out.append(_finding('10.5', 'error', 'C-APOSTROPHE', 'apostrophe',
                                leaves[0]['id'],
                                f"Decades are written without an apostrophe: write "
                                f"'{m.group(1)}s' instead of '{m.group(0)}'.",
                                _tree_evidence(leaves[0]['id'], 'decade apostrophe')))

    # 10.6 Quotation marks (unbalanced)
    if surface.count('"') % 2 == 1 or surface.count('\u201c') != surface.count('\u201d'):
        out.append(_finding('10.6', 'error', 'C-QUOTATION', 'quotation',
                            root['id'],
                            "The quotation marks in this sentence do not match up: "
                            "every opening mark needs a closing one.",
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
                                    f"The adjectives in '{lf['surface']} {nxt['surface']}' "
                                    f"are in the wrong order; write "
                                    f"'{nxt['surface']} {lf['surface']}' instead.",
                                    _wordlist_evidence(
                                        f"{lf['surface']} {nxt['surface']}",
                                        [f"{nxt['surface']} {lf['surface']}"],
                                        'adjective-order categories')))
        # 7.5 enough big / too much good
        if low == 'enough' and nxt is not None and nxt.get('type') in (
                'JJ', 'JJR', 'JJS'):
            out.append(_finding('7.5', 'error', 'C-INTENSIFIER', 'intensifier',
                                lf['id'],
                                f"With the adjective '{nxt['surface']}', the word "
                                f"'enough' comes after it: write "
                                f"'{nxt['surface']} enough', not "
                                f"'enough {nxt['surface']}'.",
                                _tree_evidence(lf['id'], 'enough + JJ')))
        if low == 'much' and i >= 1 and _lower(leaves[i - 1]) == 'too' \
                and nxt is not None and nxt.get('type') in ('JJ', 'JJR', 'JJS'):
            out.append(_finding('7.5', 'error', 'C-INTENSIFIER', 'intensifier',
                                lf['id'],
                                f"'{nxt['surface']}' is a gradable adjective, so in this "
                                f"sentence write 'too {nxt['surface']}', not "
                                f"'too much {nxt['surface']}'.",
                                _tree_evidence(lf['id'], 'too much + JJ')))
        # 7.6 as tall than
        if low == 'as' and nxt is not None and nxt.get('type') in ('JJ', 'JJR', 'JJS'):
            for k in range(i + 2, min(i + 5, len(leaves))):
                if _lower(leaves[k]) == 'than':
                    out.append(_finding('7.6', 'error', 'C-COMPARATIVE-STRUCT',
                                        'comparative', leaves[k]['id'],
                                        f"With '{nxt['surface']}' and the word 'than', use "
                                        f"'as ... as', not 'as ... than'.",
                                        _tree_evidence(lf['id'], 'as ADJ than')))
                    break
        # 7.6 more tall (analytic + morphological)
        if low in ('more', 'most') and nxt is not None and nxt.get('type') == 'JJ' \
                and _lower(nxt) in SHORT_MORPH_ADJ:
            cmp_form = _lower(nxt) + ('er' if low == 'more' else 'est')
            out.append(_finding('7.6', 'error', 'C-COMPARATIVE-STRUCT',
                                'comparative', nxt['id'],
                                f"'{nxt['surface']}' is a short adjective and in this "
                                f"sentence takes the form '{cmp_form}', not "
                                f"'{low} {nxt['surface']}'.",
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
                                f"'{lf['surface']}' is the wrong plural or singular "
                                f"form here; use '{fix}' instead.",
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
                                    f"'{lf['surface']}' takes a singular noun, so in this "
                                    f"sentence it should not be followed by the plural "
                                    f"'{nxt['surface']}'.",
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
                                f"'{cl[0]['surface']}' is the subject of this clause "
                                f"and must take the subject form: write "
                                f"'{fix}' instead.",
                                _tree_evidence(clause['id'], 'coordinate NP subject',
                                               [{'node': cl[0]['id']}])))

    # 5.5 dummy it/there (Is raining)
    # Relative clauses realized as SBAR(WHNP S(VP)) carry their subject in the
    # relative pronoun, so the inner S legitimately has no NP of its own.
    rel_s_ids = set()
    for n in _iter_nodes(root):
        if n.get('type') != 'SBAR':
            continue
        kids = n.get('children', [])
        if any(k.get('type') in ('WHNP', 'WHADVP', 'WHPP') for k in kids):
            for k in kids:
                if k.get('type') == 'S':
                    rel_s_ids.add(k['id'])
    for clause in clauses:
        if clause.get('type') != 'S':
            continue
        if clause['id'] in rel_s_ids:
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
                                f"This clause starts with '{cl[0]['surface']}' but has "
                                f"no subject; add the dummy subject 'it': for example, "
                                f"'it is {cl[1]['surface']}'.",
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
                                    'cannot be used in the passive in this sentence.',
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
                                            'back', 'away') \
                    and _lower(nxt) not in BARE_OBJECTS:
                out.append(_finding('6.8', 'error', 'C-TRANSITIVITY',
                                    'transitivity', lf['id'],
                                    f"'{lf['surface']}' does not take a direct object; "
                                    f"in this sentence it needs a preposition instead.",
                                    _wordlist_evidence(lf['surface'], [],
                                                       'verb transitivity list')))

    # 6.14 double negation
    for clause in clauses:
        cl = _leaves(clause)
        negs = [x for i, x in enumerate(cl) if _lower(x) in {'not', 'no', 'nothing', 'nobody',
                                                             'none', 'never', 'nowhere',
                                                             "n't", 'nt'}
                and not (_lower(x) == 'not' and i + 1 < len(cl)
                         and _lower(cl[i + 1]) == 'only')]
        if len(negs) >= 2:
            # A negation in a subordinate clause and another in the main clause
            # ('Though nobody expected it, ... was not ready.') is a separate
            # clause, not a double negative in the same clause.
            if any(x.get('type') == ',' for x in cl
                   [next((k for k, y in enumerate(cl) if y['id'] == negs[0]['id']), 0):
                    next((k for k, y in enumerate(cl) if y['id'] == negs[1]['id']), 0)]):
                continue
            out.append(_finding('6.14', 'error', 'C-DOUBLE-NEGATIVE', 'negation',
                                clause['id'],
                                f"In this clause, '{negs[0]['surface']}' and "
                                f"'{negs[1]['surface']}' are two negatives; "
                                'standard English uses only one negation.',
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
                base = _base_of(_lower(v))
                out.append(_finding('6.15', 'error', 'C-IMPERATIVE-VERB',
                                    'imperative', v['id'],
                                    f"After the negator '{leaves[i + 1]['surface']}', the "
                                    f"verb must be in its base form; use '{base}' instead "
                                    f"of '{v['surface']}'.",
                                    _tree_evidence(lf['id'], "do + n't + finite")))

    # 6.16 conditional with 'will' (If I will go)
    for i, lf in enumerate(leaves):
        if _lower(lf) == 'if':
            hit = None
            for candidate in leaves[i + 1:]:
                if candidate.get('type') == ',' or candidate.get('surface') == ',':
                    break
                if _lower(candidate) in ('will', 'would'):
                    hit = _lower(candidate)
                    break
            if hit:
                out.append(_finding('6.16', 'error', 'C-CONDITIONAL-WILL',
                                    'conditional', leaves[i]['id'],
                                    f"The clause after 'if' takes the present tense, not "
                                    f"'{hit}'; drop '{hit}' and use the present tense there.",
                                    _tree_evidence(lf['id'], 'if + will')))

    # 6.18 reported speech (She said me)
    for i, lf in enumerate(leaves):
        if _lower(lf) in ('said', 'say') and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) in PRON_OBJ \
                and _lower(leaves[i + 1]) not in ('it',):
            out.append(_finding('6.18', 'error', 'C-REPORTED-SPEECH',
                                'reported speech', lf['id'],
                                f"'{lf['surface']}' needs 'to' before the person it is "
                                f"said to; write '{lf['surface']} to {leaves[i + 1]['surface']}' "
                                f"instead of '{lf['surface']} {leaves[i + 1]['surface']}'.",
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
                    # Subordinator material between the two verbs ('in case X',
                    # 'once X', 'because X') means the second clause is licensed,
                    # not a run-on.
                    bw = [_lower(b) for b in between]
                    if any(w in SUBORDINATORS for w in bw) \
                            or 'in' in bw and bw.index('in') + 1 < len(bw) \
                            and bw[bw.index('in') + 1] == 'case' \
                            or 'as' in bw and bw.index('as') + 2 < len(bw) \
                            and bw[bw.index('as') + 1] == 'soon' \
                            and bw[bw.index('as') + 2] == 'as':
                        break
                    out.append(_finding('9.3', 'error', 'C-RUNON',
                                        'sentence boundary', x['id'],
                                        f"In this sentence two finite clauses are joined "
                                        "without punctuation or a conjunction; write each "
                                        "clause as its own sentence (add a period), or join "
                                        "them with a word like 'and' or 'because'.",
                                        _tree_evidence(x['id'], 'finite ... finite',
                                                       [{'node': lf['id']},
                                                        {'node': x['id']}])))
                break

    # 9.7 extra word (very the happy)
    for i, lf in enumerate(leaves):
        # An intensifier directly before a determiner is only wrong when the
        # determiner heads an adjective phrase ("very the happy"); "so the
        # group celebrated" is just coordination, not this error.
        if _lower(lf) in ('very', 'really', 'so', 'too') and i + 2 < len(leaves) \
                and leaves[i + 1].get('type') == 'DT' \
                and leaves[i + 2].get('type') in ('JJ', 'JJR', 'JJS'):
            out.append(_finding('9.7', 'error', 'C-EXTRA-WORD', 'word order',
                                leaves[i + 1]['id'],
                                f"The determiner after '{lf['surface']}' in this "
                                f"sentence is unexpected; remove it.",
                                _tree_evidence(lf['id'], 'adverb + determiner')))

    # 2.9 quantified subject: 'the number of X' takes a singular verb
    for i in range(len(leaves) - 2):
        if _lower(leaves[i]) == 'the' and _lower(leaves[i + 1]) == 'number' \
                and _lower(leaves[i + 2]) == 'of':
            for lf in leaves[i + 3:]:
                if lf.get('type') == 'VBP' or _lower(lf) in ('are', 'were'):
                    out.append(_finding('2.9', 'error', 'C-NUMBER-AGREE',
                                        'agreement', lf['id'],
                                        f"With the phrase 'the number of', this sentence takes "
                                        f"a singular verb, not '{lf['surface']}'.",
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
                                lf['id'], f"The pronoun '{surface}' here means 'I' and is "
                                "always capitalized.",
                                _wordlist_evidence('i', ['I'], 'capitalization list')))
        elif low in DAYS or (low in MONTHS and low not in {'may', 'march',
                                                           'august'}):
            if surface[:1].islower():
                out.append(_finding('10.2', 'error', 'C-PROPER-NOUN',
                                    'capitalization', lf['id'],
                                    f"'{surface}' names a day or month and must be "
                                    f"capitalized in this sentence as "
                                    f"'{surface.capitalize()}'.",
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
f"The possessive '{lf['surface']}' in this sentence "
                                f"needs a noun after it; write a possessive pronoun "
                                f"that stands alone, like 'mine' or 'yours'.",
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
                                f"'{surface}' has the wrong ordinal suffix; write "
                                f"'{num}{correct}' instead.",
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
                                f"With the correlative subject, the verb agrees with the "
                                f"nearest subject '{nearest['surface']}': use 'am', "
                                f"not '{vhead['surface']}'.",
                                _tree_evidence(nearest['id'],
                                               'nearest subject + verb')))
        elif nlow in ('he', 'she', 'it') and vlow in ('are', 'were'):
            out.append(_finding('2.13', 'error', 'C-CORRELATIVE-AGREE', 'agreement',
                                vhead['id'],
                                f"With the correlative subject, the verb agrees with the "
                                f"nearest subject '{nearest['surface']}': use "
                                f"'is/was', not '{vhead['surface']}'.",
                                _tree_evidence(nearest['id'],
                                               'nearest subject + verb')))

    # 1.3 possessive 's missing (the boys toy)
    ANIMATE_PLURAL = {'boys', 'girls', 'men', 'women', 'children', 'students',
                      'teachers', 'friends', 'parents', 'brothers', 'sisters',
                      'kids', 'babies', 'people'}
    NOUN_TAGS = ('NN', 'NNS', 'NNP', 'NNPS')
    TIME_NOUNS = {'today', 'yesterday', 'tomorrow', 'tonight', 'now', 'then',
                  'soon', 'time', 'morning', 'afternoon', 'evening', 'night',
                  'week', 'month', 'year', 'weekend'}
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
            if _lower(bhead) in TIME_NOUNS:
                continue
            out.append(_finding('1.3', 'error', 'C-POSSESSIVE-S', 'possessive',
                                ahead['id'],
                                f"In '{ahead['surface']} {bhead['surface']}', the first "
                                f"noun needs an apostrophe to show ownership: write "
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
                    high_confidence = _lower(cleaves[0]) in HUMAN_ONLY_PARTICIPLES
                    status = 'error' if high_confidence else 'suggestion'
                    confidence = 0.95 if high_confidence else 0.55
                    out.append(_finding('9.11', status, 'C-DANGLING',
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
                                            confidence)))
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
                                f"At the start of this sentence, the connector "
                                f"'{cleaves[0]['surface']}' needs a comma after it: "
                                f"write '{cleaves[0]['surface']}, ...'.",
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
                                    f"The ';' inside this list should be a comma; a "
                                    "semicolon joins whole clauses instead.",
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
                                f"This passive needs a form of 'be' plus the past "
                                f"participle; write "
                                f"'{subhead['surface']} was {verb['surface']}', or "
                                'use the correct participle form.',
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
            # A fronted adjunct often glues its prepositional phrase into the
            # first NP ("After a long and difficult meeting, of all the rooms,
            # the train is the calmest one"); that is not an object-before-verb
            # error. Skip when any *pre-verbal* NP holds adjunct material.
            pre_lvs = [_leaves(np) for np in pre]
            if any(x.get('type') in ('IN', 'TO', ',', '``', "''")
                   for lvs in pre_lvs for x in lvs):
                continue
            heads = []
            for np in pre:
                nl = _leaves(np)
                heads.append(_lower(nl[-1]) if nl else '')
            if all(h not in TIME_WORDS for h in heads):
                vp = ch[vfirst]
                vl = _leaves(vp)
                out.append(_finding('9.6', 'error', 'C-WORD-ORDER', 'word order',
                                    vl[0]['id'] if vl else vp['id'],
                                    f"In this statement the object comes before the verb; "
                                    'the object should follow the verb instead.',
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
        # 'a long and difficult meeting, of all the rooms' is one NP with an
        # attached adverbial; a comma or preposition inside the subject means
        # the CC does not coordinate two plain nouns.
        if any(x.get('type') in ('IN', ',', '``', "''") for x in sleaves):
            continue
        if conj in ('and', '&'):
            joined = ' '.join(_lower(x) for x in sleaves)
            if joined in {'bread and butter', 'peanut butter and jelly',
                          'fish and chips', 'gin and tonic'}:
                continue
            if vkey == ('3', 'sg') or vlow in ('is', 'was', 'has', 'does'):
                out.append(_finding('2.3', 'error', 'C-COORD-SUBJ-AGREE',
                                    'subject-verb agreement', vhead['id'],
                                    f"'{subj['surface']}' joins two subjects with "
                                    f"'{conj}', which makes it plural; this verb "
                                    f"'{vhead['surface']}' is singular and does not "
                                    "agree.",
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
                                    f"After '{conj}', the verb agrees with the "
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
                                    f"After '{conj}', the verb agrees with the "
                                    f"nearest subject '{near['surface']}', which is "
                                    f"plural; this verb '{vhead['surface']}' does not "
                                    "agree.",
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
                                    f"'{a['surface']}' describes '{b['surface']}', and a "
                                    f"describing noun stays singular: write "
                                    f"'{fix} {b['surface']}' instead.",
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
                                f"verb and its pronoun object '{nhead['surface']}'; "
                                f"move it after the pronoun, as in "
                                f"'... {nhead['surface']} {k['surface']}'.",
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
        cd_surface = nxt.get('surface', '') or ''
        is_clock = (nxt.get('type') == 'CD'
                    and (':' in cd_surface
                         or (cd_surface.isdigit() and len(cd_surface) <= 2))) \
            or any(a in CLOCK for a in after)
        tgt = None
        if low == 'at' and w in DAY_WORDS:
            tgt = 'on'
        elif low == 'at' and w in MONTH_WORDS:
            tgt = 'in'
        elif low == 'in' and w in DAY_WORDS:
            tgt = 'on'
        elif low == 'on' and w in MONTH_WORDS:
            if not (i + 2 < len(leaves) and leaves[i + 2].get('type') == 'CD'):
                tgt = 'in'  # 'on January 5' (with a day number) is correct
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
                                f"For a time expression like '{low} {w}...' in this "
                                f"sentence, the correct preposition is '{tgt}'.",
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
                                    f"'{low} {w} {w2}' in this sentence has too many "
                                    f"prepositions; write '{w} {w2}' instead.",
                                    _wordlist_evidence(f"{low} {w} {w2}",
                                                       [f"{w} {w2}"],
                                                       'in/on/at time table')))

    # 9.1 fragment: a subordinate clause standing alone (Because I was late.)
    if root.get('type') == 'SBAR':
        out.append(_finding('9.1', 'error', 'C-FRAGMENT', 'sentence structure',
                            root['id'],
                            "This sentence starts with a subordinate clause and has "
                            "no main clause, so it is only a fragment; add a main "
                            "clause to complete the sentence.",
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
                            f"The relative pronoun '{wl[0]['surface']}' already "
                            f"stands for the object, so '{obj['surface']}' repeats "
                            "it; remove the repetition.",
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
                                f"'{inc['surface']}' joins a whole clause, so a bare "
                                f"'to' + verb with no subject cannot follow it "
                                "directly in this sentence.",
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
                                f"The direct object in this sentence should come "
                                f"right after the verb '{verb['surface']}'; write "
                                f"'{verb['surface']} {pobj['surface']} "
                                f"{nxt.get('surface', '')}', or "
                                f"'{verb['surface']} {nxt.get('surface', '')} "
                                f"{kl[0]['surface']} {pobj['surface']}'.",
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
                                    f"This sentence begins with '{surf}', but sentences "
                                    f"start with a capital letter; write "
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


def _vbg_of(base):
    """Base verb -> '-ing' form (run->running, make->making, die->dying)."""
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


def _past_of(base):
    """Best-effort simple-past form for a verb base (see->saw, kick->kicked)."""
    try:
        from lemminflect import getInflection
        inf = getInflection(base.lower(), tag='VBD')
        if inf:
            return inf[0]
    except Exception:  # pragma: no cover
        pass
    w = base.lower()
    return w + 'd' if w.endswith('e') else w + 'ed'


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
                f"After the modal '{lf['surface']}', the verb must be "
                f"in its base form, but '{nxt['surface']}' is a third-person-"
                f"singular form; use '{lemma}'.",
                _wordlist_evidence(f"{low} {nlow}", [f"{low} {lemma}"],
                                   'modal + base verb')))
        elif nlow == 'to':
            n2 = _lower(leaves[i + 2]) if i + 2 < len(leaves) else '...'
            out.append(_finding(
                '6.12', 'error', 'C-MODAL-TO', 'verb form', nxt['id'],
                f"The modal '{lf['surface']}' is followed directly by "
                f"the verb, without 'to': write '{lf['surface']} {n2}', not "
                f"'to {n2}'.",
                _tree_evidence(nxt['id'], 'MD + to', [{'node': nxt['id']}])))
        elif nlow in MODAL_SURFACES:
            out.append(_finding(
                '6.12', 'error', 'C-MODAL-STACK', 'verb form', nxt['id'],
                f"This sentence has two modals in a row, "
                f"'{lf['surface']}' and '{nxt['surface']}'; "
                'English uses only one modal.',
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
                f"The phrase 'there {n1}' is not correct; with "
                f"'there' this sentence uses a form of 'be', so write "
                f"'there {fix}'.",
                _wordlist_evidence(f"there {n1}", [f"there {fix}"],
                                   'existential there + be')))

    # --- 2.10 / 2.11 numeral & quantifier before a singular noun ------------- #
    for i, lf in enumerate(leaves):
        low = lows[i]
        pl = lf.get('type') == 'CD' or low in PLURALIZERS
        if not pl or i + 1 >= len(leaves):
            continue
        if low in ('one', '1', 'a', 'an'):
            continue  # 'one book' stays singular
        if i > 0 and leaves[i - 1].get('type') in (
                'NN', 'NNS', 'NNP', 'NNPS', 'CD'):
            continue  # 'page five' / identifier reading
        j = i + 1
        while j < len(leaves) and leaves[j].get('type') in ('JJ', 'JJR', 'JJS'):
            j += 1
        if j >= len(leaves):
            continue
        nxt = leaves[j]
        if _lower(nxt) in {'today', 'yesterday', 'tomorrow', 'tonight', 'now',
                           'later', 'then', 'soon', 'already', 'again'}:
            continue  # trailing time adverb, not the counted noun
        if _lower(nxt) in {"o'clock", "o' clock", 'clock'}:
            continue  # 'ten o'clock' is a clock phrase, not a counted noun
        if nxt.get('type') == 'IN':
            continue  # 'many of the ...'
        if nxt.get('type') == 'NNS':
            continue
        if nxt.get('type') == 'NN':
            rule = '2.10' if lf.get('type') == 'CD' else '2.11'
            out.append(_finding(
                rule, 'error', 'C-QUANT-PLURAL', 'noun number', nxt['id'],
                f"After '{lf['surface']}' the noun must be "
                f"plural: write '{nxt['surface']}s' instead of "
                f"'{nxt['surface']}'.",
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
                f"'much' is used with uncountable nouns, but here "
                f"'{nxt['surface']}' is a count plural; use 'many'.",
                _wordlist_evidence(f"much {nlow}", [f"many {nlow}"],
                                   'much (mass) vs many (count)')))
        elif low == 'many' and nt == 'NN':
            out.append(_finding(
                '2.11', 'error', 'C-QUANTIFIER-CLASS', 'quantifier', nxt['id'],
                f"'many' is used with plural count nouns, but here "
                f"'{nxt['surface']}' is singular; use 'much' or make the "
                "noun plural.",
                _wordlist_evidence(f"many {nlow}", [f"much {nlow}"],
                                   'many (count) vs much (mass)')))
        elif low == 'less' and nt == 'NNS':
            out.append(_finding(
                '2.11', 'error', 'C-QUANTIFIER-CLASS', 'quantifier', nxt['id'],
                f"'less' is used with uncountable nouns; with the count "
                f"plural '{nxt['surface']}' here, use 'fewer'.",
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
                    f"After the preposition '{lf['surface']}', the pronoun "
                    f"must be '{obj}', not '{nxt}'.",
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
                    f"In '{lf['surface']} {nxt['surface']}', the first "
                    f"word shows ownership and should be 'their', not "
                    f"'{lf['surface']}'.",
                    _tree_evidence(lf['id'], 'there + NN (possessive slot)',
                                   [{'node': lf['id']}, {'node': nxt['id']}])))
        # its vs it's
        elif low == 'its' and (nlow in DT_WORDS or nt in verb_tags + ('MD',)):
            out.append(_finding(
                '1.10', 'error', 'C-HOMOPHONE', 'spelling', lf['id'],
                f"Here the word '{lf['surface']}' means 'it is', so "
                f"it needs an apostrophe: write 'it\u2019s'.",
                _tree_evidence(lf['id'], 'its + verb/article (it is slot)',
                               [{'node': lf['id']}])))
        # your vs you're
        elif low == 'your' and (nlow in ('a', 'an', 'the') or nt in verb_tags
                                or nlow in ('going', 'wanting')):
            out.append(_finding(
                '1.10', 'error', 'C-HOMOPHONE', 'spelling', lf['id'],
                f"Here the word '{lf['surface']}' means 'you are', so "
                f"it needs an apostrophe: write 'you\u2019re'.",
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
                f"'{lf['surface']}' is always singular, so in this "
                f"sentence the verb must be '{sg}', not "
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
                ger = _vbg_of(_base_of(n2))
                out.append(_finding(
                    '6.9', 'error', 'C-GERUND-INFIN', 'verb complement',
                    leaves[i + 1]['id'],
                    f"'{lf['surface']}' takes an 'ing' form as its "
                    f"complement: write '{lf['surface']} {ger}' "
                    f"instead of '{lf['surface']} to {n2}'.",
                    _wordlist_evidence(f"{low} to {n2}",
                                       [f"{low} {ger}"],
                                       'gerund-taking verb')))
            elif leaves[i + 1].get('type') == 'VB':
                ger = _vbg_of(_base_of(nln))
                out.append(_finding(
                    '6.9', 'error', 'C-GERUND-INFIN', 'verb complement',
                    leaves[i + 1]['id'],
                    f"'{lf['surface']}' takes an 'ing' form as its "
                    f"complement: write '{lf['surface']} {ger}' "
                    f"instead of '{low} {nln}'.",
                    _wordlist_evidence(f"{low} {nln}", [f"{low} {ger}"],
                                       'gerund-taking verb')))
        elif low in ('want', 'wants', 'wanted', 'wanting'):
            if leaves[i + 1].get('type') == 'VBG':
                vbg = _lower(leaves[i + 1])
                out.append(_finding(
                    '6.9', 'error', 'C-GERUND-INFIN', 'verb complement',
                    leaves[i + 1]['id'],
                    f"'want' takes a 'to' + verb form: write "
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
            ger = _vbg_of(_lower(leaves[i + 2])) if i + 2 < len(leaves) else 'the verb'
            out.append(_finding(
                '8.6', 'error', 'C-PREP-GERUND', 'verb complement',
                leaves[i + 1]['id'],
                f"After the preposition 'at', the verb takes the 'ing' "
                f"form; write '{ger}' instead of 'to "
                f"{_lower(leaves[i + 2]) if i + 2 < len(leaves) else '...'}'.",
                _tree_evidence(lf['id'], 'preposition + to-infinitive',
                               [{'node': lf['id']},
                                {'node': leaves[i + 1]['id']}])))
        if low in ('look', 'looks', 'looked') and nln == 'forward' \
                and i + 2 < len(leaves) and _lower(leaves[i + 2]) == 'to' \
                and i + 3 < len(leaves) \
                and leaves[i + 3].get('type') in ('VB', 'VBZ'):
            nxtv = _lower(leaves[i + 3])
            ger = _vbg_of(nxtv)
            out.append(_finding(
                '8.6', 'error', 'C-PREP-GERUND', 'verb complement',
                leaves[i + 3]['id'],
                f"After the phrase 'look forward to', the verb takes the 'ing' "
                f"form; write '{ger}' instead of '{nxtv}'.",
                _wordlist_evidence(f"look forward to {nxtv}",
                                   [f"look forward to {ger}"],
                                   'look forward to + gerund')))

    # --- 11.3 'since' needs (have/had) + past participle ---------------------- #
    SINCE_NUMWORDS = {'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                      'eight', 'nine', 'ten', 'a', 'an', 'few', 'several',
                      'many', 'couple'}
    SINCE_UNITS = {'year', 'years', 'month', 'months', 'week', 'weeks', 'day',
                   'days', 'hour', 'hours', 'minute', 'minutes', 'second',
                   'seconds', 'decade', 'decades', 'century', 'centuries',
                   'while', 'ages'}
    for i, lf in enumerate(leaves):
        if lows[i] != 'since':
            continue
        # 'since' + a length of time should be 'for' (since three years).
        if i + 2 < len(leaves):
            a, b = leaves[i + 1], leaves[i + 2]
            if (a.get('type') == 'CD' or _lower(a) in SINCE_NUMWORDS) \
                    and _lower(b) in SINCE_UNITS:
                out.append(_finding(
                    '11.3', 'error', 'C-TENSE-SINCE', 'tense', lf['id'],
                    f"With a length of time like '{a['surface']} {b['surface']}', "
                    f"use 'for', not 'since'; write 'for {a['surface']} "
                    f"{b['surface']}'.",
                    _wordlist_evidence(f"since {a['surface']} {b['surface']}",
                                       [f"for {a['surface']} {b['surface']}"],
                                       'for + length of time')))
                continue
        have_in = any(_lower(x) in ('have', 'has', 'had')
                      for x in leaves[max(0, i - 5):i])
        if have_in:
            continue
        # Only the *temporal* 'since' (a point in time) forces a perfect tense.
        # The causal conjunction ("... since everyone was ready.") is fine with
        # a simple present, so require a time expression right after 'since'.
        SINCE_TIME_WORDS = {'then', 'yesterday', 'today', 'tomorrow', 'morning',
                            'afternoon', 'evening', 'night', 'noon', 'dawn',
                            'dusk', 'childhood', 'birth', 'last'}
        nxt = leaves[i + 1] if i + 1 < len(leaves) else None
        nxt_low = _lower(nxt) if nxt is not None else ''
        is_time_point = (nxt is not None and (
            nxt.get('type') in ('CD', 'NNP')
            or nxt_low in DAYS or nxt_low in MONTHS
            or nxt_low in SINCE_TIME_WORDS))
        if not is_time_point:
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
                f"With the word 'since', this sentence needs a perfect "
                f"tense ('have/has' plus a past participle), not the present "
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
                    f"'{lf['surface']}' is a stative verb, which does not take "
                    f"the progressive form; use '{verb}' or '{verb}s' instead.",
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
        if leaves[i + 2].get('type') in ('RB', 'RBR', 'RBS'):
            continue  # relative clause: '... which had just arrived' (valid)
        # A wh-word that is the subject of a BE clause with a predicate
        # complement keeps that order: 'I know who was right'.  Inverting would
        # put the BE form before its predicate ('who right was'), not before a
        # pronoun subject, so there is nothing here to fix.
        if _lower(leaves[i + 1]) in BE_SURFACES_LEAF \
                and leaves[i + 2].get('type') in ('JJ', 'JJR', 'JJS', 'RB', 'NN', 'NNS'):
            continue
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
                f"In this sentence, '{lows[i]}' needs 'at' (or 'in' for "
                f"a country or city) after it, not 'to'; write "
                f"'{lows[i]} at', not '{lows[i]} to'.",
                _wordlist_evidence(f"{lows[i]} to",
                                   [f"arrive at", f"arrive in"],
                                   'verb + preposition')))

    # --- 6.3 'please to' -------------------------------------------------------- #
    for i, lf in enumerate(leaves):
        if lows[i] == 'please' and i + 1 < len(leaves) \
                and _lower(leaves[i + 1]) == 'to':
            out.append(_finding(
                '6.3', 'error', 'C-PLEASE-TO', 'verb form', lf['id'],
                f"The word 'please' at the start takes the verb directly; "
                f"write "
                f"'please {leaves[i + 2]['surface'] if i + 2 < len(leaves) else 'the verb'}', "
                f"not 'please to ...'.",
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
                f"'{lf['surface']} in' describes how a person feels; "
                f"write '{ed} in' instead.",
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
                f"form; after the subject pronoun '{leaves[i - 1]['surface']}' "
                f"write '{_past_of(base)}', or use a perfect with "
                f"'have {lows[i]}'.",
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
                f"The reflexive pronoun '{lf['surface']}' is not a "
                f"standard form; write '{REFLEXIVE_FIX[low]}' instead.",
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
# C-layer checks (context/meaning); high-confidence contradictions may be errors.
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
                                            f"'{lf['surface']}' can take a singular verb; in "
                                            f"this sentence 'is' may read better than "
                                            f"'{nxt['surface']}'.",
                                            _context_evidence(
                                                f"collective noun '{lf['surface']}' + plural verb",
                                                [{'option': 'is',
                                                  'evidence': 'US usage prefers the singular form'},
                                                 {'option': 'are',
                                                  'evidence': 'UK usage allows the plural form'}],
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
                            f"This sentence joins two clauses with a comma before "
                            "'however'; use '; however,' or start a new sentence "
                            "with '. However,' instead.",
                            _context_evidence(
                                "comma + however across two clauses",
                                [{'option': '; however,',
                                  'evidence': 'two complete clauses need a semicolon'},
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
                                    f"'{lf['surface']}' follows a past-tense verb in this "
                                    'sentence; after a past verb, English usually '
                                    "shifts it to 'would'.",
                                    _context_evidence(
                                        'past verb + will',
                                        [{'option': 'would',
                                          'evidence': 'matches the past reporting verb'},
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
                                f"'{lf['surface']}' is an informal word; in an "
                                'academic sentence, choose a formal word instead.',
                                _context_evidence(
                                    'informal vocabulary',
                                    [{'option': 'a formal synonym',
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
f"In this sentence, '{leaves[i + 1]['surface']}' is a "
                            "verb, not an adjective, so it should not follow a form "
                            f"of 'be' such as '{lf['surface']}'.",
                            _context_evidence(
                                "be + verb",
                                [{'option': leaves[i + 1]['surface'],
                                  'evidence': 'used as a normal verb'},
                                 {'option': f"{lf['surface']} {leaves[i + 1]['surface']}",
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
    quoted = _quoted_indices(leaves)
    clauses = _clauses(root)
    findings = []
    findings.extend(_check_wordlists(leaves))
    findings.extend(_check_adjective_adverb(leaves))
    findings.extend(_check_tree(root, clauses, leaves, text, quoted))
    findings.extend(_check_more(root, clauses, leaves))
    findings.extend(_check_context(root, clauses, leaves))
    return findings
