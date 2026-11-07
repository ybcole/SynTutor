CHAPTER III
RESEARCH METHODOLOGY
This chapter presents the methodology, system design, algorithms, and processes used to develop Syntutor. It describes the use of Agile-Scrum methodology in creating a sophisticated linguistics tool. The chapter also discussed the conceptual framework, data gathering procedures, and algorithms implemented for the generation of syntax trees and the Explainable AI (XAI) component, namely with neural constituency parsing, recursive-descent parse-string decoding, deterministic constraint-matrix evaluation, positive-evidence lexical licensing, and the hybrid acceptability-detection and correction-search channels. Ultimately, how the program will be validated will be discussed to ensure that the system is reliable for its intended users and meets aligned research standards.



3.1 SOFTWARE DEVELOPMENT METHODOLOGY

In integrating NLP with deterministic linguistic reasoning, Syntutor is developed with an iterative and adaptive approach, as required by its complex computational requirements. The researchers utilizes the Agile-Scrum methodology to create the Syntutor linguistic tool. This methodology provides a dynamic framework that involves continuous testing, immediate integration based on feedback, and the rapid-paced refinement of both graphical user interface (GUI) and the system’s engineering.


3.1.1 The Agile-Scrum Methodology
   Figure 3.1.1 Agile-Scrum Methodology

To iteratively construct Syntutor, the study adopts the Agile-Scrum methodology illustrated in Figure 3.1.1. The methodology follows a continuous pipeline that takes the project into cyclical, rapid development iterations known as sprints to produce the web application. The process begins by establishing the project's foundational scope, which defines the project boundaries, target domain, and core system objectives. These requirements are organized into the Product Backlog, serving as the centralized prioritized repository of all features, technical tasks, and definition of rules, including the NLP pipeline (spaCy tokenization plus the benepar neural constituency parser), the recursive-descent parse-string decoder, the deterministic Linguistic Constraint Matrix, the positive-evidence licensing layer, the hybrid acceptability detector and correction-search channel, and the interactive syntax-tree and practice-quiz interfaces. Following the backlog creation, the Design stage focuses on the system architecture, UI/UX wireframing for the website's interface of the tree renderer, state machine logic, and the database schemas for authentication.


Once the initial scope and design are established, development enters the iterative Scrum lifecycle. Each cycle begins with a sprint planning meeting where the research team selects priority tasks from the product backlog in order to populate the sprint backlog, establishing the deliverables from that iteration. During the cycle's Sprint Execution, active coding and algorithm development takes place. The researchers conduct daily Scrums with alignment meetings to track progress, address bottlenecks, and refine the performance of Syntutor's logic. Within each sprint, Sprint Automation incorporates automated testing workflows to verify that the Linguistic Constraint Matrix produces zero regressions and zero unrated edge types, and that the rule suites, licensing tests, and gold-corpus audit remain green. At the end of each iteration, a Sprint Review Meeting is held to demonstrate the working software to the research adviser to evaluate its functionality. This is immediately followed by a Sprint Retrospective where the team evaluates the development process and identifies operational improvements before moving into the next cycle.
The continuous cycle ultimately culminates in producing a usable software, resulting in a deployed web application wherein learners can input sentences, explore interactive syntax trees, and receive deterministic and real time explanations of grammatical concepts.








3.2 CONCEPTUAL FRAMEWORK
   Figure 3.2.1 System Architecture of Syntutor

Figure 3.2.1 presents the pipeline architecture of SynTutor, which processes English text into interactive syntax trees, rule-based explanations, and gamified quiz feedback. Traditional Grammar Error Correction (GEC) tools often overwrite errors without explaining the underlying grammar rules, causing learners to rely on automated fixes rather than building grammatical skills. SynTutor resolves this by separating detection from explanation. A trained acceptability classifier detects whether a sentence reads as natural English, while a deterministic Linguistic Constraint Matrix and lexical licensing layer explain why a structure is valid or invalid and how to repair it. As shown in Figure 3.2.1, the architecture consists of two main containers:


The ALGORITHMS Container (Left): Houses six governing modules: Neural Constituency Parsing (benepar_en3), Recursive-Descent Parse-String Decoding, Deterministic Constraint-Matrix Validation (XAI), Positive-Evidence Lexical Licensing, Hybrid Acceptability & MLM Correction Search, and Procedural Quiz Sampling & Exponential XP Leveling.


The SYNTUTOR Pipeline (Center): Connects eight system components across three feedback paths: the Candidate Re-parse Loop, the Quiz Entry Loop, and the User-Driven Re-entry Loop.


