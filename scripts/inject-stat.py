#!/usr/bin/env python3
"""Inject STAT axis values into built variable fonts.

Reads the STAT configuration from sources/config.yaml and writes
axis value entries into TTF and OTF variable fonts using fontTools'
buildStatTable API. WOFF2 should be built AFTER this step so it
inherits the STAT data.

Usage:
    python3 scripts/inject-stat.py [--config sources/config.yaml] [--font-dir out/fonts]
"""

import argparse
import sys
from pathlib import Path

import yaml
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont


def load_stat_config(config_path):
    """Load STAT axis definitions from config.yaml.

    Converts the config.yaml format into the axes list expected by
    fontTools.otlLib.builder.buildStatTable().
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    raw = config.get("stat")
    if not raw:
        print(f"ERROR: No 'stat' key in {config_path}")
        sys.exit(1)

    # Transform config.yaml format → buildStatTable format
    axes = []
    for i, axis_def in enumerate(raw):
        axis = {
            "tag": axis_def["tag"],
            "name": axis_def["name"],
            "ordering": i,
        }

        values = []
        for val_def in axis_def.get("values", []):
            entry = {
                "name": val_def["name"],
                "value": val_def["value"],
            }
            if "flags" in val_def:
                entry["flags"] = val_def["flags"]
            if "linkedValue" in val_def:
                entry["linkedValue"] = val_def["linkedValue"]
            values.append(entry)

        if values:
            axis["values"] = values
        axes.append(axis)

    return axes


def inject_font(font_path, axes):
    """Inject STAT table into a single font file."""
    print(f"  {font_path.name}...", end=" ")

    font = TTFont(str(font_path))

    total_values = sum(len(a.get("values", [])) for a in axes)

    # buildStatTable replaces the entire STAT table
    buildStatTable(font, axes, elidedFallbackName=2)

    font.save(str(font_path))
    font.close()

    print(f"{total_values} axis values injected")
    return True


def main():
    parser = argparse.ArgumentParser(description="Inject STAT axis values into built fonts")
    parser.add_argument("--config", default="sources/config.yaml", help="Config YAML with STAT definitions")
    parser.add_argument("--font-dir", default="out/fonts", help="Directory containing built fonts")
    args = parser.parse_args()

    config_path = Path(args.config)
    font_dir = Path(args.font_dir)

    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    axes = load_stat_config(config_path)
    total_values = sum(len(a.get("values", [])) for a in axes)

    print(f"STAT config: {len(axes)} axes from {config_path}")
    print(f"  {total_values} axis values to inject")
    print()

    # Inject into TTF and OTF (not WOFF2 — it will be rebuilt from TTF)
    targets = ["BuenaMono-VF.ttf", "BuenaMono-VF.otf"]
    injected = 0

    for name in targets:
        path = font_dir / name
        if path.exists():
            if inject_font(path, axes):
                injected += 1
        else:
            print(f"  {name}... SKIP (not found)")

    print(f"\nDone: {injected} fonts updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
