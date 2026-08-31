#!/usr/bin/env python3
"""Buena Mono QA Validation Suite.

Automated checks for metrics, axes, glyph coverage, OpenType features,
cross-format parity, and outline quality. Validates both .glyphs source
files and built font files against the project spec.

Usage:
    python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs          # source only
    python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs --fix    # source + auto-fix
    python3 scripts/qa-validate.py --font-dir out/fonts                        # built fonts only
    python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs --font-dir out/fonts  # both

Exit codes:
    0 = all checks pass
    1 = one or more failures
"""

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Expected values (from docs/buena.yaml immutable metrics + actual state)
# ---------------------------------------------------------------------------

EXPECTED = {
    "units_per_em": 1000,
    "advance_width": 618,
    "cap_height": 699,
    "x_height": 524,
    "ascender": 729,
    "descender": -218,
    "os2_typo_ascender": 950,
    "os2_typo_descender": -250,
    "os2_typo_line_gap": 0,
    "os2_win_ascent": 1480,
    "os2_win_descent": 500,
    "hhea_ascender": 950,
    "hhea_descender": -250,
    "hhea_line_gap": 0,
}

EXPECTED_AXES = {
    "wght": {"min": 100, "default": 400, "max": 800},
    "slnt": {"min": -10, "default": 0, "max": 0},
}

# GSUB features expected in the font
EXPECTED_FEATURES = {
    "aalt", "c2sc", "calt", "case", "ccmp",
    "cv01", "cv02", "cv03", "cv04", "cv05", "cv06",
    "cv07", "cv08", "cv09", "cv10", "cv11", "cv12", "cv13",
    "dlig", "dnom", "dtls", "frac",
    "liga", "lnum", "locl", "nalt", "numr", "onum", "ordn",
    "salt", "sinf", "smcp",
    "ss01", "ss02", "ss03", "ss04", "ss05", "ss06", "ss07",
    "ss08", "ss09", "ss10", "ss11", "ss12",
    "subs", "sups", "tnum", "zero",
}

# Unicode ranges that must be fully covered
COVERAGE_RANGES = {
    "ASCII": (0x0020, 0x007E),
    "Latin-1 Supplement": (0x00A0, 0x00FF),
}

# Format/control characters commonly absent from cmap (Unicode category Cf)
COVERAGE_EXCEPTIONS = {
    0x00AD,  # Soft Hyphen — format character, not a visible glyph
}

# Individual codepoints that must be present (spot checks)
COVERAGE_REQUIRED = {
    "Box Drawing (sample)": [0x2500, 0x2502, 0x250C, 0x2510, 0x2514, 0x2518, 0x251C, 0x2524, 0x252C, 0x2534, 0x253C],
    "Block Elements (sample)": [0x2580, 0x2584, 0x2588, 0x258C, 0x2590, 0x2591, 0x2592, 0x2593],
    "Powerline (core)": [0xE0A0, 0xE0A1, 0xE0A2, 0xE0A3],
    "Markdown-critical": [
        ord('#'), ord('*'), ord('-'), ord('>'), ord('`'),
        ord('['), ord(']'), ord('('), ord(')'), ord('{'), ord('}'),
    ],
    "Ambiguity set": [
        ord('0'), ord('O'), ord('o'),
        ord('1'), ord('l'), ord('I'),
        ord('"'), ord("'"), ord('`'),
    ],
    "Latin Extended-A (sample)": [0x0100, 0x0101, 0x010C, 0x010D, 0x0141, 0x0142, 0x0160, 0x0161],
    "Cyrillic Basic (sample)": [0x0410, 0x0411, 0x0414, 0x0416, 0x0418, 0x041B, 0x0424, 0x0430, 0x0431, 0x0434],
}

FONT_FILES = ["BuenaMono-VF.ttf", "BuenaMono-VF.woff2", "BuenaMono-VF.otf"]

# Threshold for collapsed contour detection (units)
COLLAPSE_THRESHOLD = 5


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------

class Results:
    def __init__(self):
        self.passes = []
        self.failures = []
        self.warnings = []

    def ok(self, category, message):
        self.passes.append((category, message))

    def fail(self, category, message):
        self.failures.append((category, message))

    def warn(self, category, message):
        self.warnings.append((category, message))

    @property
    def passed(self):
        return len(self.failures) == 0

    def summary(self):
        total = len(self.passes) + len(self.failures)
        return (
            f"{len(self.passes)}/{total} checks passed, "
            f"{len(self.failures)} failures, "
            f"{len(self.warnings)} warnings"
        )

    def to_dict(self):
        return {
            "passed": self.passed,
            "summary": self.summary(),
            "passes": [{"category": c, "message": m} for c, m in self.passes],
            "failures": [{"category": c, "message": m} for c, m in self.failures],
            "warnings": [{"category": c, "message": m} for c, m in self.warnings],
        }


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def load_font(path):
    """Load a font file, returns TTFont or None."""
    from fontTools.ttLib import TTFont
    try:
        return TTFont(str(path))
    except Exception as e:
        return None


def validate_file_presence(font_dir, results):
    """Check that all expected output files exist."""
    cat = "Files"
    found = {}
    for name in FONT_FILES:
        p = font_dir / name
        if p.exists():
            results.ok(cat, f"{name} exists ({p.stat().st_size:,} bytes)")
            found[name] = p
        else:
            results.fail(cat, f"{name} missing from {font_dir}")
    return found


