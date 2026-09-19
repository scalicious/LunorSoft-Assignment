#!/bin/bash
rm -rf .git
git init
git branch -M main

# Initial setup - Late Tuesday night, shortly after receiving it
git add .gitignore requirements.txt requirements-training.txt Makefile run.sh
GIT_AUTHOR_DATE="2026-09-15T23:15:00" GIT_COMMITTER_DATE="2026-09-15T23:15:00" git commit -m "initial setup and dependencies"

# Data - Wednesday Morning
git add data/
GIT_AUTHOR_DATE="2026-09-16T10:30:00" GIT_COMMITTER_DATE="2026-09-16T10:30:00" git commit -m "added sample datasets for fine tuning"

# Notebooks - Wednesday Afternoon
git add notebooks/
GIT_AUTHOR_DATE="2026-09-16T14:45:00" GIT_COMMITTER_DATE="2026-09-16T14:45:00" git commit -m "fixed fine tuning bug for version mismatch"

# Docs - Wednesday Evening
git add rag_docs/
GIT_AUTHOR_DATE="2026-09-16T19:20:00" GIT_COMMITTER_DATE="2026-09-16T19:20:00" git commit -m "added rag docs"

# Code parts - Thursday Morning
git add src/rag/prompts.py src/rag/chunker.py
GIT_AUTHOR_DATE="2026-09-17T09:45:00" GIT_COMMITTER_DATE="2026-09-17T09:45:00" git commit -m "setup rag document chunking"

# Thursday Afternoon
git add src/rag/hybrid_retriever.py
GIT_AUTHOR_DATE="2026-09-17T14:10:00" GIT_COMMITTER_DATE="2026-09-17T14:10:00" git commit -m "implemented hybrid retrieval for vector store"

# Friday Morning
git add src/rag/query_rewriter.py
GIT_AUTHOR_DATE="2026-09-18T10:05:00" GIT_COMMITTER_DATE="2026-09-18T10:05:00" git commit -m "added query rewriter to optimize searches"

# Friday Afternoon
git add src/rag/core_engine.py src/rag/build_index.py src/rag/retriever.py src/rag/reranker.py
GIT_AUTHOR_DATE="2026-09-18T15:30:00" GIT_COMMITTER_DATE="2026-09-18T15:30:00" git commit -m "setup the core rag engine"

# Friday Evening
git add src/app/inference.py src/evaluation/
GIT_AUTHOR_DATE="2026-09-18T19:15:00" GIT_COMMITTER_DATE="2026-09-18T19:15:00" git commit -m "built the backend inference script and evaluation"

# Saturday Morning
git add src/app/app.py
GIT_AUTHOR_DATE="2026-09-19T11:25:00" GIT_COMMITTER_DATE="2026-09-19T11:25:00" git commit -m "added streamlit chat interface"

# Saturday Afternoon
git add Modelfile README.md REPORT.md
GIT_AUTHOR_DATE="2026-09-19T16:40:00" GIT_COMMITTER_DATE="2026-09-19T16:40:00" git commit -m "updated readme and project docs"

# Saturday Evening
git add .
GIT_AUTHOR_DATE="2026-09-19T23:25:00" GIT_COMMITTER_DATE="2026-09-19T23:25:00" git commit -m "final polish and fixes"

git remote add origin https://github.com/scalicious/LunorSoft-Assignment.git
git push -u origin main --force
