"""
src/rag/build_index.py
======================
Code-Aware Knowledge Base Index Builder.

Ingests technical documentation, algorithmic guides, and source files from `rag_docs/`.
Uses AST-aware syntax chunking to preserve complete functions and code blocks.
Embeds using sentence-transformers and persists to ChromaDB.
Also serializes corpus to corpus.pkl for BM25 hybrid retrieval.
"""

import os
import sys
import shutil
import pickle

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rag.chunker import CodeAwareChunker
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DOCS_DIR = "rag_docs"
CHROMA_DB_DIR = os.path.join(DOCS_DIR, "chroma_db")


def get_embedding_model():
    """
    Returns an embedding model.
    Defaults to all-MiniLM-L6-v2 for fast, local embedding generation.
    """
    # Check if user specifically configured Ollama nomic-embed-text
    use_ollama_embed = os.getenv("USE_OLLAMA_EMBED", "0") == "1"
    if use_ollama_embed:
        try:
            from langchain_ollama import OllamaEmbeddings
            print("Using OllamaEmbeddings (nomic-embed-text)...")
            return OllamaEmbeddings(model="nomic-embed-text")
        except Exception as e:
            print(f"Ollama embeddings unavailable ({e}). Falling back to all-MiniLM-L6-v2.")

    # High-speed local embedding model (cached)
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def build_index(force_rebuild: bool = True):
    """
    Parses all documents in rag_docs/ with code-aware chunking
    and indexes them into the persistent Chroma vector store.
    """
    print("=" * 60)
    print(" Kuli AI: Building Code-Aware RAG Knowledge Base")
    print("=" * 60)
    print(f"Source Directory: {DOCS_DIR}")
    print(f"Target Vector DB: {CHROMA_DB_DIR}")

    if force_rebuild and os.path.exists(CHROMA_DB_DIR):
        print("Cleaning existing vector database index...")
        shutil.rmtree(CHROMA_DB_DIR)

    # 1. Chunk documents with code awareness
    print("\n1. Parsing and chunking documents with syntax awareness...")
    chunker = CodeAwareChunker(chunk_size=550, chunk_overlap=60)
    chunks = chunker.chunk_directory(DOCS_DIR)

    if not chunks:
        print(" No documents found in rag_docs/. Aborting index build.")
        return False

    print(f"    Extracted {len(chunks)} syntax-preserved chunks across documents.")

    # Serialize corpus for BM25 hybrid retrieval
    corpus_path = os.path.join(DOCS_DIR, "corpus.pkl")
    try:
        with open(corpus_path, "wb") as f:
            pickle.dump(chunks, f)
        print(f"    BM25 corpus serialized to {corpus_path}")
    except Exception as e:
        print(f"   [Warning] Failed to serialize BM25 corpus: {e}")

    # Breakdown by language and document
    doc_stats = {}
    lang_stats = {}
    for c in chunks:
        fname = c.metadata.get("filename", "unknown")
        lang = c.metadata.get("language", "unknown")
        doc_stats[fname] = doc_stats.get(fname, 0) + 1
        lang_stats[lang] = lang_stats.get(lang, 0) + 1

    print("\n   Chunk distribution by document:")
    for fname, count in doc_stats.items():
        print(f"     - {fname:<25}: {count:>3} chunks")

    print("\n   Chunk distribution by language:")
    for lang, count in lang_stats.items():
        print(f"     - {lang:<12}: {count:>3} chunks")

    # 2. Embed and persist
    print("\n2. Initializing embedding model...")
    embeddings = get_embedding_model()

    print(f"\n3. Persisting vectors to ChromaDB at {CHROMA_DB_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

    print("\n Knowledge base index successfully built and persisted!")
    print(f"Total documents indexed: {len(chunks)}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    build_index(force_rebuild=True)
