#!/usr/bin/env python3
"""proof-rhythm.py — monospace cell-rhythm proof + weight-axis gate.

Two jobs:

1. GATE (automated): the weight axis must be monotonic. Stem widths must not
   decrease as `wght` increases. This is machine-checkable and catches real
   bugs — it currently FAILS on the shipped font because the ExtraBold master
   is ~12u lighter than Bold.

2. PROOF (visual): render the classic rhythm strings — nnnn / oooo /
   hamburgefontsiv — at every named instance, for the "even gray colour /
   spacing matches counters" judgement the essay describes. A machine can't
   judge colour; a human can, so this emits HTML to look at.

Usage:
  python3 scripts/proof-rhythm.py                 # gate + write proof HTML
  python3 scripts/proof-rhythm.py --gate-only     # CI: exit 1 on regression
  python3 scripts/proof-rhythm.py --font PATH --out FILE
"""

import argparse
import os
import sys

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONT = os.path.join(PROJECT_ROOT, "fonts/variable/BuenaMono-VF.ttf")
DEFAULT_OUT = os.path.join(PROJECT_ROOT, "out/proof/rhythm.html")

# Rhythm strings. nnnn/oooo expose stem-to-counter rhythm; hamburgefontsiv is
# the classic spacing pangram-ish sample.
STRINGS = ["nnnn", "oooo", "nonnonoo", "hamburgefontsiv", "HAMBURGEFONTSIV"]

# Glyphs whose left stem is a clean vertical, with a scanline y chosen to miss
# crossbars/arms — otherwise the scanline spans the whole letter and measures
# width, not stem. (H crossbar ~y=350, E arms ~y=0/350/699: probe above them.)
STEM_PROBES = [("I", 350), ("l", 400), ("n", 260), ("H", 500), ("E", 500)]


def ink_spans(glyphset, gname, y):
    """Ink runs where a horizontal scanline at `y` crosses the outline.

    On-curve polygon approximation: adequate for vertical stems, which is all
    we measure. Avoids the coordinate-heuristic trap of guessing stems from
    sorted x values (anchors and off-curve points corrupt that).
    """
    pen = RecordingPen()
    glyphset[gname].draw(pen)
    pts, cur = [], []
    for op, args in pen.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            cur.append(args[-1])
        elif op == "closePath" and cur:
            pts.append(cur)
            cur = []
    xs = []
    for poly in pts:
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            if (y1 <= y < y2) or (y2 <= y < y1):
                t = (y - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
    xs.sort()
    return [xs[i + 1] - xs[i] for i in range(0, len(xs) - 1, 2)]


def instance(font_path, wght, slnt=0):
    f = TTFont(font_path)
    instantiateVariableFont(f, {"wght": wght, "slnt": slnt}, inplace=True)
    return f


def measure(font_path, weights, slnt=0):
    """{glyph: [(wght, stem)]} — first (leftmost) ink run per probe."""
    out = {g: [] for g, _ in STEM_PROBES}
    for w in weights:
        f = instance(font_path, w, slnt)
        gs = f.getGlyphSet()
        for g, y in STEM_PROBES:
            if g not in gs:
                continue
            spans = ink_spans(gs, g, y)
            if spans:
                out[g].append((w, round(spans[0])))
    return out


def check_monotonic(data):
    """Stems must never shrink as weight grows. Returns list of violations."""
    bad = []
    for g, series in data.items():
        for (w1, s1), (w2, s2) in zip(series, series[1:]):
            if s2 < s1:
                bad.append((g, w1, s1, w2, s2))
    return bad


def render_proof(font_path, out_path, weights):
    rel = os.path.relpath(font_path, os.path.dirname(out_path))
    rows = []
    for w in weights:
        cells = "".join(
            f'<div class="s" style="font-variation-settings:\'wght\' {w}">{s}</div>'
            for s in STRINGS
        )
        rows.append(f'<tr><th>{w}</th><td>{cells}</td></tr>')
    html = f"""<!doctype html>
<meta charset="utf-8"><title>Buena Mono — cell rhythm proof</title>
<style>
  @font-face {{ font-family:"BuenaVF"; src:url("{rel}") format("truetype");
                font-weight:100 800; }}
  body {{ font-family:-apple-system,system-ui,sans-serif; margin:2rem; color:#111; background:#fff; }}
  table {{ border-collapse:collapse; }}
  th {{ text-align:right; padding:.4rem .8rem; font:600 12px/1 ui-monospace,monospace; color:#888; vertical-align:middle; }}
  td {{ padding:.2rem 0; }}
  .s {{ font-family:"BuenaVF"; font-size:34px; letter-spacing:0; display:inline-block;
        margin-right:2.2rem; }}
  .note {{ max-width:46rem; line-height:1.5; color:#444; font-size:14px; }}
  code {{ background:#f4f4f4; padding:1px 4px; border-radius:3px; }}
</style>
<h1>Cell rhythm proof</h1>
<p class="note">Monospace bypasses pair kerning (fixed 618 cell), but even
colour still depends on the stem-to-counter relationship <em>inside</em> the
cell. Look for: uniform vertical rhythm in <code>nnnn</code>, uniform gaps in
<code>oooo</code>, no clumping or gapping in <code>hamburgefontsiv</code>, and
<strong>no reversal of colour as weight increases</strong>.</p>
<table>{''.join(rows)}</table>
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        fh.write(html)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Cell-rhythm proof + weight-axis gate")
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--gate-only", action="store_true", help="skip the HTML proof")
    args = ap.parse_args()

    if not os.path.exists(args.font):
        sys.exit(f"Font not found: {args.font}\nRun `make build` first.")

    f = TTFont(args.font, lazy=True)
    axes = {a.axisTag: a for a in f["fvar"].axes}
    if "wght" not in axes:
        sys.exit("No wght axis — nothing to check.")
    lo, hi = int(axes["wght"].minValue), int(axes["wght"].maxValue)
    weights = list(range(lo, hi + 1, 100))

    print(f"Measuring stems across wght {lo}–{hi} ...")
    rc = 0
    for slnt, label in ((0, "upright"), (-10, "italic") if "slnt" in axes else (None, None)):
        if slnt is None:
            continue
        data = measure(args.font, weights, slnt)
        print(f"\n  {label}:")
        for g, series in data.items():
            if series:
                print(f"    {g:2s} " + " ".join(f"{w}:{s:<4d}" for w, s in series))
        bad = check_monotonic(data)
        if bad:
            rc = 1
            print(f"\n  ❌ WEIGHT INVERSION ({label}) — stems shrink as wght grows:")
            for g, w1, s1, w2, s2 in bad:
                print(f"     {g}: wght {w1} stem {s1} -> wght {w2} stem {s2}  ({s2-s1:+d}u)")
        else:
            print(f"  ✅ {label}: stems monotonic across the weight axis")

    if not args.gate_only:
        p = render_proof(args.font, args.out, weights)
        print(f"\nProof written: {p}")

    if rc:
        print("\nFAIL — the weight axis is not monotonic. Known: the ExtraBold")
        print("master is ~12u lighter than Bold. Text gets LIGHTER")
        print("from wght 700 to 800.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
