#!/usr/bin/env python3
"""Build full neofetch-style profile SVGs from the generated ASCII portrait."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "assets" / "Gus-optimized.png"
DEFAULT_ASCII = ROOT / "assets" / "profile-ascii.txt"
DEFAULT_DARK = ROOT / "dark_mode.svg"
DEFAULT_LIGHT = ROOT / "light_mode.svg"
DEFAULT_USER = "agustin-caceres"

DEFAULT_STATS = {
    "repo_data": "9",
    "star_data": "0",
    "follower_data": "11",
    "following_data": "11",
    "since_data": "2023",
}

PALETTES = {
    "dark": {
        "background": "#0d1117",
        "surface": "#161b22",
        "border": "#30363d",
        "text": "#c9d1d9",
        "muted": "#6e7681",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "accent": "#39d6ff",
        "magenta": "#ff4fa3",
        "amber": "#ffd166",
        "neutral": "#e6edf3",
        "success": "#3fb950",
        "danger": "#f85149",
    },
    "light": {
        "background": "#ffffff",
        "surface": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#24292f",
        "muted": "#57606a",
        "key": "#9a6700",
        "value": "#0969da",
        "accent": "#006b87",
        "magenta": "#b0005b",
        "amber": "#8a5a00",
        "neutral": "#24292f",
        "success": "#1a7f37",
        "danger": "#cf222e",
    },
}


def github_json(url: str, token: str | None) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "agustin-caceres-profile-readme",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_public_stats(username: str) -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("ACCESS_TOKEN")
    user = github_json(f"https://api.github.com/users/{username}", token)
    if not isinstance(user, dict):
        raise ValueError("Unexpected GitHub user response")

    stars = 0
    page = 1
    while True:
        repos = github_json(
            f"https://api.github.com/users/{username}/repos?per_page=100&type=owner&page={page}",
            token,
        )
        if not isinstance(repos, list) or not repos:
            break
        stars += sum(int(repo.get("stargazers_count", 0)) for repo in repos if isinstance(repo, dict))
        page += 1

    return {
        "repo_data": f"{int(user.get('public_repos', 0)):,}",
        "star_data": f"{stars:,}",
        "follower_data": f"{int(user.get('followers', 0)):,}",
        "following_data": f"{int(user.get('following', 0)):,}",
        "since_data": str(user.get("created_at", "2023")[:4]),
    }


def color_role(pixel: tuple[int, int, int], column: int, row: int, columns: int, rows: int) -> str:
    red, green, blue = pixel
    value = (red + green + blue) / 3
    saturation = max(pixel) - min(pixel)
    if saturation < 18:
        if value < 72:
            return "accent"
        if value < 142:
            return "magenta" if column > columns * 0.56 else "neutral"
        if value < 205:
            return "neutral" if row > rows * 0.35 else "amber"
        return "amber"
    if blue > red * 1.12:
        return "accent"
    if red > blue * 1.22 and blue > green * 1.08:
        return "magenta"
    if red > green * 1.22:
        return "amber"
    return "neutral"


def ascii_elements(image: Image.Image, lines: list[str], palette: dict[str, str]) -> list[str]:
    columns = max(map(len, lines))
    rows = len(lines)
    glyph_width = 8
    line_height = 16
    left = 28
    top = 48
    sampled = image.resize((columns, rows), Image.Resampling.LANCZOS).convert("RGB")
    elements: list[str] = []
    for row, line in enumerate(lines):
        for column, character in enumerate(line):
            if character == " ":
                continue
            role = color_role(sampled.getpixel((column, row)), column, row, columns, rows)
            elements.append(
                f'<text x="{left + column * glyph_width}" y="{top + row * line_height}" '
                f'fill="{palette[role]}">{escape(character)}</text>'
            )
    return elements


def section_title(text: str, x: int, y: int, palette: dict[str, str]) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{palette["text"]}">'
        f'<tspan>{escape(text)}</tspan>'
        f'<tspan fill="{palette["muted"]}"> {"-" * 34}</tspan>'
        "</text>"
    )


def info_line(
    key: str,
    value: str,
    x: int,
    y: int,
    palette: dict[str, str],
    value_id: str | None = None,
    dot_id: str | None = None,
    width: int = 34,
) -> str:
    dots = max(2, width - len(key) - len(value))
    dot_attrs = f' id="{dot_id}"' if dot_id else ""
    value_attrs = f' id="{value_id}"' if value_id else ""
    return (
        f'<text x="{x}" y="{y}" fill="{palette["text"]}">'
        f'<tspan fill="{palette["muted"]}">. </tspan>'
        f'<tspan fill="{palette["key"]}">{escape(key)}</tspan>'
        f'<tspan>:</tspan>'
        f'<tspan{dot_attrs} fill="{palette["muted"]}"> {"." * dots} </tspan>'
        f'<tspan{value_attrs} fill="{palette["value"]}">{escape(value)}</tspan>'
        "</text>"
    )


def render_svg(
    image: Image.Image,
    lines: list[str],
    output: Path,
    theme: str,
    stats: dict[str, str],
) -> None:
    palette = PALETTES[theme]
    width = 985
    height = 530
    right_x = 420
    elements = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}px" height="{height}px" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "  <title id=\"title\">Agustin Caceres GitHub profile README</title>",
        "  <desc id=\"desc\">Terminal style profile card with ASCII portrait and profile data.</desc>",
        "  <style>",
        "    text { font-family: Consolas, 'Liberation Mono', monospace; font-size: 16px; font-weight: 700; white-space: pre; }",
        "  </style>",
        f'  <rect width="{width}" height="{height}" rx="15" fill="{palette["background"]}"/>',
        f'  <rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="12" '
        f'fill="{palette["surface"]}" stroke="{palette["border"]}"/>',
        "  <g>",
        *(f"    {element}" for element in ascii_elements(image, lines, palette)),
        "  </g>",
        "  <g>",
        f'    <text x="{right_x}" y="46" fill="{palette["text"]}">'
        f'<tspan fill="{palette["accent"]}">agustin</tspan>@github'
        f'<tspan fill="{palette["muted"]}"> {"-" * 38}</tspan></text>',
        "    "
        + info_line("Name", "Agustin Caceres", right_x, 76, palette),
        "    "
        + info_line("Focus", "Data Governance, Backend & AI", right_x, 100, palette),
        "    "
        + info_line("Builder", "Bedosbe", right_x, 124, palette),
        "    "
        + info_line("Builder", "iAlex", right_x, 148, palette),
        "    "
        + info_line("Intersection", "Technology, business & law", right_x, 172, palette),
        f'    <text x="{right_x}" y="204" fill="{palette["text"]}">'
        f'<tspan fill="{palette["muted"]}">. </tspan>'
        f'<tspan fill="{palette["key"]}">Palette</tspan>: '
        f'<tspan fill="{palette["accent"]}">cyan</tspan> '
        f'<tspan fill="{palette["magenta"]}">magenta</tspan> '
        f'<tspan fill="{palette["amber"]}">amber</tspan></text>',
        "    " + section_title("Projects", right_x, 248, palette),
        "    "
        + info_line("Bedosbe", "B2B commerce", right_x, 278, palette),
        "    "
        + info_line("iAlex", "Legal AI", right_x, 302, palette),
        "    "
        + info_line("Mode", "Ship, learn, repeat", right_x, 326, palette),
        "    " + section_title("GitHub", right_x, 370, palette),
        "    "
        + info_line("Repos", stats["repo_data"], right_x, 400, palette, "repo_data", "repo_data_dots", 18),
        "    "
        + info_line("Stars", stats["star_data"], right_x + 210, 400, palette, "star_data", "star_data_dots", 18),
        "    "
        + info_line("Followers", stats["follower_data"], right_x, 424, palette, "follower_data", "follower_data_dots", 18),
        "    "
        + info_line("Following", stats["following_data"], right_x + 210, 424, palette, "following_data", "following_data_dots", 18),
        "    "
        + info_line("Since", stats["since_data"], right_x, 448, palette, "since_data", "since_data_dots", 18),
        "    " + section_title("Contact", right_x, 482, palette),
        "    "
        + info_line("Social", "LinkedIn / X / Instagram", right_x, 512, palette),
        "  </g>",
        "</svg>",
        "",
    ]
    output.write_text("\n".join(elements), encoding="utf-8", newline="\n")
    print(f"{theme.capitalize()} profile SVG written to {output.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("ascii", nargs="?", type=Path, default=DEFAULT_ASCII)
    parser.add_argument("--dark-output", type=Path, default=DEFAULT_DARK)
    parser.add_argument("--light-output", type=Path, default=DEFAULT_LIGHT)
    parser.add_argument("--github-user", default=os.environ.get("USER_NAME", DEFAULT_USER))
    parser.add_argument("--fetch-stats", action="store_true")
    args = parser.parse_args()

    stats = DEFAULT_STATS.copy()
    if args.fetch_stats:
        try:
            stats.update(fetch_public_stats(args.github_user))
        except (OSError, URLError, TimeoutError, ValueError) as exc:
            print(f"Could not fetch GitHub stats, using defaults: {exc}")

    image = Image.open(args.image).convert("RGB")
    lines = args.ascii.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("ASCII source is empty")

    render_svg(image, lines, args.dark_output, "dark", stats)
    render_svg(image, lines, args.light_output, "light", stats)


if __name__ == "__main__":
    main()
