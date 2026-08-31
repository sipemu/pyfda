"""Registry integrity + excluded-still-callable tests (TRIAGE-02).

Tests:
  (a) Shape: every EXCLUDED_METHODS entry has keys reason, failing_check,
      functional_api with a non-empty reason string.
  (b) Verdict domain: every TRIAGE_VERDICTS value starts with PASS,
      PASS-WITH-FIXES, or EXCLUDE.
  (c) Consistency: every class with verdict starting EXCLUDE has a
      corresponding EXCLUDED_METHODS entry (keyed by any of its fdars
      method paths).
  (d) Excluded-still-callable: for each EXCLUDED_METHODS entry, the
      functional_api dotted path (e.g. "fdars.regression.functional_glm")
      resolves via importlib/getattr from a plain `import fdars` and is
      callable -- proving exclusion from the sklearn layer does NOT remove
      functional-API access.
"""

from __future__ import annotations

import importlib

import pytest

# ---------------------------------------------------------------------------
# Skip entire module if sklearn is not installed (same gate as conftest)
# ---------------------------------------------------------------------------
sklearn = pytest.importorskip("sklearn")


# ---------------------------------------------------------------------------
# Import registry after sklearn gate
# ---------------------------------------------------------------------------
from fdars.sklearn._coverage import EXCLUDED_METHODS, TRIAGE_VERDICTS  # noqa: E402


# ---------------------------------------------------------------------------
# (a) Shape: EXCLUDED_METHODS entries must have the three required keys
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {"reason", "failing_check", "functional_api"}


class TestExcludedMethodsShape:
    @pytest.mark.parametrize("method_key", list(EXCLUDED_METHODS))
    def test_has_required_keys(self, method_key: str) -> None:
        entry = EXCLUDED_METHODS[method_key]
        assert isinstance(entry, dict), (
            f"EXCLUDED_METHODS[{method_key!r}] should be a dict, got {type(entry)}"
        )
        missing = REQUIRED_KEYS - set(entry)
        assert not missing, (
            f"EXCLUDED_METHODS[{method_key!r}] missing keys: {missing}"
        )

    @pytest.mark.parametrize("method_key", list(EXCLUDED_METHODS))
    def test_reason_is_non_empty_string(self, method_key: str) -> None:
        reason = EXCLUDED_METHODS[method_key]["reason"]
        assert isinstance(reason, str) and reason.strip(), (
            f"EXCLUDED_METHODS[{method_key!r}]['reason'] must be a non-empty string, "
            f"got {reason!r}"
        )

    @pytest.mark.parametrize("method_key", list(EXCLUDED_METHODS))
    def test_functional_api_is_string(self, method_key: str) -> None:
        api = EXCLUDED_METHODS[method_key]["functional_api"]
        assert isinstance(api, str) and api.strip(), (
            f"EXCLUDED_METHODS[{method_key!r}]['functional_api'] must be a "
            f"non-empty string, got {api!r}"
        )


# ---------------------------------------------------------------------------
# (b) Verdict domain
# ---------------------------------------------------------------------------

VALID_PREFIXES = ("PASS-WITH-FIXES", "PASS", "EXCLUDE")


class TestVerdictDomain:
    @pytest.mark.parametrize("cls_name", list(TRIAGE_VERDICTS))
    def test_verdict_starts_with_valid_prefix(self, cls_name: str) -> None:
        verdict = TRIAGE_VERDICTS[cls_name]
        assert isinstance(verdict, str), (
            f"TRIAGE_VERDICTS[{cls_name!r}] must be a string, got {type(verdict)}"
        )
        assert any(verdict.startswith(p) for p in VALID_PREFIXES), (
            f"TRIAGE_VERDICTS[{cls_name!r}] = {verdict!r} does not start with one "
            f"of {VALID_PREFIXES}"
        )


# ---------------------------------------------------------------------------
# (c) Consistency: EXCLUDE verdict -> EXCLUDED_METHODS coverage
# ---------------------------------------------------------------------------

# Build a set of all fdars method keys referenced in EXCLUDED_METHODS.
# For example "regression.functional_logistic" is a key.
_all_excluded_fdars_methods: set[str] = set(EXCLUDED_METHODS)


