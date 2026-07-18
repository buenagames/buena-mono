# Generates docs/cli.png — a code-window + terminal + statusline showcase
# rendering Buena Mono in the "Show Syntax" palette (terracotta / green /
# blue on black). Run after `make build` (or with the committed fonts):
#   $ python3 docs/cli.py --output docs/cli.png
#
# Monospace makes token placement exact: every glyph shares one advance,
# so a token at column c sits at x = MARGIN + c * charW — no measuring.

import argparse

from drawbot_skia.drawbot import *
from fontTools.ttLib import TTFont

WIDTH, HEIGHT = 2048, 1152
FONT_PATH = "fonts/variable/BuenaMono-VF.ttf"

# ---- Show Syntax palette -------------------------------------------------
def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))

BG      = hx("000000")   # page
PANE    = hx("0d0d0d")   # window fill (lifts off pure black)
BORDER  = hx("262626")   # window border
HAIR    = hx("1e1e1e")   # inner dividers
FG      = hx("ededed")   # base text
MUTED   = hx("8a8a8a")   # secondary
LN      = hx("4a4a4a")   # line numbers
COM     = hx("6e6e6e")   # comments
KW      = hx("d97757")   # keywords (terracotta)
STR     = hx("10a37f")   # strings (green)
FN      = hx("4285f4")   # functions / types (blue)
NUM     = hx("4fa8ff")   # numbers (light blue)
TERRA   = hx("d97757")
GREEN   = hx("10a37f")
CARET   = hx("00c4ff")   # live caret / block cursor
RED     = hx("ff5f57")   # traffic lights
YEL     = hx("febc2e")
GRN_DOT = hx("28c840")


def rrect(x, y, w, h, r, tl=True, tr=True, br=True, bl=True):
    """Rounded-rect BezierPath with per-corner control (drawbot y-up coords)."""
    rtl, rtr = (r if tl else 0), (r if tr else 0)
    rbr, rbl = (r if br else 0), (r if bl else 0)
    p = BezierPath()
    p.moveTo((x + rbl, y))
    p.lineTo((x + w - rbr, y))
    if rbr: p.arcTo((x + w, y), (x + w, y + rbr), rbr)
    p.lineTo((x + w, y + h - rtr))
    if rtr: p.arcTo((x + w, y + h), (x + w - rtr, y + h), rtr)
    p.lineTo((x + rtl, y + h))
    if rtl: p.arcTo((x, y + h), (x, y + h - rtl), rtl)
    p.lineTo((x, y + rbl))
    if rbl: p.arcTo((x, y), (x + rbl, y), rbl)
    p.closePath()
    return p

# ---- code content: rows of (text, color) segments; None = blank line -----
CODE = [
    [("// buena mono · a writer-first monospace", COM)],
    [("import", KW), (" { shape } ", FG), ("from", KW), (" ", FG), ('"./buena"', STR), (";", FG)],
    [("const", KW), (" weights ", FG), ("=", FG), (" [", FG), ("100", NUM), (", ", FG),
     ("400", NUM), (", ", FG), ("700", NUM), (", ", FG), ("800", NUM), ("];", FG)],
    None,
    [("export", KW), (" ", FG), ("function", KW), (" ", FG), ("render", FN),
     ("(src: ", FG), ("string", FN), ("): ", FG), ("Glyph", FN), ("[] {", FG)],
    [("  return", KW), (" src", FG)],
    [('    .split(', FG), ('""', STR), (")", FG)],
    [("    .filter((c) ", FG), ("=>", KW), (" c ", FG), ("!=", KW), (" ", FG), ('" "', STR), (")", FG)],
    [("    .map((c) ", FG), ("=>", KW), (" ", FG), ("shape", FN), ("(c));", FG)],
    [("}", FG)],
    None,
    [("// ligatures  ", COM), ("=>  !=  >=  ->  <=  ===  |>", KW)],
]

