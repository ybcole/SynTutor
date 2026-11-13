# Cambridge Phase C backlog

Snapshot through the reported-directive prototype. The [master plan](CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md) defines the exit criteria. The [cross-domain QA](CGEL_CROSS_DOMAIN_QA.md) explains the pilot scope decisions.

| Diagnostic specifications | Primary pilot | Supporting pilot | Outside pilot | Production-enabled |
|---:|---:|---:|---:|---:|
| 204 | 20 | 5 | 179 | 0 |

## Next implementation batch

**Auxiliary choice in canonical tags (CLS-182)** is next. Check how tags reuse a matrix auxiliary or require supportive do, with agreement handled separately.

After that batch, triage adjacent diagnostics by governing relation and compatible edits. Use the source and diagnostic family below to find related rules. A catalog entry can share a detector or receive a documented no-detector disposition.

## Pilot groups

| Construction | Primary specs | Supporting specs | Merged evidence | Next action |
|---|---|---|---|---|
| Modal complement form | COMP-034 | — | [#105](https://github.com/ybcole/SynTutor/pull/105) | Validate canonical selection and test fresh cases. |
| Modal stacking | COMP-031 | — | [#107](https://github.com/ybcole/SynTutor/pull/107) | Test variety and ambiguous lexical readings. |
| Supportive do | CLS-100, CLS-126 | COMP-030 | [#108](https://github.com/ybcole/SynTutor/pull/108), [#109](https://github.com/ybcole/SynTutor/pull/109) | Validate question relations and separate auxiliary compatibility from lexical inflection. |
| Perfect, progressive and passive selection | MORPH-026, COMP-035, COMP-036 | — | [#110](https://github.com/ybcole/SynTutor/pull/110), [#111](https://github.com/ybcole/SynTutor/pull/111) | Validate auxiliary roles and test ambiguous simple be controls. |
| Passive causative make | CLS-357 | CLS-1451 | [Review handoff](CGEL_CROSS_DOMAIN_QA.md#cls-357-independent-review-handoff) | Complete independent review of the canonical mapping and learner explanation. |
| Action complement of enjoy | COMP-062 | — | [#106](https://github.com/ybcole/SynTutor/pull/106) | Resolve copular tree grounding and test fresh controls. |
| Determiners on role objects | COMP-087 | PHR-197 | [#114](https://github.com/ybcole/SynTutor/pull/114) | Validate referential object function and broaden role and title controls. |
| Article pronunciation | MORPH-141 | OTH-726 | [#112](https://github.com/ybcole/SynTutor/pull/112) | Validate pronunciation evidence and the read-aloud condition. |
| Main-clause question inversion | CLS-103, CLS-104 | — | [#117](https://github.com/ybcole/SynTutor/pull/117) | Validate question context and canonical grounding. |
| Fronted negative and only inversion | CLS-106, CLS-107 | — | This batch | Validate scope independently and broaden parser coverage, including subordinate clauses. |
| Primary finite negation | CLS-099 | — | This batch | Validate the source of primary scope and extend coverage beyond clause-final not. |
| Negative imperative be | CLS-102 | CLS-131 | This batch | Validate ordinary verbal directive context and broaden parser coverage. |
| Inclusive let’s | CLS-268 | — | This batch | Verify broader subject and parser coverage, including vocatives. |
| Reported negative directives | CLS-270 | — | This batch | Broaden reporting-verb and parser coverage. |
| Imperative verb form | CLS-130 | — | [#115](https://github.com/ybcole/SynTutor/pull/115) | Establish the source of directive intent and validate the resulting finding. |

## Rule-by-rule inventory

**Pilot** means a primary offline implementation exists. **Support** means the entry corroborates a pilot. **Next** identifies the next diagnostic. **Queued** means source and overlap triage is pending in this tracker.

When a batch lands, update the rows and link its evidence. Record canonical grounding, held-out results, independent review, learner explanations and registry activation separately from prototype status.

### Agreement (9)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `PHR-062` | Plural agreement with cattle and police | Ch. 5, pp. 345 | Queued |
| `PHR-065` | Singular agreement with news and shingles | Ch. 5, pp. 346 | Queued |
| `PHR-079` | Agreement with the number as a total | Ch. 5, pp. 350 | Queued |
| `PHR-087` | Demonstrative number agreement | Ch. 5, pp. 352, 353 | Queued |
| `PHR-240` | Singular selection with more than one and one more | Ch. 5, pp. 432 | Queued |
| `PHR-334` | Singular they and finite agreement | Ch. 5, pp. 493, 494 | Queued |
| `PHR-343` | Agreement attraction versus grammatical overrides | Ch. 5, pp. 500, 501 | Queued |
| `PHR-347` | Mass aggregates and agreement | Ch. 5, pp. 504 | Queued |
| `CLS-183` | Agreement with the pronoun in canonical tags | Ch. 10, pp. 893 | Queued |

### Article determiner (19)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `MORPH-041` | Determiners cannot directly govern gerund-participial verbs | Ch. 3, pp. 81, 82 | Queued |
| `COMP-087` | Bare role NP requires determiner in ordinary object position | Ch. 4, pp. 253 | Pilot |
| `PHR-028` | Bare nominal cannot occupy ordinary singular count subject | Ch. 5, pp. 329 | Queued |
| `PHR-043` | Noncount selectors much and a little | Ch. 5, pp. 339 | Queued |
| `PHR-044` | Distributive each and every select count singular | Ch. 5, pp. 339 | Queued |
| `PHR-080` | Singular complement with a great deal of | Ch. 5, pp. 349, 350 | Queued |
| `PHR-084` | Number selection by plural quantity nouns | Ch. 5, pp. 351 | Queued |
| `PHR-088` | Number selection by cardinal determiners | Ch. 5, pp. 352, 353 | Queued |
| `PHR-126` | The cannot serve as a fused determiner-head | Ch. 5, pp. 371 | Queued |
| `PHR-128` | Initial a in embedded numeral modifiers | Ch. 5, pp. 372, 373 | Queued |
| `PHR-133` | All before an indefinite article | Ch. 5, pp. 375 | Queued |
| `PHR-140` | Each as fused head and every as dependent | Ch. 5, pp. 379 | Queued |
| `PHR-157` | Either selects a singular count nominal | Ch. 5, pp. 387, 388 | Queued |
| `PHR-161` | No and none in dependent and fused-head functions | Ch. 5, pp. 390 | Queued |
| `PHR-197` | Bare role nouns in ordinary object position | Ch. 5, pp. 409 | Support |
| `CLS-201` | Set expressions in which partitives | Ch. 10, pp. 903 | Queued |
| `CLS-229` | Exclamative what and singular count NPs | Ch. 10, pp. 919, 920 | Queued |
| `CLS-1036` | Singular-noun coordination cannot satisfy a plural determinative | Ch. 15, pp. 1334, 1335 | Queued |
| `MORPH-141` | Liaison and article choice by sound | Ch. 18, pp. 1618 | Pilot |

### Extra word (7)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `CLS-100` | Supportive do excluded when a lexical clause already has an auxiliary | Ch. 3, pp. 93, 94 | Pilot |
| `COMP-030` | Supportive do is incompatible with other auxiliaries in one chain | Ch. 3, pp. 105 | Support |
| `COMP-041` | Supportive do excluded in idiomatic have got | Ch. 3, pp. 112 | Queued |
| `PHR-381` | Non-expandable declarative complements | Ch. 7, pp. 604 | Queued |
| `CLS-268` | No overt matrix subject before inclusive let's | Ch. 10, pp. 934, 935 | Pilot |
| `CLS-270` | Negating a to-infinitival report of a directive | Ch. 10, pp. 943, 944 | Pilot |
| `CLS-407` | No overt subject in infinitival interrogative complements | Ch. 14, pp. 1264 | Queued |

### Missing word (10)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `CLS-102` | Negative imperatives use supportive do | Ch. 3, pp. 94 | Pilot |
| `CLS-120` | Aspectual used to requires do or to under code ellipsis | Ch. 3, pp. 115 | Queued |
| `OTH-453` | Remote conditional apodosis requires a modal auxiliary | Ch. 3, pp. 199 | Queued |
| `COMP-063` | Peruse normally requires an object | Ch. 4, pp. 221 | Queued |
| `COMP-189` | Unlicensed implicit object for peruse | Ch. 4, pp. 304 | Queued |
| `PHR-083` | Of with plural approximate number nouns | Ch. 5, pp. 351 | Queued |
| `CLS-131` | Supportive do with be in ordinary negative imperatives | Ch. 10, pp. 857 | Support |
| `CLS-320` | Overt object with active believe plus an infinitival | Ch. 14, pp. 1203 | Queued |
| `CLS-408` | Participial NP modifiers without relative markers | Ch. 14, pp. 1265 | Queued |
| `CLS-1095` | Supplementary relative clause requires an antecedent anchor | Ch. 15, pp. 1353 | Queued |

### Other (51)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `OTH-615` | Contraction with coordinated subjects | Ch. 1, pp. 9, 10 | Queued |
| `PHR-054` | Partitive selection with aggregate plurals | Ch. 5, pp. 343 | Queued |
| `PHR-110` | Both as a binary coordination marker | Ch. 5, pp. 361 | Queued |
| `CLS-171` | Negative polarity items in simple positive declarative questions | Ch. 10, pp. 885 | Queued |
| `CLS-1119` | Obligatory gap for the comparative governor counterpart | Ch. 13, pp. 1108 | Queued |
| `CLS-1129` | Subject omission with a retained comparative verb | Ch. 13, pp. 1113 | Queued |
| `CLS-1159` | Fewer with ordinary non-count singulars | Ch. 13, pp. 1127 | Queued |
| `CLS-1166` | To complements of superior and inferior | Ch. 13, pp. 1129, 1130 | Queued |
| `CLS-1188` | Definiteness with attributive same | Ch. 13, pp. 1138 | Queued |
| `CLS-1197` | Complement selection with similar | Ch. 13, pp. 1141 | Queued |
| `CLS-1218` | Nominal complement in the postpositive other than pattern | Ch. 13, pp. 1145 | Queued |
| `CLS-1222` | Anaphoric gap in supplementary reporting as | Ch. 13, pp. 1148 | Queued |
| `CLS-1239` | Like with NP for resemblance and as for capacity | Ch. 13, pp. 1154 | Queued |
| `CLS-1244` | Personal pronoun case after comparative like | Ch. 13, pp. 1156 | Queued |
| `CLS-1259` | Comparative grade in two-member set comparisons | Ch. 13, pp. 1162 | Queued |
| `CLS-1274` | Definiteness in incorporated ranking superlatives | Ch. 13, pp. 1168, 1169 | Queued |
| `CLS-1276` | Integrated relatives after free superlatives | Ch. 13, pp. 1169 | Queued |
| `CLS-1034` | Basic coordination requires equivalent syntactic functions | Ch. 15, pp. 1323 | Queued |
| `CLS-1035` | Infinitival and gerund-participial clause coordination restriction | Ch. 15, pp. 1324 | Queued |
| `CLS-1325` | Unstressed personal pronoun before a verbal particle | Ch. 16, pp. 1383 | Queued |
| `CLS-1329` | Indirect object cannot follow direct object in the double-object alternant | Ch. 16, pp. 1384 | Queued |
| `CLS-1379` | Subject–auxiliary inversion with clausal subjects | Ch. 16, pp. 1406, 1407 | Queued |
| `CLS-1415` | Raised it in clefts and the need for be | Ch. 16, pp. 1419 | Queued |
| `CLS-1425` | Bare who unavailable as a fused-relative pseudo-cleft head | Ch. 16, pp. 1422, 1423 | Queued |
| `CLS-1451` | To in passive counterparts of bare-infinitival actives | Ch. 16, pp. 1432 | Support |
| `CLS-1479` | Be and get in the two perception-verb frames | Ch. 16, pp. 1442, 1443 | Queued |
| `PHR-600` | Every plus singular noun as a reciprocal antecedent | Ch. 17, pp. 1501 | Queued |
| `PHR-601` | Local structural licensing of compound reciprocals | Ch. 17, pp. 1502 | Queued |
| `PHR-602` | Compound reciprocals lack an emphatic adjunct use | Ch. 17, pp. 1502 | Queued |
| `PHR-606` | Subject restriction on verb-domain reciprocals | Ch. 17, pp. 1503 | Queued |
| `PHR-612` | Genitive antecedent exclusion in the mixed verb–noun reciprocal domain | Ch. 17, pp. 1503 | Queued |
| `PHR-620` | Spatial agreement inside a demonstrative NP | Ch. 17, pp. 1505 | Queued |
| `PHR-629` | Nondeictic that as a fused definite determiner-head | Ch. 17, pp. 1508 | Queued |
| `PHR-632` | Countability in fused that and pro-nominal one | Ch. 17, pp. 1508, 1509 | Queued |
| `PHR-644` | Immediate cardinal or no before bare pro-nominal ones | Ch. 17, pp. 1512 | Queued |
| `PHR-645` | Determiners requiring pro-nominal one in the immediate construction | Ch. 17, pp. 1512 | Queued |
| `PHR-653` | Count antecedent restriction on pro-nominal one | Ch. 17, pp. 1515 | Queued |
| `PHR-654` | Dependents of plural pro-nominal ones | Ch. 17, pp. 1515 | Queued |
| `PHR-655` | Content-clause complements of pro-nominal one | Ch. 17, pp. 1515, 1516 | Queued |
| `PHR-656` | Relational PP complements of pro-nominal one | Ch. 17, pp. 1515, 1516 | Queued |
| `PHR-666` | Position of other relative to attributive adjectives | Ch. 17, pp. 1518 | Queued |
| `PHR-673` | Limits on contrasting complements after auxiliary stranding | Ch. 17, pp. 1520 | Queued |
| `PHR-684` | Antecedent head restriction on reduction-driven do | Ch. 17, pp. 1524 | Queued |
| `PHR-696` | Full-complement omission with lexical verbs | Ch. 17, pp. 1528 | Queued |
| `PHR-704` | Auxiliary-headed antecedent exclusion for do so | Ch. 17, pp. 1530 | Queued |
| `PHR-705` | Contrastive objects and do so | Ch. 17, pp. 1530 | Queued |
| `PHR-706` | Do so in comparisons | Ch. 17, pp. 1530 | Queued |
| `PHR-737` | Polarity of additive inverted so | Ch. 17, pp. 1539 | Queued |
| `MORPH-391` | Place names without derived nationality adjectives | Ch. 19, pp. 1696 | Queued |
| `MORPH-480` | Multipliers of hundred | Ch. 19, pp. 1717, 1718 | Queued |
| `MORPH-481` | A and one in composite numerals | Ch. 19, pp. 1718 | Queued |

### Preposition (2)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `COMP-060` | Consist selects of | Ch. 4, pp. 220 | Queued |
| `COMP-128` | Fixed come across cannot undergo ordinary PP-fronting | Ch. 4, pp. 275 | Queued |

### Pronoun case (12)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `COMP-084` | Canonical pronominal subject and object case | Ch. 4, pp. 237 | Queued |
| `PHR-283` | Finite clause subjects and nominative case | Ch. 5, pp. 459 | Queued |
| `PHR-289` | Accusative in ordinary noncoordinate object positions | Ch. 5, pp. 461 | Queued |
| `PHR-290` | Accusative subject of a for-infinitival | Ch. 5, pp. 461 | Queued |
| `PHR-295` | Who as local subject or subjective predicative | Ch. 5, pp. 464, 465 | Queued |
| `PHR-305` | Dependent and independent genitive pronouns | Ch. 5, pp. 470, 471 | Queued |
| `PHR-321` | Own as fused modifier-head | Ch. 5, pp. 483 | Queued |
| `CLS-285` | Accusative pronouns after infinitival for | Ch. 14, pp. 1182 | Queued |
| `CLS-1101` | Reflexive anaphor requires the appropriate local antecedent in a chain | Ch. 17, pp. 1457 | Queued |
| `CLS-1103` | Pride lexically requires the subject-bound reflexive object | Ch. 17, pp. 1488 | Queued |
| `PHR-580` | Subject antecedent of an emphatic clause adjunct | Ch. 17, pp. 1497 | Queued |
| `PHR-582` | Genitive exclusion with NP-internal emphatic reflexives | Ch. 17, pp. 1497 | Queued |

### Punctuation (17)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `OTH-671` | Apostrophe shape in directional typography | Ch. 20, pp. 1725 | Queued |
| `OTH-688` | Main-clause and subordinate embedded questions | Ch. 20, pp. 1733 | Queued |
| `OTH-698` | Single-level constraint for repeated colons and semicolons | Ch. 20, pp. 1737, 1738 | Queued |
| `OTH-699` | Colons and coordinate series | Ch. 20, pp. 1738 | Queued |
| `OTH-701` | Boundary before non-initial bare coordinates | Ch. 20, pp. 1739 | Queued |
| `OTH-708` | Boundary before connective adjuncts joining main clauses | Ch. 20, pp. 1741, 1742 | Queued |
| `OTH-712` | Boundary before direct reported speech complements | Ch. 20, pp. 1743 | Queued |
| `OTH-715` | Comma at the subject–verb boundary | Ch. 20, pp. 1744 | Queued |
| `OTH-717` | Delimitation of vocatives parentheticals and dislocations | Ch. 20, pp. 1745 | Queued |
| `OTH-726` | Article choice before a parenthesised element | Ch. 20, pp. 1748 | Support |
| `OTH-730` | Insulation of parenthesised content | Ch. 20, pp. 1750 | Queued |
| `OTH-737` | Alternation of nested quotation marks | Ch. 20, pp. 1753 | Queued |
| `OTH-740` | Quoted terminal full stop inside a continuing matrix sentence | Ch. 20, pp. 1754 | Queued |
| `OTH-743` | Terminal suppression at the end of a quotation | Ch. 20, pp. 1755 | Queued |
| `OTH-756` | Hyphens in numerals fractions and established formations | Ch. 20, pp. 1761 | Queued |
| `OTH-761` | Genitive apostrophes and personal pronouns | Ch. 20, pp. 1763 | Queued |
| `OTH-764` | Sentence-final abbreviation full stop | Ch. 20, pp. 1764 | Queued |

### Spelling inflection (20)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `PHR-164` | Single-word another in ordinary indefinite noun phrases | Ch. 5, pp. 391 | Queued |
| `MORPH-078` | Consonant doubling before vowel-initial suffixes | Ch. 18, pp. 1575, 1576 | Queued |
| `MORPH-080` | Mute e deletion before ing | Ch. 18, pp. 1576, 1577 | Queued |
| `MORPH-083` | Ie bases and ing spelling | Ch. 18, pp. 1579 | Queued |
| `MORPH-092` | Regular noun plurals with final y | Ch. 18, pp. 1585 | Queued |
| `MORPH-104` | Plural spelling of personal names | Ch. 18, pp. 1595 | Queued |
| `MORPH-105` | Bare and marked genitives | Ch. 18, pp. 1595, 1596 | Queued |
| `MORPH-109` | Adding k after final c | Ch. 18, pp. 1598 | Queued |
| `MORPH-237` | Plural marking in established er plus preposition compounds | Ch. 19, pp. 1655 | Queued |
| `MORPH-258` | Singular measure bases in attributive compounds | Ch. 19, pp. 1660 | Queued |
| `MORPH-309` | Consonant doubling in lexical derivation | Ch. 19, pp. 1675 | Queued |
| `MORPH-311` | Mute e deletion before a vowel-initial suffix | Ch. 19, pp. 1675 | Queued |
| `MORPH-313` | Mute e retention after soft c and g | Ch. 19, pp. 1676 | Queued |
| `MORPH-316` | Y replacement before suffixes | Ch. 19, pp. 1676, 1677 | Queued |
| `MORPH-357` | Negative in alternants in spelling and speech | Ch. 19, pp. 1687 | Queued |
| `MORPH-385` | Invariant inhabitant nouns in Class 1a | Ch. 19, pp. 1694, 1695 | Queued |
| `MORPH-445` | Possessive ed and plural nominal inputs | Ch. 19, pp. 1709 | Queued |
| `MORPH-477` | Uninflected power heads inside numerals | Ch. 19, pp. 1717 | Queued |
| `MORPH-482` | Ordinal formation from the final cardinal base | Ch. 19, pp. 1718, 1719 | Queued |
| `MORPH-483` | Numerator and denominator in fractions | Ch. 19, pp. 1719 | Queued |

### Tense aspect (8)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `CLS-119` | Remote conditional apodosis requires modal auxiliary | Ch. 3, pp. 107 | Queued |
| `OTH-098` | Bare preterite incompatible with present-inclusive ever since | Ch. 3, pp. 141 | Queued |
| `OTH-102` | Definite completed-past adjunct with present perfect | Ch. 3, pp. 143, 144, 146 | Queued |
| `OTH-158` | Backshift choices form a prefix through embedded clauses | Ch. 3, pp. 156 | Queued |
| `OTH-216` | Fixed-composition state rejects ordinary progressive | Ch. 3, pp. 167, 168 | Queued |
| `OTH-377` | Temporal adjuncts disallow ordinary futurity will | Ch. 3, pp. 191 | Queued |
| `OTH-439` | Affirmative could and single-event perfective restriction | Ch. 3, pp. 197 | Queued |
| `OTH-458` | Finite wish complements require preterite for unreal situation | Ch. 3, pp. 200 | Queued |

### Verb form (20)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `MORPH-025` | Preterite licensing in a canonical finite clause | Ch. 3, pp. 76, 77 | Queued |
| `MORPH-026` | Past participle complement of perfect auxiliary have | Ch. 3, pp. 76, 77 | Pilot |
| `MORPH-035` | Degree modification of participial verbs | Ch. 3, pp. 79, 81 | Queued |
| `COMP-031` | Mutual exclusion of core modal auxiliaries in Standard English | Ch. 3, pp. 105, 107 | Pilot |
| `COMP-034` | Central modal selection of the following plain form | Ch. 3, pp. 106 | Pilot |
| `COMP-035` | Progressive be selects a gerund-participle | Ch. 3, pp. 106 | Pilot |
| `COMP-036` | Passive be selects a past participle | Ch. 3, pp. 106 | Pilot |
| `COMP-042` | Bare infinitival complement of had better | Ch. 3, pp. 113 | Queued |
| `OTH-182` | Perfect auxiliaries are not selectable by all catenatives | Ch. 3, pp. 161 | Queued |
| `COMP-061` | Tend selects a to-infinitival action clause | Ch. 4, pp. 220 | Queued |
| `COMP-062` | Enjoy excludes a to-infinitival action complement | Ch. 4, pp. 221 | Pilot |
| `COMP-116` | Do pseudocleft aspect connectedness | Ch. 4, pp. 270 | Queued |
| `COMP-194` | Construct and destroy lack ordinary inchoative uses | Ch. 4, pp. 306 | Queued |
| `WCAT-059` | Prepositional to after adjectives | Ch. 6, pp. 545 | Queued |
| `CLS-126` | Plain form after supportive do in questions | Ch. 10, pp. 856 | Pilot |
| `CLS-130` | Plain form in ordinary imperatives | Ch. 10, pp. 857 | Pilot |
| `CLS-182` | Auxiliary choice and tense in canonical tags | Ch. 10, pp. 892, 893 | Next |
| `CLS-357` | Infinitival marker in passive causative make | Ch. 14, pp. 1234 | Pilot |
| `MORPH-114` | Three-way vowel alternation | Ch. 18, pp. 1603 | Queued |
| `MORPH-130` | Negative am and inversion | Ch. 18, pp. 1612 | Queued |

### Word order (29)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `MORPH-056` | Negative imperative differs from negative infinitival | Ch. 3, pp. 89, 90 | Queued |
| `CLS-099` | Do-support in primary finite negation | Ch. 3, pp. 93, 94 | Pilot |
| `CLS-103` | Inversion of auxiliary and subject in closed interrogatives | Ch. 3, pp. 94, 95 | Pilot |
| `CLS-104` | Main-clause non-subject wh-inversion | Ch. 3, pp. 95 | Pilot |
| `CLS-106` | Clause-scoped initial negative triggering inversion | Ch. 3, pp. 95, 96 | Pilot |
| `CLS-107` | Initial only with clause scope triggering inversion | Ch. 3, pp. 95, 96 | Pilot |
| `CLS-108` | Fronted so and such in result constructions | Ch. 3, pp. 96 | Queued |
| `CLS-114` | One prenuclear auxiliary in subject–auxiliary inversion | Ch. 3, pp. 97 | Queued |
| `CLS-117` | Integrated frequency and modal adverbs after lexical verbs | Ch. 3, pp. 102 | Queued |
| `COMP-033` | Ordering of modal, perfect, progressive and passive auxiliaries | Ch. 3, pp. 105, 106 | Queued |
| `COMP-040` | Dynamic lexical have takes do-support | Ch. 3, pp. 111 | Queued |
| `COMP-085` | Weak object pronoun before verb particle | Ch. 4, pp. 247 | Queued |
| `COMP-138` | Direction adverb versus particle before light NP | Ch. 4, pp. 280 | Queued |
| `COMP-202` | Explain does not license canonical double-object frame | Ch. 4, pp. 309 | Queued |
| `PHR-220` | Post-head restrictor order in compound determinatives | Ch. 5, pp. 423 | Queued |
| `PHR-247` | Such and exclamative what before a | Ch. 5, pp. 435 | Queued |
| `PHR-258` | Pre-head complements adjacent to the noun | Ch. 5, pp. 441 | Queued |
| `WCAT-046` | Placement of degree enough | Ch. 6, pp. 534, 535 | Queued |
| `PHR-420` | Ago and elapsed-time on | Ch. 7, pp. 632 | Queued |
| `CLS-128` | Inversion with a fronted non-subject question phrase | Ch. 10, pp. 856 | Queued |
| `CLS-156` | Single fronting of uncoordinated interrogative phrases | Ch. 10, pp. 874 | Queued |
| `CLS-213` | Clause order after idiomatic how come | Ch. 10, pp. 909 | Queued |
| `CLS-217` | Maximal interrogative phrases | Ch. 10, pp. 910, 911 | Queued |
| `CLS-286` | Position of for and its infinitival subject | Ch. 14, pp. 1182, 1183 | Queued |
| `CLS-333` | Perfect have precedes progressive be | Ch. 14, pp. 1214, 1215, 1216, 1217, 1218, 1219 | Queued |
| `PHR-590` | Distribution of each in split reciprocals | Ch. 17, pp. 1499 | Queued |
| `PHR-593` | Adjunct one and direct-object other | Ch. 17, pp. 1500 | Queued |
| `PHR-748` | Stranding restriction in interrogative fragments with determiners | Ch. 17, pp. 1541 | Queued |
| `PHR-769` | Post-head else and implicit comparison | Ch. 17, pp. 1548 | Queued |
