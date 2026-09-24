"""The documented public import path ``from fdars.sklearn import X`` must work."""
import inspect

import pytest

pytest.importorskip("sklearn")

import fdars.sklearn as fsk  # noqa: E402
from fdars.sklearn import _skeletons  # noqa: E402
from fdars.sklearn._base import _BaseFdarsEstimator  # noqa: E402


def _defined_estimators():
    return sorted(
        name for name, obj in vars(_skeletons).items()
        if inspect.isclass(obj)
        and obj.__module__ == _skeletons.__name__
        and issubclass(obj, _BaseFdarsEstimator)
        and not name.startswith("_")
    )


def test_every_estimator_is_publicly_exported():
    names = _defined_estimators()
    assert len(names) == 28
    for name in names:
        assert getattr(fsk, name) is getattr(_skeletons, name)
        assert name in fsk.__all__


def test_documented_import_path():
    from fdars.sklearn import FPCATransformer  # noqa: F401
