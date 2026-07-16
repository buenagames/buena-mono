#!/usr/bin/env python3
"""fix-extrabold-weight.py — rebuild the ExtraBold masters from Bold (BUENA-341).

THE BUG. The ExtraBold masters (wght=800) were derived from the **Regular**
master instead of **Bold**, so the weight axis runs backwards at the top: text
gets LIGHTER from wght 700 to 800. Shipped in every release since v1.218.

Proof (scanline stem widths, upright — italic identical):

    glyph   Regular  Bold   ExtraBold   Regular+26   Bold+26
      I        81     119      107         107  <--    145
      l        82     120      108         108  <--    146
      n        83     121      109         109  <--    147
      H        80     118      106         106  <--    144
      E        80     118      106         106  <--    144

ExtraBold matches Regular+26 exactly on every probe — i.e. it is
`offset_paths(Regular, +13)`. `scripts/add-weight-extremes.py` documents the
intent as Bold-derived:

    EXTRABOLD_OFFSET = 13   # expand outward from Bold -> thicker stems
    "Extrabold (wght=800): derived from Bold (700) ... ~146 unit stems from 120"

The Thin master is a control and is correct: Regular-32 == Thin, exactly.

THE FIX. Re-derive ExtraBold = offset_paths(Bold, +13), which lands stems at
144-147 — matching the script's own documented target of ~146.

Offset code is copied verbatim from scripts/add-weight-extremes.py (dev repo)
so the geometry matches how every other master was produced.

Composites (1,001 glyphs) are SKIPPED — they inherit the new weight through
their components. Only glyphs with real paths are offset. Bold and ExtraBold
have identical path topology (verified: 0 glyphs differ), so the offset
preserves node counts and types and keeps interpolation compatible.

Anchors are NOT touched here — run scripts/normalize-anchors.py afterwards,
since heavier letters move the flat tops that anchors track (see v1.224).

Usage:
  python3 scripts/fix-extrabold-weight.py --dry-run
  python3 scripts/fix-extrabold-weight.py --apply
"""

import argparse
import math
import os
import sys

import glyphsLib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLYPHS_PATH = os.path.join(PROJECT_ROOT, "sources/BuenaMono.glyphs")

EXTRABOLD_OFFSET = 13  # expand outward from Bold -> thicker stems
ADVANCE_WIDTH = 618

# (source master name, destination master name)
PAIRS = [("Bold", "ExtraBold"), ("Bold Italic", "ExtraBold Italic")]


# ---------------------------------------------------------------- offset math
# Copied verbatim from scripts/add-weight-extremes.py (dev repo) — the same
# topology-preserving normal offset that produced every other master.

def normalize(dx, dy):
    length = math.hypot(dx, dy)
    if length < 1e-10:
        return (0.0, 0.0)
    return (dx / length, dy / length)


def outward_normal(dx, dy):
    return normalize(dy, -dx)


def _on_curve_normal(pts, types, i, n):
    px, py = pts[i]
    prev_idx = (i - 1) % n
    in_dx, in_dy = px - pts[prev_idx][0], py - pts[prev_idx][1]
    if abs(in_dx) < 1e-10 and abs(in_dy) < 1e-10:
        p2 = pts[(i - 2) % n]
        in_dx, in_dy = px - p2[0], py - p2[1]

    next_idx = (i + 1) % n
    out_dx, out_dy = pts[next_idx][0] - px, pts[next_idx][1] - py
    if abs(out_dx) < 1e-10 and abs(out_dy) < 1e-10:
        p2 = pts[(i + 2) % n]
        out_dx, out_dy = p2[0] - px, p2[1] - py

    n_in = outward_normal(in_dx, in_dy)
    n_out = outward_normal(out_dx, out_dy)
    avg_x, avg_y = n_in[0] + n_out[0], n_in[1] + n_out[1]
    if math.hypot(avg_x, avg_y) < 1e-10:
        return n_in
    avg_nx, avg_ny = normalize(avg_x, avg_y)
    dot = avg_nx * n_in[0] + avg_ny * n_in[1]
    dot = max(dot, 0.25)
    miter = min(1.0 / dot, 4.0)
    return (avg_nx * miter, avg_ny * miter)


def _off_curve_normal(pts, types, i, n):
    px, py = pts[i]
    prev_idx, next_idx = (i - 1) % n, (i + 1) % n
    if types[prev_idx] in ("line", "curve"):
        anchor = pts[prev_idx]
        dx, dy = px - anchor[0], py - anchor[1]
        if abs(dx) < 1e-10 and abs(dy) < 1e-10:
            dx, dy = pts[next_idx][0] - anchor[0], pts[next_idx][1] - anchor[1]
        return outward_normal(dx, dy)
    if types[next_idx] in ("line", "curve"):
        anchor = pts[next_idx]
        dx, dy = anchor[0] - px, anchor[1] - py
        if abs(dx) < 1e-10 and abs(dy) < 1e-10:
            dx, dy = anchor[0] - pts[prev_idx][0], anchor[1] - pts[prev_idx][1]
        return outward_normal(dx, dy)
    return outward_normal(pts[next_idx][0] - pts[prev_idx][0],
                          pts[next_idx][1] - pts[prev_idx][1])


