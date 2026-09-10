# AI Medical Knowledge Base for Neurosurgery & Glioblastoma

A self-contained, CPU-friendly RAG (Retrieval-Augmented Generation) system for building and querying a specialized medical knowledge base.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Place Your PDFs

Copy all research papers and medical PDFs into the `pdfs/` directory:

```bash
cp your_papers/*.pdf pdfs/
```

### 3. Extract PDFs to Markdown

```bash
python3 main.py extract --pdf-dir pdfs --output-dir data/markdown
```

This converts PDFs to markdown files stored in `data/markdown/`.

### 4. Install Ollama (for local LLM)

Download and install Ollama from https://ollama.ai

After installation, pull the Mistral model:

```bash
ollama pull mistral
```

Then start the Ollama server in another terminal:

```bash
ollama serve
```

### 5. Build Vector Index

```bash
python3 main.py index --markdown-dir data/markdown --index-dir data/vectorstore
```

This creates a searchable vector database from your extracted knowledge.

### 6. Query the Knowledge Base

```bash
python3 main.py query --index-dir data/vectorstore
```

This starts an interactive session where you can ask questions about neurosurgery and glioblastoma.

## Project Structure

```
.
├── pdfs/                    # Place your PDF files here
├── data/
│   ├── markdown/           # Extracted markdown files from PDFs
│   └── vectorstore/        # Vector index (Chroma database)
├── src/
│   ├── pdf_extractor.py    # PDF → Markdown extraction
│   ├── knowledge_indexer.py # Markdown → Vector index
│   └── rag_query.py        # Query interface
├── main.py                 # CLI entry point
└── requirements.txt        # Python dependencies
```

## How It Works

1. **PDF Extraction**: Converts research papers to markdown with metadata
2. **Vector Indexing**: Chunks documents and creates embeddings using Ollama
3. **RAG Query**: Retrieves relevant documents and generates answers using Mistral

## System Requirements

- Python 3.8+
- ~2GB disk space for vector index
- CPU with reasonable performance (runs on any modern CPU)
- Ollama installed and running

## Troubleshooting

**"Ollama connection refused"**
- Make sure Ollama server is running: `ollama serve`

**"No PDFs found"**
- Check that PDF files are in the `pdfs/` directory

**"Vector index not found"**
- Run the index command first: `python3 main.py index`

**Memory issues**
- Reduce chunk size in `knowledge_indexer.py` (line ~32)

## Next Steps

- Add more PDFs to `pdfs/` directory
- Re-run extraction and indexing to update knowledge base
- Experiment with different queries and prompts in `rag_query.py`
