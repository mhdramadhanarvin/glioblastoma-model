# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Local-only RAG pipeline over neurosurgery/glioblastoma research PDFs. No cloud calls — Ollama serves both the embeddings and the LLM. Three stages, run in order: PDFs → markdown → Chroma vector index → interactive Q&A.

Not a git repository.

## Commands

```bash
source .venv/bin/activate            # Python 3.13, deps already installed

python3 main.py extract              # pdfs/ -> data/markdown/
python3 main.py index                # data/markdown/ -> data/vectorstore/
python3 main.py query                # interactive REPL against the index

python3 test_system.py               # preflight: imports, dirs, Ollama reachable, PDF count
python3 example.py                   # runs all three stages end to end
```

Every stage requires a live Ollama server (`ollama serve`) with `mistral` pulled. `test_system.py` is the only test harness — there is no pytest suite, so verify changes by running the relevant stage.

Each `src/` module is also directly runnable with positional dir args, which is the fastest way to test one stage in isolation:

```bash
python3 src/pdf_extractor.py pdfs data/markdown
python3 src/knowledge_indexer.py data/markdown data/vectorstore
python3 src/rag_query.py data/vectorstore
```

## Architecture

`main.py` is a thin argparse dispatcher; each subcommand lazily imports one class and calls one method. All real logic lives in three independent `src/` modules that communicate only through the filesystem — no shared runtime state, so any stage can be re-run alone.

- **`src/pdf_extractor.py`** (`PDFExtractor.process_pdfs`) — pdfplumber text extraction, regex cleanup (de-hyphenation of wrapped lines, whitespace collapse), heuristic title (first line >10 chars) and abstract (regex between `abstract|summary|background` and `introduction|methods|keywords`). Writes one `.md` per PDF with YAML frontmatter. Failures are collected in `self.stats` and never raise — a corrupt PDF is skipped, not fatal.
- **`src/knowledge_indexer.py`** (`KnowledgeIndexer.create_index`) — DirectoryLoader over `*.md`, `RecursiveCharacterTextSplitter`, then `Chroma.from_documents` into collection `medical_knowledge`.
- **`src/rag_query.py`** (`MedicalRAG`) — reopens that same persisted collection and wraps it in a LangChain `RetrievalQA` (`chain_type="stuff"`, k=5) over an `Ollama` LLM at temperature 0.3, with the medical-expert prompt inlined in `setup_qa_chain`.

`OllamaEmbeddingFunction` is **duplicated** in the indexer and the query module. Both adapt `OllamaEmbeddings` to Chroma's `EmbeddingFunction` interface (Chroma calls `__call__(input)`, LangChain calls `embed_documents`/`embed_query`). The indexer's copy adds progress printing. **The two must stay embedding-compatible** — change the model or embedding logic in one and the persisted index no longer matches queries against it. Change both, and rebuild the index.

Embeddings come from `mistral` (a 7B generation model), not a dedicated embedding model, so indexing is the slow step — minutes to tens of minutes for thousands of chunks on CPU.

## Traps

- **`config.py` is dead code.** Nothing imports it. Real values are hardcoded: `chunk_size=2000` / `chunk_overlap=300` in `knowledge_indexer.py` (not the 1000/200 that `config.py` and `ARCHITECTURE.md` claim), `model_name="mistral"` and `temperature=0.3` as constructor defaults in the indexer and query modules, `k=5` in `setup_qa_chain`. Editing `config.py` changes nothing. There is also no `--model` flag despite the docs mentioning one. Either wire `config.py` up or edit the modules directly — don't assume it's live.
- **State is out of sync with the docs.** 352 PDFs in `pdfs/`, only 147 markdown files extracted, and `medical_knowledge` holds 0 embeddings — the index has never been built. A stale `langchain` collection also sits in `chroma.sqlite3` from an earlier run.
- **`data/` and `pdfs/` are gitignored**, so all pipeline output is local-only and reproducible from the PDFs.
- **`data/markdown/` is an Obsidian vault** (`.obsidian/` at the project root). Frontmatter and heading structure in generated markdown are load-bearing for graph view — preserve them when changing `create_markdown`.
- **The `.md` docs and status scripts are aspirational and partly stale.** `ARCHITECTURE.md`, `DEPLOYMENT.md`, `PROJECT_SUMMARY.txt`, `QUICKSTART.md`, `INSTALL.md`, `CHECKLIST.py`, `project_info.py`, and `examples.py` describe intent, cite wrong line numbers and wrong chunk sizes, and print hardcoded "deployment ready" status. Trust `src/` over any of them.
- `config/`, `models/`, and `notebooks/` are empty placeholders.