TERM = [
    [("$", TERRA), (" npm run build", FG)],
    [("▸", TERRA), (" building buena-mono …", MUTED)],
    [("✓", GREEN), (" 5,080 glyphs · 971 languages", FG)],
    [("  wght 100–800 · slnt 0 to −10°", MUTED)],
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", metavar="PNG", default="docs/cli.png")
    args = ap.parse_args()

    tt = TTFont(FONT_PATH)
    upm = tt["head"].unitsPerEm
    adv = tt["hmtx"]["A"][0]

    SIZE = 30
    charW = SIZE * adv / upm          # exact monospace advance
    lineH = 42
    MARGIN = 84                        # window inset from frame edge
    PAD = 56                           # content inset from window edge
    BAR_H = 54                         # statusline height
    R = 30                             # window corner radius

    newPage(WIDTH, HEIGHT)
    fill(*BG); rect(-2, -2, WIDTH + 2, HEIGHT + 2)

    # window (rounded outer border)
    wx, wy, ww, wh = MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEIGHT - 2 * MARGIN
    fill(*PANE); stroke(*BORDER); strokeWidth(2)
    drawPath(rrect(wx, wy, ww, wh, R)); stroke(None)

    # `top` = distance from the FRAME TOP; drawbot baseline y = HEIGHT - top.
    win_top = MARGIN                       # top edge of window, as a top-offset
    win_bot = HEIGHT - wy                  # bottom edge of window, as a top-offset

    def run(segments, top, x0):
        y = HEIGHT - top
        x = x0
        font(FONT_PATH); fontSize(SIZE)
        for txt, col in segments:
            fill(*col)
            text(txt, (x, y), align="left")
            x += len(txt) * charW

    # --- title bar: three dots + filename, hairline under ---
    tb = win_top + 60
    cx = wx + PAD + 10
    dot_y = HEIGHT - (tb - 2)
    for c in (RED, YEL, GRN_DOT):
        fill(*c); oval(cx - 9, dot_y - 9, 18, 18); cx += 38
    font(FONT_PATH); fontSize(24); fill(*MUTED)
    text("buena.ts", (cx + 22, dot_y - 8), align="left")
    stroke(*HAIR); strokeWidth(2)
    line((wx, HEIGHT - (win_top + 100)), (wx + ww, HEIGHT - (win_top + 100)))
    stroke(None)

    # --- code ---
    gutter_x = wx + PAD + 44
    text_x = wx + PAD + 88
    top = win_top + 152
    ln = 1
    for row in CODE:
        if row is not None:
            font(FONT_PATH); fontSize(SIZE); fill(*LN)
            text(str(ln), (gutter_x, HEIGHT - top), align="right")
            run(row, top, text_x)
        ln += 1
        top += lineH

    # --- terminal band: pinned above the statusline, divider above it ---
    term_h = (len(TERM) + 1) * lineH + 24   # +1 line for the live prompt
    term_bottom = win_bot - BAR_H - 30     # keep clear of the statusline
    term_top = term_bottom - term_h
    stroke(*HAIR); strokeWidth(2)
    line((wx, HEIGHT - (term_top - 20)), (wx + ww, HEIGHT - (term_top - 20)))
    stroke(None)
    t = term_top + 34
    for row in TERM:
        run(row, t, wx + PAD)
        t += lineH
    # live prompt with a caret-cyan block cursor
    run([("$ ", KW)], t, wx + PAD)
    fill(*CARET)
    rect(wx + PAD + 2 * charW, HEIGHT - t - 4, charW, SIZE * 1.1)

    # --- statusline: terracotta NORMAL block + file, right-aligned meta ---
    bar_y = wy + 2                         # just inside the bottom border
    fill(*hx("111111"))
    drawPath(rrect(wx + 2, bar_y, ww - 4, BAR_H, R - 3, tl=False, tr=False))
    seg = " NORMAL "
    seg_w = len(seg) * (24 * adv / upm)
    fill(*TERRA)
    drawPath(rrect(wx + 2, bar_y, seg_w, BAR_H, R - 3, tl=False, tr=False, br=False))
    font(FONT_PATH); fontSize(24)
    ty = bar_y + BAR_H / 2 - 8
    fill(*hx("000000")); text(seg, (wx + 10, ty), align="left")
    fill(*MUTED); text("  buena.ts", (wx + 2 + seg_w + 8, ty), align="left")
    fill(*MUTED)
    text("utf-8   ln 11, col 18   Buena Mono  ", (wx + ww - 8, ty), align="right")

    saveImage(args.output)
    print("DrawBot: cli.png done")


if __name__ == "__main__":
    main()
