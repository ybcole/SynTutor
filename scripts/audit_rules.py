"""SynTutor rule-matrix coverage audit.

Deterministic, offline check (no HTTP): drives the real parse engine +
matrix over a gold corpus and reports, for every distinct (parent, child)
edge type seen:

    rule id        -> the matrix constraint that fired
    status         -> valid / error / unlisted

Guarantees we care about:
  * no known-grammatical sentence is flagged invalid (no false positives)
  * no known-ungrammatical sentence passes as valid (no false negatives)
  * every distinct edge produced by the corpus is covered by a dedicated
    matrix rule (the ``unrated`` / ``unlisted`` count stays at 0), so a
    future input can never silently rely on "valid-by-default".

Exit code is non-zero on any regression, making it safe to run in CI.
"""

import os
import sys
from collections import Counter
from collections.abc import Iterator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.matrix import evaluate
from server.parse_engine import analyze
from server.ruleset import RULEBOOK, all_rule_ids

GOLD: list[tuple[str, bool, str]] = [
    # (sentence, expected_valid, why)
    ("The boy reads a book.", True, "simple SVO"),
    ("The clever boy reads a fascinating book.", True, "NP modifiers"),
    ("Mary is running in the park.", True, "be + VBG"),
    ("They read books.", True, "plural subject + VBP"),
    ("John runs fast.", True, "3sg subject + VBZ + ADVP"),
    ("The children play in the park every day.", True, "PP adjunct + ADVP"),
    ("She has eaten the cake.", True, "have + VBN"),
    ("They have eaten the cake.", True, "have + VBN (plural)"),
    ("They came home.", True, "irregular VBD"),
    ("They have come home.", True, "irregular VBN"),
    ("I am reading a book.", True, "am (1sg)"),
    ("The book was read by Mary.", True, "passive be + VBN"),
    ("The boys and girls are playing.", True, "coordinated plural subject + are"),
    ("Kielle and Jaisen are my classmates.", True, "coordinated subject (names)"),
    ("Apples and oranges are my favorite.", True, "coordinated plural subject"),
    ("The dog in the park is barking.", True, "NP + PP postmodifier"),
    ("The man who lives next door is kind.", True, "NP + relative clause"),
    ("He will read the book.", True, "modal + VB"),
    ("They will eat the cake.", True, "modal + VB (plural)"),
    ("Mary can swim very fast.", True, "modal + VB + ADVP"),
    ("The teacher speaks English well.", True, "V + NP object + ADVP"),
    ("You are my best friend.", True, "2nd person + are"),
    ("In the park, they run fast.", True, "fronted PP adjunct at S level"),
    ("That he left is true.", True, "clausal subject (SBAR under S)"),
    ("I know which book you read.", True, "embedded wh-clause"),

    ("The boys runs.", False, "subject-verb agreement"),
    ("The boy run.", False, "subject-verb agreement"),
    ("John are running fast.", False, "subject-verb agreement"),
    ("I runs fast.", False, "subject-verb agreement"),
    ("She have a cat.", False, "subject-verb agreement"),
    ("They runs fast.", False, "subject-verb agreement (plural subj)"),
    ("The boys is running fast.", False, "subject-verb agreement (plural subj)"),
    ("Jaisen and Kielle is my thesis groupmates.", False, "coordinated subject (names)"),
    ("Apples and oranges is my favorite.", False, "coordinated plural subject"),
    ("She and I is best friends.", False, "coordinated pronoun subject"),
    ("The boy and girl runs.", False, "coordinated singular subject + 3sg verb"),

    ("These boy runs.", False, "determiner-noun agreement"),
    ("A dogs bark.", False, "determiner-noun agreement"),
    ("Those cat is sleeping.", False, "determiner-noun agreement (pl det)"),

    ("Mary will eats.", False, "auxiliary form (modal)"),
    ("The girl has eat.", False, "auxiliary form (have)"),
    ("They have came home.", False, "past tense cannot follow have"),
    ("They have becomed happy.", False, "invalid regularized form after have"),
    ("They becomed happy.", False, "invalid regularized past form"),
    ("The girl has eats the cake.", False, "auxiliary form (have)"),
    ("The dog is barks loudly.", False, "auxiliary form (be)"),
    ("She is reads the book.", False, "auxiliary form (be)"),
    ("The boy running.", False, "clause finiteness"),
    ("The boy running fast.", False, "clause finiteness"),

    ("The my book is on the table.", False, "determiner stacking (DT + possessive)"),
    ("His the car is red.", False, "determiner stacking (possessive + DT)"),

    ("I hate your.", False, "NP head-licensing (bare possessive determiner)"),
    ("She loves my.", False, "NP head-licensing (bare possessive determiner)"),
    ("Their is a problem.", False, "NP head-licensing (bare possessive)"),
    ("He gave the book to she.", False, "pronoun case (objective after preposition)"),
    ("Me likes music.", False, "pronoun case (objective as subject)"),
    ("Him is running fast.", False, "pronoun case (objective as subject)"),
    ("They call she a hero.", False, "pronoun case (objective as direct object)"),
    ("I gave the gift to he.", False, "pronoun case (objective after preposition)"),
    ("He runs quick.", False, "adjective-adverb confusion (flat adverb)"),
    ("She sings beautiful.", False, "adjective-adverb confusion (adj after action verb)"),
    ("Dog is barking.", False, "missing article (bare singular subject)"),
    ("I need new car.", False, "missing article (bare singular object)"),
    ("He is doctor.", False, "missing article (bare predicate noun)"),
    ("He saw a elephant.", False, "a-an article selection"),
    ("He is an waiter.", False, "a-an article selection"),
    ("he runs fast.", False, "sentence capitalization"),
    ("i am happy.", False, "sentence capitalization"),
    ("He ate less cookies.", False, "quantifier-noun agreement (less + plural)"),
    ("I have fewer money.", False, "quantifier-noun agreement (fewer + mass)"),
    ("She has much friends.", False, "quantifier-noun agreement (much + plural)"),
    ("I eat many apple.", False, "quantifier-noun agreement (many + singular)"),
    ("He is more smarter.", False, "double comparative"),
    ("He is most biggest.", False, "double superlative"),
    ("I am agree.", False, "VP headed by a noun (missing verb form)"),
    ("He decided to stays.", False, "to-infinitive complement instead of base form"),

    ("I hate your car.", True, "possessive determiner + noun (valid)"),
    ("Our house is big.", True, "possessive determiner + noun (valid)"),
    ("My favorite color is blue.", True, "nominalized adjective head 'favorite' (valid)"),
    ("She likes me.", True, "objective pronoun as object (valid)"),
    ("I gave her the book.", True, "objective pronoun + indirect object (valid)"),
    ("She talked to me.", True, "objective pronoun after preposition (valid)"),
    ("He works quickly.", True, "adverb form after action verb (valid)"),
    ("The boys run fast.", True, "legitimate flat adverb 'fast' (valid)"),
    ("An apple a day helps the doctor.", True, "an + vowel sound (valid)"),
    ("He finished an hour ago.", True, "an + silent-h hour (valid)"),
    ("She is an honest student.", True, "an + silent-h honest (valid)"),
    ("He attends a university.", True, "a + consonant-sound university (valid)"),
    ("I love music.", True, "mass noun without article (valid)"),
    ("Reading is fun.", True, "gerund-like subject + uncountable fun (valid)"),
    ("He goes home.", True, "bare institutional noun (valid)"),
    ("It is I.", True, "nominative after copula (valid)"),
    ("They made her happy.", True, "object complement without case error (valid)"),
    ("He seems happy.", True, "linking verb + predicate adjective (valid)"),
    ("Every boy ran fast.", True, "determiner every + singular (valid)"),
    ("I bought fewer cookies.", True, "fewer + plural count (valid)"),
    ("He has less money.", True, "less + mass noun (valid)"),
    ("She has many friends.", True, "many + plural count (valid)"),
    ("This is my new phone.", True, "standalone demonstrative subject (valid)"),
    ("These are my books.", True, "standalone demonstrative subject (valid)"),
    ("Each is important.", True, "quantifier pronoun head (valid)"),
    ("I wanted to go home.", True, "to-infinitive complement clause (valid)"),
    ("She decided to stay.", True, "to-infinitive complement clause (valid)"),
    ("He is more beautiful.", True, "analytic comparative, degree marker + positive (valid)"),
    # --- newly implemented rules: contractions, spelling, morphology ---
    ("I dont know.", False, "1.5 missing apostrophe in contraction"),
    ("I don't know.", True, "contraction with apostrophe (valid)"),
    ("Please recieve the letter.", False, "1.4 misspelling recieve->receive"),
    ("Please receive the letter.", True, "correctly spelled receive (valid)"),
    ("He is runing.", False, "1.2 verb -ing doubling runing->running"),
    ("He is running.", True, "correct -ing doubling (valid)"),
    ("She sings happyly.", False, "1.3 adverb ending happyly->happily"),
    ("She sings happily.", True, "correct adverb ending (valid)"),
    ("He did it hisself.", False, "1.10 reflexive hisself->himself"),
    ("He did it himself.", True, "correct reflexive (valid)"),
    ("There are two hundreds people.", False, "1.9 numeral two hundreds->two hundred"),
    ("She gave me informations.", False, "1.2 uncountable informations->information"),
    ("He gave an advice.", False, "1.2 uncountable an advice->advice"),
    ("She gave me information.", True, "uncountable mass noun (valid)"),
    ("He bought a scissors.", False, "4.4 plural-only scissors->a pair of scissors"),
    # --- verb form / syntax ---
    ("I am knowing the answer.", False, "6.8 stative progressive"),
    ("I know the answer.", True, "stative simple present (valid)"),
    ("She enjoys to swim.", False, "6.6 gerund/infinitive complement"),
    ("She enjoys swimming.", True, "gerund complement (valid)"),
    ("You must to go.", False, "6.14 modal + to"),
    ("You must go.", True, "modal + base (valid)"),
    ("He wants to goes home.", False, "6.10 infinitival to + base"),
    ("He wants to go home.", True, "to + base (valid)"),
    ("They made me to cry.", False, "6.15 causative made + bare infinitive"),
    ("They made me cry.", True, "causative + bare infinitive (valid)"),
    ("I suggest him to go.", False, "6.17 verb + to-infinitive pattern"),
    ("I look forward to see you.", False, "8.6 preposition + gerund"),
    ("I look forward to seeing you.", True, "preposition + gerund (valid)"),
    ("He returned back home.", False, "8.2 redundant particle back"),
    ("He returned home.", True, "no redundant particle (valid)"),
    # --- prepositions ---
    ("He is interested on music.", False, "8.3 fixed adjective+preposition"),
    ("He is interested in music.", True, "correct adjective+preposition (valid)"),
    ("We discussed about the plan.", False, "8.4 redundant preposition about"),
    ("We discussed the plan.", True, "no redundant preposition (valid)"),
    ("Please listen music.", False, "8.3 missing preposition listen to"),
    ("Please listen to music.", True, "correct listen to (valid)"),
    # --- adjective/adverb rules ---
    ("She bought a red big car.", False, "7.2 adjective order colour before size"),
    ("She bought a big red car.", True, "correct adjective order (valid)"),
    ("The bag is enough big.", False, "7.5 intensifier enough placement"),
    ("The bag is big enough.", True, "enough after adjective (valid)"),
    ("He is as tall than me.", False, "7.6 as ... than comparative"),
    ("He is more tall than me.", False, "7.6 analytic + morphological double comparative"),
    ("He is taller than me.", True, "correct comparative (valid)"),
    ("He is more beautiful than her.", True, "analytic comparative with long adjective (valid)"),
    # --- quantifiers / determiners ---
    ("I don't have some money.", False, "2.4 some in negative context"),
    ("I don't have any money.", True, "any in negative context (valid)"),
    ("There is books on the table.", False, "2.9 existential there agreement"),
    ("There are books on the table.", True, "existential there agreement (valid)"),
    ("Everyone have a dream.", False, "2.8 indefinite pronoun + 3sg verb"),
    ("Everyone has a dream.", True, "indefinite pronoun agreement (valid)"),
    # --- sentence structure ---
    ("She hurt himself.", False, "5.4 reflexive antecedent gender"),
    ("She hurt herself.", True, "correct reflexive antecedent (valid)"),
    ("Myself am happy.", False, "5.4 reflexive pronoun as subject"),
    ("I am happy.", True, "nominative subject pronoun (valid)"),
    ("She very happy.", False, "6.3 missing copula"),
    ("She is very happy.", True, "copula present (valid)"),
    ("Went to school.", False, "9.2 missing subject"),
    ("He went to school.", True, "subject present (valid)"),
    ("Where you are going?", False, "2.6 question inversion"),
    ("Where are you going?", True, "correct question inversion (valid)"),
    ("Where is the books?", False, "6.13 question subject-verb agreement"),
    ("I came, I saw.", False, "9.4 comma splice"),
    ("I came, and I saw.", True, "coordinated clauses with conjunction (valid)"),
    # --- punctuation / orthography ---
    ("He runs fast", False, "10.8 missing terminal punctuation"),
    ("He runs fast.", True, "terminal punctuation present (valid)"),
    ("The the cat sat.", False, "10.2 repeated word"),
    ("The 1990's were great.", False, "10.5 apostrophe in plural decade"),
    ("The 1990s were great.", True, "decade plural without apostrophe (valid)"),
    ('He said "hello.', False, "10.6 unbalanced quotation marks"),
    # --- conjunction pairing ---
    ("Although he was tired, but he worked.", False, "9.9 although + but"),
    ("Although he was tired, he worked.", True, "subordinate + main clause (valid)"),
    # --- C-layer suggestions (non-blocking, verdict stays valid) ---
    ("She plays the football.", True, "3.3 unnecessary article -- suggestion"),
    ("The team are winning.", True, "11.6 collective noun agreement -- suggestion"),
    ("The girls lost her bag.", True, "11.7 pronoun antecedent -- suggestion"),
    ("I wish I was taller.", True, "11.5 subjunctive 'I wish I were' -- suggestion"),
    # --- agreement across phrases, double subject, indirect question ---
    ("The boy with the bags go to school.", False, "2.2 agreement across intervening phrase"),
    ("The boy with the bags goes to school.", True, "2.2 agreement with true head noun (valid)"),
    ("My brother he runs fast.", False, "9.5 double subject"),
    ("My brother runs fast.", True, "single subject (valid)"),
    ("I wonder where is he.", False, "9.13 indirect question word order"),
    ("I wonder where he is.", True, "indirect question statement order (valid)"),
    # --- batch: remaining matrix.md T/L rules ---
    ("I saw three boxs.", False, "1.1 regular noun plural boxs->boxes"),
    ("I saw three boxes.", True, "regular plural (valid)"),
    ("I have another books.", False, "3.8 another + plural noun"),
    ("I have another book.", True, "another + singular (valid)"),
    ("Me and him went to school.", False, "5.2 coordinate subject objective case"),
    ("He and I went to school.", True, "nominative coordinate subject (valid)"),
    ("Is raining.", False, "5.5 missing dummy subject"),
    ("It is raining.", True, "dummy subject present (valid)"),
    ("The accident was happened.", False, "6.5 intransitive passive"),
    ("The accident happened.", True, "intransitive active (valid)"),
    ("She arrived the station.", False, "6.8 verb needs a preposition"),
    ("She arrived at the station.", True, "preposition present (valid)"),
    ("I don't have no money.", False, "6.14 double negation"),
    ("I don't have any money.", True, "single negation (valid)"),
    ("Don't goes there.", False, "6.15 imperative + finite verb"),
    ("Don't go there.", True, "imperative + base form (valid)"),
    ("If I will go, I will tell you.", False, "6.16 conditional with will"),
    ("If I go, I will tell you.", True, "conditional present (valid)"),
    ("If the library staff will catalogue the books, readers will find them.",
     False, "6.16 conditional modal after a multiword subject"),
    ("If the shop owner would open earlier, more customers would arrive.",
     False, "6.16 second conditional modal after a multiword subject"),
    ("If the library staff catalogue the books, readers will find them.",
     True, "6.16 main-clause will is not in the if-clause"),
    ("She said me the truth.", False, "6.18 reported speech said + object"),
    ("She told me the truth.", True, "reported speech with told (valid)"),
    ("I like tea she likes coffee.", False, "9.3 run-on / fused sentence"),
    ("I like tea, and she likes coffee.", True, "coordinated clauses (valid)"),
    ("She is very the happy.", False, "9.7 extra determiner"),
    ("i am happy.", False, "10.2 lowercase pronoun I"),
    ("I am happy.", True, "capitalized pronoun I (valid)"),
    ("We meet on monday.", False, "10.2 lowercase day name"),
    ("We meet on Monday.", True, "capitalized day name (valid)"),
    # --- batch: C-layer suggestions (verdict stays valid) ---
    ("I am boring.", True, "7.4 participial adjective -- suggestion"),
    ("This will effect the result.", True, "11.1 confusable effect/affect -- suggestion"),
    ("We need to do a decision.", True, "11.2 collocation -- suggestion"),
    ("The book eats grass.", True, "11.4 selectional restriction -- suggestion"),
    ("He has lots of stuff to do.", True, "11.6 register -- suggestion"),
    ("I am agree with you.", False, "11.7 L1 interference flagged as error"),
    ("He said he will come.", True, "6.7 tense consistency -- suggestion"),
    ("He is a well known author.", True, "10.7 hyphenation -- suggestion"),
    ("Today I went to school.", True, "11.3 tense-time -- suggestion"),
    ("I was tired, however I slept.", True, "11.8 connector misuse -- suggestion"),
    ("He is gooder than me.", False, "1.7 irregular comparative gooder->better"),
    ("He is better than me.", True, "irregular comparative (valid)"),
    ("Please pick up it.", False, "6.11 phrasal verb particle order"),
    ("Please pick it up.", True, "phrasal verb correct order (valid)"),
    ("I like to run, swimming.", False, "9.8 parallel structure"),
    ("The number of boys are large.", False, "2.9 quantified subject agreement"),
    ("Yesterday I go to the market.", True, "11.3 tense-time -- suggestion"),
    ("This is my.", False, "5.6 possessive determiner with no noun"),
    ("The book is mine.", True, "standalone possessive pronoun (valid)"),
    ("It is the 2th of May.", False, "10.10 wrong ordinal suffix 2th->2nd"),
    ("It is the 2nd of May.", True, "correct ordinal suffix (valid)"),
    ("Either he or I is right.", False, "2.13 correlative nearest-subject agreement"),
    ("Either he or I am right.", True, "correlative nearest subject (valid)"),
    ("I found the boys toy.", False, "1.3 missing possessive apostrophe-s"),
    ("I found the boy's toy.", True, "possessive apostrophe-s (valid)"),
    ("She enjoys dancing, to read and cooking.", False, "9.8 non-parallel list items"),
    ("She enjoys dancing, reading and cooking.", True, "9.8 parallel gerund list (valid)"),
    ("She wants to paint the building.", True, "9.8 does not mistake a noun for a list item"),
    ("Walking home, the rain started.", False, "9.11 dangling modifier"),
    ("Sitting in the garden, the rain started.", False, "9.11 dangling human action"),
    ("However I left.", False, "10.4 missing comma after introductory connector"),
    ("However, I left.", True, "introductory comma present (valid)"),
    ("I like tea; coffee.", False, "10.8 semicolon joining list items"),
    ("I like tea; she likes coffee.", True, "semicolon joins clauses (valid)"),
    ("Tom told Jim he would leave.", True, "5.3 ambiguous pronoun reference -- suggestion"),
    ("I saw the man with the telescope.", True, "11.5 PP-attachment ambiguity -- suggestion"),
    ("The book wrote by John.", False, "6.4 passive formation missing be/participle"),
    ("I saw the dog.", True, "3.4 definite article first mention -- suggestion"),
    ("The boy quickly the ball kicked.", False, "9.6 object-before-verb word order"),
    # --- the 10 previously label-only rules (implemented) ---
    ("Tom and Ann is going home.", False, "2.3 coordinated subject (and) + singular verb"),
    ("Tom and Ann are going home.", True, "2.3 coordinated subject + plural verb (valid)"),
    ("The boy or the girls is here.", False, "2.3 or/nor agrees with nearest plural subject"),
    ("The girls or the boy is here.", True, "2.3 or/nor agrees with nearest singular subject (valid)"),
    ("The plan is a ten-years plan.", False, "4.2 plural noun as modifier ten-years -> ten-year"),
    ("I have a ten-year plan.", True, "4.2 singular noun modifier (valid)"),
    ("I like very much it.", False, "7.3 adverb between verb and pronoun object"),
    ("I like it very much.", True, "7.3 pronoun object before adverb (valid)"),
    ("She depends in her family.", True, "8.1 wrong preposition after depend -- suggestion"),
    ("She depends on her family.", True, "8.1 correct depend on (valid)"),
    ("I will see you on 5 pm.", False, "8.5 in/on/at time: on + clock -> at"),
    ("I will see you at 5 pm.", True, "8.5 at + clock time (valid)"),
    ("I will meet you in next Monday.", False, "8.5 no preposition before next + day"),
    ("I will meet you next Monday.", True, "8.5 next + day without preposition (valid)"),
    ("Because I was late.", False, "9.1 fragment: subordinate clause without main clause"),
    ("Because I was late, I missed the bus.", True, "9.1 subordinate clause + main clause (valid)"),
    ("The man who I saw him is here.", False, "9.10 resumptive pronoun in relative clause"),
    ("The man who I saw is here.", True, "9.10 relative clause without resumptive pronoun (valid)"),
    ("I went home because to see you.", False, "9.14 subordinator + to-infinitive without subject"),
    ("I went there in order to see you.", True, "9.14 in order to construction (valid)"),
    ("He gave to me a book.", False, "9.15 ditransitive object order gave to me a book"),
    ("He gave me a book.", True, "9.15 correct indirect-object order (valid)"),
    ("the boy runs.", False, "10.1 sentence must start with a capital letter"),
    ("The boy runs.", True, "10.1 capitalized sentence start (valid)"),
    ("They are stupid and lacks manners.", False, "2.1 coordinated predicate: conjunct verb agrees with subject"),
    ("They are stupid and lack manners.", True, "2.1 coordinated predicate agreement (valid)"),
    ("She sings and play football.", False, "2.1 flat coordinated main verbs agree with subject"),
    ("She sings and plays football.", True, "2.1 flat coordinated verbs agreement (valid)"),
    # --- basic surface-error detectors (ruleset._check_basic) ------------------ #
    ("She must goes home.", False, "6.1 modal + 3rd-singular"),
    ("She must go home.", True, "6.1 modal + bare infinitive (valid)"),
    ("You should to go.", False, "6.12 modal + to"),
    ("You should go.", True, "6.12 modal (valid)"),
    ("There has many issues.", False, "2.4 existential there + have"),
    ("There are many issues.", True, "2.4 existential (valid)"),
    ("I have three book.", False, "2.10 numeral + singular noun"),
    ("I have three books.", True, "2.10 numeral + plural (valid)"),
    ("How much books do you have?", False, "2.11 much + plural count"),
    ("How many books do you have?", True, "2.11 many + plural (valid)"),
    ("I have less books than her.", False, "2.11 less + plural count"),
    ("I have fewer books than her.", True, "2.11 fewer (valid)"),
    ("She gave it to I.", False, "5.1 preposition + nominative pronoun"),
    ("She gave it to me.", True, "5.1 preposition + objective pronoun (valid)"),
    ("I like there music.", False, "1.10 there/their homophone"),
    ("These are their rooms.", True, "1.10 their (valid)"),
    ("Your a nice person.", False, "1.10 your/you're homophone"),
    ("You're a nice person.", True, "1.10 you're + person (valid, guards 1.1 FP too)"),
    ("Its a good idea.", False, "1.10 its/it's homophone"),
    ("It's a good idea.", True, "1.10 it's (valid)"),
    ("Its color is nice.", True, "1.10 possessive its (valid)"),
    ("Everyone are here.", False, "2.8 indefinite pronoun + plural verb"),
    ("Everyone is here.", True, "2.8 indefinite pronoun (valid)"),
    ("I want going home now.", False, "6.9 want + gerund"),
    ("I want to go home now.", True, "6.9 want + to-infinitive (valid)"),
    ("She enjoys to swim.", False, "6.9 enjoy + to-infinitive"),
    ("She enjoys swimming.", True, "6.9 enjoy + gerund (valid)"),
    ("I look forward to hear from you.", False, "8.6 look forward to + base"),
    ("I look forward to hearing from you.", True, "8.6 look forward to + gerund (valid)"),
    ("I am here since Monday.", False, "11.3 since + simple present"),
    ("I have been here since Monday.", True, "11.3 since + present perfect (valid)"),
    ("We have since moved on.", True, "11.3 since as adverb after have (valid)"),
    ("They did it thereselves.", False, "1.9 nonstandard reflexive"),
    ("They did it themselves.", True, "1.9 reflexive (valid)"),
    ("He runs fastly.", False, "7.1 nonstandard adverb"),
    ("He runs fast.", True, "7.1 flat adverb is fine (valid)"),
    ("He is liking this book.", False, "6.6 stative verb + progressive"),
    ("He likes this book.", True, "6.6 stative simple present (valid)"),
    ("Tell me where is the station.", False, "9.13 indirect question word order"),
    ("Tell me where the station is.", True, "9.13 indirect question (valid)"),
    ("I arrived to the airport.", False, "8.1 arrive + to"),
    ("I arrived at the airport.", True, "8.1 arrive + at (valid)"),
    ("Please to sit down.", False, "6.3 please + to"),
    ("Please sit down.", True, "6.3 bare imperative after please (valid)"),
    ("I am interesting in art.", False, "7.4 participial adjective -ing"),
    ("I am interested in art.", True, "7.4 -ed participial adjective (valid)"),
    ("We was at school.", False, "2.1 we/they/you + was"),
    ("We were at school.", True, "2.1 were (valid)"),
    ("I seen him yesterday.", False, "1.6 bare past participle as past"),
    ("I saw him yesterday.", True, "1.6 simple past (valid)"),
    ("This bag is more expensive.", True, "7.6 multi-syllable analytic comparative (valid)"),
    ("We watch TV at night.", True, "3.2 bare TV object is idiomatic (valid)"),
    ("She feels tired.", True, "7.1 linking verb + adjective complement (valid)"),
]


