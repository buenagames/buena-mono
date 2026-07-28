#!/usr/bin/env python3
"""benchmark_gaps.py — competitive glyph-coverage gap finder.

Compares Buena Mono's cmap against a directory of benchmark/competitor fonts and
surfaces:
  * OPPORTUNITIES — in-scope codepoints that N+ peers ship but Buena lacks,
  * a TERMINAL-GRAPHICS matrix (box / blocks / Braille / sextants / octants),
  * STRENGTHS — in-scope glyphs Buena has that few peers do.

Uses only the cmap, so any weight/instance of each font works. Benchmark fonts
are NOT committed (licensing + size) — point --fonts-dir at your own directory
of competitor .ttf/.otf binaries.

    python3 tests/benchmark_gaps.py --fonts-dir /path/to/ttfs
    python3 tests/benchmark_gaps.py --fonts-dir DIR --min-peers 3 \\
        --buena fonts/variable/BuenaMono-VF.ttf
"""
import argparse
import glob
import os
from collections import Counter, defaultdict

from fontTools.ttLib import TTFont
from fontTools import unicodedata as fud

# Scripts a coding/writer monospace deliberately leaves to system fallback.
OUT_OF_SCOPE = (
    "CJK", "Hangul", "Hiragana", "Katakana", "Bopomofo", "Yi ", "Kana", "Emoji",
    "Lisu", "Tai ", "Miao", "Vai", "Cherokee", "Ethiopic", "Tibetan", "Myanmar",
    "Khmer", "Hebrew", "Arabic", "Devanagari", "Bengali", "Thai", "Lao",
    "Georgian", "Armenian", "Syriac", "Thaana", "Mongolian", "Cham", "Balinese",
    "Sundanese", "Javanese", "Braille",  # Braille excluded — already complete
)

# Terminal-graphics blocks (Buena's positioning) — always shown as a matrix.
TG_BLOCKS = {
    "Box Drawing": (0x2500, 0x257F),
    "Block Elements": (0x2580, 0x259F),
    "Braille Patterns": (0x2800, 0x28FF),
    "Legacy Computing (sextants)": (0x1FB00, 0x1FBFF),
    "Legacy Computing Suppl (octants)": (0x1CC00, 0x1CEBF),
}


def load(path):
    try:
        return set(TTFont(path, fontNumber=0, lazy=True).getBestCmap())
    except Exception:
        return None


def inscope(cp):
    if cp < 0x21:
        return False
    try:
        blk = fud.block(chr(cp))
    except Exception:
        return False
    return not any(s in blk for s in OUT_OF_SCOPE)


def main():
    ap = argparse.ArgumentParser(description="Competitive glyph-coverage gap finder")
    ap.add_argument("--buena", default="fonts/variable/BuenaMono-VF.ttf")
    ap.add_argument("--fonts-dir", required=True,
                    help="dir of benchmark .ttf/.otf binaries — ONE representative per "
                         "family (each file counts as a peer, so weight/NF variants skew --min-peers)")
    ap.add_argument("--min-peers", type=int, default=3, help="opportunity threshold (default 3)")
    args = ap.parse_args()

    buena = load(args.buena)
    if buena is None:
        raise SystemExit(f"cannot read Buena at {args.buena}")
    bench = {}
    for p in sorted(glob.glob(f"{args.fonts_dir}/**/*.ttf", recursive=True)
                    + glob.glob(f"{args.fonts_dir}/**/*.otf", recursive=True)):
        s = load(p)
        if s:
            bench[os.path.splitext(os.path.basename(p))[0]] = s
    if not bench:
        raise SystemExit(f"no readable fonts in {args.fonts_dir}")

    print(f"Buena {len(buena)} codepoints  vs  {len(bench)} benchmark fonts")
    print("  " + "  ".join(f"{n}:{len(s)}" for n, s in bench.items()) + "\n")

    names = list(bench)
    print("TERMINAL-GRAPHICS COVERAGE")
    print(f"  {'block':36}{'Buena':>7}" + "".join(f"{n[:8]:>9}" for n in names))
    for bn, (a, b) in TG_BLOCKS.items():
        rng = range(a, b + 1)
        row = f"  {bn:36}{sum(cp in buena for cp in rng):>7}"
        row += "".join(f"{sum(cp in bench[n] for cp in rng):>9}" for n in names)
        print(row)

    allpeers = set().union(*bench.values())
    byblock = defaultdict(list)
    for cp in allpeers:
        if cp in buena or not inscope(cp):
            continue
        k = sum(cp in s for s in bench.values())
        if k >= args.min_peers:
            byblock[fud.block(chr(cp))].append((cp, k))
    total = sum(len(v) for v in byblock.values())
    print(f"\nOPPORTUNITIES — in-scope, >={args.min_peers} peers have, Buena lacks ({total})")
    for blk in sorted(byblock, key=lambda x: -len(byblock[x])):
        rows = sorted(byblock[blk], key=lambda x: -x[1])[:12]
        samp = " ".join(f"{chr(cp)}·U+{cp:04X}({k})" for cp, k in rows)
        print(f"  {blk:36} {len(byblock[blk]):3}  {samp}")

    print("\nPER-FONT — in-scope codepoints Buena lacks (breadth of each peer)")
    for n, s in sorted(bench.items(), key=lambda kv: -sum(c not in buena and inscope(c) for c in kv[1])):
        print(f"  {n:14} {sum(c not in buena and inscope(c) for c in s):5}")

    uniq = [cp for cp in buena if inscope(cp) and sum(cp in s for s in bench.values()) <= 2]
    ub = Counter(fud.block(chr(cp)) for cp in uniq)
    print(f"\nBUENA STRENGTHS — in-scope glyphs <=2 peers have ({len(uniq)})")
    for blk, n in ub.most_common(10):
        print(f"  {blk:36} {n}")


if __name__ == "__main__":
    main()
