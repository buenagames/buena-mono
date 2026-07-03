#!/usr/bin/env python3
"""Generate source manifest for Buena Mono.

Reads .glyphs (via glyphsLib), UFOs (via plistlib/os), and .designspace
(via fontTools) to produce sources/source-manifest.json.

Run: python3 scripts/generate-manifest.py
Output: sources/source-manifest.json
"""

import hashlib
import json
import os
import plistlib
import sys
from datetime import datetime, timezone

import glyphsLib

try:
    from fontTools.designspaceLib import DesignSpaceDocument
except ImportError:
    DesignSpaceDocument = None

# =============================================================================
# Constants
# =============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
GLYPHS_PATH = os.path.join(SOURCES_DIR, "BuenaMono.glyphs")
DS_PATH = os.path.join(SOURCES_DIR, "BuenaMono.designspace")
MANIFEST_PATH = os.path.join(SOURCES_DIR, "source-manifest.json")

BASE_UFOS = [
    "BuenaMono-Thin.ufo",
    "BuenaMono-Regular.ufo",
    "BuenaMono-Bold.ufo",
    "BuenaMono-ExtraBold.ufo",
]


# =============================================================================
# Helpers
# =============================================================================

def sha256_file(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def count_ufo_glyphs(ufo_dir):
    """Count glyphs in a UFO by reading contents.plist."""
    cp_path = os.path.join(ufo_dir, "glyphs", "contents.plist")
    if not os.path.exists(cp_path):
        return 0
    with open(cp_path, "rb") as f:
        contents = plistlib.load(f)
    return len(contents)


# =============================================================================
# Main
# =============================================================================

def main():
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "glyphs_source": {},
        "ufos": {},
        "designspace": {},
    }

    # --- .glyphs source ---
    if os.path.exists(GLYPHS_PATH):
        print(f"Reading: {GLYPHS_PATH}")
        font = glyphsLib.load(GLYPHS_PATH)
        manifest["glyphs_source"] = {
            "file": os.path.relpath(GLYPHS_PATH, PROJECT_ROOT),
            "glyph_count": len(font.glyphs),
            "feature_count": len(font.features),
            "feature_prefix_count": len(font.featurePrefixes),
            "master_count": len(font.masters),
            "features": [f.name for f in font.features],
        }
        print(f"  Glyphs: {len(font.glyphs)}, Features: {len(font.features)}, "
              f"Prefixes: {len(font.featurePrefixes)}, Masters: {len(font.masters)}")
    else:
        print(f"WARNING: {GLYPHS_PATH} not found")

    # --- UFOs ---
    for ufo_name in BASE_UFOS:
        ufo_dir = os.path.join(SOURCES_DIR, ufo_name)
        if not os.path.exists(ufo_dir):
            print(f"WARNING: {ufo_dir} not found")
            continue

        glyph_count = count_ufo_glyphs(ufo_dir)
        fea_path = os.path.join(ufo_dir, "features.fea")
        fea_sha = sha256_file(fea_path) if os.path.exists(fea_path) else None

        manifest["ufos"][ufo_name] = {
            "glyph_count": glyph_count,
            "features_fea_sha256": fea_sha,
        }
        print(f"  {ufo_name}: {glyph_count} glyphs")

    # --- Designspace ---
    if os.path.exists(DS_PATH) and DesignSpaceDocument is not None:
        print(f"Reading: {DS_PATH}")
        ds = DesignSpaceDocument.fromfile(DS_PATH)
        manifest["designspace"] = {
            "file": os.path.relpath(DS_PATH, PROJECT_ROOT),
            "axis_count": len(ds.axes),
            "source_count": len(ds.sources),
            "instance_count": len(ds.instances),
            "axes": [{"name": a.name, "tag": a.tag} for a in ds.axes],
        }
        print(f"  Axes: {len(ds.axes)}, Sources: {len(ds.sources)}, "
              f"Instances: {len(ds.instances)}")
    elif os.path.exists(DS_PATH):
        print(f"WARNING: fontTools not available, skipping designspace analysis")
    else:
        print(f"WARNING: {DS_PATH} not found")

    # --- Write manifest ---
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