def validate_metrics(font, label, results):
    """Validate immutable metrics against expected values."""
    cat = f"Metrics [{label}]"

    head = font["head"]
    os2 = font["OS/2"]
    hhea = font["hhea"]

    checks = [
        ("unitsPerEm", head.unitsPerEm, EXPECTED["units_per_em"]),
        ("OS/2 sTypoAscender", os2.sTypoAscender, EXPECTED["os2_typo_ascender"]),
        ("OS/2 sTypoDescender", os2.sTypoDescender, EXPECTED["os2_typo_descender"]),
        ("OS/2 sTypoLineGap", os2.sTypoLineGap, EXPECTED["os2_typo_line_gap"]),
        ("OS/2 usWinAscent", os2.usWinAscent, EXPECTED["os2_win_ascent"]),
        ("OS/2 usWinDescent", os2.usWinDescent, EXPECTED["os2_win_descent"]),
        ("hhea ascender", hhea.ascent, EXPECTED["hhea_ascender"]),
        ("hhea descender", hhea.descent, EXPECTED["hhea_descender"]),
        ("hhea lineGap", hhea.lineGap, EXPECTED["hhea_line_gap"]),
    ]

    for name, actual, expected in checks:
        if actual == expected:
            results.ok(cat, f"{name} = {actual}")
        else:
            results.fail(cat, f"{name} = {actual}, expected {expected}")


def validate_advance_widths(font, label, results):
    """Every glyph width must be 0 or a multiple of 618."""
    cat = f"Widths [{label}]"
    hmtx = font["hmtx"]
    aw = EXPECTED["advance_width"]
    bad = []

    for name in font.getGlyphOrder():
        w, _ = hmtx[name]
        if w != 0 and w % aw != 0:
            bad.append((name, w))

    if not bad:
        results.ok(cat, f"All glyph widths are 0 or multiples of {aw}")
    else:
        results.fail(cat, f"{len(bad)} glyphs have non-multiple-of-{aw} widths")
        for name, w in bad[:10]:
            results.fail(cat, f"  {name}: width={w}")
        if len(bad) > 10:
            results.fail(cat, f"  ... and {len(bad) - 10} more")

    # Check that non-ligature glyphs are exactly 618 or 0
    # Ligature names may be truncated by post-process.py (losing .liga suffix),
    # so also treat glyphs whose width is a clean multiple of 618 (>618) as ligatures
    non_lig_bad = []
    for name in font.getGlyphOrder():
        w, _ = hmtx[name]
        is_ligature = ".liga" in name or (w > aw and w % aw == 0)
        if not is_ligature and w != 0 and w != aw:
            non_lig_bad.append((name, w))

    if not non_lig_bad:
        results.ok(cat, f"All non-ligature glyphs have width {aw} or 0")
    else:
        results.fail(cat, f"{len(non_lig_bad)} non-ligature glyphs have unexpected width")
        for name, w in non_lig_bad[:10]:
            results.fail(cat, f"  {name}: width={w}")


def validate_block_cell(font, label, results):
    """Block Elements must tile: one cell, identical in every master.

    U+2580-259F are geometric fill primitives, so their outlines must not be
    weight-derived or italic-sheared -- if they are, adjacent cells seam or
    overlap and the amount changes with `wght`. found exactly that:
    the range had been through `offset_paths()` and the shear, so the blocks
    grew and shrank per master, the upper and lower half-blocks missed each
    other by 50 units, and RIGHT HALF BLOCK sat in the left half at every
    weight but Regular. The expected cell comes from the normalizer that draws
    them, so the two cannot drift apart.
    """
    cat = f"Block cell [{label}]"

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import importlib
        blocks = importlib.import_module("normalize-block-elements")
    except Exception as e:                                  # pragma: no cover
        results.fail(cat, f"cannot load the block-element geometry: {e}")
        return

    from fontTools.pens.boundsPen import BoundsPen

    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    codepoints = sorted(set(blocks.RECTS) | set(blocks.SHADES))

    bad = []
    for cp in codepoints:
        name = cmap.get(cp)
        if name is None:
            bad.append(f"U+{cp:04X}: not in cmap")
            continue
        pen = BoundsPen(glyphset)
        glyphset[name].draw(pen)
        if pen.bounds is None:
            bad.append(f"U+{cp:04X}: empty outline")
            continue
        x0, y0, x1, y1 = (round(v) for v in pen.bounds)
        if cp in blocks.SHADES:
            expected = (blocks.L, blocks.B, blocks.R, blocks.T)
        else:
            rects = blocks.RECTS[cp]
            expected = (
                min(r[0] for r in rects), min(r[1] for r in rects),
                max(r[2] for r in rects), max(r[3] for r in rects),
            )
        if (x0, y0, x1, y1) != expected:
            bad.append(f"U+{cp:04X} ({name}): {(x0, y0, x1, y1)} != {expected}")

    if bad:
        results.fail(cat, f"{len(bad)} of {len(codepoints)} block glyphs are off the cell")
        for line in bad[:10]:
            results.fail(cat, f"  {line}")
        if len(bad) > 10:
            results.fail(cat, f"  ... and {len(bad) - 10} more")
    else:
        results.ok(
            cat,
            f"All {len(codepoints)} block elements sit on the "
            f"x {blocks.L}-{blocks.R}, y {blocks.B}-{blocks.T} cell",
        )

    # And they must be flat across the design space: any gvar delta here means
    # weight derivation or the italic shear has got at them again.
    if "gvar" in font:
        varying = sorted(
            cmap[cp] for cp in codepoints
            if cmap.get(cp) and any(
                any(d is not None and d != (0, 0) for d in v.coordinates)
                for v in font["gvar"].variations.get(cmap[cp], [])
            )
        )
        if varying:
            results.fail(
                cat,
                f"{len(varying)} block glyphs vary across the axes "
                f"(must be identical in all masters): {', '.join(varying[:8])}",
            )
        else:
            results.ok(cat, "No block element varies across wght or slnt")


