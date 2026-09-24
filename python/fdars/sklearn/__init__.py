"""fdars.sklearn -- scikit-learn-compatible estimator layer for fdars.

Requires the [sklearn] extra::

    pip install fdars[sklearn]

Note
----
This subpackage is **not** registered in ``fdars.__init__`` and is never
imported by a plain ``import fdars``. Users import it explicitly::

    from fdars.sklearn import FPCATransformer
    from fdars.sklearn._base import _BaseFdarsEstimator

The gating pattern mirrors ``fdars.mcp`` and ``fdars.advisor``: a top-level
``try`` block proves scikit-learn is present before any submodule import runs.
"""

try:
    from sklearn.base import BaseEstimator  # noqa: F401 -- proves sklearn present
except ImportError as _e:
    raise ImportError(
        "fdars[sklearn] requires scikit-learn. "
        "Install it with: pip install fdars[sklearn]"
    ) from _e

from fdars.sklearn._base import _BaseFdarsEstimator  # noqa: E402
from fdars.sklearn._coverage import EXCLUDED_METHODS, TRIAGE_VERDICTS  # noqa: E402

from fdars.sklearn._skeletons import (  # noqa: E402
    BSplineSmoother,
    BasisRepresentation,
    DDClassifier,
    DepthTransformer,
    DepthgramDetector,
    ElasticMultinomialClassifier,
    FPCATransformer,
    FPCKNNClassifier,
    FPCLDAClassifier,
    FPCQDAClassifier,
    FPCRegressor,
    FunctionalGMM,
    FunctionalKMeans,
    FuzzyFunctionalCMeans,
    GLMRegressor,
    Imputer,
    LRTOutlierDetector,
    LocalPolynomialSmoother,
    LogisticFPCClassifier,
    MUODDetector,
    MagnitudeShapeDetector,
    NonparametricRegressor,
    NormTransformer,
    OutliergramDetector,
    PLSRegressor,
    RobustFPCRegressor,
    SplineInterpolator,
    TVDMSSDetector,
)

# The 28 estimators that pass check_estimator, re-exported so the documented
# ``from fdars.sklearn import FPCATransformer`` works (they live in _skeletons).
__all__ = [
    "_BaseFdarsEstimator",
    "EXCLUDED_METHODS",
    "TRIAGE_VERDICTS",
    "BSplineSmoother",
    "BasisRepresentation",
    "DDClassifier",
    "DepthTransformer",
    "DepthgramDetector",
    "ElasticMultinomialClassifier",
    "FPCATransformer",
    "FPCKNNClassifier",
    "FPCLDAClassifier",
    "FPCQDAClassifier",
    "FPCRegressor",
    "FunctionalGMM",
    "FunctionalKMeans",
    "FuzzyFunctionalCMeans",
    "GLMRegressor",
    "Imputer",
    "LRTOutlierDetector",
    "LocalPolynomialSmoother",
    "LogisticFPCClassifier",
    "MUODDetector",
    "MagnitudeShapeDetector",
    "NonparametricRegressor",
    "NormTransformer",
    "OutliergramDetector",
    "PLSRegressor",
    "RobustFPCRegressor",
    "SplineInterpolator",
    "TVDMSSDetector",
]
