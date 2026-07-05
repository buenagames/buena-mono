# Changelog

All notable changes to Buena Mono are documented here.

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
