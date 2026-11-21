# goldfish methodology (protocol v0.2, 2026-11-18)

goldfish measures one thing: **what fraction of injected facts an LLM still
reports correctly after its context has been compacted.** This document is the
normative spec. Every published number must cite a protocol version and be
reproducible with the command shown in the drop's run JSON.

## Protocol

### Setup
- Endpoint: any OpenAI-compatible `/v1/chat/completions`. Target of record must
  be named in the drop (model id, server build, thinking mode).
- Context budget: session is grown to ~76k est-tokens (5 growth stages), then
  one compaction event, then a final interrogation stage.
- Reps: >=3 seeds per configuration, reported individually. Means are
  supplementary; ranges are the headline.

### Probes (14 per stage)
| class | count | retained if |
|---|---|---|
| marker | 12 | crypto-random `GOLD-xxxxxxxx` string appears verbatim in the answer |
| entity | 1 | project codename appears verbatim |
| forbidden | 1 | forbidden word does NOT appear in a fruit-list answer (compliance probe) |

Canaries are generated per-seed from `secrets`, so no value ever repeats
across drops and none can leak from training data.

### Scoring
- Deterministic substring/compliance checks only. Never LLM-judged.
- Every probe forces `YOU_FORGOT` on recall failure: silence counts as
  forgotten, so fabrication cannot inflate scores and refusal is visible.
- If a reasoning server returns `content=None` (thinking ate the budget), the
  client falls back to `reasoning`/`reasoning_content` before scoring; drops
  must label whether any answers were scored from reasoning text.
- Retention = mean over probes. Compliance probe scores 1 for absence (this is
  a rule-following signal, not memory; survivor lists must classify it).

### Compaction
- Protocol v0.2 uses the harness summarizer: the same model under test is
  asked to summarize the session prefix above a recent tail (this mirrors what
  real harnesses do, but is NOT any vendor's native compactor). Native-client
  adapters (Claude Code /compact, etc.) are v0.3 and will be versioned
  separately because they are not comparable to harness numbers.

## Known limitations (publish with every drop)
- Token counts are char/4 estimates, not tokenizer-exact.
- 1 rep per stage per seed unless stated; ranges over seeds are the honest
  uncertainty signal at this scale.
- Harness compaction measures the model's summarizer, not vendor pipelines.
  Do not extrapolate a drop to "vendor X loses Y%" unless the vendor's own
  compactor was measured.
- 14 probes/stage is a screen, not a census. Small n: one probe flipping is
  7pp of retention.

## Integrity rules
1. Every number ships with: run JSON, sha256 of the JSON, exact reproduce
   command, endpoint + build identification, date.
2. Before publishing, all run JSONs are re-scored by an independent verifier
   (`drops/verify.py`, written separately from the scorer; mismatches must be
   0). If verifier and scorer disagree, the discrepancy is investigated to
   root cause and the resolution is written into the drop notes.
3. **Corrections policy:** any retracted or amended number gets an ERRATA
   entry in this file (dated, with the original claim and what was wrong) and
   the original post is quoted, not deleted. Silent edits void the lab's
   credibility.
4. No vendor relationships. If a project is ever commercialized, sponsorships
   are disclosed on the affected drop page.
5. Negative and null results are published. A week where nothing interesting
   moved is a real week, not a skipped week.

## Community runs
Any run submitted through the "Submit your curve" issue template (endpoint,
model, build, seed, JSON attached) is listed on the scoreboard under the
submitter's handle. We re-score submitted JSONs with the verifier before
listing. We do not filter results we dislike.

## External anchors
- COMPINT / arXiv 2608.11242: 17% constraint retention (synthetic eval sets).
- Governance Decay, arXiv 2606.22528: compaction erases safety constraints.
- Deployment-Time Memorization, arXiv 2606.10062: canary methodology for
  memory pipelines (different target: deletion/privacy, not compaction).

goldfish is the live-endpoint complement: you, your endpoint, tonight.
