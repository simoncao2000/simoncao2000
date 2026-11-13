"""Shared SVG building blocks: documents, text, timing and the shell prompt."""
from .fonts import MEDIUM, REGULAR

WIDTH = 1280  # every image; the README shows them at 100% width
EDGE = 2      # left edge of content: flush with the README text, cells clear of the border
SIZE = 22     # body text size on every image
TOP = 66      # animated blocks lay out from y≈100; their view starts here

# Animation classes. Each animates *from* hidden with `backwards` fill, so
# anything that can't run CSS shows the finished frame.
#   .o  output: appears instantly, as a terminal prints
#   .k  a typed command: revealed one character per step
#   .c  the cursor: blinks
#   .h  one heatmap column: fades in
#   .a  a ring segment (pathLength=100): draws from nothing to its length
#   .f  one in-between frame of a counting number: hidden except while its
#       own animation runs, so with no animation only the final value shows
STYLE = """<style>
  .o{animation:show .01s backwards}
  .k{animation:type .45s steps(14,end) backwards}
  .c{animation:blink 1.1s steps(1,end) infinite}
  .h{animation:show .3s cubic-bezier(.23,1,.32,1) backwards}
  .a{animation:draw .9s cubic-bezier(.23,1,.32,1) backwards}
  .f{opacity:0;animation-name:flash;animation-timing-function:steps(1,end)}
  @keyframes show{from{opacity:0}}
  @keyframes type{from{clip-path:inset(-20% 100% -20% 0)}to{clip-path:inset(-20% 0 -20% 0)}}
  @keyframes blink{50%{opacity:0}}
  @keyframes draw{from{stroke-dasharray:0 100}}
  @keyframes flash{from,to{opacity:1}}
  @media (prefers-reduced-motion:reduce){.o,.k,.c,.h,.a,.f{animation:none}}
</style>"""

CLOSE = "</svg>"


def title(label):
    """The accessible description every image carries."""
    return f"<title id=\"t\">{label}</title>"


def animated(height, label):
    """Opening tags for a block that uses STYLE, cropped to start at TOP."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {TOP} {WIDTH} {height - TOP}" '
        f'width="{WIDTH}" height="{height - TOP}" '
        f'role="img" aria-labelledby="t">',
        title(label),
        STYLE,
    ]


def static(height, label):
    """Opening tags for a block with no animation."""
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" '
            f'height="{height}" role="img" aria-labelledby="t">',
            title(label)]


def document(parts):
    """Join a block's parts into the final SVG text."""
    return "\n".join(parts)


def text(face, s, size, x, y, fill):
    """`s` outlined in `fill`, baseline at (x, y); empty for empty text."""
    if not s:
        return ""
    return f'<path fill="{fill}" d="{face.outline(s, size, x, y)}"/>'


def cell(x, y, size, radius, fill):
    """One heatmap square."""
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{radius}" fill="{fill}"/>'


def appear_at(ms, body):
    """`body`, appearing instantly `ms` milliseconds after load."""
    return f'<g class="o" style="animation-delay:{ms}ms">{body}</g>'


def flash(ms, duration, body):
    """`body`, visible only from `ms` for `duration` ms (one counting frame)."""
    return f'<g class="f" style="animation-delay:{ms}ms;animation-duration:{duration}ms">{body}</g>'


def typed(body, ms, chars):
    """`body` typed out one of `chars` characters per step from `ms`."""
    return (f'<g class="k" style="animation-delay:{ms}ms;animation-timing-function:steps({chars},end)">'
            f"{body}</g>")


def prompt_prefix(t, x, y, size):
    """`simon@cao:~$ ` at (x, y). Returns (svg, x where it ends)."""
    parts, cx = [], x
    for s, colour in (("simon@cao", t["prompt"]), (":", t["ink"]), ("~", t["path"]), ("$ ", t["ink"])):
        parts.append(text(MEDIUM, s, size, cx, y, colour))
        cx += MEDIUM.width(s, size)
    return "".join(parts), cx


def prompt(t, x, y, size, command, delay=None):
    """A full prompt line. With `delay` (ms) the prefix appears 60 ms before
    the command starts typing. Returns (svg, x where the line ends)."""
    prefix, cx = prompt_prefix(t, x, y, size)
    command_svg = text(REGULAR, command, size, cx, y, t["ink"])
    end = cx + REGULAR.width(command, size)
    if not delay:
        return prefix + command_svg, end
    return (appear_at(max(delay - 60, 0), prefix)
            + typed(command_svg, delay, max(len(command), 1))), end


def cursor(t, x, baseline):
    """The blinking block cursor, sitting on `baseline`."""
    return f'<rect class="c" x="{x + 2}" y="{baseline - 21}" width="13" height="27" fill="{t["ink"]}"/>'
