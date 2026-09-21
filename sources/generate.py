"""Generate a real-data sample suite from an external source.

Usage:
  uv run --extra sources python -m sources.generate cfpb                 # random seed
  uv run --extra sources python -m sources.generate cfpb --seed 48620 --n 40
  uv run --extra sources python -m sources.generate triageiq --max-words 150

Writes sources/samples/<source>-<seed-hex>.toml, which bench/suites.py
auto-discovers as an unlocked suite (run it with --sample <source>-<seed-hex>
or --sample all).
"""

import argparse
import random

from sources import cfpb, support_tickets, triageiq
from sources.common import SAMPLES_DIR, generate

SOURCES = {
  s.name: s
  for s in (
    cfpb.source,
    support_tickets.source,
    triageiq.source,
    triageiq.negative_source,
    triageiq.urgency_source,
  )
}


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Generate a balanced sample suite from an external dataset source.",
    epilog=f"available sources: {sorted(SOURCES)}",
  )
  parser.add_argument("source", choices=sorted(SOURCES), help="which external dataset source")
  parser.add_argument("--seed", type=int, default=None, help="16-bit seed (default: random)")
  parser.add_argument("--n", type=int, default=40, help="number of cases (default 40)")
  parser.add_argument("--pool", type=int, default=5000, help="max candidates to scrape (default 5000)")
  parser.add_argument("--max-words", type=int, default=120)
  parser.add_argument("--min-words", type=int, default=8)
  parser.add_argument("--no-redact", action="store_true", help="keep emails/phones unredacted")
  parser.add_argument("--force", action="store_true", help="overwrite an existing sample file")
  args = parser.parse_args()
  if args.seed is None:
    args.seed = random.randrange(1 << 16)
  if not 0 <= args.seed < (1 << 16):
    parser.error("--seed must fit 16 bits (0..65535)")

  path = generate(SOURCES[args.source], args)
  suite = path.stem
  n_tasks = sum(1 for _ in SAMPLES_DIR.glob("*.toml"))
  print(f"wrote {path}")
  print(f"suite {suite!r} discovered ({n_tasks} sample suite(s) total)")
  print(f"run: uv run python -m bench.run --sample {suite} --out results/{suite}.json")


if __name__ == "__main__":
  main()
