# Sprite / TUI rendering tests

Font-aware monospace + terminal-UI checks and specimens for Buena Mono.

## Files

- **`sprite_coverage.py`** — the actual *test* (pass/fail). Verifies the
  TUI-critical blocks are **100% complete** (Box Drawing 128, Block Elements 32,
  Braille 256), that **every covered glyph sits on the 618 cell** (monospace
  integrity), and that each has a real outline. Reports coverage of the broader
  symbol blocks (arrows, math, geometric, dingbats, Powerline). Exits non-zero on
  failure. Hooked into **`make qa`**; run alone with **`make sprite-test`**.
  Buena-locked to 618 by default; **`--any-cell`** turns it into a general
  monospace linter that derives the cell from the font's own ASCII advance
  (e.g. lints Cascadia at its 1200 cell, JetBrains at 600) — completeness gaps
  like a missing Braille block still fail.
- **`sprite_specimen.py`** — data-driven, **column-perfect** specimen generator.
  Systematic block sweeps + generated Braille (drawille) graphics + curated TUI
  demos, **in-scope only** (no weather/zodiac/religious/astral/Nerd-PUA decor
  that would tofu). Every frame is width-computed, so any misalignment on render
  is the *font's* fault, not the specimen's. `--out FILE` (text),
  `--html FILE` (real-font viewer with wght/slnt/size/ligature/line-height/theme
  toggles; line-height defaults to 1.0 so box-drawing connects).
- **`sprite_render.py`** — renders the specimen to a PNG with the real font at
  line-height 1.0; a diffable regression artifact (render on two versions,
  compare).
- **`sprite-specimen.{txt,html,png}`** — generated baselines.
  **`make sprite-specimen`** rebuilds all three.
- **`benchmark_gaps.py`** — competitive glyph-coverage gap finder. Compares
  Buena's cmap against a `--fonts-dir` of competitor binaries (one per family)
  and reports *opportunities* (in-scope codepoints N+ peers ship that Buena
  lacks), a terminal-graphics matrix (box/blocks/Braille/sextants/octants), and
  Buena's *strengths*. Benchmark fonts aren't committed (licensing/size) — supply
  your own dir. Found the Legacy-Computing sextant/octant gap and 9 quick-win
glyphs.

## Supersedes

Removed 2026-07-18: `Monospace Typeface Sprite Rendering Test - Complete Glyph
Specimen.js` — a hand-typed visual specimen whose `analyzeCharacters()` only
*counted characters in the string* and never touched the font (so it couldn't
tell that 213 of its 797 codepoints — weather, zodiac, astral musical/arrows,
Nerd-Font PUA — are not in Buena and would render as tofu). Its `displayInHTML()`
also set `line-height: 1.2`, which breaks vertical box-drawing continuity. This
Python suite replaces it — adding a real pass/fail verdict, 618-cell integrity,
guaranteed column alignment, and in-scope curation.
