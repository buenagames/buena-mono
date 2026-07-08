#!/usr/bin/env python3
"""Batch-2 shaperglot/coverage glyphs (BUENA-335 round 2).

New encoded glyphs:
  U+1C89/U+1C8A  Ᲊ ᲊ  Cyrillic Tje (Khanty) — Т/т + horizontally-compressed
                       Ь/ь overlaid stem-on-stem (ligature construction)
  U+A7CC/U+A7CD  Ꟍ ꟍ  Latin S with diagonal stroke (Luiseño) — S/s + the
                       slash contour borrowed from Ø/ø
  U+A71B/U+A71C  ꜛ ꜜ  modifier arrows (IPA tone) — scaled ↑/↓
  U+AB65         ꭥ    Greek small capital omega — Ω scaled like small caps

New small caps (smcp/c2sc):
  41 accented pairs (ǹ→Ǹ.smcp, ḿ→Ḿ.smcp, …) via the batch-1 scale
  machinery + ꟍ→Ꟍ.smcp; ẖ as H.smcp + U+0331 components; caseless
  ƛ ʕ ʘ as component self-copies (caseless letters keep their form —
  distinct glyph so the feature substitution is real).

Usage:
  python3 scripts/add-batch2-glyphs.py --apply
"""

import argparse
import importlib.util
import os

import glyphsLib

_here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "smcp1", os.path.join(_here, "add-smcp-scaled.py"))
smcp1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smcp1)

GLYPHS_PATH = smcp1.GLYPHS_PATH
ADV = 618

# lowercase cp -> uppercase cp (all precomposed caps verified in-font)
SMCP_PAIRS = [
    (0x01F9, 0x01F8), (0x1E3F, 0x1E3E), (0x1E05, 0x1E04), (0x1E0D, 0x1E0C),
    (0x0229, 0x0228), (0x1E2D, 0x1E2C), (0x1E4D, 0x1E4C), (0x1E37, 0x1E36),
    (0x1E57, 0x1E56), (0x1E5B, 0x1E5A), (0x1E75, 0x1E74), (0x01ED, 0x01EC),
    (0x0227, 0x0226), (0x1E0B, 0x1E0A), (0x1E35, 0x1E34), (0x1E6B, 0x1E6A),
    (0x1E6D, 0x1E6C), (0x01DF, 0x01DE), (0x1E0F, 0x1E0E), (0x1E13, 0x1E12),
    (0x1E1F, 0x1E1E), (0x1E25, 0x1E24), (0x1E47, 0x1E46), (0x1E49, 0x1E48),
    (0x1E63, 0x1E62), (0x1E6F, 0x1E6E), (0x1E71, 0x1E70), (0x1E8D, 0x1E8C),
    (0x1E91, 0x1E90), (0x1E03, 0x1E02), (0x1E07, 0x1E06), (0x1E11, 0x1E10),
    (0x1E17, 0x1E16), (0x1E23, 0x1E22), (0x1E27, 0x1E26), (0x1E2F, 0x1E2E),
    (0x1E33, 0x1E32), (0x1E3B, 0x1E3A), (0x1E43, 0x1E42), (0x1E73, 0x1E72),
    (0x1E7F, 0x1E7E),
    (0xA7CD, 0xA7CC),  # ꟍ -> Ꟍ.smcp (glyphs created below)
    # micro-batch 3: the last nearly-supported stragglers
    (0x1E93, 0x1E92),  # ẓ
    (0x0283, 0x01A9),  # ʃ (esh -> Esh/Sigma form)
    (0x01AD, 0x01AC),  # ƭ
    (0x2C73, 0x2C72),  # ⱳ
    (0x1E15, 0x1E14),  # ḕ
    (0x1E21, 0x1E20),  # ḡ
    (0x0249, 0x0248),  # ɉ
    (0x0264, 0xA7CB),  # ɤ (rams horn)
    (0x026B, 0x2C62),  # ɫ
    (0xA7DB, 0xA7DA),  # ꟛ -> Ꟛ.smcp (Latin lambda, created below)
    # final stragglers — closes every nearly-supported language except Yi/Korean
    (0x0250, 0x2C6F),  # ɐ
    (0x1E8B, 0x1E8A),  # ẋ
    (0x0213, 0x0212),  # ȓ
    (0x01B9, 0x01B8),  # ƹ
    (0x0188, 0x0187),  # ƈ
    (0x01A5, 0x01A4),  # ƥ
    (0x1E89, 0x1E88),  # ẉ
    (0x1E2B, 0x1E2A),  # ḫ
]
CASELESS_SMCP = [0x019B, 0x0295, 0x0298]  # ƛ ʕ ʘ


