Check method key: T = tree rule (deterministic over the parse), L = word list or morphology (deterministic), C = needs context or meaning (normally a suggestion; a high-confidence contradiction may be invalid).
1. Word forms
ID        Rule        Example error        Check
1.1        Regular noun plurals        boxs        L
1.2        Irregular noun plurals        childs        L
1.3        Possessive ‘s / s’        the boys toy        T
1.4        Verb endings (-s, -ed, -ing)        runing        L
1.5        Irregular past tense        goed        L
1.6        Irregular past participle        had went        L
1.7        Comparative/superlative formation        gooder, more tall        L
1.8        Adverb formation        happyly        L
1.9        Reflexive forms        hisself        L
1.10        Homophones (its/it’s, their/there)        Its raining        T+L
1.11        Contractions        dont        L
1.12        Spelling        recieve        L
1.13        Numerals and measures        two hundreds        L
2. Agreement
ID        Rule        Example error        Check
2.1        Subject-verb, simple        The boy go        T
2.2        Subject-verb across intervening phrase        The boy with the bags go        T
2.3        Coordinated subjects (and / or / nor)        Tom or Ann are        T
2.4        Existential there        There is books        T
2.5        Collective and notional nouns        The team are        C
2.6        Questions and inversion        Where is the books?        T
2.7        Relative clauses        the boys who plays        T
2.8        Indefinite pronouns        Everyone have        T+L
2.9        Quantified subjects        A number of / Each of the boys are        T+L
2.10        Determiner-noun number        these book        T
2.11        Quantifier-noun        less books, much books        T+L
2.12        Pronoun-antecedent        The girls lost her bag        C
2.13        Correlatives        Either he or I am        T
2.14        Reflexive-antecedent        She hurt himself        T
3. Articles and determiners
ID        Rule        Example error        Check
3.1        a/an choice        a apple        L
3.2        Missing article        I saw dog        T+L
3.3        Unnecessary article        She plays the football        C
3.4        Definite vs indefinite        I saw the dog (first mention)        C
3.5        Stacked determiners        the my book        T
3.6        Determiner with no noun        the my        T
3.7        some/any        I don’t have some money        T+L
3.8        each/every/all/whole/other/another        another books        T+L
4. Nouns
ID        Rule        Example error        Check
4.1        Countable vs uncountable        informations, an advice        L
4.2        Noun as modifier (number)        a ten-years plan        T+L
4.3        Plural-only / singular -s nouns        a scissors, the news are        L
5. Pronouns
ID        Rule        Example error        Check
5.1        Case, simple        Me go, between you and I        T
5.2        Case in coordination and comparison        Me and him went, taller than I        T
5.3        Ambiguous reference        Tom told Jim he...        C
5.4        Relative pronoun choice        the man which        T+L
5.5        Dummy it/there        Is raining        T
5.6        Possessive pronoun vs determiner        This is my        T+L
5.7        Reflexive vs ordinary pronoun        Myself am happy        T
6. Verbs
ID        Rule        Example error        Check
6.1        Auxiliary + verb form        She can goes        T
6.2        Finite main verb        She going to school        T
6.3        Missing verb / copula        She very happy        T
6.4        Passive formation        The house build        T
6.5        Intransitive passive        It was happened        L
6.6        Stative verbs in progressive        I am knowing        L
6.7        Tense consistency        He said he will come        C
6.8        Transitivity        discuss about, arrived the station        L
6.9        Gerund vs infinitive        enjoy to swim        L
6.10        to + base form        to goes        T
6.11        Phrasal verbs        pick up it        L
6.12        Modals and semi-modals        must to go, use to go        T+L
6.13        Question formation        Where you are going?        T
6.14        Negation        I don’t have no money        T+L
6.15        Imperatives        Don’t goes        T
6.16        Conditionals        If I will go        T
6.17        Subjunctive and wish        I wish I was        C
6.18        Reported speech        She said me        T+C
6.19        Causatives and perception verbs        made me to cry        T+L
6.20        Verb + clause patterns        suggest him to go        L
7. Adjectives and adverbs
ID        Rule        Example error        Check
7.1        Adjective vs adverb        runs quick        T+L
7.2        Adjective order        red big car        L
7.3        Adverb placement        I like very much it        T+L
7.4        Participial adjectives        I am boring        L
7.5        Intensifiers and degree        enough big, too much good        T+L
7.6        Comparative structures        more taller, as tall than        T+L
7.7        Modifier position        the car red        T
8. Prepositions
ID        Rule        Example error        Check
8.1        Wrong preposition        depends in        C
8.2        Missing preposition        listen music        C
8.3        Unnecessary preposition        discuss about        L
8.4        Adjective + preposition        interested on        L
8.5        Time and place (in/on/at)        on 5 pm        L+C
8.6        Preposition + gerund        look forward to see        T+L
9. Sentence structure
ID        Rule        Example error        Check
9.1        Fragment        Because I was late.        T
9.2        Missing subject        Went to school.        T
9.3        Run-on / fused sentence        I like tea she likes coffee        T+C
9.4        Comma splice        I came, I saw.        T
9.5        Double subject        My brother he...        T
9.6        Word order in statements        Yesterday went I        T
9.7        Missing or extra word        She is very the happy        C
9.8        Parallel structure        to run, swimming        T
9.9        Conjunction pairing        Although..., but...        L
9.10        Relative clause formation        the man who I saw him        T
9.11        Dangling / misplaced modifier        Walking home, the rain started        C
9.12        Redundancy        return back        L
9.13        Indirect question word order        I wonder where is he        T
9.14        Clause linking        because to see you        T
9.15        Object order        gave to me a book        T+L
10. Punctuation and orthography
ID        Rule        Example error        Check
10.1        Sentence-initial capital        the boy runs        T
10.2        Proper nouns, “I”, days, months        i am, monday        L
10.3        Terminal punctuation        missing period/question mark        T
10.4        Commas        series, introductory, clauses        T+C
10.5        Apostrophes        the 1990’s        T
10.6        Quotation and dialogue        mismatched marks        T
10.7        Hyphens and dashes        a well known author        C
10.8        Colons and semicolons        misuse        T+C
10.9        Spacing and repeats        the the, space before comma        T
10.10        Numbers, dates, abbreviations        inconsistent format        L
11. Meaning and usage (semantic layer)
ID        Rule        Example error        Check
11.1        Confusable words        affect/effect, lose/loose        C
11.2        Collocations        do a decision        C
11.3        Tense-time agreement        Yesterday I go        C
11.4        Selectional restrictions        The book eats        C
11.5        Structural ambiguity        PP-attachment        C
11.6        Register        slang in formal writing        C
11.7        L1 interference / false friends        I am agree        C
11.8        Connector misuse        I was tired, however I slept        C

Type        App looks at        Example error        Reliable?
T        The tree’s structure        The boy go        Yes, always the same answer
L        A word list        goed        Yes, if the list is complete
C        Meaning and context        the dog (first mention)        Usually a suggestion; high-confidence contradictions may be invalid

that table is the backbone of the XAI (explainable AI) layer, because the check method decides what the explanation can honestly show. In XAI, a good explanation shows the actual evidence the decision used, not a story written afterwards. Each type uses different evidence.
Type        Evidence the decision used        What the explanation shows
T        Specific nodes and edges in the tree        The highlighted subtree, the rule that fired, and the two nodes in conflict (e.g. the boy [singular] vs go [plural form])
L        A specific entry in a word list        The list lookup: “go → past tense went; goed is not in the accepted forms”
C        Context cues and a judgment, not a fixed rule        The condition, evidence, and confidence; label uncertain cases as suggestions
