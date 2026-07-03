#!/usr/bin/env python3
"""Post-build processing for Google Fonts compliance.

Fixes applied to compiled TTF/OTF fonts:
1. Add meta table with dlng/slng script-language tags
2. Recompute xAvgCharWidth per spec (mean advance of non-zero-width glyphs)
3. Remove Mac platform name records (Google Fonts requirement)
4. Add avar table (identity mapping)
5. Truncate legacy long glyph names (>31 chars)
6. Report contour directions and numberOfHMetrics

Usage:
    python3 scripts/post-process.py [--font-dir out/fonts]
"""

import argparse
import hashlib
import sys
from pathlib import Path

from fontTools.ttLib import TTFont


def add_meta_table(font):
    """Add meta table with script/language coverage tags."""
    from fontTools.ttLib.tables._m_e_t_a import table__m_e_t_a

    meta = table__m_e_t_a()
    meta.data = {
        "dlng": "Cyrl, Grek, Latn",
        "slng": "Cyrl, Grek, Latn",
    }
    font["meta"] = meta
    return True


def fix_xavgcharwidth(font):
    """Recompute OS/2.xAvgCharWidth per the spec (mean advance of non-zero-width
    glyphs). The previous hardcoded 711 was wrong — it pushed the value far above
    the true average (~651) because it over-weighted the multi-cell ligatures."""
    os2 = font["OS/2"]
    old = os2.xAvgCharWidth
    os2.recalcAvgCharWidth(font)
    if os2.xAvgCharWidth != old:
        print(f"    xAvgCharWidth: {old} -> {os2.xAvgCharWidth}")
        return True
    return False


def remove_mac_names(font):
    """Remove Mac platform (platformID=1) name records for Google Fonts."""
    name_table = font["name"]
    mac_records = [r for r in name_table.names if r.platformID == 1]
    if not mac_records:
        return False
    name_table.names = [r for r in name_table.names if r.platformID != 1]
    print(f"    Removed {len(mac_records)} Mac platform name records")
    return True


def report_contour_directions(font):
    """Report glyphs with CCW outer contours."""
    if "glyf" not in font:
        return

    glyf = font["glyf"]
    fixed = 0

    for gname in font.getGlyphOrder():
        glyph = glyf[gname]
        if glyph.numberOfContours <= 0:
            continue

        coords, endPts, flags = glyph.getCoordinates(glyf)
        if not endPts:
            continue

        contour_areas = []
        start = 0
        for end in endPts:
            area = 0.0
            n = end - start + 1
            for j in range(n):
                idx1 = start + j
                idx2 = start + (j + 1) % n
                x1, y1 = coords[idx1]
                x2, y2 = coords[idx2]
                area += (x2 - x1) * (y2 + y1)
            contour_areas.append(area)
            start = end + 1

        if not contour_areas:
            continue

        abs_areas = [abs(a) for a in contour_areas]
        outer_idx = abs_areas.index(max(abs_areas))
        if contour_areas[outer_idx] < 0:
            fixed += 1

    if fixed:
        print(f"    {fixed} glyphs with CCW outer contours")


def truncate_long_names(font):
    """Truncate glyph names longer than 31 characters."""
    glyph_order = font.getGlyphOrder()
    renames = {}

    for gname in glyph_order:
        if len(gname) > 31:
            h = hashlib.md5(gname.encode()).hexdigest()[:4]
            truncated = gname[:26] + "_" + h
            renames[gname] = truncated

    if not renames:
        return False

    # Rename in glyf table BEFORE updating glyph order
    if "glyf" in font:
        glyf = font["glyf"]
        for old, new in renames.items():
            if old in glyf.glyphs:
                glyf.glyphs[new] = glyf.glyphs.pop(old)

    # Rename in hmtx table
    if "hmtx" in font:
        hmtx = font["hmtx"]
        for old, new in renames.items():
            if old in hmtx.metrics:
                hmtx.metrics[new] = hmtx.metrics.pop(old)

    # Update glyph order
    new_order = [renames.get(g, g) for g in glyph_order]
    font.setGlyphOrder(new_order)

    # Update cmap
    if "cmap" in font:
        for table in font["cmap"].tables:
            if hasattr(table, "cmap"):
                for cp, gname in list(table.cmap.items()):
                    if gname in renames:
                        table.cmap[cp] = renames[gname]

    # Update post table
    if "post" in font:
        post = font["post"]
        if hasattr(post, "extraNames"):
            post.extraNames = [renames.get(n, n) for n in post.extraNames]

    print(f"    Truncated {len(renames)} long glyph names")
    return True


