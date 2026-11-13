"""LeetCode: a solved gauge and difficulty boxes on the left, a 53-week
heatmap on the right.

The grid always covers whole weeks (52 past weeks plus the current one,
through Saturday), so the image only changes when the stats change or a new
week begins. That keeps the hourly CI job from committing every day.
"""
import datetime as dt

from ..fonts import BOLD, MEDIUM, REGULAR
from ..svg import EDGE, SIZE, WIDTH, CLOSE, animated, cell, document, prompt, text

HEIGHT = 340
WEEKS = 53
CELL, GAP = 12, 3
PITCH = CELL + GAP
GRID_X = WIDTH - EDGE - (WEEKS * PITCH - GAP)  # flush right
GRID_Y = 168
SMALL, TINY = 20, 15
DIFFICULTIES = ("Easy", "Medium", "Hard")
SHORT = {"Easy": "Easy", "Medium": "Med.", "Hard": "Hard"}  # as LeetCode labels them

# Gauge, after LeetCode's profile: one track per difficulty, sized by how many
# problems LeetCode has at that level, filled by how many are solved.
RING_R, RING_W, RING_GAP = 66, 8, 3      # radius, stroke, gap between tracks (of 100)
RING_X, RING_Y = EDGE + RING_R + RING_W // 2, 222
BOX_X = RING_X + RING_R + RING_W + 40    # difficulty boxes start right of the ring
BOX_W, BOX_H, BOX_GAP, BOX_PAD = 200, 44, 10, 16

# When each step starts (ms after load).
COMMAND_AT, RING_AT, GRID_AT, COLUMN_STEP = 150, 650, 650, 10


def level(n):
    """Heat level 0–4 for `n` submissions in a day: 0, 1–2, 3–5, 6–10, 11+."""
    return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 10 else 4


def week_range(today):
    """(first Sunday, last Saturday) of the 53 weeks ending this week."""
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + (WEEKS - 1) * 7)
    return start, start + dt.timedelta(days=WEEKS * 7 - 1)


def submissions(cal, start, end):
    """Total submissions between `start` and `end`, inclusive."""
    return sum(v for d, v in cal.items() if start <= d <= end)


def label(data, total):
    """The accessible description."""
    s, q = data["solved"], data["total"]
    return (f'LeetCode stats: {s["All"]} of {q["All"]} problems solved '
            f'({s["Easy"]} easy, {s["Medium"]} medium, {s["Hard"]} hard). '
            f"{total} submissions in the past 53 weeks.")


def tracks(totals):
    """[(difficulty, start, length)] round the ring in units of 100, each
    track sized by that difficulty's share of all problems, gaps between."""
    room = 100 - RING_GAP * len(DIFFICULTIES)
    out, start = [], RING_GAP / 2
    for d in DIFFICULTIES:
        length = room * totals[d] / totals["All"]
        out.append((d, start, length))
        start += length + RING_GAP
    return out


def arc(colour, start, length, animate=False):
    """A ring arc `length` units long, `start` units clockwise from 12 o'clock
    (100 units = full circle). Animated arcs draw in from their start."""
    motion = f'class="a" style="animation-delay:{RING_AT}ms" ' if animate else ""
    return (f'<circle {motion}cx="{RING_X}" cy="{RING_Y}" r="{RING_R}" pathLength="100" fill="none" '
            f'stroke="{colour}" stroke-width="{RING_W}" stroke-linecap="round" '
            f'stroke-dasharray="{length:.2f} 100" transform="rotate({start * 3.6 - 90:.2f} {RING_X} {RING_Y})"/>')


def gauge(t, data):
    """Faint tracks, then the solved part of each one in full colour."""
    faint, solid = [], []
    for d, start, length in tracks(data["total"]):
        fill, track = t["ring"][d]
        faint.append(arc(track, start, length))
        if data["solved"][d]:
            solid.append(arc(fill, start, length * data["solved"][d] / data["total"][d], animate=True))
    return faint + solid


