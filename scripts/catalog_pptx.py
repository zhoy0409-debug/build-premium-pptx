#!/usr/bin/env python3
"""Catalog reusable design signals in PPTX/PPTM/POTX files using stdlib only."""

from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
SLIDE_RE = re.compile(r"ppt/slides/slide\d+\.xml$")
OOXML_SUFFIXES = {".pptx", ".pptm", ".potx", ".potm"}


def _count(names: list[str], prefix: str, suffix: str = "") -> int:
    return sum(name.startswith(prefix) and name.endswith(suffix) for name in names)


def _aspect(cx: int, cy: int) -> str:
    if not cx or not cy:
        return "unknown"
    ratio = cx / cy
    if abs(ratio - 16 / 9) < 0.03:
        return "16:9"
    if abs(ratio - 4 / 3) < 0.03:
        return "4:3"
    return f"{ratio:.2f}:1"


def inspect_deck(path: Path) -> dict:
    result = {"path": str(path.resolve()), "name": path.name}
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            slides = sorted(name for name in names if SLIDE_RE.fullmatch(name))
            root = ET.fromstring(archive.read("ppt/presentation.xml"))
            size = root.find(f"{{{P_NS}}}sldSz")
            cx = int(size.get("cx", 0)) if size is not None else 0
            cy = int(size.get("cy", 0)) if size is not None else 0

            fonts: set[str] = set()
            colors: set[str] = set()
            for theme in (name for name in names if name.startswith("ppt/theme/theme") and name.endswith(".xml")):
                for element in ET.fromstring(archive.read(theme)).iter():
                    if element.tag.endswith(("latin", "ea", "cs")) and element.get("typeface"):
                        fonts.add(element.get("typeface", ""))
                    if element.tag.endswith(("srgbClr", "sysClr")):
                        color = element.get("val") or element.get("lastClr")
                        if color:
                            colors.add(color.upper())

            slide_xml = [archive.read(name) for name in slides]
            media = [info for info in archive.infolist() if info.filename.startswith("ppt/media/") and not info.is_dir()]
            result.update(
                slides=len(slides),
                aspect=_aspect(cx, cy),
                width_in=round(cx / 914400, 2) if cx else None,
                height_in=round(cy / 914400, 2) if cy else None,
                layouts=_count(names, "ppt/slideLayouts/slideLayout", ".xml"),
                masters=_count(names, "ppt/slideMasters/slideMaster", ".xml"),
                media=len(media),
                media_mb=round(sum(info.file_size for info in media) / 1048576, 1),
                charts=_count(names, "ppt/charts/chart", ".xml"),
                diagrams=_count(names, "ppt/diagrams/data", ".xml"),
                transition_slides=sum(b"<p:transition" in xml for xml in slide_xml),
                animated_slides=sum(b"<p:timing" in xml for xml in slide_xml),
                fonts=sorted(fonts),
                colors=sorted(colors),
            )
    except (KeyError, OSError, ET.ParseError, zipfile.BadZipFile) as error:
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def find_decks(root: Path, queries: list[str]) -> list[Path]:
    candidates = [root] if root.is_file() else root.rglob("*")
    terms = [term.casefold() for term in queries]
    return sorted(
        (
            path
            for path in candidates
            if path.is_file()
            and path.suffix.casefold() in OOXML_SUFFIXES
            and not path.name.startswith(("~$", "._"))
            and (not terms or any(term in str(path).casefold() for term in terms))
        ),
        key=lambda path: str(path).casefold(),
    )


def write_catalog(items: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.casefold() == ".csv":
        fields = list(dict.fromkeys(key for item in items for key in item))
        with output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for item in items:
                writer.writerow({key: "; ".join(value) if isinstance(value, list) else value for key, value in item.items()})
    else:
        output.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def print_summary(items: list[dict]) -> None:
    print(f"decks={len(items)} errors={sum('error' in item for item in items)}")
    print("slides aspect media charts anim name")
    for item in items:
        if "error" in item:
            print(f"ERROR  {item['name']}: {item['error']}")
        else:
            print(
                f"{item['slides']:>6} {item['aspect']:>6} {item['media']:>5} "
                f"{item['charts']:>6} {item['animated_slides']:>4} {item['name']}"
            )


def self_test() -> None:
    presentation = f'<p:presentation xmlns:p="{P_NS}"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>'
    theme = '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:latin typeface="Aptos"/><a:srgbClr val="00AA66"/></a:theme>'
    slide = f'<p:sld xmlns:p="{P_NS}"><p:transition/><p:timing/></p:sld>'
    with tempfile.TemporaryDirectory() as directory:
        deck = Path(directory) / "demo.pptx"
        with zipfile.ZipFile(deck, "w") as archive:
            archive.writestr("ppt/presentation.xml", presentation)
            archive.writestr("ppt/theme/theme1.xml", theme)
            archive.writestr("ppt/slides/slide1.xml", slide)
            archive.writestr("ppt/media/image1.png", b"x")
        item = inspect_deck(deck)
        assert item["slides"] == 1 and item["aspect"] == "16:9"
        assert item["media"] == 1 and item["transition_slides"] == 1 and item["animated_slides"] == 1
        assert item["fonts"] == ["Aptos"] and item["colors"] == ["00AA66"]
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, help="PPTX file or directory to scan")
    parser.add_argument("--query", action="append", default=[], help="OR path/name filter; repeat as needed")
    parser.add_argument("--limit", type=int, help="inspect only the first N matching decks")
    parser.add_argument("--output", type=Path, help="write .json or .csv catalog")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.root is None or not args.root.exists():
        parser.error("root must be an existing PPTX file or directory")

    paths = find_decks(args.root, args.query)
    if args.limit is not None:
        paths = paths[: max(args.limit, 0)]
    items = [inspect_deck(path) for path in paths]
    if args.output:
        write_catalog(items, args.output)
        print(f"wrote {len(items)} records to {args.output}")
    else:
        print_summary(items)
    return 0 if items else 1


if __name__ == "__main__":
    raise SystemExit(main())

