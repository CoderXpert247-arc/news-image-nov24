"""Draw the 1024x1024 front page summing up the world's news of
Tuesday 24 November 2026, and save it as ``news.png``.

Design
------
A premium print-style newspaper cover built from four bands:

1. **Masthead** (0-160px)   -- ink-navy band, letterspaced cream title,
   thin signal-red rule, amber dateline strip.
2. **Hero** (170-500px)     -- left: the lead story (red kicker, big serif
   headline, grey EU-LNG sub-line, byline row); right: a hand-drawn globe
   with cream/teal continents, graticule arcs, an amber glow + dashed
   orbit and three red hotspots (UKRAINE, HORMUZ, SEOUL) on leader lines.
3. **Briefing grid** (512-898px) -- 2 x 3 white cards, each with a
   colour-coded category chip, a two-line bold headline and a source tag,
   followed by a navy "ALSO TODAY" bar.
4. **Footer** (964-1024px)  -- hairline rule, grey source line, red
   "for make.fun" mark.

Determinism
-----------
The renderer is a pure, deterministic function of the constants in this
file: no randomness, no timestamps, no network access, and every font is
loaded by absolute path from ``C:/Windows/Fonts`` (a missing font raises
instead of silently falling back, so the output can never change shape
without notice).  Running ``python make_image.py`` therefore always
produces byte-identical PNG bytes for ``news.png``.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

W = H = 1024
HERE = Path(__file__).resolve().parent
FONT_DIR = Path("C:/Windows/Fonts")

# ---------------------------------------------------------------- palette --
PAPER = (246, 241, 228)   # #F6F1E4 cream paper
INK = (16, 24, 40)        # #101828 ink navy
RED = (178, 34, 34)       # #B22222 signal red
AMBER = (232, 163, 61)    # #E8A33D amber
TEAL = (62, 124, 123)     # #3E7C7B muted teal
GREY = (110, 106, 98)     # #6E6A62 warm grey
WHITE = (255, 255, 255)
HAIR = (226, 220, 205)    # hairline on paper
NAVY_SOFT = (46, 66, 104) # globe lighting

# ------------------------------------------------------------- typography --
_FONTS: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a Windows font by absolute path (cached, fails loudly)."""
    key = (name, size)
    if key not in _FONTS:
        path = FONT_DIR / name
        if not path.is_file():
            raise FileNotFoundError(f"required font missing: {path}")
        _FONTS[key] = ImageFont.truetype(str(path), size)
    return _FONTS[key]


def mix(a, b, t: float):
    """Alpha-blend colour *b* over colour *a* by factor *t* (0..1)."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tracked(d, x, y, text, f, fill, spacing=0.0, anchor="la"):
    """Draw *text* with manual letter-spacing; returns the total width."""
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + spacing * max(0, len(text) - 1)
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += w + spacing
    return total


def wrap(d, text, f, maxw):
    """Greedy word wrap (PIL has no wrapping of its own)."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if not cur or d.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, name, size, maxw, maxlines, lo=14):
    """Shrink the font until *text* fits in *maxlines* of *maxw* pixels."""
    while size > lo:
        f = font(name, size)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= maxlines:
            return f, lines
        size -= 1
    f = font(name, lo)
    return f, wrap(d, text, f, maxw)


# ---------------------------------------------------------------- content --
LEAD_KICKER = "LEAD  ·  WAR IN UKRAINE"
LEAD_HEAD = (
    "Putin vows \u201cinevitable\u201d retaliation after Ukraine hits "
    "Russian oil plants despite Trump\u2019s plea"
)
LEAD_SUB = (
    "The EU stops buying Russian seaborne LNG from January 1 as Brussels "
    "tightens the squeeze on Moscow\u2019s war economy."
)

# chip, chip background, chip foreground, headline, source
CARDS = [
    ("MIDEAST", RED, PAPER,
     "Iran orders Strait of Hormuz closed \u201cday by day\u201d as Qatar "
     "pushes peace talks", "AP"),
    ("TECH", TEAL, PAPER,
     "Nvidia reinstates Jensen Huang as CEO after scandal under Trump "
     "pressure", "REUTERS"),
    ("US", INK, PAPER,
     "Major Thanksgiving storm threatens millions of US holiday travelers",
     "AP"),
    ("ASIA", AMBER, INK,
     "South Korea air-raid alert as Russian jets near its airspace",
     "REUTERS"),
    ("AMERICAS", TEAL, PAPER,
     "Colombia car bomb injures 23 in night-time blast", "AP"),
    ("WORLD", RED, PAPER,
     "Allies warn Russia may put a nuclear weapon in space", "NATO"),
]

