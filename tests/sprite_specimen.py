#!/usr/bin/env python3
"""sprite_specimen.py — data-driven, column-perfect monospace TUI specimen.

Every section frame is width-computed and every row padded to the same width,
so any misalignment on render is the FONT's fault, not the specimen's. Scope is
TUI-relevant only (box-drawing, block elements, Braille, arrows, math, Powerline)
plus a few generated demos — no out-of-scope decor (weather/zodiac/religious/
astral/Nerd-PUA) that would tofu. The systematic sweeps are the visual
counterpart to `sprite_coverage.py`.

    python3 tests/sprite_specimen.py            # print
    python3 tests/sprite_specimen.py --out FILE # write
    from sprite_specimen import get_specimen     # import the text
"""
import argparse
import math
import unicodedata as ud

# ---------------------------------------------------------------- box helpers
def frame(title, lines):
    """Draw a ┌─ TITLE ─┐ box; pad every row to one width (alignment guaranteed)."""
    body = [" " + l for l in lines]
    bw = max([len(f" {title} ") + 1] + [len(b) + 1 for b in body])
    out = ["┌" + (f"─ {title} ").ljust(bw, "─") + "┐"]
    out += ["│" + b.ljust(bw) + "│" for b in body]
    out += ["└" + "─" * bw + "┘"]
    return out


def assigned(cp):
    try:
        ud.name(chr(cp))
        return True
    except ValueError:
        return False


def sweep(a, b, cols, sep="", only_assigned=True):
    chars = [chr(cp) for cp in range(a, b + 1) if (assigned(cp) or not only_assigned)]
    return [sep.join(chars[i:i + cols]) for i in range(0, len(chars), cols)]


# ------------------------------------------------------------ braille graphics
_DOT = {(0, 0): 0x01, (0, 1): 0x02, (0, 2): 0x04, (0, 3): 0x40,
        (1, 0): 0x08, (1, 1): 0x10, (1, 2): 0x20, (1, 3): 0x80}


def braille_plot(fn, cells_w, cells_h):
    W, H = cells_w * 2, cells_h * 4
    grid = [[0] * W for _ in range(H)]
    for x in range(W):
        v = max(0.0, min(1.0, fn(x / (W - 1))))
        grid[int(round((1 - v) * (H - 1)))][x] = 1
    rows = []
    for cy in range(0, H, 4):
        line = ""
        for cx in range(0, W, 2):
            bits = 0
            for dx in range(2):
                for dy in range(4):
                    if grid[cy + dy][cx + dx]:
                        bits |= _DOT[(dx, dy)]
            line += chr(0x2800 + bits)
        rows.append(line)
    return rows


# ---------------------------------------------------------------- the specimen
def get_specimen():
    S = []
    def add(block): S.extend(block); S.append("")

    S.append("═" * 74)
    S.append("  BUENA MONO — MONOSPACE TUI SPECIMEN  (column-perfect, in-scope)")
    S.append("═" * 74)
    S.append("")

    add(frame("BOX DRAWING  U+2500-257F  (128, dense — tests join continuity)",
              sweep(0x2500, 0x257F, 32)))

    add(frame("BLOCK ELEMENTS & SHADES  U+2580-259F  (32)",
              sweep(0x2580, 0x259F, 32) +
              ["", "shade ramp:  ░░░░▒▒▒▒▓▓▓▓████   █▓▒░ █▓▒░ █▓▒░",
               "eighths   :  ▁▂▃▄▅▆▇█   ▉▊▋▌▍▎▏",
               "quadrants :  ▘▝▖▗ ▀▄▌▐ ▙▟▛▜  chessboard ▛▀▜▛▀▜ ▌ ▐▌ ▐ ▙▄▟▙▄▟"]))

    add(frame("BRAILLE PATTERNS  U+2800-28FF  (256 — full block)",
              sweep(0x2800, 0x28FF, 32)))

    add(frame("BRAILLE GRAPHICS  (drawille 2x4-dot plots — a TUI differentiator)",
              ["signal  " + braille_plot(lambda t: math.sin(t * 10) * math.exp(-t) * 0.5 + 0.5, 30, 1)[0],
               "sine    " + braille_plot(lambda t: math.sin(t * 12) * 0.45 + 0.5, 30, 1)[0],
               "ramp    " + braille_plot(lambda t: t, 30, 1)[0],
               "pulse   " + braille_plot(lambda t: (math.sin(t * 20) * 0.5 + 0.5) ** 3, 30, 1)[0]]))

    add(frame("ARROWS  U+2190-21FF  (112)", sweep(0x2190, 0x21FF, 32, sep=" ")))

    add(frame("MATH OPERATORS  U+2200-22FF  (256)", sweep(0x2200, 0x22FF, 32, sep=" ")))

    add(frame("POWERLINE  U+E0A0-E0D4  (prompt separators & glyphs)",
              sweep(0xE0A0, 0xE0D4, 32, sep=" ", only_assigned=False)))

    add(frame("MIXED-WEIGHT BOX JOINS  (light / heavy / double must connect)",
              ["┌─────┰━━━━━┓   ╓─────╥─────╖   ┏━━━━━┳━━━━━┓",
               "│  a  ┃  b  ┃   ║  c  ║  d  ║   ┃  e  ┃  f  ┃",
               "├─────╊━━━━━┫   ╠═════╬═════╣   ┣━━━━━╋━━━━━┫",
               "│  g  ┃  h  ┃   ║  i  ║  j  ║   ┃  k  ┃  l  ┃",
               "└─────┺━━━━━┛   ╚═════╩═════╝   ┗━━━━━┻━━━━━┛"]))

    add(frame("SPINNER FRAMES  (braille · moon · block · arrow · bar)",
              ["braille  ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏",
               "moon     ◐ ◓ ◑ ◒        clock  ◴ ◵ ◶ ◷",
               "block    ▘ ▝ ▗ ▖        arrow  ← ↖ ↑ ↗ → ↘ ↓ ↙",
               "bar      ▏ ▎ ▍ ▌ ▋ ▊ ▉ █"]))

    add(frame("TUI COMPOSITE  (progress, gauges, tree)",
              ["build  [████████████████░░░░]  80%   ✓ 142 modules",
               "tests  [██████████████████░░]  90%   ✗ 1 failed",
               "├─ src/",
               "│  ├─ parser.rs      ██████████  100%",
               "│  └─ render.rs      ███████░░░   72%",
               "└─ Cargo.toml        ██████████  100%"]))

    return "\n".join(S).rstrip() + "\n"


