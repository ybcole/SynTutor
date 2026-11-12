-- LREF PROPOSAL: Analysis-history diagnostic status
--
-- Status: DRAFT — NOT APPLIED
--
-- Purpose:
-- Preserve diagnostic uncertainty and authority without
-- destroying compatibility with existing history records.
--
-- Do not deploy until the frontend, database compatibility,
-- and account/RLS integration tests have been reviewed.

ALTER TABLE public.analysis_history
  ADD COLUMN IF NOT EXISTS analysis_status text,
  ADD COLUMN IF NOT EXISTS diagnostic_authority text;

-- Existing history records intentionally retain NULL statuses.
-- Never infer the original verdict from is_valid.

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'analysis_history_analysis_status_check'
      AND conrelid = 'public.analysis_history'::regclass
  ) THEN
    ALTER TABLE public.analysis_history
      ADD CONSTRAINT analysis_history_analysis_status_check
      CHECK (
        analysis_status IS NULL
        OR analysis_status IN (
          'reported_violation',
          'verified_local_violation',
          'no_supported_error_detected',
          'unverified',
          'legacy_unclassified'
        )
      );
  END IF;
END
$$;

COMMENT ON COLUMN public.analysis_history.analysis_status IS
  'Diagnostic status; NULL indicates an unclassified historical record.';

COMMENT ON COLUMN public.analysis_history.diagnostic_authority IS
  'Producing diagnostic authority, not a certification of correctness.';

-- Retain is_valid during the compatibility period.
-- Do not change existing Row Level Security policies.
-- Do not backfill old records using is_valid.
