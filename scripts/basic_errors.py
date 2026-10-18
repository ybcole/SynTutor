import json, sys, urllib.request

BASE = 'http://127.0.0.1:8000/api/parse'

BATTERY = [
    # (WRONG, CORRECT control, category)
    ("He go to school every day.", "He goes to school every day.", "3sg -s missing"),
    ("She play the piano well.", "She plays the piano well.", "3sg -s missing"),
    ("I likes pizza.", "I like pizza.", "3sg -s extra"),
    ("We watches TV at night.", "We watch TV at night.", "3sg -s extra"),
    ("They runs fast.", "They run fast.", "3sg -s extra"),
    ("He doesn't likes pizza.", "He doesn't like pizza.", "do-support double 3sg"),
    ("She doesn't likes coffee.", "She doesn't like coffee.", "do-support double 3sg"),
    ("He is go to school.", "He goes to school.", "be + base"),
    ("She is cook dinner.", "She cooks dinner.", "be + base"),
    ("I am went there.", "I went there.", "be + past"),
    ("He is went home.", "He went home.", "be + past"),
    ("He goed to school.", "He went to school.", "past invention"),
    ("She catched the ball.", "She caught the ball.", "past invention"),
    ("I buyed a book.", "I bought a book.", "past invention"),
    ("They eated dinner.", "They ate dinner.", "past invention"),
    ("He runned fast.", "He ran fast.", "past invention"),
    ("I have went there.", "I have been there.", "past participle"),
    ("She has saw the movie.", "She has seen the movie.", "past participle"),
    ("He has ate dinner.", "He has eaten dinner.", "past participle"),
    ("It was broke.", "It was broken.", "past participle"),
    ("He can sings.", "He can sing.", "modal + s"),
    ("She must goes home.", "She must go home.", "modal + s"),
    ("You should to go.", "You should go.", "modal + to"),
    ("I can to swim.", "I can swim.", "modal + to"),
    ("There is many people here.", "There are many people here.", "existential agreement"),
    ("There are a problem.", "There is a problem.", "existential agreement"),
    ("There has many issues.", "There are many issues.", "existential have"),
    ("I bought two bread.", "I bought two loaves of bread.", "plural missing"),
    ("She has many informations.", "She has much information.", "mass noun plural"),
    ("The childs are playing.", "The children are playing.", "plural invention"),
    ("I have three book.", "I have three books.", "plural missing"),
    ("I need a money.", "I need money.", "uncountable a"),
    ("Do you have a homework?", "Do you have homework?", "uncountable a"),
    ("I saw a apple.", "I saw an apple.", "a/an"),
    ("He is an university student.", "He is a university student.", "a/an"),
    ("She has a umbrella.", "She has an umbrella.", "a/an"),
    ("She is teacher.", "She is a teacher.", "article missing"),
    ("He is doctor.", "He is a doctor.", "article missing"),
    ("I have car.", "I have a car.", "article missing"),
    ("That is he book.", "That is his book.", "possessive adjective"),
    ("Me went to the store.", "I went to the store.", "pronoun subj case"),
    ("Him is tall.", "He is tall.", "pronoun subj case"),
    ("Them are here.", "They are here.", "pronoun subj case"),
    ("Her is happy.", "She is happy.", "pronoun subj case"),
    ("She gave it to I.", "She gave it to me.", "pronoun obj case"),
    ("He saw we yesterday.", "He saw us yesterday.", "pronoun obj case"),
    ("I called he.", "I called him.", "pronoun obj case"),
    ("He hurt hisself.", "He hurt himself.", "reflexive form"),
    ("They did it thereselves.", "They did it themselves.", "reflexive form"),
    ("I don't have no money.", "I don't have any money.", "double negative"),
    ("He doesn't know nothing.", "He doesn't know anything.", "double negative"),
    ("She is more smarter than me.", "She is smarter than me.", "double comparative"),
    ("This is most best.", "This is the best.", "double superlative"),
    ("He is more better now.", "He is better now.", "double comparative"),
    ("He runs fastly.", "He runs fast.", "flat adverb"),
    ("She sings beautiful.", "She sings beautifully.", "adjective for adverb"),
    ("He drives careful.", "He drives carefully.", "adjective for adverb"),
    ("What you want?", "What do you want?", "question word order"),
    ("Where you are going?", "Where are you going?", "question word order"),
    ("Why he did that?", "Why did he do that?", "question word order"),
    ("When you will come?", "When will you come?", "question word order"),
    ("Who she is?", "Who is she?", "question word order"),
    ("Is raining outside.", "It is raining outside.", "subject drop"),
    ("Is very hot today.", "It is very hot today.", "subject drop"),
    ("Went to the store yesterday.", "I went to the store yesterday.", "subject drop"),
    ("There dog is big.", "Their dog is big.", "homophone there/their"),
    ("Your a nice person.", "You're a nice person.", "homophone your/you're"),
    ("Its a good idea.", "It's a good idea.", "homophone its/it's"),
    ("Whose coming to dinner.", "Who's coming to dinner.", "homophone whose/who's"),
    ("I like there music.", "I like their music.", "homophone there/their"),
    ("I want going home now.", "I want to go home now.", "gerund/infinitive"),
    ("She enjoys to swim.", "She enjoys swimming.", "gerund/infinitive"),
    ("He finished to eat.", "He finished eating.", "gerund/infinitive"),
    ("I look forward to hear from you.", "I look forward to hearing from you.", "gerund/infinitive"),
    ("She is good at to sing.", "She is good at singing.", "gerund/infinitive"),
    ("I could of helped.", "I could have helped.", "could of"),
    ("I should of known.", "I should have known.", "could of"),
    ("She made me to go.", "She made me go.", "make + to"),
    ("He let me to leave.", "He let me leave.", "let + to"),
    ("She was cry.", "She was crying.", "past prog missing -ing"),
    ("He is work hard.", "He is working hard.", "progressive missing -ing"),
    ("They are play soccer.", "They are playing soccer.", "progressive missing -ing"),
    ("I don't have many money.", "I don't have much money.", "many/much"),
    ("How much books do you have?", "How many books do you have?", "many/much"),
    ("This books are old.", "These books are old.", "demonstrative"),
    ("These car is slow.", "This car is slow.", "demonstrative"),
    ("Every students are here.", "Every student is here.", "every + plural"),
    ("Everyone are here.", "Everyone is here.", "everyone + are"),
    ("I am agree.", "I agree.", "copula + verb"),
    ("She is feel tired.", "She feels tired.", "copula + verb"),
    ("He can able to come.", "He can come.", "can able"),
    ("I am here since Monday.", "I have been here since Monday.", "present perfect missing"),
    ("She is working since 2018.", "She has been working since 2018.", "present perfect missing"),
    ("He said he is go tomorrow.", "He said he would go tomorrow.", "sequence of tenses"),
    # --- wave 2: agreement, auxiliaries, questions, passives ------------------ #
    ("He don't like it.", "He doesn't like it.", "don't/doesn't"),
    ("She don't know me.", "She doesn't know me.", "don't/doesn't"),
    ("Do she like pizza?", "Does she like pizza?", "do/does question"),
    ("I seen him yesterday.", "I saw him yesterday.", "VBN as simple past"),
    ("He have a car.", "He has a car.", "have/has"),
    ("They has a car.", "They have a car.", "has/have"),
    ("I is tired.", "I am tired.", "am/is"),
    ("You is nice.", "You are nice.", "is/are"),
    ("This bag is more expensive.", "This bag is more expensive.", "multi-syllable comparative (valid)"),
    ("She is more sharper than him.", "She is sharper than him.", "double comparative"),
    ("He is good in math.", "He is good at math.", "preposition choice"),
    ("She is interested for art.", "She is interested in art.", "preposition choice"),
    ("I arrived to the airport.", "I arrived at the airport.", "arrive preposition"),
    ("He discussed about politics.", "He discussed politics.", "discuss about"),
    ("I have less books than her.", "I have fewer books than her.", "less/fewer"),
    ("There is too much apples.", "There are too many apples.", "much/many count"),
    ("I don't have many money.", "I don't have much money.", "many/much mass"),
    ("I have much friends.", "I have many friends.", "much+count"),
    ("I am knowing him well.", "I know him well.", "stative progressive"),
    ("He is liking this book.", "He likes this book.", "stative progressive"),
    ("The news are good.", "The news is good.", "news singular"),
    ("I have a scissors.", "I have a pair of scissors.", "scissors plural-only"),
    ("I wonder where is he.", "I wonder where he is.", "indirect question"),
    ("Tell me where is the station.", "Tell me where the station is.", "indirect question"),
    ("Please to sit down.", "Please sit down.", "please to"),
    ("It was happened yesterday.", "It happened yesterday.", "intransitive passive"),
    ("She can able to swim.", "She can swim.", "can able"),
    ("I am interesting in art.", "I am interested in art.", "participial adjective"),
    ("Although he was tired, but he kept working.", "Although he was tired, he kept working.", "although but"),
    ("We was at school.", "We were at school.", "was/were"),
    ("There was many people.", "There were many people.", "existential agreement"),
    ("She like to dance.", "She likes to dance.", "3sg missing"),
]

