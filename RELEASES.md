# Releases

Index of the project's **GitHub Releases**. Each release corresponds to a
published build of the font, with the `buena-mono-<tag>.zip` bundle attached.

For the full narrative history — every version, including the pre-1.218
development milestones and the versions folded into other releases — see
[`CHANGELOG.md`](CHANGELOG.md). For the OFL-required changelog, see
[`FONTLOG.txt`](FONTLOG.txt).

## Published releases

| Tag | Title | Bundle |
|-----|-------|--------|
| 1.232 | Block Elements redrawn onto one cell | — |
| 1.231 | Chess pieces retraced from original art | ✅ |
| 1.228 | Brace recentering, shade alignment, brackets + arrows | ✅ |
| 1.227 | Music BMP, notation symbols, chess quality pass | ✅ |
| 1.226 | Legacy Computing sextants + octants | ✅ |
| 1.225 | Weight-axis fix (ExtraBold rebuilt from Bold) | ✅ |
| 1.224 | 971 languages, source-hygiene overhaul (rolls up 1.221–1.223) | ✅ |
| 1.220 | Lineage-gap set | ✅ |
| 1.219 | Game-symbol set | ✅ |
| 1.218 | Initial public release | ✅ |

`1.231`'s bundle was attached manually, built from the tag's own committed
binaries, because the tag's CI run did not execute — the jobs were never
started, so the `release` job never reached its upload step.

The workflow itself is sound: a clean checkout of the tagged tree builds and
packages correctly with no local state. Once runs execute again, tagging
produces the bundle without intervention; until then, new tags ship without one
and it has to be attached by hand.

The `1.230` release and tag were **deleted** (2026-08-04). They duplicated
`1.231`: both tags resolved to the same object, and no v1.230 binary exists in
either repo — the committed variable font goes 1.229 → 1.231. 1.230 was
superseded by 1.231 within the minute, so there was no genuine artifact to
attach, and publishing a 1.231-stamped font as `buena-mono-1.230.zip` would have
misrepresented it. The glyph work itself shipped in 1.231 and stays documented
in [`CHANGELOG.md`](CHANGELOG.md).

Versions with no standalone release, all documented in
[`CHANGELOG.md`](CHANGELOG.md):

- **1.221 – 1.223** — folded into the 1.224 release.
- **1.229** — a Google Fonts submission re-cut, superseded before it shipped.
- **1.230** — game + music glyph work; superseded by 1.231 the same day. Its
  release and tag were deleted as duplicates (see above); the work ships in 1.231.
- **0.1.0 – 1.217** — pre-public development milestones.

## Bundle layout

```
buena-mono-<tag>/
├── OFL.txt
├── ARTICLE.en_us.html
└── fonts/
    ├── BuenaMono-VF.ttf          two-axis (wght + slnt), direct download
    ├── BuenaMono-VF.otf
    ├── BuenaMono-VF.woff2
    ├── BuenaMono[wght].ttf       Roman, Google Fonts pair
    └── BuenaMono-Italic[wght].ttf   Italic, Google Fonts pair
```

The two-axis `BuenaMono-VF` is the direct-download build. The `[wght]` pair is
the Google Fonts submission form, produced by `scripts/build-gf-pair.py` with
`slnt` pinned to 0 and −10 respectively.

## Cutting a release

1. Build and verify: `make build && make qa`, then `make package` to assemble
   the Google Fonts payload and run fontspector over both faces of the pair.
2. Tag the release commit (no `v` prefix, e.g. `1.232`) and push the tag.
   Pushing a tag triggers [`.github/workflows/build.yaml`](.github/workflows/build.yaml),
   which builds from the tagged commit and uploads `buena-mono-<tag>.zip`.
3. Publish the release with notes describing what changed in the font — glyph
   coverage, features, metrics, and any provenance for imported outlines.

The CI `release` job's auto-generated body is a fallback and is skipped when a
release already exists; write the notes rather than relying on it.
