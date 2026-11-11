# SynTutor — Friday Validation Findings

**Test date:** November 11, 2026  
**Branch:** `qa/friday-validation`  
**Environment:** Linux Mint, local Flask backend on port 8001  
**Status:** Initial four test cases completed

## QA-001 — Generic node-level explanations

**Severity:** Medium

**Input:** The boy runs.

**Observed:** The generated tree follows the expected basic phrase structure. However, several XAI explanations describe grammatical categories without sufficiently explaining the corresponding nodes' relationships or grammatical functions.

**Expected:** Contextual explanations of constituents, their grammatical functions, and their relationships within the sentence.

## QA-002 — Detected agreement error not explained by node-level XAI

**Severity:** High

**Input:** The boys runs.

**Observed:** The legacy diagnostic engine triggers `C-SUBJECT-AGREEMENT` and proposes “The boys run.” However, the corresponding syntax-tree explanations do not explain the agreement violation.

**Expected:** A clearly attributed explanation of the disagreement between the plural subject and third-person singular verb, without claiming independent Cambridge verification.

## QA-003 — Cambridge diagnostic rules not enabled

**Severity:** High — Release limitation

**Observed:** The Cambridge evaluator reports `no_runtime_rules` for the tested examples. The API explicitly indicates that its legacy findings are not independently book-verified.

**Expected:** The interface should accurately distinguish legacy diagnostic findings from independently reviewed Cambridge-based findings. Rules should only be enabled after the required review and evaluation gates.

## QA-004 — Circular and incomplete auxiliary explanations

**Severity:** Medium

**Input:** She can sing.

**Observed:** The syntax-tree structure follows the expected modal auxiliary hierarchy. Some node explanations are circular or omit why the modal requires the following verb to appear in its plain form.

**Expected:** Explanations that identify the function of the modal, the structure of its VP complement, and the form-selection relationship.

## QA-005 — Diagnostic information unavailable through unresolved-tree XAI

**Severity:** High

**Input:** She can sings.

**Observed:**
- Legacy verdict: `ungrammatical`
- Triggered constraint: `C-MODAL-VERB-FORM`
- Suggested correction: “She can sing.”
- Burton-Roberts status: `unresolved`
- Cambridge status: `not_evaluated`

The UI correctly displays a provisional working tree with unresolved nodes, but node selection only shows a structural uncertainty message.

**Expected:** Preserve uncertainty about the canonical tree while separately exposing the legacy finding and proposed correction, clearly marked as not independently book-verified.

## Overall findings

The initial tests indicate that SynTutor can generate plausible Burton-Roberts trees for selected grammatical sentences and can detect certain errors through its legacy rule system.

The main observed weakness is the separation between diagnostic findings and learner-facing explanations.

These four examples do not establish general tree-generation accuracy, grammar-detection precision, correction reliability, or independent Cambridge verification.

## Recommended priorities

1. Connect supported diagnostic findings to learner-facing explanations.
2. Preserve explicit uncertainty and diagnostic authority.
3. Improve contextual explanations for grammatical relationships.
4. Add regression tests covering valid and invalid sentence pairs.
5. Independently review grammar rules before enabling them as Cambridge-verified diagnostics.

## QA-007 — Inconsistent modal-inflection diagnostics

**Severity:** High
**Reference:** Cambridge Grammar, Chapter 3, §2.4

**Problem 1 — False negative**

Input: She cans sing.

Actual:
- No legacy diagnostic triggered.
- No correction suggested.
- Burton-Roberts analysis unresolved.

Expected:
- Identify the invalid inflection of the central modal auxiliary.
- Suggest "She can sing."

**Problem 2 — Incorrect rule attribution**

Input: They cans sing.

Actual:
- C-SUBJECT-AGREEMENT triggered.
- Explanation attributes the error to subject–verb disagreement.
- Suggested correction: "They can sing."

Expected:
- Identify the central modal's inflectional restriction.
- Avoid attributing this particular error to ordinary subject–verb agreement.

**Reproduction:** test_rule_attribution.py

**Status:** Confirmed against the local QA backend.

## QA-008 — Lexical/modal ambiguity causes unresolved syntax tree

**Severity:** Medium
**Area:** Constituency parsing and Burton-Roberts normalization
**Status:** Reproduced with automated regression test

### Problem

SynTutor fails to normalize an acceptable sentence when the
word "can" functions as a lexical verb rather than a modal.

### Reproduction

Sentence: They can the peaches.

Expected:
- Recognize the intended lexical-verb interpretation.
- Produce a normalized transitive clause tree.
- Do not report a grammatical error.

Actual:
- Benepar labels "can" as MD (modal auxiliary).
- Raw parse: (VP (MD can) (NP ...))
- B-R analysis status: unresolved
- Diagnostic: PROFILE_MAPPING_NOT_APPROVED
- Reason: Auxiliary has no overt VP complement.
- No legacy grammar error is reported.

### Contrastive example

Sentence: She cans the peaches.

Actual:
- Benepar labels "cans" as VBZ.
- B-R analysis status: normalized.
- No grammar error is reported.

### Root-cause evidence

The upstream parser selects an incorrect modal interpretation
for "They can the peaches." The B-R normalizer subsequently
rejects the unsupported auxiliary-plus-NP structure.

This identifies the immediate failure mechanism, not the
complete architectural root cause.

### Recommended investigation

Evaluate constrained alternative lexical analyses when the
initial parser interpretation is incompatible with supported
syntactic evidence.

Do not apply a blanket MD-to-VB conversion.

### Regression test

evaluation/friday_validation/test_lexical_can_structure.py

Current result: 2 passed, 1 failed.

## QA-009 — Incorrect modal-form diagnosis in interrogative clauses

**Severity:** High
**Area:** Legacy grammar diagnostics and correction generation
**Status:** Confirmed through automated regression tests

### Problem

SynTutor misclassifies a modal verb-form violation in an
interrogative sentence as a run-on sentence.

### Reproduction

Input: Can she swims?

Expected:
- Detect the incorrect verb form following the modal.
- Attribute the violation to modal plain-form selection.
- Suggest: "Can she swim?"
- Avoid reporting a run-on sentence.

Actual:
- Triggered constraint: C-RUNON
- Suggested correction: None
- B-R status: normalized

### Parser evidence

Raw parse:
(SQ (MD Can) (NP (PRP she)) (VP (VBZ swims)) (. ?))

Benepar identifies the modal and question structure.

The legacy diagnostic reports two finite elements as
a run-on construction, despite the sentence containing
a single interrogative clause.

### Contrast

"He can swims." correctly triggers C-MODAL-VERB-FORM.

"Can she swims?" incorrectly triggers C-RUNON.

### Educational impact

The explanation advises students to add punctuation or
conjunctions instead of explaining the required plain
form of the verb following a central modal.

### Recommended investigation

Review modal-form checks under subject-auxiliary inversion
and the structural conditions that trigger C-RUNON.

Ensure diagnostic rules do not treat an inverted auxiliary
and its lexical verb as independent clauses.

### Regression test

evaluation/friday_validation/test_question_modal.py

Current result: 1 passed, 3 failed.
