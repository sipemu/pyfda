# Documentation build targets.
#
# The docs execute live `fdars` code at build time (markdown-exec) to render
# figures as inline SVG. That requires:
#   1. the compiled `fdars` package installed in the active environment
#      (`maturin develop`), and
#   2. `scripts/` on PYTHONPATH so code blocks can `from docs_fig import ...`.

export PYTHONPATH := scripts

.PHONY: docs-deps docs docs-serve docs-clean

docs-deps:  ## Install docs dependencies and build the fdars extension
	pip install -r docs/requirements.txt maturin
	maturin develop

docs:  ## Build the static documentation site into ./site
	mkdocs build --strict

docs-serve:  ## Live-reload docs server at http://127.0.0.1:8000
	mkdocs serve

docs-clean:
	rm -rf site
