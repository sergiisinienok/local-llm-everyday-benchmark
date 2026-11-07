#!/usr/bin/env bash
# Run the benchmark evals and save each result to results/<label>-evalN-<name>.json
#
# Usage:  ./run_all.sh <label> [evals]
#   label  names this run: model + the settings that matter, e.g. qwen3.8-27b-think-off
#   evals  optional comma list, default 1,2,3 (e.g. "2,3" skips the judge-graded Eval 1)
#
# Examples:
#   ./run_all.sh qwen3.8-27b-think-off
#   ./run_all.sh qwen3.8-27b-think-on 1
#   RESULTS_DIR=/tmp/r ./run_all.sh test 3
#
# Always runs with --no-cache so numbers come from fresh model answers.
# Eval 1 needs the cloud judge (see README); Evals 2 and 3 are fully offline.
set -euo pipefail
cd "$(dirname "$0")"

label="${1:-}"
[[ -n "$label" ]] || { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
[[ "$label" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "label may only contain letters, digits, . _ -"; exit 1; }
evals="${2:-1,2,3}"
out="${RESULTS_DIR:-results}"
mkdir -p "$out"

# (case statements instead of associative arrays: macOS ships bash 3.2)
cfg_for()  { case "$1" in 1) echo promptfooconfig.yaml;; 2) echo promptfooconfig-tools.yaml;; 3) echo promptfooconfig-vision.yaml;; esac; }
name_for() { case "$1" in 1) echo everyday;; 2) echo tools;; 3) echo vision;; esac; }

IFS=',' read -ra list <<< "$evals"
for n in "${list[@]}"; do
  cfg="$(cfg_for "$n")"
  [[ -n "$cfg" ]] || { echo "unknown eval '$n' (use 1, 2 or 3)"; exit 1; }
  f="$out/$label-eval$n-$(name_for "$n").json"
  echo "=== Eval $n ($cfg) -> $f"
  # promptfoo exits non-zero when some tests fail; that is normal for a benchmark.
  npx promptfoo@latest eval -c "$cfg" --no-cache --no-progress-bar -o "$f" || true
  [[ -s "$f" ]] || { echo "no result file written for eval $n"; exit 1; }
done

echo
python3 -I compare.py "$out"