def report_number_of_hmetrics(font):
    """Report numberOfHMetrics. Cannot be 3 with multi-width ligatures."""
    hhea = font["hhea"]
    if hhea.numberOfHMetrics != 3:
        print(f"    numberOfHMetrics: {hhea.numberOfHMetrics} (cannot be 3 with multi-width ligatures)")


def add_avar_table(font):
    """Add avar table with identity mapping for the wght axis."""
    if "avar" in font:
        return False

    from fontTools.ttLib.tables._a_v_a_r import table__a_v_a_r

    avar = table__a_v_a_r()
    avar.segments = {}

    # Get axis info from fvar
    if "fvar" in font:
        for axis in font["fvar"].axes:
            # Identity mapping: -1→-1, 0→0, 1→1
            avar.segments[axis.axisTag] = {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0}

    font["avar"] = avar
    print(f"    Added avar table (identity mapping)")
    return True


def fix_win_descent(font):
    """Set OS/2.usWinDescent to >= 500 (Google Fonts requirement)."""
    os2 = font["OS/2"]
    if os2.usWinDescent < 500:
        old = os2.usWinDescent
        os2.usWinDescent = 500
        print(f"    usWinDescent: {old} -> 500")
        return True
    return False


def flatten_nested_components(font):
    """Flatten nested TrueType components (Google Fonts requirement).

    Decomposes to simple outlines any glyph that references another
    composite glyph, and also decomposes the intermediate composites
    that are referenced.
    """
    if "glyf" not in font:
        return False

    from fontTools.pens.ttGlyphPen import TTGlyphPointPen
    from fontTools.pens.recordingPen import RecordingPointPen

    glyf = font["glyf"]

    def decompose_glyph(glyf_table, glyph, glyph_name):
        """Recursively decompose a composite glyph to simple outlines."""
        from fontTools.misc.transform import DecomposedTransform
        import math

        if not glyph.isComposite():
            return

        # Collect all simple contours by recursively resolving components
        all_coords = []
        all_flags = []
        all_endpts = []

        for comp in glyph.components:
            ref = glyf_table[comp.glyphName]

            # Recursively decompose if the referenced glyph is also composite
            if ref.isComposite():
                decompose_glyph(glyf_table, ref, comp.glyphName)
                ref = glyf_table[comp.glyphName]

            if ref.numberOfContours <= 0:
                continue

            coords, endPts, flags_arr = ref.getCoordinates(glyf_table)

            # Apply component transform
            t = comp.getComponentInfo()[1]
            import array
            new_coords = []
            for x, y in coords:
                nx = t[0] * x + t[2] * y + t[4]
                ny = t[1] * x + t[3] * y + t[5]
                new_coords.append((int(round(nx)), int(round(ny))))

            offset = len(all_coords)
            all_coords.extend(new_coords)
            all_flags.extend(flags_arr)
            all_endpts.extend(ep + offset for ep in endPts)

        if not all_coords:
            return

        # Replace with simple glyph
        from fontTools.ttLib.tables._g_l_y_f import Glyph
        import array as array_mod

        new_g = Glyph()
        new_g.numberOfContours = len(all_endpts)
        new_g.coordinates = type(glyph.coordinates if hasattr(glyph, 'coordinates') and glyph.coordinates is not None else [])(all_coords) if hasattr(glyph, 'coordinates') and glyph.coordinates is not None else all_coords
        new_g.flags = array_mod.array("B", all_flags)
        new_g.endPtsOfContours = all_endpts

        # Use fontTools' coordinate array type
        from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
        new_g.coordinates = GlyphCoordinates(all_coords)
        from fontTools.ttLib.tables.ttProgram import Program
        new_g.program = Program()

        glyf_table[glyph_name] = new_g
        glyf_table[glyph_name].recalcBounds(glyf_table)

    # Find and decompose all glyphs with nested components
    total_flattened = 0
    for gname in font.getGlyphOrder():
        glyph = glyf[gname]
        if not glyph.isComposite():
            continue
        has_nested = False
        for comp in glyph.components:
            ref = glyf.get(comp.glyphName)
            if ref and ref.isComposite():
                has_nested = True
                break
        if has_nested:
            decompose_glyph(glyf, glyph, gname)
            total_flattened += 1

    if total_flattened:
        print(f"    Flattened {total_flattened} nested components")
        return True
    return False