3.2.1 USER INPUT
Serves as the system's entry point where the learner submits an English sentence, a short passage, or a Matrix Quiz repair. The component captures the raw string and the selected sentence_index and passes them downstream without altering the text.


3.2.2 PREPROCESSING
Uses spaCy's en_core_web_md model to perform sentence segmentation, tokenization, case normalization, lemmatization, and fine-grained Part-of-Speech (POS) tagging. Attaching fine-grained POS tags and lemmas directly to the rebuilt tree allows morphology-sensitive rules to look beyond coarse phrase labels.


3.2.3 NLP PARSING ENGINE
Forms the computational core (server/parse_engine.py) across a three-stage stack:
Tokenization and POS Tagging: Reads the segmented tokens, lemmas, and Penn POS categories produced by spaCy (en_core_web_md).


Constituency Parsing: Applies the pre-trained, non-generative benepar_en3 neural constituency parser to emit a parenthesized phrase-structure parse string for the target sentence.


Parse-String Decoding: Uses a custom recursive-descent decoder and NodeBuilder to convert the bracketed string into a serializable node graph, collapse redundant single-child unary chains, and enforce a span-alignment guard so that leaf nodes match the token count.


3.2.4 SELECTED SYNTAX TREE
Represents the single validated constituency tree spanning from the root S node through phrase categories (NP, VP, PP, SBAR) down to terminal word leaves. Because the tree is reconstructed and validated rather than generatively guessed, all downstream XAI evaluations rest on a verified structure.


3.2.5 ERROR DETECTION & XAI
Evaluates the Selected Syntax Tree using four coordinated sub-modules:


Linguistic Constraint Matrix (server/matrix.py and server/ruleset.py): Evaluates every parent-child edge E(vd,vp) across 11 grammatical categories and classifies each edge into one of three states:
valid: The edge (vdvp) is licensed and maps to a positive role explanation template.
error: The edge violates a rule constraint, returning a specific C-* code, an error explanation, and a repair suggestion.
unlisted: No rule covers the edge, recording it for gold-corpus audits.


Positive-Evidence Lexical Licensing (server/licensing.py): 
	Queries lemminflect and inflect to ensure every open-class word is a valid inflection for its parser-assigned POS tag. It strips suffixes to catch malformed inflections (such as "childs", "runned", or "stupids"), checks relative-clause rules (2.7 and 5.4), and isolates each checker so a single error degrades the verdict to unverified rather than crashing.


Hybrid Acceptability Detector (server/detector.py): 
	Runs a CoLA-fine-tuned RoBERTa classifier (textattack/roberta-base-CoLA) to check overall acceptability. A sentence is marked grammatical only if both the rule matrix and the model accept it. If the rules are clean but the model rejects the sentence, the verdict becomes unverified instead of fabricating a rule violation.


Correction Search (server/corrector.py): 
When a sentence is unverified, a masked-language-model sweep (distilbert-base-uncased) masks one word at a time to find a single-token replacement that shares the same lemma in lemminflect and flips the CoLA classifier to acceptable. Through the Candidate Re-parse Loop, the corrected sentence is re-parsed through Preprocessing and the NLP Parsing Engine, promoting the error to ungrammatical (C-MLM-ANOMALY) only if the repaired tree passes the Constraint Matrix cleanly.


3.2.6 OUTPUT GENERATION
Translates structured diagnostic results into plain-language instructional feedback (summary and precomputed node_details). When all edges and words are valid (grammatical), it activates positive templates that explain the grammatical role of each constituent. When a violation is found (ungrammatical), it outputs the violated rule and suggested repair. When the verdict is unverified, it honestly reports that the rules could not explain the model's rejection.


3.2.7 USER INTERFACE
Renders the node graph as an interactive syntax tree on an HTML5 Canvas (TreeRenderer), colors nodes and edges by validation status, and displays XAI explanations when learners click or navigate nodes with arrow keys. It also hosts the Matrix Quiz module. As shown by the two outbound loops in Figure 3.2.1, the User Interface initiates the Quiz Entry Loop (routing quiz repairs through the NLP and XAI pipeline for verification) and the User-Driven Re-entry Loop back to User Input.


3.2.8 GAMIFICATION & PERSISTENCE
Manages quiz progression and cloud storage (web/js/quiz/level.js, web/js/quiz/achievements.js, web/js/auth.js, and supabase/migrations/). Correct quiz repairs award +5XP each with a +5XP flawless-run bonus, advancing learners along an exponential leveling curve (BASE_SPAN = 50, SPAN_GROWTH = 1.6) and unlocking 14 deterministic achievements. When signed in via Clerk, JWT session tokens authorize Row-Level Security (RLS) synchronization with three Supabase PostgreSQL tables: public.analysis_history, public.player_stats, and public.quiz_progress.




