"""Foundation contract tests for the fdars sklearn layer.

Verifies the FND success facts from the Phase 55 plan:
- FND-01: base package purity (import fdars needs zero sklearn)
- FND-01/02: actionable ImportError when sklearn absent
- FND-02: python/fdars/__init__.py unchanged (git diff empty)
- FND-03: _BaseFdarsEstimator verbatim storage + clone round-trips
- FND-03: set_params contract
- FND-03: fit contract (n_features_in_, argvals_, float32 upcast)
- FND-03: shim branch detection (validate_data + _HAS_TAGS_DATACLASS)
"""

from __future__ import annotations

import subprocess
import sys

import numpy as np
import pytest
from sklearn.base import clone


# ---------------------------------------------------------------------------
# FND-01: base package purity
# ---------------------------------------------------------------------------

def test_fdars_imports_without_sklearn():
    """import fdars must succeed with zero sklearn installed (FND-01).

    This test runs import fdars in a subprocess to verify it does not drag in
    scikit-learn as a side effect. The subprocess uses the same Python
    executable but we cannot uninstall sklearn -- instead we verify that
    fdars does NOT import sklearn by checking sys.modules in the subprocess.
    """
    code = (
        "import sys; "
        "import fdars; "
        "assert 'sklearn' not in sys.modules, "
        "f'sklearn leaked into sys.modules: {sorted(k for k in sys.modules if k.startswith(\"sklearn\"))}'"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"import fdars leaked sklearn into sys.modules.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# FND-02: foundation registration contract
# ---------------------------------------------------------------------------

def test_fdars_init_unchanged():
    """FND-02: fdars submodule registration contract — no core module may be dropped.

    The invariant this guard protects is the *foundation registration contract*:
    every submodule present in the Phase-55 baseline must still be registered
    in the current fdars package (via the _submodule_names → sys.modules loop
    in python/fdars/__init__.py). Additive registrations (new submodules such
    as ``fts``) are explicitly allowed; removals and renames of historically
    required submodules are not.

    The sklearn-safety invariant (import fdars must not import sklearn) is
    separately enforced by FND-01 (test_fdars_imports_without_sklearn) and is
    not re-checked here.

    Two assertions are made:
    1. Subset invariant: Phase-55 baseline _submodule_names ⊆ current names.
    2. Registration invariant: every name in the current set can be imported
       as ``fdars.<name>`` and is reachable as an attribute of the fdars package
       (the dynamic sys.modules injection in __init__.py is intact).
    """
    import importlib
    import re

    # Commit hash of the pre-Phase-55 HEAD (the baseline for the registration contract).
    PHASE_55_BASE = "bf1a60638c0330c3909721dd900e704deeb82e8b"

    # The base commit must be reachable in the clone. A shallow checkout
    # (CI default fetch-depth: 1) omits it, and `git show` against a missing
    # commit exits 128 — a harness/CI setup issue, not a registration violation.
    # Distinguish it so the failure message is actionable.
    base_present = subprocess.run(
        ["git", "cat-file", "-e", f"{PHASE_55_BASE}^{{commit}}"],
        capture_output=True,
    )
    assert base_present.returncode == 0, (
        f"Phase 55 base commit {PHASE_55_BASE} is not present in the clone — "
        "run with full git history (set fetch-depth: 0 for this job in CI). "
        "This is a test-harness/CI setup issue, not an FND-02 violation."
    )

    def _parse_submodule_names(src: str) -> set:
        """Extract the _submodule_names tuple elements from __init__.py source."""
        m = re.search(r"_submodule_names\s*=\s*\((.*?)\)", src, re.DOTALL)
        assert m, "Could not locate _submodule_names tuple in __init__.py source"
        return set(re.findall(r'"([^"]+)"', m.group(1)))

    # 1. Recover the Phase-55 baseline submodule set from git history.
    baseline_result = subprocess.run(
        ["git", "show", f"{PHASE_55_BASE}:python/fdars/__init__.py"],
        capture_output=True,
        text=True,
    )
    assert baseline_result.returncode == 0, (
        f"Could not read python/fdars/__init__.py at {PHASE_55_BASE}: "
        f"{baseline_result.stderr}"
    )
    baseline_names = _parse_submodule_names(baseline_result.stdout)

    # 2. Recover the current submodule set from HEAD (source-of-truth).
    #    We parse the source file rather than inspecting the live module because
    #    __init__.py deletes _submodule_names from the module namespace after the
    #    registration loop (``del _name, _submod, _submodule_names``).
    current_result = subprocess.run(
        ["git", "show", "HEAD:python/fdars/__init__.py"],
        capture_output=True,
        text=True,
    )
    assert current_result.returncode == 0, (
        f"Could not read python/fdars/__init__.py at HEAD: {current_result.stderr}"
    )
    current_names = _parse_submodule_names(current_result.stdout)

    # 3. Subset invariant: no Phase-55 submodule may have been dropped or renamed.
    removed = baseline_names - current_names
    assert not removed, (
        f"FND-02 violation: submodule(s) removed from fdars since Phase 55: "
        f"{sorted(removed)}. "
        f"These were present in {PHASE_55_BASE} but are gone from HEAD. "
        f"Additive new submodules are allowed; removals are not."
    )

    # 4. Registration invariant: every current submodule must be importable as
    #    ``fdars.<name>`` and must be attached as an attribute of the fdars package
    #    (the dynamic sys.modules injection loop in __init__.py is intact).
    import fdars

    broken = []
    for name in sorted(current_names):
        try:
            mod = importlib.import_module(f"fdars.{name}")
        except ImportError as exc:
            broken.append(f"fdars.{name}: import failed — {exc}")
            continue
        attr = getattr(fdars, name, None)
        if attr is None:
            broken.append(f"fdars.{name}: getattr(fdars, {name!r}) returned None")
        elif attr is not mod:
            broken.append(
                f"fdars.{name}: getattr(fdars, {name!r}) is not the imported module "
                f"(sys.modules injection broken)"
            )
    assert not broken, (
        "FND-02 registration invariant violated:\n" + "\n".join(broken)
    )


# ---------------------------------------------------------------------------
# FND-01 / FND-02: actionable ImportError (tested with real current sklearn)
# ---------------------------------------------------------------------------

def test_fdars_sklearn_import_path():
    """fdars.sklearn must import successfully when sklearn is installed.

    When sklearn IS installed (as it is for this test run via the [sklearn] or
    [dev] extra), fdars.sklearn must import without error. The actionable
    ImportError path ('pip install fdars[sklearn]') is exercised in a
    subprocess that removes sklearn from sys.modules, confirming the error
    message is correct without requiring a separate environment.
    """
    # First, confirm it imports normally when sklearn is present.
    import fdars.sklearn  # noqa: F401
    from fdars.sklearn import _BaseFdarsEstimator, EXCLUDED_METHODS, TRIAGE_VERDICTS
    import collections.abc
    assert _BaseFdarsEstimator is not None
    # EXCLUDED_METHODS and TRIAGE_VERDICTS are read-only MappingProxyType objects;
    # check Mapping (not dict) so the assertion survives the read-only wrapping.
    assert isinstance(EXCLUDED_METHODS, collections.abc.Mapping)
    assert isinstance(TRIAGE_VERDICTS, collections.abc.Mapping)


def test_actionable_import_error_message(tmp_path):
    """fdars.sklearn without sklearn must raise ImportError with the install hint.

    Simulates absence of sklearn by running a subprocess that first removes
    sklearn from the import search path, then tries to import fdars.sklearn.
    Verifies the error message contains 'pip install fdars[sklearn]'.
    """
    script = tmp_path / "check_error.py"
    script.write_text(
        "import sys\n"
        "import importlib.abc\n"
        "\n"
        "class _Blocker(importlib.abc.MetaPathFinder):\n"
        "    def find_spec(self, name, *a, **kw):\n"
        "        if name.startswith('sklearn'):\n"
        "            raise ImportError('blocked')\n"
        "        return None\n"
        "\n"
        "# Remove any cached sklearn modules\n"
        "for k in list(sys.modules):\n"
        "    if k.startswith('sklearn'):\n"
        "        del sys.modules[k]\n"
        "\n"
        "sys.meta_path.insert(0, _Blocker())\n"
        "\n"
        "try:\n"
        "    import fdars.sklearn\n"
        "    raise AssertionError('Should have raised ImportError')\n"
        "except ImportError as e:\n"
        "    msg = str(e)\n"
        "    assert 'pip install fdars[sklearn]' in msg, f'missing hint in: {msg!r}'\n"
        "    print('actionable-ok')\n"
    )
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"actionable ImportError test failed.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "actionable-ok" in result.stdout


# ---------------------------------------------------------------------------
# FND-03: verbatim storage + clone round-trip
# ---------------------------------------------------------------------------

def test_fpca_verbatim_storage_none():
    """FPCATransformer(argvals=None) must store None verbatim (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    est = FPCATransformer(n_components=2)
    params = est.get_params()
    assert params["argvals"] is None, (
        f"argvals should be None (verbatim), got {params['argvals']!r}"
    )
    assert params["n_components"] == 2


def test_fpca_clone_round_trip():
    """clone(FPCATransformer(...)) must reproduce params exactly (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    est = FPCATransformer(n_components=2)
    cloned = clone(est)
    assert cloned.get_params() == est.get_params()


def test_fpca_clone_with_argvals():
    """clone round-trip must work with a list argvals (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    argvals = list(range(10))
    est = FPCATransformer(argvals=argvals, n_components=2)
    cloned = clone(est)
    # clone() uses get_params() -> set_params(); get_params returns the stored
    # value. For list argvals, the cloned value should be equal.
    assert cloned.get_params()["n_components"] == 2
    assert list(cloned.get_params()["argvals"]) == argvals


# ---------------------------------------------------------------------------
# FND-03: set_params
# ---------------------------------------------------------------------------

def test_fpca_set_params():
    """set_params must update n_components correctly (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    est = FPCATransformer(n_components=2)
    est.set_params(n_components=3)
    assert est.get_params()["n_components"] == 3


# ---------------------------------------------------------------------------
# FND-03: fit contract — n_features_in_, argvals_, float32 upcast
# ---------------------------------------------------------------------------

@pytest.fixture
def X_6x10():
    rng = np.random.default_rng(0)
    return rng.standard_normal((6, 10)).astype(np.float64)


def test_fpca_n_features_in(X_6x10):
    """fit must set n_features_in_ via validate_data (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    est = FPCATransformer(n_components=2).fit(X_6x10)
    assert est.n_features_in_ == 10


def test_fpca_argvals_default(X_6x10):
    """fit must resolve argvals_ to np.arange(n_features) by default (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    est = FPCATransformer(n_components=2).fit(X_6x10)
    assert hasattr(est, "argvals_")
    assert est.argvals_.shape == (10,)
    np.testing.assert_array_equal(est.argvals_, np.arange(10, dtype=np.float64))


def test_fpca_float32_upcast():
    """fit on float32 must not raise and must produce float64 components_ (FND-03)."""
    from fdars.sklearn._skeletons import FPCATransformer

    rng = np.random.default_rng(1)
    X32 = rng.standard_normal((8, 15)).astype(np.float32)
    est = FPCATransformer(n_components=2).fit(X32)
    assert est.components_.dtype == np.float64


# ---------------------------------------------------------------------------
# FND-03: shim branch detection
# ---------------------------------------------------------------------------

def test_validate_shim_callable():
    """_validate from _base must be callable on this sklearn installation (FND-03)."""
    from fdars.sklearn._base import _validate

    assert callable(_validate), "_validate must be callable"


def test_has_tags_dataclass_is_bool():
    """_HAS_TAGS_DATACLASS must be a bool regardless of sklearn version (FND-03)."""
    from fdars.sklearn._base import _HAS_TAGS_DATACLASS

    assert isinstance(_HAS_TAGS_DATACLASS, bool), (
        f"_HAS_TAGS_DATACLASS must be bool, got {type(_HAS_TAGS_DATACLASS)}"
    )


def test_validate_shim_sets_n_features_in():
    """_validate must set n_features_in_ on the estimator (FND-03).

    Tests the shim is active on the installed sklearn version by calling it
    via FPCATransformer.fit and checking the sklearn-expected side effect.
    """
    from fdars.sklearn._skeletons import FPCATransformer

    rng = np.random.default_rng(2)
    X = rng.standard_normal((5, 12)).astype(np.float64)
    est = FPCATransformer(n_components=2).fit(X)
    # validate_data (or _validate_data) sets n_features_in_ as a side effect.
    assert hasattr(est, "n_features_in_")
    assert est.n_features_in_ == 12


def test_hast_tags_consistent_with_sklearn_version():
    """_HAS_TAGS_DATACLASS must match whether sklearn exposes the Tags class (FND-03)."""
    from fdars.sklearn._base import _HAS_TAGS_DATACLASS

    try:
        from sklearn.utils import Tags  # noqa: F401
        expected = True
    except ImportError:
        expected = False

    assert _HAS_TAGS_DATACLASS == expected, (
        f"_HAS_TAGS_DATACLASS={_HAS_TAGS_DATACLASS} but Tags available={expected}"
    )
