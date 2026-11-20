#!/usr/bin/env python3
"""Render the v4 front page for make.fun news-image-20261119.

Draws a 1024x1024 newspaper front page with Pillow: masthead, number
strip, three big illustrated leads, an hourly timeline, an 11-card grid
with per-story status pills, a numbered world map, an ALSO list, a
VERDICT box, a MARKETS box, and a DATE CHECK strip. Every story comes
from stories.json; every illustration is drawn in code (no photos).
Deterministic: same input -> identical bytes.
"""
import json
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996

# --- palette ---
PAPER = (247, 243, 234)
INK = (26, 26, 26)
INK_SOFT = (70, 70, 70)
RED = (185, 28, 28)
RED_DARK = (153, 27, 27)
NAVY = (30, 58, 95)
NAVY_DARK = (23, 45, 74)
BLUE = (37, 99, 235)
GREEN = (21, 128, 61)
ORANGE = (194, 65, 12)
GOLD = (180, 83, 9)
BORDER = (200, 192, 175)
CARD_BG = (255, 255, 255)
SKY = (214, 231, 245)
SEA = (163, 196, 224)

FDIR = "/usr/share/fonts/truetype"
def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SERIF_B = "liberation/LiberationSerif-Bold.ttf"
SERIF = "liberation/LiberationSerif-Regular.ttf"
SERIF_I = "liberation/LiberationSerif-Italic.ttf"
SANS_B = "liberation/LiberationSans-Bold.ttf"
SANS = "liberation/LiberationSans-Regular.ttf"
SANS_I = "liberation/LiberationSans-Italic.ttf"

STATUS_COLORS = {"REPORTED": (21, 128, 61), "CLAIM": (194, 65, 12), "FORECAST": (37, 99, 235)}

def load_data():
    with open(os.path.join(HERE, "stories.json")) as f:
        return json.load(f)

def wrap(text, fnt, width, draw):
    """Wrap text to fit width (px). Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(text, fnt, width, max_lines, draw, min_size=None):
    """Wrap text to at most max_lines; truncate last line with ellipsis."""
    lines = wrap(text, fnt, width, draw)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and draw.textlength(last + " …", font=fnt) > width:
        last = last[:-1].strip()
    out[-1] = last + " …"
    return out

def pill(draw, x, y, text, color, fnt, fg=(255, 255, 255), pad_x=5, pad_y=2):
    """Draw a small rounded status pill; returns (w, h)."""
    tw = draw.textlength(text, font=fnt)
    w, h = int(tw) + 2 * pad_x, fnt.size + 2 * pad_y
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=color)
    draw.text((x + pad_x, y + pad_y - 1), text, font=fnt, fill=fg)
    return w, h

def badge(draw, cx, cy, r, n, fill=RED, fg=(255, 255, 255)):
    """Numbered circle badge centred at (cx, cy)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=(255, 255, 255), width=1)
    t = str(n)
    f = font(SANS_B, 13 if r >= 11 else 10)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - f.size / 2 - 1), t, font=f, fill=fg)

def rule(draw, x, y, w, color=INK, width=1):
    draw.line([(x, y), (x + w, y)], fill=color, width=width)