3.3 ALGORITHMS
The Syntutor system combines a trained neural parser with a set of deterministic algorithms: neural constituency parsing, recursive-descent parse-string decoding, the deterministic constraint-matrix evaluation that provides the XAI reasoning, a positive-evidence lexical-licensing algorithm, and a hybrid acceptability-detection and correction-search layer. The trained channels decide whether an input is acceptable and where a mismatch sits; the deterministic algorithms decide why, and produce the teaching explanation. These components work together to transform raw text into a learning tool by processing structural dependencies. Each component handles a specific task and ensures that there is linguistic accuracy being presented without the “black-box” aspect most common grammar tools exhibit.
The parser is a neural constituency model (benepar). It resolves the ambiguity of English syntax by ranking candidate phrase-structure parses and returning the single highest-scoring tree for the sentence, so that a word's role, for example, whether a form is a verb heading a Verb Phrase or a noun heading a Noun Phrase, is fixed before any rule is applied. The decoder then turns that bracketed tree into a node graph with exact token spans. The constraint matrix then evaluates every parent-child edge deterministically, and the licensing layer confirms that every open-class word is a form of the lexicon sanctions for the tag it received.
The XAI structural validation works alongside the system’s parsing engine, creating a transparent feedback that identifies grammatical relationships while explaining their correctness to the user. The explanations happen automatically with the deterministic mapping of the tree’s nodes, wherein results will appear as annotations on the side of the syntax tree. Through this, learners gain a learning tool for understanding sentence construction as conveniently presented in Syntutor.The neural parser and the deterministic rule matrix create a structured parsing pipeline: the parser fixes the most probable syntax tree while the matrix, reinforced by licensing, validates and explains it. These work together with the hybrid detection channel, resulting in an intuitive program with transparent explanations for learning linguistics.


3.3.1 NEURAL CONSTITUENCY PARSING (FORMALIZATION)
Human language is inherently ambiguous (e.g., prepositional phrase attachment ambiguity, where "I saw the man with the telescope" yields multiple valid syntax trees). To computationally determine the correct hierarchical structure, Syntutor models English syntax with a neural constituency parser rather than a hand-authored grammar.
Formally, let the input sentence be a sequence of tokens w = (w₁, w₂, …, wₙ). A preprocessing function P maps the raw string to a token sequence together with a coarse Part-of-Speech tag for each token:


P(text) = ((w₁, t₁), (w₂, t₂), …, (wₙ, tₙ))


where tᵢ is the Penn-style tag spaCy assigns to token wᵢ. A (non-generative) parser function Φ then assigns a single constituent tree T over that token sequence:
 
Φ(w, t) = T = argmax over candidate trees of score(T | w)


Selected Structure
The candidate tree returned by the parser spans from the root S node through phrase categories (NP, VP, PP, …) down to the terminal words, and is emitted as a parenthesized phrase-structure string. The key property Syntutor relies on is the same one a probabilistic model would provide: the parser returns one best, well-formed, S-rooted constituent tree that every downstream stage can trust.
In practical terms within the Syntutor system, this single-tree selection is what prevents the system from generating nonsensical diagrams. Because the structure is fixed before any rule fires, the system guarantees that a word like "bark" in the sentence "The dog barks" is evaluated as a verb attached to a Verb Phrase (VP) rather than as a noun referring to tree bark. The neural parser translates abstract linguistic ambiguity into one definite structural foundation, ensuring the structure is accurate before the Explainable AI (XAI) evaluates it. The parser is a fixed, pre-trained model: it is applied, not trained, at inference time, and identical serialized input always yields the same tree.


3.3.2 PARSE-STRING DECODING AND SPAN ALIGNMENT
Because the parser emits a bracketed string rather than a data structure, Syntutor reconstructs the tree with a recursive-descent decoder. The decoder treats the parenthesized parse as a small formal language over three token kinds, open parenthesis, close parenthesis, and non-parenthesis symbols, recognized with the regular expression:


( | ) | [^ \s ( )]+


A recursive procedure then reads one node at a time: on "(", it consumes the following symbol as the node's phrase label and parses each child until the matching ")"; a bare symbol becomes a terminal leaf. A node with exactly one child (a unary chain) is collapsed to that child, so the tree contains no redundant single-branch nodes. The decoder raises a failure if it meets a trailing token or a malformed structure, preventing a silently corrupted tree.


The NodeBuilder then assigns each node a deterministic identity and geometry: 
a pre-order id (n0, n1, …);
 for a leaf, its Part-of-Speech tag as its type, its surface word, and a one-token span [i, i+1);
