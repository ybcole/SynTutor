
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

  	This study employed a mixed-methods, quasi-experimental research design using a One-Group Pretest-Posttest framework integrated with an expert system validation. This design is engineered to evaluate both the technical performance of SynTutor's Natural Language Processing (NLP) architecture and its instructional efficacy in improving deep-structure grammatical competence.

  	Through the combination of quantitative score measurements with qualitative expert analyses, the research design addresses the dual requirements of software validation and educational assessment without relying on single-method assumptions.


  	**Quantitative Quasi-Experimental Component:**

  	The quantitative phase evaluates the pedagogical impact and user experience of the system among student respondents using a structured three-phase sequence:

1. **Baseline Syntactic Pretest (Form A):** Prior to using SynTutor, the 50 BSCS student respondents complete **Syntactic Assessment Form A**, a 20-item multiple-choice diagnostic test (scored $0–20$, $1 point$ per item) measuring phrase boundary identification, subject-verb agreement across intervening prepositional phrases, collective and correlative agreement, determiner stacking, bare determiners, pronoun case, *a/an* phonotactics, missing articles, post-nominal modifier errors, adjective-for-adverb substitutions, quantifier-countability agreement, double comparatives, modal + finite verb errors, subordinate fragments, capitalization, copula + finite verb L1 interference (*"I am agree"*), and relative-clause agreement.   
2. **System Intervention:** This is the phase in which participants actively use the SynTutor application. During this phase, users input sentences into the analysis engine, interact with dynamically generated phrase-structure syntax trees, examine parent-child node relationships, and read the Explainable AI (XAI) diagnostic explanations rendered alongside the canvas.  
3. **Post-Intervention:** Participants complete a parallel posttest to measure knowledge acquisition, followed by the System Usability Scale (SUS) questionnaire to evaluate interface clarity, navigation efficiency, and system responsiveness.

   	**Qualitative Expert Validation Component:**

   	The qualitative phase evaluates the underlying system logic, parsing accuracy, and pedagogical soundness of SynTutor's backend output. Subject matter experts in English linguistics analyze a standardized benchmark set of syntactically complex and ambiguous sentences processed by the system.

   	Experts evaluate:

* **Tree Generation Accuracy:** Verification that the neural constituency parser and the tree-reconstruction stage produce valid hierarchical constituent structures that conform to phrase-structure conventions.  
* **Explanation Correctness:** Confirmation that the deterministic evaluation function accurately flags structural violations against the Linguistic Constraint Matrix without producing erroneous or misleading diagnostic explanations.


  	A mixed-methods approach was used because neither quantitative testing nor qualitative expert review alone can validate the system completely. High posttest scores prove student retention, but they cannot verify whether the parse trees adhere to formal linguistic theory. Additionally, expert approval confirms that the NLP parser and constraint matrices are theoretically sound, but it offers no empirical proof that students can successfully navigate the canvas or retain structural concepts.  
  	The research design explicitly operationalizes the evaluation of both primary hypotheses (H2 and H3). The quantitative One-Group Pretest-Posttest framework measures whether interactive syntax tree visualizations combined with transparent rule explanations yield statistically significant gains in deep-structure grammatical competence (H3). Concurrently, the qualitative expert validation phase evaluates the constituency parse trees against the Linguistic Constraint Matrix, empirically verifying that grounding the XAI engine on deterministic syntax structures eliminates generative hallucinations (H2). Hypothesis H1 is tested through deterministic parser accuracy on the benchmark corpus (zero-regression audit), and H4 is tested through System Usability Scale scores.


### **4.4 DATA COLLECTION**  

  	This section details the research instruments and benchmark datasets used to gather empirical data for evaluating the SynTutor system. Data collection is organized into quantitative measurements of student learning gain and system usability, alongside qualitative evaluations of syntactic parsing accuracy. The step-by-step administration procedure is presented in Section 4.4.3.  

  	**Table 4.1:** SynTutor Data Collection Instruments

