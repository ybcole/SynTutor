# Syntax Tree Learning Master Sheet

> Chronological + exhaustive: every part of SynTutor's analysis,
> in the order the pipeline produces it. 1:1 with the model.

*Generated 2026-10-18  •  48 POS tags  •  24 phrase nodes  •  111 rules  •  169 constraints*

---

## Stage 1: Tokenizer

*Engine: spaCy (en_core_web_md)*

Splits raw text into word tokens, keeping punctuation separate.

_Tokenization is implicit — every word below is a token._

## Stage 2: Part-of-speech tagger

*Engine: spaCy -> benepar leaves*

Tags every token with a lexical category (NN, VBZ, IN, ...). These become the leaves of the tree.

| Tag | Meaning | Example |
|-----|---------|---------|
| `CC` | Coordinating conjunction | and, but, or |
| `CD` | Cardinal number | one, 42, 1990 |
| `DT` | Determiner | the, a, an, this, some |
| `EX` | Existential there | There is a cat. |
| `FW` | Foreign word | bonjour, etc. |
| `IN` | Preposition / subordinating conjunction | in, of, that, if |
| `JJ` | Adjective | quick, happy |
| `JJR` | Adjective, comparative | quicker, happier |
| `JJS` | Adjective, superlative | quickest, happiest |
| `LS` | List item marker | 1., A. |
| `MD` | Modal | can, will, must, should |
| `NN` | Noun, singular / mass | cat, water, idea |
| `NNS` | Noun, plural | cats, ideas |
| `NNP` | Proper noun, singular | Alice, London |
| `NNPS` | Proper noun, plural | Americans, Beatles |
| `PDT` | Predeterminer | all the, both the |
| `POS` | Possessive ending | John's, the cat's |
| `PRP` | Personal pronoun | I, he, she, it, they |
| `PRP$` | Possessive pronoun | my, your, his, her, its, their |
| `RB` | Adverb | quickly, very, not |
| `RBR` | Adverb, comparative | quicker, more |
| `RBS` | Adverb, superlative | quickest, most |
| `RP` | Particle | up (give up), off (turn off) |
| `SYM` | Symbol | +, %, $, = |
| `TO` | to | to go, to eat |
| `UH` | Interjection | oh, wow, hey |
| `VB` | Verb, base form | go, be, run |
| `VBD` | Verb, past tense | went, was, ran |
| `VBG` | Verb, gerund / present participle | going, running |
| `VBN` | Verb, past participle | gone, run, written |
| `VBP` | Verb, non-3rd person singular present | go, run, are |
| `VBZ` | Verb, 3rd person singular present | goes, runs, is |
| `WDT` | Wh-determiner | which, that, whatever |
| `WP` | Wh-pronoun | who, whom, what |
| `WP$` | Possessive wh-pronoun | whose |
| `WRB` | Wh-adverb | when, where, how |
| `HYPH` | Hyphen | well-known |
| `#` | Pound sign | #10, #hashtag |
| `$` | Currency symbol | $5, €3 |
| `-NONE-` | Trace / empty category | (deleted filler) |
| `.` | Sentence-final punctuation | . ? ! |
| `,` | Comma | , |
| `:` | Colon / semicolon / dash | : ; - |
| `;` | Semicolon | ; run-on fix |
| `'` | Opening / closing quote | ' " |
| `"` | Double quote | "quoted" |
| `(` | Opening bracket | ( [ |
| `)` | Closing bracket | ) ] |

---

## Stage 3: Constituency parser

*Engine: benepar (benepar_en3)*

Groups tokens into phrase nodes (NP, VP, PP, ...) bottom-up until one root node spans the sentence.

