# SynTutor Review Summary

Review date: 2026-11-19

## Security findings

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | web/js/auth.js | 3, 38 | Mutable remote JavaScript dependencies (`@supabase/supabase-js@2` and `@clerk/clerk-js@5`) execute with access to Clerk session tokens without immutable pinning or Subresource Integrity. | 9/10 |

## System findings

| # | Severity | File | Lines | Defect | Confidence |
|---|----------|------|-------|--------|------------|
| 1 | 🔴 CRITICAL | vercel.json | 1-3 | The Vercel configuration deploys only `dist/` and provides no backend route mapping. With `API_BASE` empty, frontend calls to `/api/*` hit Vercel instead of Flask, breaking parsing and Builder features. | 9/10 |
| 2 | 🔴 CRITICAL | web/js/config.js | 12 | The tracked configuration contains a literal placeholder Supabase anonymous key (`******`) that is not detected as invalid, preventing account and progress synchronization. | 9/10 |
| 3 | 🟠 HIGH | server/hf_space.py | 221-227 | The Hugging Face transport mounts parse, evaluate, and explain but omits `/api/words` and `/api/repair-check`, despite frontend callers. | 9/10 |
| 4 | 🟡 MEDIUM | server/hf_space.py | 173-183 | The Hugging Face parser omits `include_candidate_xai` when calling `build_payload`, producing an entry-point-dependent explanation contract. | 8/10 |
| 5 | 🟡 MEDIUM | .gitignore; docs/README.md | 210-216 | Documentation says `web/js/config.js` is ignored, but it is tracked and the `.gitignore` has no matching rule. Environment-specific credentials or placeholders can be committed accidentally. | 9/10 |

## Verification

- Production build passed.
- Full Python suite: 917 tests passed; 45 skipped.
- Quiz V2, lessons, assessments, and builder JavaScript suites passed.
- Initial Python run had three missing-FastAPI dependency errors; installing `requirements-test.txt` resolved them and the rerun passed.
