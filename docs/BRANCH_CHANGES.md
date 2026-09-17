# Branch Change Description

This branch improves SynTutor's deterministic grammar validation and
correction pipeline, with particular focus on noun morphology, irregular
plurals, and agreement remediation.

## Scope of the changes

The original matrix relied heavily on parser POS tags and a small set of
hardcoded inflection rules. That allowed malformed forms such as `foots`,
`childs`, `sheeps`, and `mens` to pass as valid when the parser labeled them as
plural or singular nouns. It also generated invalid verb suggestions such as
`ares` when correcting `are` to agree with a singular subject.

The branch adds a lexical morphology layer while preserving the existing
deterministic tree-based rule matrix:

```text
spaCy + benepar parse
        |
        v
tree edge and POS-based grammar rules
        |
        +--> inflect noun-form validation
        |
        +--> deterministic remediation suggestions
```

The system now distinguishes grammatical number from lexical form validity.
POS tags still determine whether a noun is singular or plural for agreement,
while the morphology layer checks whether the observed word is an accepted
English inflection.

## Directory and file changes

### `server/matrix.py`

This is the primary implementation change.

- Added the required `inflect` dependency.
- Added `_noun_form_issue()` to validate noun forms against accepted
  singular/plural relations.
- Added the `C-NOUN-FORM` constraint and user-facing role label.
- Added noun-form remediation with a focused explanation and replacement.
- Supports productive and classical forms without a pair for every noun:
  - `cactus` → `cacti`
  - `fungus` → `fungi`
  - `radius` → `radii`
  - `analysis` → `analyses`
  - `index` → `indices`
  - `matrix` → `matrices`
- Detects malformed forms such as:
  - `foots` → `feet`
  - `childs` → `children`
  - `sheeps` → `sheep`
  - `analysises` → `analyses`
  - `mens` → `men`
  - `womens` → `women`
- Preserves valid alternatives and invariant forms:
  - `cacti` / `cactuses`
  - `people` / `persons`
  - `indexes` / `indices`
  - `sheep`, `fish`, and `deer`
- Adds an irregular-plural guard so a generic inflector cannot accept
  suffixes added to complete irregular plurals, such as `men` → `mens`.
- Extends noun-form validation to parser-tagged singular nouns when the parser
  incorrectly tags a malformed irregular plural as singular. This catches the
  exact input `The mens is good.`.
- Normalizes all finite forms of `be`, `have`, and `do` before generating
  agreement corrections:
  - `are` → `is`
  - `is` → `are`
  - never `are` → `ares`

### `requirements.txt`

Added a backend dependency manifest:

```text
spacy
benepar
transformers<4.47
inflect>=7.5,<8
```

The `transformers` upper bound remains necessary for benepar compatibility.
The `inflect` version range provides deterministic noun morphology while
allowing compatible patch releases.

### `docs/RULES.md`

Documented the new morphology layer and `C-NOUN-FORM` rule, including:

- How parser number and lexical morphology work together.
- Productive suffix examples.
- Accepted alternatives such as `cacti`/`cactuses`.
- Invalid examples such as `mens`, `foots`, and `analysises`.
- The irregular-plural guard.
- Auxiliary normalization that prevents invalid suggestions such as `ares`.
- The limitation that unknown nonce words cannot be proven invalid solely
  because they are absent from a dictionary.

### `docs/README.md`

Updated setup instructions to install from `requirements.txt` and added the
new `inflect` behavior to the system overview and constraint table.

### `docs/ARCHITECTURE.md`

Updated the implementation reference to describe:

- `inflect` as the lexical/productive morphology component.
- `_noun_form_issue()` and its role in `C-NOUN-FORM`.
- The relationship between parser POS tags, morphology validation, and
  remediation.

### `FEATURES.md`

Updated the dependency-manifest status to reflect the new
`requirements.txt` file and its noun-validation dependency.

## Behavior examples

| Input | Expected result |
|---|---|
| `These foots hurt.` | Error: use `feet` |
| `The childs play.` | Error: use `children` |
| `Those sheeps graze.` | Error: use `sheep` |
| `The mens is good.` | Error: use `men`; also exposes subject/verb agreement |
| `The men are good.` | Valid |
| `These cacti grow.` | Valid |
| `These cactuses grow.` | Valid |
| `These persons arrived.` | Valid |
| `The good man are kind.` | Error: change `are` to `is` |
| `The good men is kind.` | Error: change `is` to `are` |

## Validation performed

The implementation was checked at several levels:

1. Python compilation of `server/matrix.py`.
2. Direct morphology checks for regular, irregular, classical, invariant,
   malformed, and alternative plural forms.
3. Synthetic matrix-node evaluations verifying status, constraint ID, and
   remediation output.
4. End-to-end spaCy/benepar simulations for multiple valid and invalid
   sentences.
5. The existing full rule audit:
   - 104 gold sentences.
   - 929 evaluated edges.
   - 0 regressions.
   - 0 unrated edge types.
6. Formatting validation with `git diff --check`.

## Known boundary

`inflect` is a morphology resource, not a complete spell checker. It can
validate known English vocabulary and productive forms, but it cannot prove
that every unknown word is wrong. Proper names, technical terms, brand names,
loanwords, and newly coined words should remain subject to parser and syntax
rules unless a broader dictionary layer is explicitly added.
