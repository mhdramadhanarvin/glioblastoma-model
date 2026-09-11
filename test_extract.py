#!/usr/bin/env python3
"""Self-check for PDF extraction: parallel output must equal serial output.

Run: python3 test_extract.py [pdf_dir]   (defaults to pdfs/, uses 6 files)
"""
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "src")
from pdf_extractor import PDFExtractor

STAMP = re.compile(r"^extracted: .*$", re.MULTILINE)


def run(pdf_dir, out_dir, workers):
    ex = PDFExtractor(str(pdf_dir), str(out_dir))
    ex.process_pdfs(workers=workers)
    return ex.stats, {p.name: STAMP.sub("", p.read_text()) for p in sorted(out_dir.glob("*.md"))}


def demo(pdf_dir="pdfs", n=6):
    pdfs = sorted(Path(pdf_dir).glob("*.pdf"))[:n]
    assert pdfs, f"no PDFs in {pdf_dir}"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "in"
        src.mkdir()
        for p in pdfs:
            (src / p.name).symlink_to(p.resolve())

        s_stats, serial = run(src, tmp / "serial", workers=1)
        p_stats, par = run(src, tmp / "par", workers=4)

    assert s_stats["total"] == len(pdfs), s_stats
    assert s_stats["success"] > 0, "extraction produced nothing — backend broken"
    assert s_stats == p_stats, f"stats diverge:\n{s_stats}\n{p_stats}"
    assert serial.keys() == par.keys(), "different files written"
    for name in serial:
        assert serial[name] == par[name], f"content differs for {name}"
    assert all(t.startswith("---\ntitle:") for t in serial.values()), "frontmatter missing"

    print(f"PASS: {len(serial)} docs, serial == parallel, {s_stats['success']} extracted")


if __name__ == "__main__":
    demo(sys.argv[1] if len(sys.argv) > 1 else "pdfs")
