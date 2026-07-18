# Emit SVG versions of key templates for drag-drop import into Figma.
# SVG <text> imports as EDITABLE text layers (font must be installed in the
# Figma desktop app). Bypasses the MCP rate limit + plugin font-load block.
#   $ python3 docs/marketing_svg.py   ->  docs/marketing/svg/*.svg

import os

FONT = "Buena Mono"
ADV = 0.618  # Buena Mono advance / UPM (monospace)

PAL = dict(bg="#000000", pane="#0d0d0d", border="#262626", fg="#ededed",
           muted="#8a8a8a", ln="#4a4a4a", com="#6e6e6e", terra="#d97757",
           green="#10a37f", blue="#4285f4", num="#4fa8ff",
           red="#ff5f57", yellow="#febc2e", tgreen="#28c840",
           # Show Syntax — parts-of-speech (iA Writer palette) from
           # buena-mono.buenalabs.io; dark = on black, light = on white.
           syn_adj="#c99a5b", syn_noun="#e0603f", syn_adv="#b189d6",
           syn_verb="#6aa3dd", syn_conj="#79b06f",
           syn_adj_light="#8a6a3a", syn_noun_light="#c0392b", syn_adv_light="#7e57b0",
           syn_verb_light="#2f6fb0", syn_conj_light="#4d8248",
           caret="#00c4ff")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size, fill, anchor="start", weight=400, italic=False, feat=None):
    sty = ""
    if italic:
        sty += "font-style:italic;"
    if feat:
        sty += f"font-feature-settings:'{feat}';"
    sa = f' style="{sty}"' if sty else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'xml:space="preserve"{sa}>{esc(s)}</text>')


