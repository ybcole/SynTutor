
# **CHAPTER IV**  **RESEARCH METHODOLOGY** {#chapter-iv-research-methodology}

### **4.1 DESIGN AND METHODOLOGY**  
	This section outlines the methodical framework utilized to build and evaluate SynTutor. To evaluate how well the system works as both a software application and a learning tool, this study uses a mixed-methods design paired with a pretest-posttest experiment. The goal is to test the complete SynTutor experience, evaluating the accuracy of its sentence-parsing engine, the clarity of its visual syntax trees, the usefulness of its rule-based explanations, and its ability to help learners better understand English grammar.

### **4.2 PROJECT DEVELOPMENT**  
	The development of SynTutor was executed according to the Agile-Scrum framework, applying iterative development cycles in order to build, refine, and integrate the system's NLP architecture with an interactive frontend interface. The project's progress was consistently updated through major development sprints, with each cycle producing functional software increments that underwent verification.

#### **4.2.1 Development of the NLP Pipeline and Deterministic XAI Engine**  
	The backend functionality of the system served as the foundational structure for the tokenization, parsing, and rule-based evaluation of input sentences. The NLP pipeline was established as a seven-stage process: text preprocessing, sentence segmentation, and Part-of-Speech (POS) tagging through spaCy's en_core_web_md model; constituency parsing through the benepar_en3 neural constituency parser, which emits a phrase-structure parse string for each sentence; and a custom parse-string decoder and node-builder stage that converts the parenthesized parse string into a serializable node graph of nested constituents, each carrying token-coordinate spans aligned against the token stream.  
	A deterministic rule-based explanation algorithm, the Linguistic Constraint Matrix, was then created to evaluate every parent-child edge of the generated tree. For each edge, the evaluation function returns a licensed (valid), violated (error), or unlisted verdict together with the identifier of the fired constraint, a plain-English structural explanation, and, in the case of a violation, a repair suggestion:

* E(vd, vp) = f_valid(vd, vp)  if (vd → vp) is licensed by the rule matrix  
* E(vd, vp) = f_error(vd, vp, δ)  if (vd → vp) violates constraint δ  
* E(vd, vp) = unlisted  if no matrix rule covers the edge  

  	The matrix enforces constraints such as subject–verb agreement, determiner–noun number agreement, auxiliary and verb-form selection, clause finiteness, modifier ordering, pronoun case, article selection, and noun plural morphology, among others. Because the engine consults only hand-authored rules over the parsed tree and never a generative model, identical inputs always produce identical verdicts; the feedback channels reserved for generative explanations (surprisal, perturbation, and large-language-model notes) are intentionally left null. These components were all instrumental in ensuring the system's accuracy and validity prior to its integration with the frontend interface, and they are continuously verified by the gold-corpus regression audit described in Section 4.4.

	The Positive-Evidence Lexical Licensing layer was integrated to close the blacklist gap of the constraint matrix: for each open-class leaf, lemminflect and inflect verify that the surface form is a valid inflection for its parser-assigned POS tag, catching malformed forms such as "childs", "runned", or "stupids" while marking unknown words as unverified rather than condemned.

	The Hybrid Acceptability/Correction-Search channel was layered on top: a CoLA-fine-tuned RoBERTa classifier (textattack/roberta-base-CoLA) provides broad acceptability coverage, and when the matrix is clean but the model rejects a sentence, a deterministic masked-language-model sweep (distilbert-base-uncased) searches for a single-token repair sharing the same lemma, promoting to ungrammatical (C-MLM-ANOMALY) only if the repaired tree passes the Constraint Matrix cleanly.


#### **4.2.2 Integration of Agile-Scrum Principles**

  	Throughout the modeling, integration and deployment phases of SynTutor, agile methodologies were employed to iteratively enhance the system's frontend and backend functionalities. The user interface, syntax tree generation, and XAI components were updated within the development sprints, producing each software requirement such as the syntax tree interface and sentence parsing to allow for continuous modification and optimization within development cycles. Each sprint concluded with a verification pass: the automated gold-corpus audit for the backend rule matrix and a manual walkthrough of the frontend state machine for the interface increments.


