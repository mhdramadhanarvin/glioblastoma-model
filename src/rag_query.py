#!/usr/bin/env python3
"""RAG system for querying medical knowledge base."""

import os
import logging
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from chromadb.api.types import EmbeddingFunction
from typing import List

# Suppress Chroma telemetry warnings
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
os.environ["OTEL_SDK_DISABLED"] = "true"


class OllamaEmbeddingFunction(EmbeddingFunction):
    """Wrapper for OllamaEmbeddings that matches Chroma's interface."""

    def __init__(self, model_name: str = "mistral"):
        self.embeddings = OllamaEmbeddings(model=model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for input texts."""
        return self.embed_documents(input)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return [self.embeddings.embed_query(doc) for doc in documents]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query."""
        return self.embeddings.embed_query(query)


class MedicalRAG:
    def __init__(self, index_dir: str, model_name: str = "mistral"):
        self.index_dir = Path(index_dir)
        self.model_name = model_name
        self.embedding_function = OllamaEmbeddingFunction(model_name)
        self.vectorstore = None
        self.qa_chain = None

    def load_index(self) -> bool:
        """Load the vector index."""
        if not self.index_dir.exists():
            print(f"Index not found at {self.index_dir}")
            print("Run knowledge_indexer.py first")
            return False

        print(f"Loading index from {self.index_dir}...")
        try:
            self.vectorstore = Chroma(
                persist_directory=str(self.index_dir),
                embedding_function=self.embedding_function,
                collection_name="medical_knowledge"
            )
            print(f"✓ Index loaded")
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False

    def setup_qa_chain(self):
        """Setup the QA chain with custom prompt."""
        if not self.vectorstore:
            print("Index not loaded")
            return False

        llm = Ollama(model=self.model_name, temperature=0.3)

        template = """You are a medical expert specializing in neurosurgery and glioblastoma disease.
Use the provided context to answer questions accurately and thoroughly.
If the context doesn't contain relevant information, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": prompt}
        )
        print("✓ QA chain ready")
        return True

    def query(self, question: str) -> str:
        """Query the knowledge base."""
        if not self.qa_chain:
            print("QA chain not initialized")
            return ""

        print(f"\nQuestion: {question}\n")
        result = self.qa_chain.run(question)
        return result

    def interactive(self):
        """Start interactive query mode."""
        if not self.load_index():
            return

        if not self.setup_qa_chain():
            return

        print("\n" + "="*60)
        print("Medical Knowledge Base - Interactive Mode")
        print("="*60)
        print("Type 'quit' or 'exit' to stop\n")

        while True:
            question = input("Your question: ").strip()

            if question.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not question:
                continue

            answer = self.query(question)
            print(f"Answer: {answer}\n")


if __name__ == "__main__":
    import sys

    index_dir = sys.argv[1] if len(sys.argv) > 1 else "data/vectorstore"

    rag = MedicalRAG(index_dir)
    rag.interactive()