def validate_box_cell(font, label, results):
    """Box Drawing must tile: one cell, arms on the cell edge, slant-invariant.

    U+2500-257F are grid primitives like the Block Elements, but unlike them
    their stroke weight legitimately varies, so this cannot assert "no
    variation" outright. found three faults stacked: every
    non-Regular master had glyphs displaced inside the cell by up to 134 units
    (at Thin the stem of U+2524 sat at x 418..468 instead of straddling 309);
    the weight offset changed arm length so arms missed the cell edge; and
    Regular itself was drawn on five inconsistent grids.

    So the assertions are: geometry matches what normalize-box-drawing.py
    defines, at the default instance and at both ends of the weight axis; and
    nothing varies along slnt, since the range is slant-invariant by decision.
    """
    cat = f"Box cell [{label}]"

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import importlib
        box = importlib.import_module("normalize-box-drawing")
    except Exception as e:                                  # pragma: no cover
        results.fail(cat, f"cannot load the box-drawing geometry: {e}")
        return

    from fontTools.pens.boundsPen import BoundsPen

    ref = {cp: box.read_contours("Regular", cp) for cp in box.DOUBLE_RANGE}

    def expected(master, cp):
        pts = [p for c in box.build(master, cp, ref) for p, _ in c]
        return tuple(round(v) for v in (
            min(q[0] for q in pts), min(q[1] for q in pts),
            max(q[0] for q in pts), max(q[1] for q in pts)))

    def actual(f, cp):
        name = f.getBestCmap().get(cp)
        if name is None:
            return None
        pen = BoundsPen(f.getGlyphSet())
        f.getGlyphSet()[name].draw(pen)
        return None if pen.bounds is None else tuple(round(v) for v in pen.bounds)

    cps = list(range(0x2500, 0x2580))

    bad = []
    for cp in cps:
        a, e = actual(font, cp), expected("Regular", cp)
        if a != e:
            bad.append(f"U+{cp:04X}: {a} != {e}")
    if bad:
        results.fail(cat, f"{len(bad)} of {len(cps)} box glyphs are off the cell "
                          f"at the default instance")
        for line in bad[:8]:
            results.fail(cat, f"  {line}")
        if len(bad) > 8:
            results.fail(cat, f"  ... and {len(bad) - 8} more")
    else:
        results.ok(cat, f"All {len(cps)} box-drawing glyphs match the generated "
                        f"geometry at the default instance")

    if "gvar" not in font:
        return

    # Slant invariance: any tuple whose slnt peak is non-zero must carry no
    # deltas. This is the fault that sheared the range in the first place.
    axes = [a.axisTag for a in font["fvar"].axes]
    if "slnt" in axes:
        cmap = font.getBestCmap()
        sheared = []
        for cp in cps:
            name = cmap.get(cp)
            for var in font["gvar"].variations.get(name, []):
                peak = var.axes.get("slnt", (0, 0, 0))[1]
                if peak and any(d is not None and d != (0, 0)
                                for d in var.coordinates):
                    sheared.append(name)
                    break
        if sheared:
            results.fail(cat, f"{len(sheared)} box glyphs vary along slnt "
                              f"(the range is slant-invariant): "
                              f"{', '.join(sorted(sheared)[:8])}")
        else:
            results.ok(cat, "No box-drawing glyph varies along slnt")

    # And the weight extremes, where the displacement actually showed.
    if "glyf" not in font or "wght" not in axes:
        return
    from fontTools.varLib.instancer import instantiateVariableFont
    for master, wght in (("Thin", 100), ("ExtraBold", 800)):
        try:
            inst = instantiateVariableFont(font, {"wght": wght, "slnt": 0},
                                           inplace=False, updateFontNames=False)
        except Exception as e:                              # pragma: no cover
            results.warn(cat, f"could not instance wght={wght}: {e}")
            continue
        off = [f"U+{cp:04X}: {actual(inst, cp)} != {expected(master, cp)}"
               for cp in cps if actual(inst, cp) != expected(master, cp)]
        if off:
            results.fail(cat, f"{len(off)} box glyphs are off the cell at {master}")
            for line in off[:6]:
                results.fail(cat, f"  {line}")
        else:
            results.ok(cat, f"All {len(cps)} box-drawing glyphs match at {master}")


