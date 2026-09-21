"""TriageIQ (coldstart88/triageiq-dataset).

Synthetic support tickets, labeled at generation along three axes: sentiment
(positive/neutral/negative), urgency (low/medium/high), and category (the
5-way triage used here: billing/technical/account/feature_request/other).
Samples come from the test split.
"""

from sources.common import Source

DATASET_ID = "coldstart88/triageiq-dataset"


def _category_rows(pool: int) -> list[tuple[str, str]]:
  from sources.common import hf_rows

  rows = []
  for row in hf_rows(DATASET_ID, "data/test-00000-of-00001.parquet", pool):
    text = str(row.get("text") or "").strip()
    category = str(row.get("category") or "").strip()
    if text and category:
      rows.append((text, category))
  return rows


def _field_rows(field: str, pool: int) -> list[tuple[str, str]]:
  from sources.common import hf_rows

  rows = []
  for row in hf_rows(DATASET_ID, "data/test-00000-of-00001.parquet", pool):
    text = str(row.get("text") or "").strip()
    value = str(row.get(field) or "").strip().lower()
    if text and value:
      rows.append((text, value))
  return rows


loader_category = lambda pool: _category_rows(pool)
loader_sentiment = lambda pool: _field_rows("sentiment", pool)
loader_urgency = lambda pool: _field_rows("urgency", pool)


question = {
  "instructions": "Classify the customer's message into one of the five support categories.",
  "criteria": {
    "billing": "Payments, charges, invoices, refunds, or subscription pricing.",
    "technical": "Bugs, error messages, crashes, or features producing incorrect results.",
    "account": (
      "Login problems, forgotten or reset passwords, account lockouts, or updating "
      "account settings or credentials."
    ),
    "feature_request": "Suggestions for new features, improvements, or product enhancements.",
    "other": (
      "General questions, information requests, or anything that is not a bug, billing "
      "issue, account problem, or feature request."
    ),
  },
}

source = Source(
  name="triageiq", dataset_id=DATASET_ID, split="test", static=True, question=question, loader=loader_category
)

negative_question = {
  "instructions": "Does this support ticket express negative sentiment?",
  "criteria": {
    "true": "Yes — the customer is unhappy, frustrated, or complaining.",
    "false": "No — the message is neutral or positive.",
  },
}

negative_source = Source(
  name="triageiq_negative",
  dataset_id=DATASET_ID,
  split="test",
  static=True,
  question=negative_question,
  loader=loader_sentiment,
  type="noul",
  label_map={"negative": True, "neutral": False, "positive": False},
)

urgency_question = {
  "instructions": "How urgent is this support ticket, on a three-level scale?",
  "criteria": [
    "Low — routine request or question; it can wait in the normal queue.",
    "Medium — time-sensitive and annoying, but the customer is not blocked in a critical way.",
    "High — the customer is blocked or losing money; this needs immediate attention.",
  ],
}

urgency_source = Source(
  name="triageiq_urgency",
  dataset_id=DATASET_ID,
  split="test",
  static=True,
  question=urgency_question,
  loader=loader_urgency,
  type="score",
  label_map={"low": 0, "medium": 1, "high": 2},
)
