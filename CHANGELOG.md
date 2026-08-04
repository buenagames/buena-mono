# Changelog

All notable changes to Buena Mono are documented here.

## Releases & tags

CHANGELOG.md is the **complete history** — every version, including the pre-repo
milestones reconstructed from the source tables. Git tags mark real commits, and
GitHub Releases are cut for shippable builds; both are necessarily subsets. This
table is the authoritative index of which versions carry a tag and a release.

**Release policy (a):** a GitHub Release is cut for every **public** version
(≥ 1.218), each with its built font artifact. Pre-1.218 entries are development
history and are not released. **Tag convention:** no `v` prefix (e.g. `1.231`),
matching `buenagames/buena-mono`. Four legacy tags predate this convention
(`v0.5.0`, `v1.1`, `v1.217`, `v1.229`) and are left in place to preserve their
release links; their release titles are normalized without the prefix.

| Version | Tag | Release (current) | Policy (a) target |
|---------|-----|-------------------|-------------------|
| 1.231 | `1.231` | — | release + artifact |
| 1.230 | — | — | tag + release + artifact |
| 1.229 | `v1.229` | ✓ (no artifact) | attach artifact |
| 1.228 | — | — | tag + release + artifact |
| 1.227 | — | — | tag + release + artifact |
| 1.226 | — | — | tag + release + artifact |
| 1.225 | — | — | tag + release + artifact |
| 1.224 | — | — | tag + release + artifact |
| 1.223 | — | — | tag + release + artifact |
| 1.222 | — | — | tag + release + artifact |
| 1.221 | — | — | tag + release + artifact |
| 1.220 | — | — | tag + release + artifact |
| 1.219 | — | — | tag + release + artifact |
| 1.218 | — | — | tag + release + artifact — **initial public release** |
| 1.217 | `v1.217` | ✓ | keep — last pre-public tag |
| 1.1.0 | `v1.1` | ✓ | keep — the `v1.1` tag == the 1.1.0 milestone |
| 0.5.0 | `v0.5.0` | ✓ pre-release (no artifact) | **remove** — experimental axis, later dropped |
| 0.1.0 – 1.216 (rest) | — | — | none — reconstructed dev history |

**Open reconciliation actions** (need `gh` / push access — not doable from the
web session's read-only release API):

1. **Backfill releases** for 1.218 and 1.230–1.231, then 1.219–1.228, each with
   its built `buena-mono-<ver>.zip`. Minimum coherent set: 1.218 (first public),
   1.230, and 1.231 (newest).
2. **Attach the missing artifact** to 1.229 — its release is source-only because
   CI currently fails before the build step.
3. **Remove the `v0.5.0` release** (the tag can stay) so an experimental, removed
   axis no longer outranks the initial public release in the Releases list.

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

- Re-cut for the Google Fonts submission — the submission-ready build baking in
  source fixes the shipped 1.228 binary lacked. `ss13` machine-zero:
  `ss13` resolves `zero` → `zero.ss10`, default `0` unchanged. `smcp`/`c2sc`
  ordered before `liga`; `--flatten-components` for nested components.
- fontspector googlefonts on the wght-only GF pair: **0 FATAL / 0 FAIL / 0
  ERROR**. 5,385 glyphs.
  *(Not in the BUENA.md version table; sourced from commit history.)*

## 1.228 — 2026-07

- Braces recentered +39 to co-center with `()[]`; shade blocks
  ░▒▓ (U+2591–2593) affine-refit onto the full-block cell.
- Corner half-brackets ⸢⸣⸤⸥ (U+2E22–2E25), double square brackets ⟦⟧
  (U+27E6–27E7), and black cardinal arrows ➡⬅⬆⬇ (U+27A1, U+2B05–2B07) added
 . 5,385 glyphs.

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

<!-- Pre-1.218 development history (reconstructed from README.md and BUENA.md
     version tables; git tags/commit history for this era predate the current
     repo). Dates are month-precision (Feb 2026); glyph counts are as recorded
     at each release. -->

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
- Glyph count discrepancy across sources: README records 3,199 glyphs / 2,183
  codepoints / 50 features; the source table records 2,501 glyphs — to
  reconcile.

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
