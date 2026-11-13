"""`cat stack.txt`: one labelled line per skills group."""
from .. import content
from ..fonts import REGULAR
from ..svg import EDGE, SIZE, CLOSE, animated, document, prompt, text

COMMAND_Y, FIRST_ROW, LINE = 100, 146, 36


def height():
    """Image height for the number of groups in content.STACK."""
    return 44 + 56 + LINE * len(content.STACK) + 34


def label():
    """The accessible description."""
    return "simon@cao:~$ cat stack.txt. " + " ".join(f"{k}: {v}." for k, v in content.STACK)


def rows(t):
    """Each group name in the faint colour, its items aligned after it."""
    value_x = EDGE + REGULAR.width(max((k for k, _ in content.STACK), key=len) + "  ", SIZE)
    parts = []
    for i, (group, items) in enumerate(content.STACK):
        y = FIRST_ROW + i * LINE
        parts += [text(REGULAR, group, SIZE, EDGE, y, t["faint"]), text(REGULAR, items, SIZE, value_x, y, t["ink"])]
    return parts


def build(t):
    """The complete stack SVG."""
    command, _ = prompt(t, EDGE, COMMAND_Y, SIZE, "cat stack.txt")
    return document(animated(height(), label()) + [command] + rows(t) + [CLOSE])
