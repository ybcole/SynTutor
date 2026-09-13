SynTutor is an explainable AI-driven intelligent tutoring system that uses phrase-structure syntax trees to teach English grammar through deterministic structural analysis and pedagogical feedback. Below is the complete design specification and instruction set required to build SynTutor based on the paper's framework, algorithms, state machines, and mathematical formalizations.

System Overview & Core Purpose
System Name: SynTutor.

Core Objective: Replace opaque "black-box" grammar correction tools (which grant surface-level edits without teaching) with a transparent, rule-grounded framework that visualizes sentence constituency and provides explicit explanations for grammatical relationships.

Target Audience: English language learners, students, educators, and linguistic researchers.

Primary Function: Parse English text into interactive phrase-structure syntax trees, validate structural dependencies, and present clear, node-level natural language feedback.

Architectural Pipeline (7 Interconnected Stages)
SynTutor operates via an event-driven Input-Process-Output (IPO) architecture featuring a dual-loop feedback mechanism:

User Input Phase: Accepts raw English text (single sentences or extended passages). The user isolates a target sentence for processing without automated transformations.

Preprocessing Phase: Converts unstructured text into a standardized token sequence via tokenization, part-of-speech (POS) tagging, case normalization, punctuation handling, and noise removal.

NLP Parsing Engine: Computes sentence constituent structures using a Probabilistic Context-Free Grammar (PCFG) solved via the Cocke-Younger-Kasami (CYK) algorithm with probabilistic Viterbi decoding.

Selected Syntax Tree: Generates a single, maximum a posteriori ($\arg\max P(T)$) phrase-structure tree. The structure originates at the root sentence node ($S$) and branches into constituent phrases ($NP, VP, PP$, etc.) down to leaf word nodes.

Error Detection & XAI Module: Performs deterministic (non-generative) evaluation of each parent-child node pair against a predefined Linguistic Constraint Matrix ($\mathcal{C}$).

Output Generation: Translates structural evaluations ($f_{valid}$ or $f_{error}$) into plain-language pedagogical explanations.

User Interface Canvas & Feedback Loop: Renders an interactive tree diagram on a client-side canvas with clickable hitboxes. Includes a user-driven manual re-entry loop for editing text and resubmitting.

Mathematical & Algorithmic Engine
1. Probabilistic Context-Free Grammar (PCFG)
Model English syntax as a formal 5-tuple:

$$G = (N, \Sigma, R, S, P)$$


$N$: Finite set of non-terminal symbols representing grammatical categories (e.g., $S, NP, VP, PP$).

$\Sigma$: Finite set of terminal symbols (vocabulary words).

$R$: Production rules of the form $A \to \beta$, where $A \in N$ and $\beta \in (N \cup \Sigma)^*$.

$S$: Start symbol representing a complete sentence ($S \in N$).

$P$: Probability function assigning $P(A \to \beta)$ to each rule in $R$.

Stochastic Constraint:

$$\sum_{\beta} P(A \to \beta) = 1 \quad \forall A \in N$$


Tree Probability & Optimization:
The probability of syntax tree $T$ yielding sentence $S$ with rule applications $r_i$ is calculated as:

$$P(T, S) = \prod_{i=1}^{n} P(r_i)$$


The parsing engine extracts the Maximum A Posteriori tree $\hat{T}$:

$$\hat{T} = \arg\max_{T \in \tau(S)} P(T)$$


2. CYK Parsing Algorithm & Probabilistic Viterbi Decoding
Chomsky Normal Form (CNF) Pre-requisite: Convert all grammar rules in $R$ to strict CNF ($A \to BC$ or $A \to a$).

3D Dynamic Programming Table: Construct table $\pi(i, j, A)$ storing the maximum probability of non-terminal $A$ spanning words $w_i$ to $w_j$:

Base Case ($i = j$):

$$\pi(i, i, A) = P(A \to w_i) \quad \text{for } 1 \le i \le n$$


Recursive Step ($i < j$):

