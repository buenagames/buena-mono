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
| 1.239 | — | — | built and QA-clean; not yet tagged or released |
| 1.238 | ✅ | ✅ | |
| 1.237 | ✅ | ✅ | |
| 1.236 | ✅ | ✅ | |
| 1.235 | ✅ | ✅ | |
| 1.234 | ✅ | ✅ | |
| 1.233 | ✅ | ✅ | |
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

## 1.239 — 2026-09-28

: the mark, arrow and cell-width problems found while finishing, fixed in three parallel parts.

- **Italic accents**: `scripts/add-italic-masters.py` sheared every glyph by tan 10° and then re-centred each one in its cell on its own. A mark drawn high should move right with the slant, but its own re-centring pulled it back, while letters built from components kept their upright offsets and the italic anchors were sheared but never re-centred. In 1.238, 426 of 433 letters built from parts set their mark more than 10 units off in italic (median 69, up to 157: `ẁ ẃ ẅ ẇ ḧ` among them), and GPOS put the acute on `a` + U+0301 125 units left. Every italic offset and anchor (2,849 glyphs) is now derived from the upright, sheared, plus each glyph's own re-centring (`scripts/fix-accented-letters.py`).
- **Clearance**: every above-mark's `_top` anchor sat 41–46 units above the x-height, and the marks grew with the weight while keeping their place, so all 225 measured mark tiers lost their clearance at Bold and ExtraBold: `á` went 53 → 0 units of white from Regular to ExtraBold. Marks now keep Regular's clearance at every weight, and anchors sit on the x-height or baseline and move with the ink. GPOS gaps for `a` + U+0301 are 47/48/49/47 at Thin/Regular/Bold/ExtraBold. 89 letters from Latin Extended Additional had marks at offset 0,0, sitting inside capitals and ascenders; they are re-attached.
- **Letters on stale bases**: of 661 precomposed letters drawn as full outlines, 253 were on a different base drawing, 144 on an out-of-date version of their base, and 40 shifted 2–19 units. 518 are rebuilt as the base glyph plus their own accent contours. The cedilla U+0327 had collapsed into a blob at Bold/ExtraBold and is redrawn; `Ç ç Ş ş` use it, and the comma-below letters `Ģ Ķ Ļ Ņ Ŗ Ș Ț` use U+0326. U+032A is redrawn like U+033A/U+0346 (whose ⊓ orientation was checked against Helvetica and Noto Serif), and `ͣ ͫ` are rebuilt from `a`/`m`.
- **Arrows**: `scripts/fix-arrow-family.py` rebuilds 69 arrows from `→`'s own strokes, on one axis: `↔ ⇐ ⇒ ⇔` had sat on y 166 and `⇑ ⇓ ↕` on 266, against `→`'s 349. `⇦ ⇩` no longer overrun the cell (−31..649, −94..750 at Regular), `⇤ ⇥` no longer come apart from Bold, and the crude `⇷ ⇸ ⇺ ⇻ ⇽ ⇾ ⇪–⇮ ⇳` are redrawn. The long arrows `⟵–⟾` fit one cell. The ligatures `=> ==> =>> |=> <=> |->` are rebuilt from `=` and `->` without the self-overlapping joins (107–173 units) they had at heavy weights.
- **Cell overrun**: a new QA check fails any encoded glyph whose ink leaves the cell by more than 20 units at Regular or 52 at ExtraBold. It failed 1.238 on 150 glyph/weight pairs. `⑽–⒇` and `⒑–⒛` keep full-size parentheses with condensed digits (Regular 29..589, was −84..702); `℃ ℉ ℔ ⅏ ⅒ ↉ U+FFFC U+FFFD ☼ ∬ ∭ ∯ ∰ ₠ ₢` are fitted, the suits centred, `⋘ ⋙` redrawn as three chevrons, and 20 symbols whose parts had drifted apart (`∴ ∵ ∷ ≔ ≕ ⋯ ‑ ― ‗`, the bars of `₤ ₧ ₭ ₳` …) re-derived. The remaining offenders (217 codepoints: the Greek capitals, script capitals, Powerline separators, solid triangles …) are exempt in commented groups, and the list may only shrink. Rebuilt letters keep their marks inside the cell (`ĥ`'s circumflex, `Ą`'s ogonek at heavy weights).
- **Redrawn**: `꟒ ꟓ` (double thorn) had self-crossing counters that rendered filled and now have open bowls; `Ỿ ỿ` have a real loop; `ꚁ Ꜯ` no longer cross their counters; `ℑ` follows the weight; `ª µ & ‽ Ꜳ Œ` no longer carry reversed handles; `ⷤ ⷼ` are rebuilt from `ж ꙗ` like their siblings; the maths `∉ ∾ ≀ ≎ ≏ ≒ ≓ ⋎ ⋏` take their proper forms (`≒ ≓` are `=` with two dots, `⋎ ⋏` two flaring arms); `⊘` is `⊗`'s ring and one bar, and the two weight scripts that rewrote it on every run leave it alone.

