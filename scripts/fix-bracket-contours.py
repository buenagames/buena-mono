#!/usr/bin/env python3
"""BUENA-346 follow-up — canonical contour counts for the new brackets.

v1.228 built the corner half-brackets ⸢⸣⸤⸥ (U+2E22–25) and double square
brackets ⟦⟧ (U+27E6–27E7) as unions of disjoint rectangles:

    ⸢⸣⸤⸥  arm rect + stem rect            → 2 contours (canonical: 1, an L)
    ⟦⟧    stem + top arm + bot arm + bar  → 4 contours (canonical: 2)

fontspector's glyphset reference expects the canonical counts, so ⟧ / ⸥
trip the font's only contour_count WARN. Each bracket "part" is the union
of overlapping axis-aligned rects, so we retrace it as a single outline
(pixel-identical extents; the inner bar of ⟦⟧ is kept as-is). Winding is
normalised CCW to match bracketleft/bracketright. Per master, rebuilt from
that layer's own extents, so weight tracks automatically.

Idempotent: acts only on the un-fixed multi-rect form (corner=2, double=4);
re-running after a fix is a no-op.

    python3 scripts/fix-bracket-contours.py --dry-run
    python3 scripts/fix-bracket-contours.py --apply
"""
import argparse

GLYPHS_PATH = "sources/BuenaMono.glyphs"


def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def signed_area(pts):
    s = 0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]
        s += x0 * y1 - x1 * y0
    return s / 2


def ccw(pts):
    return pts if signed_area(pts) > 0 else list(reversed(pts))


def merge_corner(contours):
    """2 rects (arm + stem sharing a corner) → single L outline (6 pts)."""
    boxes = [bbox(c) for c in contours]
    X0 = min(b[0] for b in boxes); X1 = max(b[1] for b in boxes)
    Y0 = min(b[2] for b in boxes); Y1 = max(b[3] for b in boxes)
    # arm is wider than tall; stem is taller than wide
    arm, stem = sorted(boxes, key=lambda b: (b[1] - b[0]) - (b[3] - b[2]))[::-1]
    top = arm[3] == Y1                      # arm hugs the top edge
    left = stem[0] == X0                    # stem hugs the left edge
    rx = stem[1] if left else stem[0]       # reflex (inner) x = stem inner edge
    ry = arm[2] if top else arm[3]          # reflex (inner) y = arm inner edge
    if left and top:
        pts = [(X0, Y0), (rx, Y0), (rx, ry), (X1, ry), (X1, Y1), (X0, Y1)]
    elif (not left) and top:
        pts = [(rx, Y0), (X1, Y0), (X1, Y1), (X0, Y1), (X0, ry), (rx, ry)]
    elif left and (not top):
        pts = [(X0, Y0), (X1, Y0), (X1, ry), (rx, ry), (rx, Y1), (X0, Y1)]
    else:  # right, bottom
        pts = [(X0, Y0), (X1, Y0), (X1, Y1), (rx, Y1), (rx, ry), (X0, ry)]
    return [ccw(pts)]


def merge_double(contours, is_left):
    """4 rects (stem + 2 arms + inner bar) → [bracket L outline, inner bar]."""
    boxes = [bbox(c) for c in contours]
    ov_minx = min(b[0] for b in boxes); ov_maxx = max(b[1] for b in boxes)
    if is_left:
        inner_i = next(i for i, b in enumerate(boxes) if b[0] > ov_minx)
    else:
        inner_i = next(i for i, b in enumerate(boxes) if b[1] < ov_maxx)
    inner = contours[inner_i]
    br = [b for i, b in enumerate(boxes) if i != inner_i]
    bo = min(b[2] for b in br); to = max(b[3] for b in br)
    if is_left:
        left = min(b[0] for b in br); stem_r = min(b[1] for b in br)
        arm_end = max(b[1] for b in br)
        arms = [b for b in br if b[1] == arm_end]
        ti = max(b[2] for b in arms); bi = min(b[3] for b in arms)
        outline = [(left, to), (left, bo), (arm_end, bo), (arm_end, bi),
                   (stem_r, bi), (stem_r, ti), (arm_end, ti), (arm_end, to)]
    else:
        right = max(b[1] for b in br); stem_l = max(b[0] for b in br)
        arm_end = min(b[0] for b in br)
        arms = [b for b in br if b[0] == arm_end]
        ti = max(b[2] for b in arms); bi = min(b[3] for b in arms)
        outline = [(right, bo), (right, to), (arm_end, to), (arm_end, ti),
                   (stem_l, ti), (stem_l, bi), (arm_end, bi), (arm_end, bo)]
    return [ccw(outline), ccw(inner)]


# glyph -> (needs-this-contour-count-to-act, builder)
PLAN = {
    "u2E22": (2, lambda c: merge_corner(c)),
    "u2E23": (2, lambda c: merge_corner(c)),
    "u2E24": (2, lambda c: merge_corner(c)),
    "u2E25": (2, lambda c: merge_corner(c)),
    "u27E6": (4, lambda c: merge_double(c, True)),
    "u27E7": (4, lambda c: merge_double(c, False)),
}


def run(dry):
    import glyphsLib
    from glyphsLib.classes import GSPath, GSNode
    font = glyphsLib.load(open(GLYPHS_PATH))
    touched = False
    for gname, (need, build) in PLAN.items():
        g = font.glyphs[gname]
        acted = skipped = 0
        for L in g.layers:
            contours = [[(n.position.x, n.position.y) for n in p.nodes] for p in L.paths]
            if len(contours) != need:
                skipped += 1
                continue
            new = build(contours)
            acted += 1
            if dry:
                continue
            L.paths = []
            for pts in new:
                path = GSPath(); path.closed = True
                for (px, py) in pts:
                    path.nodes.append(GSNode(position=(round(px), round(py)), type="line"))
                L.paths.append(path)
        if acted:
            touched = True
        print(f"  {gname}: {'would fix' if dry else 'fixed'} {acted} masters"
              + (f", skipped {skipped} (already canonical)" if skipped else ""))
    if not dry and touched:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")
    elif not dry:
        print("nothing to do")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run(dry=not a.apply)


if __name__ == "__main__":
    main()
