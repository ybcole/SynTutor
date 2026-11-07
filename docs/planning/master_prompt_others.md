# Master Prompt — Data, Governance, Testing, Security, and Release

## Role
Act as the technical program lead and quality/reliability engineer for SynTutor.

## Objective
Build the governance, persistence, testing, and release infrastructure required to keep linguistic content and learner progress trustworthy as the system changes.

## Required workstreams

### Source governance
- Record exact bibliographic editions, chapters, sections, printed pages, PDF pages, evidence type, extraction protocol, review state, and copyright status.
- Keep source approval, framework crosswalk approval, runtime implementation, and test status separate.
- Maintain `unverified`/`uncertain` records honestly.

### Content versioning
- Version B-R convention profiles, Cambridge rules, lesson content, quiz assessments, and explanation templates.
- Tie progress/rewards to content version so edits do not duplicate XP or invalidate mastery silently.

### Activity ledger
- Store user, activity type, activity/content version, result evidence, calculated XP, unique idempotency key, and timestamp.
- Make event writes auditable and safe to retry.
- Calculate/validate XP on a trusted backend/RPC.

### Copyright and privacy
- Public repo: paraphrases, citations, original examples, and permissible compact structures only.
- Do not publish full textbook PDFs, extracted chapter prose, or copied exercise wording.
- Minimize public user data; leaderboard identities must be opt-in aliases.

### Testing/CI
Add automated checks for:
- JSON schema and ID uniqueness.
- Broken source/rule/concept/tree references.
- B-R chapter conventions and gold tree matching.
- Benepar normalization and unresolved analysis behavior.
- Cambridge constraints, exceptions, variety, and rule-type semantics.
- Explanation evidence/source citations.
- Corrected word alignment.
- XP calculation/idempotency.
- Achievement unlock conditions.
- Leaderboard RLS/privacy.
- Browser E2E flows and responsive layout.

### Observability/release
- Track unresolved parses and review-worthy disagreements.
- Collect minimal privacy-conscious metrics on false positives/negatives, quiz discrimination, learner confusion, and exits.
- Use feature flags and a controlled pilot.
- Compare old/new outputs on a fixed corpus.
- Keep a rollback path and database migration plan.

## Deliverables

1. Source registry and governance policy.
2. Versioning model.
3. XP activity ledger schema and trusted-write design.
4. Copyright/privacy checklist.
5. Test/CI plan and implementation.
6. Observability plan.
7. Staged release and rollback procedure.
8. Evidence that the new pipeline passes agreed acceptance gates.

## Stop condition
Do not call SynTutor production-ready merely because the core feature works locally. Stop at each governance/security/release gate until the required tests and reviews are complete.