Still open: the design calls in (circled-ring weight, the Ỿ loop form, `Ꜳ` at heavy weights, the interrobang, `∼`, the parenthesis weight of `⑴–⒇`) and the 130 accented letters left for a design pass (Greek capitals with side marks, the horn letters, `Ţ ţ`).

5,406 glyphs, unchanged.

## 1.238 — 2026-09-26

The rest of the design pass, and a font-wide repair of the curves in the heavier masters.

- **Curve handles**: Thin, Bold and ExtraBold are derived from Regular by offsetting its outline, which moved each curve's on-curve points but left the handles at Regular's length and direction. Where points moved closer together the handles overran them: they pointed backwards, crossed, or overshot their segment, which shows as hooks where the bowls of `n d q g` meet the stem and as kinks in bowls at Bold and ExtraBold. `scripts/fix-curve-handles.py` audits every cubic segment in the six derived masters against Regular's and rebuilds the flagged ones from Regular's handle directions, scaled to the segment, keeping every on-curve point and rejecting any rebuild that bulges further than Regular or adds a fault. 2,626 glyph-masters changed; the defects in the heavy masters fell by 80–95%. A new source check, `validate_source_handles`, fails on reversed handles and would have caught 1,415 of them in 1.237.
- **Symbols**: `⇧ ⇯ ↴ ↵ ↹ ⇹ ⇼ ⇿` are rebuilt from `→`'s own strokes, with shafts and heads at `→`'s weight in every master. `◍` is `○`'s ring with its stripes clipped to the inside. `ⓜ` is built like `ⓝ`. `.notdef` is a hollow box, framed at the stem weight of `l`.
- **Circled glyphs fit their cell**: `①`–`⑩`, `Ⓐ`–`Ⓩ`, `⓪`, `⓿` and `❶`–`❿` spanned about −131..748 units in a 618-unit cell at Regular, covering the characters beside them. Their rings now match `ⓐ`–`ⓩ` and `⑪`–`⑳` exactly, with the digits and capitals scaled to fit inside.
- **Letters rebuilt from their parts**: `ǧ ǩ ǰ ȟ` are the letter plus the caron; `ǣ ǽ Ǣ Ǽ` are `æ`/`Æ` plus the mark, so they share `æ`'s aperture fix; 18 accented `a`s that were drawn on an older `a` (`ǟ ǡ ǻ ȁ ȃ ȧ ạ ả ấ ầ ẩ ẫ ậ ắ ằ ẳ ẵ ặ`) are `a` plus their marks, so they share its smoothed ExtraBold curves; `ΐ ΰ` are `ϊ ϋ` plus the tonos, which no longer fuses with the dots at heavy weights.
- **Marks**: U+033A and U+0346 are redrawn as single outlines; they had been opposite-wound overlaps.
- **QA**: the Weight progression check has no exemptions left; every glyph must gain ink from Thin to ExtraBold.

Found and filed for a later pass: italic composites placing their mark about 85 units left (`ẁ ẃ ẅ ẇ ḧ`), marks touching letters at ExtraBold, letters on older base outlines (`Ǟ Ǡ Ȁ Ȃ Ȧ`, the Vietnamese `e`s), a set of glyphs needing redraws, arrow defects, and 535 glyphs still wider than their cell.

5,406 glyphs, unchanged.

## 1.237 — 2026-09-26

The design pass on what 1.236's weight fix could only partly correct, plus a
set of heavy-weight glyph defects.

- **Weight progression, completed**: the contours could only
  mirror at 75/50/25% now get their full offset, clamped point by point to
  the room around them, and glyphs whose weights were never offsets at all
  are re-derived from Regular (or from Thin, where Regular had lost the
  design). `∘` went from 20,478 / 55,263 / 142,488 / 159,898 units² at
  Thin / Regular / Bold / ExtraBold to 34,432 / 55,263 / 79,884 / 94,682.
  QA exemptions go from 14 to 3 (◍, U+033A, U+0346, each with a reason).