# --- world map (coarse equirectangular continent outlines, lon/lat) ---
CONTINENTS = {
    "north_america": [(-168, 66), (-155, 60), (-140, 60), (-130, 55), (-125, 48), (-125, 40), (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-92, 14), (-86, 12), (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-88, 18), (-90, 21), (-87, 21), (-84, 25), (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 46), (-55, 47), (-60, 52), (-65, 58), (-68, 58), (-75, 62), (-80, 66), (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68), (-168, 66)],
    "south_america": [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-71, -18), (-70, -23), (-65, -28), (-58, -34), (-57, -38), (-62, -41), (-65, -45), (-68, -50), (-68, -54), (-66, -55), (-63, -50), (-58, -42), (-52, -33), (-48, -27), (-41, -22), (-39, -17), (-35, -9), (-35, -6), (-38, -3), (-43, -2), (-50, 0), (-52, 4), (-55, 6), (-58, 8), (-62, 9), (-68, 11), (-72, 12), (-76, 10), (-79, 9)],
    "africa": [(-17, 15), (-16, 21), (-13, 27), (-9, 31), (-5, 35), (0, 36), (10, 37), (20, 32), (30, 31), (32, 31), (34, 28), (37, 22), (39, 18), (41, 12), (44, 11), (48, 11), (51, 12), (48, 6), (44, 2), (41, -2), (40, -8), (38, -14), (35, -20), (33, -26), (28, -33), (20, -35), (17, -32), (15, -27), (13, -20), (12, -14), (12, -8), (10, -3), (9, 2), (7, 4), (2, 6), (-4, 5), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
    "europe": [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (-5, 48), (-1, 50), (2, 51), (4, 53), (8, 55), (8, 57), (12, 56), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (28, 65), (24, 68), (20, 70), (25, 71), (30, 70), (32, 68), (35, 66), (40, 65), (44, 66), (48, 67), (52, 68), (56, 69), (60, 69), (64, 69), (68, 68), (62, 64), (56, 60), (52, 58), (48, 55), (44, 52), (40, 50), (36, 48), (32, 46), (28, 45), (24, 42), (22, 40), (20, 40), (16, 38), (12, 37), (8, 37), (3, 37), (0, 36), (-5, 36), (-10, 36)],
    "asia": [(30, 36), (33, 36), (36, 33), (39, 31), (43, 29), (48, 29), (52, 27), (56, 26), (58, 25), (61, 25), (64, 25), (67, 23), (70, 21), (72, 20), (74, 18), (76, 12), (77, 8), (80, 7), (80, 11), (84, 15), (87, 20), (90, 22), (92, 21), (94, 17), (97, 12), (99, 9), (101, 6), (103, 4), (105, 2), (107, 8), (109, 12), (111, 16), (113, 20), (116, 22), (118, 25), (120, 28), (122, 31), (124, 35), (126, 38), (128, 40), (130, 42), (132, 44), (135, 44), (138, 47), (141, 50), (141, 54), (138, 58), (136, 60), (140, 60), (144, 60), (148, 61), (152, 62), (156, 60), (159, 58), (161, 55), (162, 59), (165, 62), (169, 66), (173, 66), (178, 65), (180, 65), (178, 62), (174, 60), (170, 58), (166, 56), (162, 52), (158, 50), (154, 46), (150, 44), (146, 42), (142, 40), (140, 38), (138, 35), (135, 32), (132, 30), (130, 27), (127, 24), (124, 21), (121, 18), (118, 15), (115, 12), (112, 10), (110, 8), (108, 6), (106, 3), (104, 2), (102, 4), (100, 7), (98, 10), (96, 14), (94, 17), (92, 21), (90, 22), (88, 20), (86, 17), (83, 14), (81, 11), (80, 8), (78, 8), (76, 12), (74, 18), (72, 20), (70, 21), (68, 23), (66, 25), (63, 25), (60, 25), (57, 26), (54, 27), (51, 28), (48, 29), (45, 29), (42, 29), (39, 31), (36, 33), (33, 36), (30, 36)],
    "australia": [(113, -22), (114, -28), (115, -33), (117, -35), (120, -34), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (148, -39), (150, -37), (152, -32), (153, -28), (152, -24), (150, -22), (147, -19), (144, -15), (142, -11), (141, -13), (138, -15), (136, -15), (134, -12), (131, -12), (128, -14), (125, -14), (122, -17), (120, -20), (116, -21), (113, -22)],
}

def lonlat_to_xy(lon, lat, x0, y0, w, h):
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (85.0 - lat) / (85.0 - (-55.0)) * h
    return x, y

