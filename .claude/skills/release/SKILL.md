---
name: release
description: Build, validate, tag, and release a new version of Buena Mono
argument-hint: "[version]"
disable-model-invocation: true
allowed-tools: Read, Edit, Bash(git:*), Bash(gh:*), Bash(make:*), Bash(python3:*), Bash(fontmake:*), Bash(. venv/bin/activate:*)
---

# /release

Build, validate, tag, and release a new version of Buena Mono.

Takes an optional version argument (e.g., `/release 1.2.0`). If no version given, bump the patch version from current.

## Steps

### 1. Pre-flight
- `git status` — ensure working tree is clean (commit or stash first)
- Read current version from `sources/BuenaMono.glyphs` or last git tag

### 2. Build
```bash
. venv/bin/activate
python3 scripts/export-ufo.py
fontmake -m sources/BuenaMono.designspace -o variable --output-dir out/fonts/
make build-otf
make inject-stat
python3 scripts/add-gasp-table.py
python3 scripts/post-process.py
make build-woff2
```

### 3. Validate
```bash
python3 scripts/qa-validate.py --font-dir out/fonts
```
If QA fails, report errors and stop. Don't release broken fonts.

### 4. Version bump
- Update version strings in source metadata files
- Commit: `bump: version X.Y.Z`

### 5. Commit built fonts
- Stage and commit built font files: `build: rebuild fonts for vX.Y.Z`
- Push to origin

### 6. Tag and release
```bash
git tag -a vX.Y.Z -m "Buena Mono vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z out/fonts/BuenaMono-VF.ttf out/fonts/BuenaMono-VF.woff2 out/fonts/BuenaMono-VF.otf --title "Buena Mono vX.Y.Z" --generate-notes
```

### 7. Update Linear
- Update BUENA-152 with release notes
- Close any completed sub-issues

## Rules

- Never release if QA validation fails
- Always build fresh — don't release stale font files
- Tag format: `vX.Y.Z` (semver with v prefix)
