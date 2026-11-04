# MASTER PROMPT — SynTutor book layer (give this to any AI, every session)

You are helping build the "book layer" of SynTutor from Noel Burton-Roberts,
*Analysing Sentences*. Work on ONE chapter per session.

## Files you must have before starting
- CONVENTIONS.md  (the only rulebook; read ALL of it first)
- book/chNN.trees.json + book/validate_chNN.py for chapters already done (as examples)
- The chapter PDF for this session (if you can see page images)
- schema.md once it exists (first session: you will propose it, see Phase 2)

If a required file is missing, stop and tell me. Do not improvise.

## Priority order when sources disagree
1. The book (I check by eye)  2. CONVENTIONS.md  3. chNN.trees.json  4. existing code.
Never "fix" a tree or a convention yourself. Conflict or gap -> mark UNSURE and ask me.

## Hard rules
- Never use Penn Treebank / benepar / textbook X-bar habits. Book only.
- Draw each tree with the conventions of ITS chapter (convention_version). Never use a
  later chapter's labels in an earlier chapter (no NOM before Ch7, no S-bar before Ch6).
- Functions (subject, dO...) are NOT nodes; they are read off positions (CONVENTIONS §6).
- Every explanation shown to a learner must be a paraphrase tied to a book page
  (CONVENTIONS §14). No page -> write NO_BOOK_BASIS, do not invent a reason.
- Public repo: paraphrase only. No passages, no copied exercise wording. At most a
  few words quoted, always with chapter + printed page.
- Do not touch the parser, rule matrix, or the 20 existing lessons.
- Do not invent exercises beyond the book's.

## Per-chapter workflow (STOP at each gate and wait for my "approved")
Phase 1 - Trees from page images
  1. Rasterize every page with a figure, including "Discussion of exercises".
  2. Transcribe EVERY tree into book/chNN.trees.json (format: CONVENTIONS §2.2), with
     figure id, printed page, status IMG. Unreadable part -> UNSURE, never a guess.
     Trees the book never prints but the exercise wording fixes completely ->
     status DERIVED_FROM_INSTRUCTIONS. Trees not fixed by the wording -> leave out.
  3. Write book/validate_chNN.py that runs the book's OWN answers against the trees
     (dominance, immediate constituents, functions read from positions, etc.).
  4. Run it. Show me the output and a list of figures with page numbers.
  GATE 1: I compare your transcriptions with the book pages.

Phase 2 - Concepts
  5. List every concept/term of this chapter (new vs. revised from earlier chapters),
     with page numbers and any "superseded_by" later chapter. No lesson text yet.
  GATE 2: I approve or edit the concept list.

Phase 3 - Lesson file
  6. Write book/chNN.json: concepts, lesson steps (explain -> example -> check),
     examples with gold tree ids, exercises (type: build | constituent-check |
     identify-function | question) with the book's answer, and explanations
     {concept_id, text, source{chapter,page,kind}, convention_version, superseded_by,
     status}. Accepted alternatives and book simplifications go in their own fields
     (CONVENTIONS §9). Mark anything unsure NEEDS_REVIEW.
  7. Run the checklist in CONVENTIONS §13 and report each item pass/fail.
  GATE 3: I read it against the book once.

Phase 4 - Report
  8. List: files created, tests run and results, every UNSURE / NEEDS_REVIEW item,
     and anything you could not do. Do not claim success for anything you did not run.

## First chapter only
Before Phase 3 for Chapter 1, propose book/schema.md (the chNN.json format) and wait for
approval. After approval it is frozen; later chapters follow it.

## Chapter order
1 -> 10 in book order. Chapter 11 (no trees) becomes a text-only closing lesson,
done last.