def draw_map(draw, box, pins):
    """Draw the world map with numbered pins. pins: list of (n, lon, lat)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=SEA, outline=BORDER)
    for pts in CONTINENTS.values():
        xy = [lonlat_to_xy(lon, lat, x0 + 2, y0 + 2, w - 4, h - 4) for lon, lat in pts]
        draw.polygon(xy, fill=(232, 222, 198), outline=(150, 140, 120))
    for n, lon, lat in pins:
        px, py = lonlat_to_xy(lon, lat, x0 + 2, y0 + 2, w - 4, h - 4)
        badge(draw, px, py, 10, n, fill=RED)

# --- lead illustrations (flat, bold, drawn in code) ---
def draw_flag(draw, x, y, w, h, kind):
    """Small flag on a pole. kind: 'us' | 'cn' | 'ru'."""
    draw.line([(x, y), (x, y + h + 26)], fill=(90, 70, 50), width=3)
    if kind == "us":
        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK)
        for i in range(7):
            if i % 2 == 0:
                draw.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7], fill=RED)
        draw.rectangle([x, y, x + w * 0.45, y + h * 0.55], fill=NAVY)
    elif kind == "cn":
        draw.rectangle([x, y, x + w, y + h], fill=RED, outline=INK)
        for sx, sy, r in [(8, 8, 5), (20, 5, 2), (23, 10, 2), (20, 15, 2), (14, 17, 2)]:
            draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(255, 215, 0))
    else:  # ru
        draw.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255), outline=INK)
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=BLUE)
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=RED)

def draw_summit_table(draw, box):
    """Lead 1: three flags behind a summit table with three seated figures."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(233, 224, 205), outline=BORDER)
    # wall + floor
    draw.rectangle([x0, y0, x1, y0 + (y1 - y0) * 0.62], fill=(240, 232, 214))
    draw.rectangle([x0, y0 + (y1 - y0) * 0.62, x1, y1], fill=(203, 178, 140))
    # three flags
    fw, fh = 52, 32
    for i, kind in enumerate(["us", "cn", "ru"]):
        fx = x0 + 28 + i * 118
        draw_flag(draw, fx, y0 + 14, fw, fh, kind)
    # table
    tx0, ty0 = x0 + 18, y0 + 88
    tx1, ty1 = x1 - 18, y0 + 118
    draw.rectangle([tx0, ty0, tx1, ty1], fill=(122, 84, 52), outline=INK)
    draw.rectangle([tx0, ty1, tx1, ty1 + 6], fill=(96, 64, 38))
    # three seated figures (head + shoulders) behind the table
    for i, col in enumerate([(30, 58, 95), (185, 28, 28), (21, 128, 61)]):
        cx = x0 + 62 + i * 118
        draw.ellipse([cx - 13, ty0 - 26, cx + 13, ty0], fill=(245, 205, 170), outline=INK)
        draw.pieslice([cx - 26, ty0 - 2, cx + 26, ty0 + 34], 180, 360, fill=col, outline=INK)
    # papers on the table
    draw.rectangle([x0 + 40, ty0 + 6, x0 + 78, ty0 + 18], fill=(255, 255, 255), outline=INK)
    draw.rectangle([x1 - 78, ty0 + 6, x1 - 40, ty0 + 18], fill=(255, 255, 255), outline=INK)

def draw_court_scales(draw, box):
    """Lead 2: courthouse columns + scales of justice + big 9-6."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(226, 232, 240), outline=BORDER)
    # pediment + columns
    draw.polygon([(x0 + 20, y0 + 34), (x1 - 20, y0 + 34), ((x0 + x1) / 2, y0 + 8)], fill=(200, 205, 210), outline=INK)
    for i in range(4):
        cx = x0 + 34 + i * 62
        draw.rectangle([cx - 7, y0 + 36, cx + 7, y0 + 92], fill=(245, 245, 240), outline=INK)
    draw.rectangle([x0 + 14, y0 + 92, x1 - 14, y0 + 100], fill=(200, 205, 210), outline=INK)
    # scales of justice
    cx, top, bot = (x0 + x1) / 2, y0 + 106, y1 - 8
    draw.line([(cx, top), (cx, bot)], fill=INK, width=4)
    draw.line([(cx - 52, top + 14), (cx + 52, top + 14)], fill=INK, width=3)
    for sx in (cx - 52, cx + 52):
        draw.line([(sx, top + 14), (sx, top + 30)], fill=INK, width=2)
        draw.polygon([(sx - 20, top + 30), (sx + 20, top + 30), (sx, top + 46)], fill=GOLD, outline=INK)
    draw.ellipse([cx - 5, top - 6, cx + 5, top + 4], fill=GOLD, outline=INK)
    # big 9-6 verdict
    f = font(SERIF_B, 30)
    t = "9–6"
    tw = draw.textlength(t, font=f)
    draw.text(((x0 + x1) / 2 - tw / 2, y1 - 38), t, font=f, fill=RED_DARK)

def draw_cop_globe(draw, box):
    """Lead 3: globe + thermometer, FOSSIL FUELS crossed out, CUT stamp."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(216, 232, 226), outline=BORDER)
    cx, cy, r = x0 + 82, y0 + 52, 42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 180, 220), outline=INK, width=2)
    # land blobs
    draw.ellipse([cx - 32, cy - 24, cx - 4, cy + 2], fill=GREEN)
    draw.ellipse([cx - 2, cy + 6, cx + 26, cy + 32], fill=GREEN)
    draw.ellipse([cx + 8, cy - 34, cx + 34, cy - 10], fill=GREEN)
    draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(255, 255, 255), width=3)
    # thermometer (short, ends above the stamp row)
    tx = x1 - 50
    draw.rounded_rectangle([tx, y0 + 14, tx + 18, y0 + 82], radius=9, fill=(255, 255, 255), outline=INK, width=2)
    draw.rectangle([tx + 4, y0 + 48, tx + 14, y0 + 78], fill=RED)
    draw.ellipse([tx - 6, y0 + 76, tx + 24, y0 + 102], fill=RED, outline=INK)
    # FOSSIL FUELS crossed out
    f = font(SANS_B, 15)
    t = "FOSSIL FUELS"
    tw = draw.textlength(t, font=f)
    tx0 = x0 + 14
    ty = y0 + 106
    draw.text((tx0, ty), t, font=f, fill=INK_SOFT)
    draw.line([(tx0 - 2, ty + 3), (tx0 + tw + 2, ty + 13)], fill=RED, width=4)
    draw.line([(tx0 - 2, ty + 13), (tx0 + tw + 2, ty + 3)], fill=RED, width=4)
    # CUT stamp (right of the crossed-out text, inside the box)
    sf = font(SANS_B, 18)
    st = "CUT"
    draw.rounded_rectangle([x1 - 78, y0 + 102, x1 - 14, y0 + 126], radius=4, outline=RED, width=3)
    draw.text((x1 - 66, y0 + 105), st, font=sf, fill=RED)

