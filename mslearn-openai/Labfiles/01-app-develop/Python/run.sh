#!/bin/bash
# Quick start script for Azure OpenAI Lab 1

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

# Run the Azure OpenAI application
python application.py

