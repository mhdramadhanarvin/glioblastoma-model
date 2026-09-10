# Installation & Verification Checklist

## Pre-requisites Check

- [ ] Python 3.8+ installed
  ```bash
  python3 --version
  ```

- [ ] Git available (for version control)
  ```bash
  git --version
  ```

- [ ] ~5GB free disk space (for Ollama models)
  ```bash
  df -h
  ```

## Step-by-Step Installation

### 1. Clone/Setup Project
```bash
cd ~/Projects/personal/ai-model-neosurgery
```

### 2. Run Setup Script
```bash
bash setup.sh
source .venv/bin/activate
```

### 3. Install Ollama
```bash
# Download from https://ollama.ai
# Follow platform-specific instructions

# Verify installation
ollama --version

# Download Mistral model (first time only)
ollama pull mistral
```

### 4. Start Ollama Server
```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Keep this running while using the system
```

### 5. Add Your PDFs
```bash
# Copy research papers
cp ~/Downloads/*.pdf pdfs/
ls pdfs/ | head -5  # Verify PDFs are there
```

### 6. Verify System
```bash
python3 test_system.py
```

Expected output:
```
✓ All systems ready! You can now:
  1. python3 main.py extract
  2. python3 main.py index
  3. python3 main.py query
```

## Running the System

### First Time Setup (with PDFs)

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Activate environment
source .venv/bin/activate

# Step 1: Extract PDFs
python3 main.py extract --pdf-dir pdfs --output-dir data/markdown
# Wait for: "✓ Success: X | ✗ Failed: Y"

# Step 2: Build index
python3 main.py index --markdown-dir data/markdown --index-dir data/vectorstore
# Wait for: "✓ Index saved to data/vectorstore"

# Step 3: Start querying
python3 main.py query --index-dir data/vectorstore
# You should see: "Your question: "
```

### Subsequent Usage

```bash
# Keep Ollama running
# Then just run:
python3 main.py query
```

## Troubleshooting

### Problem: "Ollama connection refused"
```bash
# Solution: Check Ollama is running
ps aux | grep ollama

# If not running:
ollama serve  # in another terminal
```

### Problem: "Model not found"
```bash
# Solution: Download the model
ollama pull mistral
```

### Problem: "No PDFs found"
```bash
# Solution: Check PDF directory
ls pdfs/
file pdfs/*.pdf  # Verify they're actual PDFs
```

### Problem: "Vector index not found"
```bash
# Solution: Run indexing first
python3 main.py index
```

### Problem: Out of memory
```bash
# Solution 1: Reduce chunk size in config.py
# Change: PDF_CHUNK_SIZE = 500  (from 1000)

# Solution 2: Reduce retrieval k
# Change: RETRIEVAL_K = 3  (from 5)

# Solution 3: Use smaller model
# ollama pull orca-mini
# Edit config.py: MODEL_NAME = "orca-mini"
```

### Problem: Very slow on first query
```bash
# This is normal - Ollama is loading the model (5-10 seconds)
# Subsequent queries will be faster (2-5 seconds)
```

## File Structure Verification

```bash
# Verify all required files exist
test -f main.py && echo "✓ main.py"
test -f requirements.txt && echo "✓ requirements.txt"
test -d src && echo "✓ src/"
test -d pdfs && echo "✓ pdfs/"
test -d data && echo "✓ data/"

# Verify Python scripts
test -f src/pdf_extractor.py && echo "✓ pdf_extractor.py"
test -f src/knowledge_indexer.py && echo "✓ knowledge_indexer.py"
test -f src/rag_query.py && echo "✓ rag_query.py"
```

## Next Steps After Setup

1. **Add More PDFs**: Copy additional research papers to `pdfs/`
2. **Re-index**: Run extraction and indexing again
3. **Customize**: Edit `config.py` for different models or settings
4. **Obsidian Integration**: Copy `data/markdown/` files to Obsidian vault
5. **Batch Processing**: Use `examples.py` for advanced workflows

## Quick Reference Commands

```bash
# Extract PDFs
python3 main.py extract

# Build index
python3 main.py index

# Interactive query
python3 main.py query

# Run tests
python3 test_system.py

# Show examples
python3 examples.py

# Help
python3 main.py --help
```

## Performance Expectations

| Task | Time | Specs |
|------|------|-------|
| Extract 100 PDFs | 1-2 min | CPU-only |
| Index 100 PDFs | 30-60 sec | CPU-only |
| First query | 5-10 sec | Model loading |
| Typical query | 2-5 sec | CPU-only |

---

**Created**: 2026-09-10
**Last Updated**: 2026-09-10
