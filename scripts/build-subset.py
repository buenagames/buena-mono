#!/usr/bin/env python3
"""Build the specimen site's display subset from the full variable font.

The site (buena-mono.buenalabs.io) renders text via BuenaMono-VF.subset.woff2 — a
trimmed copy of the full font that keeps only the codepoints the specimen actually
displays, at a fraction of the size. This script produces that subset.

  - charset  : scripts/subset-charset.txt  (source of truth for coverage — edit it
               and re-run to add glyphs, e.g. new symbols used by a new demo)
  - preserves : both variable axes (wght, slnt) and ALL layout features
                (liga, calt, smcp, c2sc, ss01–ss12, zero, frac, …)

Usage:
  python3 scripts/build-subset.py [--full IN.ttf] [--charset FILE] [--output OUT.woff2]

Defaults build out/fonts/BuenaMono-VF.subset.woff2 from out/fonts/BuenaMono-VF.ttf.
Copy the result to the site repo's public/fonts/ to deploy.
"""
import argparse
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def load_charset(path):
    """Parse a charset file: hex codepoints / ranges (X-Y), whitespace/comma
    separated, '#' comments. Returns a set of ints."""
    cps = set()
    with open(path) as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            for tok in line.replace(",", " ").split():
                tok = tok.upper().replace("U+", "")
                if "-" in tok:
                    a, b = tok.split("-", 1)
                    cps.update(range(int(a, 16), int(b, 16) + 1))
                else:
                    cps.add(int(tok, 16))
    return cps


def main():
    ap = argparse.ArgumentParser(description="Build the display subset webfont.")
    ap.add_argument("--full", default=os.path.join(REPO, "out/fonts/BuenaMono-VF.ttf"),
                    help="Full variable font to subset (.ttf/.otf/.woff2).")
    ap.add_argument("--charset", default=os.path.join(HERE, "subset-charset.txt"),
                    help="Charset file (codepoints to keep).")
    ap.add_argument("--output", default=os.path.join(REPO, "out/fonts/BuenaMono-VF.subset.woff2"),
                    help="Output subset path (.woff2).")
    args = ap.parse_args()

    for label, path in (("full font", args.full), ("charset", args.charset)):
        if not os.path.exists(path):
            sys.exit(f"error: {label} not found: {path}")

    charset = load_charset(args.charset)
    src_ver = TTFont(args.full)["name"].getDebugName(5)
    src_cmap = set(TTFont(args.full).getBestCmap().keys())
    missing = sorted(cp for cp in charset if cp not in src_cmap)
    if missing:
        print(f"warning: {len(missing)} requested codepoints are absent from the full "
              f"font and will be skipped: {', '.join('U+%04X' % c for c in missing[:12])}"
              + (" …" if len(missing) > 12 else ""))

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]      # keep every GSUB/GPOS feature
    opts.glyph_names = True
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.recalc_timestamp = False
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.name_languages = ["*"]
    opts.symbol_cmap = True
    # fvar/gvar are kept by default (no instancing) — the subset stays variable.

    font = subset.load_font(args.full, opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(unicodes=charset)
    subsetter.subset(font)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    subset.save_font(font, args.output, opts)

    out = TTFont(args.output)
    cm = out.getBestCmap()
    feats = set()
    for tag in ("GSUB", "GPOS"):
        if tag in out and out[tag].table.FeatureList:
            feats.update(fr.FeatureTag for fr in out[tag].table.FeatureList.FeatureRecord)
    axes = [a.axisTag for a in out["fvar"].axes] if "fvar" in out else []
    size = os.path.getsize(args.output)
    print(f"built {args.output}")
    print(f"  from {os.path.basename(args.full)} ({src_ver})")
    print(f"  {out['maxp'].numGlyphs} glyphs · {len(cm)} cmap · {size // 1024} KB · axes {axes}")
    print(f"  layout features: {len(feats)} kept")
    # sanity: features the playground relies on + the demo specials
    need = ["liga", "calt", "smcp", "ss01", "ss12", "zero"]
    miss = [f for f in need if f not in feats]
    print("  key features:", "all present" if not miss else f"MISSING {miss}")
    specials = {0x2654: "chess ♔", 0x2660: "suit ♠", 0x273B: "spinner ✻"}
    print("  specials:", ", ".join(f"{v}={'ok' if cp in cm else 'MISSING'}" for cp, v in specials.items()))


if __name__ == "__main__":
    main()
