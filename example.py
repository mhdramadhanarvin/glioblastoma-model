#!/usr/bin/env python3
"""Example usage of the Medical Knowledge Base system."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pdf_extractor import PDFExtractor
from src.knowledge_indexer import KnowledgeIndexer
from src.rag_query import MedicalRAG


def example_workflow():
    """Demonstrate the complete workflow."""

    print("="*60)
    print("Medical Knowledge Base - Example Workflow")
    print("="*60)
    print()

    # Step 1: Check if PDFs exist
    pdf_dir = Path("pdfs")
    if not pdf_dir.exists() or not list(pdf_dir.glob("*.pdf")):
        print("⚠️  No PDFs found in 'pdfs/' directory")
        print("Please add your PDF files first, then run again.")
        return

    # Step 2: Extract PDFs
    print("Step 1: Extracting PDFs...")
    print("-" * 40)
    extractor = PDFExtractor("pdfs", "data/markdown")
    extractor.process_pdfs()
    print()

    # Step 3: Create index
    print("Step 2: Building vector index...")
    print("-" * 40)
    indexer = KnowledgeIndexer("data/markdown", "data/vectorstore")
    if indexer.create_index():
        print()
        print("Step 3: Ready to query!")
        print("-" * 40)
        print()

        # Step 4: Interactive query
        rag = MedicalRAG("data/vectorstore")
        rag.interactive()
    else:
        print("❌ Failed to create index")


if __name__ == "__main__":
    example_workflow()
