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

# Paper figure pipeline targets.
#
# Requires both scripts/ (for docs_fig) and paper/code/ (for paper_utils)
# on PYTHONPATH.  PDF compile (tectonic) is CI-only — not invoked here.
PAPER_PYTHONPATH := scripts:paper/code

.PHONY: paper paper-figures paper-coverage paper-refs paper-snippets paper-check

paper-figures:  ## Regenerate all paper figures deterministically
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_figures.py

paper-coverage:  ## Regenerate paper/coverage_counts.tex from _capability_map.json
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/assert_coverage.py

paper-refs:  ## Regenerate paper/refs.bib from _references_map.json
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_refs_bib.py

paper-snippets:  ## Regenerate paper/snippets/*.tex from executed fdars snippets (MANU-05)
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_snippets.py

paper-check:  ## Run the CI drift gates locally (exits 1 if any file is stale)
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/assert_coverage.py --check
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_refs_bib.py --check
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/check_comparison.py
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_snippets.py --check

paper: paper-figures paper-coverage paper-refs paper-snippets  ## Run the one-command reproducible paper pipeline
