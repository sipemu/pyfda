"""advise()/auto_tune() must let the provider factory resolve the model.

Regression test: the entry points used to hard-code model="claude-opus-4-8",
so FDARS_ADVISOR_MODEL never took effect and non-Anthropic providers were
asked for a Claude model name.
"""
import inspect

import fdars.advisor as adv
from fdars.advisor import _compare_methods, _pipeline
from fdars.advisor.providers import _factory


def test_entry_point_model_defaults_are_none():
    for fn in (adv.advise, adv.auto_tune, adv.describe_cluster_differences
               if hasattr(adv, "describe_cluster_differences") else adv.advise):
        assert inspect.signature(fn).parameters["model"].default is None


def test_internal_helpers_default_to_none():
    src = inspect.getsource(_pipeline) + inspect.getsource(_compare_methods)
    assert 'model: str = "claude-opus-4-8"' not in src


def test_factory_default_for_anthropic_unchanged():
    assert _factory._DEFAULT_MODELS["anthropic"] == "claude-opus-4-8"
