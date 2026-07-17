# Generates docs/social-preview.png — the 1280x640 GitHub social card.
# Run after `make build` (or with the committed fonts in fonts/variable/):
#   $ python3 docs/social-preview.py --output docs/social-preview.png
#
# Wordmark set in Buena Mono Regular; centred layout on black.

import argparse

from drawbot_skia.drawbot import *
from fontTools.ttLib import TTFont

WIDTH, HEIGHT = 1280, 640
FONT_PATH = "fonts/variable/BuenaMono-VF.ttf"

FG    = (0.93, 0.93, 0.93)   # #ededed
MUTED = (0.54, 0.54, 0.54)   # #8a8a8a

WORDMARK = "buena mono"
SUBTITLE = "a writer-first monospace typeface"
GLYPHS   = "0O  1lI  ⇒ ≠ ≥ →  ẞ ə ħ"
STATS    = "5,080 glyphs · 971 languages · wght 100–800 · slnt 0 to −10°"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", metavar="PNG", default="docs/social-preview.png")
    args = ap.parse_args()

    TTFont(FONT_PATH)  # validate the font path early

    newPage(WIDTH, HEIGHT)
    fill(0); rect(-2, -2, WIDTH + 2, HEIGHT + 2)
    font(FONT_PATH)
    cx = WIDTH / 2

    # wordmark — Buena Mono Regular (default instance, wght 400)
    fill(*FG); fontSize(128)
    text(WORDMARK, (cx, 392), align="center")

    # subtitle
    fill(*MUTED); fontSize(34)
    text(SUBTITLE, (cx, 300), align="center")

    # glyph showcase row
    fill(*FG); fontSize(52)
    text(GLYPHS, (cx, 178), align="center")

    # stats line
    fill(*MUTED); fontSize(28)
    text(STATS, (cx, 78), align="center")

    saveImage(args.output)
    print("DrawBot: social-preview.png done")


if __name__ == "__main__":
    main()
