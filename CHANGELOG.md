# Changelog

All notable changes to Buena Mono are documented here.

## Versions, tags and releases

This file is the **complete history** — every version, including the pre-1.218
development milestones. Tags and GitHub Releases cover the public versions only,
so both are necessarily subsets of what follows.

Tags carry no `v` prefix (e.g. `1.231`). Public versions are tagged and released
with their bundle, except where a version was superseded before it shipped; see
[`RELEASES.md`](RELEASES.md) for the release index and bundle layout.

| Version | Tagged | Released | Notes |
|---------|--------|----------|-------|
| 1.233 | — | — | built and QA-clean; not yet tagged or released |
| 1.232 | ✅ | ✅ | |
| 1.231 | ✅ | ✅ | |
| 1.230 | — | — | superseded by 1.231 the same day; release and tag deleted as duplicates |
| 1.229 | — | — | Google Fonts re-cut, superseded before it shipped |
| 1.228 | ✅ | ✅ | |
| 1.227 | ✅ | ✅ | |
| 1.226 | ✅ | ✅ | |
| 1.225 | ✅ | ✅ | |
| 1.224 | ✅ | ✅ | rolls up 1.221–1.223 |
| 1.221 – 1.223 | — | — | folded into the 1.224 release |
| 1.220 | ✅ | ✅ | |
| 1.219 | ✅ | ✅ | |
| 1.218 | ✅ | ✅ | **initial public release** |
| 0.1.0 – 1.217 | — | — | pre-public development history |

## 1.233 — 2026-08-31

Box Drawing redrawn onto one cell. The companion to 1.232's Block
Elements fix, and the same underlying fault — geometric primitives that tile on
a grid had been weight-derived and italic-sheared.

- **Box Drawing** (U+2500–257F) — all 128 glyphs redrawn on the cell the
  vertical metrics define, x `0–618` by y `−250–950`, light and heavy bands
  centred on x=309 / y=350, with only stroke weight varying between masters.
  Slant-invariant: a slanted `┼` does not meet its neighbours in a grid, so
  each italic master takes its upright counterpart's outlines.

  Three faults were stacked here. Every non-Regular master had glyphs
  **displaced inside the cell by up to 134 units** — at Thin all 128 were
  re-centred, so `┤`'s stem sat at x 418..468 instead of straddling 309 and its
  left arm started at 150 rather than 0. The weight offset separately changed
  arm length, so arms fell short at Thin and overhung at ExtraBold. And Regular
  itself — the only master anyone renders — was drawn on **five inconsistent
  grids**: dashes 68/136 against the solid lines' 82/164 and centred 50 units
  low; the double set's arms stopping at x 4..614 so no two ever joined;
  `╸╹╺╻╼╽╾╿` 240 wide on the double grid instead of heavy's 164; and the arcs
  and diagonals still on the `−300..900` block cell that 1.232 retired.

  Two of those shipped visibly at the default weight: `══════` and `╔══╗` seam
  by 8 units at Regular. Rendered at 200px, every one of those runs is now
  continuous, at Thin, Regular and ExtraBold alike.

  The double set keeps its drawn design — its junction topology is carried over
  by coordinate substitution rather than re-derived, so only the arms and the
  per-master rail weight change.
- **`scripts/normalize-box-drawing.py`** parses the arm table out of the Unicode
  character names rather than transcribing it, so the character database is the
  specification. As a check on the construction rule, 72 of the 80 line-set
  glyphs regenerate byte-identical to Regular; the 8 that do not are exactly
  the stubs that were wrong.
- **New `Box cell` QA check** — geometry against the generator at the default
  instance and both ends of the weight axis, plus no variation along `slnt`.
  `make qa` 110 → 119 checks.
- Fixed in `normalize-block-elements.py` en route: `.glyphs` layer order is not
  constant between glyphs, and that script assumed it was. It was harmless
  there only because all eight of its layers were identical.
- No glyph added or removed: **5,406 glyphs**. fontspector's finding set is
  unchanged from 1.232.

## 1.232 — 2026-08-31

Block Elements redrawn onto one cell; embedded copyright completed; the kerning
plan retired.

- **Block Elements** (U+2580–259F) — all 32 glyphs redrawn identically in all
  eight masters, on the cell the vertical metrics already define: x `0–618`,
  y `−250–950`. The range had been through weight derivation and the italic
  shear, which is wrong for glyphs whose job is to tile: the blocks changed size
  with `wght` (`█` gapped 50 units at Thin and overlapped 46 at ExtraBold), `▀`
  and `▄` missed each other by 50 units at the midline, `▐` was drawn in the
  *left* half at every weight but Regular, and the italic masters sheared the
  solid blocks into parallelograms. Filed as an 18-unit seam on `U+2588`; the
  seam was the visible corner of it. Shades keep their hatch, moved onto the new
  cell. Now exact at every point in the design space, and guarded by a new
  `Block cell` check in `make qa` (105 → 110 checks).
