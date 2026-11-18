# SynTutor Linguistic Dictionary

Canonical definition registry for the linguistic terms used by the Syntax Foundations reader and the Cambridge grammar lessons. The hover dictionary in both lesson books uses these definitions; term pop-ups show the definition only and no longer include a lesson link.

## Coverage and honesty

- **577 codified terms** were collected from the existing source glossaries and lesson key-term lists: 215 Foundations glossary/key-term rows and 533 Cambridge chapter key-term rows, deduplicated to 577 unique terms.
- **33 tree-notation terms** (S, NP, VP, NOM, DET, C1/C2, features such as `trans` and `-tense`, and similar) were added because they are used in the trees and explanations but are not all listed as lesson key terms.
- The file therefore contains **610 entries** in total.
- Definitions are taken from the existing Foundations and Cambridge source definitions, not invented for this file. Where both books define a term, the Foundations gloss is preferred for classroom consistency.
- **This is exhaustive for the codified glossary/key-term inventory, not for every word in every lesson.** It does not attempt to list proper names, example sentences, one-off vocabulary, or prose terms that never became a glossary/key-term entry. Those are the known exclusions.
- If a term is used in a lesson but is missing here, treat that as a coverage bug to report, not as evidence that the term has no definition.

## Source and maintenance

- This file is the definition source. `npm run dictionary:build` regenerates `web/js/linguistic-dictionary.js` from this markdown, and `npm run dictionary:audit` verifies that every runtime glossary term and alias is represented here.
- Foundations sources: `web/js/foundations-glossary.js` and `web/js/lesson-key-terms.js`.
- Cambridge sources: `key_terms` in `web/content/lessons/course.json`.
- Tree notation sources: `CONVENTIONS.md` and `server/final_d1_projection.py`.
- The hover feature shows the definition only; lesson links were removed from the pop-up.

## Dictionary

### -

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **-tense** | Non-finite feature marking a clause or verb form that carries no finite tense. |  | Tree notation (SynTutor FINAL-D1) |

### A

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **abbreviation full stop** | A full stop marking an abbreviation, as in Col. Blimp. |  | Cambridge Ch20 |
| **absolute negator** | A negator meaning zero or none, such as no, none, never, neither or nor. |  | Cambridge Ch9 |
| **absolute superlative** | A superlative use expressing a very high degree without comparison to a set. |  | Cambridge Ch13 |
| **accent** | How speech sounds are pronounced. |  | Cambridge Ch1 |
| **act-related** | An adjunct that evaluates or qualifies the act performed rather than its manner. |  | Cambridge Ch8 |
| **addressee-old** | Information the speaker assumes the addressee already knows. |  | Cambridge Ch16 |
| **adjectival passive** | A passive-like form functioning as an adjective, often describing a state. |  | Cambridge Ch16 |
| **adjectivalisation** | The formation of an adjective from another base. |  | Cambridge Ch19 |
| **Adjective** | A word that can describe a noun or give a property in a predicate, as “bright” does in “the sign was bright”. | adjectives | Foundations Ch3, Cambridge Ch6 |
| **Adjective phrase** | A phrase headed by an adjective, such as “very bright”. | adjective phrases, AP, APs | Foundations Ch3, Cambridge Ch6 |
| **Adjective phrase (AP)** | A phrase headed by an adjective. It can consist of the adjective alone or include words that modify or complete it. |  | Foundations br-03 |
| **Adjunct** | An optional modifier that can add a detail such as time, place, or manner. | adjuncts, adjunct adverbial, adjunct adverbials | Foundations Ch5, Foundations br-05, Foundations cgel-ch04, Cambridge Ch2, Cambridge Ch4, Cambridge Ch6, Cambridge Ch7, Cambridge Ch8 |
| **Adverb** | A word that can add information about a verb, adjective, or other expression, as “quietly” does in “spoke quietly”. | adverbs, Adv | Foundations Ch3, Cambridge Ch6 |
| **Adverb phrase** | A phrase headed by an adverb, such as “quite clearly”. | adverb phrases, AdvP, AdvPs | Foundations Ch3, Cambridge Ch6 |
| **Adverbial** | A function that can show when, where, or how something happens, or apply to a whole statement. | adverbials | Foundations Ch5 |
| **Adverbial clause** | A clause that contributes information such as time, reason, or condition. | adverbial clauses | Foundations Ch8 |
| **AdvP** | Adverb phrase: a phrase headed by an adverb. |  | Tree notation (SynTutor FINAL-D1) |
| **affix** | A bound morpheme attached to a base, either as a prefix or suffix. |  | Cambridge Ch19 |
| **affixal negation** | Negation marked by a prefix or suffix, such as un-, non- or -less. |  | Cambridge Ch9 |
| **agent** | The prototypical conscious causer of an action. |  | Cambridge Ch4 |
| **agreement** | The relation that gives us forms such as the box is and the boxes are. |  | Foundations cgel-ch05, Cambridge Ch5 |
| **alternation** | Different realisations of a morphological unit depending on context. |  | Cambridge Ch18 |
| **alternative question** | A question offering a stated set of alternatives. |  | Cambridge Ch10 |
| **analytic comparative** | A comparative formed with more or less rather than an inflection. |  | Cambridge Ch13, Cambridge Ch18 |
| **analytic negation** | Negation marked by a dedicated negative word such as not or no. |  | Cambridge Ch9 |
| **anaphor** | An expression interpreted through an antecedent. |  | Cambridge Ch17 |
| **anaphora** | The relation in which an expression receives its interpretation from an antecedent. |  | Cambridge Ch2, Cambridge Ch17 |
| **anaphoric not** | Not used as a pro-form for a negative clause, as in I think not. |  | Cambridge Ch9 |
| **anaphoric so** | So used as a pro-form for a clause or proposition. |  | Cambridge Ch17 |
| **anchor** | The expression, person, thing or situation a supplement comments on. |  | Foundations cgel-ch15, Cambridge Ch15 |
| **antecedent** | An expression that supplies the interpretation for another expression, as doors supplies the noun understood in the red one. |  | Foundations cgel-ch17, Cambridge Ch12, Cambridge Ch17 |
| **antecedent-contained deletion** | A construction in which an elided VP is interpreted through an antecedent containing the elided material. |  | Cambridge Ch12 |
| **anticipatory anaphora** | Anaphora in which the anaphor precedes its antecedent. |  | Cambridge Ch17 |
| **AP** | Adjective phrase: a phrase headed by an adjective. |  | Tree notation (SynTutor FINAL-D1) |
| **apodosis** | The matrix clause expressing the consequence in a conditional construction. |  | Cambridge Ch8 |
| **apostrophe** | A word-internal mark used for omission or the genitive. |  | Cambridge Ch20 |
| **appositive** | A supplement that characterises or identifies an anchor, as in my friend, a doctor. |  | Cambridge Ch15 |
| **appositive modifier** | A modifier that adds a characterisation of the head without restricting its reference. |  | Cambridge Ch5 |
| **approximate negator** | A word located towards the negative end of a scale, such as few, hardly or rarely. |  | Cambridge Ch9 |
| **ascriptive** | A use of be that ascribes a property to the subject. |  | Cambridge Ch4 |
| **aspect** | A grammatical system concerned with the internal temporal structure of a situation. |  | Cambridge Ch3 |
| **aspectuality** | The meaning side of aspect: how a situation is viewed internally or as a whole. |  | Cambridge Ch3 |
| **asyndetic** | Coordination without an overt coordinator. |  | Cambridge Ch15, Cambridge Ch20 |
| **Attachment** | The point in a tree where a group joins the structure, showing what it belongs with. | VP attachment, adjunct attachment | Foundations Ch5 |
| **attributive** | The function of an adjective phrase used as a pre-head modifier inside a nominal. |  | Cambridge Ch6 |
| **attributive VP** | A verb phrase used before a noun that does not constitute a full non-finite clause. |  | Cambridge Ch14 |
| **attributive-only adjective** | An adjective restricted to attributive function, such as former or mere. |  | Cambridge Ch6 |
| **AUX** | Auxiliary: a helping verb such as be, have, do, or a modal; it heads its own VP and takes a VP complement. |  | Tree notation (SynTutor FINAL-D1) |
| **auxiliary** | A verb that can fill special grammatical roles, such as carrying negation or appearing before the subject in a question. |  | Foundations cgel-ch03 |
| **auxiliary reduction** | The shortening of a form such as are to ’re and its attachment to the preceding word. |  | Foundations cgel-ch01 |
| **auxiliary stranding** | Use of an auxiliary alone as a reduced predicate, as in I could. |  | Cambridge Ch17 |
| **Auxiliary verb** | A helping verb that builds a chain with another verb and can express information such as tense or aspect. | auxiliary verbs, auxiliary, auxiliaries | Foundations Ch6, Cambridge Ch2, Cambridge Ch3 |

### B

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **back-formation** | The creation of a word by removing an affix from an existing word, as in edit from editor. |  | Cambridge Ch19 |
| **backshift** | A tense choice in an embedded report that takes the original occasion of speaking as a reference point. |  | Foundations cgel-ch03, Cambridge Ch3, Cambridge Ch11 |
| **bare coordinate** | The coordinate without its coordinator or modifying material. |  | Cambridge Ch15 |
| **bare declarative** | A declarative content clause without that. |  | Cambridge Ch11 |
| **bare infinitival** | An infinitival with a plain-form verb and without the marker to. |  | Foundations cgel-ch14, Cambridge Ch14 |
| **Bare infinitive** | The base form of a verb used without infinitival “to”, as “wait” is in “made them wait”. | bare infinitives | Foundations Ch10 |
| **bare relative** | A non-wh relative with no relative word or that. |  | Cambridge Ch12 |
| **base** | The form to which a suffix is attached, such as fit in fitted. |  | Foundations cgel-ch18, Cambridge Ch19 |
| **base plural** | A plural identical in form to the lexical base, as in sheep. |  | Cambridge Ch18 |
| **Basic verb phrase** | The lexical verb and the complements it takes in that use. | basic VP, basic VPs, lexical VP, lexical VPs | Foundations Ch4 |
| **biased question** | A question that conveys an expectation or preference about the answer. |  | Cambridge Ch10 |
| **binary coordination** | A coordination with two coordinates. |  | Cambridge Ch15 |
| **blending** | The fusion of parts of two words, as in smoke and fog → smog. |  | Cambridge Ch19 |
| **bound base** | A base that cannot stand alone as a word, such as dur- in durable. |  | Cambridge Ch19 |
| **bounding** | Presenting a situation as having a terminal point or complete extent. |  | Cambridge Ch8 |
| **by phrase** | The optional PP in a passive that expresses the internalised agent. |  | Cambridge Ch16 |

