"""
src/rag/retriever.py
====================
Two-Stage Retriever with Cross-Encoder Reranking & Lost-in-the-Middle Mitigation.

Stage 1: Dense Vector Retrieval (ChromaDB)
  - Fetches top-K candidate chunks using cosine similarity / inner product.
Stage 2: Cross-Encoder Joint Reranking
  - Evaluates cross-attention between user query and candidates.
  - Mitigates Lost-in-the-Middle by positioning top chunk at Index 0.
Stage 3: Context & Citation Formatting
  - Formats chunks with explicit document headers for citation extraction.
"""

import os
import sys
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rag.reranker import get_reranker
from src.rag.prompts import format_docs_with_citations, extract_citations
from src.rag.hybrid_retriever import hybrid_retrieve

DOCS_DIR = "rag_docs"
CHROMA_DB_DIR = os.path.join(DOCS_DIR, "chroma_db")

_vectorstore = None
_embeddings = None


def get_vectorstore() -> Chroma:
    """Singleton getter for the persistent Chroma vector store."""
    global _vectorstore, _embeddings
    if _vectorstore is None:
        if not os.path.exists(CHROMA_DB_DIR):
            raise RuntimeError(
                f"Chroma DB index not found at '{CHROMA_DB_DIR}'. "
                "Please run `python src/rag/build_index.py` first to generate the index."
            )
        
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=_embeddings
        )
    return _vectorstore


def retrieve_and_rerank(
    query: str,
    k_candidates: int = 10,
    top_n: int = 3,
    use_reranker: bool = True,
    mitigate_lost_in_middle: bool = True
) -> List[Document]:
    """
    Executes hybrid three-stage retrieval:
      1. Dense vector search (ChromaDB) for semantic matches.
      2. BM25 keyword search for exact technical term matches.
      3. Reciprocal Rank Fusion of both result lists.
      4. Cross-Encoder reranking to select and order the `top_n` most relevant chunks.
    """
    vs = get_vectorstore()

    # 1+2+3: Hybrid dense + BM25 + RRF
    candidates = hybrid_retrieve(
        query=query,
        vectorstore=vs,
        k_dense=k_candidates,
        k_bm25=k_candidates,
        top_n=k_candidates
    )

    if not candidates:
        return []

    # 4. Cross-Encoder reranking
    if use_reranker and len(candidates) > 1:
        reranker = get_reranker()
        ranked_docs = reranker.rerank(
            query=query,
            docs=candidates,
            top_n=top_n,
            mitigate_lost_in_middle=mitigate_lost_in_middle
        )
        return ranked_docs

    return candidates[:top_n]


def get_context(
    query: str,
    k: int = 3,
    use_reranker: bool = True
) -> str:
    """
    Convenience method returning a formatted context string ready for LLM injection.
    """
    docs = retrieve_and_rerank(query, k_candidates=max(k * 3, 6), top_n=k, use_reranker=use_reranker)
    return format_docs_with_citations(docs)


def get_context_with_metadata(
    query: str,
    k_candidates: int = 10,
    top_n: int = 3,
    use_reranker: bool = True
) -> Dict[str, Any]:
    """
    Returns rich context including raw documents, rerank scores, and initial citations.
    Useful for UI inspectors, debugger drawers, and evaluation metrics.
    """
    docs = retrieve_and_rerank(
        query=query,
        k_candidates=k_candidates,
        top_n=top_n,
        use_reranker=use_reranker
    )

    formatted_context = format_docs_with_citations(docs)
    
    citations = []
    for doc in docs:
        citations.append({
            "filename": doc.metadata.get("filename", "unknown"),
            "section": doc.metadata.get("section", "General"),
            "rerank_score": doc.metadata.get("rerank_score"),
            "source": doc.metadata.get("source")
        })

    return {
        "context_str": formatted_context,
        "documents": docs,
        "citations": citations,
        "count": len(docs)
    }


if __name__ == "__main__":
    test_query = "How do I implement binary search on answer for Aggressive Cows in C++?"
    print(f"Query: {test_query}\n")
    res = get_context_with_metadata(test_query, top_n=2)
    print(f"Retrieved {res['count']} documents:")
    for c in res['citations']:
        score_str = f" (score: {c['rerank_score']:.3f})" if c['rerank_score'] is not None else ""
        print(f" - {c['filename']} > {c['section']}{score_str}")
    print("\nFormatted Context Snippet:")
    print(res['context_str'][:400] + "...")
