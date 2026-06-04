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

import time


CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

ce = CrossEncoder(CROSS_ENCODER_MODEL)


def cross_encoder_rerank(query: str, candidates: list[dict], k_out: int = 5) -> list[str]:
    """Re-rank a candidate list using a cross-encoder.

    `candidates` is a list of {"doc_id": str, "text": str} (or a similar
    schema providing the text to score). Score each (query, candidate.text)
    pair; sort descending; return the top-`k_out` doc_id strings.

    Hint:
        from sentence_transformers import CrossEncoder
        ce = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [(query, c["text"]) for c in candidates]
        scores = ce.predict(pairs)
        # argsort descending, take top k_out, map back to doc_id
    """
    # load CrossEncoder (consider module-level for speed)
    # build pairs, score with ce.predict, argsort descending, take top k_out
    # return list of doc_id strings
    if not candidates:
        return []

    pairs = [(query, c["text"]) for c in candidates]
    
    scores = ce.predict(pairs)

    results = []
    for i, cand in enumerate(candidates):
        results.append({"doc_id": cand["doc_id"], "score": scores[i]})
    
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return [r["doc_id"] for r in results[:k_out]]

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
    # stage 1: hybrid_search to get k_in candidate doc_ids
    # resolve each doc_id back to {"doc_id": ..., "text": ...} via Weaviate query
    # stage 3: cross_encoder_rerank(query, candidates, k_out)

    start_hybrid = time.perf_counter()
    candidate_ids = hybrid_search(client, query, k=k_in, embedder=embedder)
    end_hybrid = time.perf_counter()
    print(f"DEBUG: Found {len(candidate_ids)} candidates.")
    
    candidates = []
    for doc_id in candidate_ids:

        result = client.query.get("Post", ["text", "doc_id"]).with_where({
            "path": ["doc_id"],
            "operator": "Equal",
            "valueString": doc_id
        }).do()
        
        items = result.get("data", {}).get("Get", {}).get("Post", [])
        if items:
            candidates.append(items[0])
            
    print(f"DEBUG: Successfully resolved {len(candidates)} candidates for reranking.")
    
    if not candidates:
        return []
    start_rerank = time.perf_counter()
    final_ids = cross_encoder_rerank(query, candidates, k_out=k_out)
    end_rerank = time.perf_counter()
    

    hybrid_ms = (end_hybrid - start_hybrid) * 1000
    rerank_ms = (end_rerank - start_rerank) * 1000
    
    print(f"\n--- Performance Metrics ---")
    print(f"Hybrid Search Latency: {hybrid_ms:.2f} ms")
    print(f"Cross-Encoder Latency: {rerank_ms:.2f} ms")
    print(f"Total Latency: {hybrid_ms + rerank_ms:.2f} ms")
    
    return final_ids
import weaviate
from sentence_transformers import SentenceTransformer
from rerank import rerank_search

def main():
    
    client = weaviate.Client("http://localhost:8080")
    
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    query = "how do I rebase a feature branch"
    print(f"Query: {query}\n")
    
    print("Running Hybrid Search + Reranking...")
    try:
        results = rerank_search(client, query, embedder, k_in=20, k_out=5)
        
        print(f"\nTop 5 Results (doc_ids):")
        for i, doc_id in enumerate(results, 1):
            print(f"{i}. {doc_id}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()