#!/usr/bin/env python3
"""Buena Mono — Font Summary.

Prints a concise development summary from the built font and .glyphs source.

Usage:
    python3 scripts/font-summary.py                     # default paths
    python3 scripts/font-summary.py --font path/to.ttf  # custom font path
"""

import argparse
import os
import sys
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_FONT = PROJECT_ROOT / "out" / "fonts" / "BuenaMono-VF.ttf"
DEFAULT_OTF = PROJECT_ROOT / "out" / "fonts" / "BuenaMono-VF.otf"
DEFAULT_WOFF2 = PROJECT_ROOT / "out" / "fonts" / "BuenaMono-VF.woff2"
DEFAULT_GLYPHS = PROJECT_ROOT / "sources" / "BuenaMono.glyphs"


def file_size_str(path):
    if not path.exists():
        return "—"
    size = path.stat().st_size
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    return f"{size // 1024} KB"


def main():
    parser = argparse.ArgumentParser(description="Buena Mono font summary")
    parser.add_argument("--font", default=str(DEFAULT_FONT), help="TTF variable font path")
    args = parser.parse_args()

    font_path = Path(args.font)
    if not font_path.exists():
        print(f"Font not found: {font_path}")
        print("Run `make build` first.")
        sys.exit(1)

    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    name = font["name"]
    cmap = font.getBestCmap()
    glyph_order = font.getGlyphOrder()

    # --- Identity ---
    family = name.getName(1, 3, 1, 0x0409)
    version = name.getName(5, 3, 1, 0x0409)
    family_str = str(family) if family else "?"
    version_str = str(version) if version else "?"

    # --- Axes ---
    fvar = font.get("fvar")
    axes = []
    instances = []
    if fvar:
        for axis in fvar.axes:
            axes.append((axis.axisTag, axis.minValue, axis.defaultValue, axis.maxValue))
        instances = fvar.instances

    # --- Features ---
    gsub_tags = set()
    gpos_tags = set()
    if "GSUB" in font:
        for rec in font["GSUB"].table.FeatureList.FeatureRecord:
            gsub_tags.add(rec.FeatureTag)
    if "GPOS" in font:
        for rec in font["GPOS"].table.FeatureList.FeatureRecord:
            gpos_tags.add(rec.FeatureTag)

    # --- Metrics ---
    os2 = font["OS/2"]
    head = font["head"]
    hhea = font["hhea"]
    post = font["post"]

    # --- Codepoint blocks ---
    # Count against assigned (named) codepoints, not raw block size.
    # This excludes control characters and unassigned slots.
    blocks = [
        ("Basic Latin", 0x0000, 0x007F),
        ("Latin-1 Supplement", 0x0080, 0x00FF),
        ("Latin Extended-A", 0x0100, 0x017F),
        ("Latin Extended-B", 0x0180, 0x024F),
        ("Combining Marks", 0x0300, 0x036F),
        ("Greek & Coptic", 0x0370, 0x03FF),
        ("Cyrillic", 0x0400, 0x052F),
        ("Latin Ext Additional", 0x1E00, 0x1EFF),
        ("Greek Extended", 0x1F00, 0x1FFF),
        ("General Punctuation", 0x2000, 0x206F),
        ("Super/Subscripts", 0x2070, 0x209F),
        ("Currency", 0x20A0, 0x20CF),
        ("Arrows", 0x2190, 0x21FF),
        ("Math Operators", 0x2200, 0x22FF),
        ("Box Drawing", 0x2500, 0x257F),
        ("Block Elements", 0x2580, 0x259F),
        ("Geometric Shapes", 0x25A0, 0x25FF),
        ("Braille Patterns", 0x2800, 0x28FF),
        ("Powerline (PUA)", 0xE000, 0xF8FF),
    ]

    def count_assigned(start, end):
        """Count codepoints with a Unicode name (excludes controls/unassigned)."""
        n = 0
        for cp in range(start, end + 1):
            try:
                unicodedata.name(chr(cp))
                n += 1
            except ValueError:
                pass
        return n

    block_counts = []
    for label, start, end in blocks:
        count = sum(1 for cp in cmap if start <= cp <= end)
        if label == "Powerline (PUA)":
            # PUA has no Unicode names; use count as its own total
            total = count
        else:
            total = count_assigned(start, end)
        if count > 0:
            block_counts.append((label, count, total))

    # --- Ligature count ---
    lig_glyphs = [g for g in glyph_order if ".liga" in g or ".calt" in g or ".dlig" in g or "_" in g]

    # --- Output ---
    W = 60
    SEP = "─" * W

    print()
    print(f"  {'Buena Mono — Font Summary':^{W-4}}")
    print(f"  {SEP}")
    print()

    # Identity
    print(f"  Family:       {family_str}")
    print(f"  Version:      {version_str}")
    print(f"  License:      SIL Open Font License 1.1")
    print()

    # Counts
    print(f"  {SEP}")
    print(f"  {'GLYPHS & COVERAGE':^{W-4}}")
    print(f"  {SEP}")
    print(f"  Total glyphs:       {len(glyph_order):,}")
    print(f"  Unicode codepoints: {len(cmap):,}")
    print()

    # Top blocks
    for label, count, total in block_counts:
        pct = count / total * 100
        bar_len = 12
        filled = round(pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        if pct >= 99.5:
            pct_str = "100%"
        else:
            pct_str = f"{pct:.0f}%"
        print(f"  {label:<24} {count:>4}/{total:<4} {bar} {pct_str}")
    print()

    # Variable font + italic status
    print(f"  {SEP}")
    print(f"  {'VARIABLE FONT':^{W-4}}")
    print(f"  {SEP}")
    axis_tags = {tag for tag, _, _, _ in axes}
    for tag, mn, default, mx in axes:
        print(f"  Axis: {tag}  {int(mn)}–{int(mx)}  (default {int(default)})")

    # Italic / Slant status
    has_slnt = "slnt" in axis_tags
    has_ital = "ital" in axis_tags
    italic_bit = bool(os2.fsSelection & 1)
    italic_angle = post.italicAngle
    if has_slnt:
        slnt_axis = next((mn, mx) for tag, mn, _, mx in axes if tag == "slnt")
        print(f"  Italic:  Variable slant axis ({int(slnt_axis[0])}° to {int(slnt_axis[1])}°)")
    elif has_ital:
        print(f"  Italic:  Variable ital axis (true italic masters)")
    elif italic_bit or italic_angle != 0:
        print(f"  Italic:  Yes (angle {italic_angle}°)")
    else:
        print(f"  Italic:  No — upright only")

    print(f"  Named instances: {len(instances)}")
    if instances:
        inst_names = []
        for inst in instances:
            inst_name = name.getName(inst.subfamilyNameID, 3, 1, 0x0409)
            inst_names.append(str(inst_name) if inst_name else "?")
        print(f"    {', '.join(inst_names)}")
    print()

    # Features
    print(f"  {SEP}")
    print(f"  {'OPENTYPE FEATURES':^{W-4}}")
    print(f"  {SEP}")
    gsub_sorted = sorted(gsub_tags)
    gpos_sorted = sorted(gpos_tags)
    print(f"  GSUB ({len(gsub_sorted)}):")
    # Print in rows of 10
    for i in range(0, len(gsub_sorted), 10):
        chunk = gsub_sorted[i:i+10]
        print(f"    {', '.join(chunk)}")
    print(f"  GPOS ({len(gpos_sorted)}): {', '.join(gpos_sorted)}")
    print(f"  Total: {len(gsub_sorted) + len(gpos_sorted)} features")
    print()

    # Metrics
    print(f"  {SEP}")
    print(f"  {'METRICS':^{W-4}}")
    print(f"  {SEP}")
    metrics = [
        ("UPM", head.unitsPerEm),
        ("Advance Width", font["hmtx"]["space"][0]),
        ("Cap Height", os2.sCapHeight),
        ("x-Height", os2.sxHeight),
        ("Typo Ascender", os2.sTypoAscender),
        ("Typo Descender", os2.sTypoDescender),
        ("Win Ascent", os2.usWinAscent),
        ("Win Descent", os2.usWinDescent),
        ("Fixed Pitch", "Yes" if post.isFixedPitch else "No"),
    ]
    for label, value in metrics:
        print(f"  {label:<20} {value}")
    print()

    # Paths
    print(f"  {SEP}")
    print(f"  {'PATHS':^{W-4}}")
    print(f"  {SEP}")
    source_dir = PROJECT_ROOT / "sources"
    font_dir = Path(args.font).parent
    static_dir = font_dir / "static"
    print(f"  Source:    {source_dir.relative_to(PROJECT_ROOT)}/")
    print(f"  Output:    {font_dir.relative_to(PROJECT_ROOT)}/")
    if static_dir.exists():
        print(f"  Static:    {static_dir.relative_to(PROJECT_ROOT)}/")
    print()

    # Output files
    print(f"  {SEP}")
    print(f"  {'OUTPUT FILES':^{W-4}}")
    print(f"  {SEP}")

    # Variable fonts
    print(f"  Variable:")
    ttf_path = Path(args.font)
    otf_path = ttf_path.with_suffix(".otf")
    woff2_path = ttf_path.with_suffix(".woff2")
    for label, path in [("TTF", ttf_path), ("OTF/CFF2", otf_path), ("WOFF2", woff2_path)]:
        sz = file_size_str(path)
        exists = "✓" if path.exists() else "✗"
        print(f"    {exists} {path.name:<32} {sz:>8}")

    # Static instances — check in both font_dir and static subdirectory
    family_base = family_str.replace(" ", "")
    static_files = []
    for search_dir in [font_dir, static_dir]:
        if search_dir.exists():
            static_files += sorted(search_dir.glob(f"{family_base}-*.ttf"))
            static_files += sorted(search_dir.glob(f"{family_base}-*.otf"))
    # Exclude the VF files and deduplicate
    static_files = sorted(set(f for f in static_files if "-VF" not in f.name))

    if static_files:
        print(f"\n  Static instances ({len(static_files)}):")
        for path in static_files:
            sz = file_size_str(path)
            print(f"    ✓ {path.name:<32} {sz:>8}")
    else:
        # Show what instances would be generated
        print(f"\n  Static instances: not built")
        if instances:
            inst_names = []
            for inst in instances:
                inst_name = name.getName(inst.subfamilyNameID, 3, 1, 0x0409)
                inst_names.append(str(inst_name) if inst_name else "?")
            for inst_name in inst_names:
                print(f"    ◦ {family_base}-{inst_name}.ttf")
    print()


if __name__ == "__main__":
    main()
