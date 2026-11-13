"""LeetCode: solved counts on the left, a 53-week heatmap on the right.

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
    s = data["solved"]
    return (f'LeetCode stats: {s["All"]} problems solved '
            f'({s["Easy"]} easy, {s["Medium"]} medium, {s["Hard"]} hard). '
            f"{total} submissions in the past 53 weeks.")


def solved_total(t, data):
    """The big solved number and the word "solved"."""
    total = str(data["solved"]["All"])
    return [text(BOLD, total, 48, EDGE, 196, t["ink"]),
            text(REGULAR, "solved", SIZE, EDGE + BOLD.width(total, 48) + 14, 196, t["muted"])]


def difficulty_rows(t, data):
    """`easy  28 / 975`, one line per difficulty, in its own colour."""
    parts = []
    for i, d in enumerate(DIFFICULTIES):
        y = 242 + i * 32
        parts += [text(MEDIUM, d.lower(), SMALL, EDGE, y, t[d.lower()]),
                  text(REGULAR, f'{data["solved"][d]:>4} / {data["total"][d]}', SMALL,
                       EDGE + REGULAR.width("medium ", SMALL), y, t["muted"])]
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
    """One square per day, shaded by that day's submissions."""
    return [cell(GRID_X + col * PITCH, GRID_Y + row * PITCH, CELL, 2.5, t["heat"][level(cal.get(day, 0))])
            for day, col, row in days(start, end)]


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
    command, _ = prompt(t, EDGE, 100, SIZE, "leetcode stats --year")
    return document(animated(HEIGHT, label(data, total)) + [command]
                    + solved_total(t, data) + difficulty_rows(t, data)
                    + month_labels(t, start, end) + grid(t, data["cal"], start, end)
                    + footer(t, total) + [CLOSE])
