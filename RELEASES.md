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
| 1.231 | Chess pieces retraced from original art | — |
| 1.230 | Game + music glyph work | — |
| 1.228 | Brace recentering, shade alignment, brackets + arrows | ✅ |
| 1.227 | Music BMP, notation symbols, chess quality pass | ✅ |
| 1.226 | Legacy Computing sextants + octants | ✅ |
| 1.225 | Weight-axis fix (ExtraBold rebuilt from Bold) | ✅ |
| 1.224 | 971 languages, source-hygiene overhaul (rolls up 1.221–1.223) | ✅ |
| 1.220 | Lineage-gap set | ✅ |
| 1.219 | Game-symbol set | ✅ |
| 1.218 | Initial public release | ✅ |

Releases 1.230 and 1.231 are published but have no bundle attached — they were
created ahead of a CI run that could produce one. Attaching those two artifacts
is the only outstanding gap in this table.

Versions with no standalone release, all documented in
[`CHANGELOG.md`](CHANGELOG.md):

- **1.221 – 1.223** — folded into the 1.224 release.
- **1.229** — a Google Fonts submission re-cut, superseded by 1.230 before it
  shipped.
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