BRIEF_HEAD = "Alaska Airlines plane strikes truck on runway"
BRIEF_TAG = "US  ·  AVIATION"
SOURCES = "Sources: AP  ·  Al Jazeera  ·  Reuters  ·  Guardian  ·  DW"

# globe hotspots: label, normalised position on the sphere, leader elbows
# (absolute pixels), label anchor + label position
CX, CY, R = 782, 336, 96
HOTSPOTS = [
    ("UKRAINE", (0.10, -0.48), [(706, 252), (654, 252)],
     "rm", (646, 252)),
    ("SEOUL", (0.66, -0.34), [(894, 262)], "lm", (904, 262)),
    ("HORMUZ", (0.40, 0.06), [(892, 398)], "lm", (902, 398)),
]

# --------------------------------------------------------------- geometry --
MAST_H = 160
GRID_X, GRID_GAP = 40, 16
CARD_W = (W - 2 * GRID_X - GRID_GAP) // 2   # 464
CARD_H = 118
GRID_Y = 512
ROW_PITCH = CARD_H + GRID_GAP               # 134

LEAD_X0, LEAD_X1 = 40, 556
HERO_Y = 170


# =============================================================== rendering ==
img = Image.new("RGBA", (W, H), PAPER + (255,))
d = ImageDraw.Draw(img)


def text_w(t, f):
    return d.textlength(t, font=f)


# ---------------------------------------------------------------- masthead --
d.rectangle([0, 0, W, MAST_H], fill=INK + (255,))

f_title = font("arialbd.ttf", 50)
tracked(d, W / 2, 60, "THE WORLD IN ONE FRAME", f_title, PAPER,
        spacing=5.0, anchor="mm")

d.rectangle([40, 96, W - 40, 100], fill=RED + (255,))

f_date = font("arialbd.ttf", 16)
tracked(d, W / 2, 130,
        "TUESDAY  ·  24 NOVEMBER 2026  ·  THE DAY\u2019S NEWS SUMMED UP",
        f_date, AMBER, spacing=2.6, anchor="mm")

f_ed = font("arial.ttf", 12)
tracked(d, 40, 130, "VOL. I  ·  NO. 24", f_ed, (156, 166, 184),
        spacing=1.4, anchor="lm")
tracked(d, W - 40, 130, "LATE EDITION", f_ed, (156, 166, 184),
        spacing=1.4, anchor="rm")

# ------------------------------------------------------------- lead story --
d.rectangle([LEAD_X0, 176, LEAD_X1, 181], fill=RED + (255,))

f_kick = font("arialbd.ttf", 16)
tracked(d, LEAD_X0, 200, LEAD_KICKER, f_kick, RED, spacing=2.2, anchor="la")

f_head, head_lines = fit(d, LEAD_HEAD, "georgiab.ttf", 32,
                         LEAD_X1 - LEAD_X0, 3)
hy = 232
for line in head_lines:
    d.text((LEAD_X0, hy), line, font=f_head, fill=INK + (255,))
    hy += round(f_head.size * 1.34)

rule_y = hy + 10
d.line([LEAD_X0, rule_y, LEAD_X1, rule_y], fill=HAIR + (255,), width=1)

f_sub = font("georgia.ttf", 17)
sub_lines = wrap(d, LEAD_SUB, f_sub, LEAD_X1 - LEAD_X0)
sy = rule_y + 14
for line in sub_lines:
    d.text((LEAD_X0, sy), line, font=f_sub, fill=GREY + (255,))
    sy += 24

by = 452
d.line([LEAD_X0, by - 12, LEAD_X1, by - 12], fill=HAIR + (255,), width=1)
f_small = font("arialbd.ttf", 12)
tracked(d, LEAD_X0, by, "ANALYSIS  ·  PAGE ONE", f_small, INK,
        spacing=1.6, anchor="la")
tracked(d, LEAD_X1, by, "AP  ·  REUTERS", f_small, GREY,
        spacing=1.6, anchor="ra")

# column rule separating the lead story from the globe
d.line([568, 176, 568, 466], fill=HAIR + (255,), width=1)

# ------------------------------------------------------------ globe (hero) --
# NOTE: ImageDraw on an RGBA image REPLACES pixels instead of blending them,
# so every band of transparency is drawn on its own layer and merged with
# Image.alpha_composite, which does blend correctly.
def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


sphere_mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(sphere_mask).ellipse([CX - R, CY - R, CX + R, CY + R],
                                    fill=255)


def masked(l):
    """Keep only what falls inside the globe."""
    l.putalpha(ImageChops.multiply(l.getchannel("A"), sphere_mask))
    return l


def sphere(pts):
    return [(CX + x * R, CY + y * R) for x, y in pts]


