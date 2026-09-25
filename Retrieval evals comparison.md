# Retrieval evals comparison

Golden set: `data/gold/policy_rag_golden.json`. 15 questions. Ranking metrics use the 14 questions that name a supporting section. The 1 abstain question has no relevant chunk, so it is timed and left out of the ranking means.

A chunk is relevant when its section is listed in `supporting_sections`. If that section sets `chunk_index`, only that chunk counts. The ranked list is `hybrid_search` after reciprocal rank fusion and the cross-encoder. The mean relevant set is 1.14 chunks.

The index is `mxbai-embed-large`. A question that says current is searched only on chunks that are not superseded. A question that says superseded or archived is searched only on superseded chunks. A question that says both, or neither, searches every chunk. gold-026 does not say current, so both carbon plans are searched for it. Dense search and BM25 each contribute 10 chunks from that plan, then reciprocal rank fusion and a cross-encoder. The metrics are computed on the 10 chunks returned after reranking. Scored questions: 14. Timed questions: 15. Recorded with `python -m src.eval_retrieval`.

## Rerankers, k = 10

The embedding index is the same for every row. The only change is the cross-encoder.

| Reranker | MRR | nDCG@10 | Recall@10 | Precision | Precision@10 | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Xenova/ms-marco-MiniLM-L-6-v2 | 0.7500 | 0.7941 | 0.9286 | 0.1071 | 0.1071 | 0.363 s |
| jinaai/jina-reranker-v1-tiny-en | 0.6763 | 0.7298 | 0.9286 | 0.1071 | 0.1071 | 0.281 s |
| BAAI/bge-reranker-base | 0.8571 | 0.8644 | 0.9286 | 0.1071 | 0.1071 | 1.389 s |

`BAAI/bge-reranker-base` is the highest on MRR and nDCG. Recall@10 is 0.9286 for every reranker: 13 scored questions have their evidence in the top 10, and one does not. On the default reranker that question is gold-026. Its gold section is `Carbon_New_2040#8`, and that chunk is outside the top 10. Jina is the lowest on MRR and nDCG and the fastest, at 0.281 seconds per question. BGE takes 1.389 seconds.

Precision and precision@10 match on each row because every scored query returned 10 chunks. Precision stays near 0.11 because the mean relevant set is 1.14 chunks and the list is 10 long. The ceiling when recall is 1 is 0.1143. These rows sit at 0.1071 because one evidence chunk is missing.

The default reranker is `BAAI/bge-reranker-base`.
