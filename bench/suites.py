"""Named test suites: v1 (cases/v1.toml) and v2 (cases/v2.toml).

A suite is a versioned list of tasks that can be reported on its own or
combined with the others. Task ids are unique across suites, so a task id
maps to exactly one (suite, task) pair.

Extension tasks in v2 reuse the v1 question schema under a `_v2` id, so
v1 and v2 numbers are directly comparable per task family even though no
case is shared. That identity is enforced here rather than by import, so
suites live as independent TOML data files.
"""

from bench.cases import TASKS_V1, TASKS_V2, question_payload

SUITES: dict[str, list] = {
  "v1": TASKS_V1,
  "v2": TASKS_V2,
}

SUITE_NAMES = list(SUITES)

ALL_TASKS = [task for tasks in SUITES.values() for task in tasks]
ALL_TASK_IDS = [t.id for t in ALL_TASKS]

if len(set(ALL_TASK_IDS)) != len(ALL_TASK_IDS):
  raise ValueError("Task ids must be unique across all suites")

# v2 extension tasks must reuse their v1 question verbatim.
_BY_ID = {name: {t.id: t for t in tasks} for name, tasks in SUITES.items()}
for _task in TASKS_V2:
  if _task.id.endswith("_v2"):
    _base = _BY_ID["v1"].get(_task.id[: -len("_v2")])
    if _base is not None and question_payload(_task.question) != question_payload(_base.question):
      raise ValueError(f"{_task.id} question must deep-equal the v1 {_base.id} question")


def resolve_suites(value: str) -> list[str]:
  """Parse a comma-separated suite list; 'all' expands to every suite."""
  wanted = [s.strip() for s in value.split(",") if s.strip()]
  if not wanted or "all" in wanted:
    return SUITE_NAMES[:]
  unknown = [s for s in wanted if s not in SUITES]
  if unknown:
    raise ValueError(f"Unknown suite(s): {sorted(unknown)}. Available: {SUITE_NAMES} or 'all'")
  seen = set()
  names = []
  for name in wanted:
    if name not in seen:
      seen.add(name)
      names.append(name)
  return names


def suite_plan(names: list[str], task_ids: list[str] | None = None) -> list[tuple[str, list]]:
  """Build an ordered [(suite_name, tasks...)] plan, optionally filtered by task ids.

  Task ids are matched within the selected suites only; ids from suites
  that were not selected are reported as unknown.
  """
  plan = []
  missing = list(task_ids or [])
  for name in names:
    wanted = set(task_ids or [])
    selected = [t for t in SUITES[name] if not wanted or t.id in wanted]
    if selected:
      plan.append((name, selected))
    missing = [tid for tid in missing if tid not in {t.id for t in SUITES[name]}]
  if missing:
    pool_ids = [t.id for name in names for t in SUITES[name]]
    raise ValueError(f"Unknown task(s): {sorted(missing)}. Available in selected suites: {pool_ids}")
  return plan


def tasks_by_ids(ids: list[str]) -> list:
  """Look up tasks by id across all suites (for programmatic use)."""
  if not ids:
    return ALL_TASKS[:]
  wanted = set(ids)
  unknown = wanted - set(ALL_TASK_IDS)
  if unknown:
    raise ValueError(f"Unknown task(s): {sorted(unknown)}. Available: {ALL_TASK_IDS}")
  return [t for t in ALL_TASKS if t.id in wanted]
