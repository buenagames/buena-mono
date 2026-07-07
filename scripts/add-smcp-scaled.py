#!/usr/bin/env python3
"""Batch-1 shaperglot fix: scaled small caps for IPA/African-Latin letters.

Creates .smcp glyphs for 38 lowercase letters whose uppercase form already
exists in the font, using the same derivation as the original A-Z small caps
(scripts/add-smallcaps.py in the dev repo): decompose the uppercase outlines,
scale uniformly by x-height/cap-height = 524/699, re-center in the 618 advance.
No stem compensation — matches the existing 820 .smcp glyphs (fix-uc-stems.py
deliberately excluded .smcp).

Also fixes Turkish:
  - locl bug: `sub i by uni0131` under TRK/AZE/CRT rendered every dotted i as
    dotless. Replaced with `sub i by i.loclTRK` (new glyph, component copy of i).
  - smcp: `sub i.loclTRK by uni0130.smcp` so Turkish small-cap i keeps its dot
    (uni0130.smcp already exists).

Feature rules: replaces the self-referencing no-op rules (`sub X by X;`) in
smcp/c2sc with real substitutions; appends rules where no self-sub existed.

Usage:
  python3 scripts/add-smcp-scaled.py --dry-run
  python3 scripts/add-smcp-scaled.py --apply
"""

import argparse
import os
import re
import sys

import glyphsLib
from fontTools.misc.transform import Transform

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLYPHS_PATH = os.path.join(REPO, "sources", "BuenaMono.glyphs")

ADVANCE_WIDTH = 618
SCALE = 524 / 699  # x-height / cap-height, same as add-smallcaps.py

# (lowercase cp, uppercase cp) -> glyphs uni0254 -> uni0186.smcp etc.
PAIRS = [
    (0x0254, 0x0186),  # open o
    (0x025B, 0x0190),  # open e
    (0x0253, 0x0181),  # b hook
    (0x0257, 0x018A),  # d hook
    (0x0268, 0x0197),  # i stroke
    (0x0269, 0x0196),  # iota
    (0x0272, 0x019D),  # n left hook
    (0x028B, 0x01B2),  # v hook
    (0x0289, 0x0244),  # u bar
    (0xA78C, 0xA78B),  # saltillo
    (0x01B4, 0x01B3),  # y hook
    (0x0263, 0x0194),  # gamma
    (0x0256, 0x0189),  # d tail (African D)
    (0x0199, 0x0198),  # k hook
    (0x028A, 0x01B1),  # upsilon
    (0x0292, 0x01B7),  # ezh
    (0x01EF, 0x01EE),  # ezh caron
    (0x0251, 0x2C6D),  # alpha
    (0x0266, 0xA7AA),  # h hook
    (0x0242, 0x0241),  # glottal stop
    (0x024D, 0x024C),  # r stroke
    (0x0288, 0x01AE),  # t retroflex hook
    (0x028C, 0x0245),  # turned v
    (0x0223, 0x0222),  # ou
    (0x0260, 0x0193),  # g hook
    (0xA7B5, 0xA7B4),  # beta
    (0x019E, 0x0220),  # n long right leg
    (0x0247, 0x0246),  # e stroke
    (0x024B, 0x024A),  # q hook tail
    (0x0265, 0xA78D),  # turned h
    (0x027D, 0x2C64),  # r tail
    (0x0280, 0x01A6),  # yr / small capital R
    (0x029D, 0xA7B2),  # j crossed-tail
    (0x1D7D, 0x2C63),  # p stroke
    (0x2C61, 0x2C60),  # l double bar
    (0x2C65, 0x023A),  # a stroke
    (0xA7B7, 0xA7B6),  # omega
    (0xAB53, 0xA7B3),  # chi
]


def glyph_by_unicode(font, cp):
    for g in font.glyphs:
        if g.unicode and int(g.unicode, 16) == cp:
            return g
    return None


def decomposed_paths(layer, font, master_id, xform=Transform()):
    """Flatten a layer into bare (nodes, closed) path specs, resolving
    components recursively. nodes = [(x, y, type, smooth), ...]."""
    out = []
    for path in layer.paths:
        nodes = []
        for node in path.nodes:
            x, y = xform.transformPoint((node.position.x, node.position.y))
            nodes.append((x, y, node.type, node.smooth))
        det = xform[0] * xform[3] - xform[1] * xform[2]
        if det < 0:  # mirrored: restore winding by reversing
            nodes = _reverse_nodes(nodes)
        out.append((nodes, path.closed))
    for comp in layer.components:
        ref = font.glyphs[comp.name]
        if ref is None:
            raise KeyError(f"component ref not found: {comp.name}")
        ref_layer = _layer_for_master(ref, master_id)
        ct = Transform(*comp.transform)
        out.extend(decomposed_paths(ref_layer, font, master_id, xform.transform(ct)))
    return out


def _reverse_nodes(nodes):
    # reverse contour direction, keeping GSNode on-curve semantics:
    # rotate so the node list still ends on an on-curve point per Glyphs
    rev = list(reversed(nodes))
    fixed = []
    for i, (x, y, t, s) in enumerate(rev):
        fixed.append((x, y, t, s))
    return fixed


def _layer_for_master(glyph, master_id):
    for layer in glyph.layers:
        if layer.layerId == master_id:
            return layer
    raise KeyError(f"{glyph.name}: no layer for master {master_id}")


