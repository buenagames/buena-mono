#!/usr/bin/env python3
"""Generate README specimen images from the built variable font.

Usage: python3 scripts/make-specimens.py <font.ttf> <out_docs_dir>

Produces, in <out_docs_dir>:
  specimen.png                    hero (title, weight waterfall, ligatures, glyphs)
  use-{regular,bold,italic}-{light,dark}.png   prose "in use" panels

Requires `hb-view` (harfbuzz) on PATH and Pillow. Mixed-style prose is composited
with a space-layer technique so weights/slants stay aligned on the monospace grid.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image

ADVANCE = 618  # UPM 1000 -> monospace cell = size * 618/1000


def hb(font, text, size, variations, fg, bg, out):
    subprocess.run(
        ["hb-view", "--font-size", str(size), "--variations", variations,
         "--foreground", fg, "--background", bg, "--margin", "0",
         "--output-file", out, font, text],
        check=True)
    return Image.open(out).convert("RGBA")


def hero(font, tmp, outpath):
    FG, BG, W, PAD = "111111", "ffffff", 1680, 72
    # (text, wght, size, gap_before)
    lines = [
        ("Buena Mono", 620, 132, 0),
        ("Writer-first monospace · weight 100–800 · slant 0 to −10°", 400, 34, 34),
        ("Sphinx of black quartz, judge my vow", 100, 44, 42),
        ("Sphinx of black quartz, judge my vow", 300, 44, 10),
        ("Sphinx of black quartz, judge my vow", 500, 44, 10),
        ("Sphinx of black quartz, judge my vow", 700, 44, 10),
        ("Sphinx of black quartz, judge my vow", 800, 44, 10),
        ("const inc = (x) => x >= 0 ? x + 1 : x;  a != b", 460, 44, 44),
        ("AÀÇ gβ Дж 0123 @#$€ →≠≈∑ ░▒▓█ (){}[]", 460, 46, 30),
    ]
    imgs = []
    for i, (t, w, s, g) in enumerate(lines):
        imgs.append((hb(font, t, s, f"wght={w}", FG, "ffffff", f"{tmp}/hero_{i}.png"), g))
    width = max(W, max(im.width for im, _ in imgs) + 2 * PAD)
    height = PAD * 2 + sum(im.height + g for im, g in imgs)
    canvas = Image.new("RGB", (width, height), "#ffffff")
    y = PAD
    for im, g in imgs:
        y += g
        canvas.paste(im, (PAD, y), im)
        y += im.height
    canvas.save(outpath)


ESSAY = [
    "Buena Mono is a writer-first monospace. It keeps the",
    "steady rhythm of a fixed grid — every glyph one width",
    "— while softening its shapes enough to read easily",
    "across long passages of prose. Weight ranges from a",
    "hairline thin to a solid extrabold, and a ten-degree",
    "slant gives the family a true, unhurried italic voice.",
]
EMPH = {  # combo -> (emphasised substrings, style)
    "regular": ([], None),
    "bold": (["Buena Mono", "extrabold"], "bold"),
    "italic": (["writer-first monospace.", "unhurried italic voice."], "italic"),
}
VAR = {"reg": "wght=400", "bold": "wght=700", "italic": "wght=400,slnt=-10"}
BGS = {"light": ("ffffff", "111111"), "dark": ("14161a", "e8e8e8")}


def essay_panel(font, tmp, combo, bg, outpath):
    subs, est = EMPH[combo]
    bgc, fg = BGS[bg]
    size, pad = 38, 64
    line_h = round(size * 1.72)
    width = round(max(len(l) for l in ESSAY) * size * ADVANCE / 1000.0) + 2 * pad
    height = pad * 2 + len(ESSAY) * line_h
    canvas = Image.new("RGBA", (width, height), "#" + bgc + "ff")
    for li, line in enumerate(ESSAY):
        st = ["reg"] * len(line)
        for sub in subs:
            i = line.find(sub)
            while i != -1:
                for k in range(i, i + len(sub)):
                    st[k] = est
                i = line.find(sub, i + 1)
        y = pad + li * line_h
        for style in set(st):
            layer = "".join(c if st[i] == style else " " for i, c in enumerate(line))
            if not layer.strip():
                continue
            im = hb(font, layer, size, VAR[style], fg, "00000000",
                    f"{tmp}/e_{combo}_{bg}_{li}_{style}.png")
            canvas.paste(im, (pad, y), im)
    canvas.convert("RGB").save(outpath)


def main():
    font, docs = sys.argv[1], sys.argv[2]
    os.makedirs(docs, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        hero(font, tmp, os.path.join(docs, "specimen.png"))
        for combo in EMPH:
            for bg in BGS:
                essay_panel(font, tmp, combo, bg,
                            os.path.join(docs, f"use-{combo}-{bg}.png"))
    print(f"specimens written to {docs}")


if __name__ == "__main__":
    main()
