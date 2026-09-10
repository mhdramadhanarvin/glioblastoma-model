#!/usr/bin/env python3
"""Build vector index from markdown files for RAG with batching."""

import os
import sys
from pathlib import Path
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from chromadb.api.types import EmbeddingFunction
import logging
import time

# Suppress Chroma telemetry warnings
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
os.environ["OTEL_SDK_DISABLED"] = "true"


class OllamaEmbeddingFunction(EmbeddingFunction):
    """Wrapper for OllamaEmbeddings that matches Chroma's interface."""

    def __init__(self, model_name: str = "mistral"):
        self.embeddings = OllamaEmbeddings(model=model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for input texts."""
        return self.embed_documents(input)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed documents with progress tracking."""
        embeddings = []
        start_time = time.time()

        for i, doc in enumerate(documents):
            if i % 50 == 0 and i > 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                remaining = (len(documents) - i) / rate if rate > 0 else 0
                print(f"  [{i}/{len(documents)}] {rate:.1f} chunks/sec | ETA: {remaining:.0f}s",
                      flush=True)

            embeddings.append(self.embeddings.embed_query(doc))

        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query."""
        return self.embeddings.embed_query(query)


class KnowledgeIndexer:
    def __init__(self, markdown_dir: str, index_dir: str, model_name: str = "mistral"):
        self.markdown_dir = Path(markdown_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.embedding_function = OllamaEmbeddingFunction(model_name)

    def load_documents(self) -> List:
        """Load all markdown documents."""
        print(f"Loading markdown files from {self.markdown_dir}...")
        loader = DirectoryLoader(
            str(self.markdown_dir),
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        docs = loader.load()
        print(f"Loaded {len(docs)} documents\n")
        return docs

    def split_documents(self, docs: List) -> List:
        """Split documents into larger chunks to reduce embedding time."""
        print("Splitting documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks")
        print(f"Estimated embedding time: {len(chunks) * 1.5 / 60:.0f}-{len(chunks) * 2 / 60:.0f} minutes\n")
        return chunks

    def create_index(self):
        """Create vector index with batching."""
        docs = self.load_documents()
        if not docs:
            print("No documents found!")
            return False

        chunks = self.split_documents(docs)

        print("Creating vector index...")
        print(f"Embedding {len(chunks)} chunks (showing progress every 50 chunks)...\n")

        try:
            start_time = time.time()

            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_function,
                persist_directory=str(self.index_dir),
                collection_name="medical_knowledge"
            )
            vectorstore.persist()

            elapsed = time.time() - start_time
            print(f"\n✓ Index successfully saved to {self.index_dir}")
            print(f"✓ Total chunks indexed: {len(chunks)}")
            print(f"✓ Time taken: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
            return True

        except Exception as e:
            print(f"\n✗ Error creating index: {e}")
            print("\nTroubleshooting:")
            print("  1. Make sure 'ollama serve' is running in another terminal")
            print("  2. Check Ollama has downloaded the model: ollama pull mistral")
            print("  3. Wait - embedding is slow on CPU (1-2 seconds per chunk)")
            print("  4. Do NOT kill the process - let it run to completion")
            return False


if __name__ == "__main__":
    markdown_dir = sys.argv[1] if len(sys.argv) > 1 else "data/markdown"
    index_dir = sys.argv[2] if len(sys.argv) > 2 else "data/vectorstore"

    indexer = KnowledgeIndexer(markdown_dir, index_dir)
    indexer.create_index()