- **Copyright** — `name` ID 0 and `metadata.pb` now carry the portions clause,
  naming all six donors with their years and both Reserved Font Names, and
  pointing at `OFL.txt` for the full notices. They previously stopped at the
  Buena line while `OFL.txt` carried the full clause, so the two disagreed in
  the same repository. Condensed to 416 characters: Google Fonts caps `name`
  ID 0 at 500 and the verbatim `OFL.txt` line is 714.
- **Kerning** — confirmed deliberately out of scope. `GPOS` carries `mark` and
  `mkmk` only, as it always has; `BUENA.md` described a `kern` implementation
  that was never built, and that plan has been removed rather than kept.
- No glyph added or removed: **5,406 glyphs**.

## 1.231 — 2026-07-28

- **Chess** — the 12 pieces (U+2654–265F) retraced from the author's
  own flat/modern reference silhouettes (`sources/references/chess/`), replacing
  the v1.230 parametric redraw: cleaner shapes, uniform-scaled to the mono cell,
  black filled (king's cross and knight's eye preserved as counters), white
  outlined at the family weight. The reference art is original to the author and
  licensed under the OFL with the font. 5,406 glyphs (in-place redraw).

## 1.230 — 2026-07-28

Game + music glyph work; source re-cut, GF-clean
(fontspector googlefonts **0 FATAL / 0 FAIL**).

- **Chess** — the 12 pieces (U+2654–265F) redrawn in a flat/modern
  style: bold silhouettes, flared bases, white pieces outlined / black filled.
- **Board-game** — 12 glyphs: go stones ⚪⚫, draughts men/kings
  ⛀⛁⛂⛃, go-board points ⚆⚇⚈⚉, watch ⌚, hourglass ⌛.
- **Music** — 9 glyphs: whole/half/quarter rests (U+1D13B–D) and a
  curated dingbat set — cut time 𝄵, segno 𝄋, coda 𝄌, fermata 𝄐, repeat barlines
  𝄆𝄇 — matching the existing monolinear ♩♪♫♬ + clefs.
- **5,406 glyphs** total (+21 this release). New symbol glyphs are
  weight-invariant across masters, consistent with the existing dingbats/clefs.

## 1.229 — 2026-07-28

- Re-cut for the Google Fonts submission — the submission-ready build baking in
  source fixes the shipped 1.228 binary lacked. `ss13` machine-zero:
  `ss13` resolves `zero` → `zero.ss10`, default `0` unchanged. `smcp`/`c2sc`
  ordered before `liga`; `--flatten-components` for nested components.
- fontspector googlefonts on the wght-only GF pair: **0 FATAL / 0 FAIL / 0
  ERROR**. 5,385 glyphs.

## 1.228 — 2026-07

- Braces recentered +39 to co-center with `()[]`; shade blocks
  ░▒▓ (U+2591–2593) affine-refit onto the full-block cell.
- Corner half-brackets ⸢⸣⸤⸥ (U+2E22–2E25), double square brackets ⟦⟧
  (U+27E6–27E7), and black cardinal arrows ➡⬅⬆⬇ (U+27A1, U+2B05–2B07) added. 5,385 glyphs.

## 1.227 — 2026-07

- Music BMP complete (♩ U+2669, ♬ U+266C); notation symbols — common time 𝄴
  (U+1D134) + treble/bass clefs 𝄞𝄢 (U+1D11E/1D122, adapted from Bravura, OFL).
- White knight/King/Queen chess quality pass. 5,375 glyphs.

## 1.226 — 2026-07

- Legacy Computing block graphics: 60 sextants (U+1FB00–1FB3B) + 230 block
  octants (U+1CD00–1CDE5), drawn on the full-block cell so they tile with
  block/shade and Braille. 5,370 glyphs.

## 1.225 — 2026-07

- ExtraBold masters rebuilt from Bold (were derived from Regular, ~12u light at
  `wght`=800); weight axis now monotonic across 100–800. Anchors re-normalized.
  5,080 glyphs.

## 1.224 — 2026-07

- Mark-anchor normalization (zero collisions at all corners); overlay bars on
  stroked letters restored at Bold/ExtraBold. 5,080 glyphs.

## 1.223 — 2026-07

- `ss13` machine-readable mode (ligatures decompose); Tje/omega small caps.
  5,080 glyphs.

## 1.222 — 2026-07

- 971 languages shaped (shaperglot); batch-2 small caps; new codepoints incl.
  Cyrillic Tje and S with diagonal stroke; winding normalization. 5,078 glyphs.

## 1.221 — 2026-07

- IPA/African small caps; Turkish dotted-i `locl` fix; PS-hinted CFF2
  (otfautohint + blue zones). 5,005 glyphs.

## 1.220 — 2026-07

- Lineage-gap set: CP437 remainder, keyboard/control pictures, multi-line
  bracket pieces, ceiling/floor, prompt ornaments, music accidentals, IPA
  dotted/left-stem tone bars. 4,966 glyphs.

## 1.219 — 2026-07