# -- amber glow + dashed orbit ---------------------------------------------
glow = layer()
gd = ImageDraw.Draw(glow)
for i in range(26):
    r = R + 6 + i
    a = max(0, 44 - i * 2)
    gd.ellipse([CX - r, CY - r, CX + r, CY + r], outline=AMBER + (a,),
               width=3)

orbit_r = R + 22
segments = 48
for k in range(0, segments, 2):
    a0 = k * 360.0 / segments
    a1 = a0 + (360.0 / segments) * 0.55
    gd.arc([CX - orbit_r, CY - orbit_r, CX + orbit_r, CY + orbit_r],
           a0, a1, fill=AMBER + (215,), width=3)

# -- ocean ------------------------------------------------------------------
ocean = layer()
ImageDraw.Draw(ocean).ellipse([CX - R, CY - R, CX + R, CY + R],
                              fill=INK + (255,))

# -- continents (stylised blobs) + graticule, masked to the sphere ----------
land = layer()
idr = ImageDraw.Draw(land)

idr.polygon(sphere([
    (0.02, -0.60), (0.30, -0.58), (0.55, -0.45), (0.72, -0.25),
    (0.68, -0.05), (0.50, 0.02), (0.34, -0.06), (0.20, 0.02),
    (0.08, -0.10), (0.00, -0.30), (-0.06, -0.48),
]), fill=PAPER + (255,))                                    # Eurasia
idr.polygon(sphere([
    (-0.78, -0.42), (-0.52, -0.55), (-0.34, -0.40), (-0.40, -0.20),
    (-0.30, -0.05), (-0.38, 0.15), (-0.34, 0.42), (-0.46, 0.66),
    (-0.60, 0.50), (-0.62, 0.20), (-0.70, -0.05), (-0.80, -0.20),
]), fill=PAPER + (255,))                                    # Americas
idr.polygon(sphere([
    (-0.02, -0.12), (0.22, -0.16), (0.32, 0.05), (0.26, 0.32),
    (0.10, 0.55), (-0.04, 0.42), (-0.12, 0.15), (-0.14, -0.02),
]), fill=TEAL + (255,))                                     # Africa
idr.ellipse([CX + 0.44 * R, CY + 0.36 * R, CX + 0.70 * R, CY + 0.58 * R],
            fill=TEAL + (255,))                             # Australia
idr.ellipse([CX - 0.30 * R, CY - 0.72 * R, CX - 0.08 * R, CY - 0.52 * R],
            fill=PAPER + (255,))                            # Greenland
for cx0, cy0, rx0, ry0 in (                            # isles: UK, Japan,
    (-0.13, -0.45, 0.045, 0.055),                        # Indonesia, NZ
    (0.68, -0.32, 0.04, 0.06),
    (0.52, 0.12, 0.075, 0.035),
    (0.78, 0.55, 0.035, 0.045),
):
    idr.ellipse([CX + (cx0 - rx0) * R, CY + (cy0 - ry0) * R,
                 CX + (cx0 + rx0) * R, CY + (cy0 + ry0) * R],
                fill=PAPER + (255,))

# latitude / longitude arcs (kept faint so the continents stay legible)
for dy in (-0.62, -0.32, 0.0, 0.32, 0.62):
    rx = math.sqrt(max(0.0, 1.0 - dy * dy)) * R
    ry = 0.085 * R
    idr.ellipse([CX - rx, CY + dy * R - ry, CX + rx, CY + dy * R + ry],
                outline=(246, 241, 228, 52), width=1)
for rx in (0.35, 0.70):
    idr.ellipse([CX - rx * R, CY - R, CX + rx * R, CY + R],
                outline=(246, 241, 228, 40), width=1)
idr.line([CX, CY - R, CX, CY + R], fill=(246, 241, 228, 40), width=1)
masked(land)

# -- sphere lighting: lit from the upper left, shadowed lower right ---------
shade = layer()
sdr = ImageDraw.Draw(shade)
for i in range(7):
    rr = R * (1.05 - i * 0.12)
    sdr.ellipse([CX - 0.35 * R - rr, CY - 0.35 * R - rr,
                 CX - 0.35 * R + rr, CY - 0.35 * R + rr],
                fill=NAVY_SOFT + (14,))
for i in range(6):
    rr = R * (1.05 - i * 0.15)
    sdr.ellipse([CX + 0.40 * R - rr, CY + 0.42 * R - rr,
                 CX + 0.40 * R + rr, CY + 0.42 * R + rr],
                fill=(0, 0, 0, 11))
masked(shade)

# -- rim, specular highlight, hotspot markers ------------------------------
over = layer()
od = ImageDraw.Draw(over)
od.ellipse([CX - R, CY - R, CX + R, CY + R],
           outline=(246, 241, 228, 95), width=2)
od.arc([CX - R, CY - R, CX + R, CY + R], 185, 300,
       fill=(255, 255, 255, 150), width=3)