| Tag | Meaning | Example |
|-----|---------|---------|
| `S` | Clause (sentence) | Subject + predicate: "The cat sat." |
| `NP` | Noun phrase | the big cat, a student of physics |
| `VP` | Verb phrase | is running, has eaten the cake |
| `PP` | Prepositional phrase | in the garden, of physics |
| `ADJP` | Adjective phrase | very happy, fond of music |
| `ADVP` | Adverb phrase | very quickly, in the morning |
| `SBAR` | Subordinate clause | because he left, which I saw |
| `SBARQ` | Direct question | What did you say? |
| `SINV` | Inverted clause | Never have I seen such a thing. |
| `SQ` | Yes/no question fragment | Is it raining? |
| `FRAG` | Fragment | Hello there. What a day! |
| `NML` | Nominalized expression | the rich, the young |
| `WHNP` | Wh-noun phrase | which book, who left |
| `WHADVP` | Wh-adverb phrase | when, where, how |
| `WHADJP` | Wh-adjective phrase | how tall, however old |
| `WHPP` | Wh-prepositional phrase | to whom, for what |
| `QP` | Quantifier phrase | more than five, about 20 |
| `NX` | Nominal expression | the man in black |
| `CONJP` | Conjunction phrase | but rather, as well as |
| `UCP` | Unlike-coordinated phrase | men and tigers |
| `LST` | List | 1. apples 2. pears |
| `INTJ` | Interjection node | Wow! Hey! |
| `PRT` | Particle node | give up, turn off |
| `X` | Unclassified | (unanalyzable material) |

---

## Stage 4: Rule matrix (SynTutor)

*Engine: server/matrix.py + server/licensing.py + server/ruleset.py*

SynTutor's own analysis: walks the tree and fires grammar constraints. Each maps to a numbered rule.

