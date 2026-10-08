"""Roadmap RAG with paragraph chunks and Top-1 retrieval."""

from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_MODEL,
    GENERATION_MODEL,
    MAX_OUTPUT_TOKENS,
    SOURCE_PATH,
    client,
)
from preprocess.text import split_paragraphs
from rag.settings import (
    ROADMAP_QUERIES,
    SINGLE_SOURCE_SYSTEM_PROMPT,
)

text = SOURCE_PATH.read_text(encoding="utf-8")
chunks = split_paragraphs(text, SOURCE_PATH.name)

queries = ROADMAP_QUERIES
documents = [chunk["text"] for chunk in chunks]

model = SentenceTransformer(EMBEDDING_MODEL)

query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

similarity = model.similarity(query_embeddings, document_embeddings)

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
        messages=[{"role": "user", "content": user_prompt}],
    )

    print("\nQuery: ", query)
    print("Reference: ", context)
    print("Answer: ")

    for block in response.content:
        if block.type == "text":
            print(block.text)
