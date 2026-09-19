import von

# Set backend to Von-1.0
von.set_backend("modernbert")

# 1. Multi-Class Choice Routing
result = von.decide(
    "Customer requests a full refund for an unused annual subscription.",
    choices={
        "billing": "Inquiries regarding refunds, payments, invoices, or subscriptions",
        "tech": "Technical bugs, 500 errors, database crashes, or downtime",
        "feature_request": "Requests for new features or capabilities"
    }
)
print(result.choice)         # 'billing'
print(result.confidence)     # 0.7920
print(result.probabilities)  # {'billing': 0.8742, 'tech': 0.0820, 'feature_request': 0.0438}

# 2. Binary Verification (Noul)
is_failing = von.judge(
    "Database connection pool exhausted on port 5432, connection refused.",
    instructions="Is the database infrastructure failing or down?"
)
print(is_failing)  # 0.9412