- Game-symbol set: 12 chess pieces, outlined card suits, dice, stars; 5
  previously unexported dingbats now ship. 4,886 glyphs.

## 1.218 — 2026-07-03

Initial public release.

- Two-axis variable font: **weight** 100–800, **slant** 0 to −10° (8 masters).
- **4,857 glyphs** — Latin (incl. Extended A–D), Greek, Cyrillic, IPA, math
  operators, arrows, box-drawing, block/shade elements, currency.
- **Code ligatures** — multi-cell and column-alignment preserving.
- **12 stylistic sets** (`ss01`–`ss12`).
- OpenType features: `ccmp`, `mark`, `mkmk`, `aalt`, `calt`, `liga`, `smcp`,
  `ss01`–`ss12`.
- Built on [Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono)
  (OFL 1.1) by Wei Huang.

<!-- Pre-1.218 development history. This era predates the current repository, so
     entries are reconstructed from the project's own version tables rather than
     from git history. Dates are month-precision; glyph counts are as recorded at
     the time of each milestone. -->

## 1.217 — 2026-02

- Italic masters added (`slnt` axis 0 to −10°) — the family becomes two-axis.
- `smcp`/`c2sc` identity substitutions for full cased coverage (1,039 + 794
  mappings).
- Interpolation fixes across 477 glyphs; native stylistic-set description
  (`featureNames`) blocks.
- 4,857 glyphs, 3,841 codepoints, 50 features, 8 masters, 16 instances.
  fontspector QA: 0 FAILs / 187 WARNs.

## 1.216 — 2026-02

- 7 new Unicode blocks (+608 glyphs): Phonetic Extensions (128/128), Phonetic
  Extensions Supplement (64/64), Combining Marks Supplement (63/64), Cyrillic
  Extended-A (32/32), Cyrillic Extended-B (96/96), Latin Extended-C (32/32),
  Latin Extended-D (193/199).
- 4,852 glyphs, 3,836 codepoints, 52 features.

## 1.215 — 2026-02

- Source consolidation — the `.glyphs` file becomes the single source of truth
  (44 GSUB features, native GPOS anchors); 26 orphaned UFOs removed (186 MB
  saved). fontmake now auto-generates `mark`/`mkmk` from anchors.
- Coverage expansion to 100% across Latin Extended Additional, General
  Punctuation, Superscripts/Subscripts, Currency, Geometric Shapes, Braille and
  Combining Marks.
- Contemporary records disagree on the glyph count at this milestone: 3,199
  glyphs / 2,183 codepoints / 50 features in one, 2,501 glyphs in another. The
  binaries from this era were not retained, so the figure cannot be settled;
  both are recorded here rather than picking one. Counts from 1.218 onward are
  read directly from the compiled font.

## 1.214 — 2026-02

- Google Fonts readiness — 2,485 glyphs, up to 50 OpenType features. Added
  `salt`, `lnum`, `nalt`, `dtls`, `sups`, `numr`, `dnom`, `sinf`, `tnum`, and
  the `cv01`–`cv13` character variants. fontspector: 0 FAILs.
- Tracked internally as the 1.2.0 milestone (`ccmp`/`mark`/`mkmk` features,
  post-processing pipeline).

## 1.1.2 — 2026-02

- Lowercase alternates from reference fonts; stylistic sets reorganized
  (`ss01`–`ss12`, with `ss11`–`ss20` lowercase alternates). 28 OpenType
  features. 1,698 glyphs.

## 1.1.0 — 2026-02

- Polytonic Greek, Cyrillic Extended and Latin Extended-B — 592 glyphs from
  Noto Sans Mono (`add-greek-ext-b.py`).

## 1.0.0 — 2026-02

- Greek & Coptic alphabet — 73 glyphs from Cascadia Code + JetBrains Mono
  (`add-greek.py`).

## 0.9.0 — 2026-02

- Cyrillic, Latin Extended-A/B and Pinyin — 326 glyphs from IBM Plex Mono.

## 0.8.0 — 2026-02

- Extended symbols: arrows, math operators, icons, super/subscripts, fractions,
  circled numbers, currency; 13 new OpenType features.

## 0.7.0 — 2026-02

- Black weight masters (experimental, later removed).

## 0.6.0 — 2026-02

- Thin + ExtraBold weight masters — weight axis extended to `wght` 100–800.

## 0.5.0 — 2026-02

- Optical size axis exploration (experimental, later removed).

## 0.4.0 — 2026-02

- Slant axis exploration (experimental, later removed).

## 0.3.0 — 2026-02

- Stylistic alternates (`zero`, `ss01`–`ss04`, `onum`); WOFF2 + OTF output.

## 0.2.0 — 2026-02

- Small caps (`smcp`, `c2sc`), discretionary ligatures (`dlig`); Bold master.
  505 glyphs.

## 0.1.5 — 2026-02

- Box Drawing, Block Elements, Powerline glyphs, coding ligatures. 435 glyphs.

## 0.1.0 — 2026-02

- Initial release — built on the Fragment Mono foundation, `wght` 400–700.
  191 glyphs.
