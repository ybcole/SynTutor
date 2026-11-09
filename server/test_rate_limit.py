"""Deterministic tests for the opt-in per-process request throttle."""
import unittest

from rate_limit import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def test_fixed_window_quota_and_recovery(self):
        clock = [10.0]
        limiter = RateLimiter(clock=lambda: clock[0])
        self.assertTrue(limiter.permit("reader-a", 2))
        self.assertTrue(limiter.permit("reader-a", 2))
        self.assertFalse(limiter.permit("reader-a", 2))
        self.assertTrue(limiter.permit("reader-b", 2))
        clock[0] += 60.1
        self.assertTrue(limiter.permit("reader-a", 2))

    def test_zero_limit_means_disabled(self):
        limiter = RateLimiter()
        for _ in range(200):
            self.assertTrue(limiter.permit("reader-a", 0))


if __name__ == "__main__":
    unittest.main()
