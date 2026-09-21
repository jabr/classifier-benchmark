"""Harness: run benchmark tasks against classification model backends."""

import argparse
import json
import math
import time
from pathlib import Path

from bench.backends import create_backend
from bench.cases import Case, Task
from bench.suites import SUITES, resolve_suites, suite_plan


def percentile(values: list[float], pct: float) -> float:
  ordered = sorted(values)
  idx = min(len(ordered) - 1, math.ceil(pct / 100 * len(ordered)) - 1)
  return ordered[idx]


def rank_auc(pairs: list[tuple[bool, float]]) -> float | None:
  golds = [g for g, _ in pairs]
  positives = sum(1 for g in golds if g)
  negatives = len(golds) - positives
  if not positives or not negatives:
    return None
  ranked = sorted(pairs, key=lambda p: p[1])
  i = 0
  rank_sum = 0.0
  while i < len(ranked):
    j = i
    while j + 1 < len(ranked) and ranked[j + 1][1] == ranked[i][1]:
      j += 1
    avg_rank = (i + j) / 2 + 1
    for k in range(i, j + 1):
      if ranked[k][0]:
        rank_sum += avg_rank
    i = j + 1
  return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def expected_label(task: Task, case: Case) -> str:
  if task.type == "noul":
    return "yes" if case.expected else "no"
  return str(case.expected)


def run_case(task: Task, case: Case, backend) -> dict:
  t0 = time.perf_counter()
  predicted = probability = confidence = None
  probabilities = None
  error = None
  try:
    if task.type == "choice":
      pred = backend.predict_choice(case.state, task.question)
    elif task.type == "noul":
      pred = backend.predict_noul(case.state, task.question)
    elif task.type == "score":
      pred = backend.predict_score(case.state, task.question)
    else:
      raise ValueError(f"Unknown task type {task.type}")
    predicted = pred.label
    probability = pred.probability
    probabilities = pred.probabilities
    confidence = pred.confidence
  except Exception as exc:
    error = f"{type(exc).__name__}: {exc}"
  latency_ms = (time.perf_counter() - t0) * 1000

  expected = expected_label(task, case)
  correct = None if error else (predicted == expected)
  return {
    "expected": expected,
    "predicted": predicted,
    "correct": correct,
    "probability": probability,
    "probabilities": probabilities,
    "confidence": confidence,
    "latency_ms": latency_ms,
    "error": error,
  }


def summarize_task(task: Task, rows: list[dict]) -> dict:
  scored = [r for r in rows if r["error"] is None]
  errors = [r for r in rows if r["error"] is not None]
  correct = sum(1 for r in scored if r["correct"])
  latencies = [r["latency_ms"] for r in rows]

  summary = {
    "type": task.type,
    "n": len(rows),
    "errors": len(errors),
    "correct": correct,
    "accuracy": correct / len(scored) if scored else None,
    "latency_ms_mean": sum(latencies) / len(latencies) if latencies else None,
    "latency_ms_p95": percentile(latencies, 95) if latencies else None,
    "extra": {},
  }

  if task.type == "noul" and scored:
    pairs = [(c.expected, r["probability"]) for c, r in zip(task.cases, rows) if r["error"] is None]
    abs_errors = [abs(r["probability"] - (1.0 if c.expected else 0.0)) for c, r in zip(task.cases, rows) if r["error"] is None]
    summary["extra"] = {
      "auc": rank_auc(pairs),
      "mean_prob_abs_error": sum(abs_errors) / len(abs_errors) if abs_errors else None,
    }
  elif task.type == "score" and scored:
    abs_diffs = []
    within_one = 0
    for c, r in zip(task.cases, rows):
      if r["error"] is not None:
        continue
      try:
        pred_level = int(float(r["predicted"]))
      except (TypeError, ValueError):
        continue
      diff = abs(pred_level - int(c.expected))
      abs_diffs.append(diff)
      within_one += 1 if diff <= 1 else 0
    if abs_diffs:
      summary["extra"] = {
        "mae_levels": sum(abs_diffs) / len(abs_diffs),
        "within_1": within_one / len(abs_diffs),
      }
  return summary


def evaluate_task(task: Task, backend) -> tuple[list[dict], dict]:
  rows = [run_case(task, case, backend) for case in task.cases]
  return rows, summarize_task(task, rows)


def print_task_line(task_id: str, summary: dict) -> None:
  acc = f"{summary['accuracy']:.3f}" if summary["accuracy"] is not None else "n/a"
  mean = f"{summary['latency_ms_mean']:.1f}ms" if summary["latency_ms_mean"] is not None else "?"
  p95 = f"{summary['latency_ms_p95']:.1f}ms" if summary["latency_ms_p95"] is not None else "?"
  extras = ""
  for key, value in summary.get("extra", {}).items():
    if value is not None:
      extras += f"  {key}={value:.3f}"
  err = f"  errors={summary['errors']}" if summary["errors"] else ""
  print(
    f"  {task_id:<20} {summary['type']:<6} n={summary['n']:<3} "
    f"acc={acc}  lat mean={mean}  p95={p95}{extras}{err}"
  )


def aggregate(rows: list[dict], summaries: list[dict]) -> dict:
  scored = [r for r in rows if r["error"] is None]
  correct = sum(1 for r in scored if r["correct"])
  micro = correct / len(scored) if scored else None
  macro_values = [s["accuracy"] for s in summaries if s["accuracy"] is not None]
  macro = sum(macro_values) / len(macro_values) if macro_values else None
  return {
    "micro_accuracy": micro,
    "macro_accuracy": macro,
    "n": len(rows),
    "errors": sum(s["errors"] for s in summaries),
  }