def build_smcp_layer(src_layer, font, master_id):
    """Scaled+centered small-cap layer from an uppercase layer."""
    flat = decomposed_paths(src_layer, font, master_id)
    min_x = min(x for nodes, _ in flat for x, *_ in nodes)
    max_x = max(x for nodes, _ in flat for x, *_ in nodes)
    off = (ADVANCE_WIDTH - (max_x - min_x) * SCALE) / 2 - min_x * SCALE

    layer = glyphsLib.classes.GSLayer()
    layer.layerId = layer.associatedMasterId = master_id
    layer.width = ADVANCE_WIDTH
    for nodes, closed in flat:
        gp = glyphsLib.classes.GSPath()
        gp.closed = closed
        for x, y, t, smooth in nodes:
            n = glyphsLib.classes.GSNode(
                (round(x * SCALE + off, 1), round(y * SCALE, 1)), t)
            n.smooth = smooth
            gp.nodes.append(n)
        layer.paths.append(gp)
    return layer


def make_component_copy(font, src_name, new_name):
    """New glyph whose every master layer is a bare component of src_name."""
    src = font.glyphs[src_name]
    g = glyphsLib.classes.GSGlyph(new_name)
    g.export = True
    for master in font.masters:
        _layer_for_master(src, master.id)  # assert source layer exists
        layer = glyphsLib.classes.GSLayer()
        layer.layerId = layer.associatedMasterId = master.id
        layer.width = ADVANCE_WIDTH
        comp = glyphsLib.classes.GSComponent(src_name)
        layer.components.append(comp)
        g.layers.append(layer)
    return g


def patch_feature(font, tag, replacements, additions):
    """Replace self-sub lines and append missing rules in a feature's code."""
    feat = None
    for f in font.features:
        if f.name == tag:
            feat = f
            break
    if feat is None:
        raise KeyError(f"feature {tag} not found")
    code = feat.code
    replaced, appended = [], []
    for old, new in replacements:
        if old in code:
            code = code.replace(old, new)
            replaced.append(new.strip())
        elif new in code:
            pass  # already patched
        else:
            additions = additions + [new]
    for rule in additions:
        if rule not in code:
            code = code.rstrip("\n") + "\n" + rule + "\n"
            appended.append(rule.strip())
    feat.code = code
    return replaced, appended


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.print_help()
        return

    print(f"loading {GLYPHS_PATH} ...")
    font = glyphsLib.GSFont(GLYPHS_PATH)
    existing = {g.name for g in font.glyphs}
    print(f"{len(existing)} glyphs, {len(font.masters)} masters")

    smcp_repl, c2sc_repl = [], []
    new_glyphs = []
    for lc_cp, uc_cp in PAIRS:
        lc_g = glyph_by_unicode(font, lc_cp)
        uc_g = glyph_by_unicode(font, uc_cp)
        if lc_g is None or uc_g is None:
            print(f"  SKIP U+{lc_cp:04X}: lc={lc_g and lc_g.name} uc={uc_g and uc_g.name}")
            continue
        sc_name = f"{uc_g.name}.smcp"
        if sc_name in existing:
            print(f"  exists: {sc_name}")
        else:
            g = glyphsLib.classes.GSGlyph(sc_name)
            g.export = True
            for master in font.masters:
                src_layer = _layer_for_master(uc_g, master.id)
                g.layers.append(build_smcp_layer(src_layer, font, master.id))
            new_glyphs.append(g)
        smcp_repl.append((f"sub {lc_g.name} by {lc_g.name};",
                          f"sub {lc_g.name} by {sc_name};"))
        c2sc_repl.append((f"sub {uc_g.name} by {uc_g.name};",
                          f"sub {uc_g.name} by {sc_name};"))
        print(f"  U+{lc_cp:04X} {chr(lc_cp)}: {uc_g.name} -> {sc_name}"
              f" ({sum(len(l.paths) for l in (new_glyphs[-1].layers if new_glyphs and new_glyphs[-1].name == sc_name else []))} paths total)")

    # Turkish dotted i
    if "i.loclTRK" not in existing:
        new_glyphs.append(make_component_copy(font, "i", "i.loclTRK"))
        print("  i.loclTRK: component copy of i")

    if args.dry_run:
        print(f"\ndry-run: would add {len(new_glyphs)} glyphs, "
              f"{len(smcp_repl)} smcp rules, {len(c2sc_repl)} c2sc rules")
        return

    for g in new_glyphs:
        font.glyphs.append(g)

    r, a = patch_feature(font, "smcp", smcp_repl,
                         ["sub i.loclTRK by uni0130.smcp;"])
    print(f"smcp: {len(r)} replaced, {len(a)} appended")
    r, a = patch_feature(font, "c2sc", c2sc_repl, [])
    print(f"c2sc: {len(r)} replaced, {len(a)} appended")

    # locl: Turkish/Azeri/Crimean Tatar dotted i must stay dotted
    r, a = patch_feature(font, "locl",
                         [("sub i by uni0131;", "sub i by i.loclTRK;")], [])
    print(f"locl: dotted-i fix applied ({len(r)} replaced)")

    font.save(GLYPHS_PATH)
    print(f"\nsaved {GLYPHS_PATH}: +{len(new_glyphs)} glyphs")


if __name__ == "__main__":
    main()
