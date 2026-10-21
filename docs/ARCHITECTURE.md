# SynTutor — Architecture and Logic

This document describes how SynTutor actually works, from the first browser
byte to the final node explanation, and from a source sentence to a verdict.
It is derived from the code in this repository, not from a design proposal.
Where a number or model name appears, it is the number the code uses today.

---

## 0. The system in one page

SynTutor answers four different questions about a sentence, and deliberately
keeps the answers in four separate layers:

| Question | Layer | Technology | Output |
|---|---|---|---|
| How is the sentence structured? | Parser | spaCy `en_core_web_md` + benepar `benepar_en3` | A constituency tree (`S → NP VP .`) |
| Why is that structure valid or invalid? | Rule matrix | Hand-authored constraints in `server/matrix.py`, `server/ruleset.py`, `server/licensing.py` | Per-node verdicts and explanations |
| Is the sentence acceptable English? | Detector | `textattack/roberta-base-CoLA` acceptability classifier | `acceptable` / `unacceptable` |
| What single edit repairs it? | Corrector | DistilBERT masked-LM sweep + clean-tree verification | One word replacement with a morphological reason |

The central design decision is that **the neural model locates structure but
does not author explanations**. benepar produces the tree; the symbolic matrix
walks that tree and produces the "why". A trained detector may *flag* a
sentence the rules cannot explain, but it is never allowed to invent a rule
reason: that case becomes `unverified`, not `ungrammatical`.

## Contents

