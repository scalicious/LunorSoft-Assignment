.PHONY: help setup index run eval clean test

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

help:
	@echo "Kuli AI — Engineering Copilot Build System"
	@echo "============================================"
	@echo "make setup    : Install dependencies in virtual environment"
	@echo "make index    : Rebuild ChromaDB index with AST-aware chunking"
	@echo "make run      : Launch the Streamlit IDE application"
	@echo "make eval     : Run the automated evaluation suite"
	@echo "make clean    : Remove cache and temporary runtime artifacts"

setup:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

index:
	$(PYTHON) src/rag/build_index.py

run:
	$(STREAMLIT) run src/app/app.py

eval:
	$(PYTHON) src/evaluation/evaluate.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
