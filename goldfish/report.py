"""Report rendering: table + ASCII forgetting curve + shareable one-liner."""


def render_table(stages):
    lines = ["stage              age_tokens  window  compactions  retention",
             "-----              ----------  ------  -----------  ---------"]
    for s in stages:
        lines.append("%-16s  %9d  %6d  %11d  %6.1f%%" % (
            s["stage"], s["age_tokens"], s["window_tokens"], s["compactions"],
            s["retention"] * 100))
    return "\n".join(lines)


def render_curve(stages, width=40):
    lines = ["retention", "100% " + "|" if False else "100% |"]
    for s in stages:
        bar = "#" * max(0, min(width, int(round(s["retention"] * width))))
        lines.append("%5.0f%% |%-*s %s (%dk tok)" % (
            s["retention"] * 100, width, bar, s["stage"], s["window_tokens"] // 1000))
    lines.append("      +" + "-" * width + "---- age ->")
    return "\n".join(lines)


def headline(stages):
    """The shareable sentence."""
    worst = min(stages, key=lambda s: s["retention"])
    return "goldfish: your agent retains %.0f%% of injected facts at its %s stage " \
           "(%d canaries, %d compaction events)." % (
        worst["retention"] * 100, worst["stage"], len(worst["results"]),
        worst["compactions"])
