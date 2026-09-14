# SynTutor Rule-Matrix Master Sheet (deterministic XAI)

This is the authoritative inventory of every linguistic rule that SynTutor's
validation engine can apply. The matrix is **deterministic**: given the same
parse tree, the same input always produces the same verdict — there is no
ML scoring, randomness, or heuristic jitter.

## The pipeline

```
Stage 3   spaCy tokenize + POS          -> tokens (pos, tag)
Stage 4   benepar constituency parse    -> phrase-structure tree
Stage 5   Rule matrix evaluates every   -> per-node verdict:
           parent->child edge             valid / error / unlisted
```

Every non-root node receives a verdict for the edge from its parent, and the
node's **Constraint Matrix Checks** list in the UI is built from its own
verdict plus the verdicts of its immediate children.

## How a rule fires

The engine looks up the pair `(parent TYPE, child TYPE)`. If the pair has a
dedicated rule, it returns `(status, constraint-id, human text)`. If the pair
has no dedicated rule it returns `unlisted` (`C-UNLISTED`, valid-by-default).

> **Coverage guarantee (this sheet is about those dedicated rules):**
> `python3 scripts/audit_rules.py` runs a **99-sentence gold corpus** (51
> grammatical, 48 ungrammatical), asserts that **every** expected verdict
> matches, and fails loudly if any edge type produced by the corpus falls
> through to `C-UNLISTED`. Current status: **888 edges across 0 unrated edge
> types**. Any new structure in a learner sentence either hits a rule below
> or shows up as `C-UNLISTED` in the audit — it can never silently pass.

---

## 1. Sentence level (`S`)

| Child TYPE | Rule / constraint | Verdict logic |
|---|---|---|
| `NP` | `C-SUBJECT-ROLE` | NP is the clause subject; agreement is checked on the predicate edge |
| `VP` | `C-PREDICATE` | Subject–verb agreement + finiteness (see §5, §6) |
| `ADVP` | `C-CLAUSAL-ADVERBIAL` | Clausal adverbial, licensed at sentence level |
| `PP` | `C-CLAUSAL-ADVERBIAL` | PP adjunct modifying the clause (incl. fronted) |
| `SBAR` | `C-CLAUSAL-COMPLEMENT` | Clausal constituent (e.g. `That he left is true.`) |
| `ADJP` | `C-SMALL-CLAUSE-PREDICATE` | Adjective predicate of a small-clause complement |
| `.` `,` `:` `;` `?` `!` | `C-PUNCT` | Terminal/editorial punctuation, not subject to grammatical constraints |
| (other) | `C-UNLISTED` | Valid-by-default; audit must stay at 0 |

## 2. Noun Phrase (`NP` / `NML` / `NX`)

| Child TYPE | Rule / constraint | Verdict logic |
|---|---|---|
| `DT` | `C-DETERMINER` or `C-DETERMINER-AGREEMENT` | Number agreement with head noun (§7) |
| `PRP$` (or `PRP` surfacing as `my/your/our/their/its`) | `C-DETERMINER` | Genitive possessive occupies the determinative slot |
| **bare determiner/possessive with no nominal head** | `C-HEAD-NOUN` **(error)** | `I hate your.`, `She loves my.`, `Their is a problem.` — a determiner/possessive cannot head an NP; add a noun. Exempts standalone demonstratives `this/that/these/those/each/some/one/all/several` (`This is good.`) |
| more than one determinative | `C-DET-STACK` **(error)** | `These my books`, `The my book` rejected |
| `NN`/`NNS`/`NNP`/`NNPS`/`PRP`/`NML`/`NX` | `C-HEAD-NOUN` | The **last** noun is the head (number printed) |
| bare `NN` head in an argument | `C-ARTICLE` **(error)** | Missing article (`Dog is barking.`, `I need new car.`); exempts mass/gerund/institutional nouns (`music`, `swimming`, `home`) |
| 2nd+ noun | `C-NOUN-ADJUNCT` | Compound/adjunct modifying the head (`computer lab doors`) |
| `JJ`/`JJR`/`JJS`/`ADJP` | `C-MOD-POS` | Modifier must **precede** its head noun (`red car` ok, `car red` error) |
| `JJ`/`JJR` `less/fewer/much/many/little/few` | `C-QUANTIFIER` **(error on mismatch)** | `less cookies`→`fewer`, `many apple`→`many apples`, `fewer water`→`less` |
| `CD`/`PDT`/`QP` | `C-MOD-POS` | Numeral/quantifier in modifier position |
| `PP` | `C-NP-POSTMODIFIER` | Prepositional postmodifier of the head |
| `VP` | `C-NP-REDUCED-RELATIVE` | Reduced relative clause (`the man standing there`) |
| `SBAR`/`S` | `C-NP-RELATIVE` | Relative clause (`the man who lives next door`) |
| `CC` | `C-COORDINATOR` | Coordinating conjunction in the NP |
| `NP`/`NML`/`NX` | `C-NP-COMPOUND` | Internal NP structure (nested determiners etc.) |
| `WHNP/WHPP/...` | `C-RELATIVE-*` | see §8 |
| (other) | `C-UNLISTED` | Valid-by-default; audit must stay at 0 |

