# Releases

Canonical source text for the project's **GitHub Releases**. Each GitHub
Release corresponds to a published build artifact (the `buena-mono-<tag>.zip`
attached by CI). For the complete narrative history — including the pre-1.218
development milestones, the versions bundled into other releases, and the
unreleased re-cut — see [`CHANGELOG.md`](CHANGELOG.md), which is the full
record.

## How releases are cut

Releases are created from the **GitHub Releases UI** (Releases → *Draft a new
release*): create the tag on publish, choose the target commit, and paste the
body from this file. Publishing pushes the tag, which triggers
[`.github/workflows/build.yaml`](.github/workflows/build.yaml) to build the
font from the tagged commit and upload `buena-mono-<tag>.zip` to the release.

> Note: the CI `release` job's auto-generated body is a crude fallback and is
> skipped when a release already exists. Always author the body here / in the
> UI rather than relying on it.

## Published releases

| Tag | Title | Status |
|-----|-------|--------|
| 1.231 | Chess pieces retraced (original art) | ⏳ pending — see below |
| 1.230 | Game + music glyph work | ⏳ pending — see below |
| 1.228 | brace recenter + shade align + brackets/arrows | ✅ published |
| 1.227 | music BMP + notation symbols + chess pass | ✅ published |
| 1.226 | Legacy Computing sextants + octants | ✅ published |
| 1.225 | weight-axis fix (ExtraBold) | ✅ published |
| 1.224 | 971 languages, source-hygiene overhaul (rolls up 1.221–1.224) | ✅ published |
| 1.220 | lineage-gap set | ✅ published |
| 1.219 | game-symbol set | ✅ published |
| 1.218 | initial public release | ✅ published |

Not released as standalone GitHub Releases (documented in `CHANGELOG.md`):
**1.221 / 1.222 / 1.223** (bundled into the 1.224 release), **1.229**
(Google Fonts submission re-cut, superseded by 1.230), and the pre-release
series **0.1.0 – 1.217** (internal development milestones).

---

## Pending release bodies

Paste-ready text for the two releases still to be created in the UI.

### 1.231 — Chess pieces retraced (original art)

- **Tag:** `1.231`
- **Target:** `main` (`01eea85` — 1.231 fonts with OFL donor notices restored)

```markdown
**Chess pieces retraced from original reference art.**

- **Chess (BUENA-347).** The 12 pieces (U+2654–265F) retraced from the author's own flat/modern reference silhouettes (`sources/references/chess/`), replacing the v1.230 parametric redraw: cleaner shapes, uniform-scaled to the mono cell, black filled (king's cross and knight's eye preserved as counters), white outlined at the family weight. Original art by the author, licensed OFL with the font — no third-party outlines bundled.
- **5,406 glyphs** (in-place redraw). fontspector googlefonts: 0 FATAL / 0 FAIL.
```

### 1.230 — Game + music glyph work

- **Tag:** `1.230`
- **Target:** commit `cd550b6` for the true 1.230 outlines. ⚠️ That commit
  predates the OFL-donor-notice restore (`cf1be78`), so the bundle ships with
  incomplete OFL notices. To avoid that, target `main` instead — but then the
  bundle carries the 1.231 outlines (chess already retraced). No commit is both
  "1.230 outlines" and "OFL-complete."

```markdown
Game + music glyph work (BUENA-347/348/349); source re-cut, GF-clean (fontspector googlefonts **0 FATAL / 0 FAIL**).

- **Chess (BUENA-347).** The 12 pieces (U+2654–265F) redrawn in a flat/modern style: bold silhouettes, flared bases, white outlined / black filled.
- **Board-game (BUENA-349).** 12 glyphs: go stones ⚪⚫, draughts men/kings ⛀⛁⛂⛃, go-board points ⚆⚇⚈⚉, watch ⌚, hourglass ⌛.
- **Music (BUENA-348).** 9 glyphs: whole/half/quarter rests (U+1D13B–D) and dingbats — cut time 𝄵, segno 𝄋, coda 𝄌, fermata 𝄐, repeat barlines 𝄆𝄇.
- **5,406 glyphs** (+21).
```
