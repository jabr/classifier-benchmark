import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_id = "./models/wfzyx/von"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id).to("mps")

premise = "Database connection pool exhausted on port 5432, connection refused."
hypothesis = "Is the database infrastructure failing or down? Technical failure or outage"

inputs = tokenizer(premise, hypothesis, return_tensors="pt").to("mps")
with torch.no_grad():
    logits = model(**inputs).logits
    # Entailment score (index 0)
    score = torch.softmax(logits / 1.0367, dim=-1)
    print(score)
    print(logits)
    print(inputs)