for an internal node, its phrase label as its type, the space-joined surface of its leaves, and a span [first, last) computed as the union of its children's spans; 
a punctuation flag for terminal tags in the punctuation set ( . , : ; ? ! `` '' -RRB- -LRB- ).


Alignment Guard 
After building, the number of consumed leaves must equal the sentence's token count; otherwise the decoder raises a failure. This guard guarantees that every node's token-coordinate span lines up exactly with spaCy's token stream, which the front end depends on to map a learner's caret position and node clicks to the right words. The result is a serializable graph of nodes, edges, parent-child dependencies, and depth levels, the direct blueprint for the interactive canvas.


3.3.3 DETERMINISTIC CONSTRAINT-MATRIX VALIDATION (XAI)
Once the parser and decoder have produced the data structure, the XAI module operates on top of the generated tree. The XAI does not use generative guessing; it uses a deterministic algorithmic mapping based on the structural dependencies calculated during the parse.
Let V be the set of all nodes in the generated syntax tree T, and let every non-root node v be paired with its parent node v_p. The system evaluates every parent-child edge E(v_d, v_p) against a hand-authored Linguistic Constraint Matrix, denoted as C, whose entries are deterministic functions of the parent and child Part-of-Speech classes. The relationship-evaluation function determines the system's output:






Valid State Execution:
If the edge (v_d, v_p) is licensed by C, the edge is marked valid and the system extracts the properties of v_d and v_p and maps them to a pedagogical explanation template. For example, subject-verb agreement is confirmed by comparing the number/person key of the subject head with the verb's form; a match yields a role explanation naming the subject label and the verb form.


Error State Execution:
If the edge violates a constraint in C (e.g., a determiner whose number requirement conflicts with its noun, or a subject and predicate that disagree), the system records the specific constraint identifier (a C- code) representing the syntactic rule violation and interpolates the exact structural conflict into a rule-based message, together with a repair suggestion derived from the same deterministic lexicon and morphology helpers.
Every edge is therefore classified into exactly one of three states, valid, error, or unlisted, and the sentence summary is computed by a small set of deterministic counters: the number of validated, violated, and unrated edges, the set of distinct constraints that fired, and a final three-state verdict (grammatical when nothing fired and every word licensed, ungrammatical when a violation exists, and unverified when a word or checker could not be confirmed). Because evaluation is a single traversal in which each edge is decided in constant time, the pass runs in linear time, O(|V|), over the tree, fast enough to explain a sentence in real time.
This exact mathematical linkage between the parser's output and the XAI's deterministic evaluation ensures that all educational feedback provided by Syntutor is computationally verifiable, structurally sound, and entirely free from "black-box" hallucinations.
By structuring the algorithm as a sequential pipeline, where the neural parser establishes the definite structure and the XAI evaluates constraints against that exact structure, Syntutor achieves full transparency. Unlike commercial grammar tools that rely on opaque sequence-to-sequence prediction, this deterministic approach ensures that every piece of feedback provided to the learner is directly anchored to a visible, verifiable node in the syntax tree.


3.3.4 POSITIVE-EVIDENCE LEXICAL LICENSING
A rule matrix alone is a blacklist: a sentence is "valid" whenever no hand-written rule fires, which makes the absence of a rule indistinguishable from grammaticality. The licensing algorithm closes this gap by demanding positive evidence for every open-class word.
For each open-class leaf (nouns, verbs, adjectives, adverbs) with surface s and parser-assigned tag t, the algorithm converts the Penn tag to a universal Part-of-Speech class and queries the deterministic lexicon (lemminflect) for the lemma and inflectional paradigm. A word is licensed when its surface is a listed inflection of some lemma under the tagged class. When it is not, the algorithm tests whether the surface looks like a mis-built inflection of a word the lexicon does know, by stripping a suffix family (plural -s/-es/-ies, verbal -ed/-d/-ing, comparative -er/-est, with undoubling and y→i handling) and checking whether a compatible lemma exists; a match marks the form malformed (e.g., "runned", "childs", "goed"), while an unknown word is marked unverified rather than condemned. A curated high-frequency list prevents clean sentences from being over-flagged. The layer also implements the relative-clause rules by walking SBAR/WHNP structures to check subject-gap agreement and the who/which/whose choice. Crucially, each checker runs in isolation, so one crashing checker degrades the verdict to unverified instead of erasing every other finding. The output of this stage is a tri-state result per word and an overall lexical-coverage ratio.


3.3.5 HYBRID ACCEPTABILITY DETECTION AND CORRECTION SEARCH
The final algorithmic layer broadens coverage without compromising explainability by combining a trained detector with a deterministic correction search.


