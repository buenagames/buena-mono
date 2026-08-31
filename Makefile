SOURCES=$(shell python3 scripts/read-config.py --sources )
FAMILY=$(shell python3 scripts/read-config.py --family )
help:
	@echo "###"
	@echo "# Build targets for $(FAMILY)"
	@echo "###"
	@echo
	@echo "  make build:  Builds the fonts and places them in the out/fonts/ directory"
	@echo "  make test:   Tests the fonts with fontspector"
	@echo "  make proof:  Creates HTML proof documents in the proof/ directory"
	@echo "  make images: Creates PNG specimen images in the docs/ directory"
	@echo

build: build.stamp

venv: venv/touchfile

customize: venv
	. venv/bin/activate; python3 scripts/customize.py

# Everything the built binaries actually depend on. Without the script list a
# change to post-processing leaves a stale font in out/fonts and `make build`
# reports "Nothing to be done", so the fix silently never ships. UFO contents
# are covered by check-manifest.py below, which fails the build on source drift.
BUILD_SCRIPTS = scripts/check-manifest.py scripts/build-cff2.py \
                scripts/inject-stat.py scripts/add-gasp-table.py \
                scripts/post-process.py
BUILD_SOURCES = sources/BuenaMono.designspace sources/BuenaMono.glyphs \
                sources/config.yaml

build.stamp: venv $(BUILD_SOURCES) $(BUILD_SCRIPTS)
	. venv/bin/activate; python3 scripts/check-manifest.py
	rm -rf out/fonts
	mkdir -p out/fonts
	. venv/bin/activate; fontmake -m sources/BuenaMono.designspace -o variable --flatten-components --output-dir out/fonts/
	. venv/bin/activate; python3 scripts/build-cff2.py
	. venv/bin/activate; python3 scripts/inject-stat.py
	. venv/bin/activate; python3 scripts/add-gasp-table.py
	. venv/bin/activate; python3 scripts/post-process.py
	. venv/bin/activate; python3 -c "from fontTools.ttLib import TTFont; f=TTFont('out/fonts/BuenaMono-VF.ttf'); f.flavor='woff2'; f.save('out/fonts/BuenaMono-VF.woff2')"
	touch build.stamp

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	bash scripts/install-fontspector.sh
	touch venv/touchfile

test: build.stamp
	. venv/bin/activate; command -v fontspector >/dev/null 2>&1 || bash scripts/install-fontspector.sh
	. venv/bin/activate; TOCHECK=$$(find out/fonts -type f 2>/dev/null); mkdir -p out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --html out/fontspector/fontspector-report.html --ghmarkdown out/fontspector/fontspector-report.md --badges out/badges $$TOCHECK  || echo '::warning file=sources/config.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

proof: venv build.stamp
	TOCHECK=$$(find out/fonts -type f 2>/dev/null); . venv/bin/activate; mkdir -p out/proof; diffenator2 proof $$TOCHECK -o out/proof

export-ufo: venv  ## Export UFO + designspace from .glyphs (GPOS from anchors)
	. venv/bin/activate; python3 scripts/export-ufo.py
	@echo "==> restoring GF-required feature order (glyphsLib export puts smcp after liga)"
	. venv/bin/activate; python3 scripts/fix-gf-structural-fails.py

clean:
	rm -rf venv
	find . -name "*.pyc" -delete

update-project-template:
	npx update-template https://github.com/googlefonts/googlefonts-project-template/

reports-venv: venv-reports/touchfile  ## Install the toolchain scripts/make-reports.py needs

# A SEPARATE venv, deliberately. Installed into venv/ this pulls fontParts and
# designspaceProblems, whose pins drag fontTools backwards -- 4.63 to 4.60.1 on
# 2026-08-31 -- and the font is built with fontTools. A report toolchain must
# never be able to change the binary that ships.
#
# PyICU compiles against a system ICU: on macOS that is the keg-only brewed
# icu4c, so its pkgconfig and bin must be on the path or the wheel build fails
# with an error that never mentions ICU.
venv-reports/touchfile: requirements-reports.in requirements-reports.txt
	test -d venv-reports || python3 -m venv venv-reports
	. venv-reports/bin/activate; \
	  ICU="$$(brew --prefix icu4c 2>/dev/null || brew --prefix icu4c@78 2>/dev/null)"; \
	  PKG_CONFIG_PATH="$$ICU/lib/pkgconfig:$$PKG_CONFIG_PATH" \
	  PATH="$$ICU/bin:$$PATH" \
	  pip install -q -Ur requirements-reports.txt
	touch venv-reports/touchfile

reports: reports-venv build.stamp  ## Regenerate the technical reports into the site repo
	@# OLD_FONT is the previous *released* font, for diffenator3's regression
	@# diff -- take the last release before this one. Without it that single
	@# report is skipped and every other generator still runs.
	@#   make reports OLD_FONT=/path/to/1.228/BuenaMono-VF.ttf
	@#   make reports ONLY=hyperglot,index
	@# fontspector lives in venv/, the report tools in venv-reports/, so both
	@# are on PATH for the run.
	@# venv/bin goes at the END of PATH, not the front: fontspector and
	@# diffenator3 live there and must be findable, but python3 must be the
	@# reports interpreter. Prepending venv/bin resolved python3 to the build
	@# venv, which has no hyperglot, and yaml.unsafe_load then failed to
	@# construct the objects hyperglot writes into its own output.
	ICU="$$(brew --prefix icu4c 2>/dev/null || brew --prefix icu4c@78 2>/dev/null)"; \
	  PATH="$$ICU/bin:$(CURDIR)/venv-reports/bin:$$HOME/.cargo/bin:$$PATH:$(CURDIR)/venv/bin" \
	  $(CURDIR)/venv-reports/bin/python3 scripts/make-reports.py $(if $(OLD_FONT),--old-font "$(OLD_FONT)",) $(if $(ONLY),--only "$(ONLY)",)

