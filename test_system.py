#!/usr/bin/env python3
"""
Test script to verify all components are working correctly.
Run this after setup to ensure everything is configured properly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import pdfplumber
        print("  ✓ pdfplumber")
        import langchain
        print("  ✓ langchain")
        from langchain_community.vectorstores import Chroma
        print("  ✓ langchain_community")
        from langchain_community.embeddings import OllamaEmbeddings
        print("  ✓ OllamaEmbeddings")
        print()
        return True
    except ImportError as e:
        print(f"  ❌ {e}")
        print("Run: pip install -r requirements.txt")
        return False


def test_directories():
    """Test that all required directories exist."""
    print("Testing directories...")
    required_dirs = ["pdfs", "data/markdown", "data/vectorstore", "src"]
    all_exist = True

    for dir_path in required_dirs:
        p = Path(dir_path)
        if p.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ (missing)")
            all_exist = False

    print()
    return all_exist


def test_ollama():
    """Test if Ollama is running."""
    print("Testing Ollama connection...")
    try:
        from langchain_community.embeddings import OllamaEmbeddings
        embeddings = OllamaEmbeddings(model="mistral")
        # Try a quick embedding
        embeddings.embed_query("test")
        print("  ✓ Ollama server is running")
        print()
        return True
    except Exception as e:
        print(f"  ✗ Cannot connect to Ollama")
        print(f"    Error: {str(e)[:80]}")
        print("    Make sure: ollama serve is running in another terminal")
        print("    And model is downloaded: ollama pull mistral")
        print()
        return False


def test_pdfs():
    """Check if there are PDFs to process."""
    print("Checking for PDFs...")
    pdf_dir = Path("pdfs")
    pdfs = list(pdf_dir.glob("*.pdf"))

    if pdfs:
        print(f"  ✓ Found {len(pdfs)} PDF(s)")
    else:
        print(f"  ⚠ No PDFs found in pdfs/ directory")
        print("    Add PDF files to get started")
    print()
    return True


def main():
    print("="*60)
    print("Medical Knowledge Base - System Test")
    print("="*60)
    print()

    results = {
        "Imports": test_imports(),
        "Directories": test_directories(),
        "PDFs": test_pdfs(),
        "Ollama": test_ollama(),
    }

    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")

    print()

    if all(results.values()):
        print("✓ All systems ready! You can now:")
        print("  1. python3 main.py extract")
        print("  2. python3 main.py index")
        print("  3. python3 main.py query")
    else:
        print("⚠ Some tests failed. Check the errors above.")
        if not results["Ollama"]:
            print("\nTo fix Ollama issue:")
            print("  1. Download: https://ollama.ai")
            print("  2. Run: ollama serve")
            print("  3. In another terminal: ollama pull mistral")
        if not results["Imports"]:
            print("\nTo fix imports:")
            print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()