### C

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **C** | The front position under S′. It can contain a complementiser, or a fronted auxiliary in a question. |  | Foundations Ch8 |
| **C1** | The lower front position. A fronted tensed auxiliary can occupy it in a main wh-question. |  | Foundations Ch9, Foundations br-09 |
| **C2** | The higher front position where a fronted wh-expression appears. |  | Foundations Ch9, Foundations br-09 |
| **canonical clause** | A basic positive declarative active main clause that is not coordinated. |  | Cambridge Ch2 |
| **canonical counterpart** | The syntactically more basic version of an information-packaging construction. |  | Cambridge Ch16 |
| **capitalisation** | The use of upper-case letters for sentence beginnings, proper names or emphasis. |  | Cambridge Ch20 |
| **case** | The grammatical marking of a pronoun or NP for functions such as subject, object or possessor. |  | Cambridge Ch5 |
| **Category** | The kind of word or phrase something is, such as a noun phrase (NP) or a verb phrase (VP). |  | Foundations br-02 |
| **catenative complement** | A non-finite complement that cannot be reduced to an object, predicative complement or PP complement. |  | Cambridge Ch2, Cambridge Ch14 |
| **catenative construction** | A construction in which a verb takes a non-finite complement, often recursively. |  | Cambridge Ch14 |
| **catenative verb** | A verb that takes a non-finite clause complement, often in a recursive chain. |  | Cambridge Ch3, Cambridge Ch14 |
| **character** | A graphical shape used to realise one or more punctuation indicators. |  | Cambridge Ch20 |
| **Clausal complement** | An embedded clause that fills a role made available by a head, such as “that the gate shut” after “said”. | clausal complements, clause complement, clause complements | Foundations Ch8 |
| **clausal coordination** | Coordination of clauses. |  | Cambridge Ch15 |
| **clausal negation** | Negation that makes the whole clause negative. |  | Cambridge Ch9 |
| **Clausal subject** | A clause that fills the subject role in a larger clause. | clausal subjects | Foundations Ch8 |
| **Clause** | A grammatical unit built around a predicate. It often has a subject of its own. | clauses | Foundations Ch8, Foundations cgel-clauses, Cambridge Ch2 |
| **clause type** | The grammatical system whose major terms are declarative, closed interrogative, open interrogative, exclamative and imperative. |  | Cambridge Ch10 |
| **clause-oriented adjunct** | An adjunct that modifies the clause’s applicability, such as evaluation or modality. |  | Cambridge Ch6 |
| **cleft relative** | The relative clause following the foregrounded element in an it-cleft. |  | Cambridge Ch12 |
| **clipping** | The shortening of a word without changing its meaning, as in advertisement → ad. |  | Cambridge Ch19 |
| **clitic** | A reduced form attached prosodically to a neighbouring word. |  | Cambridge Ch18 |
| **closed interrogative** | A question clause with a limited set of answers, typically yes or no. |  | Foundations cgel-ch10, Cambridge Ch10 |
| **Co-indexing** | Using the same index in a tree to show that two positions are related. | co-index, co-indexed, coindexing | Foundations Ch10 |
| **collective noun** | A singular noun denoting a group, which may take singular or plural agreement. |  | Cambridge Ch5 |
| **Combination rule** | An instruction that specifies which units can combine and how the resulting structure is grouped. |  | Foundations br-11 |
| **combining form** | A bound base of classical origin used in compounds, such as electro-. |  | Cambridge Ch19 |
| **common noun** | A noun such as doctor or city that is not specialised to naming a particular entity. |  | Cambridge Ch5 |
| **comparative** | The grade form used to compare two or more entities, as in happier or more useful. |  | Cambridge Ch6 |
| **comparative clause** | The clause in a comparison such as than it was or as it is wide, with part of its interpretation supplied by the larger construction. |  | Foundations cgel-ch13, Cambridge Ch13 |
| **comparative form** | The inflectional or analytic form marking scalar superiority, as in bigger or more useful. |  | Cambridge Ch13 |
| **comparative governor** | The expression that licenses a comparative complement, such as more, less, as or than. |  | Cambridge Ch13 |
| **comparative phrase** | The phrase containing the comparative marker and its complement or modifier. |  | Cambridge Ch13 |
| **comparison** | A construction relating two or more things or quantities on a scale or by identity and likeness. |  | Cambridge Ch13 |
| **comparison set** | The group of things or occasions a ranking is made over. |  | Foundations cgel-ch13, Cambridge Ch13 |
| **Complement** | A word or group that fills a role its head makes available in a particular use. | complements, head–complement relation, head-complement relation | Foundations Ch2, Foundations br-05, Foundations cgel-ch04, Cambridge Ch1, Cambridge Ch2, Cambridge Ch4, Cambridge Ch6, Cambridge Ch7, Cambridge Ch8 |
| **complement clause** | A clause functioning as the complement of a preposition or other head. |  | Cambridge Ch7 |
| **Complementiser** | A word that introduces a subordinate clause, such as “that” in a report or “whether” in an embedded question. | complementisers, complementizer, complementizers | Foundations Ch8 |
| **Complementiser (C)** | A word such as “that” or “whether” that introduces a subordinate clause. C labels its position in the tree. |  | Foundations br-08 |
| **complex** | Complex-transitive frame: the verb takes an object plus an object-predicative complement. |  | Tree notation (SynTutor FINAL-D1) |
| **complex catenative** | A catenative construction with an intervening NP between the matrix and subordinate verbs. |  | Cambridge Ch14 |
| **complex relative phrase** | A relative phrase containing more than the relative word itself, such as whose house or with which. |  | Cambridge Ch12 |
| **Complex transitive verb** | A verb used with a direct object and an object predicative. | complex transitive verbs, complex transitive, V [complex], [complex] | Foundations Ch4 |
| **complex word** | A word analysable into smaller morphological units. |  | Cambridge Ch19 |
| **compound** | A word formed from two or more bases, as in passer-by. |  | Foundations cgel-ch19, Cambridge Ch19 |
| **compound noun** | A lexical unit made of two or more bases functioning as a single noun. |  | Cambridge Ch5 |
| **concealed passive** | A gerund-participial complement with a passive meaning, as in The house needs painting. |  | Cambridge Ch14 |
| **concession** | A contrast in which a circumstance might lead one to expect the opposite of the main clause. |  | Cambridge Ch8 |
| **conditional** | A construction in which one situation is presented as dependent on another. |  | Cambridge Ch8 |
| **Conjunct** | One of the words or groups joined by a coordinator such as “and”. | conjuncts | Foundations Ch3 |
| **Conjunct adverbial** | A link such as “however” between a statement and its context. | conjunct adverbials | Foundations Ch5 |
| **connective** | An adjunct that links a clause to the surrounding discourse. |  | Cambridge Ch8 |
| **connective adjunct** | An expression such as however that links a clause’s meaning to surrounding text. |  | Foundations cgel-ch20, Cambridge Ch20 |
| **connective adverb** | An adverb such as however or therefore that links clauses or sentences. |  | Cambridge Ch15 |
| **consonant doubling** | Doubling of a final consonant before a suffix, as in batting. |  | Cambridge Ch18 |
| **Constituency test** | A check for whether words form a unit, using evidence such as movement, replacement, omission, or answers to questions. | constituency tests, constituent test, constituent tests | Foundations Ch1 |
| **Constituent** | A word or group that works as a unit within a larger expression. | constituents | Foundations Ch1, Foundations br-01, Cambridge Ch1 |
| **constituent structure** | The hierarchical organisation of bases and affixes within a complex word. |  | Cambridge Ch19 |
| **content clause** | A clause such as the siren rang, which can serve as a complement inside a larger construction. |  | Foundations cgel-ch07, Cambridge Ch2, Cambridge Ch11 |
| **contraction** | A reduced form written with an apostrophe, as in you’re for you are. |  | Foundations cgel-ch01 |
| **control** | The interpretation of an understood subject through another expression in the construction. |  | Cambridge Ch14 |
| **Controller** | A word or group that identifies who or what is understood as the subject of a smaller clause. | controllers, subject control, object control | Foundations Ch10 |
| **conversion** | A change of word class without a change of form, as in Google → to google. |  | Cambridge Ch19 |
| **coordinate** | One member of a pair or series joined at the same structural level. |  | Foundations cgel-ch15, Cambridge Ch15 |
| **coordinated subject** | One subject made up of coordinated expressions, as in Maya and you. |  | Foundations cgel-ch01 |
| **Coordination** | Joining words, phrases, or clauses, often with a coordinator such as “and” or “or”. | coordinator, coordinators, coordinate phrase, coordinate phrases | Foundations Ch3, Foundations cgel-clauses, Cambridge Ch2, Cambridge Ch15 |
| **coordinator** | A linking word such as and, or or but that marks a coordinate. |  | Cambridge Ch15 |
| **Copula** | A linking verb such as “be” in “the lamp is bright”, where the complement describes the subject. | copulas, copular verb, copular verbs | Foundations Ch4 |
| **copular clause** | A complex-intransitive clause whose predicative complement is related to the subject by be or a similar verb. |  | Cambridge Ch4 |
| **core complement** | A complement directly related to the verb and prototypically realised by an NP or AdjP. |  | Cambridge Ch4 |
| **correlative comparative** | The construction the more ..., the merrier, with paired comparative phrases. |  | Cambridge Ch13 |
| **correlative coordination** | Coordination with paired markers such as both ... and or either ... or. |  | Cambridge Ch15 |
| **count and mass uses** | Count uses treat things as individual units. Mass uses present material or a collection without counting units directly. |  | Foundations cgel-ch05 |
| **Count noun** | A noun that can be counted in its current use, as in “one lamp” and “two lamps”. | count nouns | Foundations Ch3, Cambridge Ch5 |
| **counterpart** | A clause differing from another on one dimension while keeping the rest constant. |  | Cambridge Ch2 |
| **Covert subject** | A subject understood even though its words are unspoken. | covert subjects, silent subject, silent subjects, understood subject, understood subjects | Foundations Ch10 |

