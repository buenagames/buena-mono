SOURCES=$(shell python3 scripts/read-config.py --sources )
FAMILY=$(shell python3 scripts/read-config.py --family )
SITE_REPO ?= ../buena-mono.buenalabs.io
help:
	@echo "###"
	@echo "# Build targets for $(FAMILY)"
	@echo "###"
	@echo
	@echo "  make build:  Builds the fonts and places them in the out/fonts/ directory"
	@echo "  make build-subset: Builds the site's display subset webfont"
	@echo "  make deploy-site:  Copies the webfonts into the specimen site repo"
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
	. venv/bin/activate; fontmake -m sources/BuenaMono.designspace -o variable --output-dir out/fonts/
	. venv/bin/activate; python3 scripts/build-cff2.py
	. venv/bin/activate; python3 scripts/inject-stat.py
	. venv/bin/activate; python3 scripts/add-gasp-table.py
	. venv/bin/activate; python3 scripts/post-process.py
	. venv/bin/activate; python3 scripts/build-gf-pair.py
	. venv/bin/activate; python3 -c "from fontTools.ttLib import TTFont; f=TTFont('out/fonts/BuenaMono-VF.ttf'); f.flavor='woff2'; f.save('out/fonts/BuenaMono-VF.woff2')"
	touch build.stamp

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

# QA the GF submission pair in isolation, exactly as Google's CI sees
# it. Mixing in the 2-axis -VF files trips family-level checks
# (canonical_filename, consistent_axes) that don't apply to the
# submission.
test: build.stamp
	. venv/bin/activate; command -v fontspector >/dev/null 2>&1 || bash scripts/install-fontspector.sh
	rm -rf out/qa; mkdir -p out/qa out/fontspector
	cp "out/fonts/BuenaMono[wght].ttf" "out/fonts/BuenaMono-Italic[wght].ttf" out/qa/
	. venv/bin/activate; fontspector --profile googlefonts -l warn --full-lists --succinct --html out/fontspector/fontspector-report.html --ghmarkdown out/fontspector/fontspector-report.md --badges out/badges out/qa/*.ttf  || echo '::warning file=sources/config.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

proof: venv build.stamp
	. venv/bin/activate; mkdir -p out/proof; if command -v diff3proof >/dev/null 2>&1; then diff3proof out/fonts/BuenaMono-VF.ttf --output out/proof; else TOCHECK=$$(find out/fonts -type f 2>/dev/null); diffenator2 proof $$TOCHECK -o out/proof; fi

export-ufo: venv  ## Export UFO + designspace from .glyphs (GPOS from anchors)
	. venv/bin/activate; python3 scripts/export-ufo.py

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

build-subset: venv  ## Build the specimen site's display subset (out/fonts/BuenaMono-VF.subset.woff2)
	. venv/bin/activate; python3 scripts/build-subset.py

deploy-site: build-subset  ## Copy full + subset webfonts into the site's public/fonts/ (override path with SITE_REPO=...)
	@test -d "$(SITE_REPO)/public/fonts" || { echo "error: no site repo at $(SITE_REPO)/public/fonts — pass SITE_REPO=/path/to/buena-mono.buenalabs.io"; exit 1; }
	@for f in BuenaMono-VF.woff2 BuenaMono-VF.ttf BuenaMono-VF.subset.woff2; do \
		test -f "out/fonts/$$f" || { echo "error: out/fonts/$$f missing — run 'make build' first"; exit 1; }; \
	done
	cp out/fonts/BuenaMono-VF.woff2 out/fonts/BuenaMono-VF.ttf out/fonts/BuenaMono-VF.subset.woff2 "$(SITE_REPO)/public/fonts/"
	@echo "→ deployed BuenaMono-VF.{woff2,ttf,subset.woff2} to $(SITE_REPO)/public/fonts/ — commit them in the site repo"

build-otf: venv  ## Build CFF2 variable font from designspace (with charstring normalization)
	mkdir -p out/fonts; . venv/bin/activate; python3 scripts/build-cff2.py

inject-stat: venv  ## Inject STAT axis values from config.yaml into TTF and OTF
	. venv/bin/activate; python3 scripts/inject-stat.py

check-manifest: venv  ## Validate source state against manifest
	. venv/bin/activate; python3 scripts/check-manifest.py

generate-manifest: venv  ## Generate source manifest
	. venv/bin/activate; python3 scripts/generate-manifest.py

build-all: export-ufo build-otf inject-stat build-woff2  ## Build TTF + WOFF2 + OTF variable fonts

images: venv  ## Generate all README/docs PNGs (hero, cli, character-set, social-preview, specimen, stylistic-sets) from fonts/variable/
	. venv/bin/activate; python3 -c "import drawbot_skia" 2>/dev/null || pip install drawbot-skia
	. venv/bin/activate; for py in docs/hero.py docs/character-set-*.py docs/cli.py docs/social-preview.py; do python3 $$py --output $${py%.py}.png; done
	. venv/bin/activate; python3 scripts/make-specimens.py fonts/variable/BuenaMono-VF.ttf docs  # specimen.png + stylistic-sets.png (needs hb-view)

marketing: venv  ## Generate marketing assets (social, video, ASO) into docs/marketing/ from fonts/variable/
	. venv/bin/activate; python3 -c "import drawbot_skia" 2>/dev/null || pip install drawbot-skia
	. venv/bin/activate; python3 docs/marketing.py

font-summary: venv build.stamp  ## Print font development summary
	. venv/bin/activate; python3 scripts/font-summary.py

qa: venv build.stamp  ## Run QA validation suite against built fonts
	. venv/bin/activate; python3 scripts/qa-validate.py --font-dir out/fonts

qa-source: venv  ## Validate .glyphs source (winding, topology, degenerate points)
	. venv/bin/activate; python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs

qa-fix: venv  ## Auto-fix source issues (winding, degenerate points)
	. venv/bin/activate; python3 scripts/qa-validate.py --source sources/BuenaMono.glyphs --fix

qa-all: qa-source build.stamp qa  ## Full validation (source + built fonts)

package: build.stamp  ## Assemble Google Fonts submission directory
	rm -rf out/googlefonts
	mkdir -p out/googlefonts/ofl/buenamono/article
	cp "out/fonts/BuenaMono[wght].ttf" out/googlefonts/ofl/buenamono/
	cp "out/fonts/BuenaMono-Italic[wght].ttf" out/googlefonts/ofl/buenamono/
	cp OFL.txt out/googlefonts/ofl/buenamono/OFL.txt
	cp docs/metadata.pb out/googlefonts/ofl/buenamono/METADATA.pb
	cp docs/ARTICLE.en_us.html out/googlefonts/ofl/buenamono/article/ARTICLE.en_us.html
	cp docs/specimen.png out/googlefonts/ofl/buenamono/article/specimen.png
	cp docs/DESCRIPTION.en_us.html out/googlefonts/ofl/buenamono/DESCRIPTION.en_us.html
	@echo "\nGoogle Fonts package ready at out/googlefonts/ofl/buenamono/"
	@ls -la out/googlefonts/ofl/buenamono/
	@echo "\nVerifying submission with fontspector (from the family dir, as GF CI does)..."
	. venv/bin/activate; command -v fontspector >/dev/null 2>&1 || bash scripts/install-fontspector.sh
	. venv/bin/activate; cd out/googlefonts/ofl/buenamono && fontspector --profile googlefonts -l warn --succinct "BuenaMono[wght].ttf" "BuenaMono-Italic[wght].ttf" || true