| Instrument / Dataset | Data Type | Primary Objective | Target Group |
| :---- | :---- | :---- | :---- |
| Syntactic Pretest & Posttest | Quantitative (Interval) | Measures baseline vs. post-intervention grammatical competence | 50 BSCS Students |
| System Usability Scale | Quantitative (Interval) | Evaluate interface usability, clarity, and navigation efficiency | 50 BSCS Students |
| Linguistic Benchmark Dataset | Qualitative / Structural | Provide standardized test sentences for parsing and XAI evaluation | System Input |
| Expert Validation Matrix | Qualitative (Ordinal/Textual) | Evaluate constituency tree accuracy and XAI diagnostic correctness | 3 English Experts |


  	To evaluate the instructional impact of SynTutor, two parallel [NUM]-item assessments were developed. The pretest establishes baseline proficiency in identifying deep-structure English grammar concepts, including constituent phrase boundaries, clause hierarchies, and phrase-structure rules. The posttest contains items of equivalent difficulty and structural complexity to measure knowledge acquisition following system intervention without introducing item-recall bias. Both instruments were validated by domain experts prior to administration.

  	Additionally, user experience and interface clarity are measured using the standardized System Usability Scale. The instrument consists of 10 statements scored on a 5-point Likert scale ranging from 1 (“Strongly Disagree”) to 5 (“Strongly Agree”). The SUS provides a composite score out of 100 and allows the research team to evaluate whether the minimalist workspace and interactive tree canvas support effective user engagement. As for the linguistic benchmark dataset and the qualitative technical evaluation, a benchmark suite of 104 syntactically complex English sentences was constructed, of which 53 are grammatical and 51 are intentionally ungrammatical. The dataset includes sentences featuring structural ambiguities, nested subordinate clauses, and intentional grammatical errors, and it doubles as the system's regression corpus. This benchmark serves as the standardized input to stress-test the backend parsing engine.

  	Lastly, a structured evaluation matrix was designed for English experts to assess the output generated from the benchmark dataset. The matrix utilizes a 4-point rubric from 1 (“Incorrect”) to 4 (“Fully Accurate”) alongside qualitative commentary fields across two primary criteria:

* **Tree Generation Accuracy:** Evaluating whether the parsing and tree-reconstruction stages generate correct hierarchical constituency trees.  
* **XAI Explanation Correctness:** Verifying whether error diagnostics generated against the Linguistic Constraint Matrix accurately pinpoint syntactic violations without hallucination.  


#### **4.4.1 SAMPLING**  
  	The study utilizes a purposive sampling technique to select the target population of SynTutor, consisting of select respondents who meet the criteria relevant to SynTutor's usability testing and syntactic validity evaluation.  
  	The primary sample consists of fifty (50) regular Bachelor of Science in Computer Science (BSCS) students at De La Salle University – Dasmariñas who will be testing the system. BSCS students represent the primary target users whose background allows them to effectively evaluate the User Interface (UI) and functionalities of SynTutor, particularly in the syntax generation, XAI tutor, and the quality of the overall experience. Their status as learners also makes them candidates for assessing the grammatical explanation, syntactic rules, and the clarity of the explanation of the system.  
  	The secondary sample, who are three (3) English expert evaluators, are the English faculty members/instructors selected based on their credentials and experience in English Syntax. Their familiarity in language learning technologies are also considered as they would conduct quality assurance on both computation and educational outputs. Specifically, they will be evaluating the structural validity of the parser output and verify whether the XAI is able to produce grammatically accurate and educational feedback.  


#### **4.4.2 DATA ANALYSIS**  
  	This section outlines the quantitative and qualitative analytical methods applied to process the data gathered from student participants and English experts. To measure pedagogical learning gains and test Hypothesis H3, student pretest and posttest scores are analyzed using a Paired Samples t-Test at a significance level of $\alpha = 0.05$ (or a Wilcoxon Signed-Rank Test if score normality is violated) to determine whether exposure to SynTutor yields statistically significant improvements in deep-structure grammatical competence. System usability is evaluated by converting student responses on the System Usability Scale into a composite score out of 100 using the standard SUS calculation formula.  

  	This composite score determines interface acceptability, learnability, and navigation efficiency. Ratings from the Expert Validation Matrix are synthesized using mean scores and percentage accuracy across tree generation accuracy and XAI explanation correctness. In addition, the technical output of the backend is analyzed through a deterministic rule-coverage audit over the benchmark corpus, which records the number of gold-standard verdict regressions, the distribution of edge verdicts (valid, error, unlisted), and the number of edge types that fire no dedicated matrix rule. A zero-regression, zero-unrated result on this audit is the operational criterion for accepting Hypothesis H2, namely that grounding the XAI engine on deterministic syntax structures successfully eliminates generative hallucinations, while qualitative expert commentary is synthesized to identify structural edge cases for future rule-matrix refinement. Hypothesis H1 is evaluated through deterministic parser accuracy on the benchmark corpus: every grammatical sentence must be accepted and every intentionally ungrammatical sentence must be rejected, with zero verdict regressions. Hypothesis H4 is tested through the composite SUS score, with scores above 68 indicating acceptable usability.


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
	The evaluation phase measures the pedagogical effectiveness, interface usability, and technical precision of SynTutor by gathering empirical data from student end-users and subject matter experts, and by executing the system's built-in technical verification.

