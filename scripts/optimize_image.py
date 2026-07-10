#!/usr/bin/env python3
"""Prepare the source portrait for ASCII and colored SVG conversion."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "assets" / "Gus.jpg"
DEFAULT_OUTPUT = ROOT / "assets" / "Gus-optimized.png"


def optimize(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    image = Image.open(source).convert("RGB")

    width, height = image.size
    crop_box = (0, int(height * 0.22), width, height)
    image = image.crop(crop_box)

    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Brightness(image).enhance(1.04)
    image = ImageEnhance.Contrast(image).enhance(1.32)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=115, threshold=3))

    # Keep the circular portrait and remove the surrounding black stage space.
    masked_width, masked_height = image.size
    subject_mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(subject_mask)
    draw.ellipse(
        (
            -int(masked_width * 0.12),
            -int(masked_height * 0.02),
            int(masked_width * 1.10),
            int(masked_height * 1.12),
        ),
        fill=255,
    )
    subject_mask = subject_mask.filter(ImageFilter.GaussianBlur(radius=7))
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
