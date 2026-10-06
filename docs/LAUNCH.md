# goldfish launch — D0–D5 drafts

Rule inherited from contextfloor: every posted number must be reproducible by a
command from this repo; screenshot the terminal, never fabricate.

## The measured facts (3 seeds, qwen3.8-flash-next @ 262k window, 14 canaries, ~76k tokens, 1 compaction)

| seed | post-compaction retention |
|------|---------------------------|
| 1337 | 14.3% |
| 4242 | 21.4% |
| 9001 | 7.1%  |

**Range: 7–21% (mean 14.3%) — vs 100% retention at every pre-compaction stage
through 76k tokens.** Note seed 4242's 92.9% dip at grown-2: even growth alone
occasionally costs a fact; compaction is the systematic killer.

Reproduce: `python -m goldfish.cli --markers 12 --seed <1337|4242|9001> --chunks 4 --turns-per-chunk 6 --json run.json`

## D0 (today) — the curve post
Everyone jokes that agents have "goldfish memory."
Nobody could measure it. Now you can.

I injected 14 facts into an agent's context (random canary strings, a project
codename, one style rule), grew the session to 76,000 tokens, then interrogated
it. Through the entire growth: 100% recall. Then one compaction event — the
automatic "summarizing older context" step every long session hits:

7 to 21% of the facts survived. 3 seeds, same cliff.

The two survivors were always the *semantic* ones — the codename, the rule.
The summarizer keeps stories. It deletes secrets. Your "never touch the
migrations folder" is a story, until the day it isn't.

[Screenshot: the curve from run-4242.out + certificate-style table]

This is project #3 in the measurement series (gguf-sentinel: what you
download isn't what you ran → contextfloor: what you pay before you type →
goldfish: what survives the session).

Repo: github.com/ar33s08/goldfish — MIT. Run it on your own endpoint:
`pip install`, one command, your own curve.

## D1 — "the 17% paper" post
Reference COMPINT (arXiv 2608.11242): 17% constraint retention, measured on
synthetic eval sets. goldfish = what you run when the agent under test is
*your* agent, on *your* endpoint, tonight.

## D2 — the fix hook
What survived across all 3 runs? Semantic facts. So the cheapest guard is a
pinned constraint file re-attached after compaction — measure it: goldfish on,
goldfish off. (That experiment is the sequel; ship only after D0–D1 land.)

## D3-D5 — reply-farming
Post "run it against your stack and drop your curve in the comments" once,
with a pinned comment giving the exact one-liner.

## Status
- [x] 3-seed data (done 2026-10-04, files run1.json, run-4242.json, run-9001.json committed)
- [ ] public repo push (needs gh auth confirm)
- [ ] screenshots of the three .out curves
- [ ] D0 posted after green CI / clean-tree check