def validate_axes(font, label, results):
    """Validate fvar axis ranges and defaults."""
    cat = f"Axes [{label}]"

    if "fvar" not in font:
        results.fail(cat, "No fvar table (not a variable font)")
        return

    fvar = font["fvar"]
    axis_map = {}
    for a in fvar.axes:
        axis_map[a.axisTag] = {
            "min": a.minValue,
            "default": a.defaultValue,
            "max": a.maxValue,
        }

    for tag, expected in EXPECTED_AXES.items():
        if tag not in axis_map:
            results.fail(cat, f"Missing axis: {tag}")
            continue

        actual = axis_map[tag]
        match = True
        for k in ("min", "default", "max"):
            if actual[k] != expected[k]:
                results.fail(cat, f"{tag} {k}: {actual[k]}, expected {expected[k]}")
                match = False
        if match:
            results.ok(cat, f"{tag} axis: {actual['min']}..{actual['default']}..{actual['max']}")

    # Warn about unexpected axes
    for tag in axis_map:
        if tag not in EXPECTED_AXES:
            results.warn(cat, f"Unexpected axis: {tag}")


def validate_stat(font, label, results):
    """Validate STAT table presence and axis value entries."""
    cat = f"STAT [{label}]"

    if "STAT" not in font:
        results.fail(cat, "No STAT table")
        return

    stat = font["STAT"].table

    if stat.DesignAxisRecord is None or len(stat.DesignAxisRecord.Axis) == 0:
        results.fail(cat, "STAT has no design axis records")
    else:
        axis_tags = [a.AxisTag for a in stat.DesignAxisRecord.Axis]
        for tag in EXPECTED_AXES:
            if tag in axis_tags:
                results.ok(cat, f"STAT axis {tag} present")
            else:
                results.fail(cat, f"STAT axis {tag} missing")

    if stat.AxisValueArray is None or len(stat.AxisValueArray.AxisValue) == 0:
        results.fail(cat, "STAT has no axis value entries (run inject-stat.py)")
    else:
        count = len(stat.AxisValueArray.AxisValue)
        expected_count = 9  # 8 wght + 1 slnt
        if count == expected_count:
            results.ok(cat, f"STAT has {count} axis value entries")
        else:
            results.warn(cat, f"STAT has {count} axis value entries, expected {expected_count}")

        # Check that Regular has elidable flag (flags=2)
        name_table = font["name"]
        has_elidable_regular = False
        for v in stat.AxisValueArray.AxisValue:
            name = name_table.getDebugName(v.ValueNameID)
            flags = getattr(v, "Flags", 0)
            if name == "Regular" and (flags & 0x0002):
                has_elidable_regular = True
        if has_elidable_regular:
            results.ok(cat, "Regular has ELIDABLE_AXIS_VALUE_NAME flag")
        else:
            results.fail(cat, "Regular missing ELIDABLE_AXIS_VALUE_NAME flag")


def validate_coverage(font, label, results):
    """Validate glyph coverage for required Unicode ranges."""
    cat = f"Coverage [{label}]"

    cmap = font.getBestCmap()
    if cmap is None:
        results.fail(cat, "No cmap table")
        return

    codepoints = set(cmap.keys())
    results.ok(cat, f"cmap has {len(codepoints)} entries")

    # Full ranges
    for range_name, (start, end) in COVERAGE_RANGES.items():
        expected = set(range(start, end + 1)) - COVERAGE_EXCEPTIONS
        missing = expected - codepoints
        if not missing:
            results.ok(cat, f"{range_name} (U+{start:04X}–U+{end:04X}) complete")
        else:
            results.fail(cat, f"{range_name}: {len(missing)} missing codepoints")
            for cp in sorted(missing)[:5]:
                results.fail(cat, f"  missing U+{cp:04X}")
            if len(missing) > 5:
                results.fail(cat, f"  ... and {len(missing) - 5} more")

    # Spot checks
    for group_name, cps in COVERAGE_REQUIRED.items():
        missing = [cp for cp in cps if cp not in codepoints]
        if not missing:
            results.ok(cat, f"{group_name}: all {len(cps)} codepoints present")
        else:
            results.fail(cat, f"{group_name}: {len(missing)}/{len(cps)} missing")
            for cp in missing:
                results.fail(cat, f"  missing U+{cp:04X}")

    return codepoints


def validate_features(font, label, results):
    """Validate GSUB feature set."""
    cat = f"Features [{label}]"

    if "GSUB" not in font:
        results.fail(cat, "No GSUB table")
        return set()

    gsub = font["GSUB"].table
    actual = set()
    if gsub.FeatureList:
        for fr in gsub.FeatureList.FeatureRecord:
            actual.add(fr.FeatureTag)

    results.ok(cat, f"GSUB has {len(actual)} feature tags")

    missing = EXPECTED_FEATURES - actual
    extra = actual - EXPECTED_FEATURES

    if not missing:
        results.ok(cat, f"All {len(EXPECTED_FEATURES)} expected features present")
    else:
        for f_tag in sorted(missing):
            results.fail(cat, f"Missing feature: {f_tag}")

    if extra:
        for f_tag in sorted(extra):
            results.warn(cat, f"Unexpected feature: {f_tag}")

    # Check that feature lookups are non-empty
    empty = []
    if gsub.FeatureList:
        for fr in gsub.FeatureList.FeatureRecord:
            if not fr.Feature.LookupListIndex:
                empty.append(fr.FeatureTag)
    if empty:
        for f_tag in set(empty):
            results.warn(cat, f"Feature {f_tag} has empty lookup list")
    else:
        results.ok(cat, "All feature lookups are non-empty")

    return actual


