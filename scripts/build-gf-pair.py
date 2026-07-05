#!/usr/bin/env python3
"""Build the Google Fonts roman/italic pair from the 2-axis VF.

Google Fonts wants a classic wght-only Roman + Italic pair rather than a
slnt-axis font (googlefonts/varfont/slnt_needs_italic — Google Workspace
can't reach slanted designspace locations, and family axes must be
consistent across roman and italic files). The repo's 2-axis
BuenaMono-VF.ttf stays the direct-download artifact; this derives the
submission pair from it with the fontTools instancer:

  BuenaMono[wght].ttf         slnt pinned to 0
  BuenaMono-Italic[wght].ttf  slnt pinned to -10, italic naming/bits

Both get a STAT table with the wght values from config.yaml plus the
GF-required ital axis linkage (roman ital=0 elidable linked to italic
ital=1).

Usage:
    python3 scripts/build-gf-pair.py [--input out/fonts/BuenaMono-VF.ttf]
                                     [--output-dir out/fonts]
"""

import argparse
from pathlib import Path

import yaml
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FAMILY = "Buena Mono"

# OS/2.fsSelection bits
FS_ITALIC, FS_REGULAR = 0x01, 0x40
# head.macStyle bits
MAC_ITALIC = 0x02

WIN, MAC = (3, 1, 0x409), (1, 0, 0)

ROMAN_ITAL = {"name": "Roman", "value": 0, "flags": 2, "linkedValue": 1}
ITALIC_ITAL = {"name": "Italic", "value": 1}


def set_name(name_table, name_id, value):
    name_table.setName(value, name_id, *WIN[:2], WIN[2])
    if name_table.getName(name_id, *MAC):
        name_table.setName(value, name_id, *MAC)


def stat_axes(config_path, ital_value):
    """wght values from config.yaml plus the ital axis linkage."""
    with open(config_path) as f:
        stat = yaml.safe_load(f)["stat"]
    wght = next(a for a in stat if a["tag"] == "wght")
    return [
        {
            "tag": "wght",
            "name": wght["name"],
            "ordering": 0,
            "values": [
                {k: v for k, v in val.items() if k in ("name", "value", "flags", "linkedValue")}
                for val in wght["values"]
            ],
        },
        {"tag": "ital", "name": "Italic", "ordering": 1, "values": [ital_value]},
    ]


def build_instance(input_path, config, slnt, italic):
    font = TTFont(input_path)
    instancer.instantiateVariableFont(font, {"slnt": slnt}, inplace=True, updateFontNames=False)

    if italic:
        name = font["name"]
        version = name.getDebugName(5)
        set_name(name, 1, FAMILY)
        set_name(name, 2, "Italic")
        set_name(name, 3, f"{version};BUEN;BuenaMono-Italic")
        set_name(name, 4, f"{FAMILY} Italic")
        set_name(name, 6, "BuenaMono-Italic")
        # Typographic names (16/17) are unnecessary: "Italic" is RIBBI.
        for nid in (16, 17):
            name.removeNames(nameID=nid)
        os2, head = font["OS/2"], font["head"]
        os2.fsSelection = (os2.fsSelection | FS_ITALIC) & ~FS_REGULAR
        head.macStyle |= MAC_ITALIC
        font["post"].italicAngle = float(slnt)

    buildStatTable(font, stat_axes(config, ITALIC_ITAL if italic else ROMAN_ITAL),
                   elidedFallbackName=2)
    return font


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="out/fonts/BuenaMono-VF.ttf")
    parser.add_argument("--output-dir", default="out/fonts")
    parser.add_argument("--config", default="sources/config.yaml")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for filename, slnt, italic in [
        ("BuenaMono[wght].ttf", 0, False),
        ("BuenaMono-Italic[wght].ttf", -10, True),
    ]:
        font = build_instance(args.input, args.config, slnt, italic)
        font.save(out / filename)
        os2, head, post = font["OS/2"], font["head"], font["post"]
        print(f"built {out / filename}")
        print(f"  fsSelection={os2.fsSelection:#06x} macStyle={head.macStyle:#04x} "
              f"italicAngle={post.italicAngle} axes={[a.axisTag for a in font['fvar'].axes]}")


if __name__ == "__main__":
    main()
