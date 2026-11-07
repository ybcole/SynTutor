# Cambridge source review — 8 November 2026

## What is now established

The twenty newly supplied files cover Cambridge Chapters 1–20 in 1,762 PDF pages.
Their chapter headings and printed-page sequences match the 2002 original
edition of *The Cambridge Grammar of the English Language*, by Rodney Huddleston
and Geoffrey K. Pullum, Cambridge University Press, ISBN 9780521431460.

Bibliographic basis: the publisher's own [frontmatter](https://assets.cambridge.org/97805214/31460/frontmatter/9780521431460_frontmatter.pdf)
identifies the title, authors, 2002 first publication and ISBN, and gives the
chapter starts matching these files. The publisher's [book record](https://www.cambridge.org/core/books/the-cambridge-grammar-of-the-english-language/A78402ABF5176AD283494180BCA2046F)
also identifies the 2002 print publication separately from the later digital
publication. The exact printing of the user's split copy remains unknown; it is
not inferred to be the publisher preview's 2015 printing.

`Chapter-1-Preface.pdf` actually begins with Chapter 1, **Preliminaries**, printed
page 1. It does not contain the book's separately paginated Preface or its title/
copyright leaves. It is indexed by its observed content without renaming the
user's original file.

The source manifest records each original filename, SHA-256, page count,
printed-page start, page-label anchors, and textless-page exceptions. Every
non-textless page had its expected number in the first/last three extracted
lines; that mechanical check is not certification of every diagram or textual
claim. Ten pages had no extractable text. Printed pp. 70 and 524 are absent from
the supplied split files; their contents were not assumed to be blank.

A mechanical coverage pass also checked all 308 printed-page references in the
196 merged rules. Every reference falls inside a supplied chapter file and none
points to a textless page. This checks citation availability, not whether each
rule accurately interprets its cited text. The receipt is
`sources/cambridge/reviews/2026-11-08-citation-coverage.json`.

No PDF, page image or extracted chapter prose is committed to this public
repository. The manifest contains only bibliographic/file/page metadata.

## Independent review completed

**Record:** `CLS-001` in `grammar/rules/clauses.json`.

**Evidence:** Chapter 2, §1; printed pp. 44–45 = supplied split-PDF pp. 2–3.
Those page images and their text were inspected. The old `pdf_pages` references
64–65 refer to the earlier full-book context and are preserved, not silently
reinterpreted as split-file page numbers.

The existing paraphrase accurately distinguishes text-level sentence units from
central subject–predicate clauses and allows clauses to be embedded. Its
original AI-authored standalone/embedded/coordination contrasts fit that scope.
The new template reuses the earlier extraction's statement and condition; it
adds only observed node-label/surface information and the project authority
boundary. This is an independent AI second pass of an earlier extraction, not a
new claim of human review.

The reviewed template `CGEL-CLS001-TEACHING-V1` cites two page-level Cambridge
source records in `grammar/explanation_templates.json`. It is a **classification
teaching note**, never an executable error rule or a correctness verdict.

Its crosswalk resolution is narrowly scoped: preserve Cambridge terminology as
a separate explanatory note and keep the canonical B-R node labels unchanged.
This does not assert that a B-R `S` and a Cambridge clause are equivalent, and it
does not resolve the original merged rules' B-R mappings. Those remain
`unverified` until their actual comparison evidence is reviewed.

Review receipt: `sources/cambridge/reviews/2026-11-08-cls-001.json`.
Source manifest: `sources/cambridge/source_manifest_2026-11-08.json`.

## Findings retained as blockers

- `CLS-002` opens with an unconditional sentence-form classification broader
  than the contextual examples on p. 44 justify. It was not promoted into a
  teaching template. Its correct terminology discussion on p. 45 does not by
  itself justify every universal formulation in the merged record.
- `PHR-011` is explicitly hedged in the source. The overview and the named
  bare-role-NP exception are not a complete general error-detection algorithm.
  Its semantic scope, additional exceptions and B-R mapping remain open.
- The other 195 merged records are not independently re-certified by this
  review. Inventorying a PDF does not review every extracted rule.
- No production Cambridge constraint is enabled. The runtime allow-list stays
  unchanged. One reviewed Cambridge teaching template is now available.
- The B-R title/edition, relevant source pages, structural template review and
  unsupported/source-anomalous constructions remain unresolved. These twenty
  uploads are Cambridge sources and do not establish B-R evidence.

## Verification and milestone status

The explanation/schema/three-transport suite passes with the real teaching note,
including a provenance test tying its unchanged statement and page references to
the review receipt. Unsupported nodes still return `NO_BOOK_BASIS`; unresolved
analyses still produce no source claim. Browser tests compare Generator and
Builder with both the production registry and a separate synthetic fixture.

The global Cambridge bibliographic checklist item can now be checked. M2 and M3
remain unchecked: the new evidence closes a Cambridge starter-content gap,
not the remaining B-R structural/source and broader acceptance issues. M4 may
be planned, but its source-grounded publication gate is not certified.

## Runtime packaging correction

The original Dockerfile copied only `server/` and `web/`, while `.dockerignore`
excluded `docs/`. The shared composer imports the canonical schema at startup,
so that file set could not start the new backend. The image definition now also
copies the grammar registry/schemas and the one canonical schema JSON. Other
documentation remains excluded. `scripts/test_runtime_packaging.py` applies
the declared COPY inputs and exclusions, then imports the backend and exercises
its evidence endpoint without parser models. The check passes and is in CI.
A real Docker image build or hosted deployment is not claimed by this fixture.
