"""Module 8 — Thursday Stretch (Honors Track): Cross-Encoder Re-Ranking.

Add a cross-encoder re-ranking stage to the lab's hybrid retriever and
evaluate the cost/benefit. Cross-encoders score (query, passage) pairs
jointly rather than independently — they produce a more discriminative
ranking, but at a real latency cost.

Use cross-encoder/ms-marco-MiniLM-L-6-v2 from sentence-transformers.
"""

from __future__ import annotations

import weaviate
from sentence_transformers import CrossEncoder
from retrieval_helpers import hybrid_search

CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

ce = CrossEncoder(CROSS_ENCODER_MODEL)


def cross_encoder_rerank(query: str, candidates: list[dict], k_out: int = 5) -> list[str]:
    """Re-rank a candidate list using a cross-encoder.

    `candidates` is a list of {"doc_id": str, "text": str} (or a similar
    schema providing the text to score). Score each (query, candidate.text)
    pair; sort descending; return the top-`k_out` doc_id strings.
    """
    if not candidates:
        return []

    pairs = [(query, c["text"]) for c in candidates]
    scores = ce.predict(pairs)

    scored_candidates = list(zip(candidates, scores))
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    top_k_ids = [c["doc_id"] for c, score in scored_candidates[:k_out]]
    return top_k_ids


def rerank_search(
    client: weaviate.Client,
    query: str,
    embedder,
    k_in: int = 50,
    k_out: int = 5,
) -> list[str]:
    """Two-stage retriever: hybrid retrieve k_in, cross-encoder re-rank to k_out.

    Stage 1: hybrid_search(client, query, k_in, embedder, alpha=0.5) -> list[doc_id]
    Stage 2: resolve each doc_id back to its text from Weaviate
    Stage 3: cross_encoder_rerank(query, candidates, k_out)

    Return the ordered list of doc_id strings, length <= k_out.
    """
    candidate_ids = hybrid_search(client, query, k_in, embedder, alpha=0.5)
    if not candidate_ids:
        return []

    operands = [{"path": ["doc_id"], "operator": "Equal", "valueString": d_id} for d_id in candidate_ids]
    
    response = (
        client.query
        .get("Post", ["doc_id", "text"])
        .with_where({
            "operator": "Or",
            "operands": operands
        })
        .with_limit(k_in)
        .do()
    )

    posts = response.get("data", {}).get("Get", {}).get("Post", [])
    
    candidates = []
    for p in posts:
        if "doc_id" in p and "text" in p:
            candidates.append({"doc_id": p["doc_id"], "text": p["text"]})

    top_ids = cross_encoder_rerank(query, candidates, k_out=k_out)
    return top_ids