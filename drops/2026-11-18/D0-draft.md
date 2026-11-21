# D0 draft — drop 1 (2026-11-18) · production stack edition

Every number here is reproducible from github.com/ar33s08/goldfish with:
`python -m goldfish.cli --base-url <your-endpoint>/v1 --model <model> --markers 12 --seed <1337|4242|9001> --chunks 4 --turns-per-chunk 6 --json run.json`
Run file hashes (sha256): 1337=`3fbd30f2dd022d37…` 4242=`b06698953f83e434…` 9001=`0a8a41597423ec0f…` (full hashes in repo `drops/2026-11-18/`, independently re-scored: 0/252 probe disagreements).

## FINAL POST (279 chars incl. link — verified) — attach drop1-curve.png

Run an agent long enough and it forgets your instructions. I didn't have numbers for that, so I built the tool: 14 facts injected, grown to 76k tokens, one forced compaction, then an interrogation.

0-7% survived across 3 seeds. The codename never made it.

https://github.com/ar33s08/goldfish

## Reply 1 (post immediately after)

Two details worth more than the headline:

- The project codename survived 3/3 runs on my October test build. On the production build it was forgotten in every run. The summarizer keeps stories and drops identifiers.
- One run didn't just forget the "never say X" rule, it used the word. Compliance decay, same pattern as the Governance Decay paper (arXiv 2606.22528).

Run JSONs, hashes, methodology and a corrections policy: https://ar33s08.github.io/goldfish

## Reply 2 (caveats — put them up before someone asks)

Disclosed in the methodology (protocol v0.2): compaction is my summarizer, same model under test, not any vendor's native pipeline. Token counts are char/4 estimates. Scoring is deterministic substring with a forced YOU_FORGOT, never LLM-judged. All runs re-scored by a separate verifier: 0 disagreements across 252 probes. Numbers this small move 7pp per probe, so seeds are reported individually, not averaged away.

## Reply 3 (the harness question, if it comes up)

Harnesses mitigate this — that's why they exist. We run a 24/7 agent org on this endpoint and it survives by keeping state outside the window. The open question nobody has answered with numbers is whether those mitigations actually work. Next drop measures exactly that: same cliff, pinned-constraint file re-attached after compaction, on/off.

## Reply 4 (if someone posts a curve or asks to contribute)

Repo has a "Submit your curve" issue template — attach your run JSON and we re-score it with the verifier and list it on the lab page under your handle. We publish results we don't like too.

## Kill switch reminder
8 weekly drops, <500 combined views, 0 inbound → niche dies clean, full-time Recovery Desk. No fifth invention.

## Honest-signal labels (keep in thread reply #1)
- Compaction = goldfish's harness-style summarizer, same model under test (native-client adapters are v0.2).
- Token counts are char/4 estimates, labeled as such.
- 1 rep per stage per seed; substring scoring, never LLM-judged; `YOU_FORGOT` demanded on recall failure so silence is data.
- "0–7%" = 1 of 14 probes survived in two runs, 0 in one. The single "survivors" were style-rule compliance passes (not memory) — we count them as retained per protocol and show raw counts here.
- Canary methodology neighbors: Workday's deployment-time-memorization paper (arXiv 2606.10062) uses high-entropy canaries for deletion/privacy; COMPINT (arXiv 2608.11242) found 17% constraint retention on synthetic sets. goldfish = the same honesty applied to YOUR session, on YOUR stack, in one command.

## Follow-ups queued
- D2 (drop 2): same model, vLLM build vs TensorFold build — October data says the codename survived 3/3 on vLLM vs 0/3 on production build. That build-vs-build delta is itself a story.
- D3: pinned-constraint-file fix hook — goldfish on/off measurement.