def _copy_path(p, dx=0.0, sx=1.0, sy=1.0, ox=0.0, oy=0.0):
    gp = glyphsLib.classes.GSPath()
    gp.closed = p.closed
    for n in p.nodes:
        x = ox + (n.position.x - ox) * sx + dx
        y = oy + (n.position.y - oy) * sy
        node = glyphsLib.classes.GSNode((round(x, 1), round(y, 1)), n.type)
        node.smooth = n.smooth
        gp.nodes.append(node)
    return gp


def _copy_paths(layer, dx=0.0, sx=1.0, sy=1.0, ox=0.0, oy=0.0):
    """Scaled/translated copies of a layer's paths (scale about (ox,oy))."""
    return [_copy_path(p, dx, sx, sy, ox, oy) for p in layer.paths]


def _stem_left_at_bottom(layer, ymax=60):
    xs = [n.position.x for p in layer.paths for n in p.nodes
          if n.position.y < ymax]
    return min(xs) if xs else 0.0


def _new_glyph(font, name, cp):
    g = glyphsLib.classes.GSGlyph(name)
    g.export = True
    if cp:
        g.unicode = f"{cp:04X}"
    return g


def make_tje(font, cap):
    """Ᲊ/ᲊ = Te + soft-sign overlaid stem-on-stem, soft sign compressed
    horizontally so the bowl stays inside the advance."""
    te = smcp1.glyph_by_unicode(font, 0x0422 if cap else 0x0442)
    soft = smcp1.glyph_by_unicode(font, 0x042C if cap else 0x044C)
    g = _new_glyph(font, f"uni1C8{'9' if cap else 'A'}", 0x1C89 if cap else 0x1C8A)
    for master in font.masters:
        te_l = smcp1._layer_for_master(te, master.id)
        so_l = smcp1._layer_for_master(soft, master.id)
        # centre stem of Te at its bottom; soft-sign stem at its bottom
        te_bottom = [n.position.x for p in te_l.paths for n in p.nodes
                     if n.position.y < 60]
        te_bottom = [x for x in te_bottom if abs(x - ADV / 2) < 120]
        t_stem_left = min(te_bottom) if te_bottom else ADV / 2 - 40
        s_stem_left = _stem_left_at_bottom(so_l)
        layer = glyphsLib.classes.GSLayer()
        layer.layerId = layer.associatedMasterId = master.id
        layer.width = ADV
        for p in _copy_paths(te_l):
            layer.paths.append(p)
        # compress soft sign about its stem-left so the bowl fits the advance
        so_xs = [n.position.x for p in so_l.paths for n in p.nodes]
        avail = (ADV - 28) - t_stem_left
        span = max(so_xs) - s_stem_left
        sx = min(1.0, avail / span) if span else 1.0
        for p in _copy_paths(so_l, dx=t_stem_left - s_stem_left,
                             sx=sx, ox=s_stem_left):
            layer.paths.append(p)
        g.layers.append(layer)
    font.glyphs.append(g)


def make_s_stroke(font, cap):
    """Ꟍ/ꟍ = S/s + the diagonal slash contour from Ø/ø."""
    s = smcp1.glyph_by_unicode(font, 0x0053 if cap else 0x0073)
    oslash = smcp1.glyph_by_unicode(font, 0x00D8 if cap else 0x00F8)
    g = _new_glyph(font, f"uniA7C{'C' if cap else 'D'}",
                   0xA7CC if cap else 0xA7CD)
    for master in font.masters:
        s_l = smcp1._layer_for_master(s, master.id)
        o_l = smcp1._layer_for_master(oslash, master.id)
        # slash = widest SIMPLE contour (the 4-node diagonal bar; the O body
        # can be wider than the slash in some masters)
        simple = [p for p in o_l.paths if len(p.nodes) <= 6]
        slash = max(simple, key=lambda p: (
            max(n.position.x for n in p.nodes)
            - min(n.position.x for n in p.nodes)))
        layer = glyphsLib.classes.GSLayer()
        layer.layerId = layer.associatedMasterId = master.id
        layer.width = ADV
        for p in _copy_paths(s_l):
            layer.paths.append(p)
        layer.paths.append(_copy_path(slash))
        g.layers.append(layer)
    font.glyphs.append(g)


def make_modifier_arrow(font, up):
    """ꜛ/ꜜ = scaled ↑/↓ (65%, centred), tone-letter size."""
    src = smcp1.glyph_by_unicode(font, 0x2191 if up else 0x2193)
    g = _new_glyph(font, "uniA71B" if up else "uniA71C",
                   0xA71B if up else 0xA71C)
    for master in font.masters:
        src_l = smcp1._layer_for_master(src, master.id)
        layer = glyphsLib.classes.GSLayer()
        layer.layerId = layer.associatedMasterId = master.id
        layer.width = ADV
        for p in _copy_paths(src_l, sx=0.65, sy=0.65, ox=ADV / 2, oy=350):
            layer.paths.append(p)
        g.layers.append(layer)
    font.glyphs.append(g)


