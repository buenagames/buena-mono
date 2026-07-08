#!/usr/bin/env python3
"""
Build CFF2/OTF variable font with charstring normalization.

The standard fontmake CFF2 build fails because the CFF charstring compiler
produces structurally incompatible charstrings across masters:

  1. Width encoding: the default master omits nominalWidthX/defaultWidthX
     from its Private dict, so its charstrings lack width values, while all
     region masters include them → different program lengths.

  2. Specializer divergence: the charstring specializer makes different
     optimization choices per master (e.g., collapsing collinear curves
     to lines, merging rlineto sequences) when coordinates differ due to
     weight/slant/opsz variation → different operator sequences.

  3. Zero-length segments: rounding artifacts produce "rlineto 0 0" in
     some masters but not others → extra operators.

The CFF2CharStringMergePen requires exact structural identity across all
masters (same operator types in the same order). Any divergence causes an
IndexError during the merge step.

Fix: monkey-patch merge_charstrings to normalize all compiled charstrings
before merging. For each glyph across all masters:
  - Generalize all charstrings (undo specializer → canonical rmoveto/rlineto/rrcurveto)
  - Strip width encoding and endchar
  - Align operator sequences: remove zero-length rlineto segments so all
    masters match the shortest (canonical) program length

Usage:
    python3 scripts/build-cff2.py
"""

import sys
import os

# ---------------------------------------------------------------------------
# Monkey-patch: normalize charstrings before CFF2 merge
# ---------------------------------------------------------------------------

import fontTools.varLib.cff as cff_mod
from fontTools.cffLib.specializer import generalizeProgram

_orig_merge = cff_mod.merge_charstrings


def _strip_program(program):
    """
    Generalize and strip width/endchar from a CFF charstring program.
    Returns the cleaned program.
    """
    if not program:
        return []

    # Step 1: Generalize the program (undo specializer decisions)
    try:
        program = generalizeProgram(program)
    except Exception:
        pass

    # Step 2: Strip endchar
    if program and program[-1] == 'endchar':
        program = program[:-1]

    if not program:
        return []

    # Step 3: Strip width value if present
    first_op_idx = next((i for i, t in enumerate(program) if isinstance(t, str)), None)
    if first_op_idx is not None and first_op_idx > 0:
        op = program[first_op_idx]
        if op == 'rmoveto' and first_op_idx == 3:
            program = program[1:]
        elif op == 'hmoveto' and first_op_idx == 2:
            program = program[1:]
        elif op == 'vmoveto' and first_op_idx == 2:
            program = program[1:]
        elif op == 'endchar' and first_op_idx == 1:
            program = program[1:]

    return program


def _split_into_ops(program):
    """
    Split a generalized program into a list of (args, operator) tuples.
    """
    ops = []
    args = []
    for token in program:
        if isinstance(token, str):
            ops.append((args, token))
            args = []
        else:
            args.append(token)
    return ops


def _ops_to_program(ops):
    """
    Convert a list of (args, operator) tuples back to a flat program.
    """
    program = []
    for args, op in ops:
        program.extend(args)
        program.append(op)
    return program


def _align_glyph_programs(programs):
    """
    Align charstring programs across all masters for a single glyph.

    For masters that have extra zero-length rlineto segments, remove them
    to match the shortest program's operator count.
    """
    if not programs or all(not p for p in programs):
        return programs

    all_ops = [_split_into_ops(p) if p else [] for p in programs]

    lengths = [len(ops) for ops in all_ops if ops]
    if len(set(lengths)) <= 1:
        return programs

    min_len = min(lengths) if lengths else 0

    aligned_ops = []
    for ops in all_ops:
        if not ops:
            aligned_ops.append([])
            continue
        if len(ops) == min_len:
            aligned_ops.append(ops)
            continue

        excess = len(ops) - min_len
        filtered = []
        removed = 0
        for args, op in ops:
            if (removed < excess and op == 'rlineto'
                    and len(args) == 2 and args[0] == 0 and args[1] == 0):
                removed += 1
                continue
            filtered.append((args, op))

        aligned_ops.append(filtered if len(filtered) == min_len else ops)

    return [_ops_to_program(ops) for ops in aligned_ops]


