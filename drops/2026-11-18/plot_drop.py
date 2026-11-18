"""Render drop-1 retention curves from verified run JSONs. Output: drop1-curve.png"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEEDS = [1337, 4242, 9001]
STAGES = ["t0-fresh", "grown-1", "grown-2", "grown-3", "grown-4", "post-compact"]
LABELS = ["fresh\n(0.5k)", "19k tok", "38k tok", "57k tok", "76k tok", "1 COMPACTION\n(6.4k tok)"]

fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200)
fig.patch.set_facecolor("#0d1117")
ax.set_facecolor("#0d1117")

for i, s in enumerate(SEEDS):
    d = json.load(open(f"run-{s}.json"))
    ret = [next(st for st in d["stages"] if st["stage"] == name)["retention"] * 100 for name in STAGES]
    x = list(range(len(STAGES)))
    color = ["#58a6ff", "#3fb950", "#f85149"][i]
    ax.plot(x, ret, marker="o", color=color, linewidth=2, markersize=6, label=f"seed {s}")
    for xi, yi in zip(x[:-1], ret[:-1]):
        if yi < 100:
            ax.annotate(f"{yi:.0f}%", (xi, yi), textcoords="offset points", xytext=(0, 8),
                        fontsize=8, color=color)

ax.axvspan(4.5, 5.5, color="#f85149", alpha=0.08)
ax.text(5.0, 50, "the cliff", ha="center", fontsize=11, color="#f85149", style="italic")
ax.set_xticks(range(len(STAGES)))
ax.set_xticklabels(LABELS, fontsize=9, color="#c9d1d9")
ax.set_ylim(-3, 108)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=9, color="#c9d1d9")
ax.set_ylabel("canary retention", color="#c9d1d9", fontsize=10)
ax.set_title("goldfish: what survives one compaction\nQwen3.8-Flash-Next (production bot-farm stack) · 14 probes · 3 seeds · 2026-11-18",
             color="#e6edf3", fontsize=12, loc="left")
for spine in ax.spines.values():
    spine.set_color("#30363d")
ax.tick_params(colors="#c9d1d9")
ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=9)
ax.grid(axis="y", color="#21262d", linewidth=0.6)
fig.text(0.99, 0.01, "goldfish · reproducible: python -m goldfish.cli --seed <s> · hashes in repo drops/2026-11-18/",
         ha="right", fontsize=7, color="#8b949e")
plt.tight_layout()
plt.savefig("drop1-curve.png", facecolor="#0d1117")
print("wrote drop1-curve.png")
