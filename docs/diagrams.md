# SynTutor — Diagram Sources (PlantUML / PlantText)

Plain-text PlantUML source for every figure referenced in `docs/thesis.md`.
Paste any block into https://www.planttext.com (or any PlantUML renderer) to generate the image.

Figures covered:

- Figure 3.1.1 — Agile-Scrum Methodology
- Figure 3.2.1 — System Architecture of SynTutor
- Figure 3.4.1 — IPO Framework of SynTutor
- Figure 3.4 — Use Case Diagram of SynTutor
- Figure 3.5 — System Flowchart of SynTutor
- Figure 3.6 — State Diagram of SynTutor

---

## Figure 3.1.1 — Agile-Scrum Methodology

```plantuml
@startuml Figure 3.1.1 Agile-Scrum Methodology
title Figure 3.1.1 Agile-Scrum Methodology

start
:Establish foundational scope
(project boundaries, target domain,
core system objectives);
:Product Backlog
(NLP pipeline, recursive-descent decoder,
constraint matrix, licensing layer,
hybrid detector + correction search,
syntax-tree + practice-quiz interfaces);
:Design
(system architecture, UI/UX wireframes,
state-machine logic, auth DB schemas);

repeat
  :Sprint Planning Meeting
  (select priority tasks -> Sprint Backlog);
  :Sprint Execution
  (coding + algorithm development);
  :Daily Scrum
  (track progress, resolve bottlenecks);
  :Sprint Automation
  (matrix regression check, rule suites,
  licensing tests, gold-corpus audit);
  :Sprint Review Meeting
  (demonstrate working software to adviser);
  :Sprint Retrospective
  (evaluate process, identify improvements);
repeat while (More sprints?) is (yes) not (no)

:Deploy usable web application
(input sentences, explore interactive
syntax trees, receive real-time explanations);
stop

@enduml
```

---

## Figure 3.2.1 — System Architecture of SynTutor

```plantuml
@startuml Figure 3.2.1 System Architecture of SynTutor
title Figure 3.2.1 System Architecture of SynTutor
skinparam componentStyle rectangle

component "User Input" as userInput

component "Preprocessing\n(spaCy en_core_web_md)" as pre

component "NLP Parsing Engine" as engine {
  component "1. Tokenization & POS\n(spaCy en_core_web_md)" as stage1
  component "2. Constituency Parsing\n(benepar_en3)" as stage2
  component "3. Parse-string Decoding\n(recursive-descent + NodeBuilder)" as stage3
}

component "Selected Syntax Tree" as tree

component "Error Detection & XAI" as xai {
  component "Linguistic Constraint Matrix\n(matrix.py + ruleset.py)" as matrix
  component "Positive-evidence Licensing\n(licensing.py)" as licensing
  component "Hybrid Acceptability Detector\n(detector.py)" as detector
  component "Correction Search\n(corrector.py)" as corrector
}

component "Output Generation" as output

component "User Interface\n(tree renderer + Matrix Quiz)" as ui

userInput --> pre
pre --> engine
stage1 --> stage2
stage2 --> stage3
engine --> tree
tree --> xai
matrix --> output
licensing --> output
detector --> output
corrector --> output
output --> ui
ui ..> userInput : User-Driven Re-entry loop

@enduml
```

---

## Figure 3.4.1 — IPO Framework of SynTutor

```plantuml
@startuml Figure 3.4.1 IPO Framework of SynTutor
title Figure 3.4.1 IPO Framework of SynTutor

skinparam rectangle {
  BackgroundColor #F7F7F7
}
skinparam usecase {
  BackgroundColor #FFFFFF
}

rectangle "INPUT" {
  usecase "Text input & sanitization" as i1
  usecase "Select target sentence" as i2
  usecase "Node click (mouse event)" as i3
}

rectangle "PROCESS" {
  usecase "Lexical & morphological analysis\n(tokenization + POS tagging)" as p1
  usecase "Syntactic parsing, tree reconstruction,\nserialization (benepar + decoder)" as p2
  usecase "XAI structural evaluation\n+ hybrid verification channel" as p3
}

rectangle "OUTPUT" {
  usecase "Interactive canvas\n(interactive syntax-tree rendering)" as o1
  usecase "Pedagogical feedback\n(natural-language explanation)" as o2
}

i1 --> p1
i2 --> p1
p1 --> p2
p2 --> p3
p3 --> o1
p3 --> o2
o1 --> i3
i3 --> p3
o2 --> i3

@enduml
```

---

## Figure 3.4 — Use Case Diagram of SynTutor

```plantuml
@startuml Figure 3.4 Use Case Diagram of SynTutor
title Figure 3.4 Use Case Diagram of SynTutor
left to right direction

actor Student

rectangle SynTutor {
  usecase "Submit text" as UC1
  usecase "View syntax tree" as UC2
  usecase "View basic explanation" as UC3
  usecase "Interact with Syntax Tree" as UC4
  usecase "Detailed explanation" as UC5
}

Student --> UC1
Student --> UC2
Student --> UC4

UC2 ..> UC3 : <<include>>
UC5 ..> UC4 : <<extend>>

@enduml
```

---

## Figure 3.5 — System Flowchart of SynTutor

```plantuml
@startuml Figure 3.5 System Flowchart of SynTutor
title Figure 3.5 System Flowchart of SynTutor

start
repeat
  :User submits text;
  :Preprocessing
  (tokenization, POS tagging, normalization);
  :NLP Parsing Engine
  (benepar neural parse -> recursive-descent decode);
  :Error Detection & XAI
  (constraint matrix + licensing + hybrid acceptability check);
  :Display output in UI
  (interactive syntax tree + basic explanation);
  note right
    Interaction loop: a node click
    retrieves the stored XAI explanation
    -- no reprocessing occurs.
  end note
  :Retrieve XAI (on node select);
  :Display detailed explanation;
repeat while (User submits new text?) is (yes)
stop

@enduml
```

---

## Figure 3.6 — State Diagram of SynTutor

```plantuml
@startuml Figure 3.6 State Diagram of SynTutor
title Figure 3.6 State Diagram of SynTutor

[*] --> Idle

Idle --> Processing : User input of text

state Processing {
  [*] --> Preprocessing
  Preprocessing --> Parsing
  Parsing --> "Syntax tree generated"
  "Syntax tree generated" --> "Explanation computed"
  "Explanation computed" --> "Output ready"
  "Output ready" --> [*]
}

Processing --> Viewing : Output ready

state Viewing {
  Viewing : Interactive syntax tree rendered
  Viewing : Basic UI explanation displayed
}

Viewing --> Exploring : User selects node
Exploring --> Viewing : Back to syntax tree
Viewing --> Processing : User submits new text
Viewing --> [*] : User exits

@enduml
```

---

## Figure 3.5 (alternative) — Explicit Flowchart with Decision Diamonds

Use this variant if you prefer literal decision diamonds instead of the loop shorthand above.

```plantuml
@startuml Figure 3.5 System Flowchart of SynTutor (explicit)
title Figure 3.5 System Flowchart of SynTutor

start
:User submits text;
:Preprocessing;
:NLP Parsing Engine;
:Error Detection & XAI;
:Display output in UI;
if (User selects a node?) then (yes)
  :Retrieve XAI (no reprocessing);
  :Display detailed explanation;
  note right: Interaction loop -> re-evaluate node selection
else (no)
  if (User submits new text?) then (yes)
    :Re-entry loop;
    note right: Restart at "User submits text"
  else (no)
    stop
  endif
endif
stop

@enduml
```
