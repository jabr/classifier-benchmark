"""Validate suite data files, cross-suite invariants, and locked content hashes.

Run via `just validate` (or `uv run python -m bench.validate`). Checks:
  - suite TOMLs parse and satisfy the schema (runs on import of bench.cases)
  - task ids unique across suites; questions of tasks that declare `extends`
    deep-equal their target (runs on import of bench.suites)
  - every suite with an entry in cases/hashes.json still matches it

Suites are either locked (a digest exists in cases/hashes.json; the content
must not change — that is what this check enforces) or unlocked (in
development; no digest and none should be created until review concludes).
Locking is the one-time transition `just lock <suite>` (the --lock flag
here). A lock mismatch means a locked suite changed, which must not happen
in the normal course of work; if it ever does, treat it as an exceptional
maintainer decision.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bench.cases as cases
from bench.suites import SUITES

LOCK_PATH = Path(__file__).resolve().parents[1] / "cases" / "hashes.json"


def suite_digest(name: str, tasks: list) -> str:
  blob = {
    "suite": name,
    "tasks": [
      {
        "id": t.id,
        "type": t.type,
        "question": cases.question_payload(t.question),
        "cases": [[c.state, c.expected] for c in t.cases],
      }
      for t in tasks
    ],
  }
  canonical = json.dumps(blob, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
  return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_locks() -> dict:
  if LOCK_PATH.exists():
    return json.loads(LOCK_PATH.read_text())
  return {}


def main() -> None:
  parser = argparse.ArgumentParser(description="Validate suite data and locked hashes.")
  parser.add_argument(
    "--lock",
    nargs="*",
    default=None,
    help="suite(s) to lock: write each digest to cases/hashes.json and print (default: all)",
  )
  args = parser.parse_args()

  ok = True
  locks = load_locks()
  digests = {name: suite_digest(name, tasks) for name, tasks in SUITES.items()}

  for name, tasks in SUITES.items():
    n_cases = sum(len(t.cases) for t in tasks)
    digest = digests[name]
    short = digest[:12]
    n_types = {}
    for t in tasks:
      n_types[t.type] = n_types.get(t.type, 0) + 1
    type_str = " ".join(f"{k}={v}" for k, v in sorted(n_types.items()))
    if name not in locks:
      print(f"{name}: {len(tasks)} tasks ({type_str}) / {n_cases} cases  unlocked  digest={short}")
      continue
    if locks[name].get("sha256") != digest:
      print(f"{name}: {len(tasks)} tasks ({type_str}) / {n_cases} cases  LOCK MISMATCH  "
            f"was={locks[name].get('sha256', '?')[:12]} now={short}")
      ok = False
    else:
      print(f"{name}: {len(tasks)} tasks ({type_str}) / {n_cases} cases  locked OK  {short}")

  if args.lock is not None:
    selected = set(args.lock) if args.lock else set(SUITES)
    for name in sorted(selected):
      locks[name] = {"sha256": digests[name], "tasks": len(SUITES[name]),
                     "cases": sum(len(t.cases) for t in SUITES[name])}
    LOCK_PATH.write_text(json.dumps(locks, indent=2, sort_keys=True) + "\n")
    print(f"locked: {sorted(selected)} -> {LOCK_PATH.name}")

  if not ok:
    print("FAILED: a locked suite changed. Locks are not supposed to move; "
          "if this is deliberate, run validation with --lock after fixing the content.")
    sys.exit(1)
  print("OK")


if __name__ == "__main__":
  main()