- **Rebuilt**: `⇖ ⇗ ⇘ ⇙` from each master's own `⇐`/`⇒` turned 45°. They
  had almost no ink, upright as well as italic. The circled and framed
  operators `⊕`–`⊡`, `⊲`–`⊵` and `▭ ▯ ◽ ▱` are redrawn from Thin, since
  Bold and ExtraBold had filled their counters into discs. `⓫`–`⓳` had
  rendered as solid black discs because their digits were wound the same
  way as the disc; the digits are knocked out again.
- **Circled glyphs**: the Regular master of 48 of them (`①`–`⑩`, `Ⓐ`–`Ⓩ`,
  `⓪`, `⓿`, `❶`–`❿`) was drawn 308 units left of the other masters, so at
  Regular they sat on the previous character. The same applied to marks
  U+0483–0489 and U+0337. All are back on the cell.
- **Dieresis**: at ExtraBold the dots merged into a bar, so `ü` read as `ū`.
  Both the square dots of `äëïöüÿ ÄËÏÖÜŸ ϊ ϋ Ϊ Ϋ` and the round U+0308 dots
  used by 36 more glyphs now keep Regular's gap at Bold and ExtraBold.
- **Letters**: the Bold and ExtraBold `a` had kinked and reversed curve
  handles; they are rebuilt from Regular's, along with the accented `a`s.
  The e-half of `æ` and `œ` no longer closes up at Bold and above. `.notdef`
  follows the font's own weight offsets.

Still open for a redraw or a design decision: `⇧ ⇯` and a few
crude arrows, `ΐ ΰ`, `ǣ ǽ`, some accented `a`s built on a different
outline, and a set of glyphs whose offset stops short because their
outlines overlap.

5,406 glyphs, unchanged.

## 1.236 — 2026-09-26

Punctuation, accents and symbols gain weight along the weight axis, the way
the letters always did. Plus the heavy-weight redraws of.

- **Weight progression**: **1,126 glyphs were heavier at Thin than at
  Bold**, among them `| ~ ! : ; ? \ { }`, quotes, dashes, arrows, currency,
  367 small caps, 27 ligatures (`<|`, `~~`, `~>`, …) and nearly all combining
  marks, so the accents on accented letters too. In 1.235 `|` measured
  94,860 / 62,860 / 27,520 / 51,388 units² of ink at Thin / Regular / Bold /
  ExtraBold: every colon, pipe and exclamation mark in bold text was drawn at
  about Thin weight. Thin and Bold are derived from Regular by offsetting its
  outline (−16 and +19 units), which depends on the direction the contours
  run. A source rewrite (319a6f9c2) had reversed these glyphs' contours, so
  both offsets ran backwards; the later winding normalisation hid the cause
  and kept the geometry, and ExtraBold, rebuilt as Bold + 13,
  inherited it. `scripts/fix-weight-inversion.py` mirrors each affected
  contour's Thin and Bold offsets through Regular and moves ExtraBold with
  Bold, checking every result for overlaps, escaped counters and ligature ink
  leaving its cells. Regular is unchanged. `|` is now 32,908 / 62,860 /
  101,088 / 128,908.
- **Box Drawing**: `normalize-box-drawing.py` mistook the single line in
  the 18 mixed single/double glyphs (`╒ ╓ ╕ …`) for a double rail; the single
  stroke now uses the light line's edges at every weight.
- **Heavy-weight redraws**: `<|||` is the mirror of `|||>` and
  `~=` is `~` and `=` in their cells. Both had drawn outside their advance.
  `ẁ ẃ ẅ` are `w` plus the mark, like `ẇ ẉ ẘ`, instead of narrower separate
  outlines. `ⱳ` is condensed at Bold/ExtraBold into its cell (−18/−33 → 2).
  The `e` aperture, which closed to an 11-unit slit at ExtraBold, is opened
  to Regular's proportion (gap 37→68 at Bold, 11→63 at ExtraBold), along with
  the accented `e`s.
- **QA**: new **Weight progression** check. Every glyph with ink must not
  get lighter from Thin to ExtraBold, upright and italic, with a documented
  list of exemptions. It fails on 1.235 with 1,186 glyphs. `make qa` goes
  from 132 to 134 checks.

