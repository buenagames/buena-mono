#!/usr/bin/env python3
"""Fix contour winding on the 38 IPA/African uppercase letters (and, by
regeneration, their .smcp derivatives).

Several of these rare capitals (Ɇ Ⱥ Ɍ Ꭓ ...) carry stroke-overlay or outer
contours wound in the hole direction, so nonzero rendering cancels where they
overlap (visible checkerboard/spur artifacts in the shipped font).

Rule: a contour's containment depth (how many other contours enclose a point
inside it, even-odd) decides its direction — depth even = filled (positive
signed area, this font's convention), depth odd = hole (negative). Mismatched
contours are reversed in place (node order reversal preserves node counts, so
interpolation compatibility is unaffected).

Usage:
  python3 scripts/fix-winding-uc-smcp.py --dry-run   # report only
  python3 scripts/fix-winding-uc-smcp.py --apply
"""

import argparse

import glyphsLib

GLYPHS_PATH = "sources/BuenaMono.glyphs"

UC_CPS = [0x0186, 0x0190, 0x0181, 0x018A, 0x0197, 0x0196, 0x019D, 0x01B2,
          0x0244, 0xA78B, 0x01B3, 0x0194, 0x0189, 0x0198, 0x01B1, 0x01B7,
          0x01EE, 0x2C6D, 0xA7AA, 0x0241, 0x024C, 0x01AE, 0x0245, 0x0222,
          0x0193, 0xA7B4, 0x0220, 0x0246, 0x024A, 0xA78D, 0x2C64, 0x01A6,
          0xA7B2, 0x2C63, 0x2C60, 0x023A, 0xA7B6, 0xA7B3]


def flatten(path):
    """Contour -> polygon vertices (control polygon is adequate for the
    depth/area sign tests on these shapes)."""
    return [(n.position.x, n.position.y) for n in path.nodes]


def signed_area(poly):
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def point_in_poly(pt, poly):
    """Even-odd ray cast."""
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xin > x:
                inside = not inside
    return inside


def interior_point(poly):
    """A point inside the polygon (even-odd sense)."""
    n = len(poly)
    cx = sum(p[0] for p in poly) / n
    cy = sum(p[1] for p in poly) / n
    if point_in_poly((cx, cy), poly):
        return (cx, cy)
    for step in range(1, n):
        for i in range(n):
            j = (i + step) % n
            mx = (poly[i][0] + poly[j][0]) / 2
            my = (poly[i][1] + poly[j][1]) / 2
            if point_in_poly((mx, my), poly):
                return (mx, my)
    return (cx, cy)  # degenerate; give up gracefully


def reverse_path(path):
    """Reverse contour direction in place, Glyphs node semantics.

    Node list is a cycle where each node's type describes the segment that
    ENDS at it. After reversing the cycle, on-curve types are re-derived
    from what now precedes each node: offcurves ahead of an on-curve node
    make it 'curve', otherwise 'line'.
    """
    nodes = [(n.position.x, n.position.y, n.type, n.smooth) for n in path.nodes]
    rev = list(reversed(nodes))
    n = len(rev)
    newnodes = []
    for i, (x, y, t, smooth) in enumerate(rev):
        if t == "offcurve":
            newtype = "offcurve"
        else:
            prev_t = rev[(i - 1) % n][2]
            newtype = "curve" if prev_t == "offcurve" else "line"
        newnodes.append((x, y, newtype, smooth))
    rebuilt = []
    for x, y, t, smooth in newnodes:
        node = glyphsLib.classes.GSNode((x, y), t)
        node.smooth = smooth
        rebuilt.append(node)
    path.nodes = rebuilt


def fix_layer(layer, label, report, apply_fix):
    polys = [flatten(p) for p in layer.paths]
    changed = 0
    for i, path in enumerate(layer.paths):
        if len(polys[i]) < 3:
            continue
        pt = interior_point(polys[i])
        depth = sum(1 for j, q in enumerate(polys)
                    if j != i and point_in_poly(pt, q))
        want_filled = depth % 2 == 0
        is_filled = signed_area(polys[i]) > 0
        if want_filled != is_filled:
            report.append(f"  {label} path{i}: depth={depth} "
                          f"area={'+' if is_filled else '-'} -> reverse")
            if apply_fix:
                reverse_path(path)
            changed += 1
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.print_help()
        return

    font = glyphsLib.GSFont(GLYPHS_PATH)
    master_ids = {m.id: m.name for m in font.masters}
    by_uni = {}
    for g in font.glyphs:
        if g.unicode:
            by_uni[int(g.unicode, 16)] = g

    total = 0
    report = []
    touched = set()
    for cp in UC_CPS:
        g = by_uni.get(cp)
        if g is None:
            print(f"MISSING U+{cp:04X}")
            continue
        for layer in g.layers:
            if layer.layerId not in master_ids:
                continue
            n = fix_layer(layer, f"{g.name}/{master_ids[layer.layerId]}",
                          report, args.apply)
            if n:
                touched.add(g.name)
                total += n

    print("\n".join(report))
    print(f"\n{total} contours reversed across {len(touched)} glyphs: "
          f"{sorted(touched)}")
    if args.apply and total:
        # drop the derived .smcp copies; regenerate after with add-smcp-scaled
        stale = [f"{name}.smcp" for name in touched]
        removed = []
        for name in stale:
            if font.glyphs[name] is not None:
                del font.glyphs[name]
                removed.append(name)
        print(f"deleted stale derivatives: {removed}")
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")


if __name__ == "__main__":
    main()
