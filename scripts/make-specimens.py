#!/usr/bin/env python3
"""Generate README specimen images from the built variable font.

Usage: python3 scripts/make-specimens.py <font.ttf> <out_docs_dir>

Produces, in <out_docs_dir>:
  specimen.png                    hero (title, weight waterfall, ligatures, glyphs)
  stylistic-sets.png              ss01-ss12 default -> alternate
  character-set.png               glyph-coverage overview

Requires `hb-view` (harfbuzz) on PATH and Pillow.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image

def hb(font, text, size, variations, fg, bg, out, features=None):
    cmd = ["hb-view", "--font-size", str(size), "--variations", variations,
           "--foreground", fg, "--background", bg, "--margin", "0"]
    if features:
        cmd += ["--features", features]
    cmd += ["--output-file", out, font, text]
    subprocess.run(cmd, check=True)
    return Image.open(out).convert("RGBA")


def hero(font, tmp, outpath):
    FG, W, PAD = "EDEDED", 1680, 72
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
    imgs = [(hb(font, t, s, f"wght={w}", FG, "000000", f"{tmp}/hero_{i}.png"), g)
            for i, (t, w, s, g) in enumerate(lines)]
    width = max(W, max(im.width for im, _ in imgs) + 2 * PAD)
    height = PAD * 2 + sum(im.height + g for im, g in imgs)
    canvas = Image.new("RGB", (width, height), "#000000")
    y = PAD
    for im, g in imgs:
        y += g
        canvas.paste(im, (PAD, y), im)
        y += im.height
    canvas.save(outpath)


SS = [
    ("ss01", "Single-story a", "a"), ("ss02", "Descending f", "f"),
    ("ss03", "Tailed l", "l"), ("ss04", "Serifed i and j", "ij"),
    ("ss05", "Alternate g", "g"), ("ss06", "Alternate g (2)", "g"),
    ("ss07", "Serifed i", "i"), ("ss08", "Straight-tail y", "y"),
    ("ss09", "Curved-tail y", "y"), ("ss10", "Plain zero", "0"),
    ("ss11", "Dotted zero", "0"), ("ss12", "Alternate r", "r"),
    ("ss13", "Machine-readable", "=>"),
]


def stylistic_sets(font, tmp, outpath):
    FG, PAD, gsize, lsize, rowH, labelW = "EDEDED", 64, 60, 30, 92, 460
    rows = []
    for tag, label, ch in SS:
        rows.append((
            hb(font, f"{tag}   {label}", lsize, "wght=400", "A0A0A0", "000000", f"{tmp}/ss_{tag}_l.png"),
            hb(font, ch, gsize, "wght=400", FG, "000000", f"{tmp}/ss_{tag}_d.png"),
            hb(font, "→", round(gsize * 0.6), "wght=400", "6E6E6E", "000000", f"{tmp}/ss_{tag}_r.png"),
            hb(font, ch, gsize, "wght=400", FG, "000000", f"{tmp}/ss_{tag}_a.png", features=tag),
        ))
    canvas = Image.new("RGB", (1120, PAD * 2 + len(rows) * rowH), "#000000")
    y = PAD
    for lab, deflt, arr, alt in rows:
        cy = y + rowH // 2
        canvas.paste(lab, (PAD, cy - lab.height // 2), lab)
        gx = PAD + labelW
        canvas.paste(deflt, (gx, cy - deflt.height // 2), deflt)
        canvas.paste(arr, (gx + 100, cy - arr.height // 2), arr)
        canvas.paste(alt, (gx + 190, cy - alt.height // 2), alt)
        y += rowH
    canvas.save(outpath)


def charset(font, tmp, outpath):
    FG, PAD, size = "EDEDED", 64, 34
    NOLIG = "-calt,-liga,-dlig,-clig"  # show raw punctuation, not code ligatures
    lines = [
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", None),
        ("abcdefghijklmnopqrstuvwxyz", None),
        ("0123456789", None),
        ("ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜ", None),
        ("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ", None),
        ("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", None),
        ("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~", NOLIG),
        ("→←↑↓↔⇒⇐≠≤≥≈∑∏∫√∞±×÷", None),
        ("░▒▓█▀▄■□●○◆◇", None),
        ("== === != >= <= => -> <- |> <| ++ -- .= ...", None),
    ]
    line_h = round(size * 1.7)
    imgs = [hb(font, t, size, "wght=400", FG, "000000", f"{tmp}/cs_{i}.png", features=feat)
            for i, (t, feat) in enumerate(lines)]
    width = max(1200, max(im.width for im in imgs) + 2 * PAD)
    canvas = Image.new("RGB", (width, PAD * 2 + len(imgs) * line_h), "#000000")
    y = PAD
    for im in imgs:
        canvas.paste(im, (PAD, y), im)
        y += line_h
    canvas.save(outpath)


def main():
    font, docs = sys.argv[1], sys.argv[2]
    os.makedirs(docs, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        hero(font, tmp, os.path.join(docs, "specimen.png"))
        stylistic_sets(font, tmp, os.path.join(docs, "stylistic-sets.png"))
        # charset() superseded by docs/character-set-roman.py / -italic.py
    print(f"specimens written to {docs}")


if __name__ == "__main__":
    main()