def reorder_smcp_before_liga(font):
    """Ensure smcp/c2sc lookups come before liga lookups in GSUB.

    Google Fonts requires small caps features to be ordered before ligatures
    so that smcp substitutions happen first.
    """
    if "GSUB" not in font:
        return False

    gsub = font["GSUB"].table
    if not gsub.FeatureList or not gsub.FeatureList.FeatureRecord:
        return False

    # Build feature tag → lookup index mapping
    feature_lookups = {}
    for fr in gsub.FeatureList.FeatureRecord:
        tag = fr.FeatureTag
        if tag not in feature_lookups:
            feature_lookups[tag] = []
        feature_lookups[tag].extend(fr.Feature.LookupListIndex)

    smcp_tags = {"smcp", "c2sc"}
    liga_tags = {"liga", "calt"}

    smcp_lookups = set()
    liga_lookups = set()
    for tag, indices in feature_lookups.items():
        if tag in smcp_tags:
            smcp_lookups.update(indices)
        elif tag in liga_tags:
            liga_lookups.update(indices)

    if not smcp_lookups or not liga_lookups:
        return False

    # Check if any smcp lookup index > any liga lookup index
    if max(smcp_lookups) < min(liga_lookups):
        return False  # Already correctly ordered

    # Reorder: move smcp lookups before liga lookups
    all_lookups = list(range(len(gsub.LookupList.Lookup)))
    other = [i for i in all_lookups if i not in smcp_lookups and i not in liga_lookups]

    # New order: everything before liga, then smcp, then liga, then everything after
    first_liga = min(liga_lookups)
    before = [i for i in other if i < first_liga]
    after = [i for i in other if i >= first_liga]
    new_order = before + sorted(smcp_lookups) + sorted(liga_lookups) + after

    # Build reverse mapping: old index -> new index
    index_map = {old: new for new, old in enumerate(new_order)}

    # Reorder the lookup list
    old_lookups = gsub.LookupList.Lookup[:]
    gsub.LookupList.Lookup = [old_lookups[i] for i in new_order]

    # Update all feature references
    for fr in gsub.FeatureList.FeatureRecord:
        fr.Feature.LookupListIndex = sorted(
            index_map[i] for i in fr.Feature.LookupListIndex if i in index_map
        )

    print(f"    Reordered GSUB: smcp/c2sc before liga/calt")
    return True


def remove_nameid17(font):
    """Remove NameID 17 if it was incorrectly set."""
    name_table = font["name"]
    n17 = name_table.getName(17, 3, 1, 0x0409)
    if n17:
        name_table.removeNames(nameID=17)
        print(f"    Removed NameID 17: '{n17.toUnicode()}'")
        return True
    return False


