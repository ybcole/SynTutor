# SynTutor Main-Branch Stress Report — 2026-11-15

**Target:** `main` worktree at `0100dbd` (`Merge origin/main (#173 Cambridge
lessons) into main`). The feature-branch checkout was not touched.

**Corpus:** the existing **183-sentence** stress suite plus a new **105-sentence**
complex-sentence corpus (38 grammatical, 41 ungrammatical, 26 known
provisional). Total: **288 complex sentences**.

**Method:** `scripts/stress_test_syntutor.py` for the 183-case baseline; a
separate runner for the 105 extra cases, using the same `build_payload`,
fact-graph and learner-explanation code. Detection expectations were tagged
per case (`grammatical` / `ungrammatical` / `provisional`).

**Artifacts**

- `artifacts/main-stress-base-2026-11-15.json`
- `artifacts/main-stress-extra-2026-11-15.json`

---

## 1. Baseline (183 cases)

| Metric | Value |
|---|---:|
| Cases | 183 |
| Fatal | 0 |
| Normalized | 165 |
| Labelled provisional working trees | 18 |
| Display labels available | 183 / 183 |
| Unlabelled triangles | 0 |
| Whole-sentence triangles | 0 |
| Red words without a bound explanation | 0 |
| Correction cascades | 0 |
| Cases flagged | 0 |

The baseline remains stable on `main`; nothing regressed from the earlier
verification.

## 2. Extra corpus (105 complex cases)

| Metric | Value |
|---|---:|
| Cases | 105 |
| Fatal | 0 |
| Normalized | 66 |
| Unresolved | 39 |
| Display labels available | 105 / 105 |
| Unlabelled triangles | 0 |
| Whole-sentence triangles | 0 |
| Grammatical cases | 38 |
| Ungrammatical cases | 41 |
| Provisional cases | 26 |
| False positives | **1** |
| True detection misses | **4** |
| Suggestion-only detections (by design) | 5 |
| Provisional cases now normalized | 3 |

**Visualization result:** every extra case produced a displayable tree; there
were **no** unlabelled nodes, no whole-sentence triangles, and no missing
display labels. The tree generator/visualizer did not fail on any of the 105
complex sentences.

## 3. Detection findings

### 3.1 False positive (real bug)

`Had I known, I would have called.`

- `C-COMMA-SPLICE` fires on the comma after the inverted conditional.
- `C-VBN-SIMPLE-PAST` fires on `known` even though it is the correct past
  participle in `Had I known`.

**Cause:** the comma-splice rule treats the inverted conditional as an
independent clause pair; the VBN rule reads the participle as a simple-past
error. Both should recognise `Had/Were/Should + subject + participle` as a
conditional inversion, not a comma splice or a simple-past error.

### 3.2 True detection misses

| Sentence | Missing finding | Why / risk |
|---|---|---|
| `The dog tail is long.` | `C-POSSESSIVE-S` (dog’s tail) | The rule only covers plural animate possessors (`students books`); singular `dog tail` is ambiguous with noun compounds (`car door`, `phone number`). |
| `I like very much this book.` | adverb/object order | `C-ADVERB-PLACEMENT` only covers pronoun objects (`V + ADVP + PRP`), not full NP objects. |
| `He always is late.` | frequency-adverb placement | No rule for `always/never/often/usually/sometimes + be`. |
| `The boss is gonna fire us.` | register | The tokenizer splits `gonna`; the register rule never sees the surface form. |

### 3.3 Suggestion-only detections (working as designed)

These are not misses; the rules intentionally return `suggestion` status:

- `I wish I was taller.` → `C-SUBJUNCTIVE`
- `Yesterday I go to school.` → `C-TENSE-TIME`
- `He said that he will come.` → `C-TENSE-CONSISTENCY`
- `He is a well known author.` → `C-HYPHEN`
- `I do a mistake every day.` → `C-COLLOCATION`

The report runner originally counted only `error` status, which made these look
like misses. They are visible in `summary.suggestions` and mapped back to their
constraints.

## 4. XAI quality on the extra corpus

| Metric | Value |
|---|---:|
| Self-referential explanations | **0** |
| Over-context (local word quoting the whole sentence) | **0** |
| Word explanations identical to their parent | **0** |
| Structural-layer repeats (UI-collapsed) | 102 |
| Jargon/internal-id leaks | 0 |

