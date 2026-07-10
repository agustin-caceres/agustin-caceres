#!/usr/bin/env python3
"""Prepare the source portrait for ASCII and colored SVG conversion."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "assets" / "Dynamizado.jpg"
DEFAULT_OUTPUT = ROOT / "assets" / "Dynamizado-optimized.png"


def optimize(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    image = Image.open(source).convert("RGB")

    # Remove empty stage space while preserving the full pose and guitar neck.
    width, height = image.size
    crop_box = (
        int(width * 0.00),
        int(height * 0.08),
        int(width * 1.00),
        int(height * 0.98),
    )
    image = image.crop(crop_box)

    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Brightness(image).enhance(1.08)
    image = ImageEnhance.Contrast(image).enhance(1.22)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=4))

    # Isolate the performer and the guitar from stage lights and haze. The broad
    # shapes survive terminal-sized rendering better than the photographic background.
    masked_width, masked_height = image.size
    subject_mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(subject_mask)
    subject_outline = [
        (int(masked_width * 0.09), int(masked_height * 0.15)),
        (int(masked_width * 0.18), int(masked_height * 0.06)),
        (int(masked_width * 0.32), int(masked_height * 0.07)),
        (int(masked_width * 0.41), int(masked_height * 0.18)),
        (int(masked_width * 0.56), int(masked_height * 0.34)),
        (int(masked_width * 0.58), int(masked_height * 0.56)),
        (int(masked_width * 0.72), masked_height),
        (int(masked_width * 0.30), masked_height),
        (int(masked_width * 0.22), int(masked_height * 0.72)),
        (int(masked_width * 0.08), int(masked_height * 0.64)),
        (int(masked_width * 0.02), int(masked_height * 0.43)),
    ]
    draw.polygon(subject_outline, fill=255)
    # Keep the long diagonal neck and headstock as a separate silhouette.
    draw.polygon(
        [
            (int(masked_width * 0.20), int(masked_height * 0.70)),
            (int(masked_width * 0.31), int(masked_height * 0.73)),
            (int(masked_width * 0.97), int(masked_height * 0.08)),
            (int(masked_width * 0.87), int(masked_height * 0.04)),
        ],
        fill=255,
    )
    subject_mask = subject_mask.filter(ImageFilter.GaussianBlur(radius=10))
    image = Image.composite(image, Image.new("RGB", image.size, "white"), subject_mask)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"Optimized image written to {output.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    optimize(args.source, args.output)


if __name__ == "__main__":
    main()
