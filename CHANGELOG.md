# Changelog

All notable changes to Buena Mono are documented here.

## 1.231 — 2026-07-28

- **Chess** — the 12 pieces (U+2654–265F) retraced from the author's
  own flat/modern reference silhouettes (`sources/references/chess/`), replacing
  the v1.230 parametric redraw: cleaner shapes, uniform-scaled to the mono cell,
  black filled (king's cross and knight's eye preserved as counters), white
  outlined at the family weight. The reference art is original to the author and
  licensed under the OFL with the font. 5,406 glyphs (in-place redraw).

## 1.230 — 2026-07-28

Game + music glyph work; source re-cut, GF-clean
(fontspector googlefonts **0 FATAL / 0 FAIL** on `BuenaMono[slnt,wght].ttf`).

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

Re-cut for the Google Fonts submission — the submission-ready build baking in
source fixes the shipped 1.228 binary lacked. `ss13` machine-zero:
`ss13` resolves `zero` → `zero.ss10`, default `0` unchanged. `smcp`/`c2sc`
ordered before `liga`; `--flatten-components` for nested components.
fontspector googlefonts on the wght-only GF pair: **0 FATAL / 0 FAIL / 0
ERROR**. 5,385 glyphs. Not published as a standalone release on this
repository — superseded by the 1.230 re-cut.

## 1.228 — 2026-07-22

Brace recentering, shade-cell alignment, and quick-win brackets + arrows.

- **Braces recentered.** `{` `}` sat ~39u low; shifted up +39 in all
  masters so they co-center with `()[]` on the cap midpoint (~350).
- **Shade blocks aligned.** `░▒▓` (U+2591–2593) lived on a different
  cell than `█`; affine-refit each master's stipple onto the full-block cell
  (x 9–609, y −300..900) so they tile with the block/sextant/octant set.
- **Corner half-brackets + double brackets + heavy arrows.** Added
  `⸢⸣⸤⸥` (U+2E22–2E25) and `⟦⟧` (U+27E6–27E7), derived per-master from the real
  bracket geometry so they track weight, plus the black cardinal arrows
  `➡⬅⬆⬇` (U+27A1, U+2B05–2B07) drawn on the cell.
- 5,375 → 5,385 glyphs / 4,254 → 4,264 codepoints.

## 1.227 — 2026-07-18

Music glyphs, curated notation symbols, and chess refinements.

- **Music BMP complete (7/7).** Added the quarter note `♩` (U+2669) and beamed
  sixteenths `♬` (U+266C), derived from the existing `♪`/`♫`.
- **Curated notation symbols.** Common time `𝄴` (U+1D134, from the `C`), plus
  treble `𝄞` (U+1D11E) and bass `𝄢` (U+1D122) clefs adapted from Bravura
  (Steinberg Media Technologies, OFL 1.1) — credited in FONTLOG and OFL.
- **Chess quality pass.** Rebuilt the white knight `♘` as a clean outline of the
  black knight `♞`, and rebalanced the white King/Queen stroke weight.
- 5,370 → 5,375 glyphs.

## 1.226 — 2026-07-18

Legacy Computing block graphics.

- **290 sextant + block-octant glyphs added.** The full Symbols for Legacy
  Computing sextant range (`U+1FB00`–`1FB3B`, 60) and the Symbols for Legacy
  Computing Supplement block octants (`U+1CD00`–`1CDE5`, 230). Each is drawn
  as solid sub-cell rectangles on Buena's exact full-block cell (x 9–609,
  split at 309; y −300..900), so they tile seamlessly with the existing
  `█ ▌ ▐` block set and the Braille layer for high-resolution terminal
  graphics. Geometry is identical across all 8 masters (block graphics are
  weight-invariant) and every glyph sits on the 618 monospace cell.
- **5,370 glyphs / 4,249 codepoints** (was 5,080 / 3,959). 971 languages
  (unchanged — the additions are symbol graphics, not new orthographies).

## 1.225 — 2026-07-16

Weight-axis fix.

- **ExtraBold rebuilt from Bold, not Regular.** The ExtraBold masters
  (wght=800) had been derived from the Regular master by mistake, leaving
  them ~12 units lighter than Bold — so text got *lighter* from wght 700 to
  800, in every release since v1.218. The masters are now re-derived from
  Bold with the same offset used for every other weight; stems run monotonic
  across the whole 100–800 axis (H stem 118 → 144 at the top). Anchors
  re-normalized to the new letter heights. 5,080 glyphs (unchanged).

## 1.224 — 2026-07-08

Mark positioning + overlay-bar repair.

- **Zero mark collisions** at every designspace corner (was 18 stress-string
  failures): anchor heights now track each master's measured flat letter
  tops (heavy masters reach past the nominal metrics), anchors lift above
  baked accents/descender tails for correct stacking, and combining marks
  carry 20u built-in clearance. Soft-dotted ḭ decomposes before above-marks.
