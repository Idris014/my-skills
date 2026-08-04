#!/usr/bin/env python3
"""Flag internal production language that leaked into visible PPTX text."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


PATTERNS = [
    ("one-sentence-summary", re.compile(r"一句话总结|一页总结|one[- ]sentence summary", re.I)),
    ("routine-summary-label", re.compile(r"^(?:总结|小结|核心结论|key takeaway|takeaway|summary)\s*[:：]?$", re.I)),
    ("visible-timing", re.compile(r"(?:时长|用时)\s*[:：]?\s*\d+\s*(?:min|分钟)|\b\d+\s*[-–]?\s*minute\s+(?:activity|exercise|discussion)\b", re.I)),
    ("interaction-label", re.compile(r"^(?:互动|互动环节|讨论环节|课堂互动|activity|discussion|think[-– ]pair[-– ]share)\s*[:：]?$", re.I)),
    ("production-label", re.compile(r"^(?:讲者提示|演讲者备注|presenter note|speaker note|visual brief|narrative job)\s*[:：]?", re.I)),
]


def slide_sort_key(path: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", path)
    return int(match.group(1)) if match else 0


def extract_slide_texts(pptx: Path):
    namespace = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    with zipfile.ZipFile(pptx) as archive:
        slide_names = sorted(
            (
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ),
            key=slide_sort_key,
        )
        for slide_number, name in enumerate(slide_names, start=1):
            root = ET.fromstring(archive.read(name))
            texts = [node.text or "" for node in root.findall(".//a:t", namespace)]
            yield slide_number, texts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()

    if not args.pptx.exists():
        print(f"ERROR: missing file: {args.pptx}", file=sys.stderr)
        return 2

    findings = []
    for slide_number, texts in extract_slide_texts(args.pptx):
        for text in texts:
            normalized = " ".join(text.split())
            if not normalized:
                continue
            for label, pattern in PATTERNS:
                if pattern.search(normalized):
                    findings.append((slide_number, label, normalized))

    if findings:
        for slide_number, label, text in findings:
            print(f"slide {slide_number}: {label}: {text}")
        print(f"FAIL: {len(findings)} audience-copy hygiene finding(s)")
        return 1

    print("PASS: no audience-copy hygiene findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
