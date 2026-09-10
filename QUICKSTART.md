# Quick Start Guide

## Complete Setup in 5 Steps

### Step 1: Initialize Project
```bash
cd ~/Projects/personal/ai-model-neosurgery
bash setup.sh
source .venv/bin/activate
```

### Step 2: Copy Your PDFs
```bash
# Copy all your research papers to the pdfs/ directory
cp ~/Downloads/*.pdf pdfs/
# or
cp /path/to/your/pdfs/*.pdf pdfs/
```

### Step 3: Install & Start Ollama
```bash
# Download from https://ollama.ai and install
# Then run in a separate terminal:
ollama serve

# In another terminal, pull the model:
ollama pull mistral
```

### Step 4: Extract PDFs to Markdown
```bash
# From project directory (with .venv activated)
python3 main.py extract --pdf-dir pdfs --output-dir data/markdown
```

This creates markdown files in `data/markdown/` that are ready for Obsidian.

### Step 5: Build Vector Index & Query
```bash
# Build the searchable index
python3 main.py index --markdown-dir data/markdown --index-dir data/vectorstore

# Start interactive mode
python3 main.py query --index-dir data/vectorstore
```

## File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point - run all commands from here |
| `src/pdf_extractor.py` | Converts PDFs → Markdown with metadata |
| `src/knowledge_indexer.py` | Creates vector index from markdown files |
| `src/rag_query.py` | Interactive query interface with LLM |
| `config.py` | Configuration settings (model, paths, prompts) |
| `requirements.txt` | Python dependencies |
| `setup.sh` | Automated setup script |

## Example Queries

Once running, you can ask questions like:

- "What are the latest treatment options for glioblastoma?"
- "Explain the surgical approach for glioblastoma resection"
- "What is the prognosis for grade IV glioblastoma?"
- "Compare temozolomide and radiation therapy effectiveness"
- "What are the complications of glioblastoma surgery?"

## Troubleshooting

**"Connection refused" when querying**
- Make sure `ollama serve` is running in another terminal

**"No documents found"**
- Check PDFs are in `pdfs/` directory and have readable text

**"Model not found"**
- Run `ollama pull mistral` to download the model

**"Out of memory"**
- Reduce `RETRIEVAL_K` in `config.py` (default: 5)

## Next Steps

1. **Add More PDFs**: Copy additional research papers to `pdfs/`
2. **Re-index**: Run `extract` and `index` again to update knowledge base
3. **Customize**: Edit `config.py` to adjust:
   - LLM model (try "llama2", "neural-chat", etc.)
   - Chunk size (affects accuracy vs speed)
   - Retrieval k (number of documents to reference)

## For Obsidian Integration

The extracted markdown files in `data/markdown/` are ready to use in Obsidian:

1. Create a new vault in Obsidian
2. Copy markdown files from `data/markdown/` into the vault
3. Use Obsidian's knowledge graph to explore connections
4. Add your own notes and tags

## Performance Notes

- **First query**: ~5-10 seconds (model loading)
- **Subsequent queries**: 2-5 seconds (on CPU)
- **Indexing 100 PDFs**: ~30-60 seconds
- **Storage**: ~100MB for 100 papers (vector index)
