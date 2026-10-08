"""goldfish offline test suite: mechanics verified without any model calls."""
import re

from goldfish.canary import build_canary_set, marker
from goldfish.experiment import Experiment, PROBE_INSTRUCTION, score_probe
from goldfish.filler import filler_turns
from goldfish.report import headline, render_curve, render_table


class FakePerfect:
    """Recalls everything visible in the window; obeys no word bans."""

    def chat(self, msgs, max_tokens=700, temperature=0.0):
        vis = " ".join(m["content"] for m in msgs)
        asked = msgs[-1]["content"]
        m = re.search(r"boundary (\d+)", asked)
        if m:
            toks = re.findall(r"GOLD-[0-9a-f]{8}", vis)
            return toks[int(m.group(1)) - 1]
        if "codename" in asked:
            return re.search(r"codename is ([A-Za-z]+-[A-Za-z]+)", vis).group(1)
        return "banana, pineapple, coconut"

    def count_tokens_approx(self, msgs):
        return sum(len(m["content"]) for m in msgs) // 4


class FakeAmnesiac:
    def chat(self, msgs, max_tokens=700, temperature=0.0):
        return "YOU_FORGOT"

    def count_tokens_approx(self, msgs):
        return sum(len(m["content"]) for m in msgs) // 4


class FakeCompactOnly:
    def chat(self, msgs, max_tokens=700, temperature=0.0):
        return "Summary: worked on stuff."

    def count_tokens_approx(self, msgs):
        return sum(len(m["content"]) for m in msgs) // 4


def test_marker_determinism_and_uniqueness():
    assert marker(3, 1337) == marker(3, 1337)
    cs = build_canary_set(12, 1337)
    vals = [c["value"] for c in cs if c["kind"] == "marker"]
    assert len(set(vals)) == 12
    assert len(cs) == 14  # 12 markers + entity + forbidden


def test_probe_template_literal():
    assert "%s" in PROBE_INSTRUCTION
    assert "YOU_FORGOT" in PROBE_INSTRUCTION


def test_filler_deterministic():
    assert filler_turns(3, 5) == filler_turns(3, 5)
    assert len(filler_turns(3, 5)) == 3


def test_perfect_recall_scores_1():
    e = Experiment(FakePerfect(), n_markers=6, seed=7)
    assert e.probe_all("t0", e.tokens())["retention"] == 1.0
    e.grow(2)
    assert e.probe_all("grown", e.tokens())["retention"] == 1.0
    assert e.tokens() > 0


def test_amnesiac_scores_low_exact():
    e = Experiment(FakeAmnesiac(), n_markers=3, seed=7)
    # 3 markers + entity lost, forbidden-word compliant: 1/5
    assert abs(e.probe_all("t0", e.tokens())["retention"] - 0.2) < 1e-9


def test_compaction_structure_and_empty_head_guard():
    e = Experiment(FakeCompactOnly(), n_markers=3, seed=7)
    assert e.compact() is False  # head too small: no-op, no crash
    e.grow(6)
    assert e.compact() is True
    assert e.compactions == 1
    assert e.messages[1]["content"].startswith("Summary of")
    s = e.probe_all("post", e.tokens())
    assert all(r["retained"] == 0.0 for r in s["results"] if r["canary"] == "marker")


def test_scorer_semantics():
    cs = build_canary_set(2, 7)
    ent = next(c for c in cs if c["kind"] == "entity")
    forb = next(c for c in cs if c["kind"] == "forbidden")
    assert score_probe(ent, "codename is %s" % ent["value"]) == 1.0
    assert score_probe(ent, "YOU_FORGOT") == 0.0
    assert score_probe(forb, "banana, pineapple, coconut") == 1.0
    assert score_probe(forb, "banana, %s" % forb["value"]) == 0.0


def test_report_renderers():
    e = Experiment(FakePerfect(), n_markers=2, seed=7)
    stages = [e.probe_all("t0", e.tokens())]
    e.grow(1)
    stages.append(e.probe_all("grown", e.tokens()))
    for s in stages:
        s["compactions"] = 0
    t = render_table(stages)
    assert "retention" in t and "%" in t
    c = render_curve(stages)
    assert "#" in c
    h = headline(stages)
    assert "goldfish:" in h and "%" in h
