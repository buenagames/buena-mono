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

build.stamp: venv sources/BuenaMono.designspace
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
	touch venv/touchfile

test: build.stamp
	. venv/bin/activate; command -v fontspector >/dev/null 2>&1 || bash scripts/install-fontspector.sh
	. venv/bin/activate; TOCHECK=$$(find out/fonts -type f 2>/dev/null); mkdir -p out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --html out/fontspector/fontspector-report.html --ghmarkdown out/fontspector/fontspector-report.md --badges out/badges $$TOCHECK  || echo '::warning file=sources/config.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

proof: venv build.stamp
	TOCHECK=$$(find out/fonts -type f 2>/dev/null); . venv/bin/activate; mkdir -p out/proof; diffenator2 proof $$TOCHECK -o out/proof

marketing: venv  ## Generate marketing/brand assets (social, video, ASO, guidelines) into marketing/{png,svg}
	. venv/bin/activate; python3 -c "import drawbot_skia" 2>/dev/null || pip install drawbot-skia
	. venv/bin/activate; python3 marketing/marketing_svg.py
	. venv/bin/activate; python3 marketing/marketing.py

export-ufo: venv  ## Export UFO + designspace from .glyphs (GPOS from anchors)
	. venv/bin/activate; python3 scripts/export-ufo.py
	@echo "==> restoring GF-required feature order (glyphsLib export puts smcp after liga)"
	. venv/bin/activate; python3 scripts/fix-gf-structural-fails.py

clean:
	rm -rf venv
	find . -name "*.pyc" -delete

update-project-template:
	npx update-template https://github.com/googlefonts/googlefonts-project-template/

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
	cp docs/ARTICLE.en_us.html out/googlefonts/ofl/buenamono/article/ARTICLE.en_us.html
	cp docs/specimen.png out/googlefonts/ofl/buenamono/article/specimen.png
	@echo "\nGoogle Fonts package ready at out/googlefonts/ofl/buenamono/"
	@ls -la out/googlefonts/ofl/buenamono/
	@echo "\nVerifying submission with fontspector (from the family dir, as GF CI does)..."
	. venv/bin/activate; command -v fontspector >/dev/null 2>&1 || bash scripts/install-fontspector.sh
	. venv/bin/activate; cd out/googlefonts/ofl/buenamono && fontspector --profile googlefonts -l warn --succinct "BuenaMono[wght].ttf" "BuenaMono-Italic[wght].ttf" || true

release:  ## Ship a new font version → public repo + live landing page (build, publish, sync:fonts, deploy)
	bash scripts/sync-release.sh
