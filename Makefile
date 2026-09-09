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

.PHONY: paper paper-figures paper-coverage paper-refs paper-snippets paper-check paper-verify arxiv

# arXiv submission bundle.
#   Contents (per https://info.arxiv.org/help/submit): LaTeX SOURCE only — no
#   PDF of the paper, no paper/code/, no build artifacts. arXiv does not
#   reliably run bibtex for a two-database \bibliography{refs,refs_manual}, so
#   the pre-generated paper.bbl is bundled and references render without arXiv
#   re-running bibtex. Requires paper/paper.bbl from a prior LaTeX+bibtex (or
#   `tectonic --keep-intermediate-files`) compile — the CI `arxiv` job produces
#   it. All packages used are in arXiv's TeX Live; no local .sty is bundled.
ARXIV_STAGE   := paper/_arxiv
ARXIV_TARBALL := paper/arxiv-submission.tar.gz

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

paper-verify:  ## Regenerate figures and assert byte-stability (SC-5 / CASE determinism hard gate)
	PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_figures.py
	git diff --exit-code paper/figures/

paper: paper-figures paper-coverage paper-refs paper-snippets  ## Run the one-command reproducible paper pipeline

arxiv:  ## Assemble paper/arxiv-submission.tar.gz (LaTeX source + paper.bbl; requires a prior compile)
	@test -f paper/paper.bbl || { \
	  echo "ERROR: paper/paper.bbl not found."; \
	  echo "Run a LaTeX+bibtex compile first (CI 'arxiv' job, or locally:"; \
	  echo "  cd paper && latexmk -pdf paper.tex   # produces paper.bbl)"; \
	  exit 1; }
	rm -rf $(ARXIV_STAGE) $(ARXIV_TARBALL)
	mkdir -p $(ARXIV_STAGE)/sections $(ARXIV_STAGE)/snippets $(ARXIV_STAGE)/figures
	install -m644 paper/paper.tex          $(ARXIV_STAGE)/
	install -m644 paper/paper.bbl          $(ARXIV_STAGE)/
	install -m644 paper/coverage_counts.tex $(ARXIV_STAGE)/
	install -m644 paper/refs.bib paper/refs_manual.bib $(ARXIV_STAGE)/
	install -m644 paper/sections/*.tex     $(ARXIV_STAGE)/sections/
	install -m644 paper/snippets/*.tex     $(ARXIV_STAGE)/snippets/
	install -m644 paper/figures/*.pdf      $(ARXIV_STAGE)/figures/
	tar -czf $(ARXIV_TARBALL) -C $(ARXIV_STAGE) .
	@echo "== arXiv bundle contents =="
	@tar -tzf $(ARXIV_TARBALL) | sort
	@echo "== bundle size =="
	@du -h $(ARXIV_TARBALL)
