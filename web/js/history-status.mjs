const LABELS = Object.freeze({
  reported_violation: "Issue reported — verification not established",
  verified_local_violation: "Verified local violation",
  no_supported_error_detected: "No supported error detected",
  unverified: "Unable to verify",
  legacy_unclassified: "Previous analysis — status unknown",
});

export function fromSummary(summary = {}) {
  const verdict = summary.verdict;

  const status = ({
    grammatical: "no_supported_error_detected",
    ungrammatical: "reported_violation",
    unverified: "unverified",
  })[verdict] ?? "unverified";

  return {
    analysis_status: status,
    diagnostic_authority:
      summary.verdict_authority ?? "unknown",
    // Retained only for compatibility with the existing database.
    // Never use this Boolean to classify a history entry.
    is_valid: verdict === "grammatical",
  };
}

export function forDisplay(row = {}) {
  const status = Object.hasOwn(
    LABELS, row.analysis_status
  ) ? row.analysis_status : "legacy_unclassified";

  const group =
    status === "reported_violation" ||
    status === "verified_local_violation"
      ? "reported"
      : status === "no_supported_error_detected"
        ? "no_issue_reported"
        : "uncertain";

  return {
    status,
    label: LABELS[status],
    group,
  };
}

export function matchesHistoryFilter(row, filter) {
  const { group } = forDisplay(row);

  if (filter === "error") {
    return group === "reported";
  }

  if (filter === "valid") {
    return group === "no_issue_reported";
  }

  return true;
}
