---
name: run-eval
description: Runs the RAGAS evaluation suite (evaluation/ragas_eval.py), saves a timestamped JSON result to evaluation/results/, and prints a before/after comparison table against the previous saved run. Use when asked to evaluate, run eval, or check RAGAS scores.
---

# Run evaluation

1. Run `python evaluation/ragas_eval.py` from the repo root and capture its stdout. The script is expected to print a single JSON object of metric name -> score (e.g. `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`).
   - If the script writes its results to a file instead of stdout, read that file's JSON instead.
   - If the script fails to run (missing dependency, missing `GROQ_API_KEY`, etc.), stop and report the error — do not fabricate results.

2. Before saving, list the existing files in `evaluation/results/` (create the directory if it doesn't exist) and note the most recent one by filename/timestamp — this is the "before" run for the comparison. If none exist, there is no "before" run.

3. Save the new result as `evaluation/results/<UTC timestamp, format YYYYMMDD-HHMMSS>.json`, containing the raw metrics JSON from step 1.

4. Print a comparison table with one row per metric, showing the previous run's score, the new run's score, and the delta (new - previous), e.g.:

   | Metric | Previous | Current | Delta |
   |---|---|---|---|
   | faithfulness | 0.812 | 0.845 | +0.033 |
   | answer_relevancy | 0.77 | 0.76 | -0.010 |

   If there was no previous run, print the new scores alone with a note that this is the first recorded run.

5. If a metric appears in one run but not the other, show it with `-` in the missing column rather than omitting the row.
