#!/usr/bin/env python3
"""v1.228 batch — three backlog fixes, written into the .glyphs source.

BUENA-342  braces sit ~39u low → shift braceleft/braceright +39 (all masters)
           to co-center with ()[] on the cap midpoint (~350).
BUENA-343  ░▒▓ shades live on a different cell than █ (x16-602,y-234..1087 vs
           x9-609,y-300..900) → affine-refit each master's shade onto █'s cell
           so they align + share the block/sextant/octant cell (keeps the
           artist's stipple, just repositions/rescales it).
BUENA-346  add the quick-win glyphs peers ship: corner half-brackets ⸢⸣⸤⸥
           (U+2E22-25) and double square brackets ⟦⟧ (U+27E6-27E7) derived
           per-master from the real bracket geometry (so they track weight),
           plus the heavy black cardinal arrows ➡⬅⬆⬇ (U+27A1,2B05-07) designed
           on the cell and pinned (dingbat pattern). NB: the issue assumed ➡
           already existed — it doesn't, so we add all four for a complete set.

    python3 scripts/add-v1228-glyphs.py --preview out.png
    python3 scripts/add-v1228-glyphs.py --dry-run
    python3 scripts/add-v1228-glyphs.py --apply
"""
import argparse

GLYPHS_PATH = "sources/BuenaMono.glyphs"

BRACE_SHIFT = 39                       # 342: 311 -> 350
BLOCK_CELL = (9, 609, -300, 900)       # 343: x0,x1,y0,y1 of █ (U+2588)
SHADES = ["uni2591", "uni2592", "uni2593"]   # ░▒▓ (not the ltshade/shade/dkshade aliases)

# 346 heavy black arrow — a chunky shaft (~150u) + solid triangular head,
# centered on the cell midline (x=309) and the arrow center (y=349). Points
# trace the → outline; the other three are 90/180/270 rotations about (309,349).
# These read as true "BLACK …WARDS ARROW" dingbats and are pinned (identical in
# every master), matching the dingbat pattern used for the other symbol glyphs.
ACX, ACY = 309, 349
ARROW_RIGHT = [(40, 274), (360, 274), (360, 174), (585, 349),
               (360, 524), (360, 424), (40, 424)]


def rot(pt, deg):
    x, y = pt[0] - ACX, pt[1] - ACY
    if deg == 0:   nx, ny = x, y
    elif deg == 90:  nx, ny = -y, x     # CCW → up
    elif deg == 180: nx, ny = -x, -y
    elif deg == 270: nx, ny = y, -x     # CW → down
    return (ACX + nx, ACY + ny)


def bracket_geom(layer):
    """Distinct X/Y of a bracket outline → structural coordinates."""
    xs = sorted({round(n.position.x) for p in layer.paths for n in p.nodes})
    ys = sorted({round(n.position.y) for p in layer.paths for n in p.nodes})
    return xs, ys


def rects_left_corner(xs, ys, top):
    """⸢ / ⸤ from bracketleft geometry. xs=[left,stem_r,arm_end], ys=[bo,bi,ti,to]."""
    left, stem_r, arm_end = xs[0], xs[1], xs[2]
    bo, bi, ti, to = ys[0], ys[1], ys[2], ys[3]
    mid = 350
    if top:   # ⸢ top-left: top arm + stem down to mid
        arm = (left, ti, arm_end, to)
        stem = (left, mid, stem_r, to)
    else:     # ⸤ bottom-left: bottom arm + stem up to mid
        arm = (left, bo, arm_end, bi)
        stem = (left, bo, stem_r, mid)
    return [arm, stem]


def rects_right_corner(xs, ys, top):
    """⸣ / ⸥ from bracketright geometry. xs=[arm_end,stem_l,right]."""
    arm_end, stem_l, right = xs[0], xs[1], xs[2]
    bo, bi, ti, to = ys[0], ys[1], ys[2], ys[3]
    mid = 350
    if top:
        arm = (arm_end, ti, right, to)
        stem = (stem_l, mid, right, to)
    else:
        arm = (arm_end, bo, right, bi)
        stem = (stem_l, bo, right, mid)
    return [arm, stem]


