#!/usr/bin/env python3
"""Compare saved benchmark results (from run_all.sh) across models / settings.

Usage:  python3 compare.py [results_dir] [label ...]
  results_dir  default: results
  label        optional: only these runs (default: all labels found)

Reads <label>-evalN-<name>.json files and prints, per eval, the pass rate of each
metric (category) per label, plus the overall test pass rate and median latency.
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

PAT = re.compile(r"^(?P<label>.+)-eval(?P<n>[123])-(?P<name>[a-z]+)\.json$")
TITLES = {"1": "Eval 1 - Everyday knowledge", "2": "Eval 2 - Image tools + terminal", "3": "Eval 3 - Vision"}


def load(path):
    rs = json.loads(path.read_text())["results"]["results"]
    metrics = defaultdict(lambda: [0, 0])
    for r in rs:
        for c in (r.get("gradingResult") or {}).get("componentResults", []):
            m = (c.get("assertion") or {}).get("metric") or "(no metric)"
            metrics[m][1] += 1
            metrics[m][0] += bool(c.get("pass"))
    tests_ok = sum(bool(r.get("success")) for r in rs)
    errors = sum(1 for r in rs if (r.get("failureReason") == 2) or ((r.get("error") or "") and not r.get("gradingResult")))
    lat = [r["latencyMs"] for r in rs if r.get("latencyMs")]
    return {
        "metrics": metrics,
        "tests": (tests_ok, len(rs)),
        "errors": errors,
        "latency": statistics.median(lat) / 1000 if lat else None,
    }


def pct(p, t):
    return "-" if not t else f"{p}/{t} ({100 * p / t:.0f}%)"


def main():
    args = sys.argv[1:]
    root = Path(args[0]) if args else Path("results")
    only = set(args[1:])
    data = defaultdict(dict)  # eval n -> label -> result
    for f in sorted(root.glob("*.json")):
        m = PAT.match(f.name)
        if not m or (only and m["label"] not in only):
            continue
        data[m["n"]][m["label"]] = load(f)
    if not data:
        sys.exit(f"No result files like <label>-eval1-everyday.json in {root}/")

    for n in sorted(data):
        labels = sorted(data[n])
        metrics = sorted({m for l in labels for m in data[n][l]["metrics"]})
        rows = [["metric"] + labels]
        for m in metrics:
            rows.append([m] + [pct(*data[n][l]["metrics"][m]) if m in data[n][l]["metrics"] else "-" for l in labels])
        rows.append(["ALL TESTS"] + [pct(*data[n][l]["tests"]) for l in labels])
        rows.append(["median latency"] + [f"{data[n][l]['latency']:.1f}s" if data[n][l]["latency"] else "-" for l in labels])
        if any(data[n][l]["errors"] for l in labels):
            rows.append(["errored tests"] + [str(data[n][l]["errors"]) for l in labels])
        w = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
        print(f"\n{TITLES[n]}")
        for i, r in enumerate(rows):
            print("  " + "  ".join(c.ljust(w[j]) for j, c in enumerate(r)))
            if i == 0:
                print("  " + "  ".join("-" * x for x in w))
    print()


if __name__ == "__main__":
    main()