- **Stroke-overlay bars restored at heavy weights**: the bars on
  Ɇ ɇ Ɍ ɍ Ᵽ ᵽ Ⱡ ⱡ Ⱥ ⱥ Ꭓ ꭓ shrank as weight grew (a relic of the
  pre-normalization winding: the weight offset contracted reversed
  contours — down to 2u at ExtraBold). Rebuilt to the Ø-slash growth
  convention; Thin keeps its authored bars.

## 1.223 — 2026-07-08

_Published on GitHub as part of the [1.224 release](https://github.com/buenagames/buena-mono/releases/tag/1.224) bundle (which rolls up 1.221–1.224)._

- **ss13 “Machine readable”**: decomposes all 164 ligatures back to their
  components for OCR/verbatim contexts (`font-feature-settings: "ss13" 1`).
- Small caps for ᲊ (Tje) and ꭥ — clears the remaining fontspector
  small-cap FAILs (back to the single intentional filename check).
- fontspector WARNs 1,072 → 347 after the winding normalization.
- **5,080 glyphs / 51 OpenType features.**

## 1.222 — 2026-07-08

_Published on GitHub as part of the [1.224 release](https://github.com/buenagames/buena-mono/releases/tag/1.224) bundle (which rolls up 1.221–1.224)._

Language-coverage completion + source hygiene (round 2).

- **971 languages shaped correctly** (shaperglot; was 835 in 1.221, 480 in
  1.220) — every nearly-supported language closed except Yi and Korean.
- **61 new small caps** (accented ǹ ḿ ṍ ḍ … and all stragglers ẓ ʃ ƭ ⱳ ɐ ẋ
  ȓ ƹ ƈ ƥ ẉ ḫ ɫ ɤ ɉ), caseless ƛ ʕ ʘ, ẖ composite.
- **New codepoints**: Ᲊ ᲊ (U+1C89/1C8A, Khanty Tje), Ꟍ ꟍ (U+A7CC/A7CD,
  Luiseño), ꜛ ꜜ tone letters, ꭥ, Ꟛ ꟛ (Latin lambda) — 19 Google Fonts
  glyphsets now at 100%.
- **Winding normalization**: 21,228 contours across 1,534 glyphs aligned to
  a single convention; restores filled counters on Ꙭ Ꚙ Ꝏ and fixes overlay
  artifacts. Interpolation start points aligned (problems 655 → 256).
- **5,078 glyphs / 3,959 codepoints** (was 5,005 / 3,950).

## 1.221 — 2026-07-07

_Published on GitHub as part of the [1.224 release](https://github.com/buenagames/buena-mono/releases/tag/1.224) bundle (which rolls up 1.221–1.224)._

Small caps for IPA/African Latin; PostScript-hinted CFF2.

- **835 languages shaped correctly** (was 480): 38 scaled small caps for
  IPA/African letters (ɔ ɛ ɓ ɗ ɨ ɩ ɲ ʋ ʉ ꞌ ƴ ɣ ɖ ƙ ʊ ʒ …) with smcp/c2sc
  rules; Turkish dotted-i locl fix (i no longer renders as dotless ı in
  Turkish text; dotted small-cap İ under smcp; fi ligature suppressed).
- Winding fixed on the 38 source capitals (Ⱥ Ɇ Ɍ Ᵽ Ⱡ Ꭓ … no longer render
  with XOR artifacts).
- The variable CFF2 OTF now ships **PostScript-hinted** (otfautohint +
  cffsubr at build time; alignment zones + standard stems seeded per master).
- **5,005 glyphs / 3,950 codepoints** (was 4,966 / 3,950).

## 1.220 — 2026-07-05

Lineage-gap expansion: 80 glyphs closing every consensus coverage gap vs the
18 obtainable monospace families from the lineage analysis.

- **CP437 / terminal completeness**: ☺ ☻ ☹ ♀ ♂ ♪ ♫ ⌐ ⌠ ⌡ — the full classic
  terminal graphics set now renders.
- **Keyboard & editor symbols**: ⏎ ␣ ⌫ ⌦ ⌧ ⌃ ⌄ ⎋ and control pictures
  ␀ ␉ ␊ ␋ ␌ ␍ ␤ (drawn as scaled letter components — they track weight).
- **Math**: ceiling/floor ⌈ ⌉ ⌊ ⌋, projective ⌅, APL ⍴, and all 19
  multi-line bracket pieces U+239B–23AD (tall parens/brackets/braces
  assemble seamlessly across lines, matched to the box-drawing line box).
- **Prompt & misc**: ❮ ❯ ❰ ❱, ✕, music accidentals ♯ ♭ ♮, half-black
  diamonds ⬖ ⬗ ⬘ ⬙, dotted square ⬚, inverted interrobang ⸘.
- **IPA**: dotted and left-stem tone bars U+A708–A716 (15), completing the
  tone-letter set.
- U+FEFF zero-width no-break space.
- **4,966 glyphs / 3,950 codepoints** (was 4,886 / 3,870).

## 1.219 — 2026-07-05

Game-symbol expansion.

- **Chess pieces** (U+2654–265F): all 12, white outlined + black filled,
  designed on the mono cell — FEN diagrams and text boards render natively.
- **Outlined card suits** ♡♢♤♧ (U+2661/2662/2664/2667), derived from the
  filled suits for an exact style match.
- **Dice** ⚀–⚅ (U+2680–2685) and **stars** ★☆ (U+2605/2606).
- Five previously unexported dingbats now ship: ✢ ✳ ✶ ✻ ✽.
- **4,886 glyphs / 3,870 codepoints** (was 4,857 / 3,841).

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

## Pre-release history (0.1.0 – 1.217)

Development milestones from the internal repo, before the public 1.218
release. These were design/build iterations and were **not published as
GitHub releases**; some axes explored here (slant, optical size, Black
weight) were experimental and later removed or reworked. Recorded for
lineage completeness.

| Version | Date | Glyphs | Codepoints | Features | Detail |
|---------|------|--------|------------|----------|--------|
| 0.1.0 | Feb 2026 | 191 | — | — | Initial build — Fragment Mono foundation, `wght` 400–700. |
| 0.1.5 | Feb 2026 | 435 | — | — | Box Drawing, Block Elements, Powerline, coding ligatures. |
| 0.2.0 | Feb 2026 | 505 | — | — | Small caps (`smcp`, `c2sc`), discretionary ligatures (`dlig`); Bold master. |
| 0.3.0 | Feb 2026 | — | — | — | Stylistic alternates (`zero`, `ss01`–`ss04`, `onum`); WOFF2 + OTF output. |
| 0.4.0 | Feb 2026 | — | — | — | Slant axis exploration (experimental, later removed). |
| 0.5.0 | Feb 2026 | — | — | — | Optical size axis exploration (experimental, later removed). |
| 0.6.0 | Feb 2026 | — | — | — | Thin + ExtraBold masters — weight axis extended to `wght` 100–800. |
| 0.7.0 | Feb 2026 | — | — | — | Black weight masters (experimental, later removed). |
| 0.8.0 | Feb 2026 | — | — | +13 | Extended symbols: arrows, math operators, icons, super/subscripts, fractions, circled numbers, currency. |
| 0.9.0 | Feb 2026 | +326 | — | — | Cyrillic, Latin Extended-A/B and Pinyin — glyphs from IBM Plex Mono. |
| 1.0.0 | Feb 2026 | +73 | — | — | Greek & Coptic alphabet — glyphs from Cascadia Code + JetBrains Mono. |
| 1.1.0 | Feb 2026 | +592 | — | — | Polytonic Greek, Cyrillic Extended, Latin Extended-B — glyphs from Noto Sans Mono. |
| 1.1.2 | Feb 2026 | 1,698 | — | 28 | Lowercase alternates; stylistic sets reorganized (`ss01`–`ss12`, `ss11`–`ss20` lowercase alternates). |
| 1.214 | Feb 2026 | 2,485 | — | ≤50 | Google Fonts readiness (internal 1.2.0 milestone): added `salt`, `lnum`, `nalt`, `dtls`, `sups`, `numr`, `dnom`, `sinf`, `tnum`, `cv01`–`cv13`. fontspector 0 FAILs. |
| 1.215 | Feb 2026 | 2,501 | — | 44 GSUB | `.glyphs` becomes the single source of truth (native GPOS anchors); 26 orphaned UFOs removed (186 MB); 100% coverage across Latin Ext. Additional, General Punctuation, Super/Subscripts, Currency, Geometric Shapes, Braille, Combining Marks. A pre-consolidation README recorded 3,199 glyphs / 2,183 codepoints — a historical counting discrepancy, superseded once counts were tracked from the single source. |
| 1.216 | Feb 2026 | 4,852 | 3,836 | 52 | 7 new Unicode blocks (+608): Phonetic Ext (128/128), Phonetic Ext Supp (64/64), Combining Marks Supp (63/64), Cyrillic Ext-A (32/32), Cyrillic Ext-B (96/96), Latin Ext-C (32/32), Latin Ext-D (193/199). |
| 1.217 | Feb 2026 | 4,857 | 3,841 | 50 | Italic masters (`slnt` 0 to −10°) — two-axis; `smcp`/`c2sc` identity subs (1,039 + 794); interpolation fixes across 477 glyphs; native `featureNames`. 8 masters / 16 instances; fontspector 0 FAILs / 187 WARNs. |

Versioning note: the jump from the `0.x`/`1.1.x` scheme to `1.214`+ reflects
a switch to `1.<versionMinor>` numbering (the `versionMinor` counter carried
over from the internal build sequence), which is why the public series begins
at 1.218 rather than 1.2.
