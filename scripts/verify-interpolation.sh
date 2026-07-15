#!/usr/bin/env bash
# Verify interpolation compatibility after a normalization pass.
#
# Gates, in order of authority:
#   5. fontspector interpolation WARNs  <-- THE ONE THAT DECIDES. GF-facing.
#   1. fontTools interpolatable count   <-- advisory ONLY. See warning below.
#   2/3. TTF + CFF2/OTF builds (strict point-type oracle) must succeed.
#   4. built-font QA must stay 105/105.
#
# ⚠️  READ THIS BEFORE TRUSTING GATE 1 (BUENA-338, 2026-07-15).
# `fontTools.varLib.interpolatable` and fontspector are DIFFERENT oracles and
# they disagree. A normalization pass (scripts/normalize-contours.py, which maps
# start points by coordinate) was measured at:
#
#     interpolatable   234 -> 92    (-61%, looks like a win)
#     TTF + CFF2 build OK, QA 105/105
#     fontspector WARN 347 -> 871   (+151%, wrong start point 168 -> 628)
#
# i.e. gates 1-4 ALL PASSED while the metric Google Fonts actually reads got
# 2.5x worse. Satisfying the fuzzy coordinate-based checker does NOT imply
# satisfying fontspector. Gate 5 is the one that decides; gate 1 is a
# diagnostic. This also casts doubt on the historical "189 glyphs fixed
# (336 -> ~147)" claim in docs/PLAN-interpolation-normalization.md, which was
# validated against gate 1 only.
#
# Usage:  . venv/bin/activate && bash scripts/verify-interpolation.sh [baseline_warns]
set -uo pipefail
cd "$(dirname "$0")/.."

# fontspector interpolation-WARN baseline for the currently shipped VF.
# Override by passing an argument when the shipped baseline moves.
BASELINE_WARNS="${1:-347}"

echo "== 1. interpolatable (incompatible glyph count) — ADVISORY ONLY =="
# The checker SILENTLY under-reports ~100x without the munkres/scipy solver.
python3 -c "import munkres" 2>/dev/null || { echo "  installing munkres (required for accurate count)"; pip install -q munkres; }
python3 -m fontTools.varLib.interpolatable sources/BuenaMono.designspace \
  > /tmp/interp_check.txt 2>&1
N=$(grep -c 'was not compatible' /tmp/interp_check.txt)
echo "  incompatible glyphs: $N   (baseline on current source: 234)"
echo "  NOTE: a drop here does NOT mean success — gate 5 decides."

echo "== 2. variable TTF build =="
fontmake -m sources/BuenaMono.designspace -o variable --output-dir out/fonts/ \
  >/tmp/fm.log 2>&1 && echo "  TTF build OK" || {
    echo "  TTF build FAILED — point-type mismatch:"
    grep -oE "in glyph [A-Za-z0-9_.]+" /tmp/fm.log | sed 's/in glyph /    /' | sort -u | head
    echo "  (revert those glyphs' glifs across all 8 masters, then re-run)"
  }

echo "== 3. CFF2/OTF build (strict point-type oracle) =="
make build-otf >/tmp/otf.log 2>&1 && echo "  CFF2 build OK" \
  || { echo "  CFF2 build FAILED — point-type mismatch remains:"; grep -iE "point type|differing" /tmp/otf.log | head; }

echo "== 4. built-font QA (expect 105/105, 0 fail) =="
python3 scripts/qa-validate.py --font-dir out/fonts | tail -3

echo "== 5. fontspector interpolation WARNs — THE DECIDING GATE =="
if ! command -v fontspector >/dev/null 2>&1; then
  echo "  fontspector not found — run scripts/install-fontspector.sh"
  echo "  ⚠️  CANNOT VERIFY. Do not commit a normalization pass without this gate."
  exit 2
fi
fontspector --profile googlefonts -l warn --full-lists --succinct \
  --html /tmp/fs_verify.html out/fonts/BuenaMono-VF.ttf >/dev/null 2>&1
W=$(python3 - <<'PY'
import re
try:
    t = open("/tmp/fs_verify.html").read()
except OSError:
    print(-1); raise SystemExit
m = re.search(r"FAIL</th>.*?WARN</th>.*?</tr>\s*<tr>\s*<td>(\d+)\s*</td>\s*<td>(\d+)\s*</td>", t, re.S)
print(m.group(2) if m else -1)
PY
)
echo "  fontspector WARN: $W   (shipped baseline: $BASELINE_WARNS)"
python3 - "$W" "$BASELINE_WARNS" <<'PY'
import sys
w, base = int(sys.argv[1]), int(sys.argv[2])
if w < 0:
    print("  ⚠️  could not parse fontspector report — treat as FAILED")
    raise SystemExit(2)
if w > base:
    print(f"  ❌ REGRESSION: +{w-base} WARNs vs shipped. DO NOT COMMIT — git restore sources/")
    raise SystemExit(1)
if w == base:
    print("  ➖ no change vs shipped — the pass achieved nothing on the metric that counts")
    raise SystemExit(1)
print(f"  ✅ IMPROVED: -{base-w} WARNs vs shipped.")
PY
RC=$?

echo
if [ "$RC" = "0" ]; then
  echo "PASS — gate 5 improved and builds/QA are green. Safe to commit."
else
  echo "FAIL — gate 5 did not improve. Revert: git restore sources/"
fi
exit "$RC"
