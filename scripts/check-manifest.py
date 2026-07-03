#!/usr/bin/env python3
"""Validate source state against manifest before builds.

Checks:
  - UFO glyph counts haven't dropped
  - features.fea checksums match
  - .glyphs glyph/feature counts haven't dropped
  - Designspace structure matches

Exits non-zero with clear message if validation fails.

Run: python3 scripts/check-manifest.py
Requires: sources/source-manifest.json (from generate-manifest.py)
"""

import hashlib
import json
import os
import plistlib
import sys

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


# =============================================================================
# Helpers
# =============================================================================

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def count_ufo_glyphs(ufo_dir):
    cp_path = os.path.join(ufo_dir, "glyphs", "contents.plist")
    if not os.path.exists(cp_path):
        return 0
    with open(cp_path, "rb") as f:
        contents = plistlib.load(f)
    return len(contents)


# =============================================================================
# Checks
# =============================================================================

def check_glyphs_source(manifest, errors):
    """Check .glyphs source hasn't lost content."""
    expected = manifest.get("glyphs_source", {})
    if not expected:
        return

    if not os.path.exists(GLYPHS_PATH):
        errors.append(f".glyphs source not found: {GLYPHS_PATH}")
        return

    font = glyphsLib.load(GLYPHS_PATH)
    actual_glyphs = len(font.glyphs)
    actual_features = len(font.features)

    exp_glyphs = expected.get("glyph_count", 0)
    exp_features = expected.get("feature_count", 0)

    if actual_glyphs < exp_glyphs:
        errors.append(
            f".glyphs glyph count dropped: {actual_glyphs} < {exp_glyphs} "
            f"(lost {exp_glyphs - actual_glyphs} glyphs)"
        )
    if actual_features < exp_features:
        errors.append(
            f".glyphs feature count dropped: {actual_features} < {exp_features} "
            f"(lost {exp_features - actual_features} features)"
        )


def check_ufos(manifest, errors):
    """Check UFO glyph counts and features.fea checksums."""
    expected_ufos = manifest.get("ufos", {})

    for ufo_name, expected in expected_ufos.items():
        ufo_dir = os.path.join(SOURCES_DIR, ufo_name)
        if not os.path.exists(ufo_dir):
            errors.append(f"UFO not found: {ufo_name}")
            continue

        # Check glyph count
        actual_count = count_ufo_glyphs(ufo_dir)
        exp_count = expected.get("glyph_count", 0)
        if actual_count < exp_count:
            errors.append(
                f"{ufo_name} glyph count dropped: {actual_count} < {exp_count} "
                f"(lost {exp_count - actual_count} glyphs)"
            )

        # Check features.fea checksum
        exp_sha = expected.get("features_fea_sha256")
        if exp_sha:
            fea_path = os.path.join(ufo_dir, "features.fea")
            if not os.path.exists(fea_path):
                errors.append(f"{ufo_name}/features.fea missing")
            else:
                actual_sha = sha256_file(fea_path)
                if actual_sha != exp_sha:
                    errors.append(
                        f"{ufo_name}/features.fea checksum mismatch "
                        f"(expected {exp_sha[:12]}..., got {actual_sha[:12]}...)"
                    )


def check_designspace(manifest, errors):
    """Check designspace structure matches."""
    expected = manifest.get("designspace", {})
    if not expected or DesignSpaceDocument is None:
        return

    if not os.path.exists(DS_PATH):
        errors.append(f"Designspace not found: {DS_PATH}")
        return

    ds = DesignSpaceDocument.fromfile(DS_PATH)

    exp_axes = expected.get("axis_count", 0)
    exp_sources = expected.get("source_count", 0)

    if len(ds.axes) != exp_axes:
        errors.append(
            f"Designspace axis count changed: {len(ds.axes)} != {exp_axes}"
        )
    if len(ds.sources) != exp_sources:
        errors.append(
            f"Designspace source count changed: {len(ds.sources)} != {exp_sources}"
        )


# =============================================================================
# Main
# =============================================================================

def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"Manifest not found: {MANIFEST_PATH}")
        print("Run 'python3 scripts/generate-manifest.py' to create it.")
        sys.exit(1)

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    print(f"Checking against manifest from {manifest.get('generated_at', 'unknown')}")

    errors = []

    print("  Checking .glyphs source...")
    check_glyphs_source(manifest, errors)

    print("  Checking UFOs...")
    check_ufos(manifest, errors)

    print("  Checking designspace...")
    check_designspace(manifest, errors)

    if errors:
        print(f"\nFAILED: {len(errors)} issue(s) found:\n")
        for err in errors:
            print(f"  - {err}")
        print("\nSource state has regressed from the manifest baseline.")
        print("If this is intentional, regenerate the manifest:")
        print("  python3 scripts/generate-manifest.py")
        sys.exit(1)
    else:
        print("\nAll checks passed.")


if __name__ == "__main__":
    main()
