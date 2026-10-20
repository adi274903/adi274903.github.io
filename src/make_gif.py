#!/usr/bin/env python3
"""Draws src/assets/how-it-works.gif: the Ask page pipeline for one example question, frame by frame (Pillow).
Colours match the site's dark theme. Run once; the build copies the GIF next to the page."""
import re, pathlib
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(__file__).resolve().parent / "assets" / "how-it-works.gif"
F = "/usr/share/fonts/google-noto/"
SANS, SANSB = F + "NotoSans-Regular.ttf", F + "NotoSans-SemiBold.ttf"
MONO, MONOB = F + "NotoSansMono-Regular.ttf", F + "NotoSansMono-SemiBold.ttf"
BG, PANEL, LINE, INK, MUT, ACC, HOT = "#0b0d12", "#12151d", "#2a3142", "#eceef4", "#a0a9bb", "#86a8ff", "#ffc46b"
W, H = 960, 470
S = 2                                     # draw at 2x, then downscale for smooth edges
font = lambda p, n: ImageFont.truetype(p, n * S)

QUESTION = "What did he do at EMMA AI?"
ANSWER = "Raised physician-rated accuracy and completeness 25% in a resident podcast platform by rebuilding Gemini and pgvector RAG retrieval over a 20-context corpus, validated by 2 physician surveys and 48 students."
STEPS = [("01 · QUESTION", ["What did he do", "at EMMA AI?"]), ("02 · READ IT", ["tokens: emma, ai", "intent: describe", "typos fixed"]),
         ("03 · FIND SECTION", ["name match: EMMA", "metadata: project", "health · AI · 2025"]), ("04 · RANK LINES", None),
         ("05 · QUOTE", ["best-matching line,", "numbers in bold,", "+ source line"])]
BOX_W, BOX_H, GAP, TOP, X0 = 166, 150, 22, 96, 28


def text(d, xy, s, f, fill):
    d.text((xy[0] * S, xy[1] * S), s, font=f, fill=fill)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle([v * S for v in box], r * S, fill=fill, outline=outline, width=width * S)


def rich(d, x, y, s, upto, maxw):
    """Typed text with metrics in bold; wraps at maxw. upto = number of characters revealed."""
    f, fb = font(SANS, 15), font(SANSB, 15)
    cx, cy, shown = x, y, 0
    for word in s.split(" "):
        w = word + " "
        if shown >= upto:
            break
        part = w[: max(0, upto - shown)]
        isnum = bool(re.search(r"\d", word))
        fw = (fb if isnum else f)
        width = d.textlength(w, font=fw) / S
        if cx + width > x + maxw:
            cx, cy = x, cy + 24
        text(d, (cx, cy), part, fw, INK if isnum else INK)
        cx += d.textlength(part, font=fw) / S
        shown += len(w)


def frame(t):
    img = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(img)
    text(d, (28, 22), "ASK MY RECORD  ·  HOW IT WORKS", font(MONOB, 12), ACC)
    # question bar (typed)
    rrect(d, (28, 46, W - 28, 84), 12, fill=PANEL, outline=LINE)
    n = min(len(QUESTION), max(0, (t - 2) * 2))
    text(d, (46, 55), QUESTION[:n] + ("▌" if t < 30 and t % 6 < 3 else ""), font(SANS, 16), INK)
    # steps
    active = -1 if t < 12 else max(0, min(4, int((t - 18 + 6.5) // 13)))
    packet = None
    for i, (title, lines) in enumerate(STEPS):
        x = X0 + i * (BOX_W + GAP)
        lit = i == active
        rrect(d, (x, TOP, x + BOX_W, TOP + BOX_H), 14, fill=PANEL if lit else BG, outline=ACC if lit else LINE, width=2 if lit else 1)
        text(d, (x + 14, TOP + 14), title, font(MONOB, 11), ACC if lit else MUT)
        col = INK if lit else MUT
        if lines:
            for k, ln in enumerate(lines):
                text(d, (x + 14, TOP + 44 + k * 22), ln, font(SANS, 14), col)
        else:
            grow = 1.0 if t >= 64 else max(0.0, min(1.0, (t - 50) / 10)) if i <= active else 0.0
            for k, sc in enumerate((0.92, 0.34, 0.18)):
                yy = TOP + 50 + k * 28
                rrect(d, (x + 14, yy, x + BOX_W - 14, yy + 12), 6, fill=BG, outline=LINE)
                rrect(d, (x + 14, yy, x + 14 + (BOX_W - 28) * sc * grow, yy + 12), 6, fill=ACC if k == 0 else "#5d6679")
            text(d, (x + 14, TOP + BOX_H - 24), "similarity", font(MONO, 11), MUT)
        if i < 4:
            ax = x + BOX_W + 3
            d.line([ax * S, (TOP + BOX_H / 2) * S, (ax + GAP - 8) * S, (TOP + BOX_H / 2) * S], fill="#6b7488", width=2 * S)
            d.polygon([((ax + GAP - 8) * S, (TOP + BOX_H / 2 - 4) * S), ((ax + GAP - 8) * S, (TOP + BOX_H / 2 + 4) * S), ((ax + GAP - 1) * S, (TOP + BOX_H / 2) * S)], fill="#6b7488")
    # packet travels left to right while the steps advance
    ty = TOP + BOX_H + 14
    d.line([(X0 + BOX_W / 2) * S, ty * S, (X0 + 4 * (BOX_W + GAP) + BOX_W / 2) * S, ty * S], fill=LINE, width=2 * S)
    if 18 <= t <= 70:
        px = X0 + BOX_W / 2 + (t - 18) / 52 * (4 * (BOX_W + GAP))
        r = 7 * S
        d.ellipse([px * S - r, ty * S - r, px * S + r, ty * S + r], fill=HOT)
    # answer card
    rrect(d, (28, 282, W - 28, 450), 14, fill=PANEL, outline=LINE)
    text(d, (46, 296), "EMMA AI CLINICAL EDUCATION PLATFORM", font(MONOB, 11), ACC)
    if t >= 72:
        rich(d, 46, 328, ANSWER, int((t - 72) * 9), W - 120)
    if t >= 90:
        text(d, (46, 420), "SOURCE LINE, QUOTED FROM MY RECORD   ·   same question, same answer, every time", font(MONOB, 10), MUT)
    return img.resize((W, H), Image.LANCZOS)


frames = [frame(t) for t in range(0, 104, 2)]
pal = [f.quantize(colors=24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
OUT.parent.mkdir(exist_ok=True)
dur = [120] * (len(pal) - 1) + [3000]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=dur, loop=0, optimize=True, disposal=1)
frames[-1].save(OUT.with_suffix(".last.png"))
frames[20].save(OUT.with_suffix(".mid.png"))
print(OUT, OUT.stat().st_size // 1024, "KB,", len(pal), "frames")
