#!/usr/bin/env python3
"""Extract usable colour palettes from colour-card images in a local library.

Colour cards ship as JPGs, which a deck cannot consume. This reads the actual
pixels, so the result is exact rather than transcribed, and keeps only pairs that
are legible as text on background — an attractive palette that fails contrast is
not a usable palette.

Requires Pillow. Outputs references/palette-library.json (hex values only, which
are facts about colour rather than copyrightable expression).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image

# Pillow >= 9.1 moved the constant onto an enum; keep both paths working.
MEDIANCUT = getattr(getattr(Image, "Quantize", Image), "MEDIANCUT")

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
SAMPLE_EDGE = 240
QUANTIZE_COLORS = 12
MIN_SHARE = 0.04
# Card stock and print margins are background, not palette.
NEAR_WHITE = 244
NEAR_BLACK = 14
# Slide type is large by definition: titles run 24pt+ and body 16pt+, so WCAG AA
# large-text (3.0) is the usability bar. Citations and source notes are small, so
# each pair also records whether it clears the 4.5 small-text bar.
AA_LARGE = 3.0
AA_SMALL = 4.5


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for value in rgb:
        srgb = value / 255
        channels.append(srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    light, dark = sorted((_luminance(first), _luminance(second)), reverse=True)
    return round((light + 0.05) / (dark + 0.05), 2)


def _is_background(rgb: tuple[int, int, int]) -> bool:
    return all(c >= NEAR_WHITE for c in rgb) or all(c <= NEAR_BLACK for c in rgb)


def dominant_colors(path: Path) -> list[dict]:
    with Image.open(path) as handle:
        image = handle.convert("RGB")
        image.thumbnail((SAMPLE_EDGE, SAMPLE_EDGE))
        quantized = image.quantize(colors=QUANTIZE_COLORS, method=MEDIANCUT)
        palette = quantized.getpalette() or []
        total = quantized.width * quantized.height
        counts = sorted(quantized.getcolors() or [], key=lambda pair: -pair[0])

    colors: list[dict] = []
    for count, index in counts:
        rgb = tuple(palette[index * 3: index * 3 + 3])
        share = count / total
        if share < MIN_SHARE or _is_background(rgb) or len(rgb) != 3:
            continue
        if any(contrast(rgb, tuple(int(c["hex"][i:i + 2], 16) for i in (1, 3, 5))) < 1.15
               for c in colors):
            continue  # visually the same swatch the quantizer split in two
        colors.append({"hex": _hex(rgb), "share": round(share, 3)})
    return colors


def build_palette(path: Path, root: Path) -> dict | None:
    colors = dominant_colors(path)
    if len(colors) < 2:
        return None
    rgbs = [tuple(int(c["hex"][i:i + 2], 16) for i in (1, 3, 5)) for c in colors]
    pairs = [
        {"background": colors[i]["hex"], "foreground": colors[j]["hex"],
         "contrast": contrast(rgbs[i], rgbs[j]),
         "ok_small_text": contrast(rgbs[i], rgbs[j]) >= AA_SMALL}
        for i in range(len(colors)) for j in range(len(colors)) if i != j
    ]
    legible = sorted((p for p in pairs if p["contrast"] >= AA_LARGE),
                     key=lambda p: -p["contrast"])
    return {
        "source": str(path.relative_to(root)),
        "family": path.parent.name,
        "colors": colors,
        "dominant": colors[0]["hex"],
        "accent": colors[1]["hex"],
        "legible_pairs": legible[:4],
        "usable_as_theme": bool(legible),
    }


def find_images(root: Path, includes: list[str]) -> list[Path]:
    terms = [term.casefold() for term in includes]
    return sorted(
        (path for path in root.rglob("*")
         if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
         and not path.name.startswith(("~$", "._"))
         and (not terms or any(term in str(path).casefold() for term in terms))),
        key=lambda path: str(path).casefold(),
    )


def self_test() -> None:
    assert contrast((255, 255, 255), (0, 0, 0)) == 21.0
    assert contrast((0, 0, 0), (255, 255, 255)) == 21.0
    # The vintage card's own green-on-tan is title-safe but not caption-safe.
    vintage = contrast((63, 77, 41), (185, 162, 118))
    assert AA_LARGE <= vintage < AA_SMALL, vintage
    assert _hex((63, 77, 41)) == "#3F4D29"
    assert _is_background((255, 255, 255)) and _is_background((2, 2, 2))
    assert not _is_background((63, 77, 41))

    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        card = root / "card.png"
        image = Image.new("RGB", (100, 100), (63, 77, 41))
        for x in range(50):
            for y in range(100):
                image.putpixel((x, y), (185, 162, 118))
        image.save(card)
        palette = build_palette(card, root)
        assert palette and palette["usable_as_theme"], palette
        assert {c["hex"] for c in palette["colors"]} == {"#3F4D29", "#B9A276"}, palette
        best = palette["legible_pairs"][0]
        assert best["contrast"] >= AA_LARGE and not best["ok_small_text"], best
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, help="directory of colour-card images")
    parser.add_argument("--include", action="append", default=[],
                        help="OR path filter; repeat as needed")
    parser.add_argument("--output", type=Path, help="write palette-library.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.root is None or not args.root.exists():
        parser.error("root must be an existing directory")

    palettes = [p for p in (build_palette(path, args.root)
                            for path in find_images(args.root, args.include)) if p]
    usable = [p for p in palettes if p["usable_as_theme"]]
    payload = {"version": 1, "palettes": usable,
               "summary": {"scanned": len(palettes), "usable": len(usable)}}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        print(f"wrote {len(usable)} palettes to {args.output}")
    for palette in usable[:40]:
        swatches = " ".join(c["hex"] for c in palette["colors"][:5])
        print(f"{palette['family'][:16]:<16} {swatches:<44} {palette['source'][-40:]}")
    print(f"scanned={len(palettes)} usable={len(usable)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
