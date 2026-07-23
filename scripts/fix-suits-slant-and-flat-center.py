#!/usr/bin/env python3
"""BUENA-349 Tier-3 + BUENA-348 Tier-1 — two small dingbat fixes.

349: the 4 FILLED card suits (♠♣♥♦, U+2660/2663/2665/2666) shear under the
     slnt axis, unlike the dice, stars, and the outline/white suits (which are
     pinned upright). Pin them upright by replacing each filled suit's italic-
     master layer outlines with its upright-master outlines (Thin→Thin Italic,
     Regular→Regular Italic, Bold→Bold Italic, ExtraBold→ExtraBold Italic).
     This is exactly what the white suits already do.

348: the flat ♭ (U+266D) is horizontally off-center (x-center ~330 vs the 309
     cell midline; ♮/♯ are already at 309). Recenter it to 309 per master.
     (The proposed "baseline drop" for accidentals was dropped after visual
     verification — they're cap-band-centered and read correctly inline; a drop
     would push them too low against capitals.)

    python3 scripts/fix-suits-slant-and-flat-center.py --dry-run
    python3 scripts/fix-suits-slant-and-flat-center.py --apply
"""
import argparse
import glyphsLib
from glyphsLib.classes import GSPath, GSNode

GLYPHS_PATH = "sources/BuenaMono.glyphs"
FILLED_SUITS = [0x2660, 0x2663, 0x2665, 0x2666]
FLAT = 0x266D
CELL_MID = 309
PAIRS = [("Thin", "Thin Italic"), ("Regular", "Regular Italic"),
         ("Bold", "Bold Italic"), ("ExtraBold", "ExtraBold Italic")]


def by_cp(font, cp):
    for g in font.glyphs:
        if g.unicode and int(g.unicode, 16) == cp:
            return g
    return None


def clone_paths(src_layer):
    out = []
    for p in src_layer.paths:
        np = GSPath()
        np.closed = p.closed
        for n in p.nodes:
            np.nodes.append(GSNode(position=(n.position.x, n.position.y),
                                   type=str(n.type)))
        out.append(np)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    font = glyphsLib.load(open(GLYPHS_PATH))
    mids = {m.id: m.name for m in font.masters}
    name2layer = lambda g: {mids[L.layerId]: L for L in g.layers if L.layerId in mids}

    # 349 — pin filled suits upright
    print("349: pin filled suits upright (copy upright layer -> italic layer)")
    for cp in FILLED_SUITS:
        g = by_cp(font, cp)
        lm = name2layer(g)
        for up, it in PAIRS:
            src, dst = lm[up], lm[it]
            same_before = ([(n.position.x, n.position.y) for p in src.paths for n in p.nodes]
                           == [(n.position.x, n.position.y) for p in dst.paths for n in p.nodes])
            if a.apply:
                dst.paths = clone_paths(src)
                dst.width = src.width
        print(f"  U+{cp:04X} {g.name:10} {'pinned 4 italic layers' if a.apply else 'would pin 4 italic layers'}")

    # 348 — recenter flat horizontally to 309
    print(f"348: recenter flat U+{FLAT:04X} to x-center {CELL_MID}")
    g = by_cp(font, FLAT)
    for name, L in name2layer(g).items():
        xs = [n.position.x for p in L.paths for n in p.nodes]
        center = (min(xs) + max(xs)) / 2
        dx = CELL_MID - center
        if a.apply:
            for p in L.paths:
                for n in p.nodes:
                    n.position = (n.position.x + dx, n.position.y)
        print(f"  {name:16} center {center:.1f} -> {CELL_MID} (dx {dx:+.1f})")

    if a.apply:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")
    else:
        print("(dry-run — no changes written)")


if __name__ == "__main__":
    main()
