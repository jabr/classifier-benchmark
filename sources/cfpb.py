"""CFPB consumer complaints (sovai/cfpb_complaints).

Real consumer-complaint narratives mirrored from the public CFPB database —
a live mirror, so the upstream pool grows and reorders; only the committed
sample content is a stable artifact. Labels come from the consumer's
self-selected CFPB `issue` at filing: CFPB scrubs PII but never verifies or
corrects categories, and the issue menu cannot represent everything consumers
complain about — screen every case against its narrative before use.
"""

from sources.common import Source

DATASET_ID = "sovai/cfpb_complaints"

ISSUE_MAP = {
  # report dispute
  "Incorrect information on your report": "report_dispute",
  "Improper use of your report": "report_dispute",
  "Problem with a company's investigation into an existing problem": "report_dispute",
  "Problem with a credit reporting company's investigation into a problem": "report_dispute",
  "Unable to get your credit report or credit score": "report_dispute",
  # collection contact
  "Attempts to collect debt not owed": "collection_contact",
  "Cont'd attempts collect debt not owed": "collection_contact",
  "Written notification about debt": "collection_contact",
  "Communication tactics": "collection_contact",
  "False statements or representation": "collection_contact",
  "Took or threatened to take negative or legal action": "collection_contact",
  # account problem
  "Managing an account": "account_problem",
  "Closing an account": "account_problem",
  "Getting a credit card": "account_problem",
  "Other features, terms, or problems": "account_problem",
  "Using a debit or ATM card": "account_problem",
  "Trouble during payment process": "account_problem",
  "Problem with a purchase shown on your statement": "account_problem",
  "Problem when making payments": "account_problem",
  "Transaction was not authorized": "account_problem",
  "Cash advance": "account_problem",
  # loan hardship
  "Struggling to pay mortgage": "loan_hardship",
  "Struggling to pay your loan": "loan_hardship",
  "Dealing with your lender or servicer": "loan_hardship",
  "Loan modification, collection, foreclosure": "loan_hardship",
  "Loan servicing, payments, escrow account": "loan_hardship",
  "Managing the loan or lease": "loan_hardship",
  "Problems at the end of the loan or lease": "loan_hardship",
  "Applying for a mortgage or refinancing an existing mortgage": "loan_hardship",
  "Closing on a mortgage": "loan_hardship",
}


def load(pool: int) -> list[tuple[str, str]]:
  from sources.common import CACHE_DIR, ds_server_rows, hf_rows

  CACHE_DIR.mkdir(parents=True, exist_ok=True)
  cache = CACHE_DIR / f"cfpb-{pool}.parquet"
  if cache.exists():
    import pyarrow.parquet as pq

    table = pq.read_table(cache)
    return list(zip(table.column("text").to_pylist(), table.column("category").to_pylist()))
  rows = []
  data = []
  try:
    data = ds_server_rows(DATASET_ID, split="train", pool=pool * 3)
  except OSError:
    # datasets-server unavailable: fall back to the full 788 MB parquet file
    data = hf_rows(DATASET_ID, "cfpb_complaints.parquet", pool * 3)
  for row in data:
    text = str(row.get("consumer_complaint_narrative") or "").strip()
    category = ISSUE_MAP.get(row.get("issue", ""))
    if not text or category is None:
      continue
    rows.append((text, category))
    if len(rows) >= pool:
      break
  if rows:
    import pyarrow as pa
    import pyarrow.parquet as pq

    pq.write_table(
      pa.table({"text": [t for t, _ in rows], "category": [c for _, c in rows]}), cache
    )
  return rows


question = {
  "instructions": (
    "A consumer complaint narrative was filed with the Consumer Financial "
    "Protection Bureau (CFPB). Which of the four complaint categories does it belong to?"
  ),
  "criteria": {
    "report_dispute": (
      "Disputes incorrect information on a credit report, problems with a bureau's "
      "investigation, or being unable to obtain their credit report or score."
    ),
    "collection_contact": (
      "A debt collector is contacting them about a debt they dispute or do not owe; "
      "written notices, repeated calls, communication tactics, or threats of legal action."
    ),
    "account_problem": (
      "Trouble managing an account or card: access problems, failed or incorrect payments, "
      "disputed charges, unauthorized transactions, or closing an account."
    ),
    "loan_hardship": (
      "Struggles to pay a mortgage or loan, risk of foreclosure, loan modification requests, "
      "or problems dealing with the lender, servicer, or end of the loan term."
    ),
  },
}

source = Source(
  name="cfpb", dataset_id=DATASET_ID, split="train", static=False, question=question, loader=load
)
