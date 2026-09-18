"""
src/rag/core_engine.py
RAG Engine for Kuli AI.
Handles query rewriting, retrieval, and generating the response.
"""

import os
import sys
import httpx
from typing import Generator, Dict, Any, Optional, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from src.rag.retriever import get_context_with_metadata
from src.rag.prompts import SYSTEM_PROMPT, extract_citations
from src.rag.query_rewriter import rewrite_query

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "kuli-qwen-7b")


def is_ollama_available(base_url: str = OLLAMA_BASE_URL, timeout: float = 1.5) -> bool:
    """Checks whether the Ollama daemon is reachable on localhost."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def get_available_ollama_models(base_url: str = OLLAMA_BASE_URL) -> List[str]:
    """Queries Ollama for currently installed local models."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    return []


def get_ollama_llm(model_name: str = DEFAULT_OLLAMA_MODEL, temperature: float = 0.1):
    """Instantiates ChatOllama with configured decoding parameters."""
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=model_name,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        top_p=0.85,
        num_predict=1024,
    )


def build_chat_prompt() -> ChatPromptTemplate:
    """
    Builds a LCEL prompt template with:
    - System prompt (strict formatting + anti-hallucination)
    - Conversation history (MessagesPlaceholder for multi-turn memory)
    - Retrieved RAG context injected into system message
    - Current user question
    """
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT + "\n\nRetrieved Context:\n{context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ])


def _convert_history(chat_history: List[Dict[str, str]]) -> List:
    """Converts simple {role, content} dicts to LangChain message objects."""
    messages = []
    for turn in chat_history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    return messages


def stream_rag_response(
    query: str,
    use_rag: bool = True,
    use_reranker: bool = True,
    use_query_rewrite: bool = True,
    temperature: float = 0.1,
    model_name: str = DEFAULT_OLLAMA_MODEL,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator yielding token deltas alongside retrieved context and citation metadata.

    Yields dicts with keys:
      - "type": "meta" | "token" | "done"
      - "token": str (when type == "token")
      - "context": dict (when type == "meta", includes rewritten_query)
      - "full_text": str (when type == "done")
      - "citations": list (when type == "done")
    """
    if chat_history is None:
        chat_history = []

    # Step 1: Query Rewriting (pre-retrieval)
    rewritten_query, was_rewritten = rewrite_query(query, enabled=use_query_rewrite)
    retrieval_query = rewritten_query

    context_meta = {"context_str": "", "documents": [], "citations": [],
                    "rewritten_query": rewritten_query if was_rewritten else None}

    # Step 2: Hybrid Retrieval (BM25 + Dense + RRF + Cross-Encoder)
    if use_rag:
        try:
            context_meta = get_context_with_metadata(
                query=retrieval_query,
                k_candidates=10,
                top_n=3,
                use_reranker=use_reranker
            )
            context_meta["rewritten_query"] = rewritten_query if was_rewritten else None
        except Exception as e:
            print(f"[CoreEngine] Retrieval failed: {e}")

    # Yield metadata immediately so UI can populate RAG inspector
    yield {"type": "meta", "context": context_meta}

    if not is_ollama_available():
        error_msg = (
            " **Ollama server is not running on `http://localhost:11434`**\n\n"
            "To use **Qwen2.5-Coder-7B** or your custom fine-tuned model:\n"
            "1. Start Ollama: `ollama serve`\n"
            "2. Pull the base model: `ollama pull qwen2.5-coder:7b`\n\n"
            "*Tip: After running the Kaggle notebook, import your fine-tuned model with `ollama create kuli-qwen-7b`.*"
        )
        yield {"type": "token", "token": error_msg}
        yield {"type": "done", "full_text": error_msg, "citations": []}
        return

    try:
        llm = get_ollama_llm(model_name=model_name, temperature=temperature)
        prompt = build_chat_prompt()
        chain = prompt | llm | StrOutputParser()

        full_text = ""
        context_text = context_meta.get("context_str", "") or "No external context retrieved."
        history_messages = _convert_history(chat_history[-10:])  # Sliding window: last 5 turns (10 msgs)

        for chunk in chain.stream({
            "question": query,  # Use original query for generation (natural language)
            "context": context_text,
            "history": history_messages
        }):
            full_text += chunk
            yield {"type": "token", "token": chunk}

        extracted_citations = extract_citations(full_text)
        final_citations = extracted_citations if extracted_citations else context_meta.get("citations", [])

        yield {"type": "done", "full_text": full_text, "citations": final_citations}

    except Exception as e:
        err = f" Inference Error: {str(e)}"
        yield {"type": "token", "token": err}
        yield {"type": "done", "full_text": err, "citations": []}


def run_rag_query(
    query: str,
    use_rag: bool = True,
    use_reranker: bool = True,
    use_query_rewrite: bool = True,
    temperature: float = 0.1,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Non-streaming execution of the full LCEL RAG chain."""
    full_output = ""
    citations = []
    meta = {}

    for event in stream_rag_response(
        query=query,
        use_rag=use_rag,
        use_reranker=use_reranker,
        use_query_rewrite=use_query_rewrite,
        temperature=temperature,
        chat_history=chat_history
    ):
        if event["type"] == "meta":
            meta = event["context"]
        elif event["type"] == "token":
            full_output += event["token"]
        elif event["type"] == "done":
            citations = event.get("citations", [])

    return {
        "query": query,
        "response": full_output,
        "context": meta,
        "citations": citations
    }
