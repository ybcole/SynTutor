# Syntax Foundations Phase 2 review

The revision branch adds assessment and progression infrastructure. Published lessons still use their existing versions. The walkthrough intercepts the course request with a temporary Chapter 2 fixture so it can also exercise the Cambridge companion prerequisite. Its prompts and answers are test data. Phase 3 is the first Burton-Roberts content revision, beginning with Chapter 1.

## Learner walkthrough

1. Open the closing check from the chapter contents before visiting other sections. Submit answers to see a numerical last and best score, selected-answer feedback, and the full answers overview.
2. A first result of 0/6 earns 0 XP. The chapter completes after the required sections have been visited. The opening check is diagnostic and can be skipped.
3. Return to the introduction and submit the five-item opening check. The result shows the total correct. The signed-in record retains the first response and first score. The opening check UI shows no feedback or answer key.
4. Retake the closing check after reviewing the answers. For this six-item fixture, 3/6 gives 7 XP, 1/6 adds zero while updating the last score, 4/6 adds 3 XP, and 6/6 adds 5 XP. A five-item chapter uses the same formula and yields totals of 0, 3, 6, 9, 12, or 15 XP.
5. Reload during a check to recover the draft. On an offline account, the UI can show a local score immediately and labels the pending sync. The account XP total reflects acknowledged server progress. Guests have separate device progress and XP.

The browser captured desktop and 390 px mobile closing review. The test uses existing article teaching, tree and Builder components. Those interactions carry no points in revised chapters. Server scoring uses versioned keys. The static catalog contains the keys needed for guest and offline scoring, and learners can consult answers after closing submission. Section visits record access to the section.

## Activation and rollback

- The new migrations create private assessment and activation tables, plus own-row-only progress and attempt tables. No chapter is active by default.
- Each revision needs a fresh content version, reviewed lesson receipt, and matching immutable SQL seed. Generate the seed with `python scripts/seed_foundations.py`. Once a catalog migration has been applied to a deployment, add subsequent catalog rows through a new migration. Keep the validator's generated contract and published migration history aligned.
- Coordinate the frontend course switch with operator activation for each chapter. Activation switches which version contributes to the XP ledger, rejects retired writes through the old RPC, and recalculates the stats cache in the same transaction. Its scope is Foundations 1–11.
- Before hosted release, inventory versions and ledger totals, capture restorable snapshots, verify the target migration chain, and rehearse the frontend/database switch. For rollback, switch the course back and call `set_foundation_active_version(chapter, null)` for each affected chapter. The old rows remain available and totals are recalculated. Reactivating the same revision restores its recorded attempts and XP.
- The Cambridge companion still accepts historical Chapter 2 completion. Its prerequisite check also accepts a completed active Chapter 2 revision. The M8 achievement criteria retain their existing version bindings and historical evidence. Connecting future revised completions to version-specific badges remains a release integration item.

## Verification

- The revised browser walkthrough covers read-ahead, opening score visibility, draft reload, zero-score completion, closing review and retakes on desktop and mobile. The published lesson walkthrough passes for all 12 lessons.
- The disposable PostgreSQL walkthrough covers migration and rollback, concurrent retries and competing scores, RLS, forged inputs, retired writes, Cambridge prerequisites, and preservation of unrelated lesson and quiz XP. Account and version isolation and offline retries also pass in the JavaScript store tests.
- The publication validator still stops at the pre-existing Chapter 2 receipt mismatch. Phase 0 also recorded drift in Chapters 3 and 8 and the Cambridge companion. Existing receipts were preserved. No hosted migrations were run.

Gate 2 is review of the walkthrough and scoring examples. The next work is the Chapter 1 source-mapped storyboard and lesson pilot in Phase 3.
