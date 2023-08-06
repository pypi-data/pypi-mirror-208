README.md: README.qmd
	quarto render $<

examples/%/_site: examples/%/_quarto.yml
	cd examples/$* \
		&& quarto add --no-prompt ../.. \
		&& quarto add --no-prompt quarto-ext/shinylive
	cd examples/$* && quartodoc build _quarto.yml --verbose
	cd examples/$* && quartodoc interlinks
	quarto render $(dir $<)

docs/examples/%: examples/%/_site
	rm -rf docs/examples/$*
	cp -rv $< $@

docs-build-examples: docs/examples/single-page docs/examples/pkgdown

docs-build: docs-build-examples
	cd docs && quarto add --no-prompt ..
	cd docs && quartodoc build
	cd docs && quartodoc interlinks
	quarto render docs

requirements-dev.txt:
	pip-compile setup.cfg --extra dev -o $@