### D

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **dash** | A punctuation indicator used for interruption, supplement or range. |  | Cambridge Ch20 |
| **declarative** | The default clause type, lacking the special properties of the other major types. |  | Cambridge Ch10 |
| **declarative content clause** | A content clause with declarative clause type. |  | Cambridge Ch11 |
| **defective lexeme** | A lexeme lacking some inflectional forms found in its category. |  | Cambridge Ch18 |
| **definiteness** | The grammatical marking associated with identifiable or familiar referents. |  | Cambridge Ch5 |
| **degree** | How far a quality or activity reaches, as in bright enough. |  | Foundations cgel-ch06, Cambridge Ch8 |
| **degree adverb** | An adverb such as very, too, quite or enough that indicates the degree of a property. |  | Cambridge Ch6 |
| **Degree word** | A modifier such as “very” that tells how strongly a quality applies. | degree words, DEG | Foundations Ch3 |
| **Degree word (DEG)** | A word such as “very” or “quite” that indicates the degree to which a quality applies. |  | Foundations br-03 |
| **deictic centre** | The perspective from which deictic expressions are interpreted, usually the speaker’s. |  | Cambridge Ch17 |
| **deictic expression** | An expression whose reference is fixed in relation to the utterance-act. |  | Cambridge Ch17 |
| **deictic marker** | The word within a larger expression that carries the deictic meaning. |  | Cambridge Ch17 |
| **deictic shift** | The adjustment of pronouns, time and place expressions in indirect report. |  | Cambridge Ch11 |
| **deictic-centre shift** | A shift of the deictic perspective from speaker to addressee or a reported participant. |  | Cambridge Ch17 |
| **deixis** | Reference determined by features of the utterance-act, such as speaker, addressee, time and place. |  | Cambridge Ch2, Cambridge Ch17 |
| **delayed right constituent coordination** | Coordination in which a shared right constituent follows both coordinates. |  | Cambridge Ch15 |
| **delimiting comma** | A comma pair enclosing a supplement or parenthetical element. |  | Cambridge Ch20 |
| **Demonstrative** | A word such as “this” or “those” that points out what the noun phrase refers to. | demonstratives, DEM | Foundations Ch7, Cambridge Ch17 |
| **Demonstrative (DEM)** | A word such as “this”, “that”, “these”, or “those” that points out a referent. |  | Foundations br-07 |
| **deontic modality** | Modality of obligation, permission and prohibition. |  | Cambridge Ch3 |
| **Derivation** | The steps that show how rules build a sentence or another structure. | derivations | Foundations Ch11, Foundations cgel-ch19, Cambridge Ch19 |
| **descriptive grammar** | An account of how speakers actually use a language. |  | Cambridge Ch1 |
| **DET** | Determiner: the constituent that combines with NOM to form NP. It may be filled or an empty zero-word position. |  | Tree notation (SynTutor FINAL-D1) |
| **determinative** | A word such as the, a or this that helps identify a noun phrase. |  | Cambridge Ch1, Cambridge Ch2, Cambridge Ch5 |
| **Determiner** | A word or phrase that helps identify or quantify what an NP refers to. DET marks its position. | determiners, DET | Foundations Ch7, Foundations cgel-ch05, Cambridge Ch2, Cambridge Ch5 |
| **Determiner (DET)** | A word or expression that helps identify or quantify what a noun phrase refers to. DET labels its position in the tree. |  | Foundations br-07 |
| **dialect** | A variety that differs in vocabulary and grammar as well as pronunciation. |  | Cambridge Ch1 |
| **diminutive** | An affix or formation expressing smallness or endearment. |  | Cambridge Ch19 |
| **Direct object** | A verb complement that often gives the person or thing involved in the action, such as “the gate” in “opened the gate”. | direct objects | Foundations Ch4, Foundations br-04, Cambridge Ch4 |
| **direct reported speech** | A report that quotes the original utterance. |  | Cambridge Ch11 |
| **direction** | The orientation of movement, as in towards the door. |  | Cambridge Ch8 |
| **direction question** | A question asking for a direction or route. |  | Cambridge Ch10 |
| **directive** | A cover term for requests, commands, instructions and similar acts. |  | Cambridge Ch10 |
| **discourse-new** | Information not yet introduced or inferable from the prior discourse. |  | Cambridge Ch16 |
| **discourse-old** | Information already introduced or inferable from the prior discourse. |  | Cambridge Ch16 |
| **Disjunct** | An adverbial that gives a speaker’s comment on a statement or on how they are saying it. | disjuncts, disjunct adverbial, disjunct adverbials | Foundations Ch5 |
| **dislocation** | A construction in which an NP is placed outside the main clause and resumed by a pronoun. |  | Cambridge Ch15 |
| **displaced subject** | The NP that follows the verb in an existential construction and corresponds to the basic subject. |  | Cambridge Ch16 |
| **ditrans** | Ditransitive frame: the verb takes two object complements. |  | Tree notation (SynTutor FINAL-D1) |
| **Ditransitive verb** | A verb used with two complements, as in “gave Mia a map”. | ditransitive verbs, ditransitive, V [ditrans], [ditrans] | Foundations Ch4 |
| **do it** | A pro-form with a pronoun object, often referring to a specific action. |  | Cambridge Ch17 |
| **do so** | A pro-form replacing a verb phrase, as in She left and I did so too. |  | Cambridge Ch17 |
| **Do-support** | Using auxiliary “do” to carry tense in a question or negative when the lexical verb needs help. | auxiliary do, TENSE | Foundations Ch6, Foundations cgel-ch03, Cambridge Ch3 |
| **domain** | The sphere or field within which a clause is claimed to hold, as in politically. |  | Cambridge Ch8 |
| **Dominance** | A node dominates each part it can reach by following branches downward. An immediate part is one branch away. | immediate dominance, dominates, immediately dominates | Foundations Ch1 |
| **dubitative** | A construction expressing doubt about a question or its answer. |  | Cambridge Ch11 |
| **Dummy subject** | A word that fills the subject position without naming a participant, such as “it” in “It is raining”. | dummy it, expletive it, dummy subjects | Foundations Ch8 |
| **duration** | The temporal extent of a situation, as in for two hours. |  | Cambridge Ch8 |
| **dynamic modality** | Modality concerned with abilities, dispositions and other properties of participants. |  | Cambridge Ch3 |

### E

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **E** | Ellipsis: a zero-word position standing for omitted material, not a movement gap. |  | Tree notation (SynTutor FINAL-D1) |
| **e-deletion** | Deletion of final e before a suffix, as in liking. |  | Cambridge Ch18 |
| **echo question** | A question that repeats part of a preceding utterance in order to question or clarify it. |  | Cambridge Ch10 |
| **Ellipsis** | Leaving words unspoken when their role or meaning can be understood from context. | ellipted, elliptical | Foundations Ch5, Foundations cgel-ch17, Cambridge Ch17 |
| **ellipsis points** | Three dots marking omission or a trailing off. |  | Cambridge Ch20 |
| **Embedded clause** | A clause that forms part of a larger phrase or clause. | embedded clauses, subordinate clause, subordinate clauses, clause embedding | Foundations Ch8, Foundations br-08, Foundations cgel-clauses |
| **Embedded interrogative** | A question inside a larger clause, as in “Mia asked which key he took”. | embedded interrogatives, embedded question, embedded questions, subordinate interrogative, subordinate interrogatives | Foundations Ch9 |
| **end weight** | The tendency to place heavier or more complex constituents later in the clause. |  | Cambridge Ch16 |
| **end-attachment coordination** | Coordination in which the second coordinate is attached at the end of the clause. |  | Cambridge Ch15 |
| **entailment** | A meaning that must be true whenever the original statement is true. |  | Cambridge Ch1 |
| **epistemic modality** | Modality concerned with the speaker's commitment to the truth of a proposition. |  | Cambridge Ch3 |
| **equality** | A comparison presenting two values as equal or at least equal, typically with as. |  | Cambridge Ch13 |
| **established word** | A word recognised as part of the vocabulary and listed in standard dictionaries. |  | Cambridge Ch19 |
| **evaluation** | A comment on the value or fortunate status of a situation. |  | Cambridge Ch8 |
| **exclamative** | A clause type with an initial what or how phrase, characteristically used for exclamatory statements. |  | Cambridge Ch10 |
| **exclamative content clause** | A content clause with exclamative type, based on what or how. |  | Cambridge Ch11 |
| **exclamatory statement** | The characteristic use of an exclamative clause, distinct from exclamation as a general meaning. |  | Cambridge Ch10 |
| **exhaustive conditional** | A conditional construction quantifying over a set of alternatives, such as whether he comes or not. |  | Cambridge Ch11 |
| **existential construction** | A construction with dummy there and a displaced subject, as in There is a frog in the pool. |  | Cambridge Ch16 |
| **expanded coordinate** | A coordinate including its coordinator and any modifiers. |  | Cambridge Ch15 |
| **expanded declarative** | A declarative content clause introduced by that. |  | Cambridge Ch11 |
| **experiencer** | The entity that feels, perceives or cognises something. |  | Cambridge Ch4 |
| **expletive** | A word such as there that fills a grammatical position without naming a participant. |  | Tree notation (SynTutor FINAL-D1) |
| **expressed subject** | A subject present as words in the clause, as him is in for him to speak. |  | Foundations cgel-ch14 |
| **extent** | The measured size or reach of a situation, as in five miles or two hours. |  | Cambridge Ch8 |
| **extraposed object** | A clause placed after dummy it in object function. |  | Cambridge Ch14 |
| **extraposed subject** | A non-finite or finite clause placed after dummy it in subject function. |  | Cambridge Ch14 |
| **Extraposition** | Placing a subject clause later in the sentence while “it” fills the usual subject position. | extraposed subject, extraposed subjects | Foundations Ch8, Foundations cgel-ch16, Cambridge Ch11, Cambridge Ch16 |

