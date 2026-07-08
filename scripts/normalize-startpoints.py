#!/usr/bin/env python3
"""Start-point / node-phase normalization across masters (BUENA-335 round 2).

For every glyph, every non-Regular master, every contour: rotate the node
list so that (a) the node-type sequence matches the Regular master's contour
exactly and (b) the summed squared distance between corresponding nodes is
minimal. Runs after normalize-winding.py (which aligns directions but can
phase-shift reversed curve contours) and also resolves the wrong_start_point
findings from fontTools varLib.interpolatable.

Usage:
  python3 scripts/normalize-startpoints.py --dry-run
  python3 scripts/normalize-startpoints.py --apply
"""

import argparse

import glyphsLib

GLYPHS_PATH = "sources/BuenaMono.glyphs"


def node_data(path):
    return [(n.position.x, n.position.y, n.type, n.smooth) for n in path.nodes]


def best_rotation(ref, other):
    """Rotation r of `other` minimizing distance to `ref`, restricted to
    rotations whose type sequence equals ref's. None if no rotation fits
    or the best is r=0."""
    n = len(other)
    if len(ref) != n:
        return None
    ref_types = [t for _, _, t, _ in ref]
    best = None
    best_cost = None
    for r in range(n):
        if [other[(i + r) % n][2] for i in range(n)] != ref_types:
            continue
        cost = 0.0
        for i in range(n):
            dx = other[(i + r) % n][0] - ref[i][0]
            dy = other[(i + r) % n][1] - ref[i][1]
            cost += dx * dx + dy * dy
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = r
    return best if best not in (None, 0) else None


def apply_rotation(path, r):
    nodes = node_data(path)
    n = len(nodes)
    rotated = [nodes[(i + r) % n] for i in range(n)]
    rebuilt = []
    for x, y, t, smooth in rotated:
        node = glyphsLib.classes.GSNode((x, y), t)
        node.smooth = smooth
        rebuilt.append(node)
    path.nodes = rebuilt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--improve-phase", action="store_true",
                    help="also re-phase contours whose types already match "
                         "(distance-min; helps after winding reversals)")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.print_help()
        return

    print(f"loading {GLYPHS_PATH} ...")
    font = glyphsLib.GSFont(GLYPHS_PATH)
    master_ids = {m.id: m.name for m in font.masters}
    reg_id = next(m.id for m in font.masters if m.name == "Regular")

    rotations = 0
    touched = set()
    unfixable = []
    for glyph in font.glyphs:
        reg_layer = next((l for l in glyph.layers if l.layerId == reg_id), None)
        if reg_layer is None or not reg_layer.paths:
            continue
        ref_contours = [node_data(p) for p in reg_layer.paths]
        for layer in glyph.layers:
            if layer.layerId not in master_ids or layer.layerId == reg_id:
                continue
            if len(layer.paths) != len(ref_contours):
                continue
            for i, path in enumerate(layer.paths):
                ref = ref_contours[i]
                other = node_data(path)
                if len(other) != len(ref):
                    unfixable.append(
                        f"{glyph.name}/{master_ids[layer.layerId]} c{i}: "
                        f"node count {len(other)} vs {len(ref)}")
                    continue
                types_match = ([t for _, _, t, _ in other]
                               == [t for _, _, t, _ in ref])
                if types_match and not args.improve_phase:
                    continue  # conservative: keep the authored phase
                r = best_rotation(ref, other)
                if r is None and not types_match:
                    unfixable.append(
                        f"{glyph.name}/{master_ids[layer.layerId]} c{i}: "
                        f"no type-matching rotation")
                    continue
                if r is not None:
                    if args.apply:
                        apply_rotation(path, r)
                    rotations += 1
                    touched.add(glyph.name)

    print(f"rotations: {rotations} contours across {len(touched)} glyphs")
    if unfixable:
        print(f"unfixable: {len(unfixable)}")
        for u in unfixable[:20]:
            print("  ", u)
    if args.apply:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")


if __name__ == "__main__":
    main()
