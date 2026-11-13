"""The top block: `whoami` → name heatmap → tagline → `cat profile.txt` → cursor.

The whole sequence plays once on load in about 2.1 s.
"""
from .. import content
from ..fonts import REGULAR
from ..svg import EDGE, SIZE, animated, appear_at, cell, cursor, document, prompt, text, CLOSE

HEIGHT = 690
LINE = 36          # profile row spacing

# Name heatmap geometry: 53 columns x 24 px fill the full width.
GRID_TOP, PITCH, CELL = 136, 24, 20
COLUMNS = 53

# Baselines.
WHOAMI_Y, TAGLINE_Y, CAT_Y, PROFILE_Y = 104, 356, 428, 472

# When each step starts (ms after load).
WHOAMI_AT, NAME_AT, COLUMN_STEP, TAGLINE_AT, CAT_AT, PROFILE_AT, CURSOR_AT = 150, 550, 12, 1250, 1400, 1950, 2050

# 5x7 pixel letters ("#" lit). With 2-column gaps between letters and a
# 3-column space, "SIMON CAO" fills exactly 53 columns: one year of weeks.
GLYPHS = {
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}
NOISE = 0.04  # share of background cells lit faintly, so it reads as real activity
SEED = 2000


def letter_gap(name, i):
    """Two empty columns after letter `i`, none next to a space or at the end."""
    last = i == len(name) - 1
    return "" if last or name[i] == " " or name[i + 1] == " " else ".."


def bitmap(name, cols=COLUMNS):
    """`name` as 7 rows of "#"/".", centred in `cols` columns."""
    rows = [""] * 7
    for i, ch in enumerate(name.upper()):
        for r in range(7):
            rows[r] += GLYPHS[ch][r] + letter_gap(name, i)
    pad = (cols - len(rows[0])) // 2
    return [("." * pad + r).ljust(cols, ".") for r in rows]


def random_stream(seed):
    """Deterministic numbers in [0, 1). A fixed seed gives the same shading
    every build, so the hero never changes unless the design does."""
    while True:
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        yield seed / 0x7FFFFFFF


def cell_level(lit, roll):
    """Heat level for one cell: letters get 3–4, background mostly 0."""
    if lit:
        return 3 + int(roll * 2)
    return 1 if roll < NOISE else 0


def name_heatmap(t):
    """The name as a contribution heatmap; columns fade in left to right."""
    bits, rolls = bitmap(content.NAME), random_stream(SEED)
    columns = []
    for c in range(COLUMNS):
        cells = [cell(EDGE + c * PITCH, GRID_TOP + r * PITCH, CELL, 3,
                      t["heat"][cell_level(bits[r][c] == "#", next(rolls))])
                 for r in range(7)]
        columns.append(f'<g class="h" style="animation-delay:{NAME_AT + c * COLUMN_STEP}ms">{"".join(cells)}</g>')
    return "".join(columns)


def profile_row(t, key, value, y, value_x, dot=None):
    """One `key  value` line; `dot` puts a coloured dot before the value."""
    parts = [text(REGULAR, key, SIZE, EDGE, y, t["faint"])]
    if dot:
        parts.append(f'<circle cx="{value_x + 7}" cy="{y - 8}" r="6" fill="{dot}"/>')
        value_x += 26
    parts.append(text(REGULAR, value, SIZE, value_x, y, t["ink"]))
    return "".join(parts)


def profile(t):
    """Every profile row, then the status row with its green dot."""
    keys = [k for k, _ in content.PROFILE] + [content.STATUS[0]]
    value_x = EDGE + REGULAR.width(max(keys, key=len) + "  ", SIZE)
    rows = [profile_row(t, k, v, PROFILE_Y + i * LINE, value_x) for i, (k, v) in enumerate(content.PROFILE)]
    status_y = PROFILE_Y + len(content.PROFILE) * LINE
    rows.append(profile_row(t, *content.STATUS, status_y, value_x, dot=t["ok"]))
    return "".join(rows)


def idle_prompt(t):
    """The last, empty prompt with the blinking cursor."""
    y = PROFILE_Y + (len(content.PROFILE) + 1) * LINE + 6
    line, end = prompt(t, EDGE, y, SIZE, "")
    return line + cursor(t, end, y)


def build(t):
    """The complete hero SVG."""
    return document(animated(HEIGHT, content.HERO_ALT) + [
        prompt(t, EDGE, WHOAMI_Y, SIZE, "whoami", delay=WHOAMI_AT)[0],
        name_heatmap(t),
        appear_at(TAGLINE_AT, text(REGULAR, content.TAGLINE, SIZE, EDGE, TAGLINE_Y, t["muted"])),
        prompt(t, EDGE, CAT_Y, SIZE, "cat profile.txt", delay=CAT_AT)[0],
        appear_at(PROFILE_AT, profile(t)),
        appear_at(CURSOR_AT, idle_prompt(t)),
        CLOSE,
    ])