- [0. The system in one page](#0-the-system-in-one-page)
- [1. Repository and runtime topology](#1-repository-and-runtime-topology)
- [2. The request lifecycle, stage by stage](#2-the-request-lifecycle-stage-by-stage)
- [3. The rule matrix in detail](#3-the-rule-matrix-in-detail)
- [4. Lessons, quiz, and Syntax Builder](#4-lessons-quiz-and-syntax-builder)
- [5. Content pipeline and generated sheets](#5-content-pipeline-and-generated-sheets)
- [6. Authentication and data model](#6-authentication-and-data-model)
- [7. Failure modes and degradation](#7-failure-modes-and-degradation)
- [8. Determinism, auditing, and known limits](#8-determinism-auditing-and-known-limits)
- [9. How to extend the system](#9-how-to-extend-the-system)
- [Appendix A — Key data shapes](#appendix-a--key-data-shapes)
- [Appendix B — Glossary](#appendix-b--glossary)

```
Browser (web/)
  main.js ──POST /api/parse──▶ server/webapp.py (Flask)
                                   │
                                   ▼
                              server/api.py ── build_payload()
                                   │
              ┌────────────────────┼─────────────────────┐
              ▼                    ▼                     ▼
    parse_engine.analyze     matrix.evaluate       detector.classify
    spaCy → benepar →        _walk / _classify     CoLA acceptability
    NodeBuilder              + licensing layer           │
              │                    │                     ▼
              │                    │              combine(summary, det)
              │                    │                     │
              │                    └──── verdict ────────┘
              │                                          │
              │                         if unverified: corrector.sweep
              │                                          │
              └──────────────► payload JSON ◀────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
  TreeRenderer               Lessons / Quiz            Syntax Builder
  (canvas tree)              (tree-quiz.js)            (node editor)
```

---

## 1. Repository and runtime topology

```
server/
  webapp.py         Flask transport; serves web/ and /api/*
  app.py            Legacy stdlib http.server with the same API
  hf_space.py       Hugging Face Spaces entrypoint (Gradio + mounted API)
  api.py            Transport-independent request/response logic
  parse_engine.py   Stage 1–3: tokenization, POS, benepar parse, node graph
  matrix.py         Stage 4: constraint matrix, node details, remediation
  ruleset.py        Rulebook (111 rules) + tree/wordlist/context checkers
  licensing.py      Positive-evidence lexical licensing + relative clauses
  detector.py       CoLA acceptability classifier (optional)
  corrector.py      MLM correction search (optional)
  spellcheck.py     Pre-parser lexicon and spelling repair
  master.py         Accessor for the generated content sheet

web/
  index.html        Application shell
  login.html        Standalone Clerk form
  css/style.css     Shell, workspace, canvas, themes
  css/quiz.css      Lessons, quiz, builder, drawers
  js/main.js        Workspace state machine, pipeline client, history
  js/renderer.js    Canvas tree layout and interaction
  js/ui.js          Node inspector, diagnostics, sentence selection
  js/tree-quiz.js   Lessons, quiz sessions, guide cards, progress
  js/syntax-builder.js      DOM-free node-graph model + tree comparison
  js/syntax-builder-ui.js   Canvas editor, Build-tree validation, XAI
  js/auth.js        Clerk + Supabase client
  js/level.js       XP / level curve
  js/achievements.js Achievement derivation
  js/rule-concepts.js       Rule concept text (folded into the tree sheet)
  js/tree-catalog.js        Four pipeline stages for achievements
  js/theme.js       Theme persistence
  js/config.js      Client keys + API_BASE (template: config.example.js)

scripts/
  tree_sheet.py           Generate docs/tree_sheet.* + web/content/tree_sheet.json
  build.js                Copy web/ to dist/ for Vercel
  master_sheet.py         Detection audit over the quiz corpus
  explanation_sheet.py    Explanation audit over valid node details
  audit_rules.py          Rule-regression audit
  test_tree_quiz.js       Quiz content audit (npm run test:quiz)
```

Runtime entry points:

- Local development: `python3 server/webapp.py` (Flask, port 8000) or
  `npm run serve`; legacy server `python3 server/app.py` (`npm run serve:legacy`).
- Production frontend: `npm run build` → `dist/`, deployed by Vercel
  (`vercel.json`: build command `npm run build`, output `dist`).
- Hugging Face Space: `server/hf_space.py` imports `server/app.py` and mounts
  its handler on the Gradio/FastAPI app. A no-op `@spaces.GPU` function exists
  only to satisfy ZeroGPU's startup scan; all inference is CPU-only.

---

## 2. The request lifecycle, stage by stage

### Stage 1 — Browser boot

`web/index.html` does four things in order:

1. An inline script reads `syntutor_theme` from `localStorage` and sets
   `data-theme` before first paint (no flash of the wrong theme).
2. Loads `css/style.css` and `css/quiz.css`.
3. Loads `js/config-hint.js`, a classic script that probes for `js/config.js`
   and prints a setup warning if a fresh checkout is missing it.
4. Loads `js/main.js` as an ES module.

`main.js` runs its top-level authentication bootstrap before defining the
workspace:

- `loadClerk()` dynamically injects `clerk.browser.js` from the Frontend API
  domain derived from the publishable key. It is a deferred singleton, so the
  bundle loads once.
- `createSupabaseClient()` builds a Supabase client whose `accessToken`
  callback returns the current Clerk session token. Clerk is registered as a
  third-party auth provider in Supabase, so the Clerk JWT is accepted by RLS.
- If Clerk cannot load, the app continues in guest mode instead of failing.
- A Clerk listener watches identity changes (sign-in, sign-out, account
  switch). When the session id changes, the in-memory history cache and the
  de-duplication set are cleared so one account never sees another's data.

`boot()` then creates the `TreeRenderer`, wires events, restores the theme,
purges legacy guest history, initializes the sidebar, calls
`initSyntaxBuilder(...)` and `initQuiz({...})` with the controller object
(quiz analysis, mode switching, progress, chat title), installs the pane
resizers, enters the `IDLE` state, and optionally starts the first-visit
onboarding tour.

### Stage 2 — Input capture

The input is a textarea (`#inputText`) overlaid by a highlight layer
(`#inputHighlights`). It starts read-only and locked.

- Clicking the textarea enters edit mode (`readOnly = false`).
- Blur re-locks it. If the text changed since the last analysis, blur calls
  `runPipeline()`.
- `Ctrl+Enter` / `Cmd+Enter` submits while editing; `Escape` leaves edit mode.
- In a locked multi-sentence passage, the overlay draws one clickable span per
  sentence. Clicking a non-active sentence re-runs the pipeline with that
  sentence's `sentence_index` without unlocking the textarea. Clicking the
  active sentence (or double-clicking a span) edits the whole passage.
- `runPipeline()` refuses to run unless the workspace is the Grammar Tutor
  (`workspaceView === 'tutor'`); Lessons and the Syntax Builder own the canvas
  through separate paths.

The request is:

```http
POST /api/parse
Content-Type: application/json

{ "text": "The clever boy reads a book.", "sentence_index": 0 }
```

`main.js` uses `API_BASE` from `js/config.js`; an empty value means
same-origin, which is how the local Flask server and the Vercel build are
wired.

### Stage 3 — Transport validation

`server/webapp.py` (`app.py` mirrors it) validates before touching a model:

| Condition | Response |
|---|---|
| Body is not JSON | `400 invalid request payload` |
| `text` empty after trim | `422 empty input` + hint |
| `sentence_index` not an integer | `400 sentence_index must be an integer` |
| `sentence_index < 0` | `400 sentence_index must be >= 0` |
| `ParseFailure` from the parser | `422` with the input |
| Any other exception (models unavailable) | `503` with install hint |

Static serving is restricted to `PUBLIC_TOP = {index.html, login.html, css,
js, content}`. Anything else under the repository (server code, scripts,
migrations, configuration) is never exposed. CORS is controlled by
`SYNTUTOR_ALLOW_ORIGIN` (default `*`) and responses are `Cache-Control:
no-store`.

### Stage 4 — Segmentation, POS tagging, and constituency parsing

`server/parse_engine.py::analyze(text, sentence_index)` is the only NLP entry
point. Its pipeline:

1. **Whitespace normalization.** `_normalize_parser_text` collapses every run
   of whitespace into one space but keeps two parallel arrays (`starts`,
   `ends`) mapping each normalized character back to the original input. This
   is what lets the frontend highlight the exact character range the user
   typed even after normalization.
2. **spaCy run.** `load_models()` loads `en_core_web_md` once and adds the
   `benepar` pipe with `benepar_en3`. During load, `torch.cuda.is_available`
   is temporarily forced to `False`; under ZeroGPU that probe reports a
   phantom GPU and kills the process. It is restored immediately afterwards.
   Both success and failure are cached (`_nlp`, `_load_error`).
3. **Sentence selection.** `doc.sents` gives sentence boundaries.
   `sentence_index` is clamped to `[0, len(sents)-1]`; out-of-range indices do
   not error, they select the nearest sentence.
4. **Constituency parse.** The target `Span` carries benepar's
   `_.parse_string`, the deterministic S-expression rendering of the selected
   tree.
5. **Decode.** `parse_parse_string` is a recursive-descent parser over the
   regex token stream `\(|\)|[^\s()]+`. It returns nested
   `(label, children)` tuples.
6. **Node graph.** `NodeBuilder` walks that nested structure and emits JSON
   nodes:
   - id: `n0`, `n1`, … in depth-first order;
   - leaves: `type` = PTB tag, `pos` = same tag, `span = [i, i+1]`,
     `surface` = word, `punct` = whether the tag is punctuation;
   - internal nodes: `type` = phrase label, `span = [first leaf, last leaf)`,
     `surface` = joined leaf text, `children`.
   - An empty benepar subtree is dropped instead of crashing.
   - After the build, the leaf counter must equal `len(target)`; otherwise
     `ParseFailure('span alignment mismatch: …')`.
7. **Token metadata.** `token_metadata` records `i`, `t`, `start`, `end`,
   `pos` (UPOS), `tag` (PTB), `dep`, `head` for every token, with character
   offsets mapped through the normalization arrays.
8. **Fine-grained tags.** Leaves are enriched by token order with `ftag`
   (spaCy PTB tag) and `fpos` (UPOS), so morphology checks are not limited to
   benepar's coarse tags.

The function returns the target sentence, sentence count, all sentence spans
with original character offsets, the token list, the parse string, the root
node, and the flat `nodes` map.

### Stage 5 — The deterministic constraint matrix

`server/matrix.py::evaluate(root, text)` instantiates `MatrixEvaluator` and
runs five phases.

#### 5.1 Pre-scan

`evaluate` first walks the tree and records, for every `VP` that directly
contains an `SBAR`, the head verb governing that clause
(`self._sbar_gov`). This lets subjunctive licensing depend on the actual
governing verb rather than a nearby word. It also records quoted leaf spans
(`_quoted_ids`).

#### 5.2 Edge walk

`_walk` visits every parent/child edge and creates one detail record per
child:

- **Punctuation** → `C-PUNCT`, `valid`, "the punctuation … closes the …".
- **Fully quoted subtree** → `C-QUOTE`, `valid`, verbatim material not judged
  by the surrounding grammar.
- **Everything else** → `_classify(parent, child, grandparent)`, a dispatch
  over the parent's phrase type:
  - `S` / `SINV` / `SQ`: subject role and predicate role, agreement,
    finiteness, question inversion;
  - `NP`: head noun, determiners, determiner agreement, determiner stacking,
    modifiers, possessives, quantifiers, postmodifiers, reduced relatives,
    noun form, pronoun case, compound nominals;
  - `VP`: verb head, auxiliaries and required complement forms, objects,
    particles, adverbials, predicate adjectives, clausal complements,
    coordination;
  - `PP`, `ADJP`, `ADVP`, `WHNP`, `WHADVP`, `WHPP`, `SBAR`, `FRAG`: head
    licensing, complements, modifiers, relative pronouns;
  - a small-clause path for `S` under `VP`;
  - anything unrecognized → `C-UNLISTED`, `unlisted`
    ("valid by default, but not covered by the matrix").
  Each branch returns `(status, constraint_id, explanation_text)`.
- `_detail` stores the record. It also normalizes explanations through
  `_strip_preface`, which removes the repeated
  `In the sentence '<sentence>', ` boilerplate from the generator strings and
  re-capitalizes the first letter. The sentence itself is still referenced
  through the quoted word/phrase inside the explanation.

A detail record has:

```json
{
  "id": "n12",
  "type": "NP",
  "pos": null,
  "surface": "the big cat",
  "span": [1, 4],
  "parent": "n3",
  "rule": "NP → DT + JJ + NN",
  "children_ids": ["n13", "n14", "n15"],
  "children": [{"id": "n13", "type": "DT", "surface": "the"}],
  "role": "clause subject",
  "constraint": "C-SUBJECT-ROLE",
  "status": "valid",
  "text": "The NP 'the big cat' is the subject …",
  "findings": []
}
```

Statuses are `valid`, `error`, `unlisted` (and findings may carry
`suggestion` or `unverified`).

#### 5.3 Root-level checks

`_root_level(root)` handles the node that has no parent:

- If the root type is in `SENTENCE_CLASSES` (`S`, `SINV`, `SQ`, `SBARQ`,
  `FRAG`, `ROOT`) and the first character of the surface is a lowercase
  letter → `C-CAPITALIZATION`, `error`.
- Otherwise the root gets `C-ROOT`, `valid`: it contains a subject daughter
  and a predicate daughter.
- If the root is not a sentence class → `C-TENSE-FINITE`, `error`: the input
  has no finite predicate VP and is a fragment.

The ruleset contains a parallel sentence-initial capitalization check
(rule 10.1, `C-SENTENCE-CAPITAL`) inside `_check_basic`; the matrix root check
covers the root node, the ruleset check covers the token-level rulebook
numbering.

#### 5.4 Finding merge

`_merge_findings` is where the rulebook and licensing layer meet the tree:

1. Run `licensing.collect_all(text, root)` when the licensing module is
   available. Otherwise fall back to `ruleset.collect(text, root)`.
   `collect_all` isolates every checker; a crash is recorded in
   `checker_errors` and degrades the verdict instead of deleting all findings.
2. Attach each finding to its `node_id` detail (falling back to the root
   detail). The finding id becomes `<node_id>:<rule_id>`.
3. For error findings, wrap the bare check text with structural context:

   ```
   The <node type> '<surface>'[ inside the <parent type> '<parent surface>'] is flagged: <finding text>
   ```

   The "inside the …" clause appears only when the node has a parent detail.
4. Attach the rule concept from `server/master.py::concept(rule_id)` when the
   content sheet is available.
5. Mark the node's own status `error` so the frontend paints it red even when
   the error came from a wordlist/context finding rather than the edge
   classifier.
6. Reconcile the detail's prose with its findings:
   - if the detail was already an error before merging (`_own_error`), keep
     its own explanation when no finding matches;
   - otherwise prefer a finding whose `rule_id` equals the detail's
     `rule_id`;
   - then a finding whose `constraint` equals the detail's `constraint`;
   - then the first error finding;
   - normalize its remediation through `_rem_from_text` when the finding did
     not supply a structured remediation.

This ordering is why a capitalization detail shows the capitalization text
rather than an unrelated agreement finding, and why "walked home." shows the
capitalization problem rather than "missing subject".

#### 5.5 Finalization and summary

For every detail, `evaluate` fills in:

- `rule_id` and `method` from `CONSTRAINT_RULE` (constraint id → `(rule id,
  T/L/C method)`);
- generic `evidence` when the checker did not supply one (tree, wordlist, or
  context shape);
- `findings` (always a list);
- `checks`: a deterministic checklist built by `_checks_for` from the node's
  own verdict plus its immediate children's verdicts;
- `remediation` for errors that do not already have one, via `_remediate`
  (constraint-specific repair functions followed by a generic fallback).

`_summarize` produces the verdict:

```text
violations         = error details + error findings (+ root detail if root error)
root_error         = the root detail is an error
verdict            = "ungrammatical" if violations
                   | "unverified"    if unverified findings or checker crashes
                   | "grammatical"   otherwise
valid              = len(violations) == 0       # legacy: "nothing fired"
```

It also reports `valid_edges`, `violated_edges`, `unrated_edges`,
`violations`, `suggested`, `suggestions`, `constraints_fired`,
`checker_errors`, `lexical_coverage`, `unverified`, and a human
`explanation`.

Important semantic detail: `summary.valid` means "no violation was found", not
"the sentence is grammatical". A sentence can be `valid: true` and
`verdict: "unverified"`. All UI code keys on `verdict` (and on node status),
not on `valid`.

The matrix uses only deterministic libraries: `inflect` for noun forms,
`lemminflect` when available for irregular verb forms, and explicit
feature functions for agreement, determiner number, auxiliary form,
finiteness, modifier order, and so on. There is no scoring model inside the
matrix. The same tree always yields the same details.

### Stage 6 — Positive-evidence licensing

`server/licensing.py` exists because the matrix is a blacklist: "no rule
fired" is not the same as "the word form is real". benepar is trained on
grammatical text and will happily parse `I am stupids` or `the men are
runned`.

`collect_all` replaces `ruleset.collect`: it runs the rulebook's wordlist,
basic, adjective/adverb, tree, "more", and context checkers plus the licensing
checks, each inside its own `try` block. The licensing module contributes
three counter-measures:

1. **Lexical licensing** (`check_lexicon`). Every open-class leaf
   (noun/verb/adjective/adverb tag) is checked against the lemminflect
   paradigm for the lemma and POS the parser assigned. Results:
   - `licensed`: the surface is an inflected form of a known lemma, or is in
     `HIGH_FREQ` (quantifiers, indefinite pronouns, irregular plurals, common
     adverbs, `tv`/`ok`);
   - `malformed`: a form outside the lemma's paradigm (`goed`, `runned`,
     `stupids`, `mans`) → rule-specific error (`C-LEXICON-MALFORMED`), with
     the accepted forms and a suggested replacement;
   - `tag_mismatch`: the surface is a form of the lemma but not the form the
     parser's tag requires. A `VBN` slot after `be`/`have` is a hard error
     (rule 1.6); other mismatches are `unverified`
     (`C-LEXICON-TAG-MISMATCH`);
   - `unknown`: not in the lexicon at all → `unverified`
     (`C-LEXICON-UNKNOWN`), not an automatic error, because names and new
     words are legitimate.
   - A second pass catches adjective-derived adverbs of the `happyly` type
     (`-y` + `-ly`) as rule 1.8 errors.
   - `skip_ids` prevents double-reporting leaves another checker already
     flagged.
2. **Relative-clause rules** (`check_relatives`). Implements the registered
   but previously missing rules 2.7 and 5.4:
   - `whose` directly followed by a verb has no possessed noun;
   - `which` after a human antecedent / `who` after a non-human antecedent;
   - subject-gap relative `the boys who plays` → verb must agree with the
     antecedent NP, with an inflection suggestion.
3. **Tri-state accounting.** `stats` counts `content`, `licensed`,
   `unverified`, `malformed`. Unknown or unverifiable words keep the
   sentence out of the `grammatical` verdict. A checker exception becomes a
   `checker_errors` entry, which also forces `unverified`.

The licensing layer is optional at import time: if lemminflect is missing,
`matrix.py` sets `licensing = None` and falls back to `ruleset.collect`,
which runs the same rulebook without the paradigm checks.

### Stage 7 — Hybrid detection

`server/detector.py` adds the acceptability channel:

- Model: `textattack/roberta-base-CoLA` by default, overridable with
  `SYNTUTOR_DETECTOR_MODEL`.
- Loaded once, CPU-only (`device=-1`), through a Hugging Face
  `text-classification` pipeline. Load failure is cached and degrades the
  system to rules-only; it never crashes a request.
- `classify(sentence)` returns `available`, `model`, `label`
  (`acceptable`/`unacceptable`), `acceptable`, `acceptable_prob`,
  `confidence`, and an `explanation` string.
- `classify_many(texts)` is the batch path used by the corrector; it returns
  one record per input, or a list of `None` when the detector is out.

`combine(summary, det)` is a pure merge:

| Matrix verdict | Detector | Combined verdict |
|---|---|---|
| `ungrammatical` | any | `ungrammatical`; detector note attached, `flagged = true` |
| `grammatical` | acceptable | `grammatical` |
| `grammatical` / `unverified` | unacceptable | `unverified`; note explains that the rules cannot account for the rejection |
| `unverified` | acceptable | `unverified` (the matrix could not positively verify it) |
| any | detector unavailable | matrix verdict unchanged |

The `unverified` branch is deliberate: the system refuses to label a sentence
ungrammatical without a rule-level reason. The detector's view is surfaced in
`summary.detector` and `summary.detector_note`, and in the payload's
`explainers.basic`.

### Stage 8 — Correction search

When and only when the verdict is `unverified`, the detector rejected the
sentence, and the detector is available, `api.py` attempts a text-space
repair with `server/corrector.py`:

1. **Span selection.** The sentence's alphabetic token spans come from the
   parse tokens (offsets relative to the target sentence). When no spans are
   supplied, the corrector's own scanner skips contractions and punctuation.
2. **MLM sweep.** For each candidate word (up to `SYNTUTOR_MLM_MAX_TOKENS`,
   default 40):
   - mask it with `[MASK]`;
   - ask `distilbert-base-uncased` (`SYNTUTOR_MLM_MODEL`) for the top
     `SYNTUTOR_MLM_TOP_K` (default 5) replacements;
   - recast the replacement to the original casing;
   - keep only candidates that share a lemma with the original
     (`corrector._shared_lemma` via lemminflect), so a flat meaning swap such
     as `He → I` cannot be promoted as a grammatical repair;
   - batch-classify the candidate sentences with `classify_many`;
   - the first candidate that flips to `acceptable` becomes the located
     repair: `{position, bad, good, cola_p, corrected_text, …}`.
3. **Promotion guard** (`api.py::_apply_correction`):
   - the original must be clearly rejected (`acceptable_prob < 0.45`);
   - the flipped candidate must be clearly accepted (`cola_p >= 0.6`);
   - the corrected sentence is re-analyzed from scratch;
   - the clean matrix must be `valid`, with no root error and no error
     details. This is the "clean AST projection": the good word's POS tag
     comes from a tree the matrix itself licensed;
   - both trees must have the same leaf count;
   - `corrector.morph_diff` must prove the two words are forms of one lemma
     and yield the used form label and required form label
     (`EXTENDED_TAG_LABEL`).
4. **Finding synthesis.** The repair becomes a normal-looking finding:
   - rule `11.4`, constraint `C-MLM-ANOMALY`, role "word form";
   - text: `The word '<bad>'[ inside the <parent type> '<parent>'] is used
     where the structure requires the <required> form. <dynamic template>`;
   - remediation: replace bad with good;
   - the summary is promoted to `ungrammatical`, `violated_edges` increments,
     and `C-MLM-ANOMALY` joins `constraints_fired`;
   - `explainers.perturbation` carries the full note (masked word,
     replacement, acceptability probability, projected tag).

If any guard fails, the sentence stays `unverified`. The corrector is
optional, just like the detector: no network, no weights, or no flip simply
means no promotion.

### Stage 9 — Payload assembly

`api.py::build_payload` returns one JSON object with six top-level keys.

```json
{
  "meta": {
    "deterministic": false,
    "k": 1,
    "parser": "benepar_en3",
    "spacy": "en_core_web_md",
    "backend": "spaCy + benepar (neural constituency) + rule matrix (XAI) + CoLA acceptability model (hybrid)",
    "sentence_count": 1,
    "target_sentence": 1
  },
  "parse": {
    "text": "The clever boy reads a book.",
    "sentence_count": 1,
    "sentences": [{"ordinal": 1, "start": 0, "end": 29, "text": "…"}],
    "tokens": [{"i": 0, "t": "The", "start": 0, "end": 3, "pos": "DET", "tag": "DT", "dep": "det", "head": "boy"}],
    "parse_string": "(S (NP (DT The) (JJ clever) (NN boy)) (VP (VBZ reads) (NP (DT a) (NN book))) (. .))"
  },
  "tree": { "id": "n0", "type": "S", "span": [0, 6], "surface": "…", "children": [] },
  "nodes": { "n0": {} },
  "node_details": { "n1": {} },
  "summary": {},
  "explainers": {
    "basic": "…",
    "contrastive": "…",
    "surprisal": null,
    "perturbation": null,
    "llm_note": null,
    "pipeline": {"stages": [], "verdict": "…", "constraints_fired": []},
    "concepts": [{"rule": "2.1", "concept": "…", "note": "…"}]
  }
}
```

`meta.deterministic` is true only when the detector did not run; the corrector
only runs when the detector is present, so this flag is a conservative proxy
for "rules-only response".

`explainers.pipeline` is the four-stage narration shared with the Lessons
copy and the Syntax Builder:

1. Tokenizer — token count and token list.
2. Part-of-speech tagger — `word/POS` pairs.
3. Constituency parser — the benepar parse string.
4. Rule matrix — validated / violated / unrated edge counts.

`explainers.concepts` maps every fired rule id to the concept text from
`web/content/tree_sheet.json` via `master.concept`.

`explainers.contrastive` describes the first repairable violation (or states
that no repair is needed / no violation exists). `explainers.basic` is a
plain-text report: input, parse string, token stream, edge counts, verdict,
hybrid detector line, correction line.

### Stage 10 — Browser rendering

When the payload arrives, `main.js`:

1. `applyStatuses(payload.tree, payload.node_details, payload.summary)` copies
   each node's detail status onto `node.edgeResult`. If the verdict is
   `ungrammatical` but no detail is an error (a finding attached to the root),
   the root is marked red.
2. Builds the session object (payload, sentences, sentence index) and stores
   the analyzed text.
3. Computes highlight spans from token offsets, merging sentence navigation
   spans when the user inspects another sentence.
4. Re-locks the input and applies the active sentence selection.
5. Calls `renderer.setTree(payload.tree)`.
6. Transitions to `VIEWING`.
7. If signed in, not a replay/navigation run, and the sentence has not already
   been recorded, inserts the analysis into Supabase `analysis_history`.

#### Tree layout and interaction

`web/js/renderer.js` implements a tidy tree layout:

- Leaves are measured and assigned equal-width slots; internal nodes are
  centered over the span of their leaf slots.
- Each depth is a row (`BOX_H + V_GAP` apart).
- The whole tree is fit into the canvas (scale clamped to 0.2–1.7).
- Mouse drag pans; wheel zooms around the cursor; hit-testing picks the
  deepest box under the pointer; arrow keys move through depth-first order;
  Enter/Space selects.
- Node colors come from `edgeResult.status`: ok / error / unlisted.
- Selection is local: `handleNodeSelect` reads
  `session.payload.node_details[id]` and renders it immediately. There is no
  second HTTP request for a node explanation.

#### Node inspector

`web/js/ui.js::renderNodeDetail` renders the right-hand explain pane:

- a status dot (ok / error / unlisted) and the phrase or tag name;
- the node surface;
- a role chip (`detail.role`);
- if the node is an error and has a remediation object: a
  "What's wrong / How to fix it / Alternative fix" card;
- otherwise: the explanation text.

This is the point where the symbolic matrix becomes learner-facing: every
phrase and word has a cached, deterministic explanation or repair card.

#### Workspace modes

`main.js` keeps three workspace owners (`workspaceView`): `tutor`, `lessons`,
`builder`, plus overlays (History, sub-panels, lessons overlay). Every mode
switch starts with `teardownWorkspace()`, which closes the quiz view, clears
the active lesson, closes the builder, clears diagnostics, restores the plain
textarea, and hides builder-only controls. The rail paints exactly one active
destination and hands the highlight to an overlay while it is open.

The frontend state machine is `IDLE → PROCESSING → VIEWING ⇄ EXPLORING`
(`END` is defined but not currently reached), with `PROCESSING` guarding
against double submits. The status strip logs
the same stages the payload describes (input, POST, spaCy, benepar, matrix,
explanations, render, history).

### Stage 11 — History and persistence

History is account-only:

- Guests never write; their history list is empty.
- Signed-in analyses insert `{user_id, sentence, is_valid,
  constraints_fired}` into `analysis_history`.
- The drawer loads the 50 most recent rows, filters by all/valid/error in
  memory, supports deleting a row, and replays an entry by tearing down the
  workspace, restoring the tutor, filling the textarea, and re-running the
  pipeline with `isReplay: true` (which skips a duplicate history insert).
- The identity listener clears caches on account switch.

---

## 3. The rule matrix in detail

### 3.1 Rulebook

`server/ruleset.py::RULEBOOK` contains 111 numbered rules in 11 sections:
word forms, agreement, articles/determiners, nouns, pronouns, verbs,
adjectives/adverbs, prepositions, sentence structure, punctuation, and
meaning/usage. Each entry is:

```python
'2.1': ('Subject-verb, simple', 'The boy go', METHOD_T)
```

`METHOD_T` / `METHOD_L` / `METHOD_C` describe the evidence type in the XAI
table: tree structure, word list/morphology, or context. `method_of(rule_id)`
resolves the method when a finding does not carry one.

Rule ids are the stable key across the system: findings, the content sheet,
the tree quiz, and the explanation sheet all index by the same `"2.1"`
string.

### 3.2 Constraint ids

Every node detail carries a `C-*` constraint id. `CONSTRAINT_RULE` maps each
constraint to `(rule_id, method)`, which is how an internal matrix check gets
a human rulebook number. Examples:

| Constraint | Rule |
|---|---|
| `C-SUBJECT-AGREEMENT` | 2.1 |
| `C-DETERMINER-AGREEMENT` | 2.10 |
| `C-DET-STACK` | 3.5 |
| `C-AUX-FORM` | 6.1 |
| `C-TENSE-FINITE` | 6.2 |
| `C-MOD-POS` | 7.7 |
| `C-CAPITALIZATION` | 10.1 |
| `C-RELATIVE-AGREE` | 2.7 |
| `C-LEXICON-MALFORMED` | 1.1 noun, 1.4–1.6 verb by form, 1.7 adjective, 1.8 other |
| `C-MLM-ANOMALY` | 11.4 |

The matrix dispatch map currently holds 133 unique constraint ids; the
generated tree sheet counts 169 distinct constraints once licensing and
ruleset-only constraints are included. Not every rulebook entry has a
dedicated tree branch; unimplemented semantic rules simply do not fire, and
unrecognized edges are marked `C-UNLISTED` rather than silently passing as
valid.

### 3.3 Findings

A finding (from `ruleset._finding`, reused by licensing) has:

```json
{
  "rule_id": "2.1",
  "method": "T",
  "status": "error",
  "constraint": "C-SUBJECT-AGREEMENT",
  "role": "subject-verb agreement link",
  "node_id": "n14",
  "text": "…",
  "evidence": {"used": "tree", "subtree": "n14", "rule": "…", "conflict": [{"node": "n14"}]},
  "remediation": {
    "violation": "…",
    "suggested_fix": "…",
    "alternative_fix": null,
    "targeted_outcome": "…"
  }
}
```

Evidence has three shapes:

- tree: `{used: 'tree', subtree, rule, conflict}`;
- word list: `{used: 'wordlist', lookup, accepted, source}`;
- context: `{used: 'context', condition, options, confidence}`.

This is the explicit XAI contract: every explanation can cite either the
subtree, the lexicon lookup, or the contextual condition that produced it.

### 3.4 Remediation

Two paths produce the "How to fix it" card:

- **Explicit** — the checker supplies a `remediation` dict with a violation,
  suggested fix, optional alternative fix, and targeted outcome.
- **Derived** — `_rem_from_text` splits the explanation text at the last
  directive clause (`Change …`, `Use …`, `Replace …`, `Add …`, etc.),
  ignoring non-directive semicolons inside quoted replacements. If no
  directive exists, it falls back to a final-sentence split, a parenthetical
  `(use …)`, or a generic "change the flagged word" suggestion.

Constraint-specific `_rem_*` methods handle agreement, determiners,
auxiliaries, determiners stacking, modifier position, pronoun case,
article choice, capitalization, quantifiers, comparatives, finite verbs, and
fragments before the generic fallback.

### 3.5 Explanation style

Explanations are generated in source with the sentence/context scaffold, then
centralized cleanup runs:

- `_pretty` tidies parse surfaces for quoting (spaces before punctuation,
  clitics, `n't`);
- `_strip_preface` removes the leading `In the sentence '<sentence>', `;
- `P`/`_p` and labels render node surfaces and phrase names;
- `_sc()` exposes the current sentence to the generator.

The result is a unique, structure-specific sentence such as:

> The VBD 'goed' inside the VP 'goed home' is flagged: 'goed' is not the
> correct past-tense form; use 'went' instead.

rather than a repeated template beginning with the same boilerplate. This
was an explicit product requirement: only the unique explanation text should
be shown; the sentence is still referenced through the quoted material.

---

## 4. Lessons, quiz, and Syntax Builder

### 4.1 Lessons as a textbook

`web/js/tree-quiz.js` defines `LESSONS`, 20 phrase/clause constructions in
pedagogical order, grouped into Phrases, Clauses, Wh-phrases, and Special
phrases. Each lesson has:

- `type` — the official parser label (`NP`, `VP`, `PP`, `S`, `SBAR`, …);
- `title`, `group`;
- `rule` — a one-line construction summary used as the canvas hint;
- `detail` — the in-depth explanation of role, head, modifiers, recognition;
- `steps` — a numbered guide for building the example tree;
- `examples` — sentences used for practice.

A lesson page sequence is Concept → Steps & Practice → end-of-lesson quiz.
The lesson-picker overlay shows per-lesson progress derived from completed
examples.

### 4.2 Gold trees come from the server

Every practice or quiz sentence is parsed live:

```js
const res = await fetch('/api/parse', { method: 'POST', body: JSON.stringify({ text: sentence }) });
```

`apiTree(payload.tree)` reduces the server node graph to
`{type, children}` / `{type, leaf, surface}`. `leavesWithTags` flattens it to
the word/tag row the builder seeds. Results are cached per sentence in
`state.cache`, so a repeated example does not re-query the model. This is the
"gold tree can never drift" rule: the exercise is graded against SynTutor's
own parse, not a hand-maintained copy.

### 4.3 The Syntax Builder model

`web/js/syntax-builder.js` is DOM-free and independently testable:

- `createModel()` → `{nodes: {}, counter: 0}`.
- `addWord`, `addPhrase`, `moveNode`, `setType`, `removeNode`.
- Phrase palette: 24 phrase labels (S, NP, VP, PP, ADJP, ADVP, SBAR, SBARQ,
  SINV, SQ, FRAG, NML, WHNP, WHADVP, WHADJP, WHPP, QP, NX, CONJP, UCP, LST, X,
  INTJ, PRT).
- POS palette: 48 lexical tags.
- `connect(parent, child)` attaches a child to a parent after
  `canConnect` rejects self-links and cycles. The builder is intentionally
  permissive: any node can be a parent or child, even if the combination is
  not a valid constituency, so the learner can always build and then be
  corrected.
- A phrase exposes a bottom-center connector dot; a connected node exposes a
  top-center endpoint used to re-route or delete the edge.
- `toTree(model)` converts the graph to a nested tree; `leavesOf`,
  `phraseSpans`, and `compareTrees` support grading.

### 4.4 Grading: structural, not textual

`compareTrees(userTree, goldTree)` compares phrase spans, not strings:

- every phrase node is reduced to `${type}[${start}-${end}]`, where
  `start`/`end` are leaf indices;
- a span present in the user tree but not the gold tree is `extra`;
- a gold span absent from the user tree is `missing`;
- `correct` iff both lists are empty.

This means moving a box without changing its span still counts as correct
(the layout is presentation), while attaching the right label at the wrong
span is wrong. Leaf text is compared separately so a wrong sentence can be
reported independently.

The builder supports four challenge kinds:

| Kind | Task |
|---|---|
| `tokens` | Type the sentence; match SynTutor's tokenization |
| `tags` | Give each word the POS tag SynTutor assigns |
| `phrases` | Words/tags given; add and connect phrase boxes |
| `full` | Type the words and build the complete tree |

The Lessons and quiz currently use `full`.

### 4.5 Builder validation and XAI

"Build tree" (`checkTree` / `validateBuiltTree` in
`syntax-builder-ui.js`) does three layers:

1. **Structure (client-side).** More than one root, unreachable orphans,
   empty phrase boxes, and unrecognized words become node errors.
2. **Lexical (server).** Word boxes are sent to `POST /api/words`, which uses
   `spellcheck.known_word`, spaCy tagging, and `best_correction` to decide
   whether a word is valid and to suggest a spelling fix.
3. **Grammar (server).** The assembled sentence is sent to `/api/parse`;
   an `ungrammatical` verdict becomes a sentence-level diagnostic in the
   explain pane, while a clean verdict clears it.

Errors are shaped like tutor `node_details`, so selecting a red box in the
builder shows the same kind of `renderNodeDetail` card as the tutor. When a
node is clean, the builder reads its POS/phrase description from
`web/content/tree_sheet.json` (fetched once and cached in `INFO`), so the
builder and the tutor describe the same tag with the same text.

The builder can also snap the constructed tree into the same fitted layout as
the read-only renderer, so the finished exercise looks like the generated
tree.

### 4.6 Gamification

`web/js/level.js` defines the XP curve:

- 5 XP per correct answer + 5 bonus for a flawless run.
- Level spans grow geometrically: `50 * 1.6^level` (50, 80, 128, 205, …);
  `levelFromXp` decomposes total XP into level, progress into the current
  span, and the next threshold.

`main.js` exposes a `progress` controller with `load`, `award`, `leaderboard`,
`getQuizProgress`, and `trackCompletion`. The implemented path today is
completion tracking:

- finishing a lesson calls `trackCompletion({ruleId: lesson.type, perfect:
  true})`, which upserts a row in Supabase `quiz_progress`
  (`completed_count`, `perfect_count`, `last_completed_at`);
- `computeUnlocked` derives the achievement set from those rows
  deterministically (First Steps, Flawless Run, per-stage scholars, Tree
  Grandmaster);
- the `award` helper exists and writes `player_stats` XP/level, but the
  current lesson/quiz path does not call it;
- guests see the UI but nothing is persisted (`progressAvailable()` gates on
  `!isGuest && clerk.user.id && supabase`).

`web/js/achievements.js` builds the catalog from the four pipeline stages and
extra milestones. Note that `computeUnlocked` maps `quiz_progress.rule_id`
through `stageInfo`, which expects a numeric stage id (1–4), while lesson
completions currently store the lesson's phrase type (`NP`, `VP`, …). The
catalog and derivation are deterministic, but the stage-specific achievements
will not unlock until that key mapping is aligned.

The Leaderboard and Achievements panels are currently placeholders
("Coming soon") in `tree-quiz.js`; the data helpers exist in `main.js` but the
dedicated views are not implemented.

---

## 5. Content pipeline and generated sheets

### 5.1 `web/content/master.json`

The quiz corpus: 11 sections (one per rulebook section) and 111 rule
questions. Each question has a `bad` sentence and its `good` correction.
`scripts/master_sheet.py` runs the real model over every question and
classifies the result as detected / miss / false positive / accepted. This is
the detection-regression sheet used to review model behavior, not a unit test
that must be perfectly green.

### 5.2 `web/content/tree_sheet.json`

`scripts/tree_sheet.py` generates the learning sheet directly from the live
code:

- Stage 1 Tokenizer;
- Stage 2 POS tagger — 48 lexical tags;
- Stage 3 Constituency parser — 24 phrase labels;
- Stage 4 Rule matrix — 111 rules with concept text, examples, methods, and
  constraint ids.

Outputs:

- `docs/tree_sheet.md` (human-readable);
- `docs/tree_sheet.json` (full data);
- `web/content/tree_sheet.json` (what the browser and `server/master.py`
  read).

The generator also merges `web/content/exhaustive_rules.json`:

- for each rule id, the exhaustive explanation becomes the stage-4 `concept`;
- the same map is stored under `sheet['exhaustive_explanations']`.

This merge is essential: `npm run build` runs `tree_sheet.py` first, and
without the merge a build would wipe the user-edited exhaustive concepts.
The patch is guarded with `os.path.exists` and `except (OSError, ValueError)`
so a missing or malformed file degrades to the built-in concepts instead of
breaking the build.

Current sheet metadata: 4 stages, 48 POS tags, 24 phrase nodes, 111 rules,
169 constraints, 242 total items, plus 210 exhaustive explanations.

### 5.3 `web/content/exhaustive_rules.json`

A 210-entry rule id → `{name, explanation, template, category}` map. It is the
surviving source of truth for the exhaustive explanations that were once in a
deleted Markdown document. `tree_sheet.py` is the only writer that folds it
into the published sheet; do not hand-edit the generated JSON.

### 5.4 Explanation sheet

`scripts/explanation_sheet.py` audits the *valid* side of the XAI output:

- run the real model over the quiz sentences;
- collect every `valid` node explanation;
- normalize quoted material to `{X}` and group by constraint;
- report template counts and flag explanations that quote no part of the
  sentence.

Final audit after the prefix cleanup: **2,893 sentences, 44 constraints,
40,124 explanations, 377 unique templates, 0 without a quoted reference.**
The earlier 608-template count reflected the repeated
`In the sentence '…', ` scaffolding; removing it collapsed the templates to
377 without losing the sentence reference, because the quoted word/phrase
inside each explanation remains.

### 5.5 Build and deploy

`npm run build` = `python3 scripts/tree_sheet.py && node scripts/build.js`.
`build.js` deletes `dist/`, copies `web/index.html`, `web/login.html`,
`web/css`, `web/js`, `web/content` into `dist/`, and leaves server code out.
Vercel serves `dist/`; the frontend calls the API origin configured in
`js/config.js` (`API_BASE`). The local Flask server serves the same `web/`
tree, so development and production share one frontend.

Useful commands:

```bash
python3 server/webapp.py        # Flask backend + static frontend
npm run serve                   # same
npm run serve:legacy            # stdlib server
npm run build                   # regenerate sheet + dist/
npm run test:quiz               # quiz content audit
npm run audit                   # rule regression audit
npm run sheet                   # detection master sheet
npm run tree:sheet              # regenerate tree sheet only
npm run explanation-sheet       # regenerate explanation audit
```

---

## 6. Authentication and data model

Frontend auth lives in `web/js/auth.js`:

- Clerk is loaded from its Frontend API domain derived from the publishable
  key; `loadClerk()` is a singleton promise.
- `createSupabaseClient()` creates the Supabase JS client with
  `persistSession: false`, `autoRefreshToken: false`,
  `detectSessionInUrl: false`, and an `accessToken` callback that returns
  `clerk.session.getToken()`.
- The same form logic is used by `login.html` (standalone, redirects to
  `index.html`) and the in-app auth modal (reloads on success).
- Keys live in `web/js/config.js`; the repository ships
  `config.example.js` as the template and warns when config is absent.

Tables used by the client:

| Table | Purpose | Client operations |
|---|---|---|
| `analysis_history` | Saved analyses | insert, select recent 50, delete |
| `player_stats` | XP and level | upsert, select own row, leaderboard read |
| `quiz_progress` | Per-rule completion/perfect counts | select, upsert, completion tracking |

Reads work anonymously for the public leaderboard. Signed-in writes depend on
Clerk being registered as a Supabase third-party auth provider; when that
configuration is missing, writes fail with RLS `42501` (a known deployment
issue, not a frontend logic bug).

---

## 7. Failure modes and degradation

| Failure | Behavior |
|---|---|
| spaCy/benepar missing or unloadable | `model_status().ready = false`; `/api/health` returns 503; `/api/parse` returns 503 with install hint |
| Input has no sentences | `ParseFailure('no sentences detected')` → 422 |
| Parse tree leaves ≠ sentence tokens | `ParseFailure('span alignment mismatch: …')` → 422 |
| Detector unavailable | rules-only verdict; `meta.deterministic = true`; basic report notes the offline channel |
| Corrector unavailable | no promotion; sentence stays `unverified` |
| One licensing/ruleset checker crashes | `checker_errors` records it; other checkers still run; verdict becomes `unverified` |
| Lexicon cannot load at all | spelling layer accepts tokens rather than rejecting valid words |
| Unknown word not in lexicon | `unverified`, not `ungrammatical` (names/new words are legitimate) |
| Matrix clean, detector rejects | `unverified` with a detector note; never a fabricated rule error |
| Frontend backend unreachable | canvas diagnostic "Backend unreachable" with the run command |
| Supabase write forbidden | warning logged; analysis still renders; history not saved |

---

## 8. Determinism, auditing, and known limits

### Determinism

- Tree construction is deterministic for a given sentence/index (benepar
  top-ranked parse).
- The matrix, licensing, remediation, and summary are pure functions of the
  tree and sentence; no random sampling and no classifier scores.
- The detector is a model and can vary in edge cases; it only changes the
  verdict when the matrix is clean (to `unverified`), never the explanation
  of a matrix violation.
- The corrector is only attempted for `unverified` sentences and is gated by
  both classifier margins and a clean-matrix re-analysis.

### Audits in the repository

- `scripts/master_sheet.py` — detection review over 111 quiz questions.
- `scripts/explanation_sheet.py` — valid-explanation review (quoted-reference
  check, template deduplication).
- `scripts/audit_rules.py` — rule-regression checks over the gold corpus.
- `scripts/test_tree_quiz.js` — asserts the quiz content/lesson inventory is
  consistent (`npm run test:quiz`).
- `py_compile` on the server modules and live `/api/health` + smoke sentences
  are the quick backend checks.

### Known limits

- benepar can produce a linguistically wrong tree. The matrix explains the
  tree it is given, so a parse error can produce a misleading explanation.
- Edges not covered by the matrix are `C-UNLISTED` and valid by default; the
  sheet tracks coverage but coverage is not total.
- The semantic rulebook section (meaning/usage) is only partially backed by
  deterministic checks; several rules are registered but do not fire.
- The detector can return `unverified` for colloquial but acceptable input
  (e.g. fragment-like answers); this is intentional conservatism.
- The master sheet still contains known false positives (roughly 40 at the
  time of writing) and a gold regression on `He runs fast` (missing terminal
  punctuation interacts with rules 10.8/10.3).
- Leaderboard and Achievements views are placeholders; the backing helpers
  exist but the panels are not built. `award` is not called by the current
  quiz path, and stage achievements expect numeric stage ids while
  `quiz_progress` stores lesson types, so that mapping needs alignment.
- Supabase writes require the Clerk third-party auth configuration described
  above.

---

## 9. How to extend the system

### Add a grammar rule

1. Add the rule id/name/example/method to `RULEBOOK` in
   `server/ruleset.py`.
2. Map its constraint to the rule id in `CONSTRAINT_RULE` in
   `server/matrix.py` (or emit a finding with the rule id directly from a
   checker).
3. Implement the check:
   - tree edge: add a branch in `_classify` / the relevant `_s_*`, `_np_*`,
     `_vp_*` method and return `(status, constraint, text)`;
   - word list: add to the appropriate `_check_*` function in
     `ruleset.py`/`licensing.py`;
   - context: use `_context_evidence`.
4. Add remediation (`_rem_*` or an explicit dict) if the default split is not
   good enough.
5. Add the concept text to `web/content/exhaustive_rules.json` and run
   `npm run tree:sheet` (or `npm run build`).
6. Add a quiz question to `web/content/master.json` if the rule should be
   exercised by the quiz/audit.
7. Run `npm run test:quiz`, `npm run explanation-sheet`, and the smoke
   sentences.

### Add a lesson or example

Edit `LESSONS` in `web/js/tree-quiz.js`: `type`, `title`, `group`, `rule`,
`detail`, numbered `steps`, and `examples`. Gold trees are fetched live, so no
tree data needs to be stored. Keep the lesson's `type` aligned with a phrase
label benepar can emit.

### Change an explanation

Add or edit the generator strings in `server/matrix.py` or the checker in
`ruleset.py`/`licensing.py`. Do not add the `In the sentence …` prefix to new
strings; `_strip_preface` removes it centrally, but new text should start
with the unique structural statement. Run `py_compile` and regenerate the
explanation sheet to see the template effect.

---

## Appendix A — Key data shapes

### Node

```json
{
  "id": "n4",
  "type": "NP",
  "span": [1, 4],
  "surface": "the big cat",
  "children": [
    {"id": "n5", "type": "DT", "pos": "DT", "span": [1, 2], "surface": "the", "punct": false}
  ]
}
```

Leaves also carry `pos`, and after parsing they carry `ftag` / `fpos`.

### Detail

See §2 Stage 5.2. A detail is keyed by node id in `payload.node_details`.
`status` is one of `valid`, `error`, `unlisted`.

### Finding

See §3.3. Findings live in `detail.findings`; error findings also promote the
containing node to `status: "error"`.

### Summary

```json
{
  "verdict": "ungrammatical",
  "valid": false,
  "valid_edges": 7,
  "violated_edges": 1,
  "unrated_edges": 0,
  "violations": ["n12"],
  "constraints_fired": ["C-SUBJECT-AGREEMENT"],
  "root_error": false,
  "explanation": "The VBZ 'goes' is flagged: …",
  "lexical_coverage": 1.0,
  "detector": {"label": "unacceptable", "acceptable": false, "acceptable_prob": 0.02},
  "detector_note": "Acceptability model …"
}
```

Key rule: the UI reads `verdict` and per-node `status`, not `valid`.

### Remediation

```json
{
  "violation": "The subject 'The boys' is plural but the verb 'goes' is singular.",
  "suggested_fix": "Change 'goes' to 'go'.",
  "alternative_fix": null,
  "targeted_outcome": "verb agrees with the subject"
}
```

---

## Appendix B — Glossary

| Term | Meaning |
|---|---|
| Constituency tree | Nested phrase structure from benepar (`S`, `NP`, `VP`, …) |
| Edge | A parent → child relation in the tree; the matrix validates edges |
| Detail | SynTutor's per-node record: role, constraint, status, text, findings |
| Constraint (`C-*`) | Stable id for a check; maps to a rulebook id |
| Rule id (`2.1`) | Numbered grammar rule shared by matrix, sheet, and quiz |
| Gold tree | The live `/api/parse` output used to grade a builder exercise |
| Licensing | Positive-evidence check that a word form is real for its POS |
| Unverified | The system cannot prove the sentence grammatical or explain why not |
| Unlisted | An edge outside the matrix's coverage, valid by default |
| Flawless run | A quiz with no wrong or skipped answers (XP bonus) |
