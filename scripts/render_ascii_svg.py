#!/usr/bin/env python3
"""Render plain ASCII art as theme-aware, terminal-colored SVG assets."""

from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "assets" / "Dynamizado-optimized.png"
DEFAULT_ASCII = ROOT / "assets" / "profile-ascii.txt"
DEFAULT_DARK = ROOT / "assets" / "profile-ascii-dark.svg"
DEFAULT_LIGHT = ROOT / "assets" / "profile-ascii-light.svg"

PALETTES = {
    "dark": {
        "cyan": "#39d6ff",
        "magenta": "#ff4fa3",
        "amber": "#ffd166",
        "neutral": "#e6edf3",
    },
    "light": {
        "cyan": "#006b87",
        "magenta": "#b0005b",
        "amber": "#8a5a00",
        "neutral": "#24292f",
    },
}


def color_role(pixel: tuple[int, int, int]) -> str:
    red, green, blue = pixel
    if blue > red * 1.12:
        return "cyan"
    if red > blue * 1.22 and blue > green * 1.08:
        return "magenta"
    if red > green * 1.22:
        return "amber"
    return "neutral"


def render_svg(image: Image.Image, lines: list[str], output: Path, theme: str) -> None:
    columns = max(map(len, lines))
    rows = len(lines)
    glyph_width = 8
    line_height = 14
    baseline = 12
    svg_width = columns * glyph_width
    svg_height = rows * line_height
    palette = PALETTES[theme]
    sampled = image.resize((columns, rows), Image.Resampling.LANCZOS).convert("RGB")

    elements: list[str] = []
    for row, line in enumerate(lines):
        for column, character in enumerate(line):
            if character == " ":
                continue
            fill = palette[color_role(sampled.getpixel((column, row)))]
            elements.append(
                f'<text x="{column * glyph_width}" y="{row * line_height + baseline}" '
                f'fill="{fill}">{escape(character)}</text>'
            )

    svg = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" '
            f'viewBox="0 0 {svg_width} {svg_height}" role="img" aria-labelledby="title">',
            "  <title id=\"title\">ASCII portrait of Gustavo Cerati playing guitar</title>",
            "  <g font-family=\"Consolas, 'Liberation Mono', monospace\" font-size=\"13\" "
            "font-weight=\"700\" xml:space=\"preserve\">",
            *(f"    {element}" for element in elements),
            "  </g>",
            "</svg>",
            "",
        ]
    )
    output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"{theme.capitalize()} SVG written to {output.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("ascii", nargs="?", type=Path, default=DEFAULT_ASCII)
    parser.add_argument("--dark-output", type=Path, default=DEFAULT_DARK)
    parser.add_argument("--light-output", type=Path, default=DEFAULT_LIGHT)
    args = parser.parse_args()

    image = Image.open(args.image)
    lines = args.ascii.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("ASCII source is empty")

    render_svg(image, lines, args.dark_output, "dark")
    render_svg(image, lines, args.light_output, "light")


if __name__ == "__main__":
    main()
