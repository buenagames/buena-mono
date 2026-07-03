---
name: font-build
description: Build, validate, and commit the font from current .glyphs source
argument-hint: "[optional: skip-commit]"
---

# /font-build

Build the font from current source, validate, and commit. No plan mode, no questions.

## Steps

### 1. Pre-flight
- `pwd` — verify we're in buena-mono repo
- `git status` — check for uncommitted changes to source files
- `. venv/bin/activate`

### 2. Source validation
```bash
python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs
```
- If unfixable issues (topology mismatches): report and **STOP** — do not proceed to build
- Do NOT use `--fix` without explicit user request — it modifies the .glyphs source

### 3. Manifest check
```bash
python3 scripts/check-manifest.py
```
- If manifest check fails: source state has regressed — **STOP** and investigate

### 4. Build
After source consolidation (v1.2+), `export-ufo.py` is safe to run if needed — the .glyphs source contains all glyphs, GSUB features, and native GPOS anchors. fontmake auto-generates mark/mkmk from anchors. Use `make export-ufo` to regenerate UFOs.

For normal builds, build directly from existing designspace + UFOs:
```bash
fontmake -m sources/BuenaMono.designspace -o variable --output-dir out/fonts/
```

### 5. Post-processing
```bash
make build-otf        # CFF2 via build-cff2.py wrapper
make inject-stat      # STAT axis values
python3 scripts/add-gasp-table.py
python3 scripts/post-process.py
make build-woff2      # TTF → WOFF2
```

### 6. Built-font validation
```bash
python3 scripts/qa-validate.py --font-dir out/fonts
```
- If failures: report and **STOP** — do not commit broken fonts
- If warnings only: continue and include them in the report

### 7. Report
- Output file sizes for TTF, OTF, WOFF2
- Report glyph count from the built font
- Report any warnings from the build
- Include QA summary (source + built-font pass/fail counts)

### 8. Commit (unless `skip-commit` argument given)
- Stage built font files and any modified source files
- Commit: `build: rebuild fonts`
- Push to origin

## Rules

- After consolidation (v1.2+), `export-ufo.py` is safe — .glyphs has all content + GPOS anchors
- fontmake auto-generates mark/mkmk from native anchors (no add-gpos-marks.py needed)
- Run `make check-manifest` before builds to catch source regressions
- Always use fontmake directly, never gftools builder
- Never skip the CFF2 build (make build-otf) — it uses the required monkey-patch
- If fontmake fails, check for topology/compatibility issues across masters
- If .designspace was unexpectedly modified, restore it before committing
- Source validation runs BEFORE the build to catch issues early
- Built-font validation runs AFTER the build to catch output-level regressions
- Never commit fonts that fail built-font QA validation
