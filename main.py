#!/usr/bin/env python3
"""Main entry point for the AI model training pipeline."""

import sys
import argparse
from pathlib import Path


def run_extract(args):
    """Run PDF extraction."""
    from src.pdf_extractor import PDFExtractor
    extractor = PDFExtractor(args.pdf_dir, args.output_dir)
    extractor.process_pdfs()


def run_index(args):
    """Run knowledge indexing."""
    from src.knowledge_indexer import KnowledgeIndexer
    indexer = KnowledgeIndexer(args.markdown_dir, args.index_dir)
    indexer.create_index()


def run_query(args):
    """Run interactive RAG query."""
    from src.rag_query import MedicalRAG
    rag = MedicalRAG(args.index_dir)
    rag.interactive()


def main():
    parser = argparse.ArgumentParser(
        description="AI Medical Knowledge Base for Neurosurgery/Glioblastoma"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract PDFs to markdown")
    extract_parser.add_argument("--pdf-dir", default="pdfs", help="Directory containing PDFs")
    extract_parser.add_argument("--output-dir", default="data/markdown", help="Output directory for markdown files")
    extract_parser.set_defaults(func=run_extract)

    # Index command
    index_parser = subparsers.add_parser("index", help="Build vector index from markdown")
    index_parser.add_argument("--markdown-dir", default="data/markdown", help="Directory containing markdown files")
    index_parser.add_argument("--index-dir", default="data/vectorstore", help="Output directory for vector index")
    index_parser.set_defaults(func=run_index)

    # Query command
    query_parser = subparsers.add_parser("query", help="Interactive query mode")
    query_parser.add_argument("--index-dir", default="data/vectorstore", help="Directory containing vector index")
    query_parser.set_defaults(func=run_query)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
