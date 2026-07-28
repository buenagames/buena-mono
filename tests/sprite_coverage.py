#!/usr/bin/env python3
"""sprite_coverage.py — font-aware TUI / monospace coverage + integrity test.

Unlike the visual specimen, this returns a verdict. It verifies that Buena Mono:
  1. covers its TUI-critical blocks *completely* (box-drawing, block elements,
     Braille — a monospace TUI font must have every cell of these),
  2. keeps every covered spacing glyph on the 618 monospace cell (integrity),
  3. draws a real outline for each (no accidental blanks, except the legitimately
     empty U+2800 blank Braille pattern),
and reports coverage of the broader symbol blocks it substantially covers.

Exits non-zero on any failure — safe to hook into `make qa` / CI.

Usage:
    python3 tests/sprite_coverage.py [path/to/font.ttf]
"""
import sys
import argparse
import unicodedata as ud
from collections import Counter

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

DEFAULT_FONT = "fonts/variable/BuenaMono-VF.ttf"
BUENA_CELL = 618  # Buena's immutable monospace advance (UPM 1000)

# Fully-assigned blocks a monospace TUI font MUST cover 100%.
MUST_COMPLETE = {
    "Box Drawing":      (0x2500, 0x257F),  # 128 — corners, joins, weights
    "Block Elements":   (0x2580, 0x259F),  # 32  — shades, quadrants, eighths
    "Braille Patterns": (0x2800, 0x28FF),  # 256 — 2x4 dot matrix; the differentiator
}

# Blocks Buena substantially covers — report coverage, still assert 618.
REPORT = {
    "Arrows":                  (0x2190, 0x21FF),
    "Mathematical Operators":  (0x2200, 0x22FF),
    "Miscellaneous Technical": (0x2300, 0x23FF),
    "Geometric Shapes":        (0x25A0, 0x25FF),
    "Dingbats":                (0x2700, 0x27BF),
    "Supplemental Arrows-A":   (0x27F0, 0x27FF),
    "Supplemental Arrows-B":   (0x2900, 0x297F),
}

POWERLINE = (0xE0A0, 0xE0D4)          # shipped Powerline PUA range
BLANK_OK = {0x2800, 0x0020, 0x00A0, 0x2007}  # legitimately outline-less


def assigned(cp):
    try:
        ud.name(chr(cp))
        return True
    except ValueError:
        return False


def derive_cell(cmap, hmtx):
    """The font's own monospace cell = modal advance of ASCII alphanumerics."""
    refs = [cmap[cp] for cp in
            list(range(0x41, 0x5B)) + list(range(0x61, 0x7B)) + list(range(0x30, 0x3A))
            if cp in cmap]
    widths = Counter(hmtx[gn][0] for gn in refs)
    return widths.most_common(1)[0][0] if widths else BUENA_CELL


def main():
    ap = argparse.ArgumentParser(
        description="Buena Mono TUI / monospace coverage + integrity test")
    ap.add_argument("font", nargs="?", default=DEFAULT_FONT)
    ap.add_argument("--any-cell", action="store_true",
                    help="derive the monospace cell from the font itself (general mono "
                         "linter) instead of asserting Buena's 618")
    args = ap.parse_args()

    f = TTFont(args.font)
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    gs = f.getGlyphSet()
    if args.any_cell:
        cell = derive_cell(cmap, hmtx)
        cell_note = f"{cell} (derived from font)"
    else:
        cell = BUENA_CELL
        cell_note = f"{cell} (Buena)"
    fails, lines = [], []

    def width_of(cp):
        return hmtx[cmap[cp]][0]

    def has_outline(cp):
        p = BoundsPen(gs)
        gs[cmap[cp]].draw(p)
        return p.bounds is not None

    for name, (a, b) in MUST_COMPLETE.items():
        want = [cp for cp in range(a, b + 1) if assigned(cp)]
        present = [cp for cp in want if cp in cmap]
        missing = [cp for cp in want if cp not in cmap]
        badw = [cp for cp in present if width_of(cp) != cell]
        blank = [cp for cp in present if cp not in BLANK_OK and not has_outline(cp)]
        ok = not (missing or badw or blank)
        lines.append(f"  [{'PASS' if ok else 'FAIL'}] {name:24} {len(present)}/{len(want)} @{cell}")
        if missing:
            fails.append(f"{name}: MISSING {len(missing)} — " +
                         ", ".join(f"U+{c:04X}" for c in missing[:10]))
        if badw:
            fails.append(f"{name}: non-{cell} advance — " +
                         ", ".join(f"U+{c:04X}({width_of(c)})" for c in badw[:10]))
        if blank:
            fails.append(f"{name}: empty outline — " +
                         ", ".join(f"U+{c:04X}" for c in blank[:10]))

    for name, (a, b) in REPORT.items():
        want = [cp for cp in range(a, b + 1) if assigned(cp)]
        present = [cp for cp in want if cp in cmap]
        badw = [cp for cp in present if width_of(cp) != cell]
        warn = f"  ! {len(badw)} non-{cell}" if badw else ""
        lines.append(f"  [    ] {name:24} {len(present)}/{len(want)} covered{warn}")
        if badw:
            fails.append(f"{name}: non-{cell} advance — " +
                         ", ".join(f"U+{c:04X}({width_of(c)})" for c in badw[:10]))

    a, b = POWERLINE
    pl = [cp for cp in range(a, b + 1) if cp in cmap]
    plbad = [cp for cp in pl if width_of(cp) != cell]
    lines.append(f"  [    ] {'Powerline (PUA)':24} {len(pl)}/{b - a + 1} @E0A0-E0D4"
                 + (f"  ! {len(plbad)} non-{cell}" if plbad else ""))
    if plbad:
        fails.append(f"Powerline: {len(plbad)} non-{cell} advance glyphs")

    print(f"Buena Mono — TUI / monospace coverage + integrity\n"
          f"  font: {args.font}\n  cell: {cell_note}\n")
    print("\n".join(lines))
    if fails:
        print("\nFAIL")
        for x in fails:
            print("  x", x)
        sys.exit(1)
    print(f"\nPASS — box-drawing, block elements and Braille are 100% complete, "
          f"every covered glyph sits on the {cell} cell.")
    sys.exit(0)


if __name__ == "__main__":
    main()