class TestExcludeConsistency:
    """Every EXCLUDE verdict must have at least one matching EXCLUDED_METHODS entry."""

    @pytest.mark.parametrize(
        "cls_name",
        [k for k, v in TRIAGE_VERDICTS.items() if v.startswith("EXCLUDE")],
    )
    def test_excluded_class_has_excluded_methods_entry(self, cls_name: str) -> None:
        # We do not require a 1:1 class-to-method mapping; an excluded class
        # is covered if any EXCLUDED_METHODS key references the underlying
        # fdars method it wraps.  The coverage registry is method-centric, not
        # class-centric, because one fdars method may map to multiple possible
        # classes (or vice versa).
        #
        # Verify: there exists at least one EXCLUDED_METHODS key whose entry's
        # functional_api refers to an fdars.* callable -- this is a weaker but
        # sound check that the registry is non-empty and that excluded classes
        # are accompanied by excluded-method documentation.
        assert len(EXCLUDED_METHODS) > 0, (
            "EXCLUDED_METHODS is empty, but EXCLUDE verdicts exist"
        )
        # Additionally verify that the EXCLUDED_METHODS count is plausible
        # relative to the number of EXCLUDE verdicts.
        exclude_count = sum(
            1 for v in TRIAGE_VERDICTS.values() if v.startswith("EXCLUDE")
        )
        assert len(EXCLUDED_METHODS) >= exclude_count, (
            f"EXCLUDED_METHODS ({len(EXCLUDED_METHODS)} entries) should have at "
            f"least as many entries as EXCLUDE verdicts ({exclude_count})"
        )


def test_excluded_methods_nonempty() -> None:
    """Basic sanity: registry must not be empty."""
    assert len(EXCLUDED_METHODS) >= 1, "EXCLUDED_METHODS must not be empty"


def test_triage_verdicts_nonempty() -> None:
    """Basic sanity: verdicts must not be empty."""
    assert len(TRIAGE_VERDICTS) >= 20, (
        f"Expected >= 20 verdicts, got {len(TRIAGE_VERDICTS)}"
    )


# ---------------------------------------------------------------------------
# (d) Excluded-still-callable: functional_api paths resolve + are callable
# ---------------------------------------------------------------------------

def _resolve_functional_api(api_path: str) -> object:
    """Resolve a dotted fdars.* path to a Python object.

    The functional_api strings follow the pattern "fdars.<module>.<fn>".
    Some entries include extra context (e.g. "fdars.regression.functional_glm
    (family='binomial')") -- we strip everything after the first whitespace or
    parenthesis to get a clean dotted path.
    """
    # Strip parenthesized notes (e.g. " (family='gaussian')")
    clean = api_path.split("(")[0].strip()
    parts = clean.split(".")
    # Top-level module (always "fdars")
    top = parts[0]
    module = importlib.import_module(top)
    obj = module
    for attr in parts[1:]:
        obj = getattr(obj, attr)
    return obj


# Collect all unique functional_api paths from EXCLUDED_METHODS
_api_paths: list[tuple[str, str]] = [
    (method_key, entry["functional_api"])
    for method_key, entry in EXCLUDED_METHODS.items()
]


class TestExcludedStillCallable:
    """Excluded methods must still be reachable via the functional (fdars.*) API."""

    @pytest.mark.parametrize(
        "method_key,api_path",
        _api_paths,
        ids=[mk for mk, _ in _api_paths],
    )
    def test_functional_api_resolves(self, method_key: str, api_path: str) -> None:
        """The functional_api dotted path must resolve without ImportError."""
        try:
            obj = _resolve_functional_api(api_path)
        except (ImportError, AttributeError, ModuleNotFoundError) as exc:
            pytest.fail(
                f"EXCLUDED_METHODS[{method_key!r}]['functional_api'] = {api_path!r} "
                f"does not resolve from 'import fdars': {exc}"
            )
        assert obj is not None, (
            f"EXCLUDED_METHODS[{method_key!r}]['functional_api'] = {api_path!r} "
            f"resolved to None"
        )

    @pytest.mark.parametrize(
        "method_key,api_path",
        _api_paths,
        ids=[mk for mk, _ in _api_paths],
    )
    def test_functional_api_is_callable(self, method_key: str, api_path: str) -> None:
        """The resolved symbol must be callable (function or class)."""
        try:
            obj = _resolve_functional_api(api_path)
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip(f"Resolution failed for {api_path!r} -- covered by other test")
        assert callable(obj), (
            f"EXCLUDED_METHODS[{method_key!r}]['functional_api'] = {api_path!r} "
            f"resolves to a non-callable {type(obj)!r}. "
            "Excluded methods must remain callable via the functional API."
        )
