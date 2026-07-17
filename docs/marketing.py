# Generates a marketing-asset starter set into docs/marketing/ from the real
# variable font. Formats: social square, vertical story/Reel/Short, YouTube
# thumbnail, X/landscape card.  Run after `make build`:
#   $ python3 docs/marketing.py
#
# Shared brand system: black canvas, Show Syntax palette, Buena Mono. A small
# code-window motif is reused across templates.

import argparse
import os

from drawbot_skia.drawbot import *
from fontTools.ttLib import TTFont

FONT = "fonts/variable/BuenaMono-VF.ttf"
_tt = TTFont(FONT)
UPM = _tt["head"].unitsPerEm
ADV = _tt["hmtx"]["A"][0]


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))

BG, PANE, BORDER = hx("000000"), hx("0d0d0d"), hx("262626")
FG, MUTED, LN = hx("ededed"), hx("8a8a8a"), hx("4a4a4a")
TERRA, GREEN, BLUE, NUMc, COM = hx("d97757"), hx("10a37f"), hx("4285f4"), hx("4fa8ff"), hx("6e6e6e")


def charw(size):
    return size * ADV / UPM


def line(s, size, x, top, H, color=FG, wght=400, align="left", boxw=None):
    """Draw text; `top` = distance from the top edge. align left|center|right."""
    font(FONT); fontVariations(wght=wght); fontSize(size); fill(*color)
    w = len(s) * charw(size)
    if align == "center":
        x = (boxw - w) / 2 if boxw else x
    elif align == "right":
        x = (boxw - w) if boxw else x
    text(s, (x, H - top))


def rrect(x, y, w, h, r):
    p = BezierPath()
    p.moveTo((x + r, y)); p.lineTo((x + w - r, y)); p.arcTo((x + w, y), (x + w, y + r), r)
    p.lineTo((x + w, y + h - r)); p.arcTo((x + w, y + h), (x + w - r, y + h), r)
    p.lineTo((x + r, y + h)); p.arcTo((x, y + h), (x, y + h - r), r)
    p.lineTo((x, y + r)); p.arcTo((x, y), (x + r, y), r); p.closePath()
    return p


def code_window(x, top, w, h, H, size=30):
    """Small reusable code-window motif; (x, top) = top-left from top edge."""
    y = H - top - h
    fill(*PANE); stroke(*BORDER); strokeWidth(2); drawPath(rrect(x, y, w, h, 24)); stroke(None)
    for i, c in enumerate((hx("ff5f57"), hx("febc2e"), hx("28c840"))):
        fill(*c); oval(x + 34 + i * 34, y + h - 52, 16, 16)
    rows = [
        [("const", TERRA), (" g ", FG), ("=", FG), (" shape", BLUE), ("(", FG), ('"a"', GREEN), (");", FG)],
        [("x ", FG), (">=", TERRA), (" 0 ", FG), ("?", TERRA), (" x ", FG), (":", FG), (" -x", FG)],
        [("// ", COM), ("=> != >= -> ===", TERRA)],
    ]
    cw = charw(size)
    ty = top + 96
    for row in rows:
        cx = x + 40
        font(FONT); fontSize(size)
        for t, col in row:
            fill(*col); text(t, (cx, H - ty))
            cx += len(t) * cw
        ty += size * 1.5


def social_square(out):
    W = H = 1080
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena mono", 116, 0, 360, H, FG, align="center", boxw=W)
    line("a writer-first monospace typeface", 30, 0, 470, H, MUTED, align="center", boxw=W)
    line("0O 1lI  => != >= ->  ß ə ħ", 44, 0, 600, H, FG, align="center", boxw=W)
    fill(*TERRA); rect(W / 2 - 60, H - 700, 120, 5)
    line("5,080 glyphs · 971 languages", 26, 0, 900, H, MUTED, align="center", boxw=W)
    line("wght 100-800 · slnt 0 to -10° · OFL", 26, 0, 946, H, MUTED, align="center", boxw=W)
    saveImage(out)


def story(out):
    W, H = 1080, 1920
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena", 150, 0, 360, H, FG, align="center", boxw=W)
    line("mono", 150, 0, 520, H, FG, align="center", boxw=W)
    line("writer-first monospace", 32, 0, 640, H, MUTED, align="center", boxw=W)
    code_window(90, 820, 900, 470, H)
    line("free · open source", 34, 0, 1560, H, TERRA, align="center", boxw=W)
    line("5,080 glyphs · 971 languages", 28, 0, 1660, H, MUTED, align="center", boxw=W)
    line("buena-mono.buenalabs.io", 30, 0, 1780, H, FG, align="center", boxw=W)
    saveImage(out)


def youtube_thumb(out):
    W, H = 1280, 720
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena", 108, 80, 250, H, FG)
    line("mono", 108, 80, 372, H, FG)
    line("the monospace for", 34, 80, 468, H, MUTED)
    line("writers who code", 34, 80, 520, H, FG)
    fill(*TERRA); rect(80, H - 600, 90, 6)
    code_window(720, 150, 480, 420, H)
    saveImage(out)


def x_card(out):
    W, H = 1600, 900
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena mono", 120, 0, 320, H, FG, align="center", boxw=W)
    line("a writer-first monospace typeface", 34, 0, 430, H, MUTED, align="center", boxw=W)
    line("0O 1lI  => != >= ->  ∑ √ ≈  ß ə ħ", 46, 0, 580, H, FG, align="center", boxw=W)
    line("5,080 glyphs · 971 languages · wght 100-800 · slnt 0 to -10°",
         26, 0, 760, H, MUTED, align="center", boxw=W)
    saveImage(out)