### F

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **factivity** | The property of a predicate that treats its complement as factive, presupposing its truth. |  | Cambridge Ch11 |
| **feature** | A property shown on a node, such as trans, intrans, pres, past, or -tense. |  | Tree notation (SynTutor FINAL-D1) |
| **Finite** | A finite verb carries tense. A finite clause contains a verb that carries tense. | finite verb, finite verbs, finite clause, finite clauses | Foundations Ch10 |
| **finite clause** | A clause headed by a primary verb form, or by a plain form in an imperative or subjunctive. |  | Cambridge Ch2, Cambridge Ch3, Cambridge Ch11 |
| **flat adverb** | An adverb with the same form as an adjective, such as fast or hard. |  | Cambridge Ch6 |
| **focus** | The constituent bearing the main informational prominence in a clause. |  | Cambridge Ch16 |
| **focus of negation** | The part of the scope that is most prominently negated. |  | Cambridge Ch9 |
| **focus-frame** | The open proposition left when the focus is replaced by a variable. |  | Cambridge Ch16 |
| **focusing modifier** | An adverb such as only or also that highlights a particular constituent. |  | Cambridge Ch6 |
| **for-complex construction** | A complex catenative construction in which for introduces the subject of the infinitival. |  | Cambridge Ch14 |
| **for-infinitival** | A to-infinitival with an overt subject introduced by for. |  | Cambridge Ch14 |
| **foreign plural** | A plural retaining a borrowed morphological pattern, as in formulae. |  | Cambridge Ch18 |
| **fossilised expression** | A fixed expression with limited internal variation, often headed by a preposition. |  | Cambridge Ch7 |
| **free indirect speech** | A blend of indirect report and the original speaker’s perspective or wording. |  | Cambridge Ch11 |
| **frequency** | How often a situation occurs, as in twice or every day. |  | Cambridge Ch8 |
| **Fronting** | Putting a word or phrase earlier in a clause, as when a tensed auxiliary moves before the subject in a yes/no question. | auxiliary fronting, fronted auxiliary, fronted auxiliaries | Foundations Ch6, Foundations br-09, Cambridge Ch10 |
| **Function** | The grammatical role a word or phrase has within a larger structure, such as subject or object. |  | Foundations br-02 |
| **fused head** | A construction in which one expression does the work of the head as well as another function, as each does in each was labelled. |  | Foundations cgel-ch05, Cambridge Ch2, Cambridge Ch5, Cambridge Ch17 |
| **fused relative** | A relative construction in which antecedent and relative clause are fused into one phrase. |  | Cambridge Ch12 |
| **fused relative NP** | A fused relative phrase headed by what, whoever or whichever and functioning as an NP. |  | Cambridge Ch12 |
| **fused relative PP** | A fused relative phrase based on where or when and functioning as a PP. |  | Cambridge Ch12 |
| **future time** | A semantic time reference that English expresses through several constructions rather than a dedicated future tense. |  | Cambridge Ch3 |

### G

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **Gap** | A position with no spoken word. In a fronting tree it shows where the fronted expression has its role. | gaps, object gap, object gaps, subject gap, subject gaps | Foundations Ch9, Foundations br-09, Cambridge Ch2, Cambridge Ch12 |
| **gapped coordination** | Coordination in which material is omitted from one coordinate under identity with another. |  | Cambridge Ch15 |
| **gapping** | Ellipsis of a repeated verb in a coordination, as in Kim likes tea and Pat coffee. |  | Cambridge Ch17 |
| **gender** | A grammatical category relevant to pronoun selection and agreement. |  | Cambridge Ch5 |
| **Generative grammar** | A grammar that specifies which sentences its rules allow and assigns structure to them. |  | Foundations Ch11 |
| **generic pronoun** | A pronoun used for people in general rather than a specific referent, as in You can’t tell. |  | Cambridge Ch17 |
| **genitive** | A form that marks a relation such as possession, as in the guests’ coats. |  | Foundations cgel-ch18, Cambridge Ch5, Cambridge Ch18 |
| **gerund-participial clause** | A non-finite clause headed by a gerund-participle in -ing. |  | Cambridge Ch14 |
| **gerund-participle** | The verb form in -ing, used after progressive be and in various non-finite clauses. |  | Cambridge Ch3 |
| **get-passive** | A passive formed with get rather than be, often with an event or adversative nuance. |  | Cambridge Ch16 |
| **goal** | The endpoint of a path or change of location, often marked by to or into. |  | Cambridge Ch4, Cambridge Ch7, Cambridge Ch8 |
| **gradable** | Able to denote a property in varying degrees, as with happy, happier, very happy. |  | Cambridge Ch6 |
| **grade** | The system of plain, comparative and superlative forms. |  | Cambridge Ch18 |
| **Grammar** | A system of rules describing how words and groups can combine in a language. | grammars | Foundations Ch11, Foundations br-11 |
| **Grammatical function** | The job a word or group does in a larger structure, such as subject or direct object. | grammatical functions, syntactic function, syntactic functions | Foundations Ch2 |
| **grammaticised preposition** | A preposition selected by a grammatical construction rather than chosen for its independent meaning. |  | Cambridge Ch7 |

### H

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **Head** | The main word that determines the category of a phrase. | head word, head words, head noun, head nouns | Foundations Ch2, Foundations br-03, Foundations cgel-ch05, Cambridge Ch1 |
| **Head noun (N)** | The noun that heads the nominal and gives the noun phrase its basic reference. |  | Foundations br-07 |
| **heavy punctuation** | A style using more optional marks, especially commas. |  | Cambridge Ch20 |
| **Hierarchy** | The way smaller units are nested inside larger ones. |  | Foundations Ch1, Foundations br-01 |
| **hollow clause** | A non-finite clause missing a non-subject element that is recovered from context. |  | Cambridge Ch12, Cambridge Ch14 |
| **hyphen** | A word-internal mark joining parts of a compound or a line break. |  | Cambridge Ch20 |

### I

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **identity** | The relation of being the same entity or set, often expressed by same. |  | Cambridge Ch13 |
| **idiom** | An expression whose meaning is not fully predictable from its parts. |  | Cambridge Ch7 |
| **if** | A conditional preposition or subordinator; in content clauses it introduces interrogatives only under restricted conditions. |  | Cambridge Ch11 |
| **illocutionary force** | The speech act performed by an utterance, such as stating, asking or directing. |  | Cambridge Ch10 |
| **imperative** | A clause type commonly used for instructions, with a plain-form verb and often an understood subject. |  | Foundations cgel-ch10, Cambridge Ch10 |
| **implicature** | A meaning a speaker suggests without stating it. |  | Cambridge Ch1 |
| **in situ** | In the position normally occupied by the corresponding element in a declarative clause. |  | Cambridge Ch10 |
| **Indefinite pronoun** | A pronoun such as “someone” that refers without naming a particular person or thing. | indefinite pronouns | Foundations Ch7 |
| **index** | A co-indexing number that links a gap to its filler or controller. |  | Tree notation (SynTutor FINAL-D1) |
| **indexing act** | A gesture, gaze or written device that helps identify a deictic referent. |  | Cambridge Ch17 |
| **Indirect object** | An object that typically names the receiver or beneficiary, such as “Mia” in “gave Mia a map”. | indirect objects | Foundations Ch4, Cambridge Ch4 |
| **indirect reported speech** | A report of what was said using a content clause, often with backshift and deixis shifts. |  | Cambridge Ch11 |
| **indirect speech act** | A speech act performed by a clause whose literal form is characteristic of another act. |  | Cambridge Ch10 |
| **inequality** | A comparison presenting values as unequal, typically with than or less. |  | Cambridge Ch13 |
| **inferiority** | Scalar inequality in which the primary term is lower on the scale. |  | Cambridge Ch13 |
| **infinitival clause** | A non-finite clause with a plain-form verb, either with to or bare. |  | Cambridge Ch14 |
| **infinitival marker** | The to before a plain verb in an infinitival clause, as in to work late. |  | Foundations cgel-ch06 |
| **infinitival relative** | A relative clause with an infinitival verb, such as a place to watch the procession from. |  | Cambridge Ch12 |
| **Infinitival “to”** | The marker “to” that precedes a base-form verb in a to-infinitive. In the tree, it acts as an untensed auxiliary with a verb phrase as its complement. |  | Foundations br-10 |
| **inflection** | A form change that marks a grammatical distinction such as past tense or plural. |  | Foundations cgel-ch18, Cambridge Ch1, Cambridge Ch18 |
| **inflectional comparative** | A comparative formed with -er, as in cheaper. |  | Cambridge Ch13, Cambridge Ch18 |
| **information packaging** | A non-canonical construction that changes how content is presented rather than its truth conditions. |  | Cambridge Ch2, Cambridge Ch16 |
| **initialism** | A word formed from the initial letters of a phrase, pronounced letter by letter or as a word. |  | Cambridge Ch19 |
| **Inner and outer VP** | Two levels of verb phrase structure. The inner VP sits inside the outer VP, which also covers material attached at the higher level. |  | Foundations br-05 |
| **Inner VP** | The smaller verb phrase nested inside a larger verb phrase. | VP₁, VP1 | Foundations Ch5 |
| **instrument** | An entity used to carry out an action, as in with a hammer. |  | Cambridge Ch8 |
| **integrated relative** | A relative clause integrated into the nominal it modifies, prototypically restricting its denotation. |  | Cambridge Ch12 |
| **intens** | Intensive frame: the verb takes a subject-predicative complement. |  | Tree notation (SynTutor FINAL-D1) |
| **Intensive verb** | A verb used with a subject predicative, such as “became” in “became quiet”. | intensive verbs, V [intens], [intens] | Foundations Ch4 |
| **internal change** | A morphological operation that changes a vowel or consonant inside the base. |  | Cambridge Ch18 |
| **interrogative content clause** | A content clause with closed or open interrogative type. |  | Cambridge Ch11 |
| **interrogative infinitival** | An infinitival clause with interrogative type, as in whether to go. |  | Cambridge Ch14 |
| **interrogative phrase** | A phrase based on an interrogative word, such as which one or how much. |  | Cambridge Ch10 |
| **intrans** | Intransitive frame: the verb takes no object complement. |  | Tree notation (SynTutor FINAL-D1) |
| **intransitive preposition** | A preposition used without a complement, such as outside in She is outside. |  | Cambridge Ch7 |
| **Intransitive verb** | A verb used without complements. | intransitive verbs, intransitive, V [intrans], [intrans] | Foundations Ch4 |
| **irrealis** | The residual mood form were used in hypothetical or counterfactual clauses. |  | Cambridge Ch11 |
| **irregular form** | An inflectional form requiring lexeme-specific information. |  | Cambridge Ch18 |
| **it-cleft** | A construction such as It was Maya who closed the valve, which singles out a value for a role. |  | Foundations cgel-ch16, Cambridge Ch16 |