def edge_iter(details: dict) -> Iterator[tuple[str, str, str, str]]:
    """Yield (parent_type, child_type, constraint, status) for every edge."""
    type_of = {d['id']: d['type'] for d in details.values()}
    for d in details.values():
        pid = d.get('parent')
        if pid is None:
            continue
        yield type_of[pid], d['type'], d['constraint'], d['status']


def run_corpus() -> tuple[list[dict], Counter, Counter, set]:
    records = []
    violations = []
    edge_counter = Counter()
    status_counter = Counter()
    suggestion_counter = Counter()
    rule_counter = Counter()
    method_counter = Counter()
    unlisted_edges = set()
    for text, expected, why in GOLD:
        analysis = analyze(text)
        result = evaluate(analysis['root'], text=analysis['sentence'])
        details = result['details']
        summary = result['summary']
        actual = summary.get('verdict')
        want = 'grammatical' if expected else 'ungrammatical'
        edges = list(edge_iter(details))
        edge_counter.update((pt, ct) for pt, ct, _, _ in edges)
        status_counter.update(st for _, _, _, st in edges)
        for pt, ct, constraint, status in edges:
            if status == 'unlisted':
                unlisted_edges.add((pt, ct, constraint))
        for d in details.values():
            if d['status'] == 'error':
                violations.append((text, d['type'], d['constraint'], d['text']))
            if d.get('rule_id'):
                rule_counter[d['rule_id']] += 1
                method_counter[d['method']] += 1
            for finding in d.get('findings', []):
                rule_counter[finding['rule_id']] += 1
                method_counter[finding['method']] += 1
                if finding['status'] == 'suggestion':
                    suggestion_counter[finding['constraint']] += 1
        records.append({
            'text': text,
            'expected': expected,
            'actual': actual,
            'why': why,
            'ok': actual == want and not summary.get('checker_errors'),
            'checker_errors': summary.get('checker_errors', []),
            'edges': len(edges),
            'fired': sorted(summary['constraints_fired']),
            'suggested': summary.get('suggested', 0),
        })
    return records, edge_counter, status_counter, unlisted_edges, suggestion_counter, rule_counter, method_counter


