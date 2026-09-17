"""
src/rag/prompts.py
==================
Educational Coding Assistant Prompts & Citation Grounding Templates.

Enforces pedagogical structure:
  1. Title / High-level overview
  2. Syntactically clean code block with type hints and comments
  3. Step-by-step logic walkthrough
  4. Time & Space complexity analysis
  5. Explicit file/doc citation provenance
"""

import re
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# System prompt for engineering students & interview evaluation
SYSTEM_PROMPT = """You are Kuli, an AI Coding Assistant.

CRITICAL INSTRUCTIONS:
- You must respond in STRICTLY ENGLISH ONLY. Do NOT output any Chinese characters, symbols, or non-English text.
- Avoid common AI phrases like "Let's break this down", "Here is a", or "In conclusion". Be direct, concise, and sound like a human engineer.
- NEVER hallucinate methods, APIs, or classes. Only use standard libraries or what is explicitly provided.
- Format your response exactly as follows:
  1. Title (H1) / High-level overview
  2. Syntactically clean code block with type hints and comments (no broken symbols)
  3. Step-by-step logic walkthrough
  4. Time & Space complexity analysis (using Big-O notation)

GROUNDING & CITATIONS:
When context is provided from documentation or source files, you MUST cite the specific file and section you referenced using the format:
`[Source: <filename> | Section: <section>]`
Example: `[Source: cpp_guide.md | Section: Dynamic Programming]`
Do not cite files that were not provided in the context.
"""

RAG_PROMPT_TEMPLATE = """{system_prompt}

Context Information:
---------------------
{context}
---------------------

Based on the context above (if relevant) and your knowledge, answer the user's question.

User Question:
{question}

Answer:"""

CHAT_RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT + "\n\nRetrieved Context:\n{context}"),
    ("human", "{question}")
])


def format_docs_with_citations(docs: List[Any]) -> str:
    """
    Formats retrieved documents into context blocks annotated with
    filename and section for clear provenance and LLM citation grounding.
    """
    if not docs:
        return "No external context retrieved."

    formatted_blocks = []
    for idx, doc in enumerate(docs):
        fname = doc.metadata.get("filename", "unknown_source")
        sec = doc.metadata.get("section", "General")
        lang = doc.metadata.get("language", "text")
        rerank_score = doc.metadata.get("rerank_score")
        score_str = f" | Relevance: {rerank_score:.3f}" if rerank_score is not None else ""

        header = f"--- Document [{idx+1}]: {fname} | Section: {sec}{score_str} ---"
        body = doc.page_content.strip()
        formatted_blocks.append(f"{header}\n{body}")

    return "\n\n".join(formatted_blocks)


def extract_citations(text: str) -> List[Dict[str, str]]:
    """
    Extracts citation references from the model output.
    Matches formats like:
      - [Source: filename.md | Section: section_name]
      - Based on filename.md, section ...
      - [Source: filename.md]
    """
    citations = []
    
    # Pattern 1: [Source: filename.md | Section: section_name]
    pattern1 = re.compile(r'\[Source:\s*([^\|\]]+)(?:\|\s*Section:\s*([^\]]+))?\]', re.IGNORECASE)
    for match in pattern1.finditer(text):
        fname = match.group(1).strip()
        section = match.group(2).strip() if match.group(2) else "General"
        citations.append({"file": fname, "section": section})

    # Pattern 2: Based on filename.md
    pattern2 = re.compile(r'Based on\s+([a-zA-Z0-9_\-\.]+\.(?:md|py|cpp|hpp))', re.IGNORECASE)
    for match in pattern2.finditer(text):
        fname = match.group(1).strip()
        if not any(c["file"] == fname for c in citations):
            citations.append({"file": fname, "section": "Referenced"})

    return citations