## 3. Verb Phrase (`VP`)

| Child TYPE | Rule / constraint | Verdict logic |
|---|---|---|
| `MD`/`AUX` (modal, be, have, do) | `C-AUXILIARY` or `C-AUX-FORM` **(error)** | Aux–verb form pairing (§6) |
| 1st `VB*` (head) | `C-HEAD-VERB` | Head verb (finite or non-finite role as parsed) |
| `NN`-headed VP | `C-HEAD-VERB` **(error)** | The parser found no verb head (`I am agree.`) |
| `VB/`VBG/VBN` after aux | `C-AUX-FORM` | Non-finite complement of the auxiliary |
| `VP` | `C-AUX-COMPLEMENT` | VP complement of the auxiliary structure |
| `NP` | `C-DIRECT-OBJECT` or `C-PRONOUN-CASE` **(error)** | Direct object; nominative pronoun object rejected (`call she` → `call her`) |
| `PP` | `C-ADJUNCT` | Oblique/adjunct modifier |
| `ADJP` | `C-PREDICATE-ADJECTIVE` or `C-ADJ-ADV` **(error)** | Predicate adj licensed after linking verbs; adjective after an action verb → adverb (`sings beautiful` → `sings beautifully`) |
| `ADVP` | `C-ADVERBIAL` or `C-ADJ-ADV` **(error)** | Flat adjective as adverb rejected (`runs quick` → `runs quickly`) |
| `SBAR` | `C-CLAUSAL-COMPLEMENT` | Clausal complement (`knows that...`) |
| `S` | `C-SMALL-CLAUSE` | Small-clause/object complement (`made her happy`) |
| `TO` | `C-INFINITIVAL-MARKER` | Infinitival marker `to` |
| `RP` | `C-PARTICLE` | Phrasal-verb particle |

## 4. Prepositional / Adjectival / Adverbial Phrases

| Parent | Child | Rule / constraint | Verdict logic |
|---|---|---|---|
| `PP` | `IN`/`TO` | `C-HEAD-PREPOSITION` | Preposition heads the PP |
| `PP` | `NP` | `C-PREP-OBJECT` or `C-PRONOUN-CASE` **(error)** | Object of the preposition; nominative pronoun rejected (`to she` → `to her`) |
| `ADJP` | `JJ*` | `C-HEAD-ADJECTIVE` | Adjective heads the AP |
| `ADJP` | `RBR`/`RBS` (`more`/`most`) | `C-COMPARATIVE-DOUBLE` **(error)** when a `JJR`/`JJS` sibling exists | `more smarter`, `most biggest` rejected |
| `ADJP` | `RB*` | `C-INTENSIFIER` | Intensifier scope |
| `ADJP` | `VBN`/`VBG` | `C-PARTICIPLE-MODIFIER` | Participle modifier (`very tired`) |
| `ADVP` | `RB*`/`ADVP` | `C-HEAD-ADVERBIAL` | Adverb heads/extends the AdvP |
| `ADVP` | `JJ*` | `C-ADJ-ADV` **(error)** | Adjective inside an adverb phrase |
| `ADVP` | `NP` | `C-ADVERBIAL-COMPLEMENT` | Temporal/measure complement (`an hour ago`) |
| `ADVP` | `CC` | `C-COORDINATOR` | Adverbial coordination |

## 5. Subject–Verb agreement (`C-SUBJECT-AGREEMENT`)

Checked deterministically on the predicate edge between the **subject head**
and the **finite verb head**:

- Number: singular `(3, sg)` vs plural `(3, pl)`; person from `PRP_KEY`
  (`I`→1sg, `he/she/it`→3sg, `they`→3pl, `you`→2nd...).
- Verb form: `VBZ` = 3rd-person singular present, `VBP` = non-3rd-person
  present, `VBD`/`MD` = person-neutral (no conflict).
- **Coordination rule (regression-driven):** a subject NP containing `CC`
  (`Jaisen and Kielle`) is **always plural**, regardless of any conjunct's
  head. `...is...` with a coordinated subject is an error; `...are...` is fine.

### Agreement table (subject key × verb key)

| Verb | Agrees with | Example |
|---|---|---|
| `VBZ` (`runs`, `is`, `has`, `does`) | 3rd-person singular only | `The boy runs.` ✓, `They runs.` ✗ |
| `VBP` (`run`, `are`, `have`, `do`) | anything except 3rd-person singular | `They run.` ✓, `He run.` ✗, `Jaisen and Kielle are...` ✓ |
| `VBD` (`ran`), `MD` (`will`) | person-neutral | `They ran.` ✓, `He will run.` ✓ |

## 6. Auxiliary verb-form selection (`C-AUX-FORM`)

| Auxiliary class | Required main verb | Wrong → Right |
|---|---|---|
| modal (`will`, `can`, `must`...) | base form (`VB`) | `will eats` → `will eat` |
| `do` (`do`/`does`/`did`) | base form (`VB`) | `do runs` → `do run` |
| `have` (`has`/`have`/`had`) | past participle (`VBN`) | `has eat` → `has eaten` |
| `be` (`is`/`are`/`am`...) | participle (`VBG`/`VBN`) | `is runs` → `is running` |

## 7. Determiner–noun number agreement (`C-DETERMINER-AGREEMENT`)

| Determiner | Requires | Example |
|---|---|---|
| `a`, `an`, `this`, `that`, `each`, `every`, `another`, `much` | singular noun | `A dogs` ✗ → `A dog` |
| `these`, `those`, `both`, `many`, `several` | plural noun | `These boy` ✗ → `These boys` |
| others (`the`, `my`, `some`...) | number-neutral | no conflict |

## 8. Relative-clause machinery

| Parent | Child | Rule / constraint |
|---|---|---|
| `SBAR` | `S` | `C-RELATIVE-CLAUSE` — subordinate clause complement |
| `SBAR` | `IN` | `C-COMPLEMENTIZER` — `that`/`because` introducing the clause |
| `SBAR` | `WHNP`/`WHPP`/`WHADVP`/`WPP`/`WADVP` | `C-RELATIVE-HEAD` |
| `WHNP` | `WP`/`WDT`/`WP$` | `C-RELATIVE-PRONOUN` |
| `WHNP` | `NN*` | `C-RELATIVE-NOUN` (`which book`) |
| `WHPP`/`WHADVP`/... | (children) | `C-RELATIVE-HEAD` |

## 9. Finiteness (`C-TENSE-FINITE`)

A main clause requires a **finite** verb:

- Predicate head is `VBG`/`VBN`/`VB` with no auxiliary → error
  (`The boy running.` → add `is` or use `runs`).
- A `to`-infinitive complement clause (`want to go`) is licensed as
  `C-INFINITIVAL-COMPLEMENT` — no finite form required.
- Input parses as a fragment (no `S` root) → error (`fragment root`,
  e.g. a bare NP with no predicate).

## 10. Punctuation & roots

| Constraint | Meaning |
|---|---|
| `C-PUNCT` | Terminal punctuation, exempt from grammatical checks |
| `C-ROOT` | A proper `S`/`SINV`/`SQ`/`SBARQ`/`FRAG` root spanning the sentence, or a fragment (error when not a clause). |
| `C-CAPITALIZATION` **(error)** | Sentence begins with a lowercase word (`he runs fast.` → `He runs fast.`) |

## 10b. Pronoun case (`C-PRONOUN-CASE`)

A strict nominative/objective split is enforced:

| Position | Must be | Wrong → Right |
|---|---|---|
| Clause subject | nominative (`I`, `we`, `he`, `she`, `they`) | `Me likes music.` → `I like music.`, `Him is running.` → `He is running.` |
| Direct object | objective (`me`, `us`, `him`, `her`, `them`) | `They call she a hero.` → `call her` |
| Object of preposition | objective | `to she` → `to her`, `for he` → `for him` |
| After a copula (`It is I.`) | exempt (standard English) | — |

## 10c. Article & determiners (`C-ARTICLE`, `C-ARTICLE-MISMATCH`)

- **Missing article**: a bare singular common noun in an argument position
  (`Dog is barking.`, `I need new car.`, `He is doctor.`) is rejected.
  Exempt: mass nouns (`water`, `music`), gerund/activity nominals
  (`swimming`, `Reading is fun.`), institutional nouns (`go home`), and
  `next/last/this/that + noun` time expressions (`next door`, `last night`).
- **a–an selection**: phonetic, not orthographic — `a elephant`→`an elephant`,
  `an waiter`→`a waiter`, with exceptions `an hour/honest/heir` (silent `h`)
  and `a university/union/one-time` (vowel letter, consonant sound).

## 11. Case-B remediation (auto-generated fix guides)

Every `error` node now carries a `remediation` block
(`violation`, `suggested_fix`, `alternative_fix`, `targeted_outcome`):

| Constraint | Suggested fix produces | Example |
|---|---|---|
| `C-SUBJECT-AGREEMENT` | re-conjugated verb (or plural/singular subject alternative) | `are`→`is` / `a light`→`lights` |
| `C-DETERMINER-AGREEMENT` | pluralized/singularized noun or swapped determiner | `boy`→`boys` / `These`→`This` |
| `C-AUX-FORM` | correct complement form (base / `-en` / `-ing`) | `eat`→`eaten` |
| `C-DET-STACK` | removal of the extra determiner | drop `the` from `the my book` |
| `C-MOD-POS` | reordered modifier (`JJ + NN`) | `car red`→`red car` |
| `C-TENSE-FINITE` | finite verb / added auxiliary; fragment→full clause | add `is`, or `runs` |
| `C-HEAD-NOUN` | a noun supplied after a bare determiner | `your` → `your idea` |
| `C-PRONOUN-CASE` | the correct nominative/objective pronoun | `she` → `her` (object) |
| `C-ADJ-ADV` | the `-ly` adverb form | `quick` → `quickly`, `beautiful` → `beautifully` |
| `C-ARTICLE` | indefinite article inserted before the noun | `doctor` → `a doctor` |
| `C-ARTICLE-MISMATCH` | swapped `a`/`an` to match the sound | `a elephant` → `an elephant` |
| `C-CAPITALIZATION` | capitalized first letter | `he` → `He` |
| `C-QUANTIFIER` | `less`↔`fewer`, `much`↔`many`, `little`↔`few` | `less cookies` → `fewer cookies` |
| `C-COMPARATIVE-DOUBLE` | only the morphological form kept | `more smarter` → `smarter` |
| `C-HEAD-VERB` | a genuine verb head for the VP | `agree`(NN) → an auxiliary + verb |
| other/fallback | generic guidance citing the failing check | — |

## Full constraint-ID index

`C-SUBJECT-AGREEMENT` `C-PREDICATE` `C-TENSE-FINITE` `C-SUBJECT-ROLE`
`C-DETERMINER-AGREEMENT` `C-DETERMINER` `C-DET-STACK` `C-HEAD-NOUN`
`C-NOUN-ADJUNCT` `C-MOD-POS` `C-HEAD-VERB` `C-AUXILIARY` `C-AUX-FORM`
`C-AUX-COMPLEMENT` `C-DIRECT-OBJECT` `C-ADJUNCT` `C-PREDICATE-ADJECTIVE`
`C-ADVERBIAL` `C-CLAUSAL-COMPLEMENT` `C-CLAUSAL-ADVERBIAL` `C-PARTICLE`
`C-HEAD-PREPOSITION` `C-PREP-OBJECT` `C-HEAD-ADJECTIVE` `C-INTENSIFIER`
`C-PARTICIPLE-MODIFIER` `C-HEAD-ADVERBIAL` `C-COORDINATOR`
`C-NP-POSTMODIFIER` `C-NP-REDUCED-RELATIVE` `C-NP-RELATIVE` `C-NP-COMPOUND`
`C-CLAUSE-SUBJECT` `C-CLAUSE-PREDICATE` `C-RELATIVE-CLAUSE`
`C-RELATIVE-HEAD` `C-RELATIVE-PRONOUN` `C-RELATIVE-NOUN` `C-COMPLEMENTIZER`
`C-PUNCT` `C-ROOT` `C-UNLISTED` (never silent — reported by the audit)
`C-PRONOUN-CASE` `C-ADJ-ADV` `C-ARTICLE` `C-ARTICLE-MISMATCH`
`C-CAPITALIZATION` `C-QUANTIFIER` `C-SMALL-CLAUSE` `C-SMALL-CLAUSE-PREDICATE`
`C-ADVERBIAL-COMPLEMENT` `C-COMPARATIVE-DOUBLE` `C-INFINITIVAL-COMPLEMENT`
`C-INFINITIVAL-MARKER`.

## Keeping it green

```bash
python3 scripts/audit_rules.py   # must print: gold regressions=0  unrated_edge_types=0
```

To add a rule: implement a branch in `MatrixEvaluator._classify()` (or a
`_rem_*` helper for Case-B), add the constraint id to `CHECK_LABELS` /
`_role_for`, then add grammatical/ungrammatical examples to `GOLD` in
`scripts/audit_rules.py` and rerun. If the new edge type cannot be closed,
the audit will list it as `C-UNLISTED` — always visible, never silent.