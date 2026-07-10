#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-assets/cerati-2.jpeg}"
OPTIMIZED="${2:-assets/cerati-2-optimized.png}"
OUTPUT="${3:-assets/profile-ascii.txt}"
WIDTH="${ASCII_WIDTH:-44}"

python scripts/optimize_image.py "$SOURCE" "$OPTIMIZED"
python scripts/image_to_ascii.py "$OPTIMIZED" "$OUTPUT" --width "$WIDTH"
python scripts/build_profile_svg.py "$OPTIMIZED" "$OUTPUT"
