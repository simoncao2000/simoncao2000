"""Projects as `ls -l ~/projects` output.

One image for the command line, then one image per project so each row can
link to its project from the README.
"""
from .. import content
from ..fonts import BOLD, REGULAR, wrap
from ..svg import EDGE, SIZE, WIDTH, CLOSE, document, prompt, static, text

HEADER_HEIGHT = 84
FIRST_LINE, LINE_GAP, BODY_LINE = 34, 36, 34
RIGHT_MARGIN = 48
PERMISSIONS = "drwxr-xr-x"


def header(t):
    """`ls -l ~/projects` and its `total N` line."""
    count = len(content.PROJECTS)
    line, _ = prompt(t, EDGE, FIRST_LINE, SIZE, "ls -l ~/projects")
    return document(static(HEADER_HEIGHT, f"simon@cao:~$ ls -l ~/projects, total {count}") + [
        line, text(REGULAR, f"total {count}", SIZE, EDGE, 72, t["faint"]), CLOSE])


def name_column():
    """Where project names (and the text under them) start."""
    return EDGE + REGULAR.width(f"{PERMISSIONS}  May 2026  ", SIZE)


def row_label(p):
    """The accessible description of one project row."""
    return f'{p["dir"]}, {p["date"]}: {p["body"]} Built with {p["stack"].replace(" · ", ", ")}.'


def link_arrow(t, x):
    """The ↗ after a project name, drawn as a stroke."""
    return (f'<path d="M{x} 32L{x+12} 20M{x+3} 20H{x+12}V29" fill="none" stroke="{t["accent"]}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')


def meta_line(t, p, x):
    """Permissions, date, `name/` and its arrow, as `ls -l` prints them."""
    name = p["dir"] + "/"
    return [text(REGULAR, PERMISSIONS, SIZE, EDGE, FIRST_LINE, t["faint"]),
            text(REGULAR, p["date"], SIZE, EDGE + REGULAR.width(PERMISSIONS + "  ", SIZE), FIRST_LINE, t["muted"]),
            text(BOLD, name, SIZE, x, FIRST_LINE, t["accent"]),
            link_arrow(t, x + BOLD.width(name, SIZE) + 14)]


def body_lines(t, lines, x):
    """The wrapped description, then the `# stack` comment below it."""
    y = FIRST_LINE + LINE_GAP
    parts = []
    for line in lines:
        parts.append(text(REGULAR, line, SIZE, x, y, t["ink"]))
        y += BODY_LINE
    return parts, y


def row(t, p):
    """One project as a complete SVG; height grows with the description."""
    x = name_column()
    lines = wrap(REGULAR, p["body"], SIZE, WIDTH - RIGHT_MARGIN - x)
    height = 52 + BODY_LINE * len(lines) + 40
    body, stack_y = body_lines(t, lines, x)
    return document(static(height, row_label(p)) + meta_line(t, p, x) + body + [
        text(REGULAR, "# " + p["stack"], SIZE, x, stack_y, t["faint"]), CLOSE])