update: venv
	venv/bin/pip install --upgrade pip-tools
	# See https://pip-tools.readthedocs.io/en/latest/#a-note-on-resolvers for
	# the `--resolver` flag below.
	venv/bin/pip-compile --upgrade --verbose --resolver=backtracking requirements.in
	venv/bin/pip-sync requirements.txt

	git commit -m "Update requirements" requirements.txt
	git push

build-woff2: venv  ## Build WOFF2 variable font from existing TTF
	. venv/bin/activate; python3 -c "from fontTools.ttLib import TTFont; f=TTFont('out/fonts/BuenaMono-VF.ttf'); f.flavor='woff2'; f.save('out/fonts/BuenaMono-VF.woff2')"

build-otf: venv  ## Build CFF2 variable font from designspace (with charstring normalization)
	mkdir -p out/fonts; . venv/bin/activate; python3 scripts/build-cff2.py

inject-stat: venv  ## Inject STAT axis values from config.yaml into TTF and OTF
	. venv/bin/activate; python3 scripts/inject-stat.py

check-manifest: venv  ## Validate source state against manifest
	. venv/bin/activate; python3 scripts/check-manifest.py

generate-manifest: venv  ## Generate source manifest
	. venv/bin/activate; python3 scripts/generate-manifest.py

build-all: export-ufo build-otf inject-stat build-woff2  ## Build TTF + WOFF2 + OTF variable fonts

font-summary: venv build.stamp  ## Print font development summary
	. venv/bin/activate; python3 scripts/font-summary.py

qa: venv build.stamp  ## Run QA validation suite against built fonts
	. venv/bin/activate; python3 scripts/qa-validate.py --font-dir out/fonts
	. venv/bin/activate; python3 tests/sprite_coverage.py $$(test -f out/fonts/BuenaMono-VF.ttf && echo out/fonts/BuenaMono-VF.ttf || echo fonts/variable/BuenaMono-VF.ttf)

check-fonts: venv  ## Verify fonts/variable/ matches the current build (release gate)
	. venv/bin/activate; python3 scripts/check-committed-fonts.py

promote-fonts: venv build.stamp  ## Copy the current build over fonts/variable/
	. venv/bin/activate; python3 scripts/check-committed-fonts.py --promote

qa-source: venv  ## Validate .glyphs source (winding, topology, degenerate points)
	. venv/bin/activate; python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs

qa-fix: venv  ## Auto-fix source issues (winding, degenerate points)
	. venv/bin/activate; python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs --fix

qa-all: qa-source build.stamp qa  ## Full validation (source + built fonts)

sprite-test: venv  ## TUI/monospace coverage + integrity (box/blocks/braille complete @618); part of `qa`
	. venv/bin/activate; python3 tests/sprite_coverage.py fonts/variable/BuenaMono-VF.ttf

sprite-specimen: venv  ## Regenerate the TUI specimen: text + real-font HTML viewer + PNG (tests/)
	. venv/bin/activate; python3 tests/sprite_specimen.py --out tests/sprite-specimen.txt --html tests/sprite-specimen.html
	. venv/bin/activate; python3 -c "import drawbot_skia" 2>/dev/null || pip install drawbot-skia
	. venv/bin/activate; python3 tests/sprite_render.py

package: build.stamp  ## Assemble Google Fonts submission directory (wght-only Roman + Italic pair)
	rm -rf out/googlefonts
	mkdir -p out/googlefonts/ofl/buenamono/article
	. venv/bin/activate; python3 scripts/build-gf-pair.py --input out/fonts/BuenaMono-VF.ttf --output-dir out/fonts
	cp "out/fonts/BuenaMono[wght].ttf" "out/googlefonts/ofl/buenamono/BuenaMono[wght].ttf"
	cp "out/fonts/BuenaMono-Italic[wght].ttf" "out/googlefonts/ofl/buenamono/BuenaMono-Italic[wght].ttf"
	cp OFL.txt out/googlefonts/ofl/buenamono/OFL.txt
	cp docs/metadata.pb out/googlefonts/ofl/buenamono/METADATA.pb
	cp docs/DESCRIPTION.en_us.html out/googlefonts/ofl/buenamono/DESCRIPTION.en_us.html
	cp docs/ARTICLE.en_us.html out/googlefonts/ofl/buenamono/article/ARTICLE.en_us.html
	cp docs/specimen.png out/googlefonts/ofl/buenamono/article/specimen.png
	@echo "\nGoogle Fonts package ready at out/googlefonts/ofl/buenamono/"
	@ls -la out/googlefonts/ofl/buenamono/
	@echo "\nVerifying submission with fontspector (from the family dir, as GF CI does)..."
	. venv/bin/activate; command -v fontspector >/dev/null 2>&1 || bash scripts/install-fontspector.sh
	. venv/bin/activate; cd out/googlefonts/ofl/buenamono && fontspector --profile googlefonts -l warn --succinct "BuenaMono[wght].ttf" "BuenaMono-Italic[wght].ttf" || true
