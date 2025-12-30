#!/bin/bash
# Quick start script for Content Safety Lab

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Try multiple possible paths to shared venv
SHARED_ENV1="$SCRIPT_DIR/../../../01-use-azure-ai-services/Python/venv"
SHARED_ENV2="$SCRIPT_DIR/../../01-use-azure-ai-services/Python/venv"
SHARED_ENV3="$(cd "$SCRIPT_DIR/../../.." && pwd)/mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/venv"

cd "$SCRIPT_DIR"

# Activate shared virtual environment
if [ -d "$SHARED_ENV1" ]; then
    source "$SHARED_ENV1/bin/activate"
elif [ -d "$SHARED_ENV2" ]; then
    source "$SHARED_ENV2/bin/activate"
elif [ -d "$SHARED_ENV3" ]; then
    source "$SHARED_ENV3/bin/activate"
else
    echo "Error: Virtual environment not found"
    echo "Tried: $SHARED_ENV1"
    echo "Tried: $SHARED_ENV2"
    echo "Tried: $SHARED_ENV3"
    exit 1
fi

# Run the Content Safety application
python prompt-shield.py

