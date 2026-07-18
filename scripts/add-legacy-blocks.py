#!/usr/bin/env python3
"""add-legacy-blocks.py — generate Legacy Computing sextants + octants (BUENA-345).

Sextants (U+1FB00-1FB3B, 60) and Block Octants (U+1CD00-1CDE5, 230) are pure
geometric block graphics: each codepoint's Unicode name (BLOCK SEXTANT-135,
BLOCK OCTANT-2468) lists exactly which subcells are filled. We generate solid
rectangles on the SAME cell as Buena's full/left/right block (x 9-609, split at
309; y -300..900), row-merged into minimal contours, identical across all 8
masters (block graphics are weight-invariant), so they tile seamlessly with the
existing █ ▌ ▐ set.

    python3 scripts/add-legacy-blocks.py --preview out.png   # render a sample, no source change
    python3 scripts/add-legacy-blocks.py --dry-run           # report what would be added
    python3 scripts/add-legacy-blocks.py --apply             # write sources/BuenaMono.glyphs
"""
import argparse
import os
import re

from fontTools import unicodedata as fud

GLYPHS_PATH = "sources/BuenaMono.glyphs"

# Cell = Buena's full-block cell (matches █ U+2588, ▌ U+258C, ▐ U+2590).
XL, XM, XR = 9, 309, 609          # left edge / column split / right edge
YB, YT = -300, 900                # bottom / top (1200 tall)
XCOL = {"L": (XL, XM), "R": (XM, XR), "F": (XL, XR)}
SEXT_ROWS = [(500, 900), (100, 500), (-300, 100)]                 # cells (1,2)(3,4)(5,6)
OCT_ROWS = [(600, 900), (300, 600), (0, 300), (-300, 0)]         # (1,2)(3,4)(5,6)(7,8)


def scan(a, b, kind):
    out = {}
    for cp in range(a, b + 1):
        try:
            m = re.match(rf"BLOCK {kind}-(\d+)$", fud.name(chr(cp)))
        except Exception:
            continue
        if m:
            out[cp] = set(int(d) for d in m.group(1))
    return out


def mapping():
    m = [(cp, cells, SEXT_ROWS) for cp, cells in sorted(scan(0x1FB00, 0x1FBFF, "SEXTANT").items())]
    m += [(cp, cells, OCT_ROWS) for cp, cells in sorted(scan(0x1CC00, 0x1CEBF, "OCTANT").items())]
    return m


def rects(cells, rows):
    """Row-code the grid, vertically merge equal codes → minimal rectangles."""
    coded = []  # (ylo, yhi, code) top->bottom
    for i, (ylo, yhi) in enumerate(rows):
        left, right = (2 * i + 1) in cells, (2 * i + 2) in cells
        code = "F" if left and right else "L" if left else "R" if right else None
        if code:
            coded.append((ylo, yhi, code))
    merged, i = [], 0
    while i < len(coded):
        ylo, yhi, code = coded[i]
        j = i + 1
        while j < len(coded) and coded[j][2] == code and coded[j][1] == ylo:
            ylo = coded[j][0]; j += 1     # rows are top->bottom, so next row's yhi == this ylo
        merged.append((ylo, yhi, code)); i = j
    out = []
    for ylo, yhi, code in merged:
        x0, x1 = XCOL[code]
        out.append((x0, x1, ylo, yhi))
    return out


def preview(out_png):
    from PIL import Image, ImageDraw
    m = mapping()
    # sample: 32 sextants + 64 octants
    sample = m[:32] + m[60:60 + 64]
    cols, cell = 24, 46
    rows = (len(sample) + cols - 1) // cols
    W, H = cols * cell, rows * cell
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    sx = (cell - 8) / (XR - XL); sy = (cell - 8) / (YT - YB)
    for k, (cp, cells, rws) in enumerate(sample):
        ox = (k % cols) * cell + 4; oy = (k // cols) * cell + 4
        for x0, x1, y0, y1 in rects(cells, rws):
            px0 = ox + (x0 - XL) * sx; px1 = ox + (x1 - XL) * sx
            py0 = oy + (YT - y1) * sy; py1 = oy + (YT - y0) * sy   # flip y
            d.rectangle([px0, py0, px1, py1], fill=(237, 237, 237))
    img.save(out_png)
    print(f"preview ({len(sample)} glyphs) -> {out_png}")


def apply(dry):
    import glyphsLib
    from glyphsLib.classes import GSGlyph, GSLayer, GSPath, GSNode
    font = glyphsLib.load(open(GLYPHS_PATH))
    mids = [m.id for m in font.masters]
    have = {g.name for g in font.glyphs}
    m = mapping()
    added = 0
    for cp, cells, rws in m:
        name = f"u{cp:04X}"
        if name in have:
            continue
        rs = rects(cells, rws)
        if dry:
            added += 1
            continue
        g = GSGlyph(name)
        g.unicode = f"{cp:04X}"
        g.category, g.subCategory = "Symbol", "Geometry"
        g.export = True
        for mid in mids:
            L = GSLayer(); L.layerId = mid; L.width = 618
            for x0, x1, y0, y1 in rs:
                p = GSPath(); p.closed = True
                for px, py in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
                    p.nodes.append(GSNode(position=(px, py), type="line"))
                L.paths.append(p)
            g.layers.append(L)
        font.glyphs.append(g)
        added += 1
    print(f"{'would add' if dry else 'added'} {added} glyphs "
          f"(60 sextants U+1FB00-1FB3B + 230 octants U+1CD00-1CDE5)")
    if not dry:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}\nNEXT: make export-ufo && make build  (then python3 tests/sprite_coverage.py)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", metavar="PNG")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if args.preview:
        preview(args.preview)
    elif args.apply:
        apply(dry=False)
    else:
        apply(dry=True)


if __name__ == "__main__":
    main()
