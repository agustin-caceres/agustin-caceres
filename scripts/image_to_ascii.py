#!/usr/bin/env python3
"""Convert an optimized image into plain ASCII art."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "assets" / "Dynamizado-optimized.png"
DEFAULT_OUTPUT = ROOT / "assets" / "profile-ascii.txt"
RAMP = "@#S%?*+;:,. "


def image_to_ascii(source: Path, output: Path, width: int) -> None:
    source = source.resolve()
    output = output.resolve()
    image = Image.open(source).convert("L")
    image = ImageOps.autocontrast(image, cutoff=1)

    original_width, original_height = image.size
    aspect = original_height / original_width
    # Terminal glyphs are taller than they are wide, so reduce the rendered height.
    height = max(1, int(width * aspect * 0.42))
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    pixels = image.getdata()
    last_index = len(RAMP) - 1
    # Lighten midtones non-linearly so the portrait reads as a crisp terminal
    # silhouette instead of a solid rectangle of characters.
    chars = [
        " " if pixel >= 224 else RAMP[round((pixel / 224) ** 0.68 * (last_index - 1))]
        for pixel in pixels
    ]
    lines = ["".join(chars[index : index + width]).rstrip() for index in range(0, len(chars), width)]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ASCII art written to {output.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--width", type=int, default=44)
    args = parser.parse_args()

    image_to_ascii(args.source, args.output, args.width)


if __name__ == "__main__":
    main()