def _patched_merge(glyphOrder, num_masters, top_dicts, masterModel):
    """
    Normalize all master charstrings before calling the original merge.
    """
    normalized = 0
    aligned = 0
    errors = 0

    # Phase 1: Strip width/endchar and generalize each charstring
    for td in top_dicts:
        for gname in glyphOrder:
            if gname not in td.CharStrings:
                continue
            cs = td.CharStrings[gname]
            cs.decompile()
            old_prog = list(cs.program)
            try:
                new_prog = _strip_program(list(cs.program))
                cs.program = new_prog
                cs.bytecode = None
                if new_prog != old_prog:
                    normalized += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f'  Warning: could not normalize {gname}: {e}',
                          file=sys.stderr)

    # Phase 2: Align programs per glyph across all masters
    for gname in glyphOrder:
        programs = []
        charstrings = []
        for td in top_dicts:
            if gname not in td.CharStrings:
                programs.append([])
                charstrings.append(None)
                continue
            cs = td.CharStrings[gname]
            cs.decompile()
            programs.append(list(cs.program))
            charstrings.append(cs)

        op_counts = set()
        for p in programs:
            ops = [t for t in p if isinstance(t, str)]
            op_counts.add(len(ops))

        if len(op_counts) > 1:
            try:
                new_programs = _align_glyph_programs(programs)
                for i, (new_prog, cs) in enumerate(zip(new_programs, charstrings)):
                    if cs is not None and new_prog != programs[i]:
                        cs.program = new_prog
                        cs.bytecode = None
                        aligned += 1
            except Exception as e:
                print(f'  Warning: could not align {gname}: {e}',
                      file=sys.stderr)

    if normalized:
        print(f'  Normalized {normalized} charstrings across {num_masters} masters',
              file=sys.stderr)
    if aligned:
        print(f'  Aligned {aligned} charstrings by removing zero-length segments',
              file=sys.stderr)
    if errors:
        print(f'  {errors} charstrings could not be normalized', file=sys.stderr)

    return _orig_merge(glyphOrder, num_masters, top_dicts, masterModel)


# Install the patch
cff_mod.merge_charstrings = _patched_merge

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def main():
    from fontmake.__main__ import main as fontmake_main

    designspace = 'sources/BuenaMono.designspace'
    output_dir = 'out/fonts'

    if not os.path.exists(designspace):
        print(f'Error: {designspace} not found. Run export-ufo.py first.',
              file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print('Building CFF2/OTF variable font (with charstring normalization)...')
    sys.argv = [
        'fontmake',
        '-m', designspace,
        '-o', 'variable-cff2',
        '--keep-overlaps',
        '--output-dir', output_dir,
    ]

    try:
        fontmake_main()
    except SystemExit as e:
        if e.code:
            print(f'\nBuild failed with exit code: {e.code}', file=sys.stderr)
            sys.exit(1)

    otf_path = os.path.join(output_dir, 'BuenaMono-VF.otf')
    if not os.path.exists(otf_path):
        print('\nError: OTF file was not created', file=sys.stderr)
        sys.exit(1)

    if os.environ.get('SKIP_PS_HINTS'):
        print('SKIP_PS_HINTS set — leaving OTF unhinted')
    else:
        # PostScript-hint the variable CFF2 (zones/stems come from the UFO
        # fontinfo written by export-ufo.py), then re-subroutinize: otfautohint
        # emits unsubroutinized charstrings (~2.2x size without this).
        import subprocess
        print('Hinting CFF2 with otfautohint...')
        subprocess.run(['otfautohint', otf_path], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('Re-subroutinizing with cffsubr...')
        subprocess.run([sys.executable, '-m', 'cffsubr', '-i', otf_path],
                       check=True)

    size_kb = os.path.getsize(otf_path) / 1024
    print(f'\nSuccess: {otf_path} ({size_kb:.0f} KB)')


if __name__ == '__main__':
    main()