### J

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **joint coordination** | A coordination interpreted as a single joint entity, as in Kim and Pat are a couple. |  | Cambridge Ch15 |

### L

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **landmark** | The reference point or area relative to which a trajector is located. |  | Cambridge Ch7 |
| **Language variety** | A set of patterns of language use shared by a group of speakers. | language varieties | Foundations Ch11 |
| **layered coordination** | A coordination in which a coordination functions as a coordinate within a larger one. |  | Cambridge Ch15 |
| **left dislocation** | Placement of an NP at the left edge with a resumptive pronoun in the clause. |  | Cambridge Ch16 |
| **let-imperative** | An imperative beginning with let, often used for first-person inclusive suggestions. |  | Cambridge Ch10 |
| **lexeme** | A word as a dictionary entry, apart from its different forms. |  | Cambridge Ch1, Cambridge Ch18 |
| **lexical base** | A base that is not part of a larger base formed by lexical word-formation. |  | Cambridge Ch18, Cambridge Ch19 |
| **Lexical category** | The grammatical class of a word, such as noun, adjective, or verb. | lexical categories, word class, word classes | Foundations Ch3 |
| **Lexical verb** | The verb that gives the main action, state, or relation in its phrase. | lexical verbs, V | Foundations Ch4, Cambridge Ch3 |
| **Lexical VP** | A verb phrase headed by the main verb, together with any complements of that verb. |  | Foundations br-06, Foundations br-10 |
| **lexical word-formation** | The creation of new lexemes from bases by derivation, compounding or other processes. |  | Cambridge Ch18, Cambridge Ch19 |
| **lexicalisation** | The establishment of a formation as a lexical item with its own meaning. |  | Cambridge Ch19 |
| **liaison** | The linking of sounds across word boundaries in connected speech. |  | Cambridge Ch18 |
| **light punctuation** | A style using relatively few optional marks, especially commas. |  | Cambridge Ch20 |
| **light verb** | A verb such as give, take or make whose main semantic content comes from its noun complement. |  | Cambridge Ch4 |
| **likeness** | A relation of similarity rather than identity, often expressed by like or similar. |  | Cambridge Ch13 |
| **litotes** | A negative expression used to convey a positive meaning indirectly, as in not uncommon. |  | Cambridge Ch9 |
| **location** | A static spatial or temporal relation, as in in the garden or at six. |  | Cambridge Ch7, Cambridge Ch8 |
| **locative deixis** | Deixis of place, expressed by here, there, this, that and related expressions. |  | Cambridge Ch17 |
| **long hyphen** | A mark used in some styles to join coordinated names or relationships. |  | Cambridge Ch20 |

### M

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **Main clause** | The highest clause in a sentence. It can contain smaller clauses. | main clauses, matrix clause, matrix clauses | Foundations Ch8, Cambridge Ch11 |
| **mandative construction** | A construction expressing requirement or recommendation, often with a subjunctive or should. |  | Cambridge Ch11 |
| **manner** | The way in which a process is carried out, as in She spoke quietly. |  | Cambridge Ch8 |
| **manufacture** | The invention of a new word without morphological structure, often a brand name. |  | Cambridge Ch19 |
| **Mass noun** | A noun used for something measured as a quantity, as in “some water”. | mass nouns | Foundations Ch3 |
| **matrix sentence** | The larger sentence containing an embedded question, quotation or other construction. |  | Foundations cgel-ch20 |
| **means** | The method by which something is achieved, as in by breaking the door down. |  | Cambridge Ch8 |
| **metalinguistic comparison** | A comparison that measures how well a description fits rather than comparing the things themselves. |  | Cambridge Ch13 |
| **metalinguistic negation** | Negation used to reject a formulation, implicature or pronunciation rather than the truth of a proposition. |  | Cambridge Ch9 |
| **minor clause type** | A conventionalised clause-like expression that does not fit the major type system neatly. |  | Cambridge Ch10 |
| **MOD** | Modal: an auxiliary such as can, may, must, should, or will. |  | Tree notation (SynTutor FINAL-D1) |
| **Modal auxiliary** | An auxiliary such as “can” or “must” that can express ability, possibility, or obligation. | modal auxiliaries, modal, modals, MOD | Foundations Ch6, Cambridge Ch3 |
| **modal preterite** | A past-tense form used to mark modal remoteness rather than past time. |  | Cambridge Ch11 |
| **modal remoteness** | The use of a past tense form to present a situation as less likely, less direct or hypothetical. |  | Cambridge Ch3 |
| **modality** | Meaning concerned with necessity, possibility and the speaker's attitude to factuality or actualisation. |  | Cambridge Ch3, Cambridge Ch8 |
| **Modifier** | A word or group that adds information to another word or group. | modifiers | Foundations Ch2, Cambridge Ch1, Cambridge Ch6, Cambridge Ch7 |
| **mood** | The grammatical marking of modality, chiefly through modal auxiliaries in English. |  | Cambridge Ch3 |
| **morphology** | The part of grammar concerned with the form of words. |  | Cambridge Ch18 |
| **multiple complementation** | The occurrence of a verb in more than one complementation pattern. |  | Cambridge Ch4 |
| **multiple coordination** | A coordination with more than two coordinates. |  | Cambridge Ch15 |
| **multiplier** | The part giving the number of hundreds, thousands or other powers in a composite numeral. |  | Foundations cgel-ch19 |

### N

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **Negation** | The grammatical expression of a negative meaning, often with “not” or “n’t”. |  | Foundations Ch6 |
| **negative auxiliary** | A negative form of an auxiliary, such as isn’t or won’t. |  | Cambridge Ch18 |
| **negative concord** | The marking of a single semantic negation more than once, as in non-standard I didn’t say nothing. |  | Cambridge Ch9 |
| **negative idiom** | An idiom with a negative meaning that is not simply a polarity-sensitive item, such as not lift a finger. |  | Cambridge Ch9 |
| **negative polarity item** | An expression such as any, ever or at all that is favoured in negative or non-affirmative contexts. |  | Cambridge Ch9 |
| **negative retort** | A reduced negative response that rejects a proposition or proposal. |  | Cambridge Ch9 |
| **neo-classical compound** | A compound formed from classical combining forms, such as biography. |  | Cambridge Ch19 |
| **never-attributive adjective** | An adjective excluded from attributive function, such as asleep or alone. |  | Cambridge Ch6 |
| **NICE** | The four auxiliary-sensitive constructions: negation, inversion, code and emphasis. |  | Cambridge Ch3 |
| **Node** | A point in a tree that represents a word, group, or position. | nodes | Foundations Ch1 |
| **NOM** | Nominal: the part of an NP below DET that contains the head noun with its modifiers and complements. |  | Tree notation (SynTutor FINAL-D1) |
| **Nominal** | The part of an NP built around the head noun. It can contain modifiers and complements. | nominals, NOM | Foundations Ch7, Cambridge Ch2, Cambridge Ch5 |
| **Nominal (NOM)** | The part of a noun phrase built around the head noun. In the tree, NOM labels the layer between NP and the head noun. That layer can also contain modifiers. |  | Foundations br-07 |
| **nominalisation** | The formation of a noun from a verb, adjective or other base. |  | Cambridge Ch19 |
| **non-affirmative context** | A question, conditional, comparative or other context that is not a positive assertion. |  | Cambridge Ch9 |
| **non-canonical clause** | A clause differing from a canonical counterpart in polarity, clause type, information packaging, subordination or coordination. |  | Cambridge Ch2 |
| **non-core complement** | A complement realised by a PP or another oblique structure rather than a direct NP. |  | Cambridge Ch4 |
| **non-count noun** | A noun use that presents a substance or collection without individual counting. |  | Cambridge Ch5 |
| **non-expandable declarative** | A declarative content clause whose governing item excludes that. |  | Cambridge Ch11 |
| **Non-finite** | A non-finite verb has no tense of its own. A non-finite clause is built around an untensed verb phrase. | non-finite clause, non-finite clauses, non-finite verb, non-finite verbs, [-tense] | Foundations Ch10, Foundations br-10 |
| **non-finite clause** | A clause whose verb is an infinitival or participial form, as in to check the gauge or checking the gauge. |  | Foundations cgel-ch14, Cambridge Ch11, Cambridge Ch14 |
| **non-gradable** | A use of an adjective that does not readily accept degree modification or comparison. |  | Cambridge Ch6 |
| **non-referential** | An NP use that ascribes a property or role rather than picking out a referent. |  | Cambridge Ch5 |
| **non-restrictive** | A relative use that adds information without restricting the antecedent’s denotation. |  | Cambridge Ch12 |
| **Non-restrictive relative** | A relative clause that adds information about an already identified group. | non-restrictive relatives, non-restrictive relative clause, non-restrictive relative clauses | Foundations Ch9 |
| **non-scalar comparison** | Comparison concerned with identity, likeness or difference rather than degree. |  | Cambridge Ch13 |
| **non-scalar equality** | Identity or likeness expressed with same, similar or as. |  | Cambridge Ch13 |
| **non-scalar inequality** | Difference or unlikeness expressed with different, other, else or unlike. |  | Cambridge Ch13 |
| **non-segmental** | A modification such as italics, bold face or capitalisation that does not occupy a separate position. |  | Cambridge Ch20 |
| **non-verbal negation** | Negation marked on a dependent rather than on the verb. |  | Cambridge Ch9 |
| **nonce constituent** | A sequence that functions as a constituent only for the purposes of a particular coordination. |  | Cambridge Ch15 |
| **nonce-word** | A word used on a particular occasion but not established in the vocabulary. |  | Cambridge Ch19 |
| **Noun** | A word that can head a noun phrase. | nouns | Foundations Ch3, Cambridge Ch5 |
| **Noun phrase** | A phrase that can be headed by a noun. A name or pronoun can also form a whole noun phrase. | noun phrases, NP, NPs | Foundations Ch2, Cambridge Ch5 |
| **NP** | Noun phrase: a phrase whose head is a noun, pronoun, or fused nominal. FINAL-D1 nominals are projected as DET + NOM. |  | Tree notation (SynTutor FINAL-D1) |
| **number-transparent noun** | A noun such as number or lot whose agreement follows the oblique complement rather than its own number. |  | Cambridge Ch5 |
| **numeral** | A word expressing number, such as cardinal, ordinal or fractional forms. |  | Cambridge Ch19 |