def validate_name_table(font, label, results):
    """Check for common name table issues."""
    cat = f"Names [{label}]"

    name = font["name"]
    records = name.names

    # Check for duplicate nameIDs (same platformID + encodingID + languageID + nameID)
    seen = set()
    dupes = []
    for r in records:
        key = (r.platformID, r.platEncID, r.langID, r.nameID)
        if key in seen:
            dupes.append(key)
        seen.add(key)

    if not dupes:
        results.ok(cat, f"No duplicate name records ({len(records)} total)")
    else:
        results.fail(cat, f"{len(dupes)} duplicate name records")

    # Check family name is present
    family_name = name.getDebugName(1) or name.getDebugName(16)
    if family_name and "Buena Mono" in family_name:
        results.ok(cat, f"Family name: {family_name}")
    else:
        results.fail(cat, f"Family name missing or wrong: {family_name}")


def validate_cross_format(fonts, results):
    """Compare glyph sets and features across all loaded formats."""
    cat = "Cross-format"

    if len(fonts) < 2:
        results.warn(cat, "Need at least 2 formats to compare")
        return

    labels = list(fonts.keys())
    ref_label = labels[0]
    ref_font = fonts[ref_label]

    ref_glyphs = set(ref_font.getGlyphOrder())
    ref_cmap = set(ref_font.getBestCmap().keys()) if ref_font.getBestCmap() else set()
    ref_features = set()
    if "GSUB" in ref_font and ref_font["GSUB"].table.FeatureList:
        ref_features = {fr.FeatureTag for fr in ref_font["GSUB"].table.FeatureList.FeatureRecord}

    for other_label in labels[1:]:
        other = fonts[other_label]

        # Glyph count
        other_glyphs = set(other.getGlyphOrder())
        if len(ref_glyphs) == len(other_glyphs):
            results.ok(cat, f"Glyph count match: {ref_label} ({len(ref_glyphs)}) = {other_label} ({len(other_glyphs)})")
        else:
            results.fail(cat, f"Glyph count mismatch: {ref_label} ({len(ref_glyphs)}) vs {other_label} ({len(other_glyphs)})")
            diff = ref_glyphs.symmetric_difference(other_glyphs)
            for g in sorted(diff)[:5]:
                where = ref_label if g in ref_glyphs else other_label
                results.fail(cat, f"  {g} only in {where}")

        # cmap
        other_cmap = set(other.getBestCmap().keys()) if other.getBestCmap() else set()
        if ref_cmap == other_cmap:
            results.ok(cat, f"cmap match: {ref_label} = {other_label} ({len(ref_cmap)} entries)")
        else:
            diff = ref_cmap.symmetric_difference(other_cmap)
            results.fail(cat, f"cmap mismatch: {len(diff)} differing codepoints between {ref_label} and {other_label}")
            for cp in sorted(diff)[:5]:
                where = ref_label if cp in ref_cmap else other_label
                results.fail(cat, f"  U+{cp:04X} only in {where}")

        # Features
        other_features = set()
        if "GSUB" in other and other["GSUB"].table.FeatureList:
            other_features = {fr.FeatureTag for fr in other["GSUB"].table.FeatureList.FeatureRecord}
        if ref_features == other_features:
            results.ok(cat, f"Feature set match: {ref_label} = {other_label}")
        else:
            diff = ref_features.symmetric_difference(other_features)
            results.fail(cat, f"Feature set mismatch: {sorted(diff)} between {ref_label} and {other_label}")


# ---------------------------------------------------------------------------
# Source validation helpers (adapted from fix-weight-consistency.py,
# add-weight-extremes.py)
# ---------------------------------------------------------------------------

def _nodes_to_tuples(gspath):
    """Convert a GSPath's nodes to [(x, y, type), ...] tuples."""
    return [(n.position.x, n.position.y, n.type) for n in gspath.nodes]


def shoelace_area(contour):
    """Compute signed area via shoelace formula.

    In font coordinates (y up): Positive = CCW (counter-clockwise),
    Negative = CW (clockwise). Only considers on-curve points (line/curve).
    """
    pts = [(x, y) for (x, y, t) in contour if t in ('line', 'curve')]
    n = len(pts)
    if n < 3:
        return 0
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]
    return area / 2


def reverse_contour(contour):
    """Reverse contour node order to flip winding direction.

    After reversing, on-curve types are reassigned:
    - If preceded by offcurve → 'curve'
    - If preceded by on-curve → 'line'
    """
    if not contour:
        return contour
    rev = list(reversed(contour))
    n = len(rev)
    result = []
    for i in range(n):
        x, y, t = rev[i]
        if t in ('line', 'curve'):
            prev_idx = (i - 1) % n
            prev_type = rev[prev_idx][2]
            if prev_type == 'offcurve':
                result.append((x, y, 'curve'))
            else:
                result.append((x, y, 'line'))
        else:
            result.append((x, y, t))
    return result