# --- small flat icons for grid cards ---
def draw_icon(draw, key, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if key == "chart":  # bar chart, rising
        draw.rectangle([x0, y0, x1, y1], fill=(232, 240, 248))
        bars = [10, 16, 13, 22, 28]
        bw = w / 7
        for i, bh in enumerate(bars):
            bx = x0 + 8 + i * (bw + 2)
            draw.rectangle([bx, y1 - 6 - bh, bx + bw, y1 - 6], fill=NAVY if i < 4 else GREEN)
        draw.line([(x0 + 8, y0 + 10), (x1 - 8, y0 + 6)], fill=RED, width=3)
    elif key == "missile":  # rocket + burst
        draw.rectangle([x0, y0, x1, y1], fill=(245, 232, 222))
        draw.polygon([(cx - 8, y0 + 10), (cx + 8, y0 + 10), (cx + 5, y0 + 34), (cx - 5, y0 + 34)], fill=(200, 200, 200), outline=INK)
        draw.polygon([(cx, y0 + 2), (cx - 8, y0 + 12), (cx + 8, y0 + 12)], fill=RED)
        draw.polygon([(cx - 12, y0 + 30), (cx - 5, y0 + 30), (cx - 10, y0 + 42)], fill=ORANGE)
        draw.polygon([(cx + 12, y0 + 30), (cx + 5, y0 + 30), (cx + 10, y0 + 42)], fill=ORANGE)
        for dx, dy in [(0, 0), (10, 6), (-10, 8), (6, 12)]:
            draw.ellipse([cx + dx - 4, y1 - 16 + dy - 4, cx + dx + 4, y1 - 16 + dy + 4], fill=(255, 170, 0))
    elif key == "cyclone":  # spiral storm
        draw.rectangle([x0, y0, x1, y1], fill=(226, 236, 244))
        for r, col in [(18, (90, 140, 190)), (13, (60, 110, 170)), (8, (30, 80, 140)), (4, NAVY)]:
            draw.arc([cx - r, cy - r, cx + r, cy + r], 40, 300, fill=col, width=4)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=NAVY)
    elif key == "gta":  # night city skyline + pink car
        draw.rectangle([x0, y0, x1, y1], fill=(40, 30, 70))
        for bx, bh, col in [(4, 26, (90, 70, 140)), (16, 36, (120, 90, 170)), (30, 22, (90, 70, 140)), (42, 32, (150, 110, 190))]:
            draw.rectangle([x0 + bx, y1 - 14 - bh, x0 + bx + 10, y1 - 14], fill=col)
        draw.rectangle([x0, y1 - 14, x1, y1], fill=(20, 16, 36))
        draw.ellipse([x1 - 16, y0 + 6, x1 - 6, y0 + 16], fill=(255, 240, 180))
        draw.rounded_rectangle([cx - 16, y1 - 24, cx + 16, y1 - 14], radius=4, fill=(255, 80, 160))
        draw.ellipse([cx - 11, y1 - 14, cx - 5, y1 - 8], fill=INK)
        draw.ellipse([cx + 5, y1 - 14, cx + 11, y1 - 8], fill=INK)
    elif key == "gavel":  # gavel + block
        draw.rectangle([x0, y0, x1, y1], fill=(238, 232, 220))
        draw.rectangle([x0 + 10, y0 + 12, x0 + 34, y0 + 22], fill=(122, 84, 52), outline=INK)
        draw.line([(x0 + 22, y0 + 22), (x0 + 34, y0 + 40)], fill=(122, 84, 52), width=5)
        draw.rectangle([x0 + 28, y1 - 14, x0 + 52, y1 - 8], fill=(150, 110, 70), outline=INK)
    elif key == "arctic":  # iceberg + flag
        draw.rectangle([x0, y0, x1, y1], fill=(214, 232, 244))
        draw.polygon([(x0 + 6, y1 - 12), (x0 + 18, y0 + 14), (x0 + 30, y1 - 12)], fill=(255, 255, 255), outline=BLUE)
        draw.polygon([(x0 + 30, y1 - 12), (x0 + 44, y0 + 20), (x0 + 56, y1 - 12)], fill=(235, 245, 255), outline=BLUE)
        draw.rectangle([x0 + 6, y1 - 12, x1 - 6, y1 - 6], fill=(120, 170, 210))
        draw.line([(x1 - 16, y0 + 8), (x1 - 16, y0 + 24)], fill=INK, width=2)
        draw.polygon([(x1 - 16, y0 + 8), (x1 - 4, y0 + 12), (x1 - 16, y0 + 16)], fill=RED)
    elif key == "bridge":  # suspension bridge
        draw.rectangle([x0, y0, x1, y1], fill=(226, 236, 244))
        draw.rectangle([x0 + 6, y1 - 12, x1 - 6, y1 - 8], fill=(90, 90, 90))
        draw.line([(x0 + 12, y0 + 8), (x0 + 12, y1 - 10)], fill=INK, width=3)
        draw.line([(x1 - 12, y0 + 8), (x1 - 12, y1 - 10)], fill=INK, width=3)
        draw.arc([x0 + 12, y0 + 2, x1 - 12, y1 - 6], 0, 180, fill=INK, width=2)
        draw.line([(cx, y0 + 16), (cx, y1 - 10)], fill=INK, width=2)
    elif key == "jobs":  # arrow UP + bars
        draw.rectangle([x0, y0, x1, y1], fill=(232, 240, 232))
        for i, bh in enumerate([12, 18, 24]):
            bx = x0 + 8 + i * 12
            draw.rectangle([bx, y1 - 8 - bh, bx + 8, y1 - 8], fill=NAVY)
        draw.line([(x0 + 40, y1 - 12), (x1 - 8, y0 + 12)], fill=GREEN, width=4)
        draw.polygon([(x1 - 8, y0 + 12), (x1 - 18, y0 + 12), (x1 - 8, y0 + 22)], fill=GREEN)
    elif key == "march":  # crowd of people
        draw.rectangle([x0, y0, x1, y1], fill=(240, 234, 222))
        for i, col in enumerate([(185, 28, 28), (30, 58, 95), (21, 128, 61), (180, 83, 9)]):
            px = x0 + 10 + i * 13
            draw.ellipse([px - 4, y0 + 12, px + 4, y0 + 20], fill=(245, 205, 170), outline=INK)
            draw.pieslice([px - 7, y0 + 20, px + 7, y0 + 38], 180, 360, fill=col, outline=INK)
        draw.rectangle([x0 + 8, y0 + 6, x1 - 8, y0 + 11], fill=INK)
    elif key == "runner":  # runner figure
        draw.rectangle([x0, y0, x1, y1], fill=(240, 238, 226))
        draw.ellipse([cx + 4, y0 + 8, cx + 14, y0 + 18], fill=(245, 205, 170), outline=INK)
        draw.line([(cx + 6, y0 + 18), (cx - 2, y0 + 28)], fill=RED, width=4)
        draw.line([(cx - 2, y0 + 28), (cx - 12, y0 + 24)], fill=RED, width=4)
        draw.line([(cx - 2, y0 + 28), (cx + 8, y0 + 24)], fill=RED, width=4)
        draw.line([(cx - 2, y0 + 28), (cx - 10, y0 + 40)], fill=INK, width=4)
        draw.line([(cx - 2, y0 + 28), (cx + 10, y0 + 38)], fill=INK, width=4)
        draw.line([(x0 + 6, y1 - 6), (x1 - 6, y1 - 6)], fill=INK, width=2)
    elif key == "senate":  # capitol dome
        draw.rectangle([x0, y0, x1, y1], fill=(238, 232, 222))
        draw.pieslice([cx - 14, y0 + 4, cx + 14, y0 + 22], 180, 360, fill=(245, 245, 240), outline=INK)
        draw.rectangle([x0 + 10, y0 + 22, x1 - 10, y0 + 26], fill=(200, 205, 210), outline=INK)
        for i in range(3):
            px = x0 + 16 + i * 14
            draw.rectangle([px - 3, y0 + 26, px + 3, y1 - 6], fill=(245, 245, 240), outline=INK)
        draw.rectangle([x0 + 8, y1 - 6, x1 - 8, y1 - 2], fill=(200, 205, 210), outline=INK)
    else:  # fallback: plain block
        draw.rectangle([x0, y0, x1, y1], fill=(230, 230, 230))

