"""Harness: run benchmark tasks against classification model backends."""

import argparse
import json
import math
import time
from pathlib import Path

from bench.backends import create_backend
from bench.cases import Case, Task, tasks_by_ids


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


def evaluate_backend(
  backend_name: str,
  tasks: list[Task],
  backend_kwargs: dict,
  save_errors: bool = False,
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

  results = {"backend": backend_name, "description": backend.description, "tasks": {}, "cases": {}}
  total_rows = []
  summaries = []
  for task in tasks:
    rows, summary = evaluate_task(task, backend)
    results["tasks"][task.id] = summary
    results["cases"][task.id] = rows
    total_rows.extend(rows)
    summaries.append(summary)
    print_task_line(task.id, summary)

  scored = [r for r in total_rows if r["error"] is None]
  correct = sum(1 for r in scored if r["correct"])
  micro = correct / len(scored) if scored else None
  macro_values = [s["accuracy"] for s in summaries if s["accuracy"] is not None]
  macro = sum(macro_values) / len(macro_values) if macro_values else None
  wall = time.perf_counter() - t0
  total_errors = sum(s["errors"] for s in summaries)

  summary = {
    "micro_accuracy": micro,
    "macro_accuracy": macro,
    "n": len(total_rows),
    "errors": total_errors,
    "wall_seconds": wall,
  }
  results["summary"] = summary
  micro_str = f"{micro:.3f}" if micro is not None else "n/a"
  macro_str = f"{macro:.3f}" if macro is not None else "n/a"
  print(
    f"  TOTAL: n={summary['n']}  micro_acc={micro_str}  macro_acc={macro_str}"
    f"  wall={wall:.1f}s"
    + (f"  ERRORS={total_errors}" if total_errors else "")
  )
  return results


def main() -> None:
  parser = argparse.ArgumentParser(description="Run classification benchmarks.")
  parser.add_argument("--backend", default="von", help="Comma-separated: von, jev, gliner2")
  parser.add_argument("--tasks", default="", help="Comma-separated task ids (default: all)")
  parser.add_argument("--limit", type=int, default=None, help="Limit cases per task")
  parser.add_argument("--device", default=None, help="Device for local backends (e.g. mps, cuda, cpu)")
  parser.add_argument("--model", default=None, help="Model id (jev: OpenRouter model id)")
  parser.add_argument("--gliner2-path", default=None, help="Path to gliner2 weights")
  parser.add_argument("--out", default=None, help="Write JSON results to this path")
  args = parser.parse_args()

  tasks = tasks_by_ids([t for t in args.tasks.split(",") if t])
  if args.limit:
    tasks = [
      Task(id=t.id, type=t.type, question=t.question, cases=t.cases[: args.limit])
      for t in tasks
    ]

  all_results = {}
  for backend_name in [b.strip() for b in args.backend.split(",") if b.strip()]:
    kwargs = {}
    if args.device:
      kwargs["device"] = args.device
    if args.model and backend_name == "jev":
      kwargs["model"] = args.model
    if args.gliner2_path and backend_name == "gliner2":
      kwargs["model_path"] = args.gliner2_path
    all_results[backend_name] = evaluate_backend(backend_name, tasks, kwargs)

  if args.out:
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nWrote results to {out_path}")


if __name__ == "__main__":
  main()
