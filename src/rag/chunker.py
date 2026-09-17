"""
src/rag/chunker.py
==================
Code-Aware Syntax Chunking Engine.

Standard character-count or token-count chunkers slice arbitrarily through code,
cutting functions in half, breaking ASTs, and confusing LLMs.
This module uses LangChain's language-specific text splitters:
  - RecursiveCharacterTextSplitter.from_language(Language.PYTHON)
  - RecursiveCharacterTextSplitter.from_language(Language.CPP)
  - MarkdownHeaderTextSplitter for structured technical documentation

Each chunk is enriched with metadata:
  - source_file: file path of origin
  - filename: base filename (for quick citation in prompts)
  - language: 'python', 'cpp', 'markdown', or 'text'
  - section: nearest markdown header or code construct
  - chunk_id: deterministic identifier
"""

import os
import re
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language,
    MarkdownHeaderTextSplitter
)


class CodeAwareChunker:
    """
    Intelligent chunker that selects splitting strategies based on file type
    and preserves logical code boundaries (functions, classes, blocks).
    """

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Specialized AST-aware splitters for code
        self.py_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.cpp_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.CPP,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Splitter for general markdown / technical text
        self.md_headers = [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ]
        self.md_header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.md_headers,
            strip_headers=False
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""]
        )

    def detect_language(self, filepath: str) -> str:
        """Infer programming or markup language from file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.py']:
            return 'python'
        elif ext in ['.cpp', '.cc', '.cxx', '.hpp', '.h']:
            return 'cpp'
        elif ext in ['.md', '.markdown']:
            return 'markdown'
        return 'text'

    def chunk_file(self, filepath: str) -> List[Document]:
        """Loads and splits a single file preserving its structural boundaries."""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Target document not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        filename = os.path.basename(filepath)
        lang = self.detect_language(filepath)

        raw_docs: List[Document] = []

        if lang == 'python':
            splits = self.py_splitter.split_text(content)
            for i, text in enumerate(splits):
                raw_docs.append(Document(
                    page_content=text,
                    metadata={"section": "Python Implementation", "sub_idx": i}
                ))

        elif lang == 'cpp':
            splits = self.cpp_splitter.split_text(content)
            for i, text in enumerate(splits):
                raw_docs.append(Document(
                    page_content=text,
                    metadata={"section": "C++ Implementation", "sub_idx": i}
                ))

        elif lang == 'markdown':
            # Two-stage splitting: Header-based first, then recursive chunking if sections are large
            header_splits = self.md_header_splitter.split_text(content)
            for h_doc in header_splits:
                header_parts = [
                    h_doc.metadata.get(k) for _, k in self.md_headers
                    if k in h_doc.metadata
                ]
                section_title = " > ".join(header_parts) if header_parts else "General"

                sub_chunks = self.text_splitter.split_text(h_doc.page_content)
                for j, sub in enumerate(sub_chunks):
                    raw_docs.append(Document(
                        page_content=sub,
                        metadata={"section": section_title, "sub_idx": j}
                    ))
        else:
            splits = self.text_splitter.split_text(content)
            for i, text in enumerate(splits):
                raw_docs.append(Document(
                    page_content=text,
                    metadata={"section": "General", "sub_idx": i}
                ))

        enriched_docs: List[Document] = []
        for idx, doc in enumerate(raw_docs):
            doc.metadata.update({
                "source": filepath,
                "filename": filename,
                "language": lang,
                "chunk_id": f"{filename}#chunk_{idx}",
                "total_chars": len(doc.page_content)
            })
            enriched_docs.append(doc)

        return enriched_docs

    def chunk_directory(self, dirpath: str) -> List[Document]:
        """Recursively parses and chunks all matching files in a directory."""
        all_chunks: List[Document] = []
        valid_extensions = ('.md', '.py', '.cpp', '.hpp', '.txt')

        for root, _, files in os.walk(dirpath):
            if any(part.startswith('.') or part == '__pycache__' or part == 'chroma_db' for part in root.split(os.sep)):
                continue

            for fname in files:
                if fname.endswith(valid_extensions):
                    fpath = os.path.join(root, fname)
                    try:
                        chunks = self.chunk_file(fpath)
                        all_chunks.extend(chunks)
                    except Exception as e:
                        print(f"[Warning] Failed to chunk {fpath}: {e}")

        return all_chunks


if __name__ == "__main__":
    chunker = CodeAwareChunker(chunk_size=500, chunk_overlap=50)
    test_docs = chunker.chunk_directory("rag_docs")
    print(f"Successfully chunked {len(test_docs)} documents.")
    if test_docs:
        print("\nSample Chunk Metadata:")
        print(test_docs[0].metadata)
        print("\nSample Content:")
        print(test_docs[0].page_content[:200] + "...")