def ig_portrait(out):
    W, H = 1080, 1350
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena mono", 104, 0, 300, H, FG, align="center", boxw=W)
    line("writer-first monospace", 30, 0, 400, H, MUTED, align="center", boxw=W)
    code_window(90, 520, 900, 470, H)
    line("free · open source · OFL", 30, 0, 1150, H, TERRA, align="center", boxw=W)
    line("5,080 glyphs · 971 languages", 26, 0, 1240, H, MUTED, align="center", boxw=W)
    saveImage(out)


def linkedin(out):
    W, H = 1200, 628
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena mono", 92, 0, 240, H, FG, align="center", boxw=W)
    line("a writer-first monospace typeface", 28, 0, 330, H, MUTED, align="center", boxw=W)
    fill(*TERRA); rect(W / 2 - 60, H - 400, 120, 5)
    line("5,080 glyphs · 971 languages · wght 100-800 · OFL", 24, 0, 470, H, MUTED, align="center", boxw=W)
    saveImage(out)


def youtube_banner(out):
    # 2560x1440; keep everything inside the TV-safe area (1546x423 centred).
    W, H = 2560, 1440
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena mono", 128, 0, 700, H, FG, align="center", boxw=W)
    line("a writer-first monospace typeface · free · open source", 30, 0, 800, H, MUTED, align="center", boxw=W)
    saveImage(out)


def app_icon(out):
    # 1024x1024 — mini code-window mark (echoes the CLI motif). iOS masks corners.
    W = H = 1024
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    tx, ty, ts = 120, 120, 784
    top = ty + ts                              # tile top edge (y-up)
    fill(*PANE); stroke(*BORDER); strokeWidth(6); drawPath(rrect(tx, ty, ts, ts, 150)); stroke(None)
    for i, c in enumerate((hx("ff5f57"), hx("febc2e"), hx("28c840"))):
        fill(*c); oval(tx + 78 + i * 70, top - 116, 52, 52)
    GRAY = hx("3a3a3a")
    def bar(x, t, w, h, col):                  # t = distance below tile top
        fill(*col); drawPath(rrect(x, top - t - h, w, h, h / 2))
    bar(tx + 90, 210, 200, 40, TERRA)          # keyword
    bar(tx + 90 + 230, 210, 230, 40, GRAY)     # identifier
    bar(tx + 170, 300, 190, 40, GRAY)          # indented line
    bar(tx + 170, 390, 150, 40, GRAY)
    fill(*TERRA); rect(tx + 170 + 180, top - 390 - 58, 46, 66)  # block cursor
    saveImage(out)


def iphone_screenshot(out):
    W, H = 1290, 2796
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("the monospace", 92, 100, 360, H, FG)
    line("for writers", 92, 100, 480, H, MUTED)
    line("who code.", 92, 100, 600, H, TERRA)
    code_window(95, 900, 1100, 1000, H, size=34)
    line("5,080 glyphs · 971 languages", 32, 0, 2180, H, FG, align="center", boxw=W)
    line("free · open source · OFL", 32, 0, 2280, H, TERRA, align="center", boxw=W)
    line("buena-mono.buenalabs.io", 34, 0, 2480, H, MUTED, align="center", boxw=W)
    saveImage(out)


def marketplace_feature(out):
    W, H = 1600, 1000
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena mono", 128, 0, 300, H, FG, align="center", boxw=W)
    line("AaBbCc 0123 => != >=", 72, 0, 470, H, FG, align="center", boxw=W)
    line("a writer-first monospace typeface", 32, 0, 620, H, MUTED, align="center", boxw=W)
    line("5,080 glyphs · 971 languages · wght 100-800 · slnt 0 to -10°", 26, 0, 780, H, MUTED, align="center", boxw=W)
    saveImage(out)


def web_hero(out):
    W, H = 1920, 1080
    newDrawing(); newPage(W, H); fill(*BG); rect(-2, -2, W + 2, H + 2)
    line("buena", 150, 130, 380, H, FG)
    line("mono", 150, 130, 540, H, FG)
    line("the monospace for writers who code", 34, 130, 650, H, MUTED)
    fill(*TERRA); drawPath(rrect(130, H - 820, 360, 90, 45))
    fill(*BG); font(FONT); fontVariations(wght=500); fontSize(34)
    text("Get it — free", (178, H - 782))
    code_window(1080, 250, 700, 580, H, size=32)
    saveImage(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="docs/marketing")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    d = args.outdir
    # social
    social_square(f"{d}/social-square.png")
    ig_portrait(f"{d}/ig-portrait.png")
    story(f"{d}/story-reel-short.png")
    x_card(f"{d}/x-card.png")
    linkedin(f"{d}/linkedin.png")
    # video / youtube
    youtube_thumb(f"{d}/youtube-thumbnail.png")
    youtube_banner(f"{d}/youtube-banner.png")
    # ASO: app store + marketplace + web
    app_icon(f"{d}/aso-app-icon.png")
    iphone_screenshot(f"{d}/aso-iphone-screenshot.png")
    marketplace_feature(f"{d}/aso-marketplace-feature.png")
    web_hero(f"{d}/aso-web-hero.png")
    print(f"marketing assets written to {d}")


if __name__ == "__main__":
    main()
