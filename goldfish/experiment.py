"""The experiment: build -> grow -> (compact) -> probe -> score.

Retention is measured at checkpoints along the session. The forgetting
curve is retention vs. context-age in (estimated) tokens.
"""

import math

from .canary import build_canary_set
from .filler import filler_turns

YOU_FORGOT = "YOU_FORGOT"

SYSTEM = ("You are a coding assistant in a long working session. "
          "Treat everything in this conversation as your own prior work in this session. "
          "When asked something about the session, answer from the session only.")

BRIEFING_TEMPLATE = (
    "# Project briefing (read carefully; you will be asked about it later)\n"
    "You are starting a long session on a project. Keep these notes in mind.\n"
    "- The project codename is {entity}.\n"
    "- Style rule for the whole session: when listing fruits, never use the word "
    "'{forbidden}'.\n"
    "- Integrity canaries: at each section boundary below there is a marker of the "
    "form GOLD-xxxxxxxx. Later you may be asked to recall them verbatim.\n"
    "{slots}\n"
    "# End of briefing\n"
)

PROBE_INSTRUCTION = (
    "\n\n---\nPROBE: Answer ONLY from your memory of this session. Do not guess, "
    "do not invent. If you cannot recall it, reply with exactly %s. "
    "Question: %%s" % YOU_FORGOT
)

COMPACT_PROMPT = (
    "Summarize the conversation so far into a compact handoff note. Preserve every "
    "concrete fact, identifier, constraint, rule, and any GOLD-xxxxxxxx markers. "
    "Output only the summary."
)


def build_briefing(canaries):
    slots = []
    markers = [c for c in canaries if c["kind"] == "marker"]
    entity = next(c for c in canaries if c["kind"] == "entity")["value"]
    forbidden = next(c for c in canaries if c["kind"] == "forbidden")["value"]
    for i, m in enumerate(markers):
        slots.append("--- %s ---\nSection %d: deployment notes, retry budgets, "
                     "owner decisions and conventions for area %d." % (m["value"], i + 1, i + 1))
    return BRIEFING_TEMPLATE.format(entity=entity, forbidden=forbidden,
                                    slots="\n".join(slots))


def initial_messages(canaries):
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_briefing(canaries)}]


def _strip_marker(text):
    return text


def score_probe(canary, answer):
    """Returns 1.0 retained / 0.0 lost. Forbidden canary scores compliance
    (forbidden word must NOT appear in a fruit answer)."""
    if canary["kind"] == "marker":
        return 1.0 if canary["value"] in answer else 0.0
    if canary["kind"] == "entity":
        return 1.0 if canary["value"] in answer else 0.0
    return 0.0 if canary["value"] in answer.lower() else 1.0


class Experiment:
    def __init__(self, client, n_markers=12, seed=1337, chunk_tokens=900,
                 compact_at=24000, tail_turns=4):
        self.client = client
        self.seed = seed
        self.chunk_tokens = chunk_tokens
        self.compact_at = compact_at
        self.tail_turns = tail_turns
        self.canaries = build_canary_set(n_markers, seed)
        self.messages = initial_messages(self.canaries)
        self.grew_tokens = 0
        self.compactions = 0

    def tokens(self):
        return self.client.count_tokens_approx(self.messages) + self.grew_tokens

    def grow(self, turns):
        """Append `turns` synthetic filler turns verbatim (no model call needed:
        in a real session these tokens enter the window; we model the window,
        not the agent's prose)."""
        for user, asst in filler_turns(turns, self.seed, self.chunk_tokens):
            self.messages.append({"role": "user", "content": user})
            self.messages.append({"role": "assistant", "content": asst})
            self.grew_tokens += (len(user) + len(asst)) // 4

    def compact(self):
        """Harness-style compaction: summarize everything but the recent tail."""
        keep = self.messages[-2 * self.tail_turns:]
        head = self.messages[:-2 * self.tail_turns]
        if len(head) < 2:
            return False
        summary = self.client.chat(
            head + [{"role": "user", "content": COMPACT_PROMPT}], max_tokens=700)
        self.messages = [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": "Summary of conversation so far:\n" + summary}] + keep
        self.grew_tokens = 0
        self.compactions += 1
        return True

    def probe(self, canary):
        question = canary["question"]
        if question.startswith("forbidden:"):
            ask = ("PROBE: Name several tropical fruits. Rules from earlier in "
                   "this session still apply.")
        elif question.startswith("marker:"):
            ask = PROBE_INSTRUCTION % (
                "What is the exact value of the canary marker written at section "
                "boundary %d of the briefing? Quote it verbatim." % (canary["slot"] + 1))
        else:
            ask = PROBE_INSTRUCTION % question.split(":", 1)[1]
        msgs = self.messages + [{"role": "user", "content": ask}]
        return self.client.chat(msgs, max_tokens=900)

    def probe_all(self, label, age_tokens):
        results = []
        for c in self.canaries:
            ans = self.probe(c)
            results.append({"canary": c["kind"], "slot": c["slot"], "value": c["value"],
                            "retained": score_probe(c, ans), "answer": ans[:300]})
        retained = sum(r["retained"] for r in results) / len(results)
        return {"stage": label, "age_tokens": age_tokens, "compactions": self.compactions,
                "window_tokens": self.tokens(), "retention": retained, "results": results}
