#!/usr/bin/env python3
"""Prepare the source portrait for ASCII and colored SVG conversion."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "assets" / "cerati-2.jpeg"
DEFAULT_OUTPUT = ROOT / "assets" / "cerati-2-optimized.png"


def optimize(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    image = Image.open(source).convert("RGB")

    width, height = image.size
    crop_box = (
        int(width * 0.00),
        int(height * 0.18),
        int(width * 1.00),
        int(height * 0.98),
    )
    image = image.crop(crop_box)

    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Brightness(image).enhance(1.06)
    image = ImageEnhance.Contrast(image).enhance(1.28)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.filter(ImageFilter.UnsharpMask(radius=1.3, percent=110, threshold=4))

    # Preserve the stage silhouette: head, torso, microphone stand, and guitar.
    masked_width, masked_height = image.size
    subject_mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(subject_mask)
    draw.polygon(
        [
            (int(masked_width * 0.02), int(masked_height * 0.44)),
            (int(masked_width * 0.12), int(masked_height * 0.31)),
            (int(masked_width * 0.22), int(masked_height * 0.23)),
            (int(masked_width * 0.36), int(masked_height * 0.25)),
            (int(masked_width * 0.47), int(masked_height * 0.36)),
            (int(masked_width * 0.51), int(masked_height * 0.56)),
            (int(masked_width * 0.74), int(masked_height * 0.76)),
            (int(masked_width * 0.98), int(masked_height * 0.73)),
            (int(masked_width * 1.00), int(masked_height * 0.96)),
            (int(masked_width * 0.20), int(masked_height * 1.00)),
            (int(masked_width * 0.00), int(masked_height * 0.88)),
        ],
        fill=255,
    )
    draw.polygon(
        [
            (int(masked_width * 0.39), int(masked_height * 0.38)),
            (int(masked_width * 0.46), int(masked_height * 0.37)),
            (int(masked_width * 0.96), int(masked_height * 0.67)),
            (int(masked_width * 0.92), int(masked_height * 0.72)),
        ],
        fill=255,
    )
    draw.polygon(
        [
            (int(masked_width * 0.23), int(masked_height * 0.78)),
            (int(masked_width * 0.50), int(masked_height * 0.77)),
            (int(masked_width * 0.99), int(masked_height * 0.87)),
            (int(masked_width * 0.97), int(masked_height * 0.96)),
            (int(masked_width * 0.31), int(masked_height * 0.92)),
        ],
        fill=255,
    )
    subject_mask = subject_mask.filter(ImageFilter.GaussianBlur(radius=9))
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
