"""Per-process limits: bounded owner/timestamp state; no study content retained."""
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Lock
from time import monotonic

from app.ai.errors import AIError


@dataclass
class Usage:
    minute: deque = field(default_factory=deque)
    day_start: float = 0
    daily: int = 0
    inflight: bool = False


class AILimiter:
    def __init__(self, *, clock=monotonic, max_users=10000):
        self.clock = clock
        self.max_users = max_users
        self.users = {}
        self.active = 0
        self.lock = Lock()

    @contextmanager
    def acquire(self, user_id):
        with self.lock:
            now = self.clock()
            # Do not evict active/day-limited users and reopen their quota.
            expired = [uid for uid, state in self.users.items()
                       if not state.inflight and now - state.day_start >= 86400]
            for uid in expired:
                del self.users[uid]
            state = self.users.get(user_id)
            if state is None:
                if len(self.users) >= self.max_users:
                    raise AIError(429, "AI capacity is busy. Try again later.")
                state = Usage(day_start=now)
                self.users[user_id] = state
            while state.minute and now - state.minute[0] >= 60:
                state.minute.popleft()
            if state.inflight or len(state.minute) >= 5 or state.daily >= 100 or self.active >= 8:
                raise AIError(429, "AI request limit reached. Try again later.")
            state.minute.append(now)
            state.daily += 1
            state.inflight = True
            self.active += 1
        try:
            yield
        finally:
            with self.lock:
                state.inflight = False
                self.active -= 1


limiter = AILimiter()