def probe(text):
    req = urllib.request.Request(BASE, data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        d = json.load(r)
    s = d['summary']
    v = s.get('verdict') or ('VALID' if s['valid'] else 'INVALID')
    if v == 'grammatical':
        return 'PASS', '', []
    if v == 'unverified':
        det = s.get('detector', {})
        return 'MODEL', det.get('label', ''), s.get('constraints_fired') or []
    return 'RULES', s.get('explanation', '')[:80], s.get('constraints_fired') or []

def run():
    from collections import Counter
    c = Counter(); rows = []
    for wrong, control, cat in BATTERY:
        w = probe(wrong)
        g = probe(control)
        c[w[0]] += 1
        if w[0] != 'RULES' or g[0] != 'PASS':
            rows.append((cat, wrong, control, w, g))
    print('=== channel counts (wrong sentences) ===')
    for k, v in sorted(c.items()): print(f'  {k:8s}: {v:3d}')
    print('\n=== problematic cases (not rules-flagged AND/OR control not clean) ===')
    for cat, wrong, control, w, g in rows:
        mark = 'PASS-through!' if w[0] == 'PASS' else ('MODEL-only' if w[0] == 'MODEL' else 'FP-control')
        print(f'[{mark}] {cat}: {wrong!r}')
        if w[0] != 'RULES':
            print(f'        -> verdict={w[0]} {w[1]} fired={w[2]}')
        if g[0] != 'PASS':
            print(f'        -> CONTROL {control!r}: verdict={g[0]} {g[1]}')

if __name__ == '__main__':
    run()