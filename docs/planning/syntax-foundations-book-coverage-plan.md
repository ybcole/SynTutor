# Syntax Foundations full-book revision master plan

**Purpose.** Use this file to implement and review SynTutor's Syntax Foundations lessons. Cover the full teaching sequence of Chapters 1–11, with a traceable place for each book subsection, its substantive distinctions, and the skills developed in its exercises. Use the same lesson UI and page layout.

**Source.** Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax*, third edition, Pearson, 2011, ISBN 9781408233740. The matrix uses printed pages. The uploaded third-edition PDF supplies the contents, chapter text, figures, and exercise discussions. Printed pages 6–268 correspond to PDF pages 21–283 in that copy. Division names within the tables are paraphrased for planning. Use the existing book-aligned chapter titles in the catalog and learner-friendly headings inside the chapters. [Reference copy](https://fliphtml5.com/nvdvc/grsk/Analysing_sentences___an_introduction_to_English_syntax/) · [Edition and source manifest](../../sources/burton_roberts/source_manifest_2026-11-08.json)

**App baseline.** `feat/lessons/revision-integration` at `bf60d8b`, including the plain-language revisions and chapter introductions. The regular Lessons entry point loads the `br-01`–`br-11` overlays and the corresponding article modules. Plan against the composed chapter, including its interactive blocks and assessments. The base catalog and legacy articles can describe earlier versions. Main and the revision branch had diverged when this plan was written. Recheck both tips before implementation and bring forward the newer Foundations prose. Work within the Syntax Foundations track.

**Implementation.** The baseline ratings below record what was available before the earlier coverage revision. The grouped route table reflects the current implementation. All 100 coverage IDs map to teaching and feedback in [the Foundations coverage blocks](../../web/js/foundations-book-content.js). Each ID is attached to a specific lesson page and is also the heading ID in the reader. The existing recaps include the additional distinctions. Chapter 7 has a dedicated appendix page in the normal navigation. Chapters 5, 6, 7 and 10 use the existing tree controls for the VP-layer, passive-question, pro-NOM and non-finite relative comparisons. Added practice is unscored, so the saved completion requirements, graded questions and XP rules can keep their existing versions.

## How to use the coverage matrix

- **Taught** means an explanation and a usable example exist. Retain them, check the linked practice, and add only what the row calls for.
- **Partial** means the page mentions the topic, combines it with another topic, or teaches only some of the source's cases. The action column names what learners still need.
- **Missing** means the baseline lacks a usable explanation for that source topic. Add it and validate the corresponding example and practice.
- A printed subsection gets an explicit heading or identifiable block in the chapter. Group two to four related teaching subsections on each reading page when they share a question or diagnostic. Use a single-topic page for a substantial trace, proof, or practice that needs room. Keep existing routes for opening, hands-on work, recaps, and closing checks. Teach the subsection blocks before the worked activity so learners use what they have just read. Every teaching row needs an original example, an explanation of how to read it, and a way to apply the method. One practice item may cover multiple rows if its feedback explains each distinction. Use integrated walkthroughs and optional practice for depth. All source topics must be reachable from the normal chapter, including the Chapter 7 appendix and Chapter 9's further applications.
- The page ranges and patterns below seed the implementation inventory. Before editing each chapter, read its body, figures, in-text tasks, answer discussions, and further exercises. Record distinct cases taught inside them, even where there is no printed heading. Split a matrix row if its cases need different teaching blocks. Finish only when the checked inventory maps every distinct case to rendered content and evidence. A source figure or ambiguous passage needs page-level review before claiming its coverage.
- Introduce notation and terms in the explanation at first use. Maintain general definitions in the existing introduction's Key terms box. Open chapters with a question or situation tied to the chapter topic, and put the example on the same page as its explanation. Teach with short sentences and concrete comparisons while retaining technical terms. Keep the book attribution and page or figure references in the existing recap disclosure.
- Preserve the sidebar, mobile contents disclosure, current page chrome, typography, themed spacing, navigation, key-terms box, canvas controls and Builder layout. Use existing examples, traces, practice and disclosure components. Include **Read tree as text** above **Tree notation** for each applicable lesson tree. Add content pages through existing registration only when needed for readable pacing. Keep Chapter 11's written synthesis activities.
- Book pp. 1–5 supply course orientation. Add one short orientation in Chapter 1 about studying sentence structure, trying a diagnosis before looking at a worked answer, and revisiting earlier chapters for notation. Prefaces, reading list and index can be referenced from the course documentation. The conceptual and exercise coverage requirement applies to Chapters 1–11, including their appendix and summaries.

## Grouped reading pages

Use the page IDs below for navigation and the coverage IDs for subheadings. The table shows source order within each reading group. Introductions, worked traces, and existing transfer activities can stay on their own routes. Where the book has a summary and worked exercise discussions, adapt them into the recap and original practice with feedback.

| Chapter | Lesson page and subsections in order |
| --- | --- |
| 1 | **Structure and constituent tests** (`concepts`): structure and hierarchy, then ways to establish constituents (BR01-01–02). **Read and repair a phrase marker** (`worked-example`): phrase vs. constituent, brackets, dominance and triangles (BR01-03). **Explain two readings** (`application`): exercise and further-exercise skills (BR01-P). |
| 2 | **Subject, predicate, NP and VP** (`concepts`): subject and predicate, then the categories of the two phrases (BR02-01–02). **Read and repair the top split** retains the guided practice. **Heads, modifiers and complements** (`application`): dependency and function, heads, modifier–head, and head–complement (BR02-03–06). **Recap**: summary and mixed worked exercise (BR02-P). |
| 3 | **Nouns and noun phrases** (`concepts`): noun tests and subclasses, then lexical vs. phrasal categories (BR03-01–02). **Adjectives, adverbs and their phrases** (`worked-example`): word categories, then AP/AdvP (BR03-03–04). **Prepositional phrases and coordination** (`prepositions-and-coordination`): P/PP, then coordinated words and phrases (BR03-05–06). **Application**: diagrams, exercise skills and feedback (BR03-P). |
| 4 | **Lexical verbs, complements and transitivity** (`concepts`): verb forms, complement selection, transitive verbs and intransitive verbs (BR04-01–04). **Follow both objects**: ditransitives and their NP/PP alternatives (BR04-05). **Intensive and complex transitive verbs** (`predicatives`): subject and object predicatives (BR04-06–07). **Compare three uses of PPs**: prepositional verbs alongside contrasting PP functions (BR04-08). **Application and recap**: six-pattern table and practice (BR04-P). |
| 5 | **Adjuncts and levels of VP** (`concepts`): VP adjuncts and levels of VP (BR05-01–02). **Worked example** retains the multi-layer trace and repair. **Mobility** (BR05-03) and **Phrasal verbs and ellipsis** (`particles`, BR05-04–05) follow, with the existing `ellipsis` page for tracing an understood complement. **Application**: VP vs. sentence adverbials and mixed practice (BR05-06, BR05-P). |
| 6 | **Tense, lexical verbs and modals** (`concepts`): tense/time, the lexical–auxiliary contrast and MOD (BR06-01–03). **Perfect, progressive and passive auxiliaries** (`chain`): PERF, PROG, PASS and auxiliary VP structure (BR06-04–07). **Adverbials** bridge to Part II (BR06-08). **Passive** and **negation** retain separate constructions and traces (BR06-09–10). **Questions and uses of have and be** (`questions`): fronting and the lexical/auxiliary contrast (BR06-11–12). **Recap**: practice in both parts (BR06-P). |
| 7 | **Determiners and pre-determiners** (`concepts`): DET/NOM and the larger PRE-DET construction (BR07-01–02). **Worked example** retains the NP trace and repair. **Pre-modifiers**: pre-modifier overview, QA, PartP, and N (BR07-03–06). **NOM layers and post-modifiers** (`post-modifiers`): recursion, PPs and APs (BR07-07–09). **Application**: modified pronouns, ellipted heads and mixed practice (BR07-10, BR07-P). **Appendix**: the pro-NOM diagnostic and worked practice (BR07-11–12). |
| 8 | **Embedding and complementisers** (`concepts`): clause nesting and abbreviated analysis, then `that`, `whether` and `if` (BR08-01–02). **Worked example** retains the C/S trace. **Clausal subjects and verb complements**: extraposition and V complements (BR08-03–04). **Clauses inside AP, NP and PP** (`clausal-complements`): A, N and P complements (BR08-05–07). **Adverbial clauses** and **Application**: adverbial clause types and mixed practice (BR08-08, BR08-P). |
| 9 | **Main questions** and **Worked example** introduce fronting (BR09-01). **Embedded interrogatives**: subordinate clause types and their question construction (BR09-02–03). **Relatives, omitted wh-phrases and that** (`relatives-and-complements`): relative vs. noun complement, omission, and relative `that` (BR09-04–06). **Relative scope**: restrictive vs. non-restrictive analysis (BR09-07). **Application**: exercise discussions, deeper questions and relative attachment (BR09-P, BR09-08–09). |
| 10 | **Introduction**: non-finiteness and overt, free and controlled subjects (BR10-01). **Forms**: the four non-finite forms (BR10-02–05), then the existing infinitival VP repair. **Complementisers and wh-phrases** (`subjects-and-control`): C1 and C2 (BR10-06–07). **Subjects, complements and adverbials** (`clause-functions`): subject/extraposition, A complement, P complement and adverbial (BR10-08–11). **Non-finite clauses in noun phrases** (`noun-clause-functions`): N complements and NOM modifiers (BR10-12–13). **Verb complements**: clause selection, then Type I/II (BR10-15 and BR10-14). **Application**: mixed analysis and passive tests (BR10-P). |
| 11 | **Languages and how to describe them** (`concepts`): varieties and the task of describing a language (BR11-01–02). **Worked example**: finite rules for unbounded sets (BR11-03), then apply the recursion rule. **Grammar and sentence analysis** (`rule-and-structure`): what a grammar specifies and how it assigns structure (BR11-04–05). **Application** keeps written synthesis. |

## 1 · Sentence structure: constituents (pp. 6–23)

**Baseline route.** Words form groups → Test a group in context → Read and repair a phrase marker → Explain two readings → recap and checks. Open with the existing landmark example.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR01-01 · 6–9 | Structure, grouping and hierarchy | Taught | Keep the nested example. Explicitly connect parts, their arrangement, and their roles. Compare a word sequence with a structurally ill-formed ordering and show why a flat tree misses a group. |
| BR01-02 · 10–14 | Finding constituents | Partial | Retain omission, substitution and wh-answer evidence. Add a worked movement test, a failed boundary test, and an obligatory constituent that survives another diagnostic. Compare the same string in two contexts where it is a constituent in only one. |
| BR01-03 · 15–18 | Phrases, constituents and their representation | Partial | Distinguish a constituent as a part of a larger unit from the category of that unit. Compare brackets, triangle shorthand and expanded trees. Teach the all-and-only dominance test, direct versus indirect dominance, and two structures for one string. |
| BR01-P · 19–23 | Exercises, solutions and further practice | Partial | Add original multi-layer bracket-to-tree and ambiguity tasks. Reveal both groupings and explain one tempting wrong bracket boundary. |

## 2 · Sentence structure: functions (pp. 24–45)

**Baseline route.** Two groups, two functions → Find the complete subject → Read and repair the top split → Read relations between sisters → recap and checks.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR02-01 · 24–28 | Subject and predicate | Partial | Keep the full-span and yes/no question tests. Compare a short and a long subject, and show mutual dependence of subject and predicate in the basic clause pattern. Use an auxiliary in the diagnostic and leave full inversion analysis for Chapter 6. |
| BR02-02 · 29–30 | NP and VP at the first split | Taught | Keep NP/VP under S and contrast grammatical category with grammatical job. Give a fresh NP in subject and non-subject jobs so the distinction transfers. Have learners pair a plausible subject and predicate and identify a phrase of neither category. |
| BR02-03 · 31–32 | Dependency, function and sister relations | Partial | Reuse the tree and add a comparison of sisters and their common parent. Locate the relevant sister relation inside a nested phrase. |
| BR02-04 · 32 | Heads and phrase identity | Taught | Compare heads from two phrase categories. Show why the whole phrase has the category of its head. |
| BR02-05 · 32–35 | Modifier and head | Partial | Model one-way dependency and optionality, including a phrase doing the modifying. Use the same intended reading across the omission pair. |
| BR02-06 · 35–37 | Head and complement | Partial | Give two-way dependency in a selected use, compare a P plus its NP with a modifier plus head, and show how deleting a constituent can change the reading. |
| BR02-P · 38–45 | Summary, practice and feedback | Partial | Give a three-way comparison for subject–predicate, modifier–head and head–complement. Add a nested analysis with feedback on categories, functions and evidence. Include matching phrases to structures, drawing an unseen structure, and interpreting ambiguous modifier scope. |

## 3 · Sentence structure: categories (pp. 46–66)

**Baseline route.** Words and phrases have categories → Find the noun and the whole phrase → Read an AP and its adverb phrase → Join two prepositional phrases → transfer, recap and checks.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR03-01 · 46–49 | Distribution and noun subclasses | Partial | Explain distribution using interchange in a sentence frame. Compare plural and possessive forms, proper versus common, count versus mass, determiner frames and a noun that changes count interpretation. |
| BR03-02 · 50–54 | Word and phrase categories | Taught | Keep N versus NP, names, pronouns and one-word phrase examples. Extend with head selection from a multi-noun NP, agreement evidence, and a pronoun replacing the whole NP. |
| BR03-03 · 54–55 | Adjectives and adverbs | Partial | Teach gradable and non-gradable uses, comparative and superlative forms, and the limits of `-ly` as a category clue. Include an adverb without `-ly`. |
| BR03-04 · 55–56 | AP and AdvP | Partial | Compare head and degree modifier in an AP and in an AdvP, including one-word forms. Trace an AdvP inside an AP and ask learners to distinguish its own head from the AP head. Include recursive modification by successive degree adverbs in the exercise discussion on pp. 63–65. |
| BR03-05 · 56–57 | Prepositions and PPs | Taught | Keep P + NP and a standalone locative PP, including the book's treatment of locative pro-forms. Contrast category with the location job. Verify book-specific borderline cases before adding them. |
| BR03-06 · 57–62 | Coordination | Partial | Move beyond PP coordination to NPs, agreement, adjective and other same-category coordination, word versus phrase coordination, shared versus local modifier scope, and cases where unlike categories can fill the same function. Confirm the book's alternative structures and coordinator placement. |
| BR03-P · 62–66 | Diagrams, practice and answer discussion | Partial | Add original lexical-versus-phrasal examples with both structures and a mixed-category justification. Require a category clue and a function for each selected group. Include identifying words and complete NPs in context, then a tree where an unexplained interior can be abbreviated with a triangle. |

## 4 · The basic Verb Phrase (pp. 67–86)

**Priority pilot.** The revised article already compares `Nora waited`, `Nora inspected the bridge`, and two uses of `opened`. The distinction lives under **Find the verb and its complements**, and the first closing item asks for VP spans. The revision should give transitive and intransitive uses their own visible teaching blocks and test whether students can distinguish their complement patterns. This chapter is the check that the plan improves discoverability as well as coverage.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR04-01 · 67–68 | Recognizing verbs | Partial | Add word-class and form diagnostics, including `-s`, `-ing`, `-ed` and `-en` forms or their irregular counterparts. Separate the lexical head from auxiliaries and compare a word used as a verb and as a noun. |
| BR04-02 · 68–70 | Lexical verb complements | Partial | Start with what a verb requires in a particular use. Contrast required and optional material, and explain why an optional PP leaves the subcategory unchanged. Introduce the six patterns before tracing them in book order. |
| BR04-03 · 70–71 | Transitive verbs | Partial | Teach one direct object NP and the V–object sister relation. Compare subject and object pronoun forms, the book's case governance terminology, and how `[trans]` encodes the complement pattern. Ask for the feature and the evidence. |
| BR04-04 · 71–72 | Intransitive verbs | Partial | Teach the zero-complement VP as its own block. Contrast a verb used both ways, an independently intransitive verb, and an intransitive VP with a place adjunct. Trace which material is inside the basic VP. |
| BR04-05 · 72–74 | Ditransitive verbs | Partial | Keep the two-NP and `to` PP pair. Add a `for` beneficiary example, distinguish roles from ordering and category, and show both basic VP structures. |
| BR04-06 · 74–76 | Intensive verbs | Partial | Name the copula and teach AP, NP and PP subject predicatives. Ask what receives the property or location, and contrast an NP predicative with an NP object in a fresh pair. |
| BR04-07 · 76–78 | Complex transitive verbs | Partial | Keep the AP object predicative and add NP and source-supported PP cases. Compare two NPs in a ditransitive VP with NP + NP in a complex-transitive VP. Show how the object and predicative relate and compare with the corresponding intensive clause. |
| BR04-08 · 78–79 | Prepositional verbs | Taught | Keep the three similar-looking PPs: selected PP, subject predicative, and adjunct. Add a new comparison where the particular P is selected. Have the learner identify the PP's job before reading the feature label. |
| BR04-P · 79–86 | Summary, practice and answer discussion | Partial | Retain the six-pattern recap and extend the classification practice so all six have fresh evidence. Include a branch repair and a same-verb construction task covering intransitive, transitive and intensive uses. Compare all four PP jobs encountered by this point, including an indirect object expressed by a PP. |

**Suggested first pass.** Open with the existing inspection/waiting context. Follow with recognition and lexical selection. Put named transitive and intransitive blocks on the current concepts page or adjacent pages. Continue to ditransitives, subject predicatives, object predicatives, and the PP comparison. Use the existing tree repair and finish with the existing six-pattern recap expanded around a decision procedure. A learner should be able to find and apply the difference between `[trans]` and `[intrans]` from the chapter contents route.

## 5 · Adverbials and other matters (pp. 87–110)

**Baseline route.** Basic VP → attach an adjunct → mobility → particles → understood material → scope.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR05-01 · 87–88 | VP adjuncts | Taught | Retain PP, AdvP and NP adjuncts. Compare time, duration or frequency with manner and other meanings. Explain that adverbial is a job available to several categories. |
| BR05-02 · 88–92 | VP levels and the `do so` pro-form | Partial | Add two adjuncts and a third VP layer. Trace the sister of V versus the sister of VP, and use `did so` with alternate spans to explain the grouping. |
| BR05-03 · 92–93 | Mobility | Partial | Keep the edge-position variants. Include a medial or displaced adjunct and explain where the book's simple phrase markers stop representing surface placement. |
| BR05-04 · 93–96 | Phrasal verbs | Partial | Teach a particle and a P in matching contexts, object placement with full NPs and pronouns, and a further book-supported particle pattern. Trace particles separately from a full PP. |
| BR05-05 · 96–98 | Ellipsis | Partial | Compare an understood required complement with an optional adjunct. Explain E, context recovery, and the difference between sentence structure and an acceptable utterance in context. Discuss ambiguous cases where the same surface verb might have an understood object or a separate intransitive use. |
| BR05-06 · 98–101 | Sentence adverbials | Partial | Keep disjuncts and conjuncts. Compare event modification, speaker comment, and links across discourse, using contrasting positions and the correct S attachment. |
| BR05-P · 101–110 | Worked solutions and further practice | Partial | Add original mixed attachment, particle and ellipsis tasks. Require a diagnostic and show how the tree records the result. Add two readings that change the verb subcategory, plus a PP attachment pair contrasting a noun modifier with a VP-related reading. |

## 6 · More on verbs: auxiliary VPs (pp. 111–140)

**Baseline route.** Auxiliary heads and chain → adverbials → passive → negation → questions. Preserve the book's Part I (form and structure) before Part II (constructions).

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR06-01 · 111–114 | Inventory, finiteness, tense and time | Partial | Compare primary and modal auxiliaries. Show tense marking on the first verb, subject–verb agreement, regular and irregular forms, and present/past tense versus past/present/future time reference. |
| BR06-02 · 114–115 | Lexical verbs versus auxiliaries | Partial | Compare complementation, the behavior of a following infinitival `to`, and the question/negation diagnostics that Part II works through. |
| BR06-03 · 115–116 | Modal auxiliaries | Partial | Teach first position, finite-only use, a single modal, agreement behavior and stem selection. Show a natural future or modal meaning without treating it as a separate future tense. |
| BR06-04 · 116–118 | Perfect `have` | Partial | Compare a clear irregular perfect participle with a matching regular past and participle form. Distinguish perfect meaning from past tense and trace the `MOD → PERF` sequence. |
| BR06-05 · 118–119 | Progressive `be` | Partial | Trace `-ing` selection, inherited position in the chain and the difference from lexical `be`. Provide a pair where only one `be` is progressive. |
| BR06-06 · 119–121 | Passive `be` | Partial | Contrast passive participle and progressive `-ing` forms, including a chain with both. Present active versus passive in Part II after teaching the form. |
| BR06-07 · 121–123 | Auxiliary VP hierarchy | Taught | Keep the nested chain. Show why the lexical V and its complements remain one constituent and why an auxiliary's VP position does not make it an adjunct. Use ellipsis evidence and trace a longer chain. |
| BR06-08 · 123–125 | Adverbials within auxiliary VPs | Partial | Compare pre-verbal placement, final default attachment and the final time-adverbial exception. Demonstrate a meaning difference between two attachments. |
| BR06-09 · 125–128 | Passives | Partial | Keep the simple passive. Add optional `by` adjunct, unchanged verb subcategory, which verbs allow passives, complex transitives retaining their predicative, and both ditransitive configurations in the book. |
| BR06-10 · 128–130 | Negation and auxiliary `do` | Partial | Explain placement and contraction of `not`, the tense carrier and the lexical stem. Contrast lexical and auxiliary `do`, and add the book's emphatic use where it belongs. |
| BR06-11 · 130–132 | Yes/no questions | Partial | Teach the C and S′ configuration, `do` when needed, and two distinct gaps in a passive question. Ask which overt item belongs to each gap. |
| BR06-12 · 132–133 | Additional uses of `have` and `be` | Partial | Retain lexical `be` inversion and add negation. Contrast lexical and perfect `have`, including both lexical question/negative patterns where the source recognizes them, with a variety note. |
| BR06-P · 133–140 | Separate Part I and Part II practice | Partial | Retain work on the order and tense of auxiliaries. Add practice on coordination, form selection, adverbial scope, and transformations. Give worked answers for both parts and show intermediate steps. Include finding lexical and auxiliary forms in a passage, distinguishing the three uses of be, and explaining what is wrong in an ill-formed chain. |

## 7 · The structure of Noun Phrases (pp. 141–170)

**Baseline route.** DET/NOM → build the basic NP → modifiers before and after the head → transfer. The appendix adds a diagnostic and refines the earlier analysis.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR07-01 · 141–145 | Basic NP and determiners | Partial | Keep DET/NOM, ART, DEM, possessives, empty DET and the name/pronoun exception. Add plural count versus mass versus singular count comparisons for empty DET, determiner competition, and an expanded nested possessive NP. |
| BR07-02 · 145–146 | Pre-determiners | Taught | Keep the PRE-DET + NP trace. Add a fresh contrast that tests the difference from DET and which combinations the source permits. |
| BR07-03 · 146 | NOM pre-modifiers | Partial | Introduce the modifier types together and then trace them in order. Compare a degree-bearing AP and an AP consisting of a single adjective. |
| BR07-04 · 146–147 | Quantifying adjectives | Partial | Expand QA, including numeral cases, and show its position relative to DET and other modifiers. |
| BR07-05 · 147–148 | Participial phrases | Partial | Trace a PartP as its own category. Contrast participial and adjectival uses using the book's diagnostics, including the limits of degree modification. |
| BR07-06 · 148–149 | Noun pre-modifiers | Partial | Trace a noun–noun compound and contrast it with independently attached AP or PartP modifiers. Explain the noun modifier's position and the head that controls the phrase. |
| BR07-07 · 149–150 | Recursive NOM layers | Taught | Keep the layered AP analysis. Add a two-modifier grouping that requires explaining scope and why a modifier forms a unit with a particular NOM. |
| BR07-08 · 150–154 | Post-modifying PPs | Partial | Compare nested PP attachment and competing readings, combine a pre-AP with a post-PP, and show the book's partitive cases where applicable. |
| BR07-09 · 154–155 | Post-modifying APs | Partial | Compare an AP before the noun with a complemented AP after it. Explain the distribution and meaning of the source's position-sensitive examples. |
| BR07-10 · 155–157 | Pronoun modification and elliptical heads | Partial | Retain an indefinite pronoun with a modifier. Add an AP/PP comparison and the source's elliptical-head analysis for superficially similar determiner or pre-determiner cases. |
| BR07-P · 157–164 | Diagrams, practice and answer discussion | Partial | Assign an original NP with possession, a pre-modifier, and an ambiguous post-modifier. Reveal both attachment readings and name the evidence. Use the p. 163 contrast between QA and a multiword determiner, including the special uses of `a few` and `a little`. |
| BR07-11 · 165–168 | Appendix: `one` as a NOM pro-form | Missing | Give `one/ones` a named block in the chapter. Use it to distinguish a complement beside N from a modifier beside NOM. Show when the earlier simple analysis requires refinement and label the appendix convention consistently. |
| BR07-12 · 169–170 | Appendix worked answer and further practice | Missing | Give a fresh mixed complement/adjunct test with `one`, and show the resulting trees. Include the appendix's determiner and substitution limits where relevant. Bridge to Chapter 9's relative-clause diagnostic. |

## 8 · Sentences within sentences (pp. 171–195)

**Baseline route.** Find nested clauses → read C and S → subjects and objects → heads and complements → adverbial clauses → trace deeper embedding.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR08-01 · 171–173 | Clause nesting and abbreviated analysis | Partial | Keep compound versus complex and nested clauses. Add an explicit abbreviated clausal analysis with lexical verbs, main and subordinate spans, and the superordinate host of each embedded clause. |
| BR08-02 · 174–176 | C, S and clause introducers | Partial | Keep `that`, empty C and `whether`. Add the distribution of interrogative `if`, and connect the C position to Chapter 6 and the two C positions in Chapter 9 without conflating them. |
| BR08-03 · 176–179 | Clausal subjects and extraposition | Partial | Compare an initial subject clause, optional extraposition and a context requiring extraposition. Distinguish expletive from referring `it` and show the matching bracket/attachment. |
| BR08-04 · 179–181 | V complements | Partial | Teach an object clause with passive evidence and an intensive verb with a clausal subject predicative. Give a close pair with the same complementiser but a different function. |
| BR08-05 · 181–182 | A complements | Partial | Trace a clause within AP. Contrast it with a nearby extraposed subject and identify the host in both trees. |
| BR08-06 · 182–184 | N complements | Taught | Keep the content-clause relation within NP. Add a new abstract noun and a brief contrast with a modifier, preparing for Chapter 9. |
| BR08-07 · 184–186 | P complements | Partial | Compare a licensed `whether` clause and the `that` limitation after P, plus temporal P with an embedded clause. Show the two levels of attachment. |
| BR08-08 · 186–188 | Adverbial clauses | Partial | Compare temporal and causal `since`, and distinguish subordinating conjunctions (including a multiword case) from P taking a clause. Contrast VP and S adverbial functions using contexts that make both readings clear. |
| BR08-P · 188–195 | Worked discussion and further practice | Partial | Give one layered sentence mixing functions. Ask for each clause's span, introducer, host and function. Use worked feedback to connect the abbreviated map with the expanded analysis. Give named extension cases for the object-side extraposition and displaced noun-content clauses raised on p. 195. Have learners identify each clause’s source function and host, with the proposed analysis attributed in the recap. |

## 9 · Wh-clauses (pp. 196–223)

**Baseline route.** Main questions → trace an object question → embedded interrogatives → relative versus content clause → attachment and scope.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR09-01 · 196–202 | Main wh-questions | Partial | Start from the answer to find the gap. Build the inventory of wh-expressions and full phrases, including a possessive, a degree phrase, subject and object NPs, AdvP and PP. Compare stranding, fronted PP, and echo questions. Teach the book's main subject-question analysis first and label its alternatives in a disclosure. |
| BR09-02 · 202 | Subordinate wh-clauses | Taught | State the two major branches of the chapter at the transition: embedded interrogatives and relatives. Use the same wh-word to show how the construction and its host change the interpretation. |
| BR09-03 · 202–204 | Embedded wh-interrogatives | Partial | Compare C1 and C2 with a matched main question. Add host and function variety and trace a gap across a deeper clause boundary. |
| BR09-04 · 204–207 | Relatives and N complements | Partial | Keep the noun-content contrast. Add the `one` diagnostic from Chapter 7, and explain the sister-of-N versus sister-of-NOM structures and how a relative gap is linked back. |
| BR09-05 · 207 | Omitted wh-expression | Partial | Show object omission, then the restrictions with a subject gap and with a wh-expression that moved along with a P or a noun. Keep the gap and link visible in the structure. |
| BR09-06 · 207–208 | Relative `that` | Partial | Compare complementiser `that` in a noun complement with `that` in a relative, showing relative `that` in C2 in the adopted analysis and explaining the C1 alternative separately. |
| BR09-07 · 208–211 | Restrictive and non-restrictive relatives | Partial | Retain the two attachments. Compare subset versus parenthetical meaning, commas, antecedent scope, and restrictions on `that` and omission. Finish with the three attachment sites N, NOM and NP. |
| BR09-P · 211–220 | Worked discussion and main practice | Partial | Add original transformations for fronting and clause type, plus a three-tree comparison for noun complement, restrictive relative and non-restrictive relative. |
| BR09-08 · 220–221 | Further question and interrogative applications | Partial | Add a full long-distance derivation, showing the category and position of each gap. Include a source-supported contrast involving subject-question C1 where the reading needs it. |
| BR09-09 · 221–223 | Further relative-clause applications | Partial | Add complex relatives with possessive or locative wh-phrases, plus mixed abbreviated analyses that classify clauses, hosts and gaps. Show both analyses where a sequence is ambiguous and include the restriction on narrowing reference for a uniquely identifying name. |

## 10 · Non-finite clauses (pp. 224–253)

**Baseline route.** Four forms → infinitival VP repair → subjects and control → clause functions → Type I versus Type II → transfer. Preserve Part I before Part II.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR10-01 · 224–225 | Form, subjects and control | Taught | Keep finite/non-finite contrasts, overt/covert subjects, free and controlled interpretations, and co-indexing. Add a multiple-gap example only after single-gap cases are clear. |
| BR10-02 · 225–226 | Bare infinitives | Taught | Compare the same stem as finite and untensed. Give a new bare infinitival clause whose subject or verb pattern must be justified. |
| BR10-03 · 226–227 | To-infinitives | Partial | Keep `to` as an untensed auxiliary and its stem complement. Add legal PERF/PROG/PASS sequences and explain why a finite modal cannot fill that position. |
| BR10-04 · 227–228 | Passive participles | Partial | Trace a passive-participial clause with its own overt subject and another with a covert subject. Distinguish the object gap from subject control. |
| BR10-05 · 228–229 | `-ing` participles | Partial | Contrast a bare non-finite `-ing` clause with progressive `be`, including a book-supported stative or non-progressive use. |
| BR10-06 · 229–230 | Complementisers and C1 | Partial | Teach the distribution of `for` with an overt subject and interrogative `whether`. Contrast the complementiser and lexical uses of the same word where helpful. |
| BR10-07 · 230–232 | C2 fronting and covert wh | Partial | Trace non-finite wh-interrogatives and the unspoken relative wh-expression. Keep separate indices or labels for wh, subject/control and any passive gap. |
| BR10-08 · 232–233 | Subjects and extraposed subjects | Partial | Compare `-ing`, to-infinitival and `for` subject patterns as licensed. Add extraposition, expletive `it` and the source's restrictions on which form can appear where. |
| BR10-09 · 233–234 | A complements | Partial | Contrast subject-controlled AP complements with the object-gap pattern. Compare referring `it` and extraposition using a fresh ambiguous pair. |
| BR10-10 · 234 | P complements | Taught | Keep the existing `-ing` example. Compare a P-selected clause with a similar-looking adjunct and explain their hosts. |
| BR10-11 · 234–235 | Non-finite adverbials | Partial | Compare purpose and participial adjuncts, source-supported overt and covert subject cases, and which controller is available. |
| BR10-12 · 235 | N complements | Partial | Show a noun whose complement states the content of a plan, request or similar meaning. Contrast it with a restrictive NP modifier. |
| BR10-13 · 235–236 | NP modification | Partial | Add full examples of infinitival, `-ing` and passive-participial relatives licensed by the source. Show restrictive attachment and trace the covert wh-expression and its gap. |
| BR10-15 · 236–239 | Verb complements and selection | Partial | Compare finite and non-finite complements, accepted forms, embedded interrogatives and meaning changes when the same verb selects a different form. |
| BR10-14 · 239–244 | Intervening NPs and Type I/II | Partial | Compare overt embedded subject with higher direct object and covert subject. Use expletive `there`, semantic selection and subject-control `promise`; explain why pronoun case or an understood subject alone does not settle the analysis. |
| BR10-P · 244–253 | Diagrams, discussion and further practice | Partial | Add original abbreviated analyses that mark each missing item and controller, including a multi-reading AP case and a comparison of Type I and II. Include ambiguity resolved by indexing alone, a diagnostic contrasting a referring pronoun and a gap, and the p. 253 passive-paraphrase test for Type I versus Type II. Explain why changing the lower subject preserves the believed situation in a Type I example but can change the addressee or acceptability with Type II. |

## 11 · Languages, sentences and grammars (pp. 254–268)

**Baseline route.** Compare lists and rules → recursive trace → rule application → licensed structures → derive a new sentence. Keep the existing written synthesis route and add depth through rule exercises.

| ID / printed page | Source topic | Baseline | Revision and evidence |
| --- | --- | --- | --- |
| BR11-01 · 254–257 | Languages and varieties | Partial | Teach a language as a set of sentences in the book's argument, then explain why speakers' sets may overlap without matching. Use a variety-aware example and state which variety the task describes. |
| BR11-02 · 257–259 | Describing a language | Partial | Compare observed examples with all sequences available to a speaker. Use a finite toy list to frame membership, then add a novel sentence and ask why listing attested examples is insufficient. |
| BR11-03 · 259–262 | Finite descriptions of infinite languages | Taught | Keep the recursive coordination exercise. Add natural clause/relative embedding as another route to unboundedness and compare the book's flat and recursive formulations. Ask how the same finite rules can be reused. |
| BR11-04 · 262–265 | What a grammar specifies | Partial | Give an explicit finite set of rules and lexical choices, then test which sequences it licenses. Connect a speaker's implicit knowledge with an analyst's explicit description. Place the historical discussion in a short source note. |
| BR11-05 · 265–268 | Grammars and sentence analysis | Partial | Extend the mini grammar so learners derive and compare structures for novel sentences. Show both membership and grouping, including rules that overgenerate and a revision prompted by evidence. Keep the final answer in the existing written comparison format. |

## Implementation sequence

1. **Confirm the release baseline.** Compare the latest revision branch and main. Inventory the live `br-*` chapter titles, section IDs, authored modules, data overlays, assessment versions and publication route. Keep the current design as the visual baseline. Main's Cambridge work shares the catalog and rendering modules. Preserve it and record any targeted integration necessary to use the same Foundations recap disclosure.
2. **Make Chapter 4 the coverage pilot.** Fill every Chapter 4 row in book order. Verify that a learner can find the two named transitivity blocks, recognize each complement pattern in new sentences, repair the appropriate branches, and explain one contrasting case without prior knowledge of the book. Review content and navigation in the current lesson chrome.
3. **Establish Chapters 1–3, then complete Chapters 5–7.** Work through each chapter individually. Treat the movement/complex phrase work in Chapter 1, dependency in Chapter 2, distribution and coordination in Chapter 3, VP levels in Chapter 5, auxiliary contrasts in Chapter 6, and the NOM appendix in Chapter 7 as required content. Recheck Chapter 4's cross-links when these are in place.
4. **Complete Chapters 8–11.** Finish embedding before wh-fronting, then non-finite clauses and control, then the written grammar synthesis. Reuse notation and diagnostics from earlier chapters and include the short source-oriented recap in each chapter.
5. **Run an integrated release check.** Check the normal Lessons route and the bundled Foundations preview against the same inventory. Check the boundaries with Cambridge, Builder and Generator, especially the shared catalog and renderer. Record results by chapter and use the existing deployment path once the review is complete.

### Per-chapter work order and definition of done

1. **Inventory.** Expand the matrix into a section- and case-level ledger for this chapter. Each entry records its ID, printed page and figure or exercise when relevant, the existing article block or assessment that establishes its baseline, the target section ID, the original example, and practice or feedback evidence. Tag a source reference by what was actually reviewed. Maintain source receipts through the repository's existing workflow.
2. **Teach.** Keep the contextual opener and sequence the blocks in book order. For each concept, give a plain-language definition, an example with the relevant words visible, a diagnostic or contrast, and a reading of any resulting tree. Give feedback for likely mistakes. In the recap, summarize the reasoning steps from the chapter, and use fresh examples in the checks. Use original prose, trees and practice scenarios. Place advanced cases in existing disclosures or extra sections with names that students can find.
3. **Wire.** Edit `web/js/*-pilot.js` and `web/content/lessons/br-XX-pilot.json` for the chapter, using the same structures and CSS as its current lesson. Reuse stable IDs and keep existing deep links working. If extra section IDs become required, keep `required_sections`, the article renderer and navigation in agreement. Review the existing content-version behavior before changing progress requirements, question IDs, answers or XP. Prepare explicit version handling when the old progress or quiz records would otherwise be interpreted against different content. Preserve one-time awards and existing account/device behavior. Amend the base catalog or shared modules only when the composed release requires it.
4. **Verify.** Run the relevant chapter browser test, composed catalog validation, lesson and assessment suites, applicable tree schema/convention validation, and static build. Verify every opening/closing answer and map opening/closing questions to outcomes. Keep every outcome covered by the closing check even if shared runtime validation is weaker. Use additional in-page practice to assess finer concepts. On desktop and mobile, confirm Contents and Next/Previous navigation, deep links, intro, practice and recap, the source disclosure, text and notation dropdowns, keyboard access, and any Builder activity. Check saved progress and assessments with both old-version and fresh state when the contract changes.
5. **Record.** Mark each ledger row only after its learner-facing block and evidence are verified. List source gaps, unverified figures or incomplete exercises explicitly. A chapter is ready when every entry has an implemented and verified destination, including cases found in the exercises. Entire-track acceptance requires all eleven chapter records and an integrated regression check.

### Existing verification entry points

- Fixtures and catalog composition: `scripts/test_foundations_preview_catalog.py`, `scripts/compose_foundations_preview.js`, and `scripts/validate_lessons.py`. Capture baseline validation results before changing lesson data so an existing receipt problem can be distinguished from a new one.
- Per-chapter and integrated browser checks: `scripts/test_chapter_*_pilot_browser.py`, `scripts/test_foundations_preview_browser.py`, and `scripts/test_lessons_browser.py`. Use the chapter file matching the work and the normal-route integration checks before release.
- Contracts and packaging: `npm run test:lessons`, `npm run test:assessments`, `npm run test:builder` when an activity changes, and `npm run build`. Validate new tree envelopes against the canonical schema and the chapter convention. Check that shipped overlays include the new content.

**Prompt for the later revision.** Implement this master plan chapter by chapter within the current Syntax Foundations design. Start with the baseline and source inventory, then deliver Chapter 4 as the coverage pilot. For every chapter, turn each source block and distinct exercise skill into traceable instruction and practice. Preserve existing UI components and progress behavior. Report the completed matrix IDs, source pages, changed files, validation results and remaining items after each chapter.
