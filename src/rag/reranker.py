"""
src/rag/reranker.py
===================
Cross-Encoder Reranker with "Lost in the Middle" Context Optimization.

Why Reranking is Critical:
  1. Bi-encoders (vector embeddings like all-MiniLM or nomic-embed) compress documents
     into static vectors, losing fine-grained cross-token interactions.
  2. Cross-encoders process (Query, Passage) jointly through all transformer layers,
     producing vastly superior semantic relevance scores.
  3. "Lost in the Middle" Mitigation: LLMs exhibit an inverted U-shaped recall curve;
     they attend strongly to the beginning (primacy effect) and end of the context,
     while frequently missing information buried in the middle.
     This module scores all candidates and strategically positions the most relevant
     code snippet at the absolute top (Index 0) of the prompt context.
"""

from typing import List, Tuple, Optional
from langchain_core.documents import Document

_reranker_instance = None


class ContextReranker:
    """
    Reranks vector-search results using a CrossEncoder model and
    applies context reordering to mitigate the Lost-in-the-Middle phenomenon.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Lazy loader with graceful fallback."""
        try:
            from sentence_transformers import CrossEncoder
            # print(f"Loading Cross-Encoder reranker: {self.model_name}...")
            self.model = CrossEncoder(self.model_name, max_length=512)
        except Exception as e:
            print(f"[Warning] Failed to load CrossEncoder ({e}). Fallback to original order.")
            self.model = None

    def rerank(
        self,
        query: str,
        docs: List[Document],
        top_n: int = 3,
        mitigate_lost_in_middle: bool = True
    ) -> List[Document]:
        """
        Reranks retrieved candidate documents by query relevance.
        
        Args:
            query: The user prompt / coding question.
            docs: List of Document candidates from initial vector retrieval.
            top_n: Number of top documents to return.
            mitigate_lost_in_middle: If True, ensures the #1 most relevant chunk
                                     is placed at Index 0 (top of context).
        """
        if not docs:
            return []

        if self.model is None or len(docs) <= 1:
            return docs[:top_n]

        # Prepare pairs for Cross-Encoder
        pairs = [[query, doc.page_content] for doc in docs]

        try:
            scores = self.model.predict(pairs)
            
            # Attach rerank score to document metadata
            doc_score_pairs = []
            for doc, score in zip(docs, scores):
                doc.metadata["rerank_score"] = float(score)
                doc_score_pairs.append((doc, float(score)))

            # Sort descending by cross-encoder score
            doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
            top_candidates = [doc for doc, _ in doc_score_pairs[:top_n]]

            if not mitigate_lost_in_middle or len(top_candidates) <= 2:
                return top_candidates

            # Lost in the Middle reordering:
            # Place the highest scoring document at the very beginning (Index 0),
            # second highest at the very end, and intermediate ones in the middle.
            # Alternating arrangement: [1st, 3rd, ..., 4th, 2nd]
            reordered: List[Optional[Document]] = [None] * len(top_candidates)
            left = 0
            right = len(top_candidates) - 1
            
            for i, doc in enumerate(top_candidates):
                if i % 2 == 0:
                    reordered[left] = doc
                    left += 1
                else:
                    reordered[right] = doc
                    right -= 1

            return [d for d in reordered if d is not None]

        except Exception as e:
            print(f"[Warning] Reranker prediction failed ({e}). Returning original docs.")
            return docs[:top_n]


def get_reranker() -> ContextReranker:
    """Singleton getter for the reranker instance."""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = ContextReranker()
    return _reranker_instance


if __name__ == "__main__":
    # Test reranker
    sample_docs = [
        Document(page_content="def add(a, b): return a + b", metadata={"filename": "math_utils.py"}),
        Document(page_content="Floyd's Tortoise and Hare algorithm detects cycles in O(N) time and O(1) space.", metadata={"filename": "cs_fundamentals.md"}),
        Document(page_content="Python list comprehension: [x**2 for x in range(10)]", metadata={"filename": "python_builtins.md"}),
    ]
    query = "How do I detect a loop in a linked list using slow and fast pointers?"
    
    reranker = get_reranker()
    results = reranker.rerank(query, sample_docs, top_n=2)
    print(f"\nQuery: {query}\n")
    for i, doc in enumerate(results):
        score = doc.metadata.get("rerank_score", "N/A")
        print(f"[{i+1}] Score: {score:.4f} | Source: {doc.metadata['filename']}")
        print(f"    Content: {doc.page_content}\n")
