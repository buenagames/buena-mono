# Changelog

All notable changes to Buena Mono are documented here.

## 1.223 — 2026-07-08

- **ss13 “Machine readable”**: decomposes all 164 ligatures back to their
  components for OCR/verbatim contexts (`font-feature-settings: "ss13" 1`).
- Small caps for ᲊ (Tje) and ꭥ — clears the remaining fontspector
  small-cap FAILs (back to the single intentional filename check).
- fontspector WARNs 1,072 → 347 after the winding normalization.
- **5,080 glyphs / 51 OpenType features.**

## 1.222 — 2026-07-08

Language-coverage completion + source hygiene (BUENA-335 round 2).

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
