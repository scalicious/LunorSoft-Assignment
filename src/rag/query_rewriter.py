"""
src/rag/query_rewriter.py
==========================
Pre-Retrieval Query Rewriting using LangChain LCEL.

Why Query Rewriting?
  Student queries are often vague, colloquial, or multi-intent:
    "how does that linked list thing work?" → poor retrieval
    "cycle detection in linked list using Floyd's two-pointer algorithm" → excellent retrieval

  This module wraps a lightweight LCEL chain (ChatOllama) that transforms
  the raw user query into a concise, retrieval-optimized technical query
  before it hits the vector store or BM25 index.

  Falls back gracefully to the original query if Ollama is unavailable.
"""

import os
import sys
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

_rewriter_chain = None

REWRITE_SYSTEM_PROMPT = """You are a search query optimizer for a computer science knowledge base.

Your ONLY job: rewrite the user's question into a concise, technical, retrieval-optimized query of 1-2 sentences.

Rules:
- Use precise technical terminology (e.g., "binary search on answer", "O(N log N)", "Floyd's algorithm")
- Remove filler words ("can you", "how do I", "please explain")
- Preserve the original intent exactly
- Output ONLY the rewritten query - no explanation, no preamble

Example:
Input:  "hey can you explain how that cycle thing works in linked lists"
Output: "cycle detection in linked list using Floyd's Tortoise and Hare two-pointer algorithm"
"""


def get_rewriter_chain():
    """Lazy-loaded LangChain LCEL rewriting chain."""
    global _rewriter_chain
    if _rewriter_chain is not None:
        return _rewriter_chain

    try:
        from langchain_ollama import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        import os

        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "kuli-qwen-7b"),
            base_url=ollama_url,
            temperature=0.0,  # Deterministic rewriting
            num_predict=80,    # Short output only
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", REWRITE_SYSTEM_PROMPT),
            ("human", "{query}")
        ])
        _rewriter_chain = prompt | llm | StrOutputParser()
        return _rewriter_chain
    except Exception as e:
        print(f"[QueryRewriter] Could not load rewriter chain: {e}")
        return None


def rewrite_query(query: str, enabled: bool = True) -> tuple[str, bool]:
    """
    Rewrites a user query for better retrieval precision.

    Args:
        query: The raw user query string.
        enabled: Whether query rewriting is toggled on.

    Returns:
        (rewritten_query, was_rewritten) tuple.
        If disabled or unavailable, returns (original_query, False).
    """
    if not enabled or len(query.split()) <= 4:
        # Very short queries don't need rewriting (likely already precise)
        return query, False

    chain = get_rewriter_chain()
    if chain is None:
        return query, False

    try:
        rewritten = chain.invoke({"query": query}).strip()
        # Sanity check: reject if the rewriter hallucinated something too different
        if not rewritten or len(rewritten) > 300 or len(rewritten) < 5:
            return query, False
        return rewritten, True
    except Exception as e:
        print(f"[QueryRewriter] Rewrite failed: {e}")
        return query, False


if __name__ == "__main__":
    test_queries = [
        "hey can you show me that cycle thing in linked lists",
        "aggressive cows problem explanation",
        "how does lora work and why is it better",
        "what is the best way to sort quickly",
    ]
    print("Query Rewriter Test\n" + "=" * 50)
    for q in test_queries:
        rewritten, changed = rewrite_query(q)
        status = " Rewritten" if changed else "- Original"
        print(f"\n{status}")
        print(f"  Input:  {q}")
        print(f"  Output: {rewritten}")
