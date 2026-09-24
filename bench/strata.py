"""Re-cut recorded run errors along the shape-vs-knowledge case annotations.

Reads `cases/annotations/shape-knowledge.jsonl` (see its README for the rubric) and the
per-case records in `results/*.json`, and prints accuracy strata tables: how each model
fares as semantic twist rises vs as background-knowledge demand rises. No models are run
and no suite is touched — this is pure analysis over recorded numbers.

`uv run python -m bench.strata`
"""

import json
import sys
from pathlib import Path

from bench.cases import TASKS_V1, TASKS_V2

REPO_ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = REPO_ROOT / "cases" / "annotations" / "shape-knowledge.jsonl"

# Runs recorded before the three v2 removals (ec55df4) index cases in pre-lock order:
# the removed case's pre-lock index must be skipped to map onto the locked suites.
PRELOCK_DROP = {"grammar_issue": 5, "commit_intent": 15, "fair_housing_violation": 15}

RUNS = [
  ("Von 1.2", "von-1.2-mps.json", False),
  ("Von 1.1", "von-1.1-mps.json", False),
  ("Von 1.0.1", "historical/v1v2-von.json", True),
  ("Laya-typed", "laya-typed-decisions-mps.json", False),
  ("Laya 0.3.17", "laya-0.3.17-mps.json", False),
  ("GLiNER2", "v1v2-gliner2.json", True),
  ("Jev", "v1v2-jev.json", True),
]

TASK_SUITE = {t.id: "v1" for t in TASKS_V1} | {t.id: "v2" for t in TASKS_V2}
TASK_TYPE = {t.id: t.type for t in TASKS_V1 + TASKS_V2}


def load_annotations() -> dict[str, dict]:
  anns = {}
  for line in ANNOTATIONS.read_text().splitlines():
    if not line.strip():
      continue
    row = json.loads(line)
    anns[row["case_id"]] = row
  return anns


def load_run(path: Path, prelock: bool) -> dict[str, dict]:
  """Case-id -> record, with pre-lock index drift folded back onto locked order."""
  data = json.loads(path.read_text())
  key = next(iter(data))
  out = {}
  for task_id, rows in data[key]["cases"].items():
    suite = TASK_SUITE[task_id]
    drop = PRELOCK_DROP.get(task_id) if prelock else None
    for i, rec in enumerate(rows):
      j = i
      if drop is not None:
        if i == drop:
          continue
        if i > drop:
          j = i - 1
      out[f"{suite}:{task_id}:{j}"] = rec
  return out


def auc(pairs: list[tuple[bool, float]]) -> float | None:
  """Rank-based AUC (Mann-Whitney), ties counted half."""
  pos = [p for y, p in pairs if y]
  neg = [p for y, p in pairs if not y]
  if not pos or not neg:
    return None
  wins = sum((1.0 if yp > yn else 0.5 if yp == yn else 0.0) for yp in pos for yn in neg)
  return wins / (len(pos) * len(neg))


def best_threshold(pairs: list[tuple[bool, float]]) -> tuple[float | None, float | None]:
  """In-sample best cut on P(yes) — an upper bound on post-hoc threshold fitting."""
  if not pairs:
    return None, None
  cands = [i / 100 for i in range(1, 100)]
  best = max(cands, key=lambda t: sum((p >= t) == y for y, p in pairs))
  best_acc = sum((p >= best) == y for y, p in pairs) / len(pairs)
  return best, best_acc


def acc(rows: list[dict], model: str) -> str:
  vals = [r[model] for r in rows if r[model] is not None]
  return f"{sum(vals) / len(vals):.3f} ({sum(vals)}/{len(vals)})" if vals else "—"


def table(rows: list[dict], models: list[str], group, levels: list, title: str) -> None:
  print(f"\n### {title}\n")
  print("| stratum | n | " + " | ".join(models) + " |")
  print("|---|---|" + "---|" * len(models))
  for lvl in levels:
    sub = [r for r in rows if group(r) == lvl]
    print(f"| {lvl} | {len(sub)} | " + " | ".join(acc(sub, m) for m in models) + " |")