for label, (nx, ny), elbows, anchor, (lx, ly) in HOTSPOTS:
    px, py = CX + nx * R, CY + ny * R
    od.line([(px, py)] + elbows, fill=RED + (235,), width=2, joint="curve")
    od.ellipse([px - 10, py - 10, px + 10, py + 10],
               outline=RED + (75,), width=2)
    od.ellipse([px - 4, py - 4, px + 4, py + 4],
               fill=RED + (255,), outline=PAPER + (255,), width=2)

gl = glow
for part in (ocean, land, shade, over):
    gl = Image.alpha_composite(gl, part)
img = Image.alpha_composite(img, gl)
d = ImageDraw.Draw(img)

label_font = font("arialbd.ttf", 12)
for label, (nx, ny), elbows, anchor, (lx, ly) in HOTSPOTS:
    tracked(d, lx, ly, label, label_font, RED, spacing=1.6, anchor=anchor)

f_cap = font("arialbd.ttf", 12)
tracked(d, W - GRID_X, 180, "THE WORLD, TODAY", f_cap, GREY,
        spacing=2.4, anchor="ra")

# ------------------------------------------------------- briefing section --
f_sec = font("arialbd.ttf", 14)
tracked(d, GRID_X, 486, "THE BRIEFING", f_sec, INK, spacing=2.4, anchor="la")
d.line([190, 494, W - GRID_X, 494], fill=HAIR + (255,), width=1)

# ------------------------------------------------------------- story grid --
f_chip = font("arialbd.ttf", 13)
f_card = font("arialbd.ttf", 19)
f_src = font("arial.ttf", 11)

for i, (chip, chip_bg, chip_fg, head, source) in enumerate(CARDS):
    row, col = divmod(i, 2)
    x = GRID_X + col * (CARD_W + GRID_GAP)
    y = GRID_Y + row * ROW_PITCH

    d.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=12,
                        fill=WHITE + (255,), outline=HAIR + (255,), width=2)

    # category chip (pill)
    chip_w = text_w(chip, f_chip) + 20
    d.rounded_rectangle([x + 18, y + 20, x + 18 + chip_w, y + 44],
                        radius=12, fill=chip_bg + (255,))
    tracked(d, x + 28, y + 32, chip, f_chip, chip_fg, spacing=1.4,
            anchor="lm")

    # source tag, aligned with the chip
    tracked(d, x + CARD_W - 16, y + 32, source, f_src, GREY,
            spacing=1.2, anchor="rm")

    # headline (max two lines)
    f_headline, lines = fit(d, head, "arialbd.ttf", 19, CARD_W - 36, 2)
    ty = y + 56
    for line in lines[:2]:
        d.text((x + 18, ty), line, font=f_headline, fill=INK + (255,))
        ty += 26

# ----------------------------------------------------------- "also today" --
bar_y0, bar_y1 = 906, 950
d.rounded_rectangle([GRID_X, bar_y0, W - GRID_X, bar_y1], radius=10,
                    fill=INK + (255,))

f_brief = font("arialbd.ttf", 16)
brief_w = text_w(BRIEF_HEAD, f_brief)
pill_w = text_w("ALSO TODAY", f_chip) + 22
pill_x = GRID_X + 16
d.rounded_rectangle([pill_x, bar_y0 + 11, pill_x + pill_w, bar_y1 - 11],
                    radius=11, fill=RED + (255,))
tracked(d, pill_x + pill_w / 2, (bar_y0 + bar_y1) / 2, "ALSO TODAY",
        f_chip, PAPER, spacing=1.4, anchor="mm")

text_x = pill_x + pill_w + 16
d.text((text_x, (bar_y0 + bar_y1) / 2), BRIEF_HEAD, font=f_brief,
       fill=PAPER + (255,), anchor="lm")
tracked(d, W - GRID_X - 16, (bar_y0 + bar_y1) / 2, BRIEF_TAG,
        font("arialbd.ttf", 12), AMBER, spacing=1.6, anchor="rm")

assert text_x + brief_w < W - GRID_X - 150, "brief bar overflow"

# ----------------------------------------------------------------- footer --
d.line([GRID_X, 966, W - GRID_X, 966], fill=GREY + (255,), width=1)
f_foot = font("arial.ttf", 13)
d.text((GRID_X, 982), SOURCES, font=f_foot, fill=GREY + (255,),
       anchor="la")
tracked(d, W - GRID_X, 982, "for make.fun", font("arialbd.ttf", 13), RED,
        spacing=1.2, anchor="ra")

# ------------------------------------------------------------------- save ---
out = HERE / "news.png"
img.convert("RGB").save(out, "PNG")
print(f"saved {out} {img.size[0]}x{img.size[1]} "
      f"({out.stat().st_size} bytes)")
