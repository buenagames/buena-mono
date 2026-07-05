# Buena Mono

<!-- QA badges — uncomment when the repo is public and the DEPLOY_PAGES
     repository variable is set to "true" (Settings > Pages must be on
     "GitHub Actions"). The JSON endpoints are published by CI to Pages.

[![][Fontspector]](https://buenagames.github.io/buena-mono/fontspector/fontspector-report.html)
[![][OpenType]](https://buenagames.github.io/buena-mono/fontspector/fontspector-report.html)
[![][Universal]](https://buenagames.github.io/buena-mono/fontspector/fontspector-report.html)
[![][Google Fonts]](https://buenagames.github.io/buena-mono/fontspector/fontspector-report.html)
[![][Glyphset]](https://buenagames.github.io/buena-mono/fontspector/fontspector-report.html)

[Fontspector]: https://img.shields.io/endpoint?url=https%3A%2F%2Fbuenagames.github.io%2Fbuena-mono%2Fbadges%2FFontspectorQA.json
[OpenType]: https://img.shields.io/endpoint?url=https%3A%2F%2Fbuenagames.github.io%2Fbuena-mono%2Fbadges%2FOpentypeSpecificationChecks.json
[Universal]: https://img.shields.io/endpoint?url=https%3A%2F%2Fbuenagames.github.io%2Fbuena-mono%2Fbadges%2FUniversalProfileChecks.json
[Google Fonts]: https://img.shields.io/endpoint?url=https%3A%2F%2Fbuenagames.github.io%2Fbuena-mono%2Fbadges%2FFontFileChecks.json
[Glyphset]: https://img.shields.io/endpoint?url=https%3A%2F%2Fbuenagames.github.io%2Fbuena-mono%2Fbadges%2FGlyphsetChecks.json
-->

Writer-first monospace typeface — tuned for extended prose in markdown and code
editors while keeping code perfectly legible. A two-axis variable font: **weight
100–800** and **slant 0 to −10°**, 8 masters, 4,857 glyphs.

![Buena Mono](docs/image1.png)

Buena Mono is built on [Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono)
by Wei Huang and extended into a variable family. Released under the
[SIL Open Font License 1.1](OFL.txt).

## Install

Grab the fonts from [`fonts/variable/`](fonts/variable) — `BuenaMono-VF.ttf`
(variable TrueType), `.otf` (variable CFF2), `.woff2` (webfont):

- **macOS** — open `BuenaMono-VF.ttf` and click *Install Font* (or drop it into Font Book).
- **Windows** — right-click `BuenaMono-VF.ttf` → *Install*.
- **Linux** — copy to `~/.local/share/fonts/` and run `fc-cache -f`.

**Web** — self-host the variable webfont:

```css
@font-face {
  font-family: "Buena Mono";
  src: url("BuenaMono-VF.woff2") format("woff2");
  font-weight: 100 800;
}
/* slant is on the `slnt` axis (0 to -10): */
.slanted { font-variation-settings: "slnt" -10; }
```

## Features

- **Axes:** weight 100–800, slant 0 to −10°
- **4,857 glyphs:** Latin (incl. Extended A–D), Greek, Cyrillic, IPA, math
  operators, arrows, box-drawing, block/shade elements, currency
- **Code ligatures** — multi-cell and column-alignment preserving
- **12 stylistic sets** — single-story `a`, tailed `l`, dotted/plain zero, and more
- OpenType: `ccmp`, `mark`, `mkmk`, `aalt`, `calt`, `liga`, `smcp`, `ss01`–`ss12`

## Specimen

Weight from hairline thin to solid extrabold, code ligatures, and multi-script
coverage:

![Buena Mono specimen](docs/specimen.png)

## Stylistic sets

Twelve stylistic sets (`ss01`–`ss12`) provide alternate letterforms:

![Buena Mono stylistic sets](docs/stylistic-sets.png)

Enable one with `font-feature-settings: "ss01" 1;` (CSS) or your editor's
OpenType settings.

## Character set

![Buena Mono character set](docs/image2.png)

![Buena Mono Italic character set](docs/image3.png)

## In use

<table>
<tr><th align="left">Regular</th><th align="left">Regular · dark</th></tr>
<tr>
<td width="50%"><img src="docs/use-regular-light.png" alt="Buena Mono Regular, light"></td>
<td width="50%"><img src="docs/use-regular-dark.png" alt="Buena Mono Regular, dark"></td>
</tr>
<tr><th align="left">Regular + Bold</th><th align="left">Regular + Bold · dark</th></tr>
<tr>
<td><img src="docs/use-bold-light.png" alt="Buena Mono Regular and Bold, light"></td>
<td><img src="docs/use-bold-dark.png" alt="Buena Mono Regular and Bold, dark"></td>
</tr>
<tr><th align="left">Regular + Italic</th><th align="left">Regular + Italic · dark</th></tr>
<tr>
<td><img src="docs/use-italic-light.png" alt="Buena Mono Regular and Italic, light"></td>
<td><img src="docs/use-italic-dark.png" alt="Buena Mono Regular and Italic, dark"></td>
</tr>
</table>

## Enabling ligatures in your editor

Buena Mono's code ligatures use `calt`/`liga`, which are on by default in most
engines. Where they aren't:

- **VS Code** — `"editor.fontFamily": "Buena Mono"`, `"editor.fontLigatures": true`
- **JetBrains IDEs** — Settings → Editor → Font → *Buena Mono*, check *Enable ligatures*
- **Sublime Text** — set `"font_face": "Buena Mono"`; ligatures are on unless `no_calt` is listed in `"font_options"`
- **Neovim/Vim** — use a GUI (Neovide, MacVim) with `guifont=Buena\ Mono`
- **Terminals** — iTerm2: *Use ligatures* in the profile; Kitty: on by default

## Build from source

Requires Python 3.9+.

```sh
make build    # build the variable fonts into out/fonts/
make test     # QA with fontspector
make proof    # HTML proofs with diffenator2
```

Design source: [`sources/BuenaMono.glyphs`](sources/) (Glyphs 3), with UFO
masters and a `.designspace`. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[CHANGELOG](CHANGELOG.md).

## Bonus — Claude Code spinner verbs

Buena Mono is a writer-first dev font, so it ships a matching spinner.
[`extras/spinner-verbs.json`](extras/spinner-verbs.json) is a 200-verb set for
[Claude Code](https://claude.com/claude-code)'s thinking spinner. Merge it into your
`~/.claude/settings.json` (or a project `.claude/settings.json`):

```jsonc
{
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": ["Krahing", "Hill-climbing", "Naming the wind", "Kwisatz-haderaching", "…and 196 more"]
  }
}
```

Grab the full set from [`extras/spinner-verbs.json`](extras/spinner-verbs.json), or
watch them cycle on the [specimen](https://buena-mono.buenalabs.io/#spinner).

## Credits

Made by [Buena](https://buenalabs.io). Built on
[Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono) by Wei Huang
(SIL OFL 1.1), itself based on Nimbus Sans.

Specimen images are licensed [CC BY-SA 4.0](docs/images-license.txt).

## License

Buena Mono is licensed under the [SIL Open Font License, Version 1.1](OFL.txt).
Portions copyright the [Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono)
Project Authors.

Copyright 2026 The Buena Mono Project Authors · [buenalabs.io](https://buenalabs.io)