#### **4.2.3 Development of the Interactive Canvas and Feedback Loops**

  	The presentation layer was developed as an interactive HTML5 canvas that renders the phrase-structure tree produced by the backend. The renderer lays leaves out in uniform slots, centers each internal node over the span of its children, draws parent-child edges (coloring edges of violated constraints red), and exposes per-node hitboxes for selection. It supports drag-to-pan, wheel zoom anchored to the cursor, keyboard navigation, and device-pixel-ratio-aware resizing. The application itself is governed by a finite state machine that drives two feedback loops: a lightweight interaction loop, in which selecting a node reads its precomputed explanation from the in-memory session payload without re-issuing a parse request, and a re-entry loop, in which editing and resubmitting the input restarts the full pipeline. In keeping with the study's instructional stance, the system never auto-corrects the learner's sentence; it displays the violation and a deterministic correction suggestion, and the learner performs the repair.


### **4.3 RESEARCH DESIGN**

The study separates two complementary forms of evidence: (a) student learning and usability outcomes, evaluated using the actual collected pretest, posttest, and System Usability Scale (SUS) records; and (b) quantitative technical evaluation of SynTutor's syntax-tree and grammar-feedback functions against published linguistic references. Participant allocation, final sample counts, and any control/experimental comparison must be reported from the actual research records rather than assumed from the original proposed design.

