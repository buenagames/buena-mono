#!/usr/bin/env python3
"""BUENA (source hygiene): convert uni2655's 3 quadratic segments to cubic.

This is a cubic (CFF2) font, but the white-queen glyph uni2655 carries 3
`qcurve` (quadratic on-curve) nodes mixed into otherwise-cubic contours — a
leftover from the v1.227 chess pass. afdko's `tx` UFO reader can't handle
quadratic points, so `charplot`/`hintplot` (the afdko-proofs generator in
make-reports.py) abort on any UFO, taking the whole report suite down with them.

A quadratic Bézier is a degenerate cubic, so the conversion is EXACT (not an
approximation): for a quad P0–Q–P2,
    C1 = P0 + 2/3 (Q - P0)
    C2 = P2 + 2/3 (Q - P2)
gives the identical curve as a cubic P0–C1–C2–P2.

Each qcurve here is preceded by exactly one offcurve (verified), so every
quadratic segment has a single control point. We rebuild each affected path,
tracking the previous on-curve (with wrap-around for the first segment).

    python3 scripts/fix-uni2655-quad-to-cubic.py --dry-run
    python3 scripts/fix-uni2655-quad-to-cubic.py --apply
"""
import argparse
import glyphsLib
from glyphsLib.classes import GSNode

GLYPHS_PATH = "sources/BuenaMono.glyphs"
GLYPH = "uni2655"


def q2c(P0, Q, P2):
    c1 = (P0[0] + 2 / 3 * (Q[0] - P0[0]), P0[1] + 2 / 3 * (Q[1] - P0[1]))
    c2 = (P2[0] + 2 / 3 * (Q[0] - P2[0]), P2[1] + 2 / 3 * (Q[1] - P2[1]))
    return c1, c2


def last_oncurve_pos(nodes):
    for n in reversed(nodes):
        if str(n.type) in ("line", "curve", "qcurve"):
            return (n.position.x, n.position.y)
    return None


def convert_path(path):
    """Return (new_nodes, n_converted) with every qcurve segment made cubic."""
    nodes = list(path.nodes)
    if not any(str(n.type) == "qcurve" for n in nodes):
        return None, 0
    prev_on = last_oncurve_pos(nodes)   # wrap-around start point
    out, buf, converted = [], [], 0
    for n in nodes:
        t = str(n.type)
        pos = (n.position.x, n.position.y)
        if t == "offcurve":
            buf.append(pos)
            continue
        if t == "qcurve":
            assert len(buf) == 1, f"expected single-control quad, got {len(buf)} offcurves"
            c1, c2 = q2c(prev_on, buf[0], pos)
            out.append(GSNode(position=c1, type="offcurve"))
            out.append(GSNode(position=c2, type="offcurve"))
            out.append(GSNode(position=pos, type="curve"))
            converted += 1
        else:  # line / curve on-curve — flush buffered offcurves unchanged
            for b in buf:
                out.append(GSNode(position=b, type="offcurve"))
            out.append(GSNode(position=pos, type=t))
        buf = []
        prev_on = pos
    assert not buf, "dangling offcurves at end of path"
    return out, converted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    font = glyphsLib.load(open(GLYPHS_PATH))
    g = font.glyphs[GLYPH]
    mids = {m.id: m.name for m in font.masters}
    total = 0
    for L in g.layers:
        if L.layerId not in mids:
            continue
        layer_conv = 0
        for p in L.paths:
            new_nodes, c = convert_path(p)
            if c:
                layer_conv += c
                if a.apply:
                    p.nodes = new_nodes
        if layer_conv:
            total += layer_conv
            print(f"  {mids[L.layerId]:16} converted {layer_conv} quad segment(s)")
    print(f"{'applied' if a.apply else 'would convert'}: {total} segments across masters")
    if a.apply:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}")


if __name__ == "__main__":
    main()
