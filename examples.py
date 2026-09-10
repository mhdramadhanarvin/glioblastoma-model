#!/usr/bin/env python3
"""
Advanced usage examples for the Medical Knowledge Base system.
"""

from src.rag_query import MedicalRAG
from src.knowledge_indexer import KnowledgeIndexer
from src.pdf_extractor import PDFExtractor
from pathlib import Path


def example_batch_processing():
    """Example: Process multiple PDF directories."""
    print("Example 1: Batch Processing Multiple Sources")
    print("-" * 50)
    print("""
    # Organize PDFs into categories:
    pdfs/
    ├── neurosurgery_basics/
    ├── glioblastoma_research/
    ├── treatment_protocols/
    └── clinical_trials/

    # Process each separately:
    for dir in pdfs/*/; do
        python3 main.py extract --pdf-dir "$dir"
        python3 main.py index
    done
    """)
    print()


def example_custom_queries():
    """Example: Advanced query patterns."""
    print("Example 2: Advanced Query Patterns")
    print("-" * 50)
    print("""
    # Research comparison
    Q: "Compare temozolomide vs bevacizumab in glioblastoma treatment"

    # Protocol extraction
    Q: "What is the standard surgical protocol for glioblastoma resection?"

    # Evidence synthesis
    Q: "What is the evidence for combining radiation and chemotherapy?"

    # Prognosis questions
    Q: "What factors influence glioblastoma prognosis and survival?"

    # Technique learning
    Q: "Explain awake craniotomy benefits and risks in glioblastoma"

    # Complication review
    Q: "What are common complications after glioblastoma surgery?"
    """)
    print()


def example_index_updates():
    """Example: Keeping index updated."""
    print("Example 3: Updating Knowledge Base")
    print("-" * 50)
    print("""
    # Add new papers to pdfs/ folder
    cp ~/Downloads/new_papers/*.pdf pdfs/

    # Re-extract (only processes new files)
    python3 main.py extract

    # Re-index entire collection
    python3 main.py index

    # Query updated knowledge base
    python3 main.py query
    """)
    print()


def example_export_markdown():
    """Example: Export for Obsidian."""
    print("Example 4: Obsidian Vault Integration")
    print("-" * 50)
    print("""
    # Method 1: Copy markdown files
    cp -r data/markdown/* ~/Obsidian/Medical-KB/

    # Method 2: Create symlink (auto-updates)
    ln -s $(pwd)/data/markdown ~/Obsidian/Medical-KB-Link

    # Then in Obsidian:
    1. Open vault settings
    2. Add folder "data/markdown" as a linked vault
    3. Explore using knowledge graph
    4. Add your own notes and cross-references
    """)
    print()


def example_embedding_search():
    """Example: Direct embedding search."""
    print("Example 5: Semantic Search Without LLM")
    print("-" * 50)
    print("""
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OllamaEmbeddings

    # Load index
    embeddings = OllamaEmbeddings(model="mistral")
    vectorstore = Chroma(
        persist_directory="data/vectorstore",
        embedding_function=embeddings
    )

    # Search for similar content
    results = vectorstore.similarity_search("glioblastoma surgery", k=3)
    for result in results:
        print(f"Score: {result.metadata}")
        print(f"Content: {result.page_content[:200]}...")
    """)
    print()


def example_batch_query():
    """Example: Batch query processing."""
    print("Example 6: Batch Query Processing")
    print("-" * 50)
    print("""
    from src.rag_query import MedicalRAG

    queries = [
        "What is IDH mutation status in glioblastoma?",
        "Explain tumor microenvironment in glioblastoma",
        "What is the role of MGMT methylation?",
    ]

    rag = MedicalRAG("data/vectorstore")
    rag.load_index()
    rag.setup_qa_chain()

    results = []
    for q in queries:
        answer = rag.query(q)
        results.append({"question": q, "answer": answer})

    # Save results
    import json
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    """)
    print()


def example_fine_tuning_prep():
    """Example: Prepare data for fine-tuning."""
    print("Example 7: Prepare for Model Fine-tuning")
    print("-" * 50)
    print("""
    # If you later want to fine-tune a model:

    1. Export QA pairs from your knowledge base
    2. Format as training data:
       {
         "instruction": "What causes glioblastoma?",
         "input": "",
         "output": "Glioblastoma is caused by..."
       }

    3. Use tools like unsloth or axolotl to fine-tune
    4. Deploy fine-tuned model with Ollama

    # For now, RAG is sufficient and more maintainable
    """)
    print()


def print_all_examples():
    """Print all examples."""
    print("\n")
    print("=" * 60)
    print("ADVANCED USAGE EXAMPLES")
    print("=" * 60)
    print()

    example_batch_processing()
    example_custom_queries()
    example_index_updates()
    example_export_markdown()
    example_embedding_search()
    example_batch_query()
    example_fine_tuning_prep()

    print("=" * 60)
    print("For more information, see:")
    print("  - README.md: Overview and quick start")
    print("  - QUICKSTART.md: Step-by-step setup")
    print("  - ARCHITECTURE.md: Technical details")
    print("=" * 60)


if __name__ == "__main__":
    print_all_examples()
