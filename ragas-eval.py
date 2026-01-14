#pip install ragas datasets langchain-openai
import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_openai import ChatOpenAI

# --- CONFIGURATION ---
# Ragas uses OpenAI by default to act as the "Judge"
# Ensure your key is set in the environment or replace here.
os.environ["OPENAI_API_KEY"] = "sk-..." 

# --- 1. PREPARE YOUR DATA ---
# In production, you would load this from your application logs (CSV/JSON).
# Structure:
# - question: What the user asked.
# - answer: What your bot replied.
# - contexts: The actual text chunks retrieved from Neo4j/VectorDB.
# - ground_truth: (Optional) The "perfect" human-written answer for reference.

data_samples = {
    "question": [
        "How do I fix the ERR_BAT_DRAIN on my XPS 15?",
        "What is the return policy for opened laptops?",
        "Who is the CEO of the company?"
    ],
    "answer": [
        # Case 1: Good Answer (Grounded in context)
        "You can fix the battery drain by running the 'FixPower.exe' script remotely.",
        
        # Case 2: Hallucination (Answer contradicts or isn't in context)
        "You can return opened laptops within 90 days for a full refund, no questions asked.",
        
        # Case 3: Irrelevant (Answer doesn't address the prompt)
        "The XPS 15 is a great laptop with a 4K display."
    ],
    "contexts": [
        # Context for Case 1 (Contains the answer)
        ["Doc 10.2: ERR_BAT_DRAIN is caused by driver corruption. Fix: Run 'FixPower.exe'."],
        
        # Context for Case 2 (Contains the REAL policy, which the bot ignored)
        ["Policy 4.1: Opened electronics cannot be returned unless defective. Restocking fees apply."],
        
        # Context for Case 3 (Irrelevant to the question, but true facts)
        ["Company Info: We were founded in 1994. Our headquarters is in Texas."]
    ],
    "ground_truth": [
        "Run the 'FixPower.exe' diagnostic script.",
        "Opened laptops generally cannot be returned unless defective.",
        "The CEO is Michael Dell." 
    ]
}

# Convert to HuggingFace Dataset format (required by Ragas)
dataset = Dataset.from_dict(data_samples)

# --- 2. DEFINE METRICS ---
# We select specific metrics to measure different aspects of quality.
metrics = [
    faithfulness,      # Does the answer contradict the context? (Hallucination check)
    answer_relevancy,  # Does the answer actually address the user's question?
    context_precision, # Was the relevant info found in the top retrieval results?
]

# --- 3. RUN EVALUATION ---
print("Running RAG Evaluation... (This sends data to OpenAI for grading)")

results = evaluate(
    dataset=dataset,
    metrics=metrics,
    # You can swap the 'judge' model here (e.g., to GPT-3.5 to save cost, though GPT-4 is recommended for eval)
    llm=ChatOpenAI(model="gpt-4-turbo-preview") 
)

# --- 4. ANALYZE RESULTS ---
print("\n--- Evaluation Scores ---")
print(results)

# Convert to Pandas for easier reading
df = results.to_pandas()

print("\n--- Detailed Analysis ---")
for index, row in df.iterrows():
    print(f"\nQ: {row['question']}")
    print(f"A: {row['answer']}")
    print(f"Faithfulness: {row['faithfulness']:.2f} (1.0 = No Hallucination)")
    print(f"Relevance: {row['answer_relevancy']:.2f} (1.0 = Highly Relevant)")