184 glyphs could only be partly corrected without their outlines colliding;
they now progress the right way but not as far as the letters. They, the 55
whose contours don't move as one offset, and the exemptions are listed for a
design pass.

5,406 glyphs, unchanged.

## 1.235 — 2026-09-25

Every glyph keeps its advance in every master, and the ligatures draw on
their own cells. Fixes both halves of
[buenagames/buena-mono#3](https://github.com/buenagames/buena-mono/issues/3)
(BUENALB-26).

- **Advances**: a monospace glyph's advance must not change along
  either axis. The four italic masters gave **all 164 ligatures a one-cell
  advance**, and Bold did the same to 54 of them. In italic, `a...b` took
  three cells instead of five, and every ligature, down to prose `ffi`,
  pulled the rest of the line left off the grid. At Bold 700 `f_f`
  advanced 618 instead of 1236, so "cliffhanger" drew over itself (#3). The
  italic masters also gave the **25 zero-width format characters** (ZWSP,
  ZWJ, ZWNJ, the bidi controls, the word joiner) a full cell, so they
  rendered as spaces. `scripts/fix-ligature-centring.py` now gives every
  glyph the Regular master's advance in all eight masters.
- **Ligature ink**: where ligatures did have their n x 618 advance,
  `fix-ligature-widths.py` had widened them without moving the outlines.
  Those were drawn centred on a single cell, so the ink stayed on the first
  of n cells: 300 units left for two cells, 600 for three, 900 for four. In
  Regular **134 ligatures drew into the character before them**. `...`, the
  case that was reported, started 253 units (3.54pt at 14pt) before its own
  origin. Each such ligature now moves right by (n − 1) × 309, in each master
  where it needs it; Thin was already drawn this way. `~=` and `<|||` are
  drawn wrong rather than placed wrong, and are left for.
- **`w`**: drawn wider than its peers at every weight (sidebearings
  42/22/−1/−17 from Thin to ExtraBold, against `m`'s 55/39/20/7). At Bold its
  ink met both cell edges and at ExtraBold it ran 17 units into each
  neighbour, so `wr` closed up (#3). It is now condensed about its centre at
  Bold and ExtraBold, and their italics, to sidebearings of 12 and 6, with
  `ŵ` alongside. Thin and Regular are unchanged.
- **QA**: three new checks, all failing on 1.234. **Ligature ink** tests the
  default and the four wght/slnt corners, **Advance invariance** the eight
  master locations, and **Lowercase cell** upright a–z at four weights.
  `make qa` goes from 125 to 132 checks.

5,406 glyphs, unchanged.

## 1.234 — 2026-09-25

Fixes the ss04 round-dot alternates (BUENALB-27, reported in
[buenagames/buena-mono#1](https://github.com/buenagames/buena-mono/issues/1))
and the missing STAT value for the italic slant.

- **`j.ss04` / `i.ss04`**: ss04 should change the shape of the dot on
  `i` and `j` and nothing else. Both alternates had drifted from that in every
  master. `j.ss04`'s dot sat **116 units left of the stem**, centred over the
  top bar. `i.ss04`'s was 10 units left. At Bold and ExtraBold both still
  carried the **Regular body**, so with ss04 on, `i` and `j` were visibly
  lighter than the text around them. The italic `j.ss04` body was also 20 units
  right of `j`'s, and neither alternate had anchors.
  `scripts/fix-ss04-dots.py` now rebuilds each alternate from its base glyph
  in every master (body, anchors and width) and centres the existing round dot
  where the square dot is.
- **STAT**: adds a slnt −10 value named "Oblique". All eight italic named
  instances declared slnt −10 in fvar with no matching STAT value, so a picker
  reading STAT could not name them (fontbakery
  `inconsistencies_between_fvar_STAT`). It is not called "Italic" because the
  universal `STAT_strings` check reserves that word for the `ital` axis. The
  Google Fonts pair is unaffected, since it gets its own `wght` + `ital` STAT.
- **QA**: a new ss04 check tests body identity and dot centring at the default
  and at the four wght/slnt corners. The STAT check now fails on any fvar
  instance coordinate that has no STAT value. `make qa` goes from 119 to 125
  checks.
- **npm**: `package.json` and `index.css`, first published to npm as 1.233.0
  from the public repo, now live in the canonical repo. The version follows the
  font: 1.234.0.

5,406 glyphs, unchanged.

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