def _apply_tuples_to_path(gspath, tuples):
    """Write [(x, y, type), ...] tuples back into a GSPath's nodes."""
    for i, (x, y, t) in enumerate(tuples):
        gspath.nodes[i].position.x = x
        gspath.nodes[i].position.y = y
        gspath.nodes[i].type = t


def _oncurve_points(contour):
    """On-curve points (line/curve) of a node-tuple contour as (x, y) pairs."""
    return [(x, y) for (x, y, t) in contour if t in ('line', 'curve')]


def _winding_number(pt, poly):
    """Winding number of a point wrt a polygon's on-curve points.

    Nonzero => the point lies inside the polygon. Robust for self-touching
    contours (unlike a parity ray-cast).
    """
    x, y = pt
    w = 0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if y0 <= y:
            if y1 > y and ((x1 - x0) * (y - y0) - (x - x0) * (y1 - y0)) > 0:
                w += 1
        else:
            if y1 <= y and ((x1 - x0) * (y - y0) - (x - x0) * (y1 - y0)) < 0:
                w -= 1
    return w


def _contour_contains(child_pts, parent_pts):
    """True if parent geometrically contains child.

    Bounding-box prefilter, then a majority vote: a child is contained when
    most of its on-curve points have nonzero winding inside the parent. The
    majority vote tolerates shared/touching edges (e.g. adjacent block cells).
    """
    if len(child_pts) < 3 or len(parent_pts) < 3:
        return False
    cx0 = min(p[0] for p in child_pts); cy0 = min(p[1] for p in child_pts)
    cx1 = max(p[0] for p in child_pts); cy1 = max(p[1] for p in child_pts)
    px0 = min(p[0] for p in parent_pts); py0 = min(p[1] for p in parent_pts)
    px1 = max(p[0] for p in parent_pts); py1 = max(p[1] for p in parent_pts)
    if not (px0 <= cx0 and py0 <= cy0 and px1 >= cx1 and py1 >= cy1):
        return False
    inside = sum(1 for p in child_pts if _winding_number(p, parent_pts) != 0)
    return inside > len(child_pts) // 2


def _nesting_targets(areas, oncurve):
    """Classify contours by geometric nesting and return per-contour winding.

    A glyph can have several disjoint outer contours (colon, percent, dotted
    i/j, box-drawing/math glyphs, ...), so "outer vs counter" cannot be decided
    by area alone. We build the containment forest, then require alternating
    winding by nesting depth: a contour at even depth must match its root
    contour's direction, odd depth must oppose it (the non-zero-fill invariant).

    The absolute direction of top-level (depth-0) contours is intentionally NOT
    constrained — this source mixes CW/CCW outers (PostScript heritage) and
    ufo2ft normalizes winding at build, so it does not affect output.

    Returns a list of target signs (+1/-1) per contour; None means unconstrained
    (top-level or zero-area).
    """
    n = len(areas)
    parents = [
        [j for j in range(n)
         if j != i and areas[j] != 0 and areas[i] != 0
         and _contour_contains(oncurve[i], oncurve[j])]
        for i in range(n)
    ]
    depth = [len(parents[i]) for i in range(n)]

    targets = [None] * n
    for i in range(n):
        if areas[i] == 0 or depth[i] == 0:
            continue  # zero-area or top-level: unconstrained
        # Root = the container in i's chain that itself has no container.
        root = next((j for j in parents[i] if depth[j] == 0), None)
        if root is None:
            continue
        root_sign = 1 if areas[root] > 0 else -1
        targets[i] = root_sign if depth[i] % 2 == 0 else -root_sign
    return targets


def validate_source_winding(font, results, fix=False):
    """Check that nested contours alternate winding by depth (fill correctness).

    The old check assumed the single largest-area contour was the only outer
    and everything else a counter, which mislabeled the many glyphs with
    multiple disjoint outer contours and produced thousands of false positives.
    This classifies by geometric nesting instead (see _nesting_targets).

    Violations are reported as warnings: they are genuine source inconsistencies
    (and matter before offset_paths weight derivation) but do not affect the
    built font, since ufo2ft normalizes winding at build. When fixing, the
    reversal decision is made on the first master layer and applied identically
    across ALL masters to preserve topology (matching node types); because the
    targets are absolute (anchored to the never-reversed root), a single pass
    converges.
    """
    cat = "Source Winding"
    master_ids = [m.id for m in font.masters]  # ordered list
    bad_glyphs = []  # (glyph_name, path_idx, depth)
    fixed_count = 0

    for glyph in font.glyphs:
        # Get master layers in order
        layers = []
        for mid in master_ids:
            layer = next((l for l in glyph.layers if l.layerId == mid), None)
            if layer is None:
                break
            layers.append(layer)
        if len(layers) != len(master_ids):
            continue
        ref_layer = layers[0]
        if len(ref_layer.paths) < 2:
            continue  # a single contour cannot contain a counter

        # Classify nesting on the FIRST master, apply any fix to all masters.
        contours = [_nodes_to_tuples(p) for p in ref_layer.paths]
        oncurve = [_oncurve_points(c) for c in contours]
        areas = [shoelace_area(c) for c in contours]
        targets = _nesting_targets(areas, oncurve)

        needs_reverse = set()
        for i, target in enumerate(targets):
            if target is None:
                continue
            sign = 1 if areas[i] > 0 else -1
            if sign != target:
                needs_reverse.add(i)
                bad_glyphs.append((glyph.name, i, None))

        # Apply fix consistently across ALL masters
        if fix and needs_reverse:
            for layer in layers:
                for i in needs_reverse:
                    c = _nodes_to_tuples(layer.paths[i])
                    _apply_tuples_to_path(layer.paths[i], reverse_contour(c))
                    fixed_count += 1

    if not bad_glyphs:
        results.ok(cat, "Nested contour winding alternates correctly by depth")
    elif fix:
        affected = len(set(g for g, *_ in bad_glyphs))
        results.ok(cat, f"Fixed winding on {fixed_count} contours across {affected} glyphs")
    else:
        affected = len(set(g for g, *_ in bad_glyphs))
        results.warn(cat, f"{len(bad_glyphs)} nested contours wind against their depth "
                          f"across {affected} glyphs (auto-fixable with --fix; "
                          f"ufo2ft normalizes winding at build)")
        for name, pi, _ in bad_glyphs[:10]:
            results.warn(cat, f"  {name} path {pi}")
        if len(bad_glyphs) > 10:
            results.warn(cat, f"  ... and {len(bad_glyphs) - 10} more")

    return len(bad_glyphs)


