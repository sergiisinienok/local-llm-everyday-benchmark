# Local LLM Everyday Benchmark

A personal test suite (97 tests) to check how well a local model (e.g. Qwen 27B on a MacBook) handles everyday tasks, including when the internet is down. Built on [promptfoo](https://www.promptfoo.com).

## Files

| File | What it is |
|---|---|
| `promptfooconfig.yaml` | **Eval 1 - Everyday knowledge (44 tests).** Factual Q&A, writing, reasoning/math, coding, practical tasks, first aid, cooking, home safety, home maintenance, travel, and offline-honesty traps. |
| `promptfooconfig-tools.yaml` | **Eval 2 - Image tools + terminal (31 tests).** Image format conversion and resizing (commands are really executed and the output files checked), terminal tool selection, restraint, safety, follow-up turns. |
| `promptfooconfig-vision.yaml` | **Eval 3 - Vision (22 tests).** Reading text, receipts, screenshots, counting, charts, tables, spatial reasoning, honesty. Vision models only. |
| `assertions.py` | Checking code for Eval 2 (runs the model's image commands in a sandbox folder, verifies results with Pillow, checks tool calls). |
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

## How to read the results

- **Pass rate per metric.** Every test is tagged with a category (`first_aid`, `img_resize`, `counting`, ...). In `promptfoo view`, look at the per-metric scores first to see where the model is strong or weak.
- **Open the failures.** Click a failed cell to see the model's answer and the reason it failed (e.g. "format is JPEG, expected PNG" or "Dangerous call: rm -rf").
- **Weigh categories differently.** There is no universal passing score. Safety categories (`first_aid`, `home_safety`, `tool_safety`) matter most; one wrong answer there outweighs many small misses elsewhere. Read those outputs yourself, don't rely on the judge alone.
- **Check honesty.** `honesty` and `honesty_vision` show whether the model admits what it can't know offline instead of inventing an answer.
- **Check speed.** The view also shows latency per answer. A slightly better but much slower model may be worse for daily use.
- **Treat it as a baseline.** The point is comparison: rerun the same files after changing the model, quantization or settings (e.g. thinking on/off) and compare scores.

Notes: automatic checks can occasionally be too strict or too loose (e.g. a correct answer phrased unexpectedly). If a failure looks unfair, read the answer and adjust that test in the YAML.