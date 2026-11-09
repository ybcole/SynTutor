"""Small per-process request throttle for local/single-worker SynTutor deployments.

This is defense-in-depth, *not* a distributed API gateway rate limiter.
Production deployments with multiple workers/replicas require an upstream
shared quota and a documented proxy/client identity policy.
"""
from collections import deque
from threading import Lock
from time import monotonic


class RateLimiter:
    def __init__(self, window_seconds=60, clock=monotonic):
        self.window_seconds = window_seconds
        self.clock = clock
        self.lock = Lock()
        self.history = {}

    def permit(self, client, limit):
        if limit <= 0:
            return True
        now = self.clock()
        with self.lock:
            hits = self.history.setdefault(client, deque())
            cutoff = now - self.window_seconds
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            # Drop idle keys to avoid retaining arbitrary client identities.
            if len(self.history) > 2048:
                for key, old in list(self.history.items()):
                    if old[-1] <= cutoff:
                        del self.history[key]
            return True
