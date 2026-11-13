"""Catppuccin colours (https://catppuccin.com/palette) mapped to drawing roles.

Mocha is used for GitHub's dark mode and Latte, its light flavour, for light
mode. The art is transparent, so every text colour is checked against
GitHub's own page background rather than Catppuccin's base.
"""

# GitHub's page background in each mode.
PAGE = {"light": "#FFFFFF", "dark": "#0D1117"}

# `empty` is the heatmap's level-0 cell: Latte crust on white, Mocha mantle on
# GitHub dark (Mocha crust is 1.01:1 against #0D1117 and disappears).
LATTE = dict(base="#EFF1F5", empty="#DCE0E8", text="#4C4F69", subtext0="#6C6F85", overlay2="#7C7F93",
             pink="#EA76CB", green="#40A02B", blue="#1E66F5", teal="#179299", yellow="#DF8E1D", red="#D20F39")
MOCHA = dict(base="#1E1E2E", empty="#181825", text="#CDD6F4", subtext0="#A6ADC8", overlay2="#9399B2",
             pink="#F5C2E7", green="#A6E3A1", blue="#89B4FA", teal="#94E2D5", yellow="#F9E2AF", red="#F38BA8")

TEXT_CONTRAST = 4.5     # WCAG AA for normal text
GRAPHIC_CONTRAST = 3.0  # WCAG AA for non-text marks (the status dot)
HEAT_STEPS = (0.35, 0.6, 0.8, 1.0)


def mix(a, b, k):
    """Blend hex colour `a` toward `b` by `k` (0 = a, 1 = b)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * k):02X}" for x, y in zip(ca, cb))


def luminance(h):
    """WCAG relative luminance of a hex colour (0 = black, 1 = white)."""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    """WCAG contrast ratio between two hex colours (1 up to 21)."""
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def legible(fg, page, ratio=TEXT_CONTRAST):
    """Nudge `fg` toward black or white, keeping its hue, until it reaches
    `ratio` against `page`. Colours that already pass come back unchanged."""
    target = "#000000" if luminance(page) > 0.5 else "#FFFFFF"
    k = 0.0
    while contrast(mix(fg, target, k), page) < ratio and k < 1:
        k += 0.01
    return mix(fg, target, k)


def heat_ramp(c):
    """Five heatmap shades, index = activity level 0–4, ending at pink."""
    return [c["empty"]] + [mix(c["base"], c["pink"], k) for k in HEAT_STEPS]


def text_roles(c):
    """Which Catppuccin colour plays which text role."""
    return dict(ink=c["text"], muted=c["subtext0"], faint=c["overlay2"],
                prompt=c["pink"], path=c["blue"], accent=c["blue"],
                easy=c["teal"], medium=c["yellow"], hard=c["red"])


def theme(c, page):
    """All roles for one flavour on one page: legible text colours, the heat
    ramp (graphics keep the palette's own shades), and the green status dot,
    which means "available" whatever the accent."""
    roles = {k: legible(v, page) for k, v in text_roles(c).items()}
    roles["heat"] = heat_ramp(c)
    roles["ok"] = legible(c["green"], page, GRAPHIC_CONTRAST)
    return roles


THEMES = {"light": theme(LATTE, PAGE["light"]), "dark": theme(MOCHA, PAGE["dark"])}
