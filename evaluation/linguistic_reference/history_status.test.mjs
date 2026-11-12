import test from "node:test";
import assert from "node:assert/strict";

import {
  fromSummary,
  forDisplay,
  matchesHistoryFilter,
} from "../../web/js/history-status.mjs";

test("legacy grammatical verdict does not certify correctness", () => {
  const result = fromSummary({
    verdict: "grammatical",
    verdict_authority: "legacy_diagnostic",
  });

  assert.equal(
    result.analysis_status,
    "no_supported_error_detected"
  );
  assert.equal(
    result.diagnostic_authority,
    "legacy_diagnostic"
  );
});

test("reported violations retain legacy authority", () => {
  const result = fromSummary({
    verdict: "ungrammatical",
    verdict_authority: "legacy_diagnostic",
  });

  assert.equal(
    result.analysis_status,
    "reported_violation"
  );
  assert.notEqual(
    result.analysis_status,
    "verified_local_violation"
  );
});

test("unverified verdict is not displayed as invalid", () => {
  const result = fromSummary({
    verdict: "unverified",
    verdict_authority: "legacy_diagnostic",
  });

  assert.equal(result.is_valid, false);
  assert.equal(forDisplay(result).group, "uncertain");
  assert.equal(forDisplay(result).label, "Unable to verify");
});

test("old false records must not be assumed incorrect", () => {
  const result = forDisplay({
    sentence: "The boys runs.",
    is_valid: false,
  });

  assert.equal(result.status, "legacy_unclassified");
  assert.equal(result.group, "uncertain");
});

test("old true records are also not independently certified", () => {
  const result = forDisplay({
    sentence: "The boy runs.",
    is_valid: true,
  });

  assert.equal(result.status, "legacy_unclassified");
});

test("new explicit status takes precedence over Boolean", () => {
  const result = forDisplay({
    is_valid: false,
    analysis_status: "unverified",
  });

  assert.equal(result.status, "unverified");
  assert.equal(result.group, "uncertain");
});

test("error filter excludes uncertain and historical records", () => {
  for (const status of [
    "unverified",
    "legacy_unclassified",
    "no_supported_error_detected",
  ]) {
    assert.equal(
      matchesHistoryFilter({ analysis_status: status }, "error"),
      false
    );
  }

  for (const status of [
    "reported_violation",
    "verified_local_violation",
  ]) {
    assert.equal(
      matchesHistoryFilter({ analysis_status: status }, "error"),
      true
    );
  }
});

test("valid filter includes only no-supported-error status", () => {
  assert.equal(
    matchesHistoryFilter({
      analysis_status: "no_supported_error_detected"
    }, "valid"),
    true
  );

  for (const status of [
    "reported_violation",
    "verified_local_violation",
    "unverified",
    "legacy_unclassified",
  ]) {
    assert.equal(
      matchesHistoryFilter({ analysis_status: status }, "valid"),
      false
    );
  }

  assert.equal(
    matchesHistoryFilter({ is_valid: true }, "valid"),
    false
  );
});
