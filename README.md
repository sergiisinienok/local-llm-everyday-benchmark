# Local LLM Everyday Benchmark

A personal test suite (97 tests) to check how well a local model (e.g. Qwen 27B on a MacBook) handles everyday tasks, including when the internet is down. Built on [promptfoo](https://www.promptfoo.com).

## Files

| File | What it is |
|---|---|
| `promptfooconfig.yaml` | **Eval 1 - Everyday knowledge (44 tests).** Factual Q&A, writing, reasoning/math, coding, practical tasks, first aid, cooking, home safety, home maintenance, travel, and offline-honesty traps. |
| `promptfooconfig-tools.yaml` | **Eval 2 - Image tools + terminal (31 tests).** Image format conversion and resizing (commands are really executed and the output files checked), terminal tool selection, restraint, safety, follow-up turns. |
| `promptfooconfig-vision.yaml` | **Eval 3 - Vision (22 tests).** Reading text, receipts, screenshots, counting, charts, tables, spatial reasoning, honesty. Vision models only. |
| `assertions.py` | Checking code for Eval 2 (runs the model's image commands in a sandbox folder, verifies results with Pillow, checks tool calls). |
| `run_all.sh` | Runs the evals and saves each result to `results/` (see *Saving and comparing results*). |
| `compare.py` | Prints one table comparing saved results across models / settings. |
| `results/` | Saved result files, one per model, setting and eval. |
| `make_vision_fixtures.py` | Generates the test images for Eval 3 (answers are known exactly). |
| `fixtures/` | *Auto-created* on first run of Eval 2 (test photos to convert/resize). |
| `fixtures_vision/` | *Created by* `make_vision_fixtures.py` (images for Eval 3). |
| `README.md` | This file. |

Keep all files in the same folder and run commands from it.

## Setup (once)

```bash
brew install ollama node imagemagick webp ffmpeg   # sips is built into macOS
pip3 install pillow
ollama pull <your-model-tag>                       # check the exact tag: ollama list
python3 make_vision_fixtures.py                    # only needed for Eval 3
```

In each `.yaml`, replace the model id (`qwen3.8:27b`) with your exact tag. Eval 3 needs a **vision** build of the model.

Eval 1 uses a cloud model (Claude) as judge for open-ended answers, so **you need a working Claude Code session** (Claude Code installed and logged in on this machine) for the judging to work. Without it the `llm-rubric` checks fail. Alternatively, set `export ANTHROPIC_API_KEY=...` or change the judge in `defaultTest` to a local model. Evals 2 and 3 need no internet and no judge.

## Run

```bash
npx promptfoo@latest eval -c promptfooconfig.yaml          # Eval 1
npx promptfoo@latest eval -c promptfooconfig-tools.yaml    # Eval 2
npx promptfoo@latest eval -c promptfooconfig-vision.yaml   # Eval 3
npx promptfoo@latest view                                  # open results in the browser
```

**Testing truly offline:** turn Wi-Fi off and run Evals 2 and 3 as they are. For Eval 1, run it offline and save the outputs (`-o results.json`), then grade when back online.

## Saving and comparing results

Use `run_all.sh` to run the evals and keep the results, so you can compare other models later.

```bash
./run_all.sh qwen3.8-27b-think-off        # runs Evals 1, 2 and 3
./run_all.sh qwen3.8-27b-think-on 1       # only the evals you list (comma list, e.g. 2,3)
python3 compare.py                        # table of everything in results/
python3 compare.py results modelA modelB  # only these labels
```

- **The label** names the run: model plus the settings that matter (`think-off`, quantization, ...). It becomes part of the file name: `results/<label>-eval1-everyday.json`, `-eval2-tools.json`, `-eval3-vision.json`. Use only letters, digits, `.`, `_` and `-`.
- **Fresh answers:** the script always runs with `--no-cache`, so numbers come from new model answers, not cached ones. Eval 1 takes about 8 min with thinking off; Evals 2 and 3 about 1 min each.
- **Eval 1 needs the cloud judge** (see Setup). To skip it, run `./run_all.sh <label> 2,3`.
- **Failed tests are normal**, so the script carries on and saves the results anyway.
- **`compare.py`** prints one table per eval: a row per metric, a column per label, then the overall pass rate and the median latency per answer. Give each run its own label and they appear side by side.

**Comparing another model**
1. Change the model id in all three `.yaml` files (provider `id`, and the `description` if you like).
2. Run `./run_all.sh <new-label>`.
3. Run `python3 compare.py`.

Or add a second entry under `providers:` in a `.yaml` and use `promptfoo view` to see both models in columns.

**Reading the comparison fairly**
- Model answers differ from run to run, so one test either way can be noise. Look at the per-metric rows, or run each model more than once.
- Eval 1 depends on the Claude judge, so scores from different dates are not perfectly comparable. Evals 2 and 3 are graded by code (no judge), so the grading itself is deterministic, but the model's answers still vary between runs.
- Compare like with like: the same thinking setting and the same configs. Thinking on/off changes the results a lot (see the comments in the provider block of each `.yaml`).
- Commit `results/` together with the configs so each result is tied to the test files that produced it.

## How to read the results

- **Pass rate per metric.** Every test is tagged with a category (`first_aid`, `img_resize`, `counting`, ...). In `promptfoo view`, look at the per-metric scores first to see where the model is strong or weak.
- **Open the failures.** Click a failed cell to see the model's answer and the reason it failed (e.g. "format is JPEG, expected PNG" or "Dangerous call: rm -rf").
- **Weigh categories differently.** There is no universal passing score. Safety categories (`first_aid`, `home_safety`, `tool_safety`) matter most; one wrong answer there outweighs many small misses elsewhere. Read those outputs yourself, don't rely on the judge alone.
- **Check honesty.** `honesty` and `honesty_vision` show whether the model admits what it can't know offline instead of inventing an answer.
- **Check speed.** The view also shows latency per answer. A slightly better but much slower model may be worse for daily use.
- **Treat it as a baseline.** The point is comparison: rerun the same files after changing the model, quantization or settings (e.g. thinking on/off) and compare scores.

Notes: automatic checks can occasionally be too strict or too loose (e.g. a correct answer phrased unexpectedly). If a failure looks unfair, read the answer and adjust that test in the YAML.