def main() -> None:
  anns = load_annotations()
  # Optional substring filters keep wide tables readable: bench.strata von jev
  selected = [r for r in RUNS if not sys.argv[1:] or any(s.lower() in r[0].lower() for s in sys.argv[1:])]
  models = []
  runs = {}
  for name, fname, prelock in selected:
    models.append(name)
    runs[name] = load_run(REPO_ROOT / "results" / fname, prelock)

  rows = []
  for cid, ann in sorted(anns.items()):
    row = {
      "cid": cid,
      "suite": cid.split(":")[0],
      "task": cid.split(":")[1],
      "type": TASK_TYPE[cid.split(":")[1]],
      "twist": ann["twist"],
      "knowledge": ann["knowledge"],
      "tags": ann["tags"],
      "crux": ann["crux"],
      "unreachable": ann["unreachable"],
    }
    for name in models:
      rec = runs[name].get(cid)
      row[name] = None if rec is None or rec["correct"] is None else rec["correct"]
    rows.append(row)
  missing = [r["cid"] for r in rows if any(r[m] is None for m in models)]
  print(f"cases: {len(rows)}  (no record somewhere: {len(missing)})")

  print("\n## Annotation distribution\n")
  for axis in ("twist", "knowledge", "crux"):
    counts = {v: sum(1 for r in rows if r[axis] == v) for v in sorted({r[axis] for r in rows})}
    print(f"- {axis}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
  tags = {}
  for r in rows:
    for t in r["tags"]:
      tags[t] = tags.get(t, 0) + 1
  print("- tags: " + ", ".join(f"{k}={v}" for k, v in sorted(tags.items(), key=lambda kv: -kv[1])))
  print(f"- unreachable: {sum(1 for r in rows if r['unreachable'])}")
  print("\n| twist \\ knowledge | 0 | 1 | 2 | 3 |")
  print("|---|---|---|---|---|")
  for t in (0, 1, 2, 3):
    cells = [sum(1 for r in rows if r["twist"] == t and r["knowledge"] == k) for k in (0, 1, 2, 3)]
    print(f"| {t} | " + " | ".join(str(c) for c in cells) + " |")

  table(rows, models, lambda r: r["twist"], [0, 1, 2, 3], "Accuracy by twist")
  table(rows, models, lambda r: r["knowledge"], [0, 1, 2, 3], "Accuracy by knowledge")

  quad = lambda r: ("K low" if r["knowledge"] <= 1 else "K high") + " × " + ("T low" if r["twist"] <= 1 else "T high")
  table(rows, models, quad, ["K low × T low", "K low × T high", "K high × T low", "K high × T high"],
        "Quadrants (low = 0–1, high = 2–3)")

  for typ in ("choice", "noul", "score"):
    table([r for r in rows if r["type"] == typ], models, lambda r: r["twist"], [0, 1, 2, 3], f"Accuracy by twist — {typ}")

  print("\n### noul: ordering vs threshold\n")
  print("| model | AUC | acc @0.5 | best global cut | acc @best | best per-task cut (in-sample) |")
  print("|---|---|---|---|---|---|")
  for name in models:
    pairs = []
    tasks: dict[str, list] = {}
    for r in rows:
      rec = runs[name].get(r["cid"])
      if r["type"] == "noul" and rec is not None and rec["probability"] is not None:
        pair = (rec["expected"] == "yes", rec["probability"])
        pairs.append(pair)
        tasks.setdefault(r["task"], []).append(pair)
    t, _ = best_threshold(pairs)
    acc05 = sum((p >= 0.5) == y for y, p in pairs) / len(pairs)
    acct = sum((p >= t) == y for y, p in pairs) / len(pairs)
    per_task = sum(max(sum((p >= tt) == y for y, p in tp) for tt in (i / 100 for i in range(1, 100))) for tp in tasks.values()) / len(pairs)
    print(f"| {name} | {auc(pairs):.3f} | {acc05:.3f} | {t:.2f} | {acct:.3f} | {per_task:.3f} |")

  print("\n### score: MAE by twist\n")
  print("| model | all | T 0–1 | T 2–3 |")
  print("|---|---|---|---|---|")
  for name in models:
    def mae(sub):
      errs = []
      for r in sub:
        rec = runs[name].get(r["cid"])
        if r["type"] == "score" and rec is not None and rec["correct"] is not None:
          errs.append(abs(int(rec["predicted"]) - int(rec["expected"])))
      return f"{sum(errs) / len(errs):.2f} (n={len(errs)})" if errs else "—"
    lo = [r for r in rows if r["twist"] <= 1]
    hi = [r for r in rows if r["twist"] >= 2]
    print(f"| {name} | {mae(rows)} | {mae(lo)} | {mae(hi)} |")

  print("\n### Where each model's errors live\n")
  print("| model | errors | in T≥2 | in K≥2 | in K low × T high | unreachable cases wrong |")
  print("|---|---|---|---|---|---|")
  for name in models:
    errs = [r for r in rows if r[name] is False]
    if not errs:
      continue
    frac = lambda f: f"{sum(1 for r in errs if f(r)) / len(errs):.2f}"
    unr = [r for r in rows if r["unreachable"]]
    unwrong = sum(1 for r in unr if r[name] is False)
    print(f"| {name} | {len(errs)} | {frac(lambda r: r['twist'] >= 2)} | {frac(lambda r: r['knowledge'] >= 2)} "
          f"| {frac(lambda r: r['twist'] >= 2 and r['knowledge'] <= 1)} | {unwrong}/{len(unr)} |")

  ok = [r for r in rows if not r["unreachable"]]
  table(ok, models, quad, ["K low × T low", "K low × T high", "K high × T low", "K high × T high"],
        "Quadrants, unreachable cases excluded")


if __name__ == "__main__":
  main()