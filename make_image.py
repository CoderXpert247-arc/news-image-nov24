"""Draws the 1024x1024 news infographic for 24 November 2026.

The repository ships the resulting news.png; main.py copies it to
/output/entry.png so the program stays deterministic (it writes the same
bytes on every run).
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024

BG = (246, 243, 236)        # warm paper
INK = (22, 22, 26)          # near-black text
RED = (178, 34, 34)         # accent red
MUTED = (110, 106, 98)      # secondary text
CARD = (255, 255, 255)
LINE = (224, 219, 208)


def font(name, size):
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
    except OSError:
        return ImageFont.load_default()


F_H1 = font("arialbd.ttf", 58)
F_DATE = font("arial.ttf", 26)
F_KICK = font("arialbd.ttf", 20)
F_HEAD = font("arialbd.ttf", 25)
F_HEAD_S = font("arialbd.ttf", 23)
F_FOOT = font("arial.ttf", 20)

STORIES = [
    ("WORLD", "Putin vows retaliation after Ukraine hits Russian oil plants", True),
    ("MIDEAST", "Iran orders Strait of Hormuz closed 'day by day' as Qatar pushes peace talks", False),
    ("TECH", "Nvidia reinstates Jensen Huang as CEO after scandal, Trump pressure", False),
    ("US", "Major Thanksgiving storm threatens millions of holiday travelers", False),
    ("ASIA", "South Korea air-raid alert as Russian jets near its airspace", False),
    ("AMERICAS", "Colombia car bomb injures 23 in night-time blast", False),
    ("EUROPE", "EU to stop buying Russian seaborne LNG from January 1", False),
    ("US", "Alaska Airlines plane strikes truck on runway", False),
    ("WORLD", "Allies warn Russia may put nuclear weapon in space", False),
]

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


def text_w(t, f):
    return d.textbbox((0, 0), t, font=f)[2]


# --- masthead -------------------------------------------------------------
d.rectangle([0, 0, W, 150], fill=INK)
d.text((512, 44), "THE WORLD IN ONE FRAME", font=F_H1, fill=(255, 255, 255), anchor="mm")
d.text((512, 96), "TUESDAY, 24 NOVEMBER 2026  ·  THE DAY'S NEWS, SUMMED UP",
       font=F_DATE, fill=(232, 106, 106), anchor="mm")
d.rectangle([0, 150, W, 156], fill=RED)

# --- lead story -----------------------------------------------------------
lead_y = 178
d.rounded_rectangle([40, lead_y, W - 40, lead_y + 148], radius=14, fill=CARD, outline=LINE, width=2)
d.rectangle([40, lead_y, 50, lead_y + 148], fill=RED)
d.text((72, lead_y + 22), "LEAD  ·  WAR IN UKRAINE", font=F_KICK, fill=RED)
d.text((72, lead_y + 56), "Putin vows 'inevitable' retaliation after Ukraine",
       font=F_HEAD, fill=INK)
d.text((72, lead_y + 92), "hits Russian oil plants despite Trump's plea",
       font=F_HEAD, fill=INK)
d.text((72, lead_y + 124), "EU also moves to end Russian LNG imports from Jan 1",
       font=F_FOOT, fill=MUTED)

# --- story grid -----------------------------------------------------------
cols, rows = 2, 4
gx0, gy0 = 40, lead_y + 168
gap = 18
cw = (W - 2 * gx0 - gap) // cols
ch = 116

for i, (kick, head, hot) in enumerate(STORIES[1:]):
    r, c = divmod(i, cols)
    x = gx0 + c * (cw + gap)
    y = gy0 + r * (ch + gap)
    d.rounded_rectangle([x, y, x + cw, y + ch], radius=12,
                        fill=CARD, outline=(RED if hot else LINE), width=2)
    d.text((x + 18, y + 14), kick, font=F_KICK, fill=(RED if hot else MUTED))
    # wrap headline
    words, lines, cur = head.split(), [], ""
    maxw = cw - 36
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(trial, F_HEAD_S) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    ly = y + 44
    for ln in lines[:3]:
        d.text((x + 18, ly), ln, font=F_HEAD_S, fill=INK)
        ly += 28

# --- footer ---------------------------------------------------------------
fy = gy0 + rows * (ch + gap) + 6
d.line([40, fy, W - 40, fy], fill=LINE, width=2)
d.text((512, fy + 26),
       "Sources: AP · Al Jazeera · DW · Guardian · NPR · US News  —  news-image-20261124",
       font=F_FOOT, fill=MUTED, anchor="mm")
d.text((512, fy + 56), "built for make.fun", font=F_FOOT, fill=RED, anchor="mm")

img.save("news.png", "PNG")
print("saved news.png", img.size)