# --- page layout ---
def render(data, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    xL, xR = MARGIN, W - MARGIN
    y = 10

    # --- masthead ---
    f_title = font(SERIF_B, 44)
    title = "Thursday 19 November 2026"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, y), title, font=f_title, fill=INK)
    y += 52
    f_sub = font(SERIF_I, 16)
    sub = "Trump, Xi and Putin meet in Shenzhen  ·  World Court: Myanmar guilty  ·  COP31 drops fossil fuels"
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, y), sub, font=f_sub, fill=RED_DARK)
    y += 22
    f_judge = font(SANS, 11)
    jl = data["META"]["judge_line"]
    tw = d.textlength(jl, font=f_judge)
    d.text(((W - tw) / 2, y), jl, font=f_judge, fill=INK_SOFT)
    y += 16
    rule(d, xL, y, CW, INK, 3)
    y += 5
    rule(d, xL, y, CW, INK, 1)
    y += 8

    # --- region bar ---
    f_reg = font(SANS_B, 11)
    reg_parts = [f"{r} {n}" for r, n in data["REGIONS"]]
    reg_text = "   ·   ".join(reg_parts)
    bar_h = 18
    d.rectangle([xL, y, xR, y + bar_h], fill=NAVY_DARK)
    tw = d.textlength(reg_text, font=f_reg)
    d.text((xL + 10, y + 4), reg_text, font=f_reg, fill=(255, 255, 255))
    f_33 = font(SANS_B, 12)
    t33 = f"{data['META']['stories']} STORIES"
    tw33 = d.textlength(t33, font=f_33)
    d.text((xR - tw33 - 10, y + 3), t33, font=f_33, fill=(255, 215, 0))
    y += bar_h + 6

    # --- number strip: 6 boxes ---
    f_num = font(SERIF_B, 22)
    f_numlab = font(SANS, 9)
    nboxes = len(data["STATS"])
    bw = (CW - (nboxes - 1) * 6) / nboxes
    bh = 40
    for i, (num, lab) in enumerate(data["STATS"]):
        bx = xL + i * (bw + 6)
        d.rectangle([bx, y, bx + bw, y + bh], fill=CARD_BG, outline=BORDER)
        d.rectangle([bx, y, bx + bw, y + 3], fill=RED)
        tw = d.textlength(num, font=f_num)
        d.text((bx + (bw - tw) / 2, y + 6), num, font=f_num, fill=INK)
        tw = d.textlength(lab, font=f_numlab)
        d.text((bx + (bw - tw) / 2, y + 30), lab, font=f_numlab, fill=INK_SOFT)
    y += bh + 8

    # --- three big leads ---
    lead_h = 240
    lw = (CW - 2 * 9) / 3
    lead_draw = {1: draw_summit_table, 2: draw_court_scales, 3: draw_cop_globe}
    for i, lead in enumerate(data["LEADS"]):
        lx = xL + i * (lw + 9)
        d.rectangle([lx, y, lx + lw, y + lead_h], fill=CARD_BG, outline=BORDER)
        # illustration
        lead_draw[lead["n"]](d, (lx + 1, y + 1, lx + lw - 1, y + 132))
        # number badge + status pill
        badge(d, lx + 16, y + 146, 11, lead["n"], fill=RED)
        f_pill = font(SANS_B, 9)
        pw, _ = pill(d, lx + 32, y + 137, lead["status"], STATUS_COLORS[lead["status"]], f_pill)
        # headline (2 lines max)
        f_head = font(SERIF_B, 17)
        lines = fit_lines(lead["head"], f_head, lw - 16, 2, d)
        ty = y + 154
        for ln in lines:
            d.text((lx + 8, ty), ln, font=f_head, fill=INK)
            ty += 18
        # deck (2 lines max)
        f_deck = font(SANS, 11)
        dlines = fit_lines(lead["deck"], f_deck, lw - 16, 2, d)
        for ln in dlines:
            d.text((lx + 8, ty), ln, font=f_deck, fill=INK_SOFT)
            ty += 12
        # source
        f_src = font(SANS_B, 8)
        d.text((lx + 8, y + lead_h - 12), lead["src"], font=f_src, fill=(140, 130, 115))
    y += lead_h + 8

    # --- timeline: THE DAY BY HOURS ---
    f_tl = font(SANS_B, 11)
    d.text((xL, y), "THE DAY BY HOURS", font=f_tl, fill=INK)
    rule(d, xL + 118, y + 6, CW - 118, BORDER, 1)
    y += 16
    tl_h = 40
    nslots = len(data["TIMELINE"])
    sw = (CW - (nslots - 1) * 6) / nslots
    f_time = font(SANS_B, 12)
    f_city = font(SANS_B, 9)
    f_ev = font(SANS, 9)
    for i, (t, city, ev) in enumerate(data["TIMELINE"]):
        sx = xL + i * (sw + 6)
        d.rectangle([sx, y, sx + sw, y + tl_h], fill=CARD_BG, outline=BORDER)
        d.text((sx + 5, y + 3), t, font=f_time, fill=RED_DARK)
        d.text((sx + 5, y + 17), city, font=f_city, fill=INK)
        ev_lines = fit_lines(ev, f_ev, sw - 10, 2, d)
        ey = y + 28
        for ln in ev_lines:
            d.text((sx + 5, ey), ln, font=f_ev, fill=INK_SOFT)
            ey += 10
        if i < nslots - 1:
            d.line([(sx + sw + 1, y + tl_h / 2), (sx + sw + 5, y + tl_h / 2)], fill=RED, width=2)
    y += tl_h + 8

    # --- grid: cards 4-8 (6 cols x 1 row) + HOW SURE legend in last slot ---
    f_grid = font(SANS_B, 10)
    d.text((xL, y), "THE DAY IN STORIES", font=f_grid, fill=INK)
    rule(d, xL + 128, y + 5, CW - 128, BORDER, 1)
    y += 14
    cols, rows = 6, 1
    gap = 8
    card_w = (CW - (cols - 1) * gap) / cols
    card_h = 140
    grid_top = y
    f_chead = font(SERIF_B, 13)
    f_cdeck = font(SANS, 10)
    f_csrc = font(SANS_B, 7)
    f_pill2 = font(SANS_B, 8)
    for idx, card in enumerate(data["CARDS"]):
        r, c = divmod(idx, cols)
        cx = xL + c * (card_w + gap)
        cy = grid_top + r * (card_h + gap)
        d.rectangle([cx, cy, cx + card_w, cy + card_h], fill=CARD_BG, outline=BORDER)
        # icon band (top)
        draw_icon(d, card["ill"], (cx + 1, cy + 1, cx + card_w - 1, cy + 54))
        # number badge over icon
        badge(d, cx + 14, cy + 14, 10, card["n"], fill=RED)
        # status pill (top-right of icon)
        st = card["status"]
        tw = d.textlength(st, font=f_pill2)
        pw = tw + 8
        pill(d, cx + card_w - pw - 4, cy + 5, st, STATUS_COLORS[st], f_pill2, pad_x=4, pad_y=1)
        # headline (2 lines)
        lines = fit_lines(card["head"], f_chead, card_w - 12, 2, d)
        ty = cy + 60
        for ln in lines:
            d.text((cx + 6, ty), ln, font=f_chead, fill=INK)
            ty += 15
        # deck (2 lines)
        dlines = fit_lines(card["deck"], f_cdeck, card_w - 12, 2, d)
        for ln in dlines:
            d.text((cx + 6, ty), ln, font=f_cdeck, fill=INK_SOFT)
            ty += 12
        # source
        d.text((cx + 6, cy + card_h - 11), card["src"], font=f_csrc, fill=(140, 130, 115))
    # HOW SURE legend in the 6th slot (row 1, col 6)
    lx = xL + 5 * (card_w + gap)
    ly = grid_top
    d.rectangle([lx, ly, lx + card_w, ly + card_h], fill=NAVY_DARK, outline=NAVY_DARK)
    f_leg = font(SANS_B, 12)
    d.text((lx + 8, ly + 10), "HOW SURE?", font=f_leg, fill=(255, 215, 0))
    f_legt = font(SANS, 10)
    leg_items = [("REPORTED", "2+ outlets", GREEN), ("CLAIM", "one party", ORANGE), ("FORECAST", "not yet happened", BLUE)]
    ly2 = ly + 34
    for name, desc, col in leg_items:
        d.ellipse([lx + 8, ly2 + 2, lx + 18, ly2 + 12], fill=col, outline=(255, 255, 255))
        d.text((lx + 22, ly2), name, font=f_legt, fill=(255, 255, 255))
        d.text((lx + 22, ly2 + 13), desc, font=f_legt, fill=(200, 205, 215))
        ly2 += 34
    y = grid_top + rows * card_h + (rows - 1) * gap + 8

    # --- map (left) + ALSO (right) ---
    f_sec = font(SANS_B, 11)
    map_w = 300
    also_x = xL + map_w + 10
    also_w = xR - also_x
    sec_h = 190
    also = data["ALSO"]
    d.text((xL, y), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((also_x, y), f"ALSO ON THURSDAY  ·  {also[0][0]}–{also[-1][0]}", font=f_sec, fill=INK)
    y += 15
    pins = [(c["n"], c["pin"][0], c["pin"][1]) for c in data["LEADS"] + data["CARDS"]]
    draw_map(d, (xL, y, xL + map_w, y + sec_h), pins)
    # ALSO list: 2 columns, 10 + 9
    f_also = font(SANS, 11)
    f_alnum = font(SANS_B, 11)
    col_w = (also_w - 10) / 2
    row_h = 18
    for ci in range(2):
        chunk = also[ci * 10:(ci + 1) * 10]
        ax = also_x + ci * (col_w + 10)
        ay = y
        for item in chunk:
            n, region, field, text, status = item
            # status colour on the number
            col = STATUS_COLORS[status]
            d.text((ax, ay), str(n), font=f_alnum, fill=col)
            # text, truncated to column width
            tw_num = d.textlength(str(n) + "  ", font=f_alnum)
            lines = fit_lines(text, f_also, col_w - tw_num - 2, 1, d)
            d.text((ax + tw_num, ay), lines[0] if lines else "", font=f_also, fill=INK)
            ay += row_h
    y += sec_h + 8

    # --- VERDICT + MARKETS boxes ---
    box_h = 64
    half = (CW - 8) / 2
    d.rectangle([xL, y, xL + half, y + box_h], fill=NAVY_DARK, outline=NAVY_DARK)
    f_vh = font(SANS_B, 11)
    d.text((xL + 8, y + 6), "THE VERDICT", font=f_vh, fill=(255, 215, 0))
    f_vt = font(SANS, 11)
    vlines = fit_lines(data["VERDICT"].replace("THE VERDICT — ", ""), f_vt, half - 16, 3, d)
    vy = y + 22
    for ln in vlines:
        d.text((xL + 8, vy), ln, font=f_vt, fill=(255, 255, 255))
        vy += 14
    mx = xL + half + 8
    d.rectangle([mx, y, mx + half, y + box_h], fill=(245, 240, 228), outline=BORDER)
    d.text((mx + 8, y + 6), "MARKETS & MONEY", font=f_vh, fill=RED_DARK)
    mlines = fit_lines(data["MARKETS"].replace("MARKETS & MONEY — ", ""), f_vt, half - 16, 3, d)
    my = y + 22
    for ln in mlines:
        d.text((mx + 8, my), ln, font=f_vt, fill=INK)
        my += 14
    y += box_h + 8

    # --- DATE CHECK strip ---
    f_dc = font(SANS_B, 10)
    f_dct = font(SANS, 10)
    d.rectangle([xL, y, xR, y + 54], fill=(252, 240, 240), outline=RED)
    d.text((xL + 8, y + 5), "DATE CHECK", font=f_dc, fill=RED_DARK)
    dlines = fit_lines(data["DATECHECK"][1], f_dct, CW - 16, 2, d)
    dy = y + 19
    for ln in dlines:
        d.text((xL + 8, dy), ln, font=f_dct, fill=INK)
        dy += 11
    dlines = fit_lines(data["DATECHECK"][2] + "  " + data["DATECHECK"][3], f_dct, CW - 16, 1, d)
    d.text((xL + 8, dy), dlines[0] if dlines else "", font=f_dct, fill=INK_SOFT)
    y += 54 + 6

    # --- footer ---
    f_ft = font(SANS, 9)
    ft = (f"ONE DAY ON EARTH — Thursday 19 November 2026  ·  All {data['META']['stories']} stories happened, "
          f"or were first reported, on 19 November 2026  ·  Sources: Reuters · AP · AFP · Al Jazeera · BBC · ABC")
    tw = d.textlength(ft, font=f_ft)
    d.text(((W - tw) / 2, y), ft, font=f_ft, fill=(140, 130, 115))

    img.save(out_path, "PNG", optimize=True)
    return out_path

def main():
    data = load_data()
    render(data, os.path.join(HERE, "entry.png"))

if __name__ == "__main__":
    main()
