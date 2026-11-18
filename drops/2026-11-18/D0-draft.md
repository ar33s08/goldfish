# D0 draft — drop 1 (2026-11-18) · production stack edition

Every number here is reproducible from github.com/ar33s08/goldfish with:
`python -m goldfish.cli --base-url <your-endpoint>/v1 --model <model> --markers 12 --seed <1337|4242|9001> --chunks 4 --turns-per-chunk 6 --json run.json`
Run file hashes (sha256): 1337=`3fbd30f2dd022d37…` 4242=`b06698953f83e434…` 9001=`0a8a41597423ec0f…` (full hashes in repo `drops/2026-11-18/`, independently re-scored: 0/252 probe disagreements).

## Post text (X)

Everyone jokes that agents have "goldfish memory." Nobody could measure it. Now you can — in about an hour, on your own endpoint.

We injected 14 facts into an agent's context (crypto-random canary strings, a project codename, one style rule), grew the session to 76,000 tokens, and interrogated it memory-only.

Through the growth: recall held (93–100%, though one seed quietly frayed to 71% on its own). Then ONE compaction event — the automatic "summarize older context" step every long session hits on a 262k model:

0 to 7% of the facts survived. 3 seeds, same cliff.

Two details the vendors won't post:

• The project codename — the one fact that survived all 3 runs on our October test stack — was FORGOT IN EVERY RUN on the production stack. The summarizer keeps stories; it deletes identifiers.

• On 1 of 3 runs the agent didn't just forget the "never say X" style rule — it cheerfully violated it. Compliance decay, exactly as the Governance Decay paper (arXiv 2606.22528) predicts.

Your "never touch the migrations folder" instruction is a story the summarizer tells until the day it doesn't.

This is our production bot-farm stack — the model + server we actually run 24/7, not a lab build. Curve attached, hashes in repo. Run it against your stack and drop your curve in the comments.

#AIagents #LLM #contextrot

[attach drop1-curve.png]

## Honest-signal labels (keep in thread reply #1)
- Compaction = goldfish's harness-style summarizer, same model under test (native-client adapters are v0.2).
- Token counts are char/4 estimates, labeled as such.
- 1 rep per stage per seed; substring scoring, never LLM-judged; `YOU_FORGOT` demanded on recall failure so silence is data.
- "0–7%" = 1 of 14 probes survived in two runs, 0 in one. The single "survivors" were style-rule compliance passes (not memory) — we count them as retained per protocol and show raw counts here.

## Follow-ups queued
- D2 (drop 2): same model, vLLM build vs TensorFold build — October data says the codename survived 3/3 on vLLM vs 0/3 on production build. That build-vs-build delta is itself a story.
- D3: pinned-constraint-file fix hook — goldfish on/off measurement.
