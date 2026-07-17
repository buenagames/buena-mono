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
           red="#ff5f57", yellow="#febc2e", tgreen="#28c840")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size, fill, anchor="start", weight=400):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'xml:space="preserve">{esc(s)}</text>')


def rect(x, y, w, h, fill, r=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'


def circle(cx, cy, r, fill):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'


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
    body.append(rect(wx, wy+700, ww, 2, "#1e1e1e"))
    term = [
        [("$", K), (" npm run build", F)],
        [("> ", K), ("building buena-mono ...", PAL["muted"])],
        [("+ ", ST), ("5,080 glyphs · 971 languages", F)],
        [("  wght 100-800 · slnt 0 to -10°", PAL["muted"])],
    ]
    ty = wy + 764
    for row in term:
        body.append(code_line(wx+56, ty, S, row)); ty += int(S*1.4)
    # statusline
    body.append(f'<rect x="{wx+2}" y="{wy+928}" width="{ww-4}" height="54" rx="0" fill="#111111"/>')
    body.append(rect(wx+2, wy+928, 150, 54, PAL["terra"]))
    body.append(t(wx+28, wy+964, "NORMAL", 24, "#000000"))
    body.append(t(wx+178, wy+964, "buena.ts", 24, PAL["muted"]))
    body.append(t(wx+ww-24, wy+964, "utf-8   ln 11, col 18   Buena Mono", 24, PAL["muted"], "end"))
    return W, H, body


def main():
    outdir = "docs/marketing/svg"
    os.makedirs(outdir, exist_ok=True)
    for name, fn in [("social-square", social_square), ("hero", hero), ("cli", cli)]:
        w, h, body = fn()
        open(f"{outdir}/{name}.svg", "w").write(svg(w, h, body))
    print(f"SVGs written to {outdir}")


if __name__ == "__main__":
    main()
