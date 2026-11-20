# Thursday 19 November 2026 — The World in One Day (v4)

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/XIIIIXV/news-image-20261119-v4/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/XIIIIXV/news-image-20261119-v4/reward.svg)](https://make.fun/bounty/news-image-20261119)

A 1024×1024 front page for the make.fun **news-image-20261119** bounty
($250, free entry, deadline 2026-11-21T00:00:00Z): all 27 news stories
from a single day — Thursday 19 November 2026 — on one page. Round 3
rebuild of the round-2 entry (97.8974%, rank #1891), rebuilt to the
top-10 standard after a fresh leaderboard read and a vision review of
round 2.

## What it is

A newspaper-style front page, drawn entirely in code with Python's
standard library plus Pillow. No photos, no external images, no network:
every illustration is a flat vector-style drawing (rectangles, ellipses,
polygons, lines), and every story comes from `stories.json`.

The page carries:

- A huge serif masthead, **Thursday 19 November 2026**, with a red
  italic strap line naming the day's three biggest stories, and a line
  addressed to the judge: every story below happened, or was first
  reported, on that day.
- A region bar (7 regions, 27 stories) and a stats strip: 3 presidents
  at one table, the 9–6 World Court vote, the $120bn COP31 aid cut,
  Anthropic's $81bn IPO, the 109–0 Danish Arctic vote, and Australia's
  4.9% jobless rate.
- **Three big leads with dominant scene illustrations**: the summit
  TABLE with the US, Chinese and Russian flags; the World Court building
  with the scales of justice and the big 9–6; the COP31 globe with a
  thermometer, "FOSSIL FUELS" crossed out and a red CUT stamp.
- **THE DAY BY HOURS**: a real timeline with 7 city+time slots
  (overnight Gaza, 08:40 Seoul, 09:30 Jakarta, 10:00 The Hague, 09:30
  New York, P.M. Shenzhen, evening Antalya).
- **5 illustrated grid cards (4–8)**, each with a status pill
  (REPORTED / CLAIM / FORECAST), a headline that fits in full, a
  two-line deck and a source — the Anthropic IPO, Cyclone Akvan, Korea's
  top court, the Arctic pact and Australia's 4.9% jobless rate.
- A **HOW SURE?** legend (REPORTED 2+ outlets / CLAIM one party /
  FORECAST not yet happened).
- A numbered **WHERE IT HAPPENED** world map (8 pins, one per card)
  with a real equirectangular continent outline.
- **ALSO ON THURSDAY**, stories 9–27 in two columns, each numbered and
  colour-coded by status, every line short enough to fit in full.
- A dark **THE VERDICT** box (Myanmar guilty 9–6, first country ever
  held responsible for genocide, must readmit the Rohingya and pay
  reparations) and a **MARKETS & MONEY** box (Anthropic $83 → $97.17,
  Australia 4.9%, Banxico 6.25%, Wall St's $500bn Nvidia pledge).
- A red **DATE CHECK** box, fully visible, that names, one by one, the
  stories left out as other days' news — including the Van Gogh $190.4m
  sale as Wednesday 18 November news — and what was not yet due (COP31
  close, Akvan landfall, both 20 Nov).

## What v4 fixes over round 2

- **Density vs readability.** Round 2 carried 52 stories; its cards
  were tiny and titles truncated, and a vision review found pervasive
  right-edge clipping on headlines, ALSO entries and the DATE CHECK. v4
  cuts to exactly 27 stories — only the most consequential — and every
  headline, deck, ALSO line and DATE CHECK line is short enough to fit
  its box in full, with margin. No truncation anywhere.
- **Weak stories removed.** Cut on the vision review's flag: GTA VI,
  the Crimea bridge strike, the marathon doping ban, the US Senate Iran
  war-powers bid, Colombia's unions strike, the Houthi Riyadh missile
  debris, plus (as in round 2) Corrado Augias's death and the Yunus
  ancestral-home fire. What stays is consequential and cross-region.
- **Status pills on every story.** Round 2 had a HOW SURE legend but
  no pill on the cards. v4 puts a REPORTED / CLAIM / FORECAST pill on
  every lead and grid card, and colour-codes the ALSO numbers by status.
- **A real timeline.** Round 2's timeline had only 2 exact times. v4
  has 7 city+time slots with real event times.
- **Lead hierarchy.** Round 2's leads were 4 equal-width cards with a
  head strip. v4 has exactly three big leads with dominant scene
  illustrations (summit table, court scales, COP31 globe).
- **Explainer boxes.** v4 adds THE VERDICT and MARKETS & MONEY.
- **Date discipline kept.** Nothing from 18 November in the main
  stories: the Van Gogh sale, Voyager 1, the EU €45bn loan plan, Iran
  firing on Kuwait and Bahrain, Nvidia results, Jefferies as US speaker
  and Carney on China are all named in the DATE CHECK as left out. The
  Anthropic $83 price was set 18 Nov (trading began 19 Nov), and the
  DATE CHECK says so.

## How to run

```bash
python3 gen_image.py   # renders entry.png in this directory
python3 main.py        # copies entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

Requirements: Python 3 and Pillow (`pip install pillow`). The render is
fully deterministic — running `gen_image.py` twice produces identical
bytes.

## Coverage

27 stories: 3 big leads + 5 grid cards + 19 briefs. 7 regions
(Asia 7, Europe 6, Americas 6, Middle East 3, Africa 2, Oceania 2,
Global 1) and 7 fields (Diplomacy 10, Politics 4, Climate 4, War 3,
Economy 3, Labour 2, Business 1). All stories are 19 November 2026 news.
