# Marketing / brand assets

Generated brand + marketing materials for Buena Mono. Kept **here in the dev
repo** (not the public `buenagames/buena-mono` font repo) so the public repo
stays focused on the font.

- **`marketing_svg.py` → `svg/`** — 21 editable-Buena-Mono SVG templates for
  Figma import: core images (hero, cli, specimen, stylistic-sets, character-sets,
  social-preview), social posts, Reels/Shorts, YouTube, ASO, and brand guidelines
  (logo exclusion zone, stats board, type system). Pure Python; SVG `<text>` +
  `font-family="Buena Mono"` imports as editable text in Figma Desktop.
- **`marketing.py` → `png/`** — 11 flat PNG marketing assets rendered from the
  real variable font via `drawbot_skia`.

Regenerate everything: **`make marketing`** from the dev repo root (needs the
built font at `fonts/variable/BuenaMono-VF.ttf`; installs `drawbot-skia` on
first run).

Design system: black canvas, the Show Syntax code palette + parts-of-speech
(iA Writer) palette, caret `#00c4ff`, reusable code-window motif. Note: the
public repo keeps its own README/specimen PNGs (`docs/*.png` via `docs/*.py` +
`scripts/make-specimens.py`) — those are documentation images, separate from
this marketing kit.
