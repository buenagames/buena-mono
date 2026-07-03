#!/usr/bin/env python3
"""Add gasp table to built variable fonts.

Sets the standard Google Fonts gasp values:
  rangeMaxPPEM=0xFFFF, flags=0x000F
  (GASP_GRIDFIT | GASP_DOGRAY | GASP_SYMMETRIC_GRIDFIT | GASP_SYMMETRIC_SMOOTHING)

Usage:
    python3 scripts/add-gasp-table.py [--font-dir out/fonts]
"""

import argparse
import sys
from pathlib import Path

from fontTools.ttLib import TTFont


def add_gasp(font_path):
    """Add gasp table to a single font file."""
    print(f"  {font_path.name}...", end=" ")

    font = TTFont(str(font_path))

    # Create gasp table: version 1, single range covering all sizes
    from fontTools.ttLib.tables._g_a_s_p import table__g_a_s_p
    gasp = table__g_a_s_p()
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}  # all sizes: gridfit + smoothing + symmetric
    font["gasp"] = gasp

    font.save(str(font_path))
    font.close()
    print("gasp table added")


def main():
    parser = argparse.ArgumentParser(description="Add gasp table to built fonts")
    parser.add_argument("--font-dir", default="out/fonts", help="Directory containing built fonts")
    args = parser.parse_args()

    font_dir = Path(args.font_dir)

    targets = ["BuenaMono-VF.ttf", "BuenaMono-VF.otf"]
    updated = 0

    for name in targets:
        path = font_dir / name
        if path.exists():
            add_gasp(path)
            updated += 1
        else:
            print(f"  {name}... SKIP (not found)")

    print(f"\nDone: {updated} fonts updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