def double_left(xs, ys):
    """⟦ = bracketleft + an inner vertical bar of stem width, one gap to its right.
    arm_end is DERIVED so the arms always enclose the inner bar (the single
    bracket's arm_end is too short once the stem thickens — see BUENA-346)."""
    left, stem_r = xs[0], xs[1]
    bo, bi, ti, to = ys[0], ys[1], ys[2], ys[3]
    sw = stem_r - left
    gap = round(sw * 0.5)
    inner_l = stem_r + gap
    inner_r = inner_l + sw
    arm_end = inner_r + gap
    stem = (left, bo, stem_r, to)
    top_arm = (left, ti, arm_end, to)
    bot_arm = (left, bo, arm_end, bi)
    inner = (inner_l, bi, inner_r, ti)                    # inner vertical, between arms
    return [stem, top_arm, bot_arm, inner]


def double_right(xs, ys):
    stem_l, right = xs[1], xs[2]
    bo, bi, ti, to = ys[0], ys[1], ys[2], ys[3]
    sw = right - stem_l
    gap = round(sw * 0.5)
    inner_r = stem_l - gap
    inner_l = inner_r - sw
    arm_end = inner_l - gap
    stem = (stem_l, bo, right, to)
    top_arm = (arm_end, ti, right, to)
    bot_arm = (arm_end, bo, right, bi)
    inner = (inner_l, bi, inner_r, ti)
    return [stem, top_arm, bot_arm, inner]


def rect_to_pts(r):
    x0, y0, x1, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ---- glyph plan: name -> (codepoint, builder) ------------------------------
def plan(font):
    """Return {name: (cp, per_master_fn)} where per_master_fn(layer_of_master)
    returns a list of contours (each a list of (x,y) pts)."""
    bl = font.glyphs["bracketleft"]
    br = font.glyphs["bracketright"]
    blL = {l.layerId: l for l in bl.layers}
    brL = {l.layerId: l for l in br.layers}

    def corner(side, top):
        def fn(master_id):
            if side == "L":
                xs, ys = bracket_geom(blL[master_id]); rs = rects_left_corner(xs, ys, top)
            else:
                xs, ys = bracket_geom(brL[master_id]); rs = rects_right_corner(xs, ys, top)
            return [rect_to_pts(r) for r in rs]
        return fn

    def dbl(side):
        def fn(master_id):
            if side == "L":
                xs, ys = bracket_geom(blL[master_id]); rs = double_left(xs, ys)
            else:
                xs, ys = bracket_geom(brL[master_id]); rs = double_right(xs, ys)
            return [rect_to_pts(r) for r in rs]
        return fn

    def arrow(deg):
        pts = [rot(p, deg) for p in ARROW_RIGHT]
        return lambda master_id: [pts]

    return {
        "u2E22": (0x2E22, corner("L", True)),    # ⸢ top-left
        "u2E23": (0x2E23, corner("R", True)),    # ⸣ top-right
        "u2E24": (0x2E24, corner("L", False)),   # ⸤ bottom-left
        "u2E25": (0x2E25, corner("R", False)),   # ⸥ bottom-right
        "u27E6": (0x27E6, dbl("L")),             # ⟦
        "u27E7": (0x27E7, dbl("R")),             # ⟧
        "u27A1": (0x27A1, arrow(0)),             # ➡
        "u2B05": (0x2B05, arrow(180)),           # ⬅
        "u2B06": (0x2B06, arrow(90)),            # ⬆
        "u2B07": (0x2B07, arrow(270)),           # ⬇
    }


