#!/usr/bin/env python3
"""Build README.md from the profile template."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "README.template.md"
README = ROOT / "README.md"


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    README.write_text(template, encoding="utf-8", newline="\n")
    print(f"README written to {README.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
