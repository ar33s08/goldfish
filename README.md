# goldfish

**How much does your agent actually remember?**

goldfish injects canary facts into an agent's context (crypto-random
`GOLD-xxxxxxxx` markers, a project codename, one forbidden word), grows the
session, runs a harness-style compaction, then interrogates it memory-only.
Output: an exact retention table and a forgetting curve.

```
stage              age_tokens  window  compactions  retention
t0-fresh                498     498            0   100.0%
grown-4               76472   76472            0   100.0%
post-compact           7120    7120            1    14.3%
```

## Usage

```bash
GOLDFISH_BASE_URL=https://your-endpoint/v1 \
GOLDFISH_MODEL=your-model GOLDFISH_API_KEY=*** \
python -m goldfish.cli --markers 12 --seed 1337 --chunks 4 --json run.json
```

## Honest-signal protocol
Every probe demands `YOU_FORGOT` when recall fails, so silence is data, not
fabrication. Scoring is deterministic substring/compliance, never LLM-judged.

## Limits (v0.1)
- Compaction is goldfish's own harness-style summarizer, not the target
  client's native one (native-log adapters are v0.2).
- Token counts are char/4 estimates, labeled as such.
- Single rep per stage; use multiple seeds for confidence bands.
