#!/bin/bash
# Quick start script for RAG with Own Data Lab

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SHARED_PYTHON_DIR="$(cd "$SCRIPT_DIR/../../../mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python" && pwd)"

cd "$SCRIPT_DIR"

# Activate shared virtual environment
if [ -d "$SHARED_PYTHON_DIR/venv" ]; then
    source "$SHARED_PYTHON_DIR/venv/bin/activate"
else
    echo "Error: Virtual environment not found at $SHARED_PYTHON_DIR/venv"
    exit 1
fi

# Run the RAG application
python ownData.py

