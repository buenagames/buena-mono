#!/usr/bin/env python3
"""Font-wide contour-winding normalization (BUENA-335 round 2).

Extends the containment rule proven on the 38 IPA capitals to every glyph:
a contour is a *hole* only if it is FULLY contained in another contour of the
same layer (tested on vertices + edge-sampled midpoints, pulled 0.5% toward
the centroid); partial overlaps and disjoint contours are *filled*. Desired
direction per contour index is decided ONCE on the Regular master, then every
master's contour is reversed if its own signed area disagrees — masters end
up direction-consistent without breaking fontmake's point-type alignment.

Convention: filled = positive signed area in the source (glyphsLib y-up
shoelace); cu2qu flips uniformly for TrueType output, so only relative
correctness and cross-master consistency matter.

Skips: component-only layers (they inherit their base glyph's fix), layers
whose contour count differs from Regular (reported), contours with <3 nodes.

Usage:
  python3 scripts/normalize-winding.py --dry-run
  python3 scripts/normalize-winding.py --apply
"""

import argparse
import statistics

import glyphsLib

GLYPHS_PATH = "sources/BuenaMono.glyphs"


def flatten(path):
    return [(n.position.x, n.position.y) for n in path.nodes]


def signed_area(poly):
    s = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x1 + (y - y1) * (x2 - x1) / (y2 - y1) > x:
                inside = not inside
    return inside


def sample_points(poly, per_edge=9):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    pts = []
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        for k in range(per_edge):
            t = k / (per_edge - 1)
            x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            pts.append((x + (cx - x) * 0.005, y + (cy - y) * 0.005))
    return pts


def fully_inside(inner, outer):
    return all(point_in_poly(p, outer) for p in sample_points(inner))


def desired_signs(layer):
    """True=filled(+), False=hole(-), None=skip, per contour index."""
    polys = [flatten(p) for p in layer.paths]
    out = []
    for i, poly in enumerate(polys):
        if len(poly) < 3:
            out.append(None)
            continue
        lvl = sum(1 for j, q in enumerate(polys)
                  if j != i and len(q) >= 3 and fully_inside(poly, q))
        out.append(lvl % 2 == 0)
    return out


def reverse_path(path):
    nodes = [(n.position.x, n.position.y, n.type, n.smooth) for n in path.nodes]
    rev = list(reversed(nodes))
    n = len(rev)
    rebuilt = []
    for i, (x, y, t, smooth) in enumerate(rev):
        if t == "offcurve":
            newtype = "offcurve"
        else:
            prev_t = rev[(i - 1) % n][2]
            newtype = "curve" if prev_t == "offcurve" else "line"
        node = glyphsLib.classes.GSNode((x, y), newtype)
        node.smooth = smooth
        rebuilt.append(node)
    path.nodes = rebuilt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.print_help()
        return

    print(f"loading {GLYPHS_PATH} ...")
    font = glyphsLib.GSFont(GLYPHS_PATH)
    master_ids = {m.id: m.name for m in font.masters}
    reg_id = next(m.id for m in font.masters if m.name == "Regular")

    total_flips = 0
    touched = {}
    skipped_mismatch = []
    for glyph in font.glyphs:
        reg_layer = next((l for l in glyph.layers if l.layerId == reg_id), None)
        if reg_layer is None or not reg_layer.paths:
            continue  # empty or component-only in Regular
        want = desired_signs(reg_layer)
        for layer in glyph.layers:
            if layer.layerId not in master_ids:
                continue
            if len(layer.paths) != len(want):
                skipped_mismatch.append(
                    f"{glyph.name}/{master_ids[layer.layerId]} "
                    f"({len(layer.paths)} vs {len(want)} contours)")
                continue
            for i, path in enumerate(layer.paths):
                if want[i] is None:
                    continue
                poly = flatten(path)
                if len(poly) < 3:
                    continue
                cur = signed_area(poly) > 0
                if cur != want[i]:
                    if args.apply:
                        reverse_path(path)
                    total_flips += 1
                    touched[glyph.name] = touched.get(glyph.name, 0) + 1

    print(f"contours to reverse: {total_flips} across {len(touched)} glyphs")
    if skipped_mismatch:
        print(f"skipped (contour-count mismatch vs Regular): {len(skipped_mismatch)}")
        for s in skipped_mismatch[:20]:
            print("  ", s)
    if touched:
        per = sorted(touched.values())
        print(f"flips per glyph: median {statistics.median(per)}, max {max(per)}")
    if args.apply:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")


if __name__ == "__main__":
    main()
