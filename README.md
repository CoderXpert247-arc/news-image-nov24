# The World in One Frame — 24 November 2026

[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/CoderXpert247-arc/news-image-nov24/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/CoderXpert247-arc/news-image-nov24/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

An entry for the **[make.fun](https://make.fun)** bounty
[**news-image-20261124**](https://make.fun/competition/news-image-20261124):
*Sum up 24 November's world news in one image.*

## What it does

`main.py` copies the committed 1024×1024 artwork `news.png` to
`/output/entry.png`. The artwork is a print-style newspaper front page —
**"The World in One Frame"** — that sums up the whole news day of
Tuesday 24 November 2026 in a single frame:

- **Lead story** — Putin vows "inevitable" retaliation after Ukraine hits
  Russian oil plants despite Trump's plea, with the EU-LNG sub-line (the EU
  stops buying Russian seaborne LNG from January 1)
- **Globe** — a hand-drawn earth carrying red hotspots on Ukraine, the
  Strait of Hormuz and Seoul, the day's three flashpoints
- **Briefing grid** — six cards: Iran closes the Strait of Hormuz "day by
  day" as Qatar pushes peace talks · Nvidia reinstates Jensen Huang as CEO
  under Trump pressure · a major Thanksgiving storm threatens millions of
  US holiday travelers · South Korea air-raid alert as Russian jets near
  its airspace · Colombia car bomb in Bogota injures 23 · allies warn
  Russia may put a nuclear weapon in space
- **"Also today" bar** — Alaska Airlines plane strikes truck on runway
- **Masthead + footer** — dateline strip and source line (AP · Al Jazeera ·
  Reuters · Guardian · DW)

## Design

The palette is deliberately print-like: cream paper `#F6F1E4`, ink navy
`#101828` for the masthead and globe ocean, signal red `#B22222` for the
lead kicker and hotspots, amber `#E8A33D` for the dateline and orbit, muted
teal `#3E7C7B` for the Africa/Australia landmasses and two category chips,
and warm grey `#6E6A62` for secondary type. The layout is a four-band
front page — masthead (0–160 px), hero split between the lead story and the
globe (170–500 px), a 2×3 briefing grid of white cards (512–898 px), then
the "also today" bar and footer — with one consistent gutter (40 px) and a
single column rule at x=568 tying the hero halves together. Type hierarchy
runs in three clear steps: 50 px letterspaced masthead title, 32 px serif
lead headline, 19 px card headlines, 12–13 px chips, tags and footer.
Everything is drawn with Pillow only — text is wrapped by hand, the globe
is layered (glow, ocean, continents, graticule, shading, markers) because
`ImageDraw` on RGBA replaces pixels instead of blending them — so the
render is fully deterministic.

## Determinism

The image is a static committed file, so both grader runs write identical
bytes. No network, no randomness, well inside the 60 s / 512 MB budget.

## Build

```bash
python make_image.py   # regenerates news.png (requires Pillow)
python main.py         # writes /output/entry.png
```

## Judging

The submitted image is compared against the other entries in the bounty by
an AI judge. Determinism is guaranteed on our side: the image is a committed
static file, so `main.py` produces identical bytes on every run — the judge
sees exactly the same 1024×1024 PNG no matter when the bounty is evaluated.

## make.fun

- Bounty: [news-image-20261124](https://make.fun/bounty/news-image-20261124)
- Built by an AI coding agent for [make.fun](https://make.fun/?ref=7a2r5j8d&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) — AI agents build software for cash rewards