def make_small_cap_omega(font):
    """ꭥ = Ω scaled to x-height (same derivation as the smcp set)."""
    omega = smcp1.glyph_by_unicode(font, 0x03A9)
    g = _new_glyph(font, "uniAB65", 0xAB65)
    for master in font.masters:
        src_l = smcp1._layer_for_master(omega, master.id)
        g.layers.append(smcp1.build_smcp_layer(src_l, font, master.id))
    font.glyphs.append(g)


def make_h_line_smcp(font):
    """ẖ.smcp = H.smcp + combining macron below (both centred, zero offset)."""
    g = glyphsLib.classes.GSGlyph("uni1E96.smcp")
    g.export = True
    for master in font.masters:
        layer = glyphsLib.classes.GSLayer()
        layer.layerId = layer.associatedMasterId = master.id
        layer.width = ADV
        for ref in ("H.smcp", "uni0331"):
            comp = glyphsLib.classes.GSComponent(ref)
            layer.components.append(comp)
        g.layers.append(layer)
    font.glyphs.append(g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    print(f"loading {GLYPHS_PATH} ...")
    font = glyphsLib.GSFont(GLYPHS_PATH)
    existing = {g.name for g in font.glyphs}

    # 1. new encoded glyphs
    if "uni1C89" not in existing:
        make_tje(font, cap=True)
        make_tje(font, cap=False)
        print("  + uni1C89/uni1C8A (Tje)")
    if "uniA7CC" not in existing:
        make_s_stroke(font, cap=True)
        make_s_stroke(font, cap=False)
        print("  + uniA7CC/uniA7CD (S with diagonal stroke)")
    if "uniA71B" not in existing:
        make_modifier_arrow(font, up=True)
        make_modifier_arrow(font, up=False)
        print("  + uniA71B/uniA71C (modifier arrows)")
    if "uniAB65" not in existing:
        make_small_cap_omega(font)
        print("  + uniAB65 (small capital omega)")
    if "uniA7DA" not in existing:
        # Latin capital/small lambda = component copies of Greek Λ/λ
        for new_name, donor_cp, cp in (("uniA7DA", 0x039B, 0xA7DA),
                                       ("uniA7DB", 0x03BB, 0xA7DB)):
            donor = smcp1.glyph_by_unicode(font, donor_cp)
            g = smcp1.make_component_copy(font, donor.name, new_name)
            g.unicode = f"{cp:04X}"
            font.glyphs.append(g)
        print("  + uniA7DA/uniA7DB (Latin lambda)")

    # 2. small caps
    smcp_rules, c2sc_rules = [], []
    n_sc = 0
    for lc_cp, uc_cp in SMCP_PAIRS:
        lc = smcp1.glyph_by_unicode(font, lc_cp)
        uc = smcp1.glyph_by_unicode(font, uc_cp)
        if lc is None or uc is None:
            print(f"  SKIP U+{lc_cp:04X}")
            continue
        sc_name = f"{uc.name}.smcp"
        if sc_name not in existing:
            g = glyphsLib.classes.GSGlyph(sc_name)
            g.export = True
            for master in font.masters:
                src = smcp1._layer_for_master(uc, master.id)
                g.layers.append(smcp1.build_smcp_layer(src, font, master.id))
            font.glyphs.append(g)
            n_sc += 1
        smcp_rules.append((f"sub {lc.name} by {lc.name};",
                           f"sub {lc.name} by {sc_name};"))
        c2sc_rules.append((f"sub {uc.name} by {uc.name};",
                           f"sub {uc.name} by {sc_name};"))
    print(f"  + {n_sc} scaled small caps")

    for cp in CASELESS_SMCP:
        g0 = smcp1.glyph_by_unicode(font, cp)
        sc_name = f"{g0.name}.smcp"
        if sc_name not in existing:
            font.glyphs.append(smcp1.make_component_copy(font, g0.name, sc_name))
        smcp_rules.append((f"sub {g0.name} by {g0.name};",
                           f"sub {g0.name} by {sc_name};"))
    print("  + caseless small caps (ƛ ʕ ʘ)")

    if "uni1E96.smcp" not in existing:
        make_h_line_smcp(font)
        smcp_rules.append(("sub uni1E96 by uni1E96;",
                           "sub uni1E96 by uni1E96.smcp;"))
        print("  + uni1E96.smcp (H.smcp + macron below)")

    if not args.apply:
        print("dry-run only; not saving")
        return

    r, a = smcp1.patch_feature(font, "smcp", smcp_rules, [])
    print(f"smcp: {len(r)} replaced, {len(a)} appended")
    r, a = smcp1.patch_feature(font, "c2sc", c2sc_rules, [])
    print(f"c2sc: {len(r)} replaced, {len(a)} appended")

    font.save(GLYPHS_PATH)
    print(f"saved {GLYPHS_PATH}")


if __name__ == "__main__":
    main()
