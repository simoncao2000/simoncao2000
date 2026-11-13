"""`python -m generator`: write every profile image to assets/<theme>/.

The static blocks are rebuilt every run; their output is identical unless the
design or content changes. The LeetCode cards are only rewritten when the
fetch succeeds, so an outage never replaces good data with nothing.
"""
import datetime as dt
from pathlib import Path

from . import content, leetcode_api
from .blocks import hero, leetcode, projects, stack
from .palette import THEMES

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def write(theme, name, svg):
    """Save one image as assets/<theme>/<name>.svg."""
    folder = ASSETS / theme
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.svg").write_text(svg, encoding="utf-8")


def build_static(theme, t):
    """Hero, projects and stack for one theme."""
    write(theme, "hero", hero.build(t))
    write(theme, "projects", projects.header(t))
    for p in content.PROJECTS:
        write(theme, p["slug"], projects.row(t, p))
    write(theme, "stack", stack.build(t))


def fetch_stats():
    """LeetCode stats, or None (with a message) when LeetCode is unreachable."""
    try:
        return leetcode_api.fetch(content.LEETCODE_USER)
    except Exception as e:
        print(f"LeetCode fetch failed, keeping existing cards: {e}")
        return None


def build_leetcode(data):
    """The LeetCode card for every theme."""
    today = dt.datetime.now(dt.timezone.utc).date()
    for theme, t in THEMES.items():
        write(theme, "leetcode", leetcode.build(t, data, today))
    print(f"LeetCode: {data['solved']['All']} solved")


def main():
    """Build the static blocks, then the LeetCode card if stats arrived."""
    for theme, t in THEMES.items():
        build_static(theme, t)
    data = fetch_stats()
    if data:
        build_leetcode(data)


if __name__ == "__main__":
    main()
