"""Deterministic filler: synthetic dev-session turns to grow the context.

Filler content is generated from a seed (no LLM calls) so every run is
reproducible and token distances are exactly comparable across reps.
"""

import random

_FILES = [
    "src/api/routes.py", "src/api/auth.py", "src/core/engine.py",
    "src/db/models.py", "src/worker/queue.py", "src/config.py",
    "tests/test_engine.py", "tests/conftest.py", "deploy/fly.toml",
    "src/utils/retry.py", "src/utils/telemetry.py", "scripts/migrate.py",
]
_SYMPTOMS = [
    "500 errors spike after deploys",
    "worker queue backs up overnight",
    "flaky timeouts on the /search endpoint",
    "memory creep in the ingest job",
    "test suite hangs on CI runners",
    "cache misses doubled since the refactor",
]


def _log_block(rng: random.Random, size: int) -> str:
    lines = []
    for _ in range(size):
        f = rng.choice(_FILES)
        ln = rng.randint(10, 900)
        lvl = rng.choice(["INFO", "WARN", "ERROR"])
        ms = rng.randint(1, 4000)
        lines.append("%s %s:%d latency=%dms attempt=%d" % (lvl, f, ln, ms, rng.randint(1, 3)))
    return "\n".join(lines)


def filler_turns(count: int, seed: int, chunk_tokens: int = 900) -> list:
    """Returns a list of (user_text, assistant_text) pairs, deterministic by seed.
    Each pair adds roughly chunk_tokens*4 characters of context."""
    rng = random.Random(seed * 7919 + count)
    pairs = []
    for t in range(count):
        symptom = _SYMPTOMS[(seed + t) % len(_SYMPTOMS)]
        f = _FILES[(seed * 3 + t) % len(_FILES)]
        user = "Turn %d: we are still seeing %s. Show me the tail of %s and what it implies." % (
            t + 1, symptom, f)
        asst = ("Pulled %s and correlated the window. Findings for turn %d:\n\n%s\n\n"
                "Summary: the pattern points at %s retries amplifying %s. "
                "Next step is to bound the retry budget in %s and re-run the load profile. "
                "I have noted the surrounding evidence in my working notes for later turns."
                % (f, t + 1, _log_block(rng, chunk_tokens // 8), f, symptom, f))
        pairs.append((user, asst))
    return pairs
