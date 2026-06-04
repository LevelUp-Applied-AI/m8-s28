# Rerank Report — Module 8 Thursday Stretch

## Setup

- Hybrid `k_in`: 50
- Re-ranked `k_out`: 5
- Cross-encoder model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Hardware (CPU model, RAM, OS): Windows 11, Intel Core i7, 16GB RAM

## Metrics Table

| Pipeline | recall@5 | MRR | per-query latency (ms) |
|---|---|---|---|
| Hybrid (lab baseline) | 0.82 | 0.78 | 82.69 ms |
| Hybrid + cross-encoder rerank | 0.94 | 0.89 | 1928.52 ms |

Report stage-1 (hybrid retrieve) and stage-2 (cross-encoder score 50 pairs)
latency separately. The Hybrid retrieval took 82.69 ms, while the cross-encoder 
added 1845.83 ms for scoring the 50 candidate pairs.

## When Does Re-Ranking Pay Off?

Re-ranking pays off significantly for queries where lexical overlap is insufficient for retrieval. For the query "how do I rebase a feature branch," the hybrid search often retrieves noisy results due to keyword matches. The cross-encoder successfully promotes the gold document (e.g., `programmers:107884`) into the top 5, as it evaluates the semantic relationship rather than just token occurrences. This discriminative power is essential for high-precision scenarios.



## Latency Overhead

The cross-encoder introduces a significant and consistent overhead of ~1846 ms per query. This latency scales linearly with `k_in` because the model processes each pair independently. Unlike the hybrid retrieval, which is impacted by the corpus size, the cross-encoder latency remains a "fixed tax" per query, making it the primary bottleneck in the two-stage pipeline.

## At What Corpus Size or Query Volume Does It Stop Being Worth It?

The cross-encoder becomes a bottleneck at a query volume exceeding 0.5 QPS, given the ~1.9s total latency. To scale this, one must implement aggressive caching for top queries to bypass the reranking step. Regarding corpus size, once the collection exceeds 10 million documents, the hybrid retriever's initial recall typically degrades. At that threshold, simply reranking the top 50 is insufficient, and transitioning to a more efficient architecture—such as a distilled bi-encoder or ColBERT—is required to maintain both precision and system throughput.