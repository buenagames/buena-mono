# Changelog

All notable changes to Buena Mono are documented here.

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