**H01 — Phrase-structure parsing:** The evaluated system is the integrated spaCy + Benepar (\`benepar_en3\`) + Burton–Roberts FINAL-D1 projection pipeline. Four separate measures were used: development-exposed published full-tree PARSEVAL accuracy; unseen published partial structural-relation agreement; unseen deterministic Burton–Roberts rule compliance; and unseen conversion consistency. Rule compliance and conversion consistency are **not substitutes for complete-tree accuracy**. No independent complete-tree gold annotations or expert-adjudicated unseen trees were available.

**H02 — Grammar grounding:** The same sentences were analyzed by rule-grounded SynTutor (Arm A) and an ungrounded neural acceptability/correction baseline (Arm B). Their grammatical judgments, localizations, valid corrections, and incorrect/unsupported feedback were scored with symmetric criteria. The primary endpoint was the absence of demonstrably incorrect or unsupported feedback, together with non-abstaining clean feedback; additional outcomes are reported separately.

**Educational outcomes (H03/H04):** Student learning gains and usability are evaluated separately using the study's documented assessment and survey procedures. Technical parsing performance alone cannot establish learning effectiveness, and learner scores alone cannot validate syntax-tree accuracy.

**Methodological status:** The wording in this chapter has been aligned retrospectively with frozen Evaluations V1, V2, and V3. This editorial clarification does not revise original result files or transform previously evaluated items into a new unseen test. The reported H01 significance tests on sentence complexity assess differences or trends, not whether complete-tree accuracy clears an independently defined statistical threshold.

### **4.4 DATA COLLECTION**

Two sources of data were used for distinct research questions: verified student assessment/survey records for pedagogical outcomes, and reproducible textbook-based computational benchmarks for H01 and H02.

| Instrument / dataset | Data source | Research question | Scope |
|---|---|---|---|
| Syntactic pretest and posttest | Actual student responses | H03 | Learning outcomes; report final participant counts and group allocation from verified records |
| System Usability Scale (SUS) | Actual completed survey records | H04 | Usability; do not treat intended respondents as completed responses |
| Frozen technical Evaluations V1, V2, V3 | Three separate 100-sentence datasets (each 50 grammatical and 50 ungrammatical), textbook references, and locked scoring scripts | H01 and H02 | Structural and linguistic-feedback evaluation, independent of learner-test scores |
| Published Burton–Roberts reference diagrams | 216 development-exposed diagrams and a separately checked published figure | H01 | Full-tree and triangle-aware comparisons **only on disclosed development-exposed references** |

The sources for linguistic reference judgments were Burton–Roberts (2011, 3rd ed.) and Huddleston and Pullum (2002). For unseen sentences without complete authoritative Burton–Roberts answer trees, structural accuracy was assessed only on **published partial relations**, while deterministic compliance and conversion checks were reported under their own names.

Earlier manuscript references to a **104-sentence zero-regression corpus** describe a separate development/regression resource, not the frozen 100-sentence V1–V3 technical evaluations. These datasets and scores must not be conflated.

An Expert Validation Matrix had been proposed in earlier planning drafts. Because no qualified independent reviewer team supplied unseen complete H01 tree gold standards, that proposed instrument is **not represented as completed technical validation**. Any educator feedback actually collected for other objectives requires its own independently verifiable sample, rubric, and records.

#### **4.4.1 SAMPLING**

Student recruitment for the pretest, posttest, and usability components was based on the approved eligibility and consent procedure. The original design identified BSCS students at De La Salle University–Dasmariñas as a target population. Actual participant counts, completion counts, and any control/experimental allocation are to be reported according to the original signed records and score sheets, not the initial recruitment targets.

The 100-sentence V1/V2/V3 technical corpora were **selected linguistic test cases, not human research participants**. Grammatical and ungrammatical sentences were evaluated by automated procedures against published textbook judgments. The contamination audit checked prior exact and near-duplicate overlap; it does not establish the absence of examples from model pretraining.

No sample of independent linguists constructed or adjudicated complete unseen reference syntax trees in the reported H01 technical evaluation. Therefore, no missing expert sample size, adjudication rate, or panel-derived accuracy percentage is imputed.

#### **4.4.2 DATA ANALYSIS**

**H01:** Report labeled/unlabeled PARSEVAL F1 and exact match for the development-exposed textbook diagrams, distinguishing raw, aligned, triangle-aware, and complete zero-triangle subsets. For the frozen unseen datasets, report per-item and per-relation published partial-reference agreement, canonical structural-rule compliance, conversion consistency, successful coverage, and unresolved cases. Give denominators and difficulty-stratified results. Wilson confidence intervals describe binary estimates; bootstrap intervals describe structural F1 where available. Kruskal–Wallis, Jonckheere–Terpstra, and Fisher–Freeman–Halton tests evaluate *differences across complexity*; they are not one-sample tests of high accuracy.

**H01 hypothesis interpretation:** The original H01 uses 'statistically significant degree of accuracy' without a prespecified numerical benchmark and lacks unseen complete authoritative full-tree answers. Therefore the available scores do **not** establish confirmatory rejection of H01. The later 80–83% engineering aspiration is not retrospectively substituted for a preregistered null threshold. Development-exposed F1, rule compliance, and conversion consistency must remain separately labeled.

**H02:** Compare Arm A versus Arm B with exact two-sided paired McNemar tests for the predefined primary incorrect/unsupported-feedback and decided-clean outcomes, followed by secondary grammatical judgment, error localization, correction validity, and full adequacy; apply the documented Holm–Bonferroni adjustments. Report effect sizes, raw paired denominators, abstentions, and error-family coverage. The frozen V3 primary difference is statistically significant **within the tested eight-family curriculum**; it does not imply universal English grammar accuracy.

**H03/H04:** Analyze pretest/posttest outcomes and SUS only from actual collected learner records, matching the statistical procedure to the observed group design, paired identifiers, and assumptions. If a controlled comparison was used, do not treat it as one-group data. An educator validation mean or four-point accuracy score is included only if corresponding completed and auditable rating forms exist.

**Post-evaluation reporting:** V1, V2, and V3 are retained as separate historical frozen evaluations. Post-sprint improvements on those same sentences are regression observations rather than newly unseen results. All changes to methodology prose are explicitly documented as retrospective clarification and not as a pre-execution amendment.

#### **4.4.3 ETHICAL CONSIDERATIONS**  
  	To ensure the protection of the participants, institutional compliance, and data integrity, the study adheres to the following ethical protocols. Participation by both the 50 BSCS students and the 3 English experts is entirely voluntary. Clear, written informed consent forms detailing the scope of the study, potential risks, and data usage will be distributed and signed prior to data collection. All collected test results, SUS surveys, and expert matrices will be stripped of personally identifiable information. Unique alphanumeric participant codes will be assigned to all records to maintain confidentiality in compliance with data privacy regulations. Participants and experts retain the absolute right to withdraw from the evaluation process at any time without penalty or academic prejudice. Lastly, all electronic files containing raw scores, feedback logs, and encrypted transcripts will be stored in a secure storage accessible only by the researchers.


### **4.5 DEVELOPMENT PLANNING**  
	Development planning outlines the technical infrastructure, software stack, and environment requirements established to build, test, and deploy the SynTutor application.

#### **4.5.1 SOFTWARE SPECIFICATIONS**  
	The SynTutor application is engineered using a modular client-server architecture that decouples the browser frontend from the Python backend. In production, the static frontend is built and served by Vercel, while the NLP execution engine runs as a separate service on a Hugging Face Space; the two communicate through a small JSON REST interface governed by cross-origin (CORS) rules. During development, a single Python process serves both on one origin and port.  

	**Frontend Interface Environment**

* **Framework:** Vanilla JavaScript ES modules with no front-end framework and no transpilation step, keeping the application shell (index.html), styling, and logic directly loadable by any modern browser. A trivial build step (scripts/build.js) copies the static assets (index.html, login.html, css/, js/) into dist/ so Vercel can serve them as a static site.  

* **Visualization Engine:** A custom HTML5 Canvas renderer (js/renderer.js) that computes the tree layout, edge geometry, and node hitboxes in application code and handles selection, pan, zoom, and keyboard navigation without a third-party graph library.  
* **Styling & UI:** Hand-authored CSS3 with custom-property design tokens (css/style.css) for a responsive, minimalist workspace layout and diagnostic side-panels.  
* **Authentication & Persistence:** Clerk for sign-in (email/password with email-code verification and optional second factor) and Supabase for per-user analysis history, secured by Row-Level Security keyed to the signed-in user.  

  	**Backend NLP & XAI Engine**  
* **Core Language & Runtime:** Python 3.10+ for text processing and HTTP serving.  
* **Web Framework:** In production the API is served through Hugging Face's Gradio SDK (gradio 5.49.0) on the free ZeroGPU hardware tier: the entrypoint (app.py) launches a minimal Gradio app, registering a no-op @spaces.GPU handler that the ZeroGPU runtime requires, which consumes no GPU quota because SynTutor is CPU-only, and mounts the same GET /api/health and POST /api/parse routes onto the app's FastAPI server. Locally and inside the container image (Dockerfile), the Python standard-library http.server (threaded) exposes the identical endpoints and also serves the static frontend from a public whitelist.  
* **Preprocessing & POS Tagging:** spaCy (en_core_web_md) for tokenization, sentence segmentation, case normalization, Part-of-Speech tagging, and dependency metadata.  
* **Parsing Algorithm:** The benepar_en3 neural constituency parser for phrase-structure analysis; a custom recursive-descent decoder converts the parser's parenthesized parse string into a node graph, and a node-builder stage validates that tree leaves align one-to-one with the token stream before the tree is accepted.  
* **XAI Engine:** A deterministic rule module (server/matrix.py) mapping every parent-child tree edge against the Linguistic Constraint Matrix, producing per-node role, constraint, checks, plain-English explanation, and remediation text.  
* **Dependency Manifest:** requirements.txt pinning spacy==3.8.16, benepar==0.2.0, transformers==4.46.3 (required by benepar's retokenizer), and inflect>=7.5,<8 (deterministic English noun morphology used to reject malformed plurals). Because the ZeroGPU runtime emulates a CUDA device, the parser is explicitly pinned to the CPU while loading so that benepar's device probe reports no GPU and the model stays on CPU.  


  	**Deployment & Client Specifications**  
* **Runtime Deployment (Production):** The static frontend is deployed to Vercel at https://syntutor.vercel.app. `npm run build` executes scripts/build.js, which copies the public assets into dist/, and Vercel serves dist/ with no server code (the Python backend is explicitly excluded from the deployment). The Python backend is deployed to a Hugging Face Space at https://ybcole-syntutor.hf.space: app.py launches Gradio on port 7860 (the port exposed by the platform) and mounts the /api/health and /api/parse routes on the same server, with CORS enabled so the Vercel origin can call the API directly. Both deployments redeploy automatically whenever the main branch is updated.  
* **Local Development:** For development, python3 server/app.py (or npm run serve) still serves the static frontend and the REST API from a single process and origin, defaulting to port 8000 (configurable via SYNTUTOR_PORT / SYNTUTOR_HOST); js/config.js selects the API base URL ('' for a same-origin call, otherwise the URL of the deployed backend).  
* **Verification Command:** `npm run audit` executes the offline gold-corpus regression audit without starting the HTTP server, providing the maintained acceptance check for the rule matrix.  
* **Client Requirements:** Standard desktop device equipped with a modern web browser (Google Chrome, Mozilla Firefox, Microsoft Edge, etc.) and active internet access for Clerk authentication, Supabase persistence, and model-backed analysis against the deployed API.


### **4.6 EVALUATION OF THE PROJECT**

Evaluation combines the actual educational intervention/survey evidence (H03/H04) with the separate published-reference technical assessment (H01/H02). The two evidence streams answer different research questions.

#### **4.6.1 RESPONDENTS OF THE STUDY**

The primary participant population for the educational and usability components consists of the students who actually provided consent and completed the applicable assessment or survey. Report actual eligibility, totals, group allocation, and attrition from verified study records. No purported independent H01 expert tree annotations are included in this thesis's completed technical evidence.

#### **4.6.2 RESEARCH INSTRUMENTS AND TECHNIQUES**

The student instruments are the syntactic pretest/posttest and 10-item SUS. The technical instruments are the frozen textbook-derived V1–V3 sentence corpora, their gold judgment/partial-relation specifications, and the corresponding archived H01/H02 scoring procedures. H01 includes published full-tree accuracy on **development-exposed** diagrams and independent partial-reference, compliance, and conversion measurements on unseen sentences. H02 uses an identical-input paired comparison of rule-grounded and ungrounded systems.

The older 104-sentence development corpus and any proposed four-point expert rubric are not substituted for those frozen evaluation measures.

#### **4.6.3 DATA GATHERING**

1. **Educational assessment:** Collect and score the student pretest, intervention exposure, posttest, and SUS responses using the actual approved study design and participant codes.
2. **Technical benchmark preparation:** Record source editions, grammaticality labels, sentence-complexity strata, partial published relationships, correction alternatives, dataset hashes, and scorer versions before each independent evaluation.
3. **Technical execution:** Execute each frozen V1–V3 benchmark against the corresponding frozen code and scoring protocol; archive predictions, denominators, exceptions, and statistical outputs.
4. **Post-evaluation reliability work:** Use previously exposed examples only as development/regression cases. Do not describe post-sprint V3 success as a second independent evaluation.

#### **4.6.4 TECHNICAL VERIFICATION OF THE SYSTEM**

Parser normalization, schema conformance, terminal-yield preservation, deterministic output, H01 partial structural agreement, and H02 outcome reliability were analyzed separately. Passing a rule-coverage audit does not prove that every linguistic attachment is correct. Likewise, automated regression-test success does not provide an independent full-tree reference answer.

For H01, an independently validated **unseen complete-tree F1** remains unavailable in the absence of complete authoritative answers or independent adjudicated trees; its status is **unverified**. The report preserves lower raw full-tree F1, the higher triangle-aware subset, and the independent partial-reference results without presenting any one as universal structural accuracy.

For H02, the actual V3 primary clean-feedback outcome was 89/100 for grounded SynTutor versus 65/100 for the ungrounded baseline (exact two-sided McNemar p = 0.000116; Holm-adjusted p = 0.000232). This supports rejection of the H02 null **for the evaluated benchmark and its covered rule families**, without asserting complete absence of unsupported claims on unrestricted English.

The wording of this chapter was reconciled **after** the frozen evaluations. No historical measurement or original result was changed.

# **REFERENCES:** {#references:}

Ansari, M., & Ansari, M. (2025). AI-Driven Innovations and Emerging Trends in Applied Linguistics and Language Education. American Research Journal of Humanities & Social Science, 8(3), 108-122.  
Bochari, S., & Hastini, H. (2025). Visualizing Syntax: The Effectiveness of Tree Diagram-Based Sentence Parsing in Addressing Structural Ambiguity in EFL. JOURNAL EDUSCIENCE, 12(5), 1225-1236.  
Bryant, C., Yuan, Z., Qorib, M. R., Cao, H., Ng, H. T., & Briscoe, T. (2023). Grammatical error correction: A survey of the state of the art. *Computational Linguistics, 49*(3), 643–701.  
Bucog, E. A. (2025). Artificial Intelligence Utilization in Enhancing Student Performance in Language Courses of One University in Batangas Province. Asia Pacific Journal of Management and Sustainable Development, 13(1, Part 4), 1-1.  
Cano, P. M. A., Catiggay, J. M. L., Florida, J. M. M., Pua, J. M. R., & Samonte, M. J. C. (2024). Natural language processing of grammar checker tools for academic writing: A systematic literature review. *Journal of Electrical Systems, 20*(7s), 1151–1156.  
Cantilero, K. (2025). Syntactic Priming, Speech Acts, and Linguistic Competence of Senior High School Learners: Basis for the Development of Language Enhancement Exemplars. Psychology and Education: A Multidisciplinary Journal, 44(10), 1-1.  
Cruz, S. R. D. (2025). AI-Integrated English Classroom Practices in Philippine Higher Education. AsTEN Journal of Teacher Education.  
Deng, J., Chen, C., Hou, C., & Yuan, X. (2025, January). InstructGEC: Enhancing Unsupervised Grammatical Error Correction with Instruction Tuning. In Proceedings of the 31st International Conference on Computational Linguistics (pp. 110-122).  
Domingo, M. A. T. (2025). Investigating the influence of AI-driven tools in ESL students' experience of AI-induced impostor syndrome and academic confidence. *Asian Journal of English Language Studies, 13*(1), 98–125.  
Farrow, R. (2023). The possibilities and limits of explicable artificial intelligence (XAI) in education: A socio-technical perspective. *Learning, Media and Technology, 48*(2), 266–279.  
Karjo, C. H., & Ying, Y. (2024, September). Measuring student's accuracy in drawing syntactic tree diagrams using syntax tree generator. In Proceedings of the 2024 the 16th International Conference on Education Technology and Computers (pp. 104-109).  
Li, Y., Cui, L., Yan, J., Yin, Y., Bi, W., Shi, S., & Zhang, Y. (2023). Explicit syntactic guidance for neural text generation.*Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 14095–14112.  
Li, Y., et al. (2025). Integrating multiple XAI techniques to enhance LLM interpretability.  
Magday, W. D., Memita, J. F., Abon, J. T., Gumilet, G. G., Cablinan, A. B. G., Castro, L. T., ... & Tumaneng, E. B. B. (2025). Enhancing students' subject-verb agreement skill by using CiCi artificial intelligence-based app: Embedded mixed-methods study. HO CHI MINH CITY OPEN UNIVERSITY JOURNAL OF SCIENCE-SOCIAL SCIENCES, 162-179.  
Muralidaran, V. (2022). *A linguistically motivated approach to grammar induction* [Doctoral dissertation, Cardiff University]. ORCA (Online Research Data @ Cardiff).   
Ribeiro-Flucht, J., et al. (2024). Explainable AI in language learning: Linking empirical evidence and theoretical concepts in proficiency and readability modeling of Portuguese. *Proceedings of the 19th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2024)*, 199–209. Association for Computational Linguistics.  
Rugaiyah, R. (2023). The potential of artificial intelligence in improving linguistic competence: A systematic literature review. Arkus, 9 (2), 319–324.  
Sagum, J. K. A., Sagum, R. A., Dela Fuente, M. B., & Inovero, C. G. (2023, December). Automated Filipino Language Treebank Generator. In Proceedings of the 2023 7th International Conference on Natural Language Processing and Information Retrieval (pp. 119-123).  
Soriano, S., Martinez, R. A., Jr., Pabalan, J. L., III, Dulay, M. J. B., Fangon, M. R., Rosales, R. S. T., Nabor-Ferrer, C., & Mathur, A. (2024). Effectiveness of Meta AI in enhancing academic writing proficiency: The case of Filipino ESL learners. *Library Progress International, 44*(3), 18929–18939.  
Triana, H., Indriyani, V., Putri, D. A., & Saputra, H. (2025). Validation of Artificial Intelligence (AI) In Syntactic Analysis to Improve Students' Linguistic Competence and AI Literacy. INTERACTION: Jurnal Pendidikan Bahasa, 12(3), 369-378.  
Wei, Z. (2023). Artificial intelligence in language instruction: Impact on English learning achievement, L2 motivation, and self-regulated learning. *Frontiers in Psychology, 14*, Article 1261955.
