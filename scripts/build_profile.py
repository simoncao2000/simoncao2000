"""Build the profile README artwork (terminal theme, light + dark).

Every string is outlined to SVG paths in JetBrains Mono, so the images look
the same on every device. LeetCode stats are fetched live; if LeetCode is
unreachable, the existing LeetCode cards are left untouched.

    pip install fonttools uharfbuzz
    python scripts/build_profile.py
"""
import datetime as dt
import json
import re
import urllib.request
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONT_DIR = Path(__file__).resolve().parent / ".fonts"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
LEETCODE_USER = "000433430"
FALLBACK_NAME = "Simon Cao"


# --------------------------------------------------------------------- type
def font_file():
    FONT_DIR.mkdir(exist_ok=True)
    path = FONT_DIR / "JetBrainsMono.ttf"
    if not path.exists():
        urllib.request.urlretrieve(FONT_URL, path)
    return path


class Face:
    def __init__(self, path, weight):
        coords = {"wght": weight}
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        self.hbfont.set_variations(coords)
        self.upem = self.hbfont.face.upem
        static = instancer.instantiateVariableFont(TTFont(str(path)), coords)
        self.glyphset = static.getGlyphSet()
        self.order = static.getGlyphOrder()

    def _shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"calt": False, "liga": False})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size):
        if not text:
            return 0
        return sum(p.x_advance for p in self._shape(text)[1]) * size / self.upem

    def path(self, text, size, x, y):
        infos, pos = self._shape(text)
        s = size / self.upem
        pen = SVGPathPen(self.glyphset)
        cx = 0
        for info, p in zip(infos, pos):
            tp = TransformPen(pen, (s, 0, 0, -s, x + (cx + p.x_offset) * s, y - p.y_offset * s))
            self.glyphset[self.order[info.codepoint]].draw(tp)
            cx += p.x_advance
        d = pen.getCommands()
        d = re.sub(r"-?\d+\.\d+|-?\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), d)
        return re.sub(r" (?=-)", "", d)


FONT = font_file()
mono = Face(FONT, 400)
mono_md = Face(FONT, 600)
mono_bd = Face(FONT, 760)


def text(face, s, size, x, y, fill, extra=""):
    if not s:
        return ""
    return f'<path{extra} fill="{fill}" d="{face.path(s, size, x, y)}"/>'


def wrap(face, s, size, maxw):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if face.width(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


# ------------------------------------------------------------------ palette
# One step off GitHub's own colours so the art sits naturally on the page.
T = {
    "light": dict(bg="#F6F8FA", bar="#EAEEF2", border="#D1D9E0", ink="#1F2328", muted="#59636E",
                  faint="#818B98", prompt="#1A7F37", path="#0969DA", dot="#D1D9E0",
                  easy="#1A7F37", medium="#9A6700", hard="#CF222E",
                  heat=["#EFF2F5", "#ACEEBB", "#4AC26B", "#2DA44E", "#116329"]),
    "dark": dict(bg="#0D1117", bar="#151B23", border="#30363D", ink="#E6EDF3", muted="#9198A1",
                 faint="#6E7681", prompt="#3FB950", path="#58A6FF", dot="#3D444D",
                 easy="#3FB950", medium="#D29922", hard="#F85149",
                 heat=["#151B23", "#033A16", "#196C2E", "#2EA043", "#56D364"]),
}

STYLE = """<style>
  .o{animation:show .01s backwards}
  .k{animation:type .45s steps(14,end) backwards}
  .c{animation:blink 1.1s steps(1,end) infinite}
  .h{animation:show .3s cubic-bezier(.23,1,.32,1) backwards}
  @keyframes show{from{opacity:0}}
  @keyframes type{from{clip-path:inset(-20% 100% -20% 0)}to{clip-path:inset(-20% 0 -20% 0)}}
  @keyframes blink{50%{opacity:0}}
  @media (prefers-reduced-motion:reduce){.o,.k,.c,.h{animation:none}}
</style>"""


def window(w, h, t, title, label):
    """Terminal window chrome: rounded frame, title bar, three neutral dots."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">',
        f"<title id=\"t\">{label}</title>",
        STYLE,
        f'<clipPath id="f"><rect width="{w}" height="{h}" rx="14"/></clipPath>',
        f'<g clip-path="url(#f)"><rect width="{w}" height="{h}" fill="{t["bg"]}"/>'
        f'<rect width="{w}" height="44" fill="{t["bar"]}"/>'
        f'<path d="M0 44H{w}" stroke="{t["border"]}" stroke-width="1.5"/></g>',
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="14" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>',
        "".join(f'<circle cx="{26 + i*20}" cy="22" r="6" fill="{t["dot"]}"/>' for i in range(3)),
        text(mono, title, 15, (w - mono.width(title, 15)) / 2, 27, t["faint"]),
    ]


def prompt(t, x, y, size, command, delay=None):
    """`simon@cao:~$ command` — the command types out when a delay is given."""
    parts, cx = [], x
    for s, c in (("simon@cao", t["prompt"]), (":", t["ink"]), ("~", t["path"]), ("$ ", t["ink"])):
        parts.append(text(mono_md, s, size, cx, y, c))
        cx += mono_md.width(s, size)
    cmd = text(mono, command, size, cx, y, t["ink"])
    if delay is not None:
        n = max(len(command), 1)
        cmd = (f'<g class="k" style="animation-delay:{delay}ms;animation-timing-function:steps({n},end)">'
               f"{cmd}</g>")
    pre = f'<g class="o" style="animation-delay:{max((delay or 0) - 60, 0)}ms">' + "".join(parts) + "</g>" if delay else "".join(parts)
    return pre + cmd, cx + mono.width(command, size)


def later(ms, body):
    return f'<g class="o" style="animation-delay:{ms}ms">{body}</g>'


# --------------------------------------------------------------------- hero
# 5x7 pixel letters; "SIMON CAO" spans 52 columns, one short of a
# contribution graph's 53 weeks, so the name sits on a real-sized grid.
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


def name_bitmap(name, cols=53):
    rows = [""] * 7
    for i, ch in enumerate(name.upper()):
        g = GLYPHS[ch]
        for r in range(7):
            rows[r] += g[r] + (".." if i < len(name) - 1 and ch != " " and name[i + 1] != " " else "")
    width = len(rows[0])
    pad = (cols - width) // 2
    return [("." * pad + r).ljust(cols, ".") for r in rows]


def lcg(seed):
    while True:
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        yield seed / 0x7FFFFFFF


def name_heatmap(t, x, y, pitch, cell, start_ms):
    bits = name_bitmap("Simon Cao")
    rnd = lcg(2000)
    cols = []
    for c in range(len(bits[0])):
        rects = []
        for r in range(7):
            v = next(rnd)
            lvl = (3 + int(v * 2)) if bits[r][c] == "#" else (1 if v < 0.04 else 0)
            rects.append(f'<rect x="{x + c*pitch}" y="{y + r*pitch}" width="{cell}" height="{cell}" rx="3" '
                         f'fill="{t["heat"][lvl]}"/>')
        cols.append(f'<g class="h" style="animation-delay:{start_ms + c*16}ms">{"".join(rects)}</g>')
    return "".join(cols)


def hero(theme):
    t = T[theme]
    W, H = 1280, 640
    s = window(W, H, t, "simon@cao: ~",
               "Terminal. whoami prints the name Simon Cao drawn as a contribution heatmap, "
               "then: Software Engineer, full-stack web. "
               "Focus: full-stack web development. Stack: React, TypeScript, Next.js, Python. "
               "Education: B.S. Computer Science, UW–Stout, 2026. Status: open to full-time roles.")
    x, sz = 48, 24
    p, _ = prompt(t, x, 104, sz, "whoami", delay=200)
    s.append(p)
    pitch, cell = 22, 18
    gx = (W - (53 * pitch - (pitch - cell))) / 2
    s.append(name_heatmap(t, gx, 140, pitch, cell, 700))
    s.append(later(1600, text(mono, "Software Engineer · full-stack web", sz, x, 342, t["muted"])))
    p, _ = prompt(t, x, 414, sz, "cat profile.txt", delay=1800)
    s.append(p)
    rows = [("focus", "Full-stack web development", None),
            ("stack", "React, TypeScript, Next.js, Python", None),
            ("education", "B.S. Computer Science, UW–Stout '26", None),
            ("status", "Open to full-time roles", t["prompt"])]
    out = []
    for i, (k, v, dot) in enumerate(rows):
        y = 458 + i * 36
        out.append(text(mono, k, sz, x, y, t["faint"]))
        vx = x + mono.width("education  ", sz)
        if dot:
            out.append(f'<circle cx="{vx + 7}" cy="{y - 8}" r="6" fill="{dot}"/>')
            vx += 26
        out.append(text(mono, v, sz, vx, y, t["ink"]))
    s.append(later(2500, "".join(out)))
    p, cx = prompt(t, x, 606, sz, "")
    s.append(later(2700, p + f'<rect class="c" x="{cx + 2}" y="{606 - 21}" width="13" height="27" fill="{t["ink"]}"/>'))
    s.append("</svg>")
    return "\n".join(s)


# ----------------------------------------------------------------- projects
PROJECTS = [
    dict(slug="manifest-editor", dir="manifest-editor",
         body="Browser editor for IIIF manifests and 3D scenes, built for stakeholders in London.",
         stack="react · typescript · indexeddb"),
    dict(slug="kintsugi", dir="kintsugi3d-builder",
         body="Research software for 3D texture reconstruction at UW–Stout.",
         stack="java · javafx · maven"),
    dict(slug="church-site", dir="gishen-debre-kerbe",
         body="Website and content management system for a church community.",
         stack="next.js · typescript · sanity"),
    dict(slug="unimentor", dir="unimentor",
         body="iOS app that connects university students with peer tutors.",
         stack="swift · swiftui · firebase"),
]


def card(p, theme):
    t = T[theme]
    W, H = 600, 300
    label = f'{p["dir"]}: {p["body"]} Built with {p["stack"].replace(" · ", ", ")}.'
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">',
         f'<title id="t">{label}</title>',
         f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>']
    # "~/dir/" heading, with the arrow that says "this opens"
    s.append(text(mono_md, "~/", 26, 40, 74, t["faint"]))
    s.append(text(mono_bd, p["dir"] + "/", 26, 40 + mono_md.width("~/", 26), 74, t["path"]))
    s.append(f'<path d="M{W-56} {64}L{W-42} {50}M{W-52} {50}H{W-42}V{60}" fill="none" stroke="{t["faint"]}" '
             f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    y = 124
    for line in wrap(mono, p["body"], 21, W - 80):
        s.append(text(mono, line, 21, 40, y, t["muted"]))
        y += 32
    s.append(f'<path d="M40 {H-74}H{W-40}" stroke="{t["border"]}" stroke-width="1.5"/>')
    s.append(text(mono, p["stack"], 19, 40, H - 38, t["faint"]))
    s.append("</svg>")
    return "\n".join(s)


# ------------------------------------------------------------------ buttons
def button(label, kind, theme):
    t = T[theme]
    size, h = 21, 56
    w = round(26 + 22 + 12 + mono_md.width(label, size) + 28)
    icon = {
        "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/>',
        "out": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/>',
    }[kind]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">',
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>',
        f'<g transform="translate(26 {h/2 - 11}) scale(.92)" fill="none" stroke="{t["prompt"]}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{icon}</g>',
        text(mono_md, label, size, 60, h / 2 + 7.5, t["ink"]),
        "</svg>"])


# ----------------------------------------------------------------- leetcode
def fetch_leetcode(user):
    q = ("query($u:String!){matchedUser(username:$u){profile{realName} "
         "submitStatsGlobal{acSubmissionNum{difficulty count}} userCalendar{submissionCalendar}} "
         "allQuestionsCount{difficulty count}}")
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=json.dumps({"query": q, "variables": {"u": user}}).encode(),
        headers={"content-type": "application/json", "referer": "https://leetcode.com",
                 "user-agent": "Mozilla/5.0 (profile-readme-builder)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)["data"]
    m = data["matchedUser"]
    solved = {d["difficulty"]: d["count"] for d in m["submitStatsGlobal"]["acSubmissionNum"]}
    total = {d["difficulty"]: d["count"] for d in data["allQuestionsCount"]}
    cal = {dt.datetime.fromtimestamp(int(k), dt.timezone.utc).date(): v
           for k, v in json.loads(m["userCalendar"]["submissionCalendar"]).items()}
    return dict(name=(m["profile"].get("realName") or FALLBACK_NAME).strip(),
                solved=solved, total=total, cal=cal)


def level(n):
    return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 10 else 4


def leetcode(data, theme, today):
    t = T[theme]
    W, H = 1280, 380
    yr = sum(v for d, v in data["cal"].items() if (today - d).days < 365)
    label = (f'LeetCode stats for {data["name"]}: {data["solved"]["All"]} problems solved '
             f'({data["solved"]["Easy"]} easy, {data["solved"]["Medium"]} medium, {data["solved"]["Hard"]} hard). '
             f"{yr} submissions in the past year.")
    s = window(W, H, t, "simon@cao: ~/leetcode", label)
    x, sz = 48, 22
    p, _ = prompt(t, x, 100, sz, "leetcode stats --year")
    s.append(p)

    # left column: name, total, per-difficulty
    s.append(text(mono_bd, data["name"], 34, x, 162, t["ink"]))
    total = str(data["solved"]["All"])
    s.append(text(mono_bd, total, 48, x, 232, t["ink"]))
    s.append(text(mono, "solved", sz, x + mono_bd.width(total, 48) + 14, 232, t["muted"]))
    for i, d in enumerate(("Easy", "Medium", "Hard")):
        y = 278 + i * 32
        s.append(text(mono_md, d.lower(), 20, x, y, t[d.lower()]))
        s.append(text(mono, f'{data["solved"][d]:>4} / {data["total"][d]}', 20, x + mono.width("medium ", 20), y, t["muted"]))

    # right column: 53-week heatmap ending today, weeks start on Sunday
    gx, gy, cell, gap = 432, 168, 12, 3
    pitch = cell + gap
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
    cells, months, last_col = [], [], -9
    day, col = start, 0
    while day <= today:
        row = (day.weekday() + 1) % 7
        if day.day <= 7 and row == 0 and col - last_col >= 3:
            months.append((col, day.strftime("%b")))
            last_col = col
        n = data["cal"].get(day, 0)
        cells.append(f'<rect x="{gx + col*pitch}" y="{gy + row*pitch}" width="{cell}" height="{cell}" rx="2.5" '
                     f'fill="{t["heat"][level(n)]}"/>')
        day += dt.timedelta(days=1)
        if row == 6:
            col += 1
    for c, m in months:
        s.append(text(mono, m, 15, gx + c * pitch, gy - 12, t["faint"]))
    s += cells
    # legend
    lx = gx + 53 * pitch - 5 * pitch - mono.width("less ", 15) - mono.width(" more", 15)
    ly = gy + 7 * pitch + 30
    s.append(text(mono, f"{yr} submissions in the past year", 17, gx, ly + 12, t["muted"]))
    s.append(text(mono, "less", 15, lx, ly + 11, t["faint"]))
    lx += mono.width("less ", 15)
    for i in range(5):
        s.append(f'<rect x="{lx + i*pitch}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" fill="{t["heat"][i]}"/>')
    s.append(text(mono, "more", 15, lx + 5 * pitch + 4, ly + 11, t["faint"]))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------- main
def main():
    OUT.mkdir(exist_ok=True)
    for th in T:
        (OUT / f"hero-{th}.svg").write_text(hero(th), encoding="utf-8")
        for p in PROJECTS:
            (OUT / f"{p['slug']}-{th}.svg").write_text(card(p, th), encoding="utf-8")
        (OUT / f"email-{th}.svg").write_text(button("Email", "mail", th), encoding="utf-8")
        (OUT / f"linkedin-{th}.svg").write_text(button("LinkedIn", "out", th), encoding="utf-8")
    try:
        data = fetch_leetcode(LEETCODE_USER)
    except Exception as e:  # keep the last good card when LeetCode is unreachable
        print(f"LeetCode fetch failed, keeping existing cards: {e}")
        return
    today = dt.datetime.now(dt.timezone.utc).date()
    for th in T:
        (OUT / f"leetcode-{th}.svg").write_text(leetcode(data, th, today), encoding="utf-8")
    print(f"LeetCode: {data['name']}, {data['solved']['All']} solved")


if __name__ == "__main__":
    main()