def gauge_centre(t, data):
    """`36/4110` and "Solved", centred in the ring."""
    count = f'{data["solved"]["All"]}/{data["total"]["All"]}'
    return [text(BOLD, count, 22, RING_X - BOLD.width(count, 22) / 2, RING_Y + 3, t["ink"]),
            text(REGULAR, "Solved", TINY, RING_X - REGULAR.width("Solved", TINY) / 2, RING_Y + 28, t["muted"])]


def difficulty_box(t, d, solved, total, top):
    """One rounded box: the difficulty in its colour, `solved/total` on the right."""
    value = f"{solved}/{total}"
    baseline = top + BOX_H / 2 + 6
    return [f'<rect x="{BOX_X}" y="{top}" width="{BOX_W}" height="{BOX_H}" rx="8" fill="{t["panel"]}"/>',
            text(MEDIUM, SHORT[d], 18, BOX_X + BOX_PAD, baseline, t[d.lower()]),
            text(REGULAR, value, 18, BOX_X + BOX_W - BOX_PAD - REGULAR.width(value, 18), baseline, t["ink"])]


def difficulty_boxes(t, data):
    """Easy, Med. and Hard boxes stacked beside the ring, centred on it."""
    top = RING_Y - (3 * BOX_H + 2 * BOX_GAP) / 2
    parts = []
    for i, d in enumerate(DIFFICULTIES):
        parts += difficulty_box(t, d, data["solved"][d], data["total"][d], top + i * (BOX_H + BOX_GAP))
    return parts


def days(start, end):
    """Every day in the grid as (date, column, row); weeks start on Sunday."""
    day, col = start, 0
    while day <= end:
        row = (day.weekday() + 1) % 7
        yield day, col, row
        if row == 6:
            col += 1
        day += dt.timedelta(days=1)


def month_starts(start, end):
    """(column, "Mon") for each month's first full week, at least 3 apart."""
    marks, last = [], -9
    for day, col, row in days(start, end):
        if day.day <= 7 and row == 0 and col - last >= 3:
            marks.append((col, day.strftime("%b")))
            last = col
    return marks


def month_labels(t, start, end):
    """Month names above the grid."""
    return [text(REGULAR, m, TINY, GRID_X + c * PITCH, GRID_Y - 12, t["faint"]) for c, m in month_starts(start, end)]


def grid(t, cal, start, end):
    """One square per day, shaded by that day's submissions, grouped by week
    so the columns can sweep in left to right."""
    weeks = {}
    for day, col, row in days(start, end):
        weeks.setdefault(col, []).append(
            cell(GRID_X + col * PITCH, GRID_Y + row * PITCH, CELL, 2.5, t["heat"][level(cal.get(day, 0))]))
    return [f'<g class="h" style="animation-delay:{GRID_AT + col * COLUMN_STEP}ms">{"".join(cells)}</g>'
            for col, cells in weeks.items()]


def footer(t, total):
    """The submissions count under the grid and the less → more legend."""
    y = GRID_Y + 7 * PITCH + 30
    x = GRID_X + WEEKS * PITCH - 5 * PITCH - REGULAR.width("less ", TINY) - REGULAR.width(" more", TINY)
    parts = [text(REGULAR, f"{total} submissions in the past 53 weeks", 17, GRID_X, y + 12, t["muted"]),
             text(REGULAR, "less", TINY, x, y + 11, t["faint"])]
    x += REGULAR.width("less ", TINY)
    parts += [cell(x + i * PITCH, y, CELL, 2.5, t["heat"][i]) for i in range(5)]
    parts.append(text(REGULAR, "more", TINY, x + 5 * PITCH + 4, y + 11, t["faint"]))
    return parts


def build(t, data, today):
    """The complete LeetCode SVG for `data` (from leetcode_api.fetch)."""
    start, end = week_range(today)
    total = submissions(data["cal"], start, end)
    command, _ = prompt(t, EDGE, 100, SIZE, "leetcode stats --year", delay=COMMAND_AT)
    return document(animated(HEIGHT, label(data, total)) + [command]
                    + gauge(t, data) + gauge_centre(t, data) + difficulty_boxes(t, data)
                    + month_labels(t, start, end) + grid(t, data["cal"], start, end)
                    + footer(t, total) + [CLOSE])