Detection: 
A CoLA-fine-tuned RoBERTa acceptability classifier (server/detector.py) decides whether the sentence reads as acceptable English, giving broad coverage without needing a hand-written rule per error. The detector is optional and degrades gracefully: if its weights cannot be loaded, the system falls back to the rules-only verdict.
Combination: 
A sentence is grammatical only if both channels accept it. When the matrix reports a violation, the verdict is ungrammatical and the model's view is shown alongside it. When the matrix is clean but the model rejects the sentence, the rules cannot explain the rejection, so the verdict is set to unverified and the rejection is surfaced instead of a fabricated rule explanation.
Correction Search: 
To explain a rules-clean rejection deterministically, the system performs a masked-language-model sweep in text space (server/corrector.py): it masks one word at a time, asks a masked-language model (distilbert-base-uncased by default) for top-k replacements, and substitutes each candidate back into the acceptability model until a swap flips the sentence from unacceptable to acceptable. That single-token swap is the error locus (the bad word) and the candidate correction (the good word). The corrected sentence is then re-parsed and must pass the rule matrix cleanly, which supplies the authoritative required Part-of-Speech tag for the good word; finally, a morphological diff (lemminflect) requires the two words to share a lemma. Only when all gates pass is the finding promoted to a deterministic ungrammatical verdict, under the constraint identifier C-MLM-ANOMALY, with an explanation generated from a fixed template rather than a language model. A promotion therefore never rewrites a mere meaning change into a grammar condemnation, and the deterministic explanation path remains free of generative text.


3.3.6 MATRIX QUIZ PROCEDURAL SAMPLING, GRADING, AND GAMIFICATION
The Matrix Quiz is built on top of the same deterministic pipeline, so a quiz repair is never graded by string matching alone; it is re-parsed through the NLP Parsing Engine and the Linguistic Constraint Matrix. Each rule section (1 to 11) has three difficulty tiers (easy, medium, hard) and a procedurally generated bank of up to forty repair items. Every item consists of an incorrect sentence (bad), the expected corrected sentence (good), and a fallback explanation. Before a run begins, a diversity sampler selects the five-question set by extracting two-, three-, and four-word n-gram features from each candidate, including comma- and tail-aware features, and greedily choosing the candidate with the greatest minimum feature distance from the questions already selected. It also prefers items whose post-comma context key has not yet been used, so that a five-item drill exercises structurally varied cases instead of repeated lexical frames.

Grading uses a two-gate rule. An answer is marked correct only if (1) its normalized text matches the expected repair after casing, punctuation, and whitespace normalization, and (2) the backend parse of the repaired sentence has zero violated edges, no root error, and a grammatical verdict. For paragraph-level repairs, each sentence returned by the parser is validated independently. When an answer is wrong, the same deterministic remediation used in the tutor (violation breakdown, suggested and alternative fixes, and targeted outcome) is surfaced to the learner.

Gamification is derived deterministically from the permanent quiz_progress rows, so no unlock table is needed. Correct repairs award +5 XP, and a run with no wrong or skipped answers adds a +5 XP flawless bonus. Progress is decomposed into levels using a geometric threshold: the XP required to leave level L is BASE_SPAN times 1.6 to the power of L, starting at 50 (50, 80, 128, 205, 328, ...). Achievements are recomputed on demand from completed rule and difficulty combinations, including section scholars, "First Steps," "Flawless Run," and "Grammar Grandmaster." Signed-in learners synchronize displayed names, XP, levels, and quiz completion counts to Supabase through Clerk-issued JWTs subject to Row-Level Security; the leaderboard orders rows by level descending, then XP descending, and reads are public while writes are restricted to the owning user's Clerk sub claim.

3.3.7 DETERMINISTIC REMEDIATION CARDS
In addition to passive XAI explanation, the system exposes each rule violation as a deterministic remediation card rather than an automatic rewrite, preserving the no-auto-correction principle. When a node is flagged as an error, the selected node's subtree is emphasized on the canvas and the right-hand explanation panel presents a Case B remediation card containing the detected violation, a suggested fix, an optional alternative fix, and, when the rule provides it, the targeted grammatical outcome. Because the token-level edits are not applied by the system, the original input text and active sentence remain untouched; learners are guided to repair the sentence themselves, after which they may resubmit the corrected text for a fresh parse and verdict, and the system reports whether other issues remain or the sentence is now grammatical.