def html_page(text):
    import html
    esc = html.escape(text)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Buena Mono — TUI sprite specimen</title>
<style>
@font-face {{ font-family:"Buena Mono";
  src:url("../fonts/variable/BuenaMono-VF.ttf") format("truetype");
  font-weight:100 800; font-style:normal; font-display:block; }}
:root {{ --bg:#000; --fg:#ededed; --bar:#0d0d0d; --br:#262626; }}
body.light {{ --bg:#fff; --fg:#111; --bar:#f4f4f4; --br:#ddd; }}
body {{ background:var(--bg); color:var(--fg); margin:0; font-family:system-ui,sans-serif; }}
.bar {{ position:sticky; top:0; z-index:9; background:var(--bar); border-bottom:1px solid var(--br);
  padding:10px 18px; display:flex; flex-wrap:wrap; gap:18px; align-items:center; font-size:13px; }}
label {{ display:flex; gap:7px; align-items:center; white-space:nowrap; }}
/* line-height:1.0 is REQUIRED for box-drawing vertical continuity; letter-spacing MUST be 0 */
pre#spec {{ font-family:"Buena Mono",ui-monospace,monospace; white-space:pre; line-height:1.0;
  letter-spacing:0; font-size:16px; padding:26px; margin:0; overflow-x:auto;
  font-variation-settings:"wght" var(--wght,400),"slnt" var(--slnt,0);
  font-feature-settings:"calt" var(--calt,1),"liga" var(--liga,1); }}
</style></head><body>
<div class="bar">
  <label>wght <input id="wght" type="range" min="100" max="800" value="400"></label>
  <label>slnt <input id="slnt" type="range" min="-10" max="0" value="0"></label>
  <label>size <input id="size" type="range" min="10" max="28" value="16"></label>
  <label><input id="calt" type="checkbox" checked> ligatures</label>
  <label><input id="lh" type="checkbox" checked> line-height 1.0</label>
  <label><input id="theme" type="checkbox"> light</label>
</div>
<pre id="spec">{esc}</pre>
<script>
const s=document.getElementById('spec'), set=(k,v)=>s.style.setProperty(k,v);
wght.oninput=e=>set('--wght',e.target.value);
slnt.oninput=e=>set('--slnt',e.target.value);
size.oninput=e=>s.style.fontSize=e.target.value+'px';
calt.onchange=e=>{{set('--calt',e.target.checked?1:0);set('--liga',e.target.checked?1:0);}};
lh.onchange=e=>s.style.lineHeight=e.target.checked?'1.0':'1.4';  /* 1.4 = watch box joins break */
theme.onchange=e=>document.body.classList.toggle('light',e.target.checked);
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write the plain-text specimen")
    ap.add_argument("--html", help="write a real-font HTML viewer")
    args = ap.parse_args()
    text = get_specimen()
    if args.html:
        open(args.html, "w", encoding="utf-8").write(html_page(text))
        print(f"HTML viewer written to {args.html}")
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text)
        print(f"specimen written to {args.out}")
    if not (args.out or args.html):
        print(text)


if __name__ == "__main__":
    main()
