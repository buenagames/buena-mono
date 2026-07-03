#!/usr/bin/env bash
# Verify interpolation compatibility after a normalization pass (Path A).
# Gates: interpolatable count must DROP toward 0; CFF2/OTF build (the strict
# point-type oracle) must succeed; built-font QA must stay 105/105.
#
# Usage:  . venv/bin/activate && bash scripts/verify-interpolation.sh
set -uo pipefail
cd "$(dirname "$0")/.."

echo "== 1. interpolatable (incompatible glyph count) =="
# The checker SILENTLY under-reports ~100x without the munkres/scipy solver.
python3 -c "import munkres" 2>/dev/null || { echo "  installing munkres (required for accurate count)"; pip install -q munkres; }
python3 -m fontTools.varLib.interpolatable sources/BuenaMono.designspace \
  > /tmp/interp_check.txt 2>&1
N=$(grep -c 'was not compatible' /tmp/interp_check.txt)
echo "incompatible glyphs: $N   (full-checker baseline on G3 source: 332)"

echo "== 2. variable TTF build =="
fontmake -m sources/BuenaMono.designspace -o variable --output-dir out/fonts/ \
  >/tmp/fm.log 2>&1 && echo "  TTF build OK" || { echo "  TTF build FAILED"; tail -5 /tmp/fm.log; }

echo "== 3. CFF2/OTF build (strict point-type oracle) =="
make build-otf >/tmp/otf.log 2>&1 && echo "  CFF2 build OK" \
  || { echo "  CFF2 build FAILED — point-type mismatch remains:"; grep -iE "point type|differing" /tmp/otf.log | head; }

echo "== 4. built-font QA (expect 105/105, 0 fail) =="
python3 scripts/qa-validate.py --font-dir out/fonts | tail -3

echo
echo "Done. If N dropped and CFF2 built + QA passed: commit. Else: git restore sources/"
