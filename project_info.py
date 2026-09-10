#!/usr/bin/env python3
"""
Project Information & Statistics Script
Shows comprehensive information about the medical knowledge base system.
"""

import os
from pathlib import Path
import subprocess


def count_lines(file_path):
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0


def get_file_size(file_path):
    """Get file size in KB."""
    try:
        return os.path.getsize(file_path) / 1024
    except:
        return 0


def show_project_stats():
    """Show project statistics."""
    print("\n" + "="*70)
    print("PROJECT STATISTICS")
    print("="*70)

    # Count files
    py_files = list(Path(".").glob("**/*.py"))
    md_files = list(Path(".").glob("**/*.md"))

    total_lines = sum(count_lines(f) for f in py_files)
    total_size = sum(get_file_size(f) for f in py_files)

    print(f"\nCode Files:")
    print(f"  Python files: {len(py_files)}")
    print(f"  Total lines: {total_lines}")
    print(f"  Total size: {total_size:.1f} KB")

    print(f"\nDocumentation:")
    print(f"  Markdown files: {len(md_files)}")

    print(f"\nBreakdown:")
    for f in sorted(py_files):
        lines = count_lines(f)
        size = get_file_size(f)
        print(f"  {str(f):40s} {lines:5d} lines  {size:6.1f} KB")


def show_structure():
    """Show project structure."""
    print("\n" + "="*70)
    print("PROJECT STRUCTURE")
    print("="*70)

    structure = """
    ai-model-neosurgery/
    ├── src/
    │   ├── pdf_extractor.py       - Extract PDFs to markdown
    │   ├── knowledge_indexer.py   - Build vector index
    │   ├── rag_query.py           - Query interface
    │   └── __init__.py            - Package init
    ├── main.py                    - CLI entry point
    ├── config.py                  - Configuration
    ├── setup.sh                   - Setup script
    ├── test_system.py             - System verification
    ├── example.py                 - Full workflow example
    ├── examples.py                - Advanced examples
    ├── requirements.txt           - Dependencies
    ├── .gitignore                 - Git config
    │
    ├── Documentation/
    │   ├── README.md              - Overview
    │   ├── QUICKSTART.md          - 5-step setup
    │   ├── INSTALL.md             - Installation guide
    │   ├── ARCHITECTURE.md        - Technical details
    │   ├── PROJECT_SUMMARY.txt    - This summary
    │   └── project_info.py        - This script
    │
    ├── Data Directories/ (created at runtime)
    │   ├── pdfs/                  - Your PDF files
    │   ├── data/markdown/         - Extracted markdown
    │   ├── data/vectorstore/      - Vector index
    │   └── .obsidian/             - Obsidian config
    """
    print(structure)


def show_quick_commands():
    """Show quick command reference."""
    print("\n" + "="*70)
    print("QUICK COMMAND REFERENCE")
    print("="*70)

    commands = """
    Setup (first time only):
      bash setup.sh
      source .venv/bin/activate
      ollama pull mistral

    Main Commands:
      python3 main.py extract      - Extract PDFs to markdown
      python3 main.py index        - Build vector index
      python3 main.py query        - Interactive query mode

    Utilities:
      python3 test_system.py       - Verify system setup
      python3 example.py           - Run full workflow
      python3 examples.py          - Show advanced examples
      python3 project_info.py      - Show this information

    Background Process:
      ollama serve                 - Start Ollama (keep running)
    """
    print(commands)


def show_dependencies():
    """Show dependencies info."""
    print("\n" + "="*70)
    print("DEPENDENCIES")
    print("="*70)

    try:
        with open("requirements.txt", "r") as f:
            deps = f.read().strip().split("\n")
            print("\nPython packages:")
            for dep in deps:
                print(f"  - {dep}")
    except:
        print("Could not read requirements.txt")

    print("\nExternal tools:")
    print("  - Ollama (local LLM runtime)")
    print("  - Python 3.8+")


def show_next_steps():
    """Show next steps."""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)

    steps = """
    1. START HERE:
       Read QUICKSTART.md for 5-step setup guide

    2. INSTALL OLLAMA:
       Download from https://ollama.ai
       Follow platform-specific instructions

    3. GATHER YOUR RESEARCH:
       Collect all neurosurgery and glioblastoma PDFs

    4. VERIFY SETUP:
       python3 test_system.py

    5. RUN SETUP:
       bash setup.sh
       source .venv/bin/activate

    6. PREPARE DATA:
       cp ~/Downloads/*.pdf pdfs/
       python3 main.py extract
       python3 main.py index

    7. START QUERYING:
       ollama serve              (Terminal 1)
       python3 main.py query     (Terminal 2)
    """
    print(steps)


def show_features():
    """Show key features."""
    print("\n" + "="*70)
    print("KEY FEATURES")
    print("="*70)

    features = """
    ✓ LOCAL & OFFLINE
      - No cloud required
      - Works offline after setup
      - All data stays on your machine

    ✓ CPU-ONLY
      - No GPU needed
      - Works on any modern computer
      - Even works on older laptops

    ✓ SPECIALIZED
      - Trained on neurosurgery research
      - Focused on glioblastoma disease
      - Domain-specific knowledge base

    ✓ RETRIEVAL-AUGMENTED
      - Answers backed by your research papers
      - No hallucinations or made-up facts
      - Cites sources

    ✓ EXPANDABLE
      - Add more PDFs anytime
      - Knowledge base grows with you
      - Easy to customize and modify

    ✓ OBSIDIAN READY
      - Markdown files for knowledge graphs
      - Import directly into Obsidian vault
      - Perfect for research organization
    """
    print(features)


def main():
    """Show all information."""
    print("\n")
    print("*"*70)
    print("*" + " "*68 + "*")
    print("*" + "  AI MEDICAL KNOWLEDGE BASE - PROJECT INFORMATION".center(68) + "*")
    print("*" + "  Neurosurgery & Glioblastoma Research Assistant".center(68) + "*")
    print("*" + " "*68 + "*")
    print("*"*70)

    show_features()
    show_structure()
    show_project_stats()
    show_dependencies()
    show_quick_commands()
    show_next_steps()

    print("\n" + "="*70)
    print("For more information:")
    print("  - README.md: Project overview")
    print("  - QUICKSTART.md: Step-by-step setup")
    print("  - INSTALL.md: Detailed installation")
    print("  - ARCHITECTURE.md: Technical details")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
