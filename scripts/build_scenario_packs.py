#!/usr/bin/env python3
"""Turn a slide index into scenario packs: plain-language choices a beginner can make.

A local library is unusable as a file list. Filenames describe topics ("黑板风格",
"杭州亚运会"), not message types, so the user cannot tell which deck answers
"I need to show a trend". This collapses hundreds of decks into a handful of named
scenarios, each already resolved to a concrete deck plus an ordered slide list.

Input:  the JSON written by index_slides.py
Output: references/local-library.json (metadata only; no copyrighted slides)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# Layout-bank families. These carry native charts and ship in parallel colorways,
# which is what makes automatic theme selection possible.
FAMILIES = (
    ("work-report-cn-300", re.compile(r"中文300页.*工作汇报"), "zh", "中文长篇工作汇报"),
    ("work-report-cn-100", re.compile(r"中文100页.*工作汇报"), "zh", "中文标准工作汇报"),
    ("work-report-en-300", re.compile(r"英文300页.*工作汇报"), "en", "English long-form report"),
    ("work-report-en-150", re.compile(r"英文150页.*工作汇报"), "en", "English standard report"),
)

COLORWAY_THEME = {
    "blue-white": "academic-blue",
    "red-blue": "institutional-red",
    "orange-blue": "green-gold",
    "yellow-green": "green-gold",
}

# Ordered role recipes, in the vocabulary index_slides.py emits.
SCENARIOS = {
    "年终述职": {
        "en": "year_end_review", "length": "12-18 slides",
        "roles": ["cover", "agenda", "body", "bar-chart", "timeline",
                  "line-chart", "comparison", "risk", "closing"],
    },
    "季度工作汇报": {
        "en": "quarterly_report", "length": "10-14 slides",
        "roles": ["cover", "agenda", "body", "bar-chart", "process",
                  "line-chart", "closing"],
    },
    "项目提案": {
        "en": "project_proposal", "length": "12-16 slides",
        "roles": ["cover", "body", "section", "risk", "process",
                  "comparison", "bar-chart", "timeline", "closing"],
    },
    "毕业答辩": {
        "en": "thesis_defense", "length": "10-15 slides",
        "roles": ["cover", "agenda", "method", "diagram", "bar-chart",
                  "line-chart", "comparison", "risk", "closing"],
    },
    "开题/中期汇报": {
        "en": "proposal_review", "length": "10-14 slides",
        "roles": ["cover", "agenda", "body", "method", "timeline",
                  "process", "risk", "closing"],
    },
    "文献汇报": {
        "en": "journal_club", "length": "10-14 slides",
        "roles": ["cover", "body", "method", "image-and-claim", "diagram",
                  "line-chart", "body", "closing"],
    },
    "学术报告": {
        "en": "academic_talk", "length": "14-20 slides",
        "roles": ["cover", "agenda", "body", "method", "diagram", "gallery",
                  "bar-chart", "line-chart", "comparison", "closing"],
    },
    "商业路演": {
        "en": "pitch", "length": "10-14 slides",
        "roles": ["cover", "body", "bar-chart", "comparison", "process",
                  "timeline", "risk", "closing"],
    },
}

# When the exact role is absent, fall back in this order before giving up.
ROLE_FALLBACK = {
    "method": ["process", "diagram", "body"],
    "diagram": ["image-and-claim", "gallery", "body"],
    "risk": ["comparison", "body"],
    "timeline": ["process", "body"],
    "comparison": ["body"],
    "gallery": ["image-and-claim", "body"],
    "line-chart": ["bar-chart", "composition-chart"],
    "bar-chart": ["line-chart", "composition-chart"],
    "agenda": ["section", "body"],
    "cover": ["section"],
    "closing": ["section", "body"],
    "body": ["image-and-claim", "text-dense", "diagram"],
}

# Structural slides must be unique in a deck; content layouts may repeat if that is
# the only way to cover a role. A repeated layout beats a missing part of the story.
UNIQUE_ROLES = {"cover", "agenda", "closing", "section"}

PREFERRED_DENSITY = {"cover": "light", "section": "sparse", "agenda": "light",
                     "closing": "sparse"}


def family_of(deck_name: str) -> tuple[str, str, str] | None:
    for key, pattern, language, label in FAMILIES:
        if pattern.search(deck_name):
            return key, language, label
    return None


CHART_ROLES = {"bar-chart", "line-chart", "composition-chart", "scatter-chart",
               "radar-chart", "priority-matrix"}
# Above this, a slide is a bespoke showpiece (a world map carrying nine charts)
# rather than a layout that adapts to someone else's content.
BUSY_ELEMENTS = 6


def score(slide: dict, role: str) -> tuple:
    """Rank candidates by fit, preferring the cleanest layout that carries the message.

    Maximum decoration is the wrong target: a generic chart step needs one clear
    chart, not the deck's most elaborate infographic.
    """
    wanted = PREFERRED_DENSITY.get(role, "medium")
    density_fit = 0 if slide["density"] == wanted else 1
    ideal_charts = 1 if role in CHART_ROLES else 0
    chart_excess = abs(len(slide["charts"]) - ideal_charts)
    busy_excess = max(0, slide["groups"] + slide["pics"] - BUSY_ELEMENTS)
    return (density_fit, chart_excess, busy_excess, slide["slide"])


def pick(slides: list[dict], role: str, used: set[int]) -> dict | None:
    """Resolve a role to a slide, preferring an unused one before allowing reuse."""
    chain = [role] + ROLE_FALLBACK.get(role, [])
    for allow_reuse in (False, True):
        if allow_reuse and role in UNIQUE_ROLES:
            break
        for candidate_role in chain:
            pool = [s for s in slides if s["role"] == candidate_role
                    and (allow_reuse or s["slide"] not in used)]
            if pool:
                best = min(pool, key=lambda s: score(s, role))
                return {**best, "matched_as": candidate_role,
                        "reused": allow_reuse and best["slide"] in used}
    return None


def build_packs(index: dict) -> dict:
    banks: dict[str, dict] = {}
    for record in index.get("decks", []):
        if "error" in record or not record.get("slides"):
            continue
        found = family_of(record["deck"])
        if not found:
            continue
        key, language, label = found
        colorway = record.get("colorway", "default")
        banks.setdefault(key, {"label": label, "language": language, "colorways": {}})
        banks[key]["colorways"][colorway] = {
            "relpath": record["relpath"],
            "usable_slides": record["usable"],
            "theme": COLORWAY_THEME.get(colorway, "academic-blue"),
        }

    packs = {}
    for name, spec in SCENARIOS.items():
        family = _best_family(banks, spec)
        if not family:
            continue
        key, colorway = family
        record = _record_for(index, banks[key]["colorways"][colorway]["relpath"])
        used: set[int] = set()
        steps, missing = [], []
        for role in spec["roles"]:
            chosen = pick(record["slides"], role, used)
            if not chosen:
                missing.append(role)
                continue
            used.add(chosen["slide"])
            steps.append({
                "role": role,
                "slide": chosen["slide"],
                "matched_as": chosen["matched_as"],
                "reused_layout": chosen["reused"],
                "density": chosen["density"],
                "title_sample": chosen["title"],
                "charts": chosen["charts"],
            })
        packs[name] = {
            "en": spec["en"],
            "recommended_length": spec["length"],
            "family": key,
            "default_colorway": colorway,
            "theme": banks[key]["colorways"][colorway]["theme"],
            "steps": steps,
            "unmatched_roles": missing,
        }
    return {"version": 1, "families": banks, "packs": packs}


def _best_family(banks: dict, spec: dict) -> tuple[str, str] | None:
    """Prefer a Chinese chart-bearing bank; prefer the longer bank for long talks."""
    order = ["work-report-cn-300", "work-report-cn-100",
             "work-report-en-300", "work-report-en-150"]
    if "10-14" in spec["length"] or "10-15" in spec["length"]:
        order = ["work-report-cn-100", "work-report-cn-300",
                 "work-report-en-150", "work-report-en-300"]
    for key in order:
        if key in banks and banks[key]["colorways"]:
            preferred = ["blue-white", "red-blue", "orange-blue", "yellow-green"]
            if spec["en"] in {"thesis_defense", "journal_club", "academic_talk",
                              "proposal_review"}:
                preferred = ["blue-white", "red-blue", "yellow-green", "orange-blue"]
            for colorway in preferred:
                if colorway in banks[key]["colorways"]:
                    return key, colorway
            return key, next(iter(banks[key]["colorways"]))
    return None


def _record_for(index: dict, relpath: str) -> dict:
    return next(r for r in index["decks"] if r.get("relpath") == relpath)


def self_test() -> None:
    def slide(num, role, density="medium", groups=0, pics=0, charts=()):
        return {"slide": num, "role": role, "density": density, "title": f"t{num}",
                "subtitle": "", "chars": 300, "runs": 10, "pics": pics,
                "tables": 0, "groups": groups, "charts": list(charts)}

    index = {"decks": [{
        "deck": "中文100页工作汇报PPT（蓝白配色）.pptx",
        "relpath": "a/中文100页工作汇报PPT（蓝白配色）.pptx",
        "colorway": "blue-white", "usable": 8,
        "slides": [
            slide(7, "cover", "light", pics=1), slide(10, "agenda", "light"),
            slide(18, "body"), slide(20, "process"), slide(27, "timeline"),
            slide(31, "bar-chart", charts=["barChart"]),
            # A nine-chart world map is still a bar-chart slide, but a far worse
            # pick for a generic chart step than the single-chart slide above.
            slide(33, "bar-chart", groups=9, charts=["barChart"] * 9),
            slide(35, "line-chart", charts=["lineChart"]),
            slide(40, "comparison"), slide(50, "closing", "sparse"),
        ],
    }]}
    result = build_packs(index)
    pack = result["packs"]["年终述职"]
    assert pack["family"] == "work-report-cn-100", pack
    assert pack["theme"] == "academic-blue", pack
    slides = [step["slide"] for step in pack["steps"]]
    assert 27 in slides and 31 in slides, slides
    assert 33 not in slides, "the showpiece map must lose to the plain bar chart"
    # 'comparison' consumes slide 40 first; 'risk' must still resolve, by reuse.
    risk = next(s for s in pack["steps"] if s["role"] == "risk")
    assert risk["matched_as"] == "comparison" and risk["reused_layout"], risk
    assert not pack["unmatched_roles"], pack["unmatched_roles"]
    # Structural roles must never be satisfied by reuse.
    for step in pack["steps"]:
        if step["role"] in UNIQUE_ROLES:
            assert not step["reused_layout"], step
    assert [s["slide"] for s in pack["steps"]].count(7) == 1, pack["steps"]
    defense = result["packs"]["毕业答辩"]
    assert defense["default_colorway"] == "blue-white", defense
    method = next(s for s in defense["steps"] if s["role"] == "method")
    assert method["matched_as"] == "process", method
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", nargs="?", type=Path, help="JSON from index_slides.py")
    parser.add_argument("--output", type=Path, help="write local-library.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.index is None or not args.index.exists():
        parser.error("index must be an existing JSON file from index_slides.py")

    index = json.loads(args.index.read_text(encoding="utf-8"))
    result = build_packs(index)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        print(f"wrote {len(result['packs'])} packs to {args.output}")
    for name, pack in result["packs"].items():
        gaps = f"  MISSING={','.join(pack['unmatched_roles'])}" if pack["unmatched_roles"] else ""
        print(f"{name:<14} {pack['family']:<20} {len(pack['steps']):>2} slides{gaps}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