3.4 OPERATIONAL FRAMEWORK
The operational framework of Syntutor delineates the functional execution of the system from the initial user interaction to the final delivery of pedagogical feedback. The system is architected upon a dynamic, event-driven Input-Process-Output (IPO) model, shown in Figure 3.4 below. In contrast to traditional static grammar checkers that execute a single linear scan and terminate, the operational flow of Syntutor utilizes a continuous feedback loop. It maintains an active, stateful listening mode, which allows user interactions to trigger secondary and tertiary processing states without necessitating a full system reload.


Figure 3.4.1 IPO Framework of Syntutor

3.4.1 THE INPUT PHASE
The Input phase is categorized into two distinct interaction stages, each responsible for transmitting specific data payloads to the processing engine. The primary stage involves textual input and sanitization, wherein the user accesses the client-side interface to input a raw string of English text. To ensure system stability and parsing efficiency, the interface applies an input validation protocol, stripping the string of non-standard characters and evaluating the string length to prevent memory saturation during the parsing phase. Subsequently, the user selects a specific target sentence, effectively isolating the input scope. This selected string is then bundled into an API request payload and transmitted to the backend middleware.
Following the initial syntax visualization, the system transitions into the secondary stage, characterized by asynchronous event-driven inputs. In this state, the frontend listens for user mouse events. A click on a terminal leaf node, representing an individual word, or a non-terminal parent node, representing a phrase cluster, triggers an event handler. This handler packages the specific node's unique identifier, lexical type, and hierarchical coordinate data into a localized JSON payload, which is then passed back to the processing engine for targeted evaluation.






3.4.2 THE PROCESS PHASE
The Process phase constitutes the core linguistic and deterministic engine of the system. It translates the raw string inputs and event triggers into structured, verifiable data through a rigorous three-stage sequential pipeline. Initially, the system conducts lexical and morphological analysis. Upon receiving the validated target sentence, a pre-processing script is executed to perform tokenization, systematically dividing the string into discrete word tokens and handling punctuation delimiters. Following tokenization, a Part-of-Speech (POS) tagger is applied to assign a preliminary lexical category to each token based on its surface-level morphology and immediate surrounding context. This step prepares the data array for deep structural parsing.
The second stage involves syntactic parsing, tree reconstruction, and serialization. The tagged token array is fed into the Natural Language Processing (NLP) middleware, where the benepar neural constituency parser produces the highest-scoring phrase-structure parse string for the sentence, and the recursive-descent decoder rebuilds it into a hierarchical node graph. The decoder assigns each node a deterministic identifier, a Part-of-Speech or phrase type, a token-coordinate span, and its parent-child dependencies, and enforces a span-alignment guard so that the number of leaves matches the sentence's token count exactly. The serialized nodes, edges, and depth levels are then transmitted to the frontend.
The third stage encompasses the Explainable Artificial Intelligence (XAI) structural evaluation together with the hybrid verification channel. The XAI module validates every parent-child relationship against the system's predefined Linguistic Constraint Matrix (C) and the positive-evidence licensing layer, and it compiles a valid response when a relationship is licensed or an error response (identifying the exact rule violation) when it is not. A trained acceptability classifier then reviews the sentence: if the matrix is clean but the model rejects the input, a correction search locates the single-token repair, re-parses the corrected sentence, and only promotes the finding once the corrected sentence passes the matrix and the morphological gates. The combined result is finalized as a three-state verdict, grammatical, ungrammatical, or unverified.


3.4.3 THE OUTPUT PHASE
The Output phase is responsible for translating the complex, serialized backend data structures into an accessible, interactive educational user interface. This phase delivers two distinct forms of synchronized output. The primary visual output consists of the interactive canvas. The frontend receives the serialized JSON tree data and executes a rendering algorithm to calculate the coordinate geometry for each node. A dynamic, mathematical tree diagram is rendered on the interface, illustrating the hierarchical syntactic and dependency relations connecting the words. To facilitate the secondary input loop, the canvas is rendered with interactive, scalable hitboxes around every node and branch, and each node and edge is coloured according to its validation status.
The secondary output is the pedagogical feedback generated by the XAI module. Triggered sequentially after the structural evaluation stage, the system outputs a natural-language explanation. This data is injected into the Document Object Model (DOM) and displayed within the user interface as a contextual modal or side-panel. Rather than merely providing a corrected sentence, this output explicitly narrates the structural rules governing the user's selected node, thereby bridging abstract algorithmic logic with human-readable educational instruction.


3.5 USE CASE / FLOWCHART / STATE DIAGRAM
  	In this section, three UML diagrams will be utilized to portray how the Syntutor system operates. The three diagrams will act as complementary representations of the system's operation along different dimensions. The Use Case Diagram will show the system's functional area, as seen by the actors who use it. The Flow Chart will document how the system (automated processing path and user for every reason for exiting the system) executes sequentially. The State Diagram will model the individual states of the system and how the various events will provide for the change of the system states.