#### **4.6.1 RESPONDENTS OF THE STUDY**  
	The evaluation of the SynTutor system incorporates two distinct respondent groups selected through purposive sampling to evaluate both pedagogical usability and technical precision. The primary group consists of fifty (n = 50) regular Bachelor of Science in Computer Science (BSCS) students at De La Salle University – Dasmariñas (DLSU-D). As the primary end-users, their technical background enables them to effectively evaluate the interactive UI canvas and dynamic tree rendering, while their status as English language learners makes them ideal candidates to evaluate learning gains, explanation clarity, and syntactic priming. The secondary group comprises three (n = 3) English and Linguistics faculty members from DLSU-D. Selected for their academic credentials and tertiary teaching experience in English syntax, these experts perform technical quality assurance by verifying the structural precision of the constituency parser output and the diagnostic validity of the Explainable AI (XAI) feedback.

#### **4.6.2 RESEARCH INSTRUMENTS AND TECHNIQUES**  
	Data collection utilizes four primary research instruments designed to measure pedagogical impact, user experience, and computational accuracy. To evaluate instructional effectiveness, two parallel assessments, a syntactic pretest and posttest, measure baseline versus post-intervention student performance in identifying phrase boundaries and structural syntax rules without introducing bias.  
	User experience and interface clarity are measured using the standardized System Usability Scale (SUS), which consists of 10 statements scored on a 5-point Likert scale ranging from "Strongly Disagree" (1) to "Strongly Agree" (5) to generate a usability score out of 100. For the qualitative evaluation, a standardized linguistic benchmark dataset of 104 sentences containing syntactically complex English sentences that feature structural ambiguities and intentional errors is executed through the backend engine. Finally, a structured Expert Validation Matrix featuring a 4-point rubric (ranging from 1 for "Incorrect" to 4 for "Fully Accurate") and qualitative commentary fields is used by linguistics expert respondents to evaluate tree generation accuracy and XAI explanation correctness.

#### **4.6.3 DATA GATHERING**  
	The data gathering procedure is executed across four sequential phases to systematically capture quantitative student outcomes and qualitative expert reviews.

1. **Phase 1 (Pre-Intervention):** Student participants complete the syntactic pretest in a controlled environment to establish baseline grammatical comprehension prior to exposure to SynTutor.  
2. **Phase 2 (System Intervention):** Participants undergo an orientation on the interactive canvas and actively engage with the application by submitting sentences, exploring constituent tree boundaries, and reading automated rule-checking feedback.  
3. **Phase 3 (Post-Intervention Learning Gains & Usability):** Participants complete the parallel syntactic posttest immediately following the system interaction to evaluate knowledge acquisition, followed by the System Usability Scale survey to gather user interface feedback.  
4. **Phase 4 (Expert Technical Validation):** The standardized benchmark sentence dataset is executed through the SynTutor pipeline, and the resulting visual syntax trees and diagnostic explanations are compiled into review packets for independent evaluation by the English experts using the Expert Validation Matrix.  

   **4.6.4 TECHNICAL VERIFICATION OF THE SYSTEM**  
  	Beyond human evaluation, the system's output is verified automatically and repeatably. The gold-corpus regression audit drives the real parsing and evaluation pipeline over the sentence benchmark corpus and checks two properties:  
  	1. Every grammatical sentence is accepted and every intentionally ungrammatical sentence is rejected (no false positives and no false negatives).  
  	2. Every parent-child edge type exercised by the corpus is covered by a dedicated rule in the Linguistic Constraint Matrix (no unrated edge types).  
  	The audit reports the total number of evaluated edges and their verdict distribution and exits with a failure code on any regression, so it can serve as an acceptance gate. The current build passes this audit with zero verdict regressions, and zero unrated edge types. Complementary to the audit, the GET /api/health endpoint verifies that the NLP models are loaded and available before any evaluation session, and the deterministic design of the pipeline guarantees that repeated submissions of identical text return identical trees, verdicts, and explanations.


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
