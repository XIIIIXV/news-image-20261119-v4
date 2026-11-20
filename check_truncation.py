#!/usr/bin/env python3
"""Zero-truncation check for the v4 front page.

Reuses gen_image.fit_lines to verify every text element fits its box
without the ellipsis truncation. Exits non-zero if anything truncates.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw
from gen_image import font, fit_lines, SERIF_B, SANS, SANS_B, CW

data = json.load(open(os.path.join(HERE, "stories.json")))
img = Image.new("RGB", (1024, 1024), (255, 255, 255))
d = ImageDraw.Draw(img)
problems = []

def check(label, text, fnt, width, max_lines):
    lines = fit_lines(text, fnt, width, max_lines, d)
    if any("…" in ln for ln in lines):
        problems.append(f"{label}: TRUNCATED -> {lines}")
    return lines

# leads: head 2 lines in lw-16, deck 2 lines
lw = (CW - 2 * 9) / 3
for lead in data["LEADS"]:
    check(f"lead {lead['n']} head", lead["head"], font(SERIF_B, 17), lw - 16, 2)
    check(f"lead {lead['n']} deck", lead["deck"], font(SANS, 11), lw - 16, 2)

# grid cards: head 2 lines, deck 2 lines, width card_w-12
card_w = (CW - 5 * 8) / 6
for card in data["CARDS"]:
    check(f"card {card['n']} head", card["head"], font(SERIF_B, 13), card_w - 12, 2)
    check(f"card {card['n']} deck", card["deck"], font(SANS, 10), card_w - 12, 2)

# timeline events: 2 lines in slot width
sw = (CW - 6 * 6) / 7
for t, city, ev in data["TIMELINE"]:
    check(f"timeline {city} event", ev, font(SANS, 9), sw - 10, 2)

# ALSO: 1 line in column width minus number
also_w = 1024 - 14 - 300 - 10 - 14
col_w = (also_w - 10) / 2
for item in data["ALSO"]:
    n, region, field, text, status = item
    tw_num = d.textlength(str(n) + "  ", font=font(SANS_B, 11))
    check(f"also {n}", text, font(SANS, 11), col_w - tw_num - 2, 1)

# DATE CHECK: 2 lines + 1 line in CW-16
check("datecheck left-out", data["DATECHECK"][1], font(SANS, 10), CW - 16, 2)
check("datecheck not-yet-due", data["DATECHECK"][2] + "  " + data["DATECHECK"][3],
      font(SANS, 10), CW - 16, 1)

# number strip labels, stats
for num, lab in data["STATS"]:
    check(f"stat label {num}", lab, font(SANS, 9), (CW - 5 * 6) / 6 - 8, 1)

# verdict + markets: 3 lines in half-16
half = (CW - 8) / 2
check("verdict", data["VERDICT"].replace("THE VERDICT — ", ""), font(SANS, 11), half - 16, 3)
check("markets", data["MARKETS"].replace("MARKETS & MONEY — ", ""), font(SANS, 11), half - 16, 3)

if problems:
    print("TRUNCATION FOUND:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("ZERO TRUNCATION: all heads, decks, ALSO lines, timeline, DATE CHECK, verdict, markets fit.")
