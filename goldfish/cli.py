"""goldfish CLI: run the forgetting-curve experiment on an OpenAI-compatible model."""

import argparse
import json
import os
import sys

from .client import ChatClient
from .experiment import Experiment
from .report import render_table, render_curve, headline


def main(argv=None):
    p = argparse.ArgumentParser(prog="goldfish")
    p.add_argument("--base-url", default=os.environ.get("GOLDFISH_BASE_URL"))
    p.add_argument("--api-key", default=os.environ.get("GOLDFISH_API_KEY", ""))
    p.add_argument("--model", default=os.environ.get("GOLDFISH_MODEL"))
    p.add_argument("--markers", type=int, default=12)
    p.add_argument("--seed", type=int, default=1337)
    p.add_argument("--chunks", type=int, default=4, help="grow stages")
    p.add_argument("--turns-per-chunk", type=int, default=6)
    p.add_argument("--compact-at", type=int, default=24000, help="est tokens before compaction")
    p.add_argument("--no-compact", action="store_true")
    p.add_argument("--json", dest="json_out")
    a = p.parse_args(argv)
    if not (a.base_url and a.model):
        p.error("--base-url and --model required (or GOLDFISH_BASE_URL/GOLDFISH_MODEL)")

    client = ChatClient(a.base_url, a.api_key, a.model)
    exp = Experiment(client, n_markers=a.markers, seed=a.seed, compact_at=a.compact_at)
    stages = []
    stages.append(exp.probe_all("t0-fresh", exp.tokens()))
    print("t0 done", file=sys.stderr, flush=True)
    for i in range(a.chunks):
        exp.grow(a.turns_per_chunk)
        stages.append(exp.probe_all("grown-%d" % (i + 1), exp.tokens()))
        print("grown-%d done (%dk tok)" % (i + 1, exp.tokens() // 1000), file=sys.stderr, flush=True)
    if not a.no_compact:
        exp.compact()
        stages.append(exp.probe_all("post-compact", exp.tokens()))
        print("post-compact done", file=sys.stderr, flush=True)
    # age_tokens is the window at probe time; patch stages accordingly
    print("\n" + render_table(stages) + "\n\n" + render_curve(stages) + "\n\n" + headline(stages))
    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump({"seed": a.seed, "model": a.model, "stages": stages}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
