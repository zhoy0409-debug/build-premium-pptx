#!/usr/bin/env python3
"""Index a local PPTX library at slide level so layouts can be selected by message type.

Deck-level metadata (see catalog_pptx.py) answers "what decks exist". This answers
"which slide in which deck is the right layout for this point", which is what a
beginner actually needs. Stdlib only.

Outputs one record per usable slide: role, density, title, chart kinds, and the
counts needed to judge whether real content will fit.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")
OOXML_SUFFIXES = {".pptx", ".pptm", ".potx", ".potm"}

CHART_KINDS = (
    "barChart", "bar3DChart", "lineChart", "pieChart", "doughnutChart",
    "scatterChart", "areaChart", "radarChart", "bubbleChart",
)

# Vendor instruction pages ship inside purchased decks. They are not layouts.
# The second group catches "how to use this template" tutorials, which are reliably
# identifiable because they walk the reader through the PowerPoint UI — real slide
# content does not tell its audience which ribbon tab to click.
VENDOR_RE = re.compile(
    r"持续更新|免费获取|咨询|更多模版|更多优惠|双击打开即可安装|如何一键修改|"
    r"版权|购买|售后|微信|淘宝|店铺|字体安装|安装字体|使用说明|版本："
    r"|选项卡|幻灯片母版|配色方案|变体|点击\s*【|选择\s*【|右击|使用模板时",
)

ROLE_PATTERNS = (
    ("closing", re.compile(r"THANK\s*YOU|感谢聆听|谢谢聆听|感谢观看|谢谢观看", re.I)),
    ("agenda", re.compile(r"目录|CONTENTS|Catalog\s*Page", re.I)),
    ("timeline", re.compile(r"时间轴|timeline|里程碑|roadmap|历程", re.I)),
    ("comparison", re.compile(r"\bVS\b|对比|优势\s*[&/]\s*不足|优劣|before\s*&?\s*after", re.I)),
    ("process", re.compile(r"流程|步骤|process|workflow|方法论|实施路径", re.I)),
    ("risk", re.compile(r"风险|问题分析|挑战|risk|问题及", re.I)),
    ("method", re.compile(r"研究方法|技术路线|method|实验设计|方案设计", re.I)),
    ("quote", re.compile(r"^[“\"']|案例|观点|insight", re.I)),
)

CHART_ROLE = {
    "barChart": "bar-chart", "bar3DChart": "bar-chart",
    "lineChart": "line-chart", "areaChart": "line-chart",
    "pieChart": "composition-chart", "doughnutChart": "composition-chart",
    "scatterChart": "scatter-chart", "bubbleChart": "priority-matrix",
    "radarChart": "radar-chart",
}

COLORWAYS = {
    "蓝白": "blue-white", "红蓝": "red-blue", "橙蓝": "orange-blue",
    "黄绿": "yellow-green", "绿金": "green-gold",
}


def _text_runs(root: ET.Element) -> list[str]:
    return [e.text.strip() for e in root.iter(f"{{{A_NS}}}t") if e.text and e.text.strip()]


def _chart_kinds(archive: zipfile.ZipFile, part: str) -> list[str]:
    try:
        root = ET.fromstring(archive.read(part))
    except (KeyError, ET.ParseError):
        return []
    return [kind for kind in CHART_KINDS if root.find(f".//{{{C_NS}}}{kind}") is not None]


def _slide_charts(archive: zipfile.ZipFile, names: list[str], num: int) -> list[str]:
    relpart = f"ppt/slides/_rels/slide{num}.xml.rels"
    if relpart not in names:
        return []
    kinds: list[str] = []
    for rel in ET.fromstring(archive.read(relpart)):
        target = rel.get("Target", "")
        if "charts/chart" in target and target.endswith(".xml"):
            kinds += _chart_kinds(archive, "ppt/charts/" + target.split("charts/")[-1])
    return sorted(set(kinds))


def _is_ascii_ish(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) > 0.8


def _density(chars: int) -> str:
    if chars < 60:
        return "sparse"
    if chars < 260:
        return "light"
    if chars < 620:
        return "medium"
    return "dense"


def classify(texts: list[str], chars: int, pics: int, groups: int,
             charts: list[str], position: int) -> str:
    joined = " ".join(texts[:8])
    for role, pattern in ROLE_PATTERNS:
        if pattern.search(joined):
            return role
    if charts:
        return CHART_ROLE.get(charts[0], "chart")
    # Covers sit behind the vendor front matter, so position counts kept slides only.
    if position <= 6 and chars < 260 and pics:
        return "cover"
    if chars < 60:
        return "section"
    if pics >= 3:
        return "gallery"
    if groups >= 3:
        return "diagram"
    if pics and chars < 500:
        return "image-and-claim"
    if chars >= 620:
        return "text-dense"
    return "body"


def index_deck(path: Path, root: Path | None = None) -> dict:
    rel = str(path.relative_to(root)) if root and root in path.parents else path.name
    record: dict = {"deck": path.name, "path": str(path.resolve()), "relpath": rel}
    colorway = next((v for k, v in COLORWAYS.items() if k in path.name), None)
    if colorway:
        record["colorway"] = colorway
    slides: list[dict] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            entries = sorted(
                (int(SLIDE_RE.fullmatch(n).group(1)), n)
                for n in names if SLIDE_RE.fullmatch(n)
            )
            for num, name in entries:
                node = ET.fromstring(archive.read(name))
                texts = _text_runs(node)
                joined = " ".join(texts[:10])
                if VENDOR_RE.search(joined):
                    continue
                chars = sum(len(t) for t in texts)
                pics = len(node.findall(f".//{{{P_NS}}}pic"))
                groups = len(node.findall(f".//{{{P_NS}}}grpSp"))
                charts = _slide_charts(archive, names, num)
                if not (chars or pics or groups or charts):
                    continue  # a blank spacer page is not a layout
                position = len(slides) + 1
                title = next((t for t in texts if len(t) >= 2 and not _is_ascii_ish(t)), "")
                subtitle = next((t for t in texts if len(t) >= 4 and _is_ascii_ish(t)), "")
                slides.append({
                    "slide": num,
                    "role": classify(texts, chars, pics, groups, charts, position),
                    "density": _density(chars),
                    "title": title[:40],
                    "subtitle": subtitle[:48],
                    "chars": chars,
                    "runs": len(texts),
                    "pics": pics,
                    "tables": len(node.findall(f".//{{{A_NS}}}tbl")),
                    "groups": groups,
                    "charts": charts,
                })
    except (KeyError, OSError, ET.ParseError, zipfile.BadZipFile) as error:
        record["error"] = f"{type(error).__name__}: {error}"
        return record
    record["slides"] = slides
    record["usable"] = len(slides)
    return record


def find_decks(root: Path, excludes: list[str]) -> list[Path]:
    terms = [term.casefold() for term in excludes]
    candidates = [root] if root.is_file() else root.rglob("*")
    return sorted(
        (
            path for path in candidates
            if path.is_file()
            and path.suffix.casefold() in OOXML_SUFFIXES
            and not path.name.startswith(("~$", "._"))
            and not any(term in str(path).casefold() for term in terms)
        ),
        key=lambda path: str(path).casefold(),
    )


def summarize(records: list[dict]) -> dict:
    roles: dict[str, int] = {}
    for record in records:
        for slide in record.get("slides", []):
            roles[slide["role"]] = roles.get(slide["role"], 0) + 1
    return {
        "decks": len(records),
        "errors": sum("error" in record for record in records),
        "slides": sum(record.get("usable", 0) for record in records),
        "roles": dict(sorted(roles.items(), key=lambda kv: -kv[1])),
    }


def self_test() -> None:
    slide = (
        f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}"><p:cSld><p:spTree>'
        f'<a:t>年度工作时间轴</a:t><a:t>Work Report-Timeline</a:t>'
        f'<p:pic/><p:grpSp/><p:grpSp/><p:grpSp/>'
        f"</p:spTree></p:cSld></p:sld>"
    )
    vendor = f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}"><a:t>模板持续更新中，更新后可免费获取</a:t></p:sld>'
    # A tutorial page carrying a picture and little text otherwise looks like a cover.
    tutorial = (f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}"><p:cSld><p:spTree>'
                f'<a:t>点击</a:t><a:t>【</a:t><a:t>视图</a:t><a:t>】</a:t>'
                f'<a:t>选项卡，选择</a:t><a:t>幻灯片母版</a:t><p:pic/>'
                f"</p:spTree></p:cSld></p:sld>")
    blank = f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}"><p:cSld><p:spTree/></p:cSld></p:sld>'
    cover = (f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}"><p:cSld><p:spTree>'
             f'<a:t>年终述职报告</a:t><p:pic/></p:spTree></p:cSld></p:sld>')
    with tempfile.TemporaryDirectory() as directory:
        deck = Path(directory) / "中文100页工作汇报PPT（蓝白配色）.pptx"
        with zipfile.ZipFile(deck, "w") as archive:
            archive.writestr("ppt/slides/slide1.xml", blank)
            for n in range(2, 7):  # vendor front matter, as shipped
                archive.writestr(f"ppt/slides/slide{n}.xml", vendor)
            archive.writestr("ppt/slides/slide7.xml", tutorial)
            archive.writestr("ppt/slides/slide8.xml", cover)
            archive.writestr("ppt/slides/slide9.xml", slide)
        record = index_deck(deck)
        assert record["usable"] == 2, record
        assert record["colorway"] == "blue-white", record
        # The cover sits at slide 8 but is the 1st kept slide, so it must still
        # classify as a cover rather than losing out to the position cutoff.
        first, second = record["slides"]
        assert first["slide"] == 8 and first["role"] == "cover", first
        assert second["slide"] == 9 and second["role"] == "timeline", second
        assert second["title"] == "年度工作时间轴", second
        assert second["subtitle"] == "Work Report-Timeline", second
        assert second["groups"] == 3 and second["pics"] == 1, second
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, help="PPTX file or directory to index")
    parser.add_argument("--exclude", action="append", default=[],
                        help="skip paths containing this term; repeat as needed")
    parser.add_argument("--limit", type=int, help="index only the first N decks")
    parser.add_argument("--output", type=Path, help="write the slide index as JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.root is None or not args.root.exists():
        parser.error("root must be an existing PPTX file or directory")

    paths = find_decks(args.root, args.exclude)
    if args.limit is not None:
        paths = paths[: max(args.limit, 0)]
    root = args.root if args.root.is_dir() else args.root.parent
    records = [index_deck(path, root) for path in paths]
    summary = summarize(records)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {"summary": summary, "decks": records}
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {summary['slides']} slides from {summary['decks']} decks to {args.output}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())
