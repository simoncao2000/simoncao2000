"""JetBrains Mono: download, measure, and outline text as SVG path data.

Text is drawn as outlines rather than <text>, because SVGs shown through an
<img> can't load web fonts. HarfBuzz shapes the text; fontTools supplies the
outlines from a static instance at the same weight, so widths and glyphs
always agree.
"""
import re
import urllib.request
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
FONT_PATH = Path(__file__).resolve().parent / ".fonts" / "JetBrainsMono.ttf"  # git-ignored


def ensure_font():
    """Return FONT_PATH, downloading the font on first use."""
    if not FONT_PATH.exists():
        FONT_PATH.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    return FONT_PATH


def compact(d):
    """Round path coordinates to 0.1 and drop spaces before minus signs."""
    d = re.sub(r"-?\d+\.\d+|-?\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), d)
    return re.sub(r" (?=-)", "", d)


class Face:
    """One weight of the variable font."""

    def __init__(self, path, weight):
        """Load `path` with its `wght` axis pinned to `weight`."""
        coords = {"wght": weight}
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        self.hbfont.set_variations(coords)
        self.upem = self.hbfont.face.upem
        static = instancer.instantiateVariableFont(TTFont(str(path)), coords)
        self.glyphset = static.getGlyphSet()
        self.order = static.getGlyphOrder()

    def shape(self, text):
        """HarfBuzz (glyph infos, positions) for `text`, ligatures off so
        `->` and `!=` stay as typed, the way a terminal shows them."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"calt": False, "liga": False})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size):
        """Advance width of `text` at `size` px."""
        if not text:
            return 0
        return sum(p.x_advance for p in self.shape(text)[1]) * size / self.upem

    def outline(self, text, size, x, y):
        """SVG path data for `text` with its baseline starting at (x, y).
        Font units are scaled to `size` and flipped (fonts are y-up)."""
        infos, pos = self.shape(text)
        s = size / self.upem
        pen = SVGPathPen(self.glyphset)
        cx = 0
        for info, p in zip(infos, pos):
            tp = TransformPen(pen, (s, 0, 0, -s, x + (cx + p.x_offset) * s, y - p.y_offset * s))
            self.glyphset[self.order[info.codepoint]].draw(tp)
            cx += p.x_advance
        return compact(pen.getCommands())


def wrap(face, text, size, max_width):
    """Greedy word wrap into lines no wider than `max_width`. A word longer
    than a line gets a line to itself rather than being broken."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if face.width(trial, size) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


_font = ensure_font()
REGULAR = Face(_font, 400)  # body text
MEDIUM = Face(_font, 600)   # the prompt
BOLD = Face(_font, 760)     # project names, big numbers