### O

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **object of a preposition** | The NP complement of a transitive preposition, as in the garden in in the garden. |  | Cambridge Ch7 |
| **Object predicative** | A complement that describes or identifies the direct object, as “blue” does in “painted the door blue”. | object predicatives | Foundations Ch4 |
| **oblique** | An NP related to the verb through a preposition rather than directly as a core complement. |  | Cambridge Ch4, Cambridge Ch7 |
| **oblique-complex construction** | A complex catenative construction in which the intervening NP is the complement of a preposition. |  | Cambridge Ch14 |
| **open conditional** | A conditional that leaves the fulfilment of the condition open. |  | Cambridge Ch8 |
| **open interrogative** | A question clause that asks for missing information, commonly with who, what, where or how. |  | Foundations cgel-ch10, Cambridge Ch10, Cambridge Ch12 |
| **operator** | A fronted auxiliary or wh-expression that occupies C1 or C2. |  | Tree notation (SynTutor FINAL-D1) |
| **orthographic sentence** | A unit of writing beginning with a capital and ending with a primary terminal. |  | Cambridge Ch20 |
| **orthographic word** | A minimal unit of writing flanked by spaces or punctuation. |  | Cambridge Ch20 |
| **Outer VP** | The larger verb phrase containing a smaller VP and, in these trees, an added modifier. | VP₂, VP2 | Foundations Ch5 |
| **Overt subject** | A subject expressed in words. | overt subjects | Foundations Ch10 |

### P

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **parasitic gap** | A gap that is licensed by another gap in the same construction. |  | Cambridge Ch12 |
| **parenthesis** | A pair of round or square brackets enclosing material. |  | Cambridge Ch20 |
| **parenthetical** | A detached expression commenting on or qualifying the clause, such as I think. |  | Cambridge Ch10, Cambridge Ch15 |
| **Participle** | An untensed verb form such as “going” or “gone”, used in constructions such as progressives, perfects, and passives. | participles, past participle, past participles, passive participle, passive participles, -ing participle, -ing participles | Foundations Ch10, Foundations cgel-ch03 |
| **Participle phrase** | A phrase built around a participial verb, such as “glowing” in “the glowing coals”. | participle phrases, PartP | Foundations Ch7 |
| **Particle** | A word such as “off” that combines with a verb in a phrasal verb. | particles, Prt | Foundations Ch5, Foundations cgel-ch04, Cambridge Ch4 |
| **partitive** | A construction denoting a subset or subquantity of a set, often with of. |  | Cambridge Ch5 |
| **PASS** | Passive auxiliary: be when it takes a past-participle VP complement in a passive construction. |  | Tree notation (SynTutor FINAL-D1) |
| **passive** | A construction that can make the affected participant the subject, as in The valve was closed by Maya. |  | Foundations cgel-ch16, Cambridge Ch16 |
| **Passive auxiliary** | A form of “be” that selects a passive participle, as in “was written”. | passive auxiliaries, passive be, PASS | Foundations Ch6 |
| **Passive clause** | A construction in which an active object can serve as subject, as “the gate” does in “the gate was opened”. | passive clauses, passive sentence, passive sentences, passive subject, object promotion | Foundations Ch6 |
| **past** | Past tense feature. |  | Tree notation (SynTutor FINAL-D1) |
| **past participle** | The verb form used after perfect have and passive be, as in taken or written. |  | Cambridge Ch3, Cambridge Ch18 |
| **past-participial clause** | A non-finite clause headed by a past participle. |  | Cambridge Ch14 |
| **path** | An intermediate route between source and goal, as in through the tunnel. |  | Cambridge Ch8 |
| **patient** | The entity affected by an action. |  | Cambridge Ch4 |
| **PERF** | Perfect auxiliary: have when it takes a past-participle VP complement. |  | Tree notation (SynTutor FINAL-D1) |
| **perfect** | The secondary past tense marked by have plus a past participle. |  | Cambridge Ch3 |
| **Perfect auxiliary** | A form of “have” that selects a participle, as in “has written”. | perfect auxiliaries, perfect have, PERF | Foundations Ch6 |
| **person deixis** | Deixis involving the speaker, addressee or third parties, expressed by personal pronouns. |  | Cambridge Ch17 |
| **phrasal** | Phrasal-verb frame: a lexical verb combines with a particle. |  | Tree notation (SynTutor FINAL-D1) |
| **Phrasal category** | The grammatical class of a phrase, such as NP or AP. | phrasal categories, phrase category, phrase categories | Foundations Ch3 |
| **Phrasal verb** | A verb combined with a particle, such as “turn off”. | phrasal verbs, [phrasal] | Foundations Ch5 |
| **Phrase** | A unit that can contain several words or consist of one word. | phrases | Foundations Ch1 |
| **Phrase marker** | A tree or labelled brackets showing how words are grouped. | phrase markers | Foundations Ch1 |
| **pied-piping** | Fronting a preposition together with its complement, as in To whom are you speaking? |  | Cambridge Ch7 |
| **plain form** | The uninflected verb form used after modal auxiliaries and supportive do, as in check. |  | Foundations cgel-ch03, Cambridge Ch3 |
| **plain-complex construction** | A complex catenative construction with an intervening NP that is not introduced by a preposition. |  | Cambridge Ch14 |
| **pleonastic negation** | A negative marker that adds no separate semantic negation. |  | Cambridge Ch9 |
| **plural** | The number form used for more than one entity. |  | Cambridge Ch18 |
| **polar question** | A question with a closed set of answers, typically yes and no. |  | Cambridge Ch10 |
| **polarity** | The contrast between positive and negative clauses. |  | Cambridge Ch9 |
| **polysyndetic** | Multiple coordination with a coordinator before every non-initial coordinate. |  | Cambridge Ch15 |
| **positive polarity item** | An expression such as some or already that is favoured in positive contexts. |  | Cambridge Ch9 |
| **Post-modifier** | A modifier that comes after the noun it describes. | post-modifiers, postmodifier, postmodifiers | Foundations Ch7 |
| **postposing** | Placement of a constituent later than its default position, often for weight or focus. |  | Cambridge Ch16 |
| **postpositive** | The function of an adjective phrase used as a post-head modifier inside an NP. |  | Cambridge Ch6 |
| **potential word** | A morphologically grammatical word that is not established. |  | Cambridge Ch19 |
| **PP** | Prepositional phrase: a phrase headed by a preposition. |  | Tree notation (SynTutor FINAL-D1) |
| **Pre-determiner** | A word such as “both” that can appear before the determiner, as in “both those maps”. | pre-determiners, PRE-DET | Foundations Ch7 |
| **Pre-modifier** | A modifier that comes before the head it describes. | pre-modifiers, premodifier, premodifiers | Foundations Ch7 |
| **predicand** | The element to which a predicative complement applies, usually the subject or object. |  | Cambridge Ch4 |
| **Predicate** | The part that says what the subject does, what happens to it, or what state it is in. | predicates | Foundations Ch2, Foundations br-02 |
| **Predicative** | A complement that describes or identifies a subject or direct object. | predicatives | Foundations Ch4 |
| **predicative complement** | A complement that ascribes a property to the subject or object rather than naming a participant. |  | Cambridge Ch2, Cambridge Ch4, Cambridge Ch6, Cambridge Ch7, Cambridge Ch14 |
| **predicator** | The clause function realised by the verb phrase. |  | Cambridge Ch4 |
| **prefix** | An affix attached before the base. |  | Cambridge Ch19 |
| **prenucleus** | The position before the nucleus clause, occupied by a fronted element such as a wh-phrase or auxiliary. |  | Cambridge Ch2 |
| **prep** | Prepositional-verb frame: the verb takes a PP complement. |  | Tree notation (SynTutor FINAL-D1) |
| **preposing** | Placement of a complement in front of the nucleus clause, as in This one she accepted. |  | Cambridge Ch7, Cambridge Ch16 |
| **Preposition** | A word such as “under” that can head a phrase expressing a relation such as place, time, or direction. | prepositions | Foundations Ch3, Foundations cgel-ch07, Cambridge Ch7 |
| **preposition phrase** | A phrase headed by a preposition, with an optional complement and optional modifiers. |  | Cambridge Ch7 |
| **Prepositional complement** | A prepositional phrase selected by a verb, as “on the map” is in “relied on the map”. | prepositional complements, PP complement, PP complements | Foundations Ch4 |
| **Prepositional phrase** | A phrase headed by a preposition, such as “under the bridge”. | prepositional phrases, PP, PPs | Foundations Ch3 |
| **prepositional to** | The to in accustomed to the schedule or accustomed to working late. |  | Foundations cgel-ch06 |
| **Prepositional verb** | A verb used with a selected prepositional phrase. | prepositional verbs, V [prep], [prep] | Foundations Ch4, Cambridge Ch4 |
| **pres** | Present tense feature. |  | Tree notation (SynTutor FINAL-D1) |
| **presentational construction** | A construction introducing an entity into the discourse, often with here/there + verb + NP. |  | Cambridge Ch16 |
| **presupposition** | A proposition treated as already assumed in an utterance. |  | Cambridge Ch1, Cambridge Ch10, Cambridge Ch16 |
| **preterite** | The verb form often used for past time, as in lived or went. |  | Cambridge Ch1, Cambridge Ch3, Cambridge Ch18 |
| **primary term** | The term expressed in the matrix clause of a term comparison. |  | Cambridge Ch13 |
| **primary terminal** | A full stop, question mark or exclamation mark marking the end of an orthographic sentence. |  | Cambridge Ch20 |
| **Pro-form** | A word that stands in for a larger structure. “One” can stand in for a NOM. | pro-forms, pro-NOM | Foundations Ch7, Cambridge Ch17 |
| **pro-nominal one** | The pronoun one used to stand for a nominal expression. |  | Cambridge Ch17 |
| **productivity** | The availability of a word-formation pattern for creating new words. |  | Cambridge Ch19 |
| **PROG** | Progressive auxiliary: be when it takes an -ing VP complement. |  | Tree notation (SynTutor FINAL-D1) |
| **progressive** | The aspect marked by be plus a gerund-participle, presenting a situation as in progress. |  | Cambridge Ch3 |
| **Progressive auxiliary** | A form of “be” that selects an -ing form, as in “is writing”. | progressive auxiliaries, progressive be, PROG | Foundations Ch6 |
| **Progressive auxiliary (PROG)** | A form of “be” used with a verb in its -ing form to present a situation as ongoing. |  | Foundations br-06 |
| **Pronoun** | A word such as “she”, “it”, or “they” that can fill a noun phrase position. | pronouns | Foundations Ch3, Cambridge Ch5 |
| **proper name** | A conventional name for a particular entity, such as New Zealand or The Open University. |  | Cambridge Ch5 |
| **proper noun** | A noun specialised to head a proper name, such as Clinton or Thames. |  | Cambridge Ch5 |
| **protasis** | The subordinate clause expressing the condition in a conditional construction. |  | Cambridge Ch8 |
| **Prt** | Particle: the particle position of a phrasal verb, such as up in called up. |  | Tree notation (SynTutor FINAL-D1) |
| **pseudo-cleft** | A specifying construction such as What helped was closing the valve, with a fused relative as one part. |  | Foundations cgel-ch16, Cambridge Ch16 |
| **psp** | Past participle form feature. |  | Tree notation (SynTutor FINAL-D1) |
| **punctuation** | The use of marks, spaces and non-segmental modifications to indicate structure and meaning in writing. |  | Cambridge Ch20 |
| **punctuation indicator** | A punctuation mark, space, or non-segmental modification such as italics or capitals. |  | Cambridge Ch20 |
| **punctuation mark** | A written symbol such as a comma, full stop or question mark. |  | Cambridge Ch20 |
| **purpose** | The intended result of an action, as in in order to help. |  | Cambridge Ch8 |

