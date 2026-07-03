#!/usr/bin/env python3
"""Export Buena Mono .glyphs source to UFO + designspace.

Uses glyphsLib.to_designspace() for the initial conversion, then fixes
the designspace for multi-axis builds (wght × slnt × opsz) since glyphsLib
doesn't always handle custom axes correctly.

Supports 2-master (wght only) and 4+ master (wght × slnt) configurations.

Run: python3 scripts/export-ufo.py
Input: sources/BuenaMono.glyphs
"""

import os
import sys

import glyphsLib
from fontTools.designspaceLib import (
    DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
GLYPHS_PATH = os.path.join(SOURCES_DIR, "BuenaMono.glyphs")


def master_style(master):
    """Master style name. Glyphs 3-format sources leave customName empty and put
    the style in master.name; Glyphs 2 sources used customName. Prefer name."""
    return (getattr(master, "name", "") or getattr(master, "customName", "") or "").strip()


def ufo_name_for_master(master):
    """Map a GSFontMaster to its UFO filename."""
    clean = f"BuenaMono-{master_style(master).replace(' ', '-')}"
    return f"{clean}.ufo"


def master_location(master):
    """Extract axis location dict from a master's axes list and font axes."""
    # master.axes is a list like [400, 100, 0] or [700, 100, -10]
    # Index 0 = Weight, Index 1 = Width (implicit, always 100), Index 2+ = custom axes.
    # NOTE: Glyphs 3-format sources truncate axesValues to the count of declared
    # axes and DROP the slant value from italic masters (index 2). So derive Slant
    # from the master name, which is reliable, instead of trusting axes[2].
    loc = {}
    axes_vals = master.axes if master.axes else []

    # Weight is always index 0
    loc["Weight"] = axes_vals[0] if len(axes_vals) > 0 else 400

    # Index 1 is Width (implicit) — skip

    # Slant: derive from name (italic => -10), falling back to legacy index 2.
    name = master_style(master).lower()
    if "italic" in name:
        loc["Slant"] = -10
    elif len(axes_vals) > 2:
        loc["Slant"] = axes_vals[2]

    # Index 3 would be Optical Size (future)
    if len(axes_vals) > 3:
        loc["Optical Size"] = axes_vals[3]

    return loc


def needs_manual_designspace(font):
    """Check if we need to manually construct the designspace."""
    # If there are more than 1 declared axis or more than 2 masters
    return len(font.axes) > 1 or len(font.masters) > 2


def export_simple(font):
    """Standard 2-master export via glyphsLib.to_designspace()."""
    ds = glyphsLib.to_designspace(font)

    master_names = {400: "Regular", 700: "Bold"}
    for source in ds.sources:
        weight = int(source.location.get("Weight", 400))
        name = master_names.get(weight, f"W{weight}")
        ufo_filename = f"BuenaMono-{name}.ufo"
        source.filename = ufo_filename

        # Remove EraseOpenCornersFilter
        FILTER_KEY = "com.github.googlei18n.ufo2ft.filters"
        if FILTER_KEY in source.font.lib:
            filters = source.font.lib[FILTER_KEY]
            filters = [f for f in filters if f.get("name") != "eraseOpenCorners"]
            if filters:
                source.font.lib[FILTER_KEY] = filters
            else:
                del source.font.lib[FILTER_KEY]

        ufo_path = os.path.join(SOURCES_DIR, ufo_filename)
        source.font.save(ufo_path, overwrite=True)
        print(f"  Wrote: {ufo_path}")

    ds_path = os.path.join(SOURCES_DIR, "BuenaMono.designspace")
    ds.filename = "BuenaMono.designspace"
    ds.write(ds_path)
    print(f"  Wrote: {ds_path}")
    return ds


def export_multiaxis(font):
    """Multi-axis export: write UFOs via glyphsLib, construct designspace manually."""
    # Step 1: Use glyphsLib to get the UFO fonts (it handles glyph data well)
    ds_raw = glyphsLib.to_designspace(font)

    # Step 2: Map each source to its correct master by index
    # glyphsLib maintains master order, so index-based mapping is reliable
    written_ufos = {}
    for idx, master in enumerate(font.masters):
        ufo_filename = ufo_name_for_master(master)
        if idx >= len(ds_raw.sources):
            print(f"  WARNING: No UFO source for master '{master_style(master)}' (index {idx})")
            continue
        source = ds_raw.sources[idx]

        # Remove EraseOpenCornersFilter
        FILTER_KEY = "com.github.googlei18n.ufo2ft.filters"
        if FILTER_KEY in source.font.lib:
            filters = source.font.lib[FILTER_KEY]
            filters = [f for f in filters if f.get("name") != "eraseOpenCorners"]
            if filters:
                source.font.lib[FILTER_KEY] = filters
            else:
                del source.font.lib[FILTER_KEY]

        ufo_path = os.path.join(SOURCES_DIR, ufo_filename)
        source.font.save(ufo_path, overwrite=True)
        written_ufos[master.id] = ufo_filename
        loc = master_location(master)
        print(f"  Wrote: {ufo_path} (location: {loc})")

    # Step 3: Construct designspace manually with correct axes and locations
    ds = DesignSpaceDocument()

    # Add Weight axis
    wght = AxisDescriptor()
    wght.tag = "wght"
    wght.name = "Weight"
    wght.minimum = 100
    wght.maximum = 800
    wght.default = 400
    ds.addAxis(wght)

    # Add Slant axis (if present in font)
    has_slant = any(a.axisTag == "slnt" for a in font.axes)
    if has_slant:
        slnt = AxisDescriptor()
        slnt.tag = "slnt"
        slnt.name = "Slant"
        slnt.minimum = -10
        slnt.maximum = 0
        slnt.default = 0
        ds.addAxis(slnt)

    # Add Optical Size axis (if present in font)
    has_opsz = any(a.axisTag == "opsz" for a in font.axes)
    if has_opsz:
        opsz = AxisDescriptor()
        opsz.tag = "opsz"
        opsz.name = "Optical Size"
        opsz.minimum = 8
        opsz.maximum = 48
        opsz.default = 14
        ds.addAxis(opsz)

    # Add sources
    for i, master in enumerate(font.masters):
        loc = master_location(master)
        ufo_filename = written_ufos.get(master.id)
        if not ufo_filename:
            continue

        src = SourceDescriptor()
        src.filename = ufo_filename
        src.name = f"Buena Mono {master_style(master)}"
        src.familyName = "Buena Mono"
        src.styleName = master_style(master)

        # Build location dict matching axis names
        src.location = {}
        src.location["Weight"] = loc.get("Weight", 400)
        if has_slant:
            src.location["Slant"] = loc.get("Slant", 0)
        if has_opsz:
            src.location["Optical Size"] = loc.get("Optical Size", 14)

        # First source is the default (Regular Roman)
        if i == 0:
            src.copyLib = True
            src.copyGroups = True
            src.copyFeatures = True
            src.copyInfo = True

        ds.addSource(src)

    # Add named instances
    weight_instances = [
        ("Thin", 100),
        ("ExtraLight", 200),
        ("Light", 300),
        ("Regular", 400),
        ("Medium", 500),
        ("SemiBold", 600),
        ("Bold", 700),
        ("ExtraBold", 800),
    ]

    slant_instances = [(None, 0)]
    if has_slant:
        # Italic instances sit at the slant axis extreme (-10), matching the
        # italic masters. (Was -9.5, which fontbakery flags as suspicious coords.)
        slant_instances.append(("Italic", -10))

    for wname, wval in weight_instances:
        for sname, sval in slant_instances:
            inst = InstanceDescriptor()
            if sname:
                # "Regular Italic" becomes just "Italic" per GF convention
                style = sname if wname == "Regular" else f"{wname} {sname}"
            else:
                style = wname
            inst.name = f"Buena Mono {style}"
            inst.familyName = "Buena Mono"
            inst.styleName = style
            inst.location = {"Weight": wval}
            if has_slant:
                inst.location["Slant"] = sval
            if has_opsz:
                inst.location["Optical Size"] = 14  # default
            ds.addInstance(inst)

    # Write designspace
    ds_path = os.path.join(SOURCES_DIR, "BuenaMono.designspace")
    ds.write(ds_path)
    print(f"  Wrote: {ds_path}")

    return ds


def main():
    if not os.path.exists(GLYPHS_PATH):
        print(f"Error: {GLYPHS_PATH} not found.")
        print("Run 'python3 scripts/bootstrap-source.py' first.")
        sys.exit(1)

    print(f"Loading: {GLYPHS_PATH}")
    font = glyphsLib.load(GLYPHS_PATH)

    print(f"  Masters: {[master_style(m) for m in font.masters]}")
    print(f"  Axes: {[(a.name, a.axisTag) for a in font.axes]}")

    print("Converting to designspace + UFO...")

    if needs_manual_designspace(font):
        print("  (multi-axis mode)")
        ds = export_multiaxis(font)
    else:
        print("  (simple mode)")
        ds = export_simple(font)

    print()
    print(f"Sources: {len(ds.sources)} UFOs + 1 designspace")
    print(f"Axes: {[a.name for a in ds.axes]}")
    ds_path = os.path.join(SOURCES_DIR, "BuenaMono.designspace")
    print(f"Ready for: fontmake -m {ds_path} -o variable")
    print()
    print("  WARNING: this overwrote the UFOs from .glyphs and WIPED the")
    print("  interpolation-compatibility normalization (start points / contour")
    print("  direction) that currently lives only in the UFOs, not in .glyphs.")
    print("  Restore it: see docs/PLAN-interpolation-normalization.md")
    print("  (re-run scripts/normalize-contours.py + the CFF2 gate).")


if __name__ == "__main__":
    main()