def offset_paths(paths, offset):
    """Offset all paths by `offset` units along the right-of-travel normal."""
    result = []
    for contour in paths:
        n = len(contour)
        if n == 0:
            continue
        pts = [(c[0], c[1]) for c in contour]
        types = [c[2] for c in contour]
        new_contour = []
        for i in range(n):
            if types[i] in ("line", "curve"):
                nx, ny = _on_curve_normal(pts, types, i, n)
            else:
                nx, ny = _off_curve_normal(pts, types, i, n)
            new_contour.append((round(pts[i][0] + offset * nx),
                                round(pts[i][1] + offset * ny),
                                types[i]))
        result.append(new_contour)
    return result


def layer_to_paths(layer):
    paths = []
    for gspath in layer.paths:
        contour = [(n.position.x, n.position.y, n.type) for n in gspath.nodes]
        if contour:
            paths.append(contour)
    return paths


# ------------------------------------------------------------------ operation

def master_ids(font):
    return {m.name: m.id for m in font.masters}


def layer_of(glyph, mid):
    for l in glyph.layers:
        if l.layerId == mid:
            return l
    return None


def apply_to_layer(dst_layer, new_paths):
    """Write offset coordinates back, preserving node objects and types."""
    for gspath, contour in zip(dst_layer.paths, new_paths):
        for node, (x, y, t) in zip(gspath.nodes, contour):
            node.position = (x, y)


def zero_len_segments(paths):
    """Count consecutive coincident nodes — i.e. zero-length segments.

    build-cff2.py normalizes charstrings and REMOVES zero-length segments. If
    the offset collapses a segment that the source master doesn't have, the
    removal happens in ExtraBold only and its point structure diverges from the
    other masters — the CFF2 build then rejects the font ("'rmoveto' at point
    index N ... differs from the default font point type"). Glyphs where that
    happens are left un-offset rather than corrupting the build.
    """
    n = 0
    for contour in paths:
        pts = [(round(c[0]), round(c[1])) for c in contour]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            if a == b:
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Rebuild ExtraBold from Bold (BUENA-341)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-file", help="newline-separated glyph names to leave "
                    "un-offset (CFF2 build casualties; see --help notes)")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.error("pass --dry-run or --apply")

    skip = set()
    if args.skip_file and os.path.exists(args.skip_file):
        skip = {l.strip() for l in open(args.skip_file) if l.strip()}
        print(f"skip list: {len(skip)} glyphs")

    print(f"loading {GLYPHS_PATH} ...")
    font = glyphsLib.load(open(GLYPHS_PATH))
    ids = master_ids(font)

    for src_name, dst_name in PAIRS:
        if src_name not in ids or dst_name not in ids:
            sys.exit(f"missing master: {src_name} / {dst_name}")

    total = {"offset": 0, "skipped_composite": 0, "skipped_empty": 0,
             "mismatch": 0, "skipped_degenerate": 0}
    mismatches = []
    degenerate = []

    for src_name, dst_name in PAIRS:
        sid, did = ids[src_name], ids[dst_name]
        n_off = 0
        for glyph in font.glyphs:
            src, dst = layer_of(glyph, sid), layer_of(glyph, did)
            if src is None or dst is None:
                continue
            if not src.paths:
                # pure composite or empty: inherits via components
                total["skipped_composite" if src.components else "skipped_empty"] += 1
                continue
            # topology must match or we would corrupt interpolation
            if [len(p.nodes) for p in src.paths] != [len(p.nodes) for p in dst.paths]:
                total["mismatch"] += 1
                mismatches.append(f"{glyph.name} ({dst_name})")
                continue
            if glyph.name in skip:
                total["skipped_degenerate"] += 1
                degenerate.append(glyph.name)
                continue
            src_paths = layer_to_paths(src)
            new_paths = offset_paths(src_paths, EXTRABOLD_OFFSET)
            if args.apply:
                apply_to_layer(dst, new_paths)
            n_off += 1
        total["offset"] += n_off
        print(f"  {src_name} -> {dst_name}: {n_off} glyphs offset by +{EXTRABOLD_OFFSET}")

    print(f"\n  offset             : {total['offset']}")
    print(f"  skipped composite  : {total['skipped_composite']}  (inherit via components)")
    print(f"  skipped empty      : {total['skipped_empty']}")
    print(f"  skipped degenerate : {total['skipped_degenerate']}  (offset would collapse a segment)")
    print(f"  topology mismatch  : {total['mismatch']}")
    if mismatches:
        print("    " + ", ".join(mismatches[:10]))
    if degenerate:
        print(f"\n  NOTE: {len(set(degenerate))} glyphs keep the old (light) ExtraBold because")
        print("  offsetting them collapses a segment and breaks the CFF2 build:")
        print("    " + ", ".join(sorted(set(degenerate))[:12]) + (" ..." if len(set(degenerate)) > 12 else ""))

    if args.apply:
        print(f"\nsaving {GLYPHS_PATH} ...")
        font.save(GLYPHS_PATH)
        print("saved.")
        print("\nNEXT: python3 scripts/normalize-anchors.py   (heavier letters move")
        print("      the flat tops anchors track — see v1.224)")
        print("      then: python3 scripts/export-ufo.py && make build")
        print("      gate: python3 scripts/proof-rhythm.py   (must exit 0)")
    else:
        print("\ndry run — nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