### Q

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **Q** | Quantifier: a determiner-like word such as every, many, or all. |  | Tree notation (SynTutor FINAL-D1) |
| **QA** | Quantifying adjective: an adjective-like quantifier such as many in many reasons. |  | Tree notation (SynTutor FINAL-D1) |
| **quantification** | The marking of quantity, including universal, existential and negative meanings. |  | Cambridge Ch5 |
| **Quantifying adjective** | A word such as “three” that expresses quantity within NOM and is marked QA. | quantifying adjectives, QA | Foundations Ch7 |
| **quasi-modal** | A fixed expression with modal meaning, such as have to, had better or be able to. |  | Cambridge Ch3 |
| **question** | A semantic or pragmatic category concerned with seeking information, not a clause type. |  | Cambridge Ch10 |
| **question tag** | A short auxiliary-and-pronoun question attached to a clause, as in aren’t they? |  | Foundations cgel-ch10 |
| **quotation mark** | A paired indicator enclosing quoted or highlighted material. |  | Cambridge Ch20 |
| **Q–A presupposition** | A presupposition carried by a question and reflected in the form of its answers. |  | Cambridge Ch10 |

### R

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **raised complement** | An intervening NP that is syntactically associated with the matrix verb but semantically associated with the subordinate verb. |  | Cambridge Ch14 |
| **raising** | A relation in which a subject or object is understood as belonging semantically to a lower predicate. |  | Tree notation (SynTutor FINAL-D1) |
| **realignment** | A packaging difference that changes the alignment of semantic roles and syntactic functions. |  | Cambridge Ch16 |
| **reason** | The explanation for a situation, as in because of the strike. |  | Cambridge Ch8 |
| **reciprocal** | A form such as each other that represents a relation holding in both directions or among members of a group. |  | Foundations cgel-ch17 |
| **reciprocal pronoun** | A form such as each other or one another expressing a mutual relation. |  | Cambridge Ch17 |
| **Recursion** | Using the result of a rule as a new input to the same rule. | recursive rule, recursive rules, recursive coordination | Foundations Ch11, Foundations br-11 |
| **reference point** | The time from which an expression counts backward or forward. |  | Foundations cgel-ch07 |
| **referential** | An NP use that picks out an entity or entities. |  | Cambridge Ch5 |
| **reflexive** | A form such as herself or themselves. It can point back to a local antecedent or add emphasis in a separate use. |  | Foundations cgel-ch17 |
| **reflexive pronoun** | A form such as herself or themselves used for local anaphora or emphasis. |  | Cambridge Ch17 |
| **register** | A way of using language that suits a particular situation. |  | Cambridge Ch1 |
| **regular form** | An inflectional form produced by a general rule not specific to a lexeme. |  | Cambridge Ch18 |
| **Relative clause** | A clause that modifies a noun group, often with a position linked to that group. | relative clauses | Foundations Ch9, Cambridge Ch12 |
| **relative construction** | A cover term for relative clauses and fused relatives, including NP and PP types. |  | Cambridge Ch12 |
| **relative infinitival** | An infinitival clause functioning as a relative modifier, as in a place to stay. |  | Cambridge Ch14 |
| **relative phrase** | The initial phrase in a wh relative, containing the relative word and any material that percolates with it. |  | Cambridge Ch12 |
| **relative superlative** | A superlative use locating the extreme within a comparison set. |  | Cambridge Ch13 |
| **relative word** | A word such as who, whom, whose, which, where or when used in a relative construction. |  | Cambridge Ch12 |
| **relativised element** | The element in a relative clause that is linked anaphorically to the antecedent. |  | Cambridge Ch12 |
| **remote conditional** | A conditional using modal preterite or irrealis marking to present the condition as remote. |  | Cambridge Ch8 |
| **reordering** | A packaging difference that mainly changes linear order, as in preposing and inversion. |  | Cambridge Ch16 |
| **Replacement test** | A check that swaps a stretch of words for an expression that can do the same job. | replacement tests, substitution test, substitution tests | Foundations Ch1, Foundations br-01 |
| **reported speech** | The reporting of another utterance, either directly or indirectly. |  | Cambridge Ch11 |
| **restrictive** | A relative use that delimits the set denoted by the head nominal. |  | Cambridge Ch12 |
| **Restrictive relative** | A relative clause that helps identify which people or things are meant. | restrictive relatives, restrictive relative clause, restrictive relative clauses | Foundations Ch9 |
| **result** | The outcome of a situation, as in so that the hills glowed. |  | Cambridge Ch8 |
| **resumptive pronoun** | A pronoun in the clause that corresponds to a dislocated NP. |  | Cambridge Ch16 |
| **retrospective anaphora** | Anaphora in which the anaphor follows its antecedent. |  | Cambridge Ch17 |
| **reverse pseudo-cleft** | A pseudo-cleft with the fused relative after be, as in Closing the valve was what helped. |  | Cambridge Ch16 |
| **reversed polarity tag** | A tag whose polarity is opposite to that of the clause it follows. |  | Cambridge Ch9 |
| **right dislocation** | Placement of an NP at the right edge after a resumptive pronoun. |  | Cambridge Ch16 |
| **right nonce-constituent coordination** | Coordination of expressions that are not independent constituents but form matching right-hand sequences. |  | Cambridge Ch15 |