def validate_source_degenerate(font, results, fix=False):
    """Flag zero-length segments: consecutive on-curve points at identical coords.

    These are typically artifacts of weight-offset derivation collapsing a thin
    stroke. ufo2ft/cu2qu drops zero-length segments during the build, so they do
    NOT reach the built font (verified: 0 in output). Reported as warnings —
    deduplicated to distinct logical points (a point degenerate in N masters was
    previously counted N times, inflating the total and hiding the master) and
    auto-fixable with --fix (nudges the duplicate point by 1 unit per master).
    """
    cat = "Source Degenerate"
    master_names = {m.id: m.name for m in font.masters}
    points = {}  # (glyph, path_idx, node_idx) -> set(master names)
    fixed_count = 0

    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.layerId not in master_names:
                continue
            for pi, gspath in enumerate(layer.paths):
                nodes = gspath.nodes
                n = len(nodes)
                for i in range(n):
                    n1, n2 = nodes[i], nodes[(i + 1) % n]
                    if (n1.type in ('line', 'curve') and n2.type in ('line', 'curve')
                            and n1.position.x == n2.position.x
                            and n1.position.y == n2.position.y):
                        points.setdefault((glyph.name, pi, i), set()).add(
                            master_names[layer.layerId])
                        if fix:
                            n2.position.x += 1
                            fixed_count += 1

    glyphs_affected = len(set(g for g, _, _ in points))
    if not points:
        results.ok(cat, "No degenerate (zero-length) segments found")
    elif fix:
        results.ok(cat, f"Fixed {fixed_count} degenerate points across {glyphs_affected} glyphs")
    else:
        results.warn(cat, f"{len(points)} zero-length segments across {glyphs_affected} "
                          f"glyphs (auto-fixable with --fix; ufo2ft drops them at build)")
        for (name, pi, ni), masters in list(points.items())[:10]:
            results.warn(cat, f"  {name} path {pi} node {ni} ({len(masters)} masters)")
        if len(points) > 10:
            results.warn(cat, f"  ... and {len(points) - 10} more")

    return len(points)


def validate_source_topology(font, results):
    """Verify all masters have matching path count, node count, and node types per glyph."""
    cat = "Source Topology"
    master_ids = {m.id for m in font.masters}
    expected_masters = len(font.masters)
    bad = []

    for glyph in font.glyphs:
        layers = [l for l in glyph.layers if l.layerId in master_ids]

        if len(layers) != expected_masters:
            bad.append((glyph.name, f"expected {expected_masters} layers, got {len(layers)}"))
            continue

        path_counts = [len(l.paths) for l in layers]
        if len(set(path_counts)) > 1:
            bad.append((glyph.name, f"path count mismatch: {set(path_counts)}"))
            continue

        if path_counts[0] == 0:
            continue

        for pi in range(path_counts[0]):
            node_counts = [len(l.paths[pi].nodes) for l in layers]
            if len(set(node_counts)) > 1:
                bad.append((glyph.name, f"path {pi} node count mismatch: {set(node_counts)}"))
                break

            ref_types = [n.type for n in layers[0].paths[pi].nodes]
            for li, layer in enumerate(layers[1:], 1):
                layer_types = [n.type for n in layer.paths[pi].nodes]
                if layer_types != ref_types:
                    bad.append((glyph.name, f"path {pi} node type mismatch in master {li}"))
                    break
            else:
                continue
            break

    if not bad:
        results.ok(cat, f"All {len(font.glyphs)} glyphs have consistent topology across {expected_masters} masters")
    else:
        results.fail(cat, f"{len(bad)} glyphs with topology issues (NOT auto-fixable)")
        for name, reason in bad[:10]:
            results.fail(cat, f"  {name}: {reason}")
        if len(bad) > 10:
            results.fail(cat, f"  ... and {len(bad) - 10} more")

    return len(bad)


