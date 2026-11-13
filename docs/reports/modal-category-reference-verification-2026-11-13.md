# Scope of the legacy modal category gate

The gate reduces false positives from spelling-only rules. It does not establish
auxiliary function independently of the parser, and does not authorize a
book-verified verdict. Existing legacy diagnostic authority remains unchanged.

## References actually consulted

These citations refer to the two supplied chapter PDFs; printed page numbers
are distinct from one-based PDF page positions. The supplied extracts do not
establish the Burton–Roberts edition. Short quotations below were checked in
extracted text, not inferred from repository rule citations.

- Burton–Roberts, Chapter 4, **A first look at verbs**, printed p. 68 (PDF p. 63):
  “words can belong to more than one category”. The examples contrast verbal,
  nominal and adjectival uses of *interest*. Inflection and syntactic context,
  rather than spelling alone, establish the category in use.
- Burton–Roberts, Chapter 6, Part I, **The contrast between lexical and auxiliary
  verbs**, printed pp. 114–115 (PDF pp. 109–110): inversion and negation distinguish
  auxiliaries; lexical *need* can take an NP object or *to*-infinitive, whereas
  auxiliary *need* behaves differently. These are constructional diagnostics.
- Burton–Roberts, Chapter 6, **Modal auxiliaries (MOD)**, printed pp. 115–116
  (PDF pp. 110–111): modals are finite, do not show subject agreement, and
  precede the stem form of the following verb. The book derives the exclusion
  of consecutive modals from these restrictions and represents modals as MOD.
- Huddleston and Pullum, *The Cambridge Grammar of the English Language*,
  Chapter 3 §1.5, printed pp. 83–84 (PDF pp. 82–83): the plain form is used in
  imperative, subjunctive and infinitival constructions; infinitival *to* is a
  separate syntactic word. Cambridge's *plain form* is not a Penn POS tag.
- Cambridge, Chapter 3 §2.1, printed pp. 92–93 (PDF pp. 91–92): negation,
  inversion, code and emphasis distinguish auxiliary behavior from lexical
  behavior (the NICE constructions).
- Cambridge, Chapter 3 §2.3, printed p. 106 (PDF p. 105), table [44]: a modal
  determines the **plain form** of the next verb, which may itself be lexical
  or auxiliary.
- Cambridge, Chapter 3 §2.4(a–c), printed pp. 106–107 (PDF pp. 105–106): central
  modals lack secondary forms and take bare infinitival complements. Thus a
  second genuine central modal cannot supply the required plain form.
  Footnote 18 on p. 107 explicitly notes restricted combinations in some
  nonstandard dialects. This is not a universal prohibition across dialects.
- Cambridge, Chapter 3 §2.5.1, printed p. 108 (PDF p. 107): modal *can* and
  *will* display these properties. This describes their auxiliary uses, not
  every homograph bearing those spellings.

## Engineering interpretation

`_is_central_modal` requires the existing central-modal spelling inventory plus
Penn MD evidence. The four uses gate basic modal checks, the second modal in a
stack, modal-before-*to*, and modal-as-finite-after-*to*. This is an intentionally
conservative prerequisite for these legacy diagnoses. It is not a new
classifier. Missing/nonmodal tags cause abstention by these predicates; they do
not prove grammaticality. A true modal mistagged VB can therefore be missed.
The references justify category sensitivity, not MD's reliability.

Benepar's Penn MD, Burton–Roberts's MOD, and Cambridge's auxiliary/lexical
classification are different representations. No tree-convention change or
Cambridge production-rule activation is part of this fix.

## Remaining parser limitations

In the configured parser, *They may can peaches*, *They will can peaches*, and
*They could can peaches* label lexical *can* MD and yield a false modal-stack
finding. *They may will the estate to charity* shows the same issue for lexical
*will*. These lexical readings are engineer linguistic judgments applying the
source principles, not examples claimed to occur in the books.

*They can fish* has both an ability-to-fish reading and a preserve-fish reading;
the parser selects the former. That selection alone does not exclude the latter.
*They may can fish* is similarly unsafe to reject categorically. No special-case
repair or speculative semantic disambiguation is introduced. Existing false
stacking findings remain a known legacy limitation rather than a claim that MD
settles grammatical function.

Regression cases are engineer-authored controls, not independently held-out
linguistic evaluation. Synthetic mistags test the gate's abstention policy, not
the real parser's accuracy. General references do not independently validate
each generated tree or correction.