The three diagrams will provide an integrated and coherent representation of Syntutor's architecture and will reinforce the design principles established through the Conceptual Framework regarding separating automated processes and user-driven processes, how the explanations provided for XAI were precomputed, and how the only way to return to the pipeline was for the user to submit text.


Figure 3.4: Use Case Diagram of Syntutor
	
Figure 3.4 defines the functional boundaries of SynTutor across two external actors: the Student (primary learner) and the Expert Evaluator (linguistics validator). Automated backend tasks such as tokenization, parsing, and constraint checking are excluded from the diagram because they run internally without direct user interaction.


Submit Text: Both actors begin by submitting an English sentence or passage for analysis.


View Syntax Tree and View Basic Explanation (<<include>>): Allows the actor to view the generated constituency tree. The <<include>> link to View Basic Explanation ensures that every syntax tree display is mandatorily paired with a sentence-level natural-language summary.


Interact with Syntax Tree and View Detailed Explanation (<<extend>>): Enables the actor to pan, zoom, and explore tree nodes on the canvas. The <<extend>> link from View Detailed Explanation indicates that node-specific explanations are optional and appear only when the actor selects a specific node, reading its precomputed diagnostic from cache.


Take Matrix Quiz and Earn XP, Levels & Achievements (<<include>>): Allows the Student to choose a grammar rule from the 11 matrix sections and a difficulty tier (easy, medium, hard) to complete a 5-question repair drill. It includes Submit Text (<<include>>) to validate each repair through the /api/parse pipeline and includes Earn XP, Levels & Achievements (<<include>>) to calculate XP, level progress, and badges at the end of the quiz.


View Public Leaderboard, Sync Progress & Analysis History (<<extend>>), and Sign In / Register (<<include>>): Allows the Student to view global rankings in player_stats. Sync Progress & Analysis History extends this feature for users who want to save their XP, quiz progress, and sentence history to Supabase, which mandatorily includes Sign In / Register (Clerk Auth).


Figure 3.5 System Flowchart of Syntutor

Figure 3.5 traces how SynTutor executes sequentially from START to END across its two workspace modes. Ovals represent terminals, parallelograms represent inputs and outputs, rectangles represent processes, and diamonds represent decision points.


Text Analysis Mode (Left Spine): When the user selects Text Analysis Mode and submits text (User Submits Text), the pipeline runs Preprocessing (spaCy tokenization, POS tagging, and lemmatization), the NLP Parsing Engine (benepar_en3 parsing), Generate Selected Syntax Tree (recursive-descent decoding and span alignment), and the Error Detection & XAI Module (Constraint Matrix, Lexical Licensing, and Hybrid CoLA/MLM checks). The system then outputs the tree and basic explanation simultaneously in Display Syntax Tree and Basic Explanation (UI).
Node Interaction Loop: At the decision diamond Does the user select a node in the syntax tree?, choosing Yes triggers Retrieve Precomputed Node-Level Explanation (No Reprocessing). The client reads the cached explanation from session.payload.node_details, renders it via Display Detailed Explanation, and loops back to the decision diamond so the user can inspect multiple nodes without re-parsing.


Matrix Quiz Mode Spine (Right Column)
Matrix Quiz Mode (Right Spine): When the user selects Matrix Quiz Mode, Select Rule (Sections 1 to 11) & Difficulty Tier calls questionPool() to sample 5 diverse questions. For each question, the user submits a repair that is checked by Validate Repair via NLP + XAI Pipeline (POST /api/parse) and scored by Grade Answer (answer.js), which requires both an answer-key match and a grammatical verdict with zero error nodes. The decision diamond: More questions in 5-item quiz? loops until all 5 items are answered. The system then runs Compute Earned XP, Exponential Level & Unlocked Achievements and outputs Display Quiz Summary & Sync Leaderboard / Progress (Supabase).


Re-Entry Loop: Both paths meet at Does the user submit new text or start another quiz?. Answering Yes loops back to the mode selector for a new run, while No ends the session at END.


Figure 3.6 State Diagram of Syntutor

Figure 3.6.1 models SynTutor's client-side controller as a Finite State Machine (FSM) with four persistent states: Idle, Processing, Viewing, and Exploring. The Matrix Quiz operates as a UI mode that reuses this same parser state lifecycle when checking quiz answers.


Idle State: After starting at the initial pseudostate (System ready), the system waits in Idle until the user submits text.


Processing State: Triggering User submits text moves the system into the Processing composite state, which runs five sequential backend steps: Preprocessing, Parsing, Syntax tree generated, Explanation computed, and Output ready. If an empty input or a parse or network error occurs, the system returns to Idle. Once the response is ready (Output ready), the system transitions to Viewing.


