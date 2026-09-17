"""
src/rag/hybrid_retriever.py
============================
Hybrid BM25 + Dense Vector Retriever with Reciprocal Rank Fusion (RRF).

Why Hybrid Search?
  - Dense vector search (ChromaDB/all-MiniLM) excels at semantic similarity
    but is "keyword blind" - it may miss exact technical terms like `lower_bound`,
    `Floyd's Tortoise`, or `O(log N)`.
  - BM25 (sparse TF-IDF) excels at exact keyword matching but misses
    semantic synonyms (e.g., "loop detection" vs "cycle detection").
  - Reciprocal Rank Fusion (RRF) merges ranked lists from both systems:
      score(d) = Σ 1 / (k + rank_i(d))  where k=60 (standard constant)
  - This consistently outperforms either system alone by 10-20% on recall.
"""

import os
import sys
import pickle
from typing import List, Optional
from langchain_core.documents import Document

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

CORPUS_CACHE_PATH = os.path.join("rag_docs", "corpus.pkl")

_bm25_model = None
_bm25_docs: List[Document] = []


def _load_bm25(corpus_path: str = CORPUS_CACHE_PATH):
    """Loads the BM25 index from a serialized corpus of Documents."""
    global _bm25_model, _bm25_docs
    if _bm25_model is not None:
        return _bm25_model, _bm25_docs

    if not os.path.exists(corpus_path):
        return None, []

    try:
        from rank_bm25 import BM25Okapi
        with open(corpus_path, "rb") as f:
            _bm25_docs = pickle.load(f)

        tokenized_corpus = [
            doc.page_content.lower().split() for doc in _bm25_docs
        ]
        _bm25_model = BM25Okapi(tokenized_corpus)
        return _bm25_model, _bm25_docs
    except ImportError:
        print("[HybridRetriever] Warning: `rank-bm25` not installed. BM25 disabled.")
        return None, []
    except Exception as e:
        print(f"[HybridRetriever] Warning: Failed to load BM25 corpus ({e}). BM25 disabled.")
        return None, []


def _bm25_retrieve(query: str, k: int = 20) -> List[Document]:
    """Returns top-k documents by BM25 keyword score."""
    bm25, docs = _load_bm25()
    if bm25 is None or not docs:
        return []

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    scored = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [docs[i] for i, _ in scored[:k]]


def reciprocal_rank_fusion(
    ranked_lists: List[List[Document]],
    k: int = 60
) -> List[Document]:
    """
    Merges multiple ranked document lists using Reciprocal Rank Fusion.
    score(d) = sum( 1 / (k + rank(d)) )  for each list containing d.
    Documents are de-duplicated by chunk_id metadata.
    """
    doc_scores = {}
    doc_map = {}

    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list):
            doc_id = doc.metadata.get("chunk_id", doc.page_content[:64])
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0.0
                doc_map[doc_id] = doc
            doc_scores[doc_id] += 1.0 / (k + rank + 1)

    sorted_ids = sorted(doc_scores, key=doc_scores.__getitem__, reverse=True)
    result = []
    for doc_id in sorted_ids:
        doc = doc_map[doc_id]
        doc.metadata["rrf_score"] = round(doc_scores[doc_id], 6)
        result.append(doc)
    return result


def hybrid_retrieve(
    query: str,
    vectorstore,
    k_dense: int = 12,
    k_bm25: int = 12,
    top_n: int = 10
) -> List[Document]:
    """
    Runs dense vector search + BM25, fuses results with RRF.

    Args:
        query: The user's (possibly rewritten) query.
        vectorstore: A LangChain Chroma vectorstore instance.
        k_dense: Number of candidates from dense vector search.
        k_bm25: Number of candidates from BM25 keyword search.
        top_n: Final number of fused candidates to return.

    Returns:
        Fused, de-duplicated list of Documents ranked by RRF score.
    """
    # Stage 1a: Dense vector retrieval
    try:
        dense_results = vectorstore.similarity_search(query, k=k_dense)
    except Exception as e:
        print(f"[HybridRetriever] Dense search failed: {e}")
        dense_results = []

    # Stage 1b: BM25 keyword retrieval
    bm25_results = _bm25_retrieve(query, k=k_bm25)

    # Stage 2: Reciprocal Rank Fusion
    lists_to_fuse = [l for l in [dense_results, bm25_results] if l]
    if not lists_to_fuse:
        return []

    fused = reciprocal_rank_fusion(lists_to_fuse)
    return fused[:top_n]


if __name__ == "__main__":
    from src.rag.retriever import get_vectorstore
    vs = get_vectorstore()
    query = "How to detect a cycle in a linked list using Floyd's algorithm?"
    results = hybrid_retrieve(query, vs, top_n=5)
    print(f"\nHybrid Retrieval Results for: '{query}'")
    for i, doc in enumerate(results):
        rrf = doc.metadata.get("rrf_score", 0)
        fname = doc.metadata.get("filename", "unknown")
        print(f"  [{i+1}] RRF={rrf:.5f} | {fname} | {doc.page_content[:80].strip()}...")
