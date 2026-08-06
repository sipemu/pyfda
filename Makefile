# Documentation build targets.
#
# The docs execute live `fdars` code at build time (markdown-exec) to render
# figures as inline SVG. That requires:
#   1. the compiled `fdars` package installed in the active environment
#      (`maturin develop`), and
#   2. `scripts/` on PYTHONPATH so code blocks can `from docs_fig import ...`.

export PYTHONPATH := scripts

.PHONY: docs-deps docs docs-check docs-scorecard docs-serve docs-clean

docs-deps:  ## Install docs dependencies and build the fdars extension
	pip install -r docs/requirements.txt maturin
	maturin develop

docs:  ## Build the static documentation site into ./site, gate on figure errors
	mkdocs build --strict
	python scripts/check_docs_figures.py site

docs-check:  ## Fail if any built figure block errored (run after `make docs`)
	python scripts/check_docs_figures.py site

docs-scorecard:  ## Print the A+ documentation scorecard
	python scripts/a_plus_scorecard.py

docs-serve:  ## Live-reload docs server at http://127.0.0.1:8000
	mkdocs serve

docs-clean:
	rm -rf site