| Rule | Constraint | Name | Layer |
|------|-----------|------|-------|
| `1.1` | `C-PLURAL-FORM` | Regular noun plurals | T |
| `1.2` | `C-NOUN-FORM` | Irregular noun plurals | T |
| `1.3` | `C-POSSESSIVE-S` | Possessive ‘s / s’ | T |
| `1.4` | `C-VERB-ENDING` | Verb endings (-s, -ed, -ing) | T |
| `1.5` | `C-VERB-FORM` | Irregular past tense | T |
| `1.6` | `C-VBN-SIMPLE-PAST` | Irregular past participle | T |
| `1.7` | `C-COMPARATIVE-FORM` | Comparative/superlative formation | T |
| `1.8` | `C-ADVERB-FORM` | Adverb formation | T |
| `1.9` | `C-REFLEXIVE-FORM` | Reflexive forms | T |
| `1.10` | `C-HOMOPHONE` | Homophones (its/it’s, their/there) | T |
| `1.11` | `C-CONTRACTION` | Contractions | T |
| `1.12` | `C-LEXICON-MALFORMED` | Spelling | T |
| `1.12` | `C-LEXICON-TAG-MISMATCH` | Spelling | T |
| `1.12` | `C-LEXICON-UNKNOWN` | Spelling | T |
| `1.12` | `C-SPELLING` | Spelling | T |
| `1.13` | `C-NUMERAL` | Numerals and measures | T |
| `2.1` | `C-CLAUSE-SUBJECT` | Subject-verb, simple | T |
| `2.1` | `C-PREDICATE` | Subject-verb, simple | T |
| `2.1` | `C-SUBJECT-AGREEMENT` | Subject-verb, simple | T |
| `2.1` | `C-WAS-WERE` | Subject-verb, simple | T |
| `2.2` | `C-SUBJ-AGREE-XP` | Subject-verb across intervening phrase | T |
| `2.3` | `C-COORD-SUBJ-AGREE` | Coordinated subjects (and / or / nor) | T |
| `2.3` | `C-COORDINATOR` | Coordinated subjects (and / or / nor) | T |
| `2.4` | `C-EXISTENTIAL` | Existential there | T |
| `2.4` | `C-EXISTENTIAL-VERB` | Existential there | T |
| `2.5` | `C-COLLECTIVE` | Collective and notional nouns | T |
| `2.6` | `` | Questions and inversion | T |
| `2.7` | `C-NP-RELATIVE` | Relative clauses | T |
| `2.7` | `C-RELATIVE-AGREE` | Relative clauses | T |
| `2.7` | `C-RELATIVE-CLAUSE` | Relative clauses | T |
| `2.8` | `C-INDEF-AGREE` | Indefinite pronouns | T |
| `2.8` | `C-INDEFINITE-AGREE` | Indefinite pronouns | T |
| `2.9` | `C-NUMBER-AGREE` | Quantified subjects | T |
| `2.10` | `C-DETERMINER-AGREEMENT` | Determiner-noun number | T |
| `2.11` | `C-QUANTIFIER` | Quantifier-noun | T |
| `2.11` | `C-QUANTIFIER-CLASS` | Quantifier-noun | T |
| `2.12` | `C-PRON-ANTECEDENT` | Pronoun-antecedent | T |
| `2.13` | `C-CORRELATIVE-AGREE` | Correlatives | T |
| `2.14` | `C-REFLEXIVE-ANTECEDENT` | Reflexive-antecedent | T |
| `3.1` | `C-ARTICLE-MISMATCH` | a/an choice | T |
| `3.2` | `C-ARTICLE` | Missing article | T |
| `3.3` | `C-UNNECESSARY-ARTICLE` | Unnecessary article | T |
| `3.4` | `C-FIRST-MENTION` | Definite vs indefinite | T |
| `3.5` | `C-DET-STACK` | Stacked determiners | T |
| `3.6` | `C-DETERMINER` | Determiner with no noun | T |
| `3.6` | `C-HEAD-NOUN` | Determiner with no noun | T |
| `3.7` | `C-SOME-ANY` | some/any | T |
| `3.8` | `C-DET-NOUN-AGREE` | each/every/all/whole/other/another | T |
| `4.1` | `C-UNCOUNTABLE` | Countable vs uncountable | T |
| `4.2` | `C-NOUN-ADJUNCT` | Noun as modifier (number) | T |
| `4.2` | `C-NOUN-MODIFIER-NUMBER` | Noun as modifier (number) | T |
| `4.2` | `C-NP-COMPOUND` | Noun as modifier (number) | T |
| `4.3` | `C-PLURAL-ONLY` | Plural-only / singular -s nouns | T |
| `5.1` | `C-PREP-PRON-CASE` | Case, simple | T |
| `5.1` | `C-PRONOUN-CASE` | Case, simple | T |
| `5.2` | `C-COORD-CASE` | Case in coordination and comparison | T |
| `5.3` | `C-PRON-AMBIG` | Ambiguous reference | T |
| `5.4` | `C-RELATIVE-HEAD` | Relative pronoun choice | T |
| `5.4` | `C-RELATIVE-NOUN` | Relative pronoun choice | T |
| `5.4` | `C-RELATIVE-POSSESSIVE` | Relative pronoun choice | T |
| `5.4` | `C-RELATIVE-PRONOUN` | Relative pronoun choice | T |
| `5.5` | `C-DUMMY-IT` | Dummy it/there | T |
| `5.6` | `C-POSSESSIVE` | Possessive pronoun vs determiner | T |
| `5.7` | `C-REFLEXIVE-SUBJECT` | Reflexive vs ordinary pronoun | T |
| `6.1` | `C-AUX-COMPLEMENT` | Auxiliary + verb form | T |
| `6.1` | `C-AUX-FORM` | Auxiliary + verb form | T |
| `6.1` | `C-AUXILIARY` | Auxiliary + verb form | T |
| `6.1` | `C-MODAL-VERB-FORM` | Auxiliary + verb form | T |
| `6.2` | `C-HEAD-VERB` | Finite main verb | T |
| `6.2` | `C-TENSE-FINITE` | Finite main verb | T |
| `6.3` | `C-COPULA` | Missing verb / copula | T |
| `6.3` | `C-PLEASE-TO` | Missing verb / copula | T |
| `6.4` | `C-PASSIVE` | Passive formation | T |
| `6.5` | `C-INTRANSITIVE-PASSIVE` | Intransitive passive | T |
| `6.6` | `C-STATIVE-PROG` | Stative verbs in progressive | T |
| `6.6` | `C-STATIVE-PROGRESSIVE` | Stative verbs in progressive | T |
| `6.7` | `C-TENSE-CONSISTENCY` | Tense consistency | T |
| `6.8` | `C-TRANSITIVITY` | Transitivity | T |
| `6.9` | `C-GERUND-INFIN` | Gerund vs infinitive | T |
| `6.9` | `C-GERUND-INFINITIVE` | Gerund vs infinitive | T |
| `6.10` | `C-INFINITIVAL-COMPLEMENT` | to + base form | T |
| `6.10` | `C-INFINITIVAL-MARKER` | to + base form | T |
| `6.10` | `C-TO-BASE` | to + base form | T |
| `6.11` | `C-PARTICLE` | Phrasal verbs | T |
| `6.11` | `C-PHRASAL-ORDER` | Phrasal verbs | T |
| `6.12` | `C-MODAL-STACK` | Modals and semi-modals | T |
| `6.12` | `C-MODAL-TO` | Modals and semi-modals | T |
| `6.13` | `C-QUESTION-INVERSION` | Question formation | T |
| `6.14` | `C-DOUBLE-NEGATIVE` | Negation | T |
| `6.15` | `C-IMPERATIVE-VERB` | Imperatives | T |
| `6.16` | `C-CONDITIONAL-WILL` | Conditionals | T |
| `6.17` | `C-SUBJUNCTIVE` | Subjunctive and wish | T |
| `6.18` | `C-REPORTED-SPEECH` | Reported speech | T |
| `6.19` | `C-CAUSATIVE-TO` | Causatives and perception verbs | T |
| `6.20` | `C-CLAUSAL-COMPLEMENT` | Verb + clause patterns | T |
| `6.20` | `C-VERB-CLAUSE-PATTERN` | Verb + clause patterns | T |
| `7.1` | `C-ADJ-ADV` | Adjective vs adverb | T |
| `7.1` | `C-HEAD-ADJECTIVE` | Adjective vs adverb | T |
| `7.1` | `C-PREDICATE-ADJECTIVE` | Adjective vs adverb | T |
| `7.1` | `C-SMALL-CLAUSE-PREDICATE` | Adjective vs adverb | T |
| `7.2` | `C-ADJ-ORDER` | Adjective order | T |
| `7.3` | `C-ADVERB-PLACEMENT` | Adverb placement | T |
| `7.3` | `C-ADVERBIAL` | Adverb placement | T |
| `7.3` | `C-ADVERBIAL-COMPLEMENT` | Adverb placement | T |
| `7.3` | `C-HEAD-ADVERBIAL` | Adverb placement | T |
| `7.4` | `C-PARTICIPIAL` | Participial adjectives | T |
| `7.4` | `C-PARTICIPIAL-ADJ` | Participial adjectives | T |
| `7.4` | `C-PARTICIPLE-MODIFIER` | Participial adjectives | T |
| `7.5` | `C-INTENSIFIER` | Intensifiers and degree | T |
| `7.6` | `C-COMPARATIVE-DOUBLE` | Comparative structures | T |
| `7.6` | `C-COMPARATIVE-STRUCT` | Comparative structures | T |
| `7.7` | `C-MOD-POS` | Modifier position | T |
| `7.7` | `C-NP-POSTMODIFIER` | Modifier position | T |
| `8.1` | `C-HEAD-PREPOSITION` | Wrong preposition | T |
| `8.1` | `C-PREP-CHOICE` | Wrong preposition | T |
| `8.1` | `C-WRONG-PREPOSITION` | Wrong preposition | T |
| `8.2` | `C-MISSING-PREP` | Missing preposition | T |
| `8.3` | `C-EXTRA-PREP` | Unnecessary preposition | T |
| `8.4` | `C-ADJ-PREP` | Adjective + preposition | T |
| `8.5` | `C-ADJUNCT` | Time and place (in/on/at) | T |
| `8.5` | `C-PREP-OBJECT` | Time and place (in/on/at) | T |
| `8.5` | `C-TIME-PLACE-PREP` | Time and place (in/on/at) | T |
| `8.6` | `C-PREP-GERUND` | Preposition + gerund | T |
| `9.1` | `C-FRAGMENT` | Fragment | T |
| `9.1` | `C-ROOT` | Fragment | T |
| `9.2` | `C-MISSING-SUBJECT` | Missing subject | T |
| `9.3` | `C-RUNON` | Run-on / fused sentence | T |
| `9.4` | `C-COMMA-SPLICE` | Comma splice | T |
| `9.5` | `C-DOUBLE-SUBJECT` | Double subject | T |
| `9.6` | `C-WORD-ORDER` | Word order in statements | T |
| `9.7` | `C-EXTRA-WORD` | Missing or extra word | T |
| `9.8` | `C-MISPLACED-MODIFIER` | Parallel structure | T |
| `9.8` | `C-PARALLEL` | Parallel structure | T |
| `9.9` | `C-CONJUNCTION-PAIR` | Conjunction pairing | T |
| `9.10` | `C-NP-REDUCED-RELATIVE` | Relative clause formation | T |
| `9.10` | `C-RESUMPTIVE-RELATIVE` | Relative clause formation | T |
| `9.11` | `C-DANGLING` | Dangling / misplaced modifier | T |
| `9.12` | `C-REDUNDANCY` | Redundancy | T |
| `9.13` | `C-INDIRECT-Q-ORDER` | Indirect question word order | T |
| `9.13` | `C-INDIRECT-WH-INVERSION` | Indirect question word order | T |
| `9.14` | `C-CLAUSAL-ADVERBIAL` | Clause linking | T |
| `9.14` | `C-CLAUSE-LINKING` | Clause linking | T |
| `9.14` | `C-CLAUSE-PREDICATE` | Clause linking | T |
| `9.14` | `C-COMPLEMENTIZER` | Clause linking | T |
| `9.15` | `C-DIRECT-OBJECT` | Object order | T |
| `9.15` | `C-OBJECT-ORDER` | Object order | T |
| `9.15` | `C-SMALL-CLAUSE` | Object order | T |
| `10.1` | `C-CAPITALIZATION` | Sentence-initial capital | T |
| `10.1` | `C-SENTENCE-CAPITAL` | Sentence-initial capital | T |
| `10.2` | `C-COMMA-OMISSION` | Proper nouns, “I”, days, months | T |
| `10.2` | `C-PROPER-NOUN` | Proper nouns, “I”, days, months | T |
| `10.3` | `C-TERMINAL-PUNCT` | Terminal punctuation | T |
| `10.4` | `C-INTRO-COMMA` | Commas | T |
| `10.5` | `C-APOSTROPHE` | Apostrophes | T |
| `10.6` | `C-QUOTATION` | Quotation and dialogue | T |
| `10.7` | `C-HYPHEN` | Hyphens and dashes | T |
| `10.8` | `C-PUNCT` | Colons and semicolons | T |
| `10.9` | `C-SPACING-REPEAT` | Spacing and repeats | T |
| `10.10` | `C-NUMERAL-FORMAT` | Numbers, dates, abbreviations | T |
| `11.1` | `C-CONFUSABLE` | Confusable words | T |
| `11.2` | `C-COLLOCATION` | Collocations | T |
| `11.3` | `C-TENSE-SINCE` | Tense-time agreement | T |
| `11.3` | `C-TENSE-TIME` | Tense-time agreement | T |
| `11.4` | `C-SELECTIONAL` | Selectional restrictions | T |
| `11.5` | `C-PP-ATTACH` | Structural ambiguity | T |
| `11.6` | `C-REGISTER` | Register | T |
| `11.7` | `C-L1-INTERFERENCE` | L1 interference / false friends | T |
| `11.8` | `C-CONNECTOR` | Connector misuse | T |
| — | `C-UNLISTED` | — | T |

---
