# Project Dependencies & Architecture

## Core Technologies

### PDF Processing
- **pdfplumber**: Extract text from research papers with high accuracy
- Handles tables, multi-column layouts, and academic paper formats

### Vector Search & RAG
- **LangChain**: Framework for building RAG applications
- **Chroma**: Lightweight vector database (stores embeddings locally)
- **OllamaEmbeddings**: Generate embeddings using Ollama

### Local LLM
- **Ollama**: Run large language models locally on CPU
- **Mistral 7B**: Base model (efficient, good reasoning)

## Architecture

```
Your PDFs
    ↓
[PDF Extractor] → Markdown Files (data/markdown/)
    ↓
[Knowledge Indexer] → Vector Index (data/vectorstore/)
    ↓
[RAG Query Engine] → Interactive Interface
    ↓
User Questions
```

## Data Flow

1. **Extraction**: PDFs → Text cleaning → Markdown with metadata
2. **Indexing**: Markdown → Chunking → Embeddings → Vector database
3. **Retrieval**: Query → Semantic search → Top-5 relevant chunks
4. **Generation**: LLM answers based on retrieved context

## Key Components

### src/pdf_extractor.py
- Reads PDFs using pdfplumber
- Cleans formatting and normalizes text
- Extracts metadata (title, abstract, word count)
- Outputs markdown files ready for Obsidian

### src/knowledge_indexer.py
- Loads markdown files
- Splits documents into 1000-token chunks (with 200-token overlap)
- Generates embeddings using Ollama
- Stores in Chroma vector database

### src/rag_query.py
- Loads persisted vector index
- Sets up retrieval chain with custom prompt
- Provides interactive query interface
- Returns answers with source attribution

## Performance Characteristics

| Operation | Time | Hardware |
|-----------|------|----------|
| Extract 100 PDFs | 1-2 min | CPU |
| Index 100 PDFs | 30-60 sec | CPU |
| First query | 5-10 sec | CPU (model load) |
| Subsequent query | 2-5 sec | CPU |

## Customization Points

### config.py
- `MODEL_NAME`: Switch models (llama2, neural-chat, etc.)
- `MODEL_TEMPERATURE`: Adjust answer creativity (0.0-1.0)
- `PDF_CHUNK_SIZE`: Balance between context and precision
- `RETRIEVAL_K`: Number of source documents to use

### src/rag_query.py (line 26-31)
- Modify the `template` string to change system behavior
- Add domain-specific instructions and tone

### src/knowledge_indexer.py (line 26-31)
- Adjust `chunk_size` and `chunk_overlap` for different documents

## Storage Breakdown

For 100 research papers:

| Component | Size |
|-----------|------|
| Markdown files | ~50-100 MB |
| Vector index | ~30-50 MB |
| Ollama model cache | ~4 GB (first time) |
| Total with model | ~4.1-4.2 GB |

Vector index size depends on document count and chunk size.

## Scaling

The system is optimized for:
- **100-1000 PDFs**: Direct usage, no changes needed
- **1000-5000 PDFs**: May need to split indexing into batches
- **5000+ PDFs**: Consider chunking into multiple indices per topic

## Alternative Models

You can swap `mistral` for other models available in Ollama:

```bash
ollama pull llama2              # 7B, good general purpose
ollama pull neural-chat         # 7B, optimized for chat
ollama pull orca-mini           # 3B, smaller/faster
ollama pull medllama2           # 7B, medical domain tuned
```

Then update `config.py` or use `--model` flag.
