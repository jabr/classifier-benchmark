"""Validate suite data files, cross-suite invariants, and locked content hashes.

Run via `just validate` (or `uv run python -m bench.validate`). Checks:
  - suite TOMLs parse and satisfy the schema (runs on import of bench.cases)
  - task ids unique across suites; v2 extension questions equal their v1
    originals (runs on import of bench.suites)
  - each suite with an entry in cases/hashes.json is unchanged

Hash mismatches mean the data changed after being locked: if the change was
intentional, re-lock the affected suites with `just relock <suite|all>` and
commit the updated cases/hashes.json.
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
    "--relock",
    nargs="*",
    default=None,
    help="suite(s) to re-hash and write (no names = all suites)",
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
      print(f"{name}: {len(tasks)} tasks ({type_str}) / {n_cases} cases  UNLOCKED  digest={short}")
      continue
    if locks[name].get("sha256") != digest:
      print(f"{name}: {len(tasks)} tasks ({type_str}) / {n_cases} cases  LOCK MISMATCH  "
            f"was={locks[name].get('sha256', '?')[:12]} now={short}")
      ok = False
    else:
      print(f"{name}: {len(tasks)} tasks ({type_str}) / {n_cases} cases  locked OK  {short}")

  if args.relock is not None:
    selected = set(args.relock) if args.relock else set(SUITES)
    for name in sorted(selected):
      locks[name] = {"sha256": digests[name], "tasks": len(SUITES[name]),
                     "cases": sum(len(t.cases) for t in SUITES[name])}
    LOCK_PATH.write_text(json.dumps(locks, indent=2, sort_keys=True) + "\n")
    print(f"re-locked: {sorted(selected)} -> {LOCK_PATH.name}")

  if not ok:
    print("FAILED: locked suite content changed; re-lock deliberately if intended.")
    sys.exit(1)
  print("OK")


if __name__ == "__main__":
  main()
