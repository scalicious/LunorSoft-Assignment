"""
src/app/inference.py
Inference API for Kuli AI.
Delegates execution to Ollama and handles streaming.
"""

import os
import sys
from typing import Generator, Dict, Any, List, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rag.core_engine import (
    stream_rag_response,
    run_rag_query,
    DEFAULT_OLLAMA_MODEL
)


def stream_response(
    prompt: str,
    model_name: str = DEFAULT_OLLAMA_MODEL,
    use_rag: bool = True,
    use_reranker: bool = True,
    use_query_rewrite: bool = True,
    temperature: float = 0.1,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Unified streaming entrypoint for the Streamlit UI.

    Yields event dicts: {"type": "meta"|"token"|"done", ...}
    """
    yield from stream_rag_response(
        query=prompt,
        use_rag=use_rag,
        use_reranker=use_reranker,
        use_query_rewrite=use_query_rewrite,
        temperature=temperature,
        model_name=model_name,
        chat_history=chat_history or []
    )


def generate_response(
    prompt: str,
    model_name: str = DEFAULT_OLLAMA_MODEL,
    use_rag: bool = True,
    use_reranker: bool = True,
    use_query_rewrite: bool = True,
    temperature: float = 0.1,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """Non-streaming backward-compatible helper returning plain text."""
    res = run_rag_query(
        query=prompt,
        use_rag=use_rag,
        use_reranker=use_reranker,
        use_query_rewrite=use_query_rewrite,
        temperature=temperature,
        chat_history=chat_history
    )
    
    response_text = res["response"]
    citations = res.get("citations", [])
    
    # If the LLM didn't natively format citations in the text but RAG returned them, append them manually
    if citations and "Source:" not in response_text:
        response_text += "\n\n**Citations:**\n"
        for i, c in enumerate(citations):
            file_name = c.get("filename", c.get("file", "unknown"))
            response_text += f"[{i+1}] [Source: {file_name}]\n"
            
    return response_text
