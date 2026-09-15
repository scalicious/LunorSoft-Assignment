#!/usr/bin/env bash
# =============================================================================
# Kuli AI - Application Launcher
# =============================================================================

set -e

# Change directory to project root
cd "$(dirname "$0")"

echo " Starting Kuli AI Engineering Copilot..."

# Check virtual environment
if [ -d "venv" ]; then
    echo " Activating virtual environment (venv)..."
    source venv/bin/activate
else
    echo " Warning: venv not found. Using system python."
fi

# Check if index exists; build if missing
if [ ! -d "rag_docs/chroma_db" ]; then
    echo " ChromaDB index not found. Building code-aware index..."
    python src/rag/build_index.py
fi

# Check Ollama daemon status
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo " Ollama daemon detected at http://localhost:11434 (7B Model Ready)"
else
    echo " Note: Ollama daemon not running. App will offer local fallback."
fi

echo " Launching Streamlit Interface on http://localhost:8501"
streamlit run src/app/app.py
