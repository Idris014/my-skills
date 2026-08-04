#!/usr/bin/env python3
"""Structural smoke checks for slide and companion-demo deliverables."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


PML = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


class HtmlAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.local_refs: list[str] = []
        self.remote_runtime_refs: list[str] = []
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "meta" and values.get("name", "").lower() == "viewport":
            self.has_viewport = True

        attr = "href" if tag in {"a", "link"} else "src" if tag in {"script", "img", "source"} else None
        if not attr or not values.get(attr):
            return
        ref = values[attr]
        if ref.startswith(("http://", "https://")):
            if tag != "a":
                self.remote_runtime_refs.append(ref)
        elif not ref.startswith(("#", "data:", "mailto:", "javascript:")):
            self.local_refs.append(ref.split("#", 1)[0].split("?", 1)[0])


def audit_pptx(path: Path) -> dict:
    result: dict = {"path": str(path), "exists": path.exists(), "errors": [], "warnings": []}
    if not path.exists():
        result["errors"].append("PPTX does not exist")
        return result
    if path.suffix.lower() != ".pptx":
        result["errors"].append("Expected a .pptx file")
        return result

    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                result["errors"].append(f"Corrupt ZIP member: {bad}")
            slide_names = sorted(
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            )
            result["slide_count"] = len(slide_names)
            if not slide_names:
                result["errors"].append("No slide XML found")

            empty_slides = []
            for name in slide_names:
                root = ET.fromstring(archive.read(name))
                text = "".join(node.text or "" for node in root.findall(".//a:t", PML)).strip()
                rel_name = name.replace("slides/slide", "slides/_rels/slide") + ".rels"
                has_relationships = rel_name in archive.namelist()
                if not text and not has_relationships:
                    empty_slides.append(name)
            if empty_slides:
                result["warnings"].append(f"Possibly empty slides: {empty_slides}")

            notes = [
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
            ]
            source_note_count = 0
            for name in notes:
                xml = archive.read(name).decode("utf-8", errors="ignore")
                if "[Sources]" in xml:
                    source_note_count += 1
            result["notes_slide_count"] = len(notes)
            result["source_note_count"] = source_note_count
    except (zipfile.BadZipFile, ET.ParseError) as exc:
        result["errors"].append(str(exc))
    return result


def audit_keynote(path: Path) -> dict:
    result = {"path": str(path), "exists": path.exists(), "errors": [], "warnings": []}
    if not path.exists():
        result["errors"].append("Keynote output does not exist")
    elif path.suffix.lower() != ".key":
        result["errors"].append("Expected a .key path")
    elif path.is_file() and path.stat().st_size == 0:
        result["errors"].append("Keynote output is empty")
    return result


def audit_html(path: Path) -> dict:
    result: dict = {"path": str(path), "exists": path.exists(), "errors": [], "warnings": []}
    if not path.exists():
        result["errors"].append("HTML file does not exist")
        return result

    text = path.read_text(encoding="utf-8")
    audit = HtmlAudit()
    audit.feed(text)
    duplicates = sorted({item for item in audit.ids if audit.ids.count(item) > 1})
    missing = sorted({ref for ref in audit.local_refs if not (path.parent / ref).exists()})

    result.update(
        {
            "id_count": len(audit.ids),
            "duplicate_ids": duplicates,
            "missing_local_refs": missing,
            "remote_runtime_refs": audit.remote_runtime_refs,
            "has_viewport_meta": audit.has_viewport,
        }
    )
    if duplicates:
        result["errors"].append("Duplicate HTML ids")
    if missing:
        result["errors"].append("Missing local HTML resources")
    if audit.remote_runtime_refs:
        result["warnings"].append("Remote runtime dependencies prevent fully offline use")
    if not audit.has_viewport:
        result["warnings"].append("Missing viewport meta tag")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pptx", type=Path)
    parser.add_argument("--key", type=Path)
    parser.add_argument("--html", type=Path, action="append", default=[])
    parser.add_argument("--expect-slides", type=int)
    args = parser.parse_args()

    reports = []
    if args.pptx:
        report = audit_pptx(args.pptx)
        if args.expect_slides is not None and report.get("slide_count") != args.expect_slides:
            report["errors"].append(
                f"Expected {args.expect_slides} slides, found {report.get('slide_count', 0)}"
            )
        reports.append({"kind": "pptx", **report})
    if args.key:
        reports.append({"kind": "keynote", **audit_keynote(args.key)})
    reports.extend({"kind": "html", **audit_html(path)} for path in args.html)

    if not reports:
        parser.error("Provide at least one --pptx, --key, or --html input")

    print(json.dumps({"reports": reports}, ensure_ascii=False, indent=2))
    return 1 if any(report["errors"] for report in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
