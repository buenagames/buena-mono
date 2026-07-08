#!/usr/bin/env python3
"""Anchor-height normalization (BUENA-335: stacked-mark collisions).

Root cause of the collidoscope findings: `top`/`bottom` anchors sit at the
NOMINAL metrics (x-height 524 / cap 699 / ascender 729 / baseline 0) in every
master, but the heavy masters' flat letter tops actually reach beyond them
(x: Thin 508 · Regular 524 · Bold 543 · ExtraBold 537), so combining marks
physically overlap their bases at Bold/ExtraBold. Precomposed accented
glyphs additionally keep their anchor UNDER the baked accents (ế ink to 905,
anchor 524), so a stacked mark lands on the accent.

Fix, per master and per glyph:
- class anchors (y == 524/699/729 upright equivalents) → the master's
  measured flat ink top for that class ('x' / 'H' / 'l')
- any glyph whose ink extends > LIFT_THRESHOLD above the class height →
  anchor at its own ink top (stack above the baked accents)
- `bottom` mirrored: baseline-class stays at the measured flat bottom;
  glyphs with ink < −LIFT_THRESHOLD (ɖ tails, baked below-marks) get the
  anchor at their ink bottom
- italic masters shear anchor x by Δx = SHEAR · Δy (measured 0.1771)

Round-letter overshoot (≤ threshold) intentionally keeps the class height —
marks tuck over round tops exactly as the Regular design does.

Usage:
  python3 scripts/normalize-anchors.py --dry-run | --apply
"""

import argparse

import glyphsLib

GLYPHS_PATH = "sources/BuenaMono.glyphs"
LIFT_THRESHOLD = 40
SHEAR = 31.0 / 175.0  # measured from H/x anchor x-positions in italic masters
CLASS_CPS = {524: 0x78, 699: 0x48, 729: 0x6C}  # x, H, l


def ink_bounds(layer):
    ys = [n.position.y for p in layer.paths for n in p.nodes]
    return (min(ys), max(ys)) if ys else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.print_help()
        return

    font = glyphsLib.GSFont(GLYPHS_PATH)
    masters = {m.id: m.name for m in font.masters}
    by_uni = {}
    for g in font.glyphs:
        if g.unicode:
            by_uni[int(g.unicode, 16)] = g

    # measured flat class heights per master
    flat_top = {}   # (master_id, nominal_y) -> measured ink top
    flat_bottom = {}
    for mid in masters:
        for nominal, cp in CLASS_CPS.items():
            layer = next(l for l in by_uni[cp].layers if l.layerId == mid)
            flat_top[(mid, nominal)] = ink_bounds(layer)[1]
        layer = next(l for l in by_uni[0x78].layers if l.layerId == mid)
        flat_bottom[mid] = ink_bounds(layer)[0]  # flat baseline (should be 0)

    moved = {"class": 0, "lift-top": 0, "lift-bottom": 0}
    touched = set()
    for g in font.glyphs:
        for layer in g.layers:
            if layer.layerId not in masters:
                continue
            bounds = ink_bounds(layer)
            if bounds is None:
                continue  # component-only layers carry no path ink to measure
            ymin, ymax = bounds
            italic = "Italic" in masters[layer.layerId]
            for a in layer.anchors:
                y0 = a.position.y
                new_y = None
                kind = None
                if a.name == "top":
                    base = flat_top.get((layer.layerId, round(y0)))
                    if base is not None:
                        new_y, kind = base, "class"
                    ref = new_y if new_y is not None else y0
                    if ymax > ref + LIFT_THRESHOLD:
                        new_y, kind = ymax, "lift-top"
                elif a.name == "bottom":
                    if round(y0) == 0:
                        new_y, kind = flat_bottom[layer.layerId], "class"
                    ref = new_y if new_y is not None else y0
                    if ymin < ref - LIFT_THRESHOLD:
                        new_y, kind = ymin, "lift-bottom"
                if new_y is None or abs(new_y - y0) < 0.6:
                    continue
                dx = SHEAR * (new_y - y0) if italic else 0.0
                if args.apply:
                    a.position = (a.position.x + dx, new_y)
                moved[kind] += 1
                touched.add(g.name)

    print(f"anchor moves: {moved}  across {len(touched)} glyphs")
    if args.apply:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")


if __name__ == "__main__":
    main()