Viewing State: Displays the rendered syntax tree and basic explanation. From Viewing, the user can select a node (User selects syntax node) to enter Exploring, submit edited text or switch sentences (User submits new input) to re-enter Processing, clear the workspace (New session / clear) to return to Idle, or exit (User exits) to reach the final state.


Exploring State: Highlights the selected node's subtree and displays its precomputed XAI explanation from session.payload.node_details without making a new HTTP request. Clearing the selection (Back to syntax tree) returns to Viewing, submitting new text (User submits new input) moves directly to Processing, and clearing the session (New session / clear) returns to Idle.


3.6 RESPONDENTS OF THE STUDY
The respondents of this study are categorized into two distinct groups to ensure a comprehensive and multi-faceted evaluation of the Syntutor system. The evaluation phase requires assessing both the pedagogical impact and usability of the software from a learner's perspective, as well as validating the linguistic accuracy and pedagogical soundness of the Explainable AI (XAI) from an expert's perspective.
The first group of respondents consists of the primary target end-users: Bachelor of Science in Computer Science (BSCS) students enrolled at De La Salle University - Dasmariñas (DLSU-D). Through purposive sampling, a total of fifty (50) student respondents will be selected to participate in the system testing and evaluation. The selection of BSCS students is highly relevant to the study; their technical background allows them to effectively navigate and evaluate the system's Interactive UI Canvas and the dynamic syntax tree generation, while their status as English language learners makes them ideal candidates to test the system's ability to improve grammatical comprehension and syntactic priming. The students will evaluate the system based on its usability, the clarity of the natural-language explanations provided by the Output Generation component, and their perceived improvement in structural grammar analysis.
To qualify for the study, student respondents must meet the following inclusion criteria: (1) currently enrolled as regular BSCS students at DLSU-D, (2) have a fundamental understanding of English grammar, and (3) are willing to interact with the Syntutor web application to analyze English texts.
The second group of respondents consists of expert evaluators, specifically three (3) English and Linguistics professors or instructors. Because Syntutor utilizes a neural constituency parser together with a deterministic constraint matrix and an XAI structural validation module, it is crucial that the generated phrase-structure syntax trees and rule-based diagnostic feedback are linguistically sound. The expert evaluators will be selected using purposive sampling based on their academic credentials, teaching experience in English syntax, and familiarity with language learning technologies.
The role of the expert respondents is to conduct a rigorous quality assurance test on the system's educational output. They will assess the parser's structural precision, verify that the XAI does not produce "hallucinated" or grammatically incorrect feedback, and evaluate whether the system's deterministic mapping correctly translates complex syntactical constraints into pedagogical explanations suitable for students. By combining the feedback from both the student learners and the linguistic experts, the researchers can continuously refine the application through the Agile-Scrum development sprints, ensuring that Syntutor is both technically robust and practically effective as a digital tutoring agent.


3.6.1 Ethical Considerations
To ensure full institutional compliance, data privacy, and protection of the participants’ data, the evaluation of the system adheres to the following protocols:
Informed Consent and Voluntary Participation
Participation of the respondents is strictly voluntary. A written informed consent that outlines the scope of the study, potential risks, and the intended usage of collected data will be given prior to data gathering. Participants retain the right to withdraw at any moment without penalty.
Anonymity & Data Confidentiality:
All collected data including syntactic pretest/posttest scores, the SUS survey responses, and the validation of experts are removed from personal identifiable information. Each participant is assigned a code to ensure anonymity in compliance with data privacy standards.
Data Security:
All collected digital data will be encrypted and stored in a secure digital repository accessible only to the researchers, to be used for academic purposes only.


3.6.2 Statistical Treatment of Data
In order to measure the effectiveness of the application and its overall user experience, the data collected from the respondents will be processed using the following statistical treatment methods:


Paired Samples t-Test: 
Evaluates the student learning gains by comparing the mean baseline performance on the syntactic pretest against post-intervention performance on the parallel posttest. If the pretest/posttest score distributions violate the assumption of normality, the Wilcoxon Signed-Rank test will be applied as an alternative.


System Usability Scale (SUS) Scoring: 
Student feedback on the 10-item Likert scale SUS questionnaire is calculated using standard SUS scoring formulas to produce a normalized score out of 100, evaluating system usability, learnability, and overall user interface navigation.


Mean Scores and Percentage Accuracy: 
Ratings from the 4-point rubric in the validation matrix are synthesized using descriptive statistics for the accuracy of the generated syntax tree and correctness of the XAI feature.
