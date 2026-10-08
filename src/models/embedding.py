"""Minimal RAG with two in-memory documents and Top-1 retrieval."""

from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_MODEL,
    GENERATION_MODEL,
    MAX_OUTPUT_TOKENS,
    client,
)
from rag.settings import SINGLE_SOURCE_SYSTEM_PROMPT

model = SentenceTransformer(EMBEDDING_MODEL)

print("Model device:", model.device)
print("Parameter device:", next(model.parameters()).device)

queries = [
    "What is the capital of China?",
    "Explain gravity",
]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun.",
]

query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

similarity = model.similarity(query_embeddings, document_embeddings)
print(similarity)

best_indices = similarity.argmax(-1).tolist()


system_prompt = SINGLE_SOURCE_SYSTEM_PROMPT

for query_idx, document_idx in enumerate(best_indices):
    query = queries[query_idx]
    context = documents[document_idx]

    user_prompt = f"""
Question:
{query}

Reference material:
[1] {context}
"""

    response = client.messages.create(
        model=GENERATION_MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )

    print("\nQuestion: ", query)
    print("Reference: ", context)
    print("Answer: ")

    for block in response.content:
        if block.type == "text":
            print(block.text)
