# Contributing to Buena Mono

Thanks for your interest in Buena Mono! Bug reports, glyph fixes, and coverage
suggestions are welcome.

## Reporting issues

Open an issue with a clear description. For rendering bugs, include the text,
the app/OS, and a screenshot; for a glyph, note its Unicode codepoint.

## Building

Requires Python 3.9+.

```sh
make build    # build the variable fonts into out/fonts/
make test     # QA with fontspector
make proof    # HTML proofs with diffenator2
```

The design source is [`sources/BuenaMono.glyphs`](sources/) (Glyphs 3), with UFO
masters and a `.designspace`. Build straight from the committed `sources/` — the
Makefile does not regenerate them.

## Pull requests

- Keep changes focused and describe the intent.
- Run `make build` and `make test` before submitting; the CI runs fontspector.
- By contributing, you agree to license your work under the
  [SIL Open Font License 1.1](OFL.txt), and to be added to
  [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt).

## License

Buena Mono is released under the [SIL Open Font License 1.1](OFL.txt). Portions
copyright the [Fragment Mono](https://github.com/weiweihuanghuang/fragment-mono)
Project Authors.