# ---- preview ---------------------------------------------------------------
def preview(out_png):
    import glyphsLib
    from PIL import Image, ImageDraw
    font = glyphsLib.load(open(GLYPHS_PATH))
    reg = font.masters[1].id
    pl = plan(font)
    # shades refit (Regular) + braces (shifted) + new glyphs
    cells = []
    # new glyphs
    for name, (cp, fn) in pl.items():
        cells.append((name, fn(reg)))
    cols, cell = 5, 150
    rows = (len(cells) + cols - 1) // cols
    W, H = cols * cell, rows * cell
    img = Image.new("RGB", (W, H), (10, 10, 10)); d = ImageDraw.Draw(img)
    sx = (cell - 30) / 618; sy = (cell - 30) / 1000
    for k, (name, contours) in enumerate(cells):
        ox = (k % cols) * cell + 15; oy = (k // cols) * cell + 15
        d.rectangle([ox, oy, ox + 618 * sx, oy + 1000 * sy], outline=(40, 40, 40))
        for pts in contours:
            poly = [(ox + x * sx, oy + (800 - y) * sy) for x, y in pts]
            d.polygon(poly, fill=(235, 235, 235))
        d.text((ox + 2, oy + 2), name, fill=(120, 120, 120))
    img.save(out_png)
    print(f"preview ({len(cells)} new glyphs) -> {out_png}")


# ---- apply -----------------------------------------------------------------
def apply(dry):
    import glyphsLib
    from glyphsLib.classes import GSGlyph, GSLayer, GSPath, GSNode
    font = glyphsLib.load(open(GLYPHS_PATH))
    mids = [m.id for m in font.masters]

    # 342 — brace shift
    for gname in ["braceleft", "braceright"]:
        for L in font.glyphs[gname].layers:
            for p in L.paths:
                for n in p.nodes:
                    n.position = (n.position.x, n.position.y + BRACE_SHIFT)

    # 343 — shade refit onto █'s cell (per master, per shade)
    tx0, tx1, ty0, ty1 = BLOCK_CELL
    for gname in SHADES:
        for L in font.glyphs[gname].layers:
            xs = [n.position.x for p in L.paths for n in p.nodes]
            ys = [n.position.y for p in L.paths for n in p.nodes]
            if not xs:
                continue
            sx = (tx1 - tx0) / (max(xs) - min(xs)); sy = (ty1 - ty0) / (max(ys) - min(ys))
            mnx, mny = min(xs), min(ys)
            for p in L.paths:
                for n in p.nodes:
                    n.position = (tx0 + (n.position.x - mnx) * sx,
                                  ty0 + (n.position.y - mny) * sy)

    # 346 — new glyphs
    pl = plan(font)
    have = {g.name for g in font.glyphs}
    added = 0
    for name, (cp, fn) in pl.items():
        if name in have:
            continue
        added += 1
        if dry:
            continue
        g = GSGlyph(name); g.unicode = f"{cp:04X}"
        if cp in (0x27A1, 0x2B05, 0x2B06, 0x2B07):
            g.category, g.subCategory = "Symbol", "Arrow"
        elif cp in (0x27E6, 0x27E7):
            g.category, g.subCategory = "Punctuation", "Parenthesis"
        else:  # 2E22-25 corner half-brackets
            g.category, g.subCategory = "Punctuation", "Quote"
        g.export = True
        for mid in mids:
            L = GSLayer(); L.layerId = mid; L.associatedMasterId = mid; L.width = 618
            for pts in fn(mid):
                path = GSPath(); path.closed = True
                for (px, py) in pts:
                    path.nodes.append(GSNode(position=(px, py), type="line"))
                L.paths.append(path)
            g.layers.append(L)
        font.glyphs.append(g)

    print(f"342: braces +{BRACE_SHIFT}  |  343: refit {len(SHADES)} shades -> block cell  |  "
          f"346: {'would add' if dry else 'added'} {added} glyphs")
    if not dry:
        font.save(GLYPHS_PATH)
        print(f"saved {GLYPHS_PATH}  ({len(font.glyphs)} glyphs)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", metavar="PNG")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.preview:
        preview(a.preview)
    elif a.apply:
        apply(dry=False)
    else:
        apply(dry=True)


if __name__ == "__main__":
    main()
