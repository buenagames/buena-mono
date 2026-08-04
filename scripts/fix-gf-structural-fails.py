#!/usr/bin/env python3
"""Fix the two *structural* fontspector FAILs on the GF pair.

Triage of the v1.228 wght-only pair found 12 FAILs; 10 are packaging-pipeline
artifacts that clear in a full `make build` (gasp, usWinDescent, instance PS
names — set by inject-stat / add-gasp-table / post-process). The two real ones:

  1. nested_components — handled by fontmake `--flatten-components` (added to the
     Makefile build; NOT this script).
  2. feature-ordering — GF requires small-caps (`smcp`, `c2sc`) lookups before
     `liga` lookups; in source `liga` is defined first. This script moves the
     smcp + c2sc feature blocks ahead of liga in BOTH the canonical
     sources/BuenaMono.glyphs (so `make export-ufo`/the re-cut stay correct) and
     the 8 UFO features.fea (what `make build` compiles today).

    python3 scripts/fix-gf-structural-fails.py
"""
import glob
import os
import re
import sys

import glyphsLib

DEV = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GLYPHS = os.path.join(DEV, "sources", "BuenaMono.glyphs")
SMALLCAPS = ["c2sc", "smcp"]  # insert in this order, both before liga


def fix_glyphs():
    font = glyphsLib.GSFont(GLYPHS)
    feats = font.features
    tags = [f.name for f in feats]
    if "liga" not in tags:
        print("  .glyphs: no liga feature — skip"); return
    moved = []
    for tag in SMALLCAPS:
        if tag not in tags:
            continue
        cur = [f.name for f in feats]
        i = cur.index(tag)
        liga = cur.index("liga")
        if i < liga:
            continue
        feats.insert(cur.index("liga"), feats.pop(i))
        moved.append(tag)
    if moved:
        font.save(GLYPHS)
        print("  .glyphs: moved %s before liga; saved" % ", ".join(moved))
    else:
        print("  .glyphs: small-caps already before liga")


def _move_block_before(text, tag, anchor="liga"):
    """Move `feature <tag> {...} <tag>;` to immediately before `feature <anchor> {`."""
    blk = re.search(r"(?ms)^feature %s \{.*?^\} %s;\n?" % (tag, tag), text)
    anc = re.search(r"(?m)^feature %s \{" % anchor, text)
    if not blk or not anc:
        return text, False
    if blk.start() < anc.start():
        return text, False  # already before
    block = blk.group(0)
    text = text[:blk.start()] + text[blk.end():]          # remove block
    anc = re.search(r"(?m)^feature %s \{" % anchor, text)  # re-find after removal
    text = text[:anc.start()] + block + text[anc.start():]  # insert before anchor
    return text, True


def fix_ufo_fea():
    feas = sorted(glob.glob(os.path.join(DEV, "sources/BuenaMono-*.ufo/features.fea")))
    for fea in feas:
        t = open(fea).read()
        changed = []
        for tag in SMALLCAPS:  # smcp last so it ends up first (each inserted just before liga)
            t, ok = _move_block_before(t, tag)
            if ok:
                changed.append(tag)
        if changed:
            open(fea, "w").write(t)
        print("  %-40s %s" % (os.path.basename(os.path.dirname(fea)),
                              "moved " + ",".join(changed) if changed else "ok"))


def main():
    if not os.path.exists(GLYPHS):
        sys.exit("no .glyphs at %s" % GLYPHS)
    print("feature-ordering fix (small-caps before liga):")
    fix_glyphs()
    fix_ufo_fea()


if __name__ == "__main__":
    main()