def report(records, edge_counter, status_counter, unlisted_edges,
           suggestion_counter, rule_counter, method_counter):
    print('=' * 88)
    print('SynTutor rule-matrix coverage audit')
    print('=' * 88)

    failed = [r for r in records if not r['ok']]
    total_suggestions = sum(r['suggested'] for r in records)
    print(f'\nGold corpus: {len(records)} sentences, '
          f'{len([r for r in records if r["expected"]])} expected-valid / '
          f'{len([r for r in records if not r["expected"]])} expected-invalid.')
    if failed:
        print(f'\n!! REGRESSIONS ({len(failed)})')
        for r in failed:
            print(f'   {r["text"]!r}: expected '
                  f'{"grammatical" if r["expected"] else "ungrammatical"} '
                  f'but got {r["actual"]}  [{r["why"]}]  fired={r["fired"]}'
                  + (f'  checker_errors={r["checker_errors"]}'
                     if r.get('checker_errors') else ''))
    else:
        print('   all expected verdicts matched  [no false positives / no false negatives]')

    total_edges = sum(status_counter.values())
    print(f'\nEdges evaluated: {total_edges} -> '
          f'{status_counter.get("valid", 0)} valid / '
          f'{status_counter.get("error", 0)} error / '
          f'{status_counter.get("unlisted", 0)} unlisted')
    print(f'Distinct (parent, child) type pairs exercised: {len(edge_counter)}')

    # Rule / method coverage against docs/matrix.md
    registered = all_rule_ids()
    exercised = sorted(rule_counter, key=lambda r: tuple(int(p) for p in r.split('.'))
                       if r and r[0].isdigit() else (99,))
    print(f'\nRule-matrix coverage: {len(exercised)}/{len(registered)} registered rules '
          f'observed firing on the corpus.')
    print('   method breakdown of the checks that ran: '
          + ', '.join(f'{m}={method_counter[m]}' for m in ('T', 'L', 'C')))
    unexercised = [r for r in registered if r not in rule_counter]
    if unexercised:
        print(f'   rules not exercised by the gold corpus ({len(unexercised)}): '
              + ', '.join(unexercised))
    if suggestion_counter:
        print('   suggestions raised (C layer, non-blocking): '
              + ', '.join(f'{c} x{n}' for c, n in sorted(suggestion_counter.items())))

    print('\nEdge-coverage matrix (parent TYPE -> child TYPE : constraint)')
    rows = {}
    for (pt, ct), count in sorted(edge_counter.items()):
        rows.setdefault(pt, []).append((ct, count))
    for pt, children in rows.items():
        print(f'  [{pt}]')
        for ct, count in sorted(children):
            print(f'      -> {ct:<6} x{count}')

    if unlisted_edges:
        print(f'\n!! UNLISTED edge types ({len(unlisted_edges)}) - fall through to valid-by-default:')
        for pt, ct, constraint in sorted(unlisted_edges):
            print(f'   [{pt}] -> [{ct}] ({constraint})')
    else:
        print('\n   no unlisted edges - every edge type in the corpus hits a dedicated rule')

    return len(failed), len(unlisted_edges), total_edges, total_suggestions


def main() -> int:
    (records, edges, statuses, unlisted,
     suggestions, rules, methods) = run_corpus()
    failures, unrated, total, sug_total = report(
        records, edges, statuses, unlisted, suggestions, rules, methods)
    print(f'\nSUMMARY: gold regressions={failures}  unrated_edge_types={unrated}  '
          f'edges={total}  suggestions={sug_total}')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())