def validate_source_collapsed(font, results):
    """Check for contours with bbox < 5u in both dimensions (collapsed strokes)."""
    cat = "Source Collapsed"
    master_ids = {m.id for m in font.masters}
    master_names = {m.id: m.name for m in font.masters}
    bad = []

    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.layerId not in master_ids:
                continue
            for pi, gspath in enumerate(layer.paths):
                if not gspath.nodes:
                    continue
                xs = [n.position.x for n in gspath.nodes]
                ys = [n.position.y for n in gspath.nodes]
                bbox_w = max(xs) - min(xs)
                bbox_h = max(ys) - min(ys)
                if bbox_w < COLLAPSE_THRESHOLD and bbox_h < COLLAPSE_THRESHOLD:
                    mname = master_names.get(layer.layerId, layer.layerId)
                    bad.append((glyph.name, mname, pi, bbox_w, bbox_h))

    if not bad:
        results.ok(cat, "No collapsed contours found")
    else:
        results.warn(cat, f"{len(bad)} collapsed contours found (NOT auto-fixable)")
        for name, mname, pi, bw, bh in bad[:10]:
            results.warn(cat, f"  {name} path {pi} bbox={bw:.0f}x{bh:.0f} in {mname}")
        if len(bad) > 10:
            results.warn(cat, f"  ... and {len(bad) - 10} more")

    return len(bad)


def validate_source(source_path, results, fix=False):
    """Run all source-level validations on a .glyphs file."""
    import glyphsLib

    cat = "Source Load"
    try:
        font = glyphsLib.load(str(source_path))
    except Exception as e:
        results.fail(cat, f"Failed to load {source_path}: {e}")
        return False

    results.ok(cat, f"Loaded {source_path.name}: {len(font.glyphs)} glyphs, {len(font.masters)} masters")

    winding_issues = validate_source_winding(font, results, fix=fix)
    degenerate_issues = validate_source_degenerate(font, results, fix=fix)
    topology_issues = validate_source_topology(font, results)
    collapsed_issues = validate_source_collapsed(font, results)

    # If --fix was used and issues were fixed, save the file
    if fix and (winding_issues > 0 or degenerate_issues > 0):
        with open(str(source_path), "wb") as f:
            glyphsLib.dump(font, f)
        results.ok("Source Fix", f"Saved fixes to {source_path.name}")

    # Topology issues are blockers (not auto-fixable)
    return topology_issues == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Buena Mono QA Validation")
    parser.add_argument("--source", help="Path to .glyphs source file for source-level validation")
    parser.add_argument("--fix", action="store_true", help="Auto-fix fixable source issues (winding, degenerate points)")
    parser.add_argument("--font-dir", default=None, help="Directory containing built fonts")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    # Default: if neither --source nor --font-dir given, validate built fonts
    if args.source is None and args.font_dir is None:
        args.font_dir = "out/fonts"

    if args.fix and not args.source:
        parser.error("--fix requires --source")

    results = Results()

    # --- Source validation ---
    if args.source:
        source_path = Path(args.source)
        if not source_path.exists():
            results.fail("Source Load", f"Source file not found: {source_path}")
            print_results(results, args.json)
            return 1
        validate_source(source_path, results, fix=args.fix)

    # --- Built-font validation ---
    if args.font_dir:
        font_dir = Path(args.font_dir)

        # 1. File presence
        found_files = validate_file_presence(font_dir, results)

        # 2. Load fonts
        fonts = {}
        for name, path in found_files.items():
            f = load_font(path)
            if f:
                fonts[name] = f
            else:
                results.fail("Load", f"Failed to load {name}")

        if not fonts:
            results.fail("Load", "No fonts could be loaded, aborting")
            print_results(results, args.json)
            return 1

        # 3. Per-font checks
        for label, font in fonts.items():
            validate_metrics(font, label, results)
            validate_advance_widths(font, label, results)
            validate_block_cell(font, label, results)
            validate_box_cell(font, label, results)
            validate_axes(font, label, results)
            validate_stat(font, label, results)
            validate_coverage(font, label, results)
            validate_features(font, label, results)
            validate_name_table(font, label, results)

        # 4. Cross-format parity
        validate_cross_format(fonts, results)

        # 5. Close fonts
        for f in fonts.values():
            f.close()

    # 6. Report
    print_results(results, args.json)
    return 0 if results.passed else 1


def print_results(results, as_json=False):
    if as_json:
        print(json.dumps(results.to_dict(), indent=2))
        return

    # Header
    print()
    print("=" * 60)
    print("  Buena Mono QA Validation Report")
    print("=" * 60)

    # Failures
    if results.failures:
        print(f"\n  FAILURES ({len(results.failures)})")
        print("  " + "-" * 56)
        for cat, msg in results.failures:
            print(f"  FAIL  {cat}: {msg}")

    # Warnings
    if results.warnings:
        print(f"\n  WARNINGS ({len(results.warnings)})")
        print("  " + "-" * 56)
        for cat, msg in results.warnings:
            print(f"  WARN  {cat}: {msg}")

    # Summary
    print()
    print("  " + "-" * 56)
    status = "PASS" if results.passed else "FAIL"
    print(f"  [{status}] {results.summary()}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    sys.exit(main())
