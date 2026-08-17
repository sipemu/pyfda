"""fdars.advisor.aspects — Per-aspect diagnostics builders.

Each submodule contains one ``_build_<aspect>_diagnostics`` function plus its
private helpers, moved verbatim from ``advisor/__init__.py``.  The functions
are imported lazily by ``build_diagnostics()`` in ``advisor/__init__.py`` so
that importing ``fdars.advisor`` never forces a heavy import chain.

Submodules
----------
alignment  : ``_build_alignment_diagnostics``
fpca       : ``_build_fpca_diagnostics``
basis      : ``_build_basis_diagnostics``
smoothing  : ``_build_smoothing_diagnostics``
clustering : ``_build_clustering_diagnostics``
inference  : ``_build_inference_diagnostics``
"""
