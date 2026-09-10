#!/usr/bin/env python3
"""Extract text from PDFs and convert to markdown."""

import os
import re
from pathlib import Path
from typing import Optional
import pdfplumber
from datetime import datetime
import json


class PDFExtractor:
    def __init__(self, pdf_dir: str, output_dir: str):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {"total": 0, "success": 0, "failed": 0, "rejected": 0, "errors": []}
        self.rejected = []

    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """Extract text from PDF."""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text(x_tolerance=1) or ""
            return text if text.strip() else None
        except Exception as e:
            self.stats["errors"].append(f"{pdf_path.name}: {str(e)}")
            return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"(?<=[a-z])\n(?=[a-z])", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract_abstract(self, text: str) -> str:
        """Extract abstract from text."""
        abstract_match = re.search(
            r"(?:abstract|summary|background)(.*?)(?:introduction|methods|keywords|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if abstract_match:
            return abstract_match.group(1).strip()[:500]
        return ""

    def extract_title(self, text: str, pdf_path: Path) -> str:
        """Extract title with improved heuristic."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # Skip journal furniture
        skip_patterns = [
            r"^RESEARCH\s+ARTICLE\s*$",
            r"^PLOS",
            r"^Perspectives",
            r"^METHODS AND RESOURCES",
            r"^[A-Z\s]{1,30}$"
        ]

        candidates = []
        for line in lines[:15]:
            if any(re.match(p, line, re.IGNORECASE) for p in skip_patterns):
                continue
            if any(c.islower() for c in line):
                candidates.append(line)

        if candidates:
            return max(candidates, key=len)[:150]
        return pdf_path.stem

    def count_mashed_runs(self, text: str) -> int:
        """Count runs of 25+ letters with no spaces."""
        return len(re.findall(r"[a-zA-Z]{25,}", text))

    def quality_gate(self, text: str, pdf_path: Path) -> tuple[bool, Optional[str]]:
        """Check document quality. Returns (is_valid, reject_reason)."""
        mashed_runs = self.count_mashed_runs(text)
        if mashed_runs > 5:
            return False, f"Too many mashed runs: {mashed_runs}"

        word_count = len(text.split())
        if word_count < 500:
            return False, f"Too short: {word_count} words"

        if not text.strip():
            return False, "No extractable text"

        return True, None

    def create_markdown(self, pdf_path: Path, text: str) -> str:
        """Create markdown with frontmatter."""
        title = self.extract_title(text, pdf_path)
        abstract = self.extract_abstract(text)

        markdown = f"""---
title: {title[:150]}
source: {pdf_path.name}
extracted: {datetime.now().isoformat()}
word_count: {len(text.split())}
tags: [neurosurgery, glioblastoma, research]
---

## Abstract
{abstract if abstract else "No abstract found"}

## Content

{text}
"""
        return markdown

    def process_pdfs(self):
        """Process all PDFs in directory."""
        pdfs = sorted(self.pdf_dir.glob("*.pdf"))
        print(f"Found {len(pdfs)} PDFs\n")

        for i, pdf_path in enumerate(pdfs, 1):
            print(f"[{i}/{len(pdfs)}] {pdf_path.name}...", end=" ", flush=True)
            self.stats["total"] += 1

            text = self.extract_text(pdf_path)
            if not text:
                print("❌ extraction failed")
                self.stats["failed"] += 1
                continue

            text = self.clean_text(text)

            is_valid, reject_reason = self.quality_gate(text, pdf_path)
            if not is_valid:
                print(f"⊘ rejected: {reject_reason}")
                self.stats["rejected"] += 1
                self.rejected.append({"file": pdf_path.name, "reason": reject_reason})
                continue

            markdown = self.create_markdown(pdf_path, text)

            output_path = self.output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(markdown, encoding="utf-8")

            print(f"✓ ({len(text.split())} words)")
            self.stats["success"] += 1

        self._print_report()

    def _print_report(self):
        """Print extraction report."""
        print("\n" + "="*60)
        print("EXTRACTION REPORT")
        print("="*60)
        print(f"Total PDFs: {self.stats['total']}")
        print(f"Success: {self.stats['success']}")
        print(f"Rejected: {self.stats['rejected']}")
        print(f"Failed: {self.stats['failed']}")
        if self.stats["errors"]:
            print(f"\nErrors:")
            for error in self.stats["errors"][:3]:
                print(f"  - {error}")

        if self.rejected:
            rejected_path = self.output_dir.parent / "rejected.json"
            with open(rejected_path, "w") as f:
                json.dump(self.rejected, f, indent=2)
            print(f"\nRejected docs saved to {rejected_path}")


if __name__ == "__main__":
    import sys

    pdf_dir = sys.argv[1] if len(sys.argv) > 1 else "pdfs"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "data/markdown"

    extractor = PDFExtractor(pdf_dir, output_dir)
    extractor.process_pdfs()
