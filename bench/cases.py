"""Bench-owned task and case schema, plus TOML suite loading.

The benchmark defines its own question schema — the System One wire shape
{"type": "choice"|"noul"|"score", "instructions": str, "criteria": ...} —
shared by the typesafe/jev decisions API and adapted per model in
bench/backends/. Suites live as data in cases/v1.toml and cases/v2.toml
(TOML so harnesses in other languages can read them directly). Suites are
locked (final; digest verified against cases/hashes.json by
bench/validate.py — do not edit) or unlocked (in development; no hash):
`just lock <suite>` is the one-time transition at the end of review.

Task ids must be unique across suites. A task may declare `extends = "<task-id>"`:
it then poses the identical question as that task (with its own new cases), and the
registry enforces the deep-equality — that is what makes extension suites (v2's
`<id>_v2` tasks, and any future suite) directly comparable.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Union

CASES_DIR = Path(__file__).resolve().parents[1] / "cases"


@dataclass
class Choice:
  """Pick one option from a fixed list with a probability distribution."""

  instructions: str
  criteria: dict[str, str]


@dataclass
class Noul:
  """A yes/no probability question."""

  instructions: str
  criteria: dict[str, str] | None = None


@dataclass
class Score:
  """A position on an ordered scale (2 to 10 levels)."""

  instructions: str
  criteria: list[str]


Question = Union[Choice, Noul, Score]


@dataclass
class Case:
  state: str
  expected: Union[str, bool, int]


@dataclass
class Task:
  id: str
  type: str
  question: Question
  cases: list[Case]
  extends: str | None = None


def _question_from_raw(task_id: str, task_type: str, raw: dict) -> Question:
  instructions = raw.get("instructions")
  if not isinstance(instructions, str) or not instructions.strip():
    raise ValueError(f"{task_id}: question.instructions must be a non-empty string")
  criteria = raw.get("criteria")
  if task_type == "choice":
    if not isinstance(criteria, dict) or not criteria:
      raise ValueError(f"{task_id}: choice questions require a non-empty criteria table")
    for key, value in criteria.items():
      if not isinstance(key, str) or not isinstance(value, str):
        raise ValueError(f"{task_id}: choice criteria must map option key -> string description")
    return Choice(instructions=instructions, criteria=dict(criteria))
  if task_type == "noul":
    if criteria is not None and not isinstance(criteria, dict):
      raise ValueError(f"{task_id}: noul criteria must be a table of true/false descriptions")
    return Noul(instructions=instructions, criteria=criteria)
  if task_type == "score":
    if not isinstance(criteria, list) or len(criteria) < 2:
      raise ValueError(f"{task_id}: score questions require at least two criteria levels")
    for level in criteria:
      if not isinstance(level, str):
        raise ValueError(f"{task_id}: score criteria levels must be strings")
    return Score(instructions=instructions, criteria=list(criteria))
  raise ValueError(f"{task_id}: unknown task type {task_type!r}")


def load_suite(path: Path) -> list[Task]:
  """Parse and validate a suite TOML into Task objects (structure is trusted
  only after these checks; recorded scores depend on exact content, which is
  additionally covered by the hashes in cases/hashes.json)."""
  with open(path, "rb") as fh:
    data = tomllib.load(fh)
  tasks = []
  for raw_task in data.get("task", []):
    task_id = raw_task.get("id")
    task_type = raw_task.get("type")
    if not isinstance(task_id, str) or not task_id:
      raise ValueError(f"task missing id: {raw_task!r}")
    if task_type not in ("choice", "noul", "score"):
      raise ValueError(f"{task_id}: unknown task type {task_type!r}")
    question = _question_from_raw(task_id, task_type, raw_task.get("question") or {})
    cases = []
    for raw_case in raw_task.get("cases", []):
      state = raw_case.get("state")
      expected = raw_case.get("expected")
      if not isinstance(state, str) or not state.strip():
        raise ValueError(f"{task_id}: every case needs a non-empty state")
      if task_type == "noul" and not isinstance(expected, bool):
        raise ValueError(f"{task_id}: noul expected values must be true/false")
      if task_type == "choice":
        if not isinstance(expected, str) or expected not in question.criteria:
          raise ValueError(f"{task_id}: expected {expected!r} must be a criteria option key")
      if task_type == "score":
        if isinstance(expected, bool) or not isinstance(expected, int):
          raise ValueError(f"{task_id}: score expected values must be level indices")
        if not 0 <= expected < len(question.criteria):
          raise ValueError(f"{task_id}: expected {expected!r} out of range")
      cases.append(Case(state=state, expected=expected))
    if not cases:
      raise ValueError(f"{task_id}: no cases")
    extends = raw_task.get("extends")
    if extends is not None and (not isinstance(extends, str) or not extends.strip()):
      raise ValueError(f"{task_id}: extends must be a task id")
    tasks.append(Task(id=task_id, type=task_type, question=question, cases=cases, extends=extends))
  if not tasks:
    raise ValueError(f"{path.name}: no tasks")
  ids = [t.id for t in tasks]
  if len(set(ids)) != len(ids):
    raise ValueError(f"{path.name}: duplicate task ids {[i for i in ids if ids.count(i) > 1]}")
  return tasks


def question_payload(question: Question) -> dict:
  """The canonical System One wire form shared with the typesafe/jev API."""
  if isinstance(question, Choice):
    return {"type": "choice", "instructions": question.instructions, "criteria": dict(question.criteria)}
  payload = {"type": "noul", "instructions": question.instructions}
  if isinstance(question, Noul) and question.criteria:
    payload["criteria"] = dict(question.criteria)
  if isinstance(question, Score):
    return {"type": "score", "instructions": question.instructions, "criteria": list(question.criteria)}
  return payload


TASKS_V1 = load_suite(CASES_DIR / "v1.toml")
TASKS_V2 = load_suite(CASES_DIR / "v2.toml")
