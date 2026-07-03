# Buena Mono

Writer-first monospace typeface — tuned for extended prose in markdown and code
editors while keeping code perfectly legible. A two-axis variable font: **weight
100–800** and **slant 0 to −10°**, 8 masters, 4,857 glyphs.

![Buena Mono specimen](docs/specimen.png)

Buena Mono is built on [Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono)
by Wei Huang and extended into a variable family. Released under the
[SIL Open Font License 1.1](OFL.txt).

## Download

Variable fonts live in [`fonts/variable/`](fonts/variable):

| File | Format |
|------|--------|
| `BuenaMono-VF.ttf` | Variable TrueType (`wght`, `slnt`) |
| `BuenaMono-VF.otf` | Variable CFF2 |
| `BuenaMono-VF.woff2` | Variable webfont |

## Features

- **Axes:** weight 100–800, slant 0 to −10°
- **4,857 glyphs:** Latin (incl. Extended A–D), Greek, Cyrillic, IPA, math
  operators, arrows, box-drawing, block/shade elements, currency
- **Code ligatures** — multi-cell and column-alignment preserving
- **12 stylistic sets** — single-story `a`, tailed `l`, dotted/plain zero, and more
- OpenType: `ccmp`, `mark`, `mkmk`, `aalt`, `calt`, `liga`, `smcp`, `ss01`–`ss12`

## Build from source

Requires Python 3.9+.

```sh
make build    # build the variable fonts into out/fonts/
make test     # QA with fontspector
make proof    # HTML proofs with diffenator2
```

Design source: [`sources/BuenaMono.glyphs`](sources/) (Glyphs 3), with UFO
masters and a `.designspace`.

## License

Buena Mono is licensed under the [SIL Open Font License, Version 1.1](OFL.txt).
Portions copyright the [Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono)
Project Authors.

Copyright 2026 The Buena Mono Project Authors · [buenalabs.io](https://buenalabs.io)
