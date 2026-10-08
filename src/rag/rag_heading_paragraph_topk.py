"""Roadmap RAG with heading-prefixed paragraphs and Top-k diagnostics."""

from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_MODEL,
    GENERATION_MODEL,
    MAX_OUTPUT_TOKENS,
    SOURCE_PATH,
    client,
)
from preprocess.text import split_heading_paragraphs
from rag.settings import (
    MULTI_SOURCE_SYSTEM_PROMPT,
    ROADMAP_QUERIES,
)

text = SOURCE_PATH.read_text(encoding="utf-8")
chunks = split_heading_paragraphs(text, SOURCE_PATH.name)
print(f"Source: {SOURCE_PATH}")
print(f"Chunk count: {len(chunks)}")

queries = ROADMAP_QUERIES
documents = [chunk["text"] for chunk in chunks]

model = SentenceTransformer(EMBEDDING_MODEL)

query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

similarity = model.similarity(query_embeddings, document_embeddings)

DEBUG_RETRIEVAL = True

if DEBUG_RETRIEVAL:
    for query_idx in [2, 4]:
        print(f"\nQuery: {query_idx + 1}: {queries[query_idx]}")

        ranked = similarity[query_idx].topk(k=len(documents))

        for rank, (document_idx, score) in enumerate(
            zip(ranked.indices.tolist(), ranked.values.tolist()),
            start=1,
        ):
            chunk = chunks[document_idx]
            marker = "<-- TARGET" if chunk["title"].startswith("Phase 3 ") else ""

            print(
                f"Rank: {rank:2d} | Score: {score:.4f} | "
                f"Chunk: {chunk['chunk_id']} | {chunk['title']}{marker}"
            )
            preview = chunk["body"][:160].replace("\n", " ")
            print(f"    Preview: {preview}")
    raise SystemExit(0)


top_k = min(3, len(documents))
top_results = similarity.topk(top_k, dim=-1)
top_indices = top_results.indices.tolist()
top_scores = top_results.values.tolist()

system_prompt = MULTI_SOURCE_SYSTEM_PROMPT

for query_idx, document_indices in enumerate(top_indices):
    query = queries[query_idx]
    print(f"\nQuery: {query}")
    contexts = []
    for rank, document_idx in enumerate(document_indices, start=1):
        document = documents[document_idx]
        score = top_scores[query_idx][rank - 1]
        title = chunks[document_idx]["title"]

        print(f"Rank: {rank}, Score: {score:.4f} | {title}")
        contexts.append(f"[{rank}] {document}")
    context = "\n\n".join(contexts)

    user_prompt = f"""

        Question:
        {query}

        Reference material:
        {context}
    """

    response = client.messages.create(
        model=GENERATION_MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    print("Reference: ", context)
    print("Answer: ")

    for block in response.content:
        if block.type == "text":
            print(block.text)