def rect(x, y, w, h, fill, r=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'


def circle(cx, cy, r, fill):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'


def sline(x1, y1, x2, y2, stroke, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{w}"{d}/>'


def srect(x, y, w, h, stroke, sw=2, dash=None, fill="none", fillop=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    fo = f' fill-opacity="{fillop}"' if fillop is not None else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{fo} '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def tls(x, y, s, size, fill, ls, anchor="start"):
    """letter-spaced text (for spec labels)."""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" xml:space="preserve">{esc(s)}</text>')


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n{rect(0,0,w,h,PAL["bg"])}\n' + "\n".join(body) + "\n</svg>")


def code_line(x, y, size, tokens):
    """One <text> with coloured <tspan>s; monospace keeps alignment."""
    spans = "".join(f'<tspan fill="{c}">{esc(tok)}</tspan>' for tok, c in tokens)
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'xml:space="preserve">{spans}</text>')


def social_square():
    W = H = 1080
    b = [
        t(W/2, 430, "buena mono", 116, PAL["fg"], "middle"),
        t(W/2, 540, "a writer-first monospace typeface", 30, PAL["muted"], "middle"),
        t(W/2, 690, "0O 1lI  => != >= ->  ß ə ħ", 44, PAL["fg"], "middle"),
        rect(W/2-60, 745, 120, 5, PAL["terra"]),
        t(W/2, 900, "5,080 glyphs · 971 languages", 26, PAL["muted"], "middle"),
        t(W/2, 946, "wght 100-800 · slnt 0 to -10° · OFL", 26, PAL["muted"], "middle"),
    ]
    return W, H, b


def hero():
    W, H = 2048, 1024
    b = [
        t(128, 150, "buena mono regular", 40, PAL["fg"]),
        rect(128, 168, 1792, 3, PAL["fg"]),
        t(128, 700, "AaBb", 620, PAL["fg"]),
        rect(128, 852, 1792, 3, PAL["fg"]),
        t(1920, 916, "OFL v1.1", 40, PAL["fg"], "end"),
    ]
    return W, H, b


def cli():
    W, H = 2048, 1152
    wx, wy, ww, wh = 84, 84, 1880, 984
    S = 30; cw = S * ADV; gx = wx + 200
    dots = [circle(wx+56+i*38, wy+62, 9, c) for i, c in
            enumerate((PAL["red"], PAL["yellow"], PAL["tgreen"]))]
    K, F, ST, FN, N, C = PAL["terra"], PAL["fg"], PAL["green"], PAL["blue"], PAL["num"], PAL["com"]
    rows = [
        [("// buena mono · a writer-first monospace", C)],
        [("import", K), (" { shape } ", F), ("from", K), (" ", F), ('"./buena"', ST), (";", F)],
        [("const", K), (" weights = [", F), ("100", N), (", ", F), ("400", N), (", ", F),
         ("700", N), (", ", F), ("800", N), ("];", F)],
        None,
        [("export", K), (" ", F), ("function", K), (" ", F), ("render", FN),
         ("(src: ", F), ("string", FN), ("): ", F), ("Glyph", FN), ("[] {", F)],
        [("  return", K), (" src", F)],
        [("    .split(", F), ('""', ST), (")", F)],
        [("    .filter((c) => c != ", F), ('" "', ST), (")", F)],
        [("    .map((c) => ", F), ("shape", FN), ("(c));", F)],
        [("}", F)],
        None,
        [("// ligatures  => != >= -> <= === |>", C)],
    ]
    body = [rect(wx, wy, ww, wh, PAL["pane"], 30)]
    body.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="30" '
                f'fill="none" stroke="{PAL["border"]}" stroke-width="2"/>')
    body += dots
    body.append(t(wx+200, wy+70, "buena.ts", 24, PAL["muted"]))
    body.append(rect(wx, wy+108, ww, 2, "#1e1e1e"))
    ln = 1; y = wy + 190
    for row in rows:
        if row is not None:
            body.append(t(wx+150, y, str(ln), S, PAL["ln"], "end"))
            body.append(code_line(gx, y, S, row))
        ln += 1; y += int(S*1.4)
    # terminal
    body.append(rect(wx, wy+686, ww, 2, "#1e1e1e"))
    term = [
        [("$", K), (" npm run build", F)],
        [("> ", K), ("building buena-mono ...", PAL["muted"])],
        [("+ ", ST), ("5,080 glyphs · 971 languages", F)],
        [("  wght 100-800 · slnt 0 to -10°", PAL["muted"])],
    ]
    ty = wy + 726
    for row in term:
        body.append(code_line(wx+56, ty, S, row)); ty += int(S*1.4)
    # live prompt with a caret-cyan block cursor
    body.append(code_line(wx+56, ty, S, [("$ ", K)]))
    cwv = S * ADV
    body.append(rect(wx+56 + int(2*cwv), ty - 26, int(cwv), int(S*1.1), PAL["caret"]))
    # statusline
    body.append(f'<rect x="{wx+2}" y="{wy+928}" width="{ww-4}" height="54" rx="0" fill="#111111"/>')
    body.append(rect(wx+2, wy+928, 150, 54, PAL["terra"]))
    body.append(t(wx+28, wy+964, "NORMAL", 24, "#000000"))
    body.append(t(wx+178, wy+964, "buena.ts", 24, PAL["muted"]))
    body.append(t(wx+ww-24, wy+964, "utf-8   ln 11, col 18   Buena Mono", 24, PAL["muted"], "end"))
    return W, H, body


def code_window_svg(x, y, w, h, size=30):
    K, F, ST, FN, C = PAL["terra"], PAL["fg"], PAL["green"], PAL["blue"], PAL["com"]
    els = [rect(x, y, w, h, PAL["pane"], 24),
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="none" '
           f'stroke="{PAL["border"]}" stroke-width="2"/>']
    for i, c in enumerate((PAL["red"], PAL["yellow"], PAL["tgreen"])):
        els.append(circle(x + 42 + i * 34, y + 46, 8, c))
    rows = [
        [("const", K), (" g ", F), ("= ", F), ("shape", FN), ("(", F), ('"a"', ST), (");", F)],
        [("x >= 0 ? x : -x", F)],
        [("// ", C), ("=> != >= -> ===", K)],
    ]
    cy = y + 108
    for row in rows:
        els.append(code_line(x + 40, cy, size, row)); cy += int(size * 1.5)
    return els


# ---- core images ----
def social_preview():
    W, H = 1280, 640
    return W, H, [
        t(W/2, 250, "buena mono", 128, PAL["fg"], "middle"),
        t(W/2, 340, "a writer-first monospace typeface", 34, PAL["muted"], "middle"),
        t(W/2, 462, "0O 1lI  => != >= ->  ß ə ħ", 52, PAL["fg"], "middle"),
        t(W/2, 572, "5,080 glyphs · 971 languages · wght 100-800 · slnt 0 to -10°", 28, PAL["muted"], "middle"),
    ]


def specimen():
    W, H = 1680, 917
    x = 72
    b = [t(x, 190, "buena mono", 132, PAL["fg"]),
         t(x, 268, "Writer-first monospace · weight 100-800 · slant 0 to -10°", 34, PAL["muted"])]
    y = 360
    for wght in (100, 300, 500, 700, 800):
        b.append(t(x, y, "Sphinx of black quartz, judge my vow", 44, PAL["fg"], weight=wght)); y += 58
    y += 22
    K, F, N = PAL["terra"], PAL["fg"], PAL["num"]
    b.append(code_line(x, y, 44, [("const", K), (" inc ", F), ("= (x) ", F), ("=>", K), (" x ", F),
             (">=", K), (" 0 ", F), ("?", K), (" x + ", F), ("1", N), (" : x;  a ", F), ("!=", K), (" b", F)]))
    y += 80
    b.append(t(x, y, "AÀÇ gβ Дж 0123 @#$€ →≠≈∑ ░▒▓█ (){}[]", 46, PAL["fg"]))
    return W, H, b


def stylistic_sets():
    W, H = 1120, 1324
    SS = [("ss01", "Single-story a", "a"), ("ss02", "Descending f", "f"), ("ss03", "Tailed l", "l"),
          ("ss04", "Serifed i and j", "ij"), ("ss05", "Alternate g", "g"), ("ss06", "Alternate g (2)", "g"),
          ("ss07", "Serifed i", "i"), ("ss08", "Straight-tail y", "y"), ("ss09", "Curved-tail y", "y"),
          ("ss10", "Plain zero", "0"), ("ss11", "Dotted zero", "0"), ("ss12", "Alternate r", "r"),
          ("ss13", "Machine-readable", "=>")]
    b = []; y = 130
    for tag, label, ch in SS:
        b += [t(64, y, f"{tag}   {label}", 30, PAL["muted"]),
              t(524, y, ch, 60, PAL["fg"]),
              t(636, y, "→", 36, PAL["ln"]),
              t(724, y, ch, 60, PAL["fg"], feat=tag)]
        y += 92
    return W, H, b


def charset(label, italic=False):
    W, H = 2048, 1024
    lines = ["ABCDEFGHIJKLMNOPQRS", "TUVWXYZ0123456789",
             "abcdefghijklmnopqrs", "tuvwxyz,.;:!@#$%&*(){}[]"]
    b = [t(128, 150, label, 40, PAL["fg"], italic=italic), rect(128, 168, 1792, 3, PAL["fg"])]
    y = 400
    for ln in lines:
        b.append(t(128, y, ln, 118, PAL["fg"], italic=italic)); y += 135
    b += [rect(128, 852, 1792, 3, PAL["fg"]),
          t(1920, 916, "OFL v1.1", 40, PAL["fg"], "end", italic=italic)]
    return W, H, b


# ---- marketing ----
def ig_portrait():
    W, H = 1080, 1350
    return W, H, ([t(W/2, 300, "buena mono", 104, PAL["fg"], "middle"),
                   t(W/2, 400, "writer-first monospace", 30, PAL["muted"], "middle")]
                  + code_window_svg(90, 520, 900, 470)
                  + [t(W/2, 1150, "free · open source · OFL", 30, PAL["terra"], "middle"),
                     t(W/2, 1240, "5,080 glyphs · 971 languages", 26, PAL["muted"], "middle")])


def story():
    W, H = 1080, 1920
    return W, H, ([t(W/2, 340, "buena", 150, PAL["fg"], "middle"),
                   t(W/2, 500, "mono", 150, PAL["fg"], "middle"),
                   t(W/2, 620, "writer-first monospace", 32, PAL["muted"], "middle")]
                  + code_window_svg(90, 760, 900, 470)
                  + [t(W/2, 1560, "free · open source", 34, PAL["terra"], "middle"),
                     t(W/2, 1660, "5,080 glyphs · 971 languages", 28, PAL["muted"], "middle"),
                     t(W/2, 1780, "buena-mono.buenalabs.io", 30, PAL["fg"], "middle")])


def x_card():
    W, H = 1600, 900
    return W, H, [
        t(W/2, 320, "buena mono", 120, PAL["fg"], "middle"),
        t(W/2, 430, "a writer-first monospace typeface", 34, PAL["muted"], "middle"),
        t(W/2, 580, "0O 1lI  => != >= ->  ∑ √ ≈  ß ə ħ", 46, PAL["fg"], "middle"),
        t(W/2, 760, "5,080 glyphs · 971 languages · wght 100-800 · slnt 0 to -10°", 26, PAL["muted"], "middle"),
    ]


def linkedin():
    W, H = 1200, 628
    return W, H, [
        t(W/2, 240, "buena mono", 92, PAL["fg"], "middle"),
        t(W/2, 330, "a writer-first monospace typeface", 28, PAL["muted"], "middle"),
        rect(W/2-60, 400, 120, 5, PAL["terra"]),
        t(W/2, 470, "5,080 glyphs · 971 languages · wght 100-800 · OFL", 24, PAL["muted"], "middle"),
    ]


def youtube_thumb():
    W, H = 1280, 720
    return W, H, ([t(80, 250, "buena", 108, PAL["fg"]), t(80, 372, "mono", 108, PAL["fg"]),
                   t(80, 468, "the monospace for", 34, PAL["muted"]),
                   t(80, 520, "writers who code", 34, PAL["fg"]),
                   rect(80, 560, 90, 6, PAL["terra"])]
                  + code_window_svg(720, 150, 480, 420))


def youtube_banner():
    W, H = 2560, 1440
    return W, H, [
        t(W/2, 700, "buena mono", 128, PAL["fg"], "middle"),
        t(W/2, 790, "a writer-first monospace typeface · free · open source", 30, PAL["muted"], "middle"),
    ]


def app_icon():
    W = H = 1024
    tx, ty, ts = 120, 120, 784
    GRAY = "#3a3a3a"
    b = [rect(tx, ty, ts, ts, PAL["pane"], 150),
         f'<rect x="{tx}" y="{ty}" width="{ts}" height="{ts}" rx="150" fill="none" '
         f'stroke="{PAL["border"]}" stroke-width="6"/>']
    for i, c in enumerate((PAL["red"], PAL["yellow"], PAL["tgreen"])):
        b.append(circle(tx + 104 + i * 70, ty + 90, 26, c))
    b += [rect(tx+90, ty+210, 200, 40, PAL["terra"], 20), rect(tx+320, ty+210, 230, 40, GRAY, 20),
          rect(tx+170, ty+300, 190, 40, GRAY, 20), rect(tx+170, ty+390, 150, 40, GRAY, 20),
          rect(tx+350, ty+382, 46, 66, PAL["caret"])]  # block cursor (caret #00c4ff)
    return W, H, b


def iphone_screenshot():
    W, H = 1290, 2796
    return W, H, ([t(100, 360, "the monospace", 92, PAL["fg"]),
                   t(100, 480, "for writers", 92, PAL["muted"]),
                   t(100, 600, "who code.", 92, PAL["terra"])]
                  + code_window_svg(95, 760, 1100, 700, size=34)
                  + [t(W/2, 2180, "5,080 glyphs · 971 languages", 32, PAL["fg"], "middle"),
                     t(W/2, 2280, "free · open source · OFL", 32, PAL["terra"], "middle"),
                     t(W/2, 2480, "buena-mono.buenalabs.io", 34, PAL["muted"], "middle")])


def marketplace():
    W, H = 1600, 1000
    return W, H, [
        t(W/2, 300, "buena mono", 128, PAL["fg"], "middle"),
        t(W/2, 470, "AaBbCc 0123 => != >=", 72, PAL["fg"], "middle"),
        t(W/2, 620, "a writer-first monospace typeface", 32, PAL["muted"], "middle"),
        t(W/2, 780, "5,080 glyphs · 971 languages · wght 100-800 · slnt 0 to -10°", 26, PAL["muted"], "middle"),
    ]


def web_hero():
    W, H = 1920, 1080
    return W, H, ([t(130, 380, "buena", 150, PAL["fg"]), t(130, 540, "mono", 150, PAL["fg"]),
                   t(130, 650, "the monospace for writers who code", 34, PAL["muted"]),
                   rect(130, 730, 360, 90, PAL["terra"], 45),
                   t(178, 788, "Get it — free", 34, "#000000")]
                  + code_window_svg(1080, 250, 700, 580, size=32))


# ---- brand guidelines ----
def logo_exclusion_zone():
    W, H = 1920, 1200
    GUIDE = PAL["green"]
    size = 150
    cwid = size * ADV
    mark = "buena mono"
    mw = len(mark) * cwid
    mx = (W - mw) / 2
    baseline = 650
    cap = size * 0.729
    Xu = round(cap)                       # exclusion unit = cap height
    bx, by = round(mx - Xu), round(baseline - cap - Xu)
    bw, bh = round(mw + 2 * Xu), round(cap + 2 * Xu)
    return W, H, [
        sline(bx, 0, bx, H, GUIDE, 1.5, "6 9"),
        sline(bx + bw, 0, bx + bw, H, GUIDE, 1.5, "6 9"),
        sline(0, by, W, by, GUIDE, 1.5, "6 9"),
        sline(0, by + bh, W, by + bh, GUIDE, 1.5, "6 9"),
        srect(bx, by, bw, bh, GUIDE, 2),
        srect(bx + bw - Xu, by, Xu, Xu, GUIDE, 1.5, fill=GUIDE, fillop=0.14),
        t(bx + bw - Xu/2, by + Xu/2 + 18, "×", 54, GUIDE, "middle"),
        t(W/2, baseline, mark, size, PAL["fg"], "middle"),
        sline(bx, by + bh + 96, W/2 - 190, by + bh + 96, PAL["muted"], 1),
        sline(W/2 + 190, by + bh + 96, bx + bw, by + bh + 96, PAL["muted"], 1),
        tls(W/2, by + bh + 106, "EXCLUSION ZONE", 26, PAL["fg"], 8, "middle"),
    ]


def stats_board():
    W, H = 2000, 1200
    cards = [
        ("Glyphs", "5,080", PAL["syn_adj"]),
        ("Languages", "971", PAL["syn_noun"]),
        ("Masters", "8", PAL["syn_adv"]),
        ("OpenType features", "51", PAL["syn_verb"]),
        ("Stylistic sets", "13", PAL["syn_conj"]),
        ("Weight range", "100-800", PAL["green"]),
    ]
    mx, my, gap = 60, 60, 40
    cw = (W - 2 * mx - 2 * gap) / 3
    ch = (H - 2 * my - gap) / 2
    ink = "#0a0a0a"
    b = []
    for i, (label, num, col) in enumerate(cards):
        r, c = divmod(i, 3)
        x = mx + c * (cw + gap); y = my + r * (ch + gap)
        b += [rect(x, y, cw, ch, col, 20),
              t(x + 42, y + 74, label, 32, ink),
              t(x + 42, y + ch - 56, num, 118, ink, weight=500)]
    return W, H, b


def type_system():
    W, H = 2000, 1400
    b = [t(100, 90, "buenalabs.io", 26, PAL["muted"]),
         t(W - 100, 90, "buena mono · v1.225", 26, PAL["muted"], "end"),
         t(100, 390, "type", 200, PAL["fg"]),
         t(100, 570, "system", 200, PAL["fg"]),
         t(100, 668, "start small", 34, PAL["muted"]),
         sline(100, 724, W - 100, 724, PAL["border"], 2)]
    cols = ["Headings", "Body", "Elements", "Links"]
    cx = [100, 575, 1050, 1525]
    for i, name in enumerate(cols):
        b.append(t(cx[i], 802, name, 28, PAL["muted"]))
        if i < 3:
            b.append(sline(cx[i + 1] - 38, 764, cx[i + 1] - 38, H - 80, PAL["border"], 1))

    def spec(x, y, txt, size, px, fill=None, ls=None):
        node = tls(x, y, txt, size, fill or PAL["fg"], ls) if ls else t(x, y, txt, size, fill or PAL["fg"])
        return [node, t(x, y + 44, px, 22, PAL["muted"])]

    b += spec(cx[0], 960, "Display", 60, "128 px")
    b += spec(cx[0], 1080, "Heading", 46, "72 px")
    b += spec(cx[0], 1190, "Title", 36, "48 px")
    b += [t(cx[1], 950, "Writer-first monospace,", 24, PAL["fg"]),
          t(cx[1], 986, "tuned for prose and", 24, PAL["fg"]),
          t(cx[1], 1022, "code alike.", 24, PAL["fg"]),
          t(cx[1], 1068, "20 px", 22, PAL["muted"]),
          t(cx[1], 1156, "Body copy sets clean", 18, PAL["fg"]),
          t(cx[1], 1184, "at small sizes.", 18, PAL["fg"]),
          t(cx[1], 1226, "16 px", 22, PAL["muted"])]
    b += spec(cx[2], 952, "Subtitle", 24, "16 px")
    b += spec(cx[2], 1062, "Caption", 20, "12 px")
    b += spec(cx[2], 1172, "OVERLINE", 16, "10 px", ls=3)
    b += spec(cx[3], 952, "BUTTON", 22, "14 px", fill=PAL["terra"], ls=2)
    b += spec(cx[3], 1062, "Button", 18, "12 px")
    b += spec(cx[3], 1172, "Link", 16, "10 px", fill=PAL["blue"])
    return W, H, b


def main():
    outdir = "docs/marketing/svg"
    os.makedirs(outdir, exist_ok=True)
    items = [
        ("hero", hero), ("cli", cli), ("social-preview", social_preview),
        ("specimen", specimen), ("stylistic-sets", stylistic_sets),
        ("character-set-roman", lambda: charset("buena mono regular")),
        ("character-set-italic", lambda: charset("buena mono italic", italic=True)),
        ("social-square", social_square), ("ig-portrait", ig_portrait),
        ("story-reel-short", story), ("x-card", x_card), ("linkedin", linkedin),
        ("youtube-thumbnail", youtube_thumb), ("youtube-banner", youtube_banner),
        ("aso-app-icon", app_icon), ("aso-iphone-screenshot", iphone_screenshot),
        ("aso-marketplace-feature", marketplace), ("aso-web-hero", web_hero),
        ("brand-logo-exclusion-zone", logo_exclusion_zone),
        ("brand-stats", stats_board),
        ("brand-type-system", type_system),
    ]
    for name, fn in items:
        w, h, body = fn()
        open(f"{outdir}/{name}.svg", "w").write(svg(w, h, body))
    print(f"{len(items)} SVGs written to {outdir}")


if __name__ == "__main__":
    main()
