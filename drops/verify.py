"""Independent re-score of goldfish run JSONs.
Recomputes retained = (value in answer) per probe and retention per stage,
compares against the in-tool numbers, prints a table + per-file sha256.
Usage: python verify.py run-*.json
"""
import hashlib
import json
import sys

def verify(path):
    raw = open(path, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    d = json.loads(raw)
    rows, mismatches = [], 0
    for st in d["stages"]:
        recomputed = 0.0
        for r in st["results"]:
            ans = r.get("answer") or ""
            if r["canary"] == "forbidden":
                # compliance probe: retained means the word did NOT appear
                got = 0.0 if r["value"] in ans.lower() else 1.0
            else:
                got = 1.0 if r["value"] in ans else 0.0
            if got != r["retained"]:
                mismatches += 1
            recomputed += got
        recomputed /= max(1, len(st["results"]))
        agree = abs(recomputed - st["retention"]) < 1e-9
        rows.append((st["stage"], st["age_tokens"], st["compactions"],
                     st["retention"], recomputed, agree))
    print(f"== {path}  seed={d.get('seed')} model={d.get('model')}")
    print(f"   sha256={sha[:16]}…  probes={sum(len(s['results']) for s in d['stages'])}  scorer-mismatches={mismatches}")
    for stage, age, comp, tool, rec, agree in rows:
        flag = "OK " if agree else "MISMATCH"
        print(f"   {stage:14s} {age:7d}tok comp={comp}  tool={tool:5.1%}  recomputed={rec:5.1%}  {flag}")
    return rows, mismatches

if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        _, m = verify(p)
        bad += m
    sys.exit(1 if bad else 0)