def add_ligature_carets(font):
    """Add a GDEF LigCaretList with caret positions at cell boundaries for
    multi-cell code ligatures, so text cursors land between the composed
    characters. Fixes the fontbakery `ligature_carets` WARN. Widths are exact
    multiples of the 618 monospace cell (verified), so carets sit at 618, 1236,
    ... up to width-618."""
    from fontTools.ttLib.tables import otTables as ot

    CELL = 618
    gdef = font.get("GDEF")
    if gdef is None or gdef.table is None:
        return False
    if getattr(gdef.table, "LigCaretList", None):
        return False  # already present

    hmtx = font["hmtx"]
    ligs = []
    for gname in font.getGlyphOrder():
        if not gname.endswith(".liga"):
            continue
        w = hmtx[gname][0]
        if w <= CELL or w % CELL != 0:
            continue
        carets = [CELL * i for i in range(1, w // CELL)]
        ligs.append((gname, carets))
    if not ligs:
        return False

    # Coverage requires glyphs in glyph-ID order; LigGlyph list must match.
    ligs.sort(key=lambda t: font.getGlyphID(t[0]))
    lcl = ot.LigCaretList()
    lcl.Coverage = ot.Coverage()
    lcl.Coverage.glyphs = [g for g, _ in ligs]
    lcl.LigGlyphCount = len(ligs)
    lcl.LigGlyph = []
    for _, carets in ligs:
        lg = ot.LigGlyph()
        lg.CaretCount = len(carets)
        lg.CaretValue = []
        for c in carets:
            cv = ot.CaretValue()
            cv.Format = 1
            cv.Coordinate = c
            lg.CaretValue.append(cv)
        lcl.LigGlyph.append(lg)
    gdef.table.LigCaretList = lcl
    print(f"    Added GDEF LigCaretList for {len(ligs)} ligatures")
    return True


STYLISTIC_SET_NAMES = {
    "ss01": "Single-story a",
    "ss02": "Descending f",
    "ss03": "Tailed l",
    "ss04": "Serifed i and j",
    "ss05": "Alternate g",
    "ss06": "Alternate g (2)",
    "ss07": "Serifed i",
    "ss08": "Straight-tail y",
    "ss09": "Curved-tail y",
    "ss10": "Plain zero",
    "ss11": "Dotted zero",
    "ss12": "Alternate r",
}


def add_stylistic_set_names(font):
    """Attach UI names to stylistic-set features (ssXX) via GSUB FeatureParams +
    name records, so apps (InDesign, etc.) show human-readable labels. Fixes the
    fontbakery `stylisticset_description` WARN."""
    from fontTools.ttLib.tables import otTables as ot

    gsub = font.get("GSUB")
    if gsub is None or gsub.table.FeatureList is None:
        return False
    name = font["name"]
    used = {r.nameID for r in name.names}

    def alloc_name_id():
        nid = 256  # FeatureParams UINameID must be >= 256
        while nid in used:
            nid += 1
        used.add(nid)
        return nid

    tag_to_nid = {}
    added = False
    for fr in gsub.table.FeatureList.FeatureRecord:
        tag = fr.FeatureTag
        if tag not in STYLISTIC_SET_NAMES:
            continue
        if fr.Feature.FeatureParams is not None:
            continue  # already named
        if tag not in tag_to_nid:
            nid = alloc_name_id()
            label = STYLISTIC_SET_NAMES[tag]
            name.setName(label, nid, 3, 1, 0x409)  # Windows / English
            name.setName(label, nid, 1, 0, 0)      # Mac / English
            tag_to_nid[tag] = nid
        fp = ot.FeatureParamsStylisticSet()
        fp.Version = 0
        fp.UINameID = tag_to_nid[tag]
        fr.Feature.FeatureParams = fp
        added = True
    if added:
        print(f"    Added UI names for {len(tag_to_nid)} stylistic sets")
    return added


def add_fvar_instance_ps_names(font):
    """Give every fvar named instance a PostScript name entry (name record +
    instance.postscriptNameID). Fixes fontspector `fvar_instance_ps_names`
    [missing-ps-name]. PS name = <PS family>-<StyleNoSpaces>, e.g.
    BuenaMono-ThinItalic."""
    fvar = font.get("fvar")
    if fvar is None:
        return False
    name = font["name"]
    used = {r.nameID for r in name.names}

    def alloc_name_id():
        nid = 256
        while nid in used:
            nid += 1
        used.add(nid)
        return nid

    # PS family base from nameID 6 ("BuenaMono-Regular" -> "BuenaMono")
    ps6 = name.getDebugName(6) or "BuenaMono-Regular"
    ps_family = ps6.rsplit("-", 1)[0] if "-" in ps6 else ps6

    changed = False
    for inst in fvar.instances:
        pid = getattr(inst, "postscriptNameID", 0xFFFF)
        if pid is not None and pid != 0xFFFF and pid >= 256:
            continue  # already has a PS name
        sub = name.getDebugName(inst.subfamilyNameID) or ""
        style = "".join(sub.split())  # strip spaces -> valid PS token
        ps_name = f"{ps_family}-{style}" if style else ps_family
        nid = alloc_name_id()
        name.setName(ps_name, nid, 3, 1, 0x409)  # Windows / English
        name.setName(ps_name, nid, 1, 0, 0)      # Mac / English
        inst.postscriptNameID = nid
        changed = True
    if changed:
        print("    Added PostScript names for fvar instances")
    return changed


def add_smart_dropout(font):
    """Add a minimal `prep` program enabling smart dropout control so thin
    features don't drop out at small ppem on scan-converting rasterizers.
    Fixes the fontbakery `smart_dropout` FAIL. TrueType (glyf) only — CFF2/OTF
    has no prep table, so it's skipped there."""
    if "glyf" not in font:
        return False
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables import ttProgram

    # PUSHW 511 / SCANCTRL (dropout control on, all conditions)
    # PUSHB 4   / SCANTYPE (4 = smart dropout control)
    asm = ["PUSHW[] 511", "SCANCTRL[]", "PUSHB[] 4", "SCANTYPE[]"]
    if "prep" in font:
        prog = font["prep"].program
        cur = list(prog.getAssembly())
        if any("SCANTYPE" in ins for ins in cur):
            return False  # already has dropout control
        prog.fromAssembly(asm + cur)
    else:
        prep = newTable("prep")
        prog = ttProgram.Program()
        prog.fromAssembly(asm)
        prep.program = prog
        font["prep"] = prep
    print("    Added smart-dropout prep program")
    return True


def process_font(font_path):
    """Apply all post-processing fixes to a single font."""
    print(f"  {font_path.name}:")

    font = TTFont(str(font_path))
    modified = False

    # Remove incorrectly-set NameID 17
    if remove_nameid17(font):
        modified = True

    # Fix OS/2 usWinDescent for Google Fonts
    if fix_win_descent(font):
        modified = True

    # Flatten nested TrueType components
    if flatten_nested_components(font):
        modified = True

    # Reorder smcp/c2sc before liga/calt
    if reorder_smcp_before_liga(font):
        modified = True

    # Add GDEF ligature caret positions (cursor stops between ligature cells)
    if add_ligature_carets(font):
        modified = True

    # Add smart-dropout prep program (TrueType only)
    if add_smart_dropout(font):
        modified = True

    # Add UI names for stylistic sets (ss01-ss12)
    if add_stylistic_set_names(font):
        modified = True

    # Add PostScript names for fvar named instances
    if add_fvar_instance_ps_names(font):
        modified = True

    # Add meta table
    if "meta" not in font:
        add_meta_table(font)
        print(f"    Added meta table (dlng/slng)")
        modified = True

    # Fix xAvgCharWidth
    if fix_xavgcharwidth(font):
        modified = True

    # Remove Mac platform name records
    if remove_mac_names(font):
        modified = True

    # Add avar table
    if add_avar_table(font):
        modified = True

    # Note: truncate_long_names disabled — causes GSUB reference breakage
    # and is not required by fontspector/Google Fonts for TrueType fonts

    # Report contour directions
    report_contour_directions(font)

    # Report numberOfHMetrics
    report_number_of_hmetrics(font)

    if modified:
        font.save(str(font_path))
        print(f"    Saved.")
    else:
        print(f"    No changes needed.")

    font.close()


def main():
    parser = argparse.ArgumentParser(description="Post-build processing for Google Fonts")
    parser.add_argument("--font-dir", default="out/fonts", help="Directory containing built fonts")
    args = parser.parse_args()

    font_dir = Path(args.font_dir)

    targets = ["BuenaMono-VF.ttf", "BuenaMono-VF.otf"]

    for name in targets:
        path = font_dir / name
        if path.exists():
            process_font(path)
        else:
            print(f"  {name}: SKIP (not found)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