def print_suite_line(name: str, totals: dict) -> None:
  micro = f"{totals['micro_accuracy']:.3f}" if totals["micro_accuracy"] is not None else "n/a"
  macro = f"{totals['macro_accuracy']:.3f}" if totals["macro_accuracy"] is not None else "n/a"
  err = f"  ERRORS={totals['errors']}" if totals["errors"] else ""
  print(f"  suite {name}: n={totals['n']}  micro_acc={micro}  macro_acc={macro}{err}")


def evaluate_backend(
  backend_name: str,
  plan: list[tuple[str, list[Task]]],
  backend_kwargs: dict,
) -> dict:
  print(f"=== backend: {backend_name} ===")
  t0 = time.perf_counter()
  backend = create_backend(backend_name, **backend_kwargs)
  try:
    load_seconds = backend.warmup()
    print(f"  warmup: {load_seconds:.1f}s  ({backend.description})")
  except Exception as exc:
    print(f"  warmup FAILED: {exc}")
    return {"backend": backend_name, "failed": str(exc)}

  results = {
    "backend": backend_name,
    "description": backend.description,
    "suites": [name for name, _ in plan],
    "tasks": {},
    "cases": {},
    "suite_summaries": {},
  }
  total_rows = []
  total_summaries = []
  for suite_name, suite_tasks in plan:
    n_cases = sum(len(t.cases) for t in suite_tasks)
    print(f"-- suite {suite_name}: {len(suite_tasks)} task(s) / {n_cases} case(s) --")
    suite_rows = []
    suite_summaries = []
    for task in suite_tasks:
      rows, summary = evaluate_task(task, backend)
      summary = {"suite": suite_name, **summary}
      results["tasks"][task.id] = summary
      results["cases"][task.id] = rows
      suite_rows.extend(rows)
      suite_summaries.append(summary)
      print_task_line(task.id, summary)
    suite_totals = aggregate(suite_rows, suite_summaries)
    results["suite_summaries"][suite_name] = suite_totals
    print_suite_line(suite_name, suite_totals)
    total_rows.extend(suite_rows)
    total_summaries.extend(suite_summaries)

  totals = aggregate(total_rows, total_summaries)
  wall = time.perf_counter() - t0
  totals["wall_seconds"] = wall
  results["summary"] = totals
  micro_str = f"{totals['micro_accuracy']:.3f}" if totals["micro_accuracy"] is not None else "n/a"
  macro_str = f"{totals['macro_accuracy']:.3f}" if totals["macro_accuracy"] is not None else "n/a"
  print(
    f"  TOTAL: n={totals['n']}  micro_acc={micro_str}  macro_acc={macro_str}"
    f"  wall={wall:.1f}s"
    + (f"  ERRORS={totals['errors']}" if totals["errors"] else "")
  )
  return results


def main() -> None:
  parser = argparse.ArgumentParser(description="Run classification benchmarks.")
  parser.add_argument("--backend", default="von", help="Comma-separated: von, jev, gliner2, laya")
  parser.add_argument("--suite", default=None, help="Core suite(s) to run: v1, v2, comma-separated, or 'all' (default when --sample is not given)")
  parser.add_argument("--sample", default=None, help="Generated sample suite(s) to run: name (e.g. cfpb-bbee), comma-separated, or 'all' (every discovered sample)")
  parser.add_argument("--tasks", default="", help="Comma-separated task ids within the selected suites (default: all)")
  parser.add_argument("--limit", type=int, default=None, help="Limit cases per task")
  parser.add_argument("--device", default=None, help="Device for local backends (e.g. mps, cuda, cpu)")
  parser.add_argument("--model", default=None, help="Model id (jev: OpenRouter model id)")
  parser.add_argument("--gliner2-path", default=None, help="Path to gliner2 weights")
  parser.add_argument("--von-path", default=None, help="Path to von weights (or registry alias)")
  parser.add_argument("--laya-path", default=None, help="Path to laya weights (or HF repo id)")
  parser.add_argument("--out", default=None, help="Write JSON results to this path")
  args = parser.parse_args()

  suite_names = []
  if args.suite or not args.sample:
    suite_names += resolve_suites(args.suite or "all")
  if args.sample:
    suite_names += resolve_samples(args.sample)
  task_ids = [t.strip() for t in args.tasks.split(",") if t.strip()]
  plan = suite_plan(suite_names, task_ids)
  if args.limit:
    plan = [
      (name, [Task(id=t.id, type=t.type, question=t.question, cases=t.cases[: args.limit]) for t in tasks])
      for name, tasks in plan
    ]

  all_results = {}
  for backend_name in [b.strip() for b in args.backend.split(",") if b.strip()]:
    kwargs = {}
    if args.device and backend_name in ("von", "gliner2", "laya"):
      kwargs["device"] = args.device
    if args.model and backend_name == "jev":
      kwargs["model"] = args.model
    if args.gliner2_path and backend_name == "gliner2":
      kwargs["model_path"] = args.gliner2_path
    if args.von_path and backend_name == "von":
      kwargs["model_path"] = args.von_path
    if args.laya_path and backend_name == "laya":
      kwargs["model_path"] = args.laya_path
    all_results[backend_name] = evaluate_backend(backend_name, plan, kwargs)

  if args.out:
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nWrote results to {out_path}")


if __name__ == "__main__":
  main()