$$\pi(i, j, A) = \max_{i \le k < j, \, A \to BC \in R} \left[ P(A \to BC) \cdot \pi(i, k, B) \cdot \pi(k+1, j, C) \right]$$


Backpointer Matrix: Maintain backpointer matrix $\mathcal{B}(i, j, A)$ storing optimal split points $k$ and child non-terminals $B, C$ to serialize the rendered tree layout.

Complexity Metrics:

Time Complexity: $\mathcal{O}(n^3 \cdot \vert{}G\vert{})$.

Space Complexity: $\mathcal{O}(n^2 \cdot \vert{}G\vert{})$.

3. XAI Structural Validation & Explanation Algorithm
The XAI module evaluates structural relationships deterministically without generative language models:

Let $V$ be the set of nodes in tree $\hat{T}$. For a dependent node $v_d$ and parent node $v_p$, evaluate relationship function $E(v_d, v_p)$ against Linguistic Constraint Matrix $\mathcal{C}$:

$$E(v_d, v_p) = \begin{cases} f_{valid}(v_d, v_p), & \text{if } (v_d \to v_p) \in \mathcal{C} \\ f_{error}(v_d, v_p, \delta), & \text{if } (v_d \to v_p) \notin \mathcal{C} \end{cases}$$


Valid State Execution ($f_{valid}$): Maps $v_d$ and $v_p$ properties to a positive confirmation template and defines functional grammatical roles ($Role(v_d) = \text{Map\_To\_Function}(Type(v_d), Type(v_p))$).

Error State Execution ($f_{error}$): Identifies violation rule $\delta$ and produces a deterministic failure diagnostic: "The node " + Type(v_d) + " cannot structurally append to " + Type(v_p) + " because it violates constraint " + \delta.

User Interface & Operational Flow
Use Cases & Actors
Primary Actor: Student / Learner.

Core Use Cases:

Submit Text: Primary entry point to initiate text analysis.

View Syntax Tree: Displays interactive tree diagram; automatically triggers View Basic Explanation(<<include>> relationship).

Interact with Syntax Tree: Canvas node selection triggers Detailed Explanation modal (<<extend>> relationship).

System State Machine & Behavior
System StateNested Sub-States / Operational LogicEvent / Transition TriggerIdleSystem is inactive, waiting for initial text submission.

User submits text $\to$Transitions to Processing.

ProcessingExecuted as an automated composite state machine:


1. Preprocessing


2. Parsing


3. SyntaxTreeGenerated


4. ExplanationComputed


5. OutputReady



Output ready $\to$Transitions to Viewing.

ViewingRenders interactive syntax tree on dynamic canvas and displays precomputed basic pedagogical explanation.

User selects syntax node$\to$ Transitions to Exploring.


User submits new input$\to$ Transitions to Processing.


User exits $\to$ Transitions to End.

ExploringRetrieves precomputed node-level XAI explanation string directly from memory without triggering re-parsing.

Back to syntax tree $\to$Returns to Viewing.

Dual-Loop Feedback Mechanics
Interaction Loop (Lightweight Retrieval): Clicking individual nodes or branches fetches precalculated XAI explanations directly from DOM state. No reprocessing or parsing engine runs during exploration.

Re-Entry Loop (Full Pipeline Restart): Resubmitting edited or new text manually triggers a complete run of the 7-stage pipeline. Auto-correction is intentionally prohibited to promote active learning and user autonomy.

Technical Scope & Constraints
Language Scope: Exclusively supports English language text.

Parsing Framework: Constituent-based / phrase-structure trees ($S, NP, VP, PP, AP, AdvP$). Dependency parsing structures are explicitly excluded.

Linguistic Scope: Focuses strictly on sentential syntax, POS tagging, tense, agreement, and modifier placement. Excludes semantic analysis, pragmatics, style edits, or generative text creation.

XAI Integrity: Must remain 100% deterministic, grounding all natural-language explanations in verifiable tree backpointers and constraint matrices to eliminate AI hallucinations.