### S

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **S** | The sentence or clause node that groups a subject and predicate in the basic tree. |  | Foundations Ch2 |
| **S and S′** | S labels the clause with its subject and predicate. S′, read “S-bar”, is the higher layer that groups C with S. |  | Foundations br-08 |
| **scalar comparison** | Comparison of relative position on a gradable scale, as in older than or as old as. |  | Cambridge Ch13 |
| **scale orientation** | The direction of a scale determined by lexical meaning, as with old versus young. |  | Cambridge Ch13 |
| **scopal focus** | The element that a focusing modifier applies to semantically. |  | Cambridge Ch6 |
| **Scope** | The part of the structure that an expression applies to. |  | Foundations Ch5 |
| **scope of negation** | The part of the meaning that is negated. |  | Cambridge Ch9 |
| **secondary boundary mark** | A comma, semicolon or colon marking boundaries within or between clauses. |  | Cambridge Ch20 |
| **secondary term** | The term expressed in the subordinate comparative clause or phrase. |  | Cambridge Ch13 |
| **segmental** | Occupying a position in the linear sequence of writing, as marks and spaces do. |  | Cambridge Ch20 |
| **semantic role** | The part an entity plays in the situation expressed by a clause, such as agent, patient or goal. |  | Cambridge Ch4 |
| **sentence** | A unit of text, usually realised by a clause or a coordination of clauses. |  | Cambridge Ch2 |
| **sentence terminal** | A mark such as a full stop, question mark or exclamation mark that can end a written sentence. |  | Foundations cgel-ch20 |
| **set comparison** | Comparison among members of a set, often with a superlative. |  | Cambridge Ch13 |
| **simple catenative** | A catenative construction with no intervening NP between the matrix and subordinate verbs. |  | Cambridge Ch14 |
| **simple word** | A word not analysable into smaller morphological units. |  | Cambridge Ch19 |
| **simple-syndetic** | Multiple coordination with a coordinator before the final coordinate only. |  | Cambridge Ch15 |
| **Sister nodes** | Two or more parts that share the same immediate parent in a tree. | sister node, sister constituents, sisters | Foundations Ch2, Foundations br-04 |
| **situation** | Whatever a clause expresses: an action, process, event, state or relation. |  | Cambridge Ch3 |
| **slash** | A mark used for alternatives, fractions, dates or line breaks. |  | Cambridge Ch20 |
| **source** | The starting point of a path or change of location, often marked by from or off. |  | Cambridge Ch4, Cambridge Ch7, Cambridge Ch8 |
| **spatial deixis** | Deixis of location and movement, as with here, there, come and go. |  | Cambridge Ch17 |
| **specifying** | A use of be that identifies the value of a variable, often allowing subject and complement to reverse. |  | Cambridge Ch4 |
| **speech act** | The act performed in speaking, such as asserting, asking or conceding. |  | Cambridge Ch8 |
| **stacked modification** | A sequence in which one modifier is itself modified, as in only very rarely. |  | Cambridge Ch6 |
| **Stem form** | The base form of a verb, such as “go”, “write”, or “inspect”. | stem forms, plain form, base form | Foundations Ch10, Foundations br-10 |
| **stimulus** | The entity or proposition that arouses a feeling, perception or cognition. |  | Cambridge Ch4 |
| **stranding** | The use of a preposition without its complement in the normal post-head position, as in What are you looking at? |  | Cambridge Ch7 |
| **Structural ambiguity** | Two or more readings that arise when the same words can be grouped in different ways. |  | Foundations Ch1, Foundations br-01 |
| **subclausal coordination** | Coordination of phrases or words within a clause. |  | Cambridge Ch15 |
| **subclausal negation** | Negation that affects a constituent without making the whole clause negative. |  | Cambridge Ch9 |
| **Subject** | The part paired with the predicate. In a basic English statement it usually comes before the verb and controls agreement. | subjects | Foundations Ch2, Foundations br-02, Cambridge Ch4 |
| **Subject predicative** | A complement that describes or identifies the subject, as “ready” does in “Mia was ready”. | subject predicatives | Foundations Ch4 |
| **subject-dependent inversion** | Inversion of the subject with a dependent of the verb, as in On board were two nurses. |  | Cambridge Ch16 |
| **subject-determiner** | A genitive NP that combines determiner function with a subject-like relation to the head noun. |  | Cambridge Ch5 |
| **subjectless non-finite** | A non-finite clause with no overt subject, interpreted from context. |  | Cambridge Ch14 |
| **subjunctive** | A finite clause construction using the plain form, as in that he be told. |  | Cambridge Ch11 |
| **submodification** | A structure in which a modifier modifies another modifier, as in quite remarkably well. |  | Cambridge Ch6 |
| **subordinate clause** | A clause that characteristically functions as dependent within a larger construction. |  | Cambridge Ch11 |
| **subordinate negation** | Negation understood in an embedded clause even when marked in the matrix. |  | Cambridge Ch9 |
| **Subordinating conjunction** | A linking word such as “because” introducing a clause that depends on a larger clause. | subordinating conjunctions | Foundations Ch8 |
| **subordinator** | A marker such as that, whether or if that introduces a subordinate clause. |  | Cambridge Ch7, Cambridge Ch11 |
| **suffix** | An affix attached after the base. |  | Cambridge Ch19 |
| **suffixation** | The addition of a suffix to a base. |  | Cambridge Ch18 |
| **superiority** | Scalar inequality in which the primary term is higher on the scale. |  | Cambridge Ch13 |
| **superlative** | A form such as deepest or most efficiently, used to locate the extreme of a scale within a set. |  | Foundations cgel-ch13, Cambridge Ch6, Cambridge Ch13 |
| **supplement** | An expression set apart from the main structure that adds information about an anchor. |  | Foundations cgel-ch15, Cambridge Ch2, Cambridge Ch7, Cambridge Ch8, Cambridge Ch12, Cambridge Ch15, Cambridge Ch20 |
| **supplementary relative** | A prosodically detached relative clause adding information about an antecedent. |  | Cambridge Ch12 |
| **supplementation** | The relation between an anchor and a detached supplement. |  | Cambridge Ch15 |
| **syncretism** | Identity of form between distinct inflectional categories. |  | Cambridge Ch18 |
| **syndetic** | Coordination overtly marked by a coordinator. |  | Cambridge Ch15 |
| **syntax** | The study of how words combine into phrases, clauses and sentences. |  | Cambridge Ch2 |
| **synthetic negation** | Negation marked by a word or affix with another function as well, such as never or un-. |  | Cambridge Ch9 |
| **S′** | Read “S-bar”. In these trees it groups the C position with S, which contains the subject and predicate. | S', S-bar | Foundations Ch8 |
| **S″** | Read “S-double-bar”. It groups the higher C2 position with S′. | S-dbar, S-double-bar | Foundations Ch9 |

### T

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **tag** | A short interrogative clause attached to a preceding clause, typically seeking confirmation. |  | Cambridge Ch10 |
| **temporal anaphora** | Interpretation of a time expression through an antecedent time in the discourse. |  | Cambridge Ch17 |
| **temporal deixis** | Deixis of time, expressed by now, then, yesterday and tense. |  | Cambridge Ch17 |
| **Tense** | A grammatical distinction such as present or past, expressed by a verb form. | tense feature, [pres], [past] | Foundations Ch6, Foundations br-06, Cambridge Ch3 |
| **term comparison** | Comparison between a primary term and a secondary term. |  | Cambridge Ch13 |
| **that relative** | A non-wh relative introduced by the subordinator that. |  | Cambridge Ch12 |
| **theme** | A broad role for an entity involved in a situation without being a prototypical agent or patient. |  | Cambridge Ch4 |
| **to-infinitival** | An infinitival clause introduced by the subordinator to. |  | Cambridge Ch14 |
| **To-infinitive** | A form made from infinitival “to” followed by a base-form verb, as in “to wait”. | to-infinitives, to-infinitival clause, to-infinitival clauses | Foundations Ch10 |
| **tough construction** | A construction such as John is easy to please, with a hollow infinitival complement. |  | Cambridge Ch14 |
| **trajector** | The entity whose location or movement is specified in a spatial relation. |  | Cambridge Ch7 |
| **trans** | Transitive frame: the verb takes one object complement. |  | Tree notation (SynTutor FINAL-D1) |
| **transitive preposition** | A preposition that takes an object NP complement. |  | Cambridge Ch7 |
| **Transitive verb** | A verb used with one direct object in this classification. | transitive verbs, transitive, transitivity, V [trans], [trans] | Foundations Ch4 |
| **Transitive verb (V [trans])** | A verb used with a direct object. Transitivity describes how the verb is used in a particular construction. |  | Foundations br-04 |
| **transitivity** | The presence or absence of a direct object in a clause or verb use. |  | Cambridge Ch4 |
| **triangle** | An unlabelled or partly labelled node standing for a span whose internal structure is not analysed. |  | Tree notation (SynTutor FINAL-D1) |
| **Type I verb** | A verb that takes a clause with its own subject in this pattern, as in “expected [Mia to wait]”. | Type I verbs, V(I) | Foundations Ch10 |
| **Type II verb** | A verb that takes an object and a separate clause whose silent subject is controlled by that object, as in “persuaded Mia [to wait]”. | Type II verbs, V(II) | Foundations Ch10 |

### U

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **unbounded dependency** | A relation in which a fronted phrase is co-indexed with a gap that may be deeply embedded. |  | Cambridge Ch10, Cambridge Ch12 |
| **upward percolation** | The spread of a relative feature from a word to the larger phrase containing it. |  | Cambridge Ch12 |

### V

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **valency** | The set of complement patterns available to a word in a particular sense. |  | Foundations cgel-ch04, Cambridge Ch4 |
| **variable question** | A question asking for the value of a variable, typically with a wh-phrase. |  | Cambridge Ch10 |
| **Verb phrase** | A phrase headed by a verb. The main verb phrase in a basic statement acts as the predicate. | verb phrases, VP, VPs | Foundations Ch2 |
| **verbal negation** | Negation marked in association with the verb, often with not or n’t. |  | Cambridge Ch9 |
| **verbalisation** | The formation of a verb from another base. |  | Cambridge Ch19 |
| **verbless clause** | A clause with no verb, often functioning as an adjunct or supplement. |  | Cambridge Ch14 |
| **vocative** | An expression naming the person being addressed, as in Jo, close the door. |  | Foundations cgel-ch20, Cambridge Ch5, Cambridge Ch10, Cambridge Ch20 |
| **vowel-change plural** | A plural formed by changing the base vowel, as in teeth. |  | Cambridge Ch18 |
| **VP** | Verb phrase: a phrase headed by a verb. Complements are sisters of V; adjunct adverbials are sisters of VP inside a higher VP. |  | Tree notation (SynTutor FINAL-D1) |
| **VP complement** | A verb phrase that serves as the complement of a head, such as an auxiliary. |  | Foundations br-06 |
| **VP-oriented adjunct** | An adjunct that modifies the predicate, such as manner or frequency. |  | Cambridge Ch6 |

### W

| Term | Definition | Also matched as | Source |
|---|---|---|---|
| **weak form** | A reduced pronunciation of a grammaticised word in connected speech. |  | Cambridge Ch18 |
| **wh relative** | A relative clause containing a relative word such as who, which or whose. |  | Cambridge Ch12 |
| **Wh-expression** | A word or group such as “who” or “which book” that can ask for information. | wh-expressions, wh-phrase, wh-phrases | Foundations Ch9 |
| **whether** | A subordinator introducing closed interrogative content clauses. |  | Cambridge Ch11 |
| **word token** | One occurrence of a word in speech or writing. |  | Cambridge Ch1 |
| **written sentence** | A unit of text. In ordinary prose, an initial capital and a terminal mark usually help identify its boundaries. |  | Foundations cgel-clauses |

## Known exclusions and unresolved coverage

- Proper names, place names, and example words used only as data (for example, *Max*, *Mina*, *the robins*) are not dictionary entries.
- Terms that appear only in running prose and were never added to a chapter glossary or key-term list are not guaranteed to be included; this is the main residual gap.
- Cambridge terminology is listed as used by the Cambridge lessons; it is not a Burton-Roberts authority and does not rename B-R nodes.
- Variant definitions across chapters are collapsed to one entry. The source column identifies the books/chapters that use the term; chapter-specific nuances may still need a lesson note.
- No claim is made that this list covers every possible English linguistic term, only the terms codified in SynTutor's two lesson books.
