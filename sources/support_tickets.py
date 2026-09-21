"""Support-Ticket-Router (cngchis/Support-Ticket-Router-12K-Cleaned).

Synthetic support tickets (GPT-4-class generated, then filtered and cleaned),
with a 6-way routing label assigned at generation. Samples are drawn from the
test split.
"""

from sources.common import Source

DATASET_ID = "cngchis/Support-Ticket-Router-12K-Cleaned"


def load(pool: int) -> list[tuple[str, str]]:
  from sources.common import hf_rows

  rows = []
  for row in hf_rows(DATASET_ID, "processed/test.jsonl", pool):
    text = str(row.get("text") or "").strip()
    label = str(row.get("label") or "").strip()
    if text and label:
      rows.append((text, label))
  return rows


question = {
  "instructions": (
    "A customer support ticket arrived in the queue. "
    "Which of the six categories does it belong to?"
  ),
  "criteria": {
    "billing": (
      "Invoices, payments, charges, refunds, or pricing questions; "
      "billing disputes or incorrect charges."
    ),
    "technical": (
      "Something in the product is broken: bugs, error messages, crashes, "
      "or features behaving incorrectly."
    ),
    "complaint": (
      "Frustration with service quality, unmet expectations, or poor customer "
      "experience, without a distinct billing/technical/account issue."
    ),
    "api": (
      "Developer questions about API integration, endpoints, authentication keys, "
      "webhooks, or SDK setup."
    ),
    "cancellation": "Requests to cancel a subscription, close an account, or end the service.",
    "upgrade": (
      "Interest in upgrading a plan, switching to a different tier, adding features, "
      "or premium options."
    ),
  },
}

source = Source(
  name="support_tickets", dataset_id=DATASET_ID, split="test", static=True, question=question, loader=load
)
