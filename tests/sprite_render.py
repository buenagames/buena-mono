#!/usr/bin/env python3
"""sprite_render.py — render the TUI specimen to a PNG with the real font.

Line-height == font size (1.0) so box-drawing connects vertically. The PNG is a
diffable regression artifact: render on two font versions and compare.

Usage: python3 tests/sprite_render.py [--out FILE.png] [--size 22]
Run from the repo root (needs fonts/variable/BuenaMono-VF.ttf).
"""
import argparse

from drawbot_skia.drawbot import *
from fontTools.ttLib import TTFont

from sprite_specimen import get_specimen  # same directory

FONT = "fonts/variable/BuenaMono-VF.ttf"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tests/sprite-specimen.png")
    ap.add_argument("--size", type=int, default=22)
    args = ap.parse_args()

    lines = get_specimen().rstrip("\n").split("\n")
    tt = TTFont(FONT)
    upm = tt["head"].unitsPerEm
    adv = tt["hmtx"]["A"][0]
    S = args.size
    char_w = S * adv / upm
    line_h = S  # 1.0 leading — box joins must touch
    M = 44
    cols = max(len(l) for l in lines)
    W = int(M * 2 + cols * char_w)
    H = int(M * 2 + len(lines) * line_h)

    newPage(W, H)
    fill(0)
    rect(-2, -2, W + 2, H + 2)
    fill(0.93, 0.93, 0.93)
    font(FONT)
    fontSize(S)
    y = H - M - S
    for ln in lines:
        text(ln, (M, y))
        y -= line_h
    saveImage(args.out)
    print(f"rendered {args.out} ({W}x{H})")


if __name__ == "__main__":
    main()
