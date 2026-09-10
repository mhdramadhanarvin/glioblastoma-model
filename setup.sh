#!/bin/bash
# Setup script for AI Medical Knowledge Base

set -e

echo "=================================="
echo "AI Medical Knowledge Base Setup"
echo "=================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p pdfs data/markdown data/vectorstore
echo "✓ Directories created"
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Add PDF files to: pdfs/"
echo "2. Start Ollama server: ollama serve"
echo "3. Extract PDFs: python3 main.py extract"
echo "4. Build index: python3 main.py index"
echo "5. Query: python3 main.py query"
echo ""
echo "For help: python3 main.py --help"