The non-repetition policy is working where it matters: **words and lexical
wrappers always have their own explanation**, and no word is collapsed onto an
enclosing `C2`/`VP`/`NP`. The 102 repeats are structural layers (`VP`/`NP`/`S′`)
whose text is identical to their parent; the UI collapses them, but the payload
still carries the duplicate copy. Moving the dedupe to the server
(`explanation_key` / `parent_key` / `is_structural_repeat`) would remove this
from the payload and make every consumer consistent.

## 5. Provisional tree gaps on `main`

26 cases remain unresolved (all produce labelled provisional trees, not
triangles):

**Inversion family (8)** — the largest cluster
- `Never have I seen such a storm.`
- `Only after the meeting did she realize the mistake.`
- `Here comes the bus.`
- `So tired was he that he fell asleep.`
- `Not until midnight did the committee finish.`
- `Rarely does the manager approve overtime.`
- `Under no circumstances should you open the door.`
- `Such was the impact that the policy changed.`

**Ellipsis / gapping (4)**
- `They reviewed the first draft and we the second.`
- `She can play the piano and he can too.`
- `The students finished the exam, and the teacher the grading.`
- `Some ordered tea, others coffee.`

**Appositives / parentheticals (3)**
- `The plan, a bold one, was approved.`
- `The proposal — a compromise — satisfied everyone.`
- `The CEO, a former engineer, explained the design.`

**Participial adjuncts (2)**
- `Having finished the report, she went home.`
- `The committee, having reviewed the evidence, approved the plan.`

**Comparatives (2)**
- `He earns less than his colleague.`
- `The more you practice, the better you become.`

**Non-finite perception/complex object (2)**
- `We heard the door close.`
- `The children were seen playing in the yard.`

**Pied-piping / stranding (1)**
- `Who did you give the keys to?`

**Nested relative gap (1)**
- `The book that the teacher recommended to the students who were preparing for the exam was out of print.`

Three formerly provisional cases now normalize: `Fewer students attended than
last year.`, `The report to which she referred was missing.`, and `The professor
who the students believe has submitted the report was praised.`

## 6. Recommended next steps (ranked)

1. **Fix the inverted-conditional false positive.** Teach comma-splice and
   VBN-simple-past rules that `Had/Were/Should + subject + participle` is a
   conditional inversion. Add `Had I known, I would have called.` as a
   regression.
2. **Extend adverb placement.** Cover `V + ADVP + full NP` (not only pronoun
   objects) and frequency adverbs before `be` (`He always is late`). Add
   regression pairs.
3. **Decide the singular possessive policy.** Either flag `the dog tail` with a
   safe animate-noun list, or document it as an intentional compound ambiguity.
   Do not extend blindly to `car door`/`phone number`.
4. **Handle register contractions before tokenization.** Check the original
   surface text for `gonna`, `wanna`, `gotta`, `kinda`, `ain't`; the tokenizer
   splits them.
5. **Close the inversion family** (8 cases) — the largest learner-visible tree
   gap. One licensed rule for negative/only/locative/so inversion; keep the
   ambiguity explicit where needed.
6. **Close appositives and participial adjuncts** (5 cases) — both are common
   in academic writing and currently provisional.
7. **Move explanation dedupe server-side.** Return `explanation_key`,
   `parent_key`, and `is_structural_repeat`; remove the 102 structural repeats
   from the payload.
8. **Promote this 105-case corpus into the permanent stress suite** and add CI
   gates: 0 false positives on tagged grammatical cases, 0 true misses on
   tagged ungrammatical cases, 0 triangles, 0 unbound words.

## 7. Bottom line

- **Detection:** strong overall. 1 false positive and 4 true misses across 105
  complex cases (5 of 79 error-relevant cases); the other 5 flagged cases are
  suggestion-only by design.
- **Tree generation/display:** no failures. Every case was displayable, with no
  unlabelled or whole-sentence triangles. The remaining 26 cases are known
  construction gaps, not rendering failures.
- **XAI:** non-repetition for words is solid (0 self-reference, 0 over-context,
  0 word-parent duplicates). Structural-layer repeats (102) remain a payload
  and architecture issue, best fixed server-side.
