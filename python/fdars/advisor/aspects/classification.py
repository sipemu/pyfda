"""fdars.advisor.aspects.classification — Classification diagnostics builder.

Contains ``_build_classification_diagnostics``.  Accepts the result dict
returned by any ``fdars.classification.*`` function.  Two distinct result
shapes are handled:

* Point-estimate functions (``fclassif_lda``, ``fclassif_qda``, ``fclassif_knn``,
  ``fclassif_kernel``, ``fclassif_dd``, etc.) ->
  ``{"predicted": arr (n,), "accuracy": float}``

* Cross-validation function (``fclassif_cv``) ->
  ``{"error_rate": float, "fold_errors": arr (nfold,), "best_ncomp": int}``
  NOTE: ``fclassif_cv`` has NO ``"accuracy"`` key — only ``"error_rate"``.

RESEARCH corrections applied:
  - Correction #2: read CV rate from raw key ``"error_rate"`` (fclassif_cv's
    actual key, NOT ``"cv_error_rate"``); emit in diagnostics as
    ``cv_error_rate`` to distinguish from point-estimate accuracy.
  - Correction #6: guard ``accuracy`` with ``if "accuracy" in raw``; when
    only CV error_rate is present, derive ``accuracy = 1.0 - error_rate``.

``n_classes`` cannot be inferred from the result dict (which contains only
predicted labels, not ground-truth class count).  It is an EXPLICIT parameter
forwarded from ``build_diagnostics(result, "classification", n_classes=K)``.

All values in the returned dict are native Python types (``float``, ``int``,
``bool``, ``list``, ``None``).  No NumPy scalars.  Two calls on the same input
always return an equal, JSON-serialisable dict.
"""

from __future__ import annotations

import numpy as np


def _build_classification_diagnostics(
    raw: dict,
    *,
    n_classes: "int | None" = None,
    holdout_accuracy: "float | None" = None,
    **kwargs,
) -> dict:
    """Compute classification diagnostics from an fdars classification result dict.

    Handles two result shapes (point-estimate and ``fclassif_cv``) by key
    presence guards.  All key accesses are guarded (ASVS V5): missing keys
    emit ``None`` rather than raising ``KeyError``.

    Parameters
    ----------
    raw : dict
        Native fdars classification result dict.  Keys vary by function:

        - Point-estimate: ``"predicted"`` (int array n,), ``"accuracy"`` (float)
        - ``fclassif_cv``: ``"error_rate"`` (float), ``"fold_errors"`` (array),
          ``"best_ncomp"`` (int)

    n_classes : int, optional
        Ground-truth class count.  Cannot be inferred from the result dict;
        caller supplies it via ``build_diagnostics(..., n_classes=K)``.  When
        ``None`` (default), the ``n_classes`` field in the output is ``None``.
    holdout_accuracy : float, optional
        Caller-supplied holdout or CV accuracy against which to compute the
        overfitting gap.  The ``elastic_multinomial`` result dict carries ONLY
        ``train_accuracy`` — there is NO holdout/CV accuracy in the result, so
        the gap can only be computed when the caller supplies this value (ASPECT-02,
        grounding invariant: the gap MUST come from a real fdars/caller-measured
        value, never fabricated).  When ``None`` (default) the
        ``overfitting_gap`` field is ``None`` (not fabricated).
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``list``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"classification"``
        - n_obs (int or None): number of observations (from predicted length or
          fold_errors length)
        - n_classes (int or None): caller-supplied ground-truth class count
        - accuracy (float or None): proportion correctly classified (point-est)
          or ``1.0 - error_rate`` when only CV result present
        - error_rate (float or None): ``1.0 - accuracy`` for point-estimate
          results
        - cv_error_rate (float or None): CV error rate from ``fclassif_cv``
          (raw key ``"error_rate"``); emitted as ``cv_error_rate`` to
          distinguish from point-estimate accuracy
        - fold_error_std (float or None): std of per-fold errors (CV path)
        - best_ncomp (int or None): number of FPC components minimising CV
          error
    """
    diag: dict = {"method": "classification"}

    # -- n_obs: infer from predicted length or fold_errors length ------------
    if "predicted" in raw:
        n_obs: "int | None" = int(len(np.asarray(raw["predicted"])))
    elif "fold_errors" in raw:
        # CV path: n_obs cannot be determined from folds alone, but we can
        # fall back to None rather than guessing.
        n_obs = None
    else:
        n_obs = None
    diag["n_obs"] = n_obs

    # -- n_classes: explicit caller-supplied parameter; cannot be inferred ---
    diag["n_classes"] = int(n_classes) if n_classes is not None else None

    # -- Point-estimate path: "accuracy" present ------------------------------
    if "accuracy" in raw:
        accuracy = float(raw["accuracy"])
        diag["accuracy"] = accuracy
        diag["error_rate"] = round(1.0 - accuracy, 10)
        # No cv_error_rate in point-estimate results
        diag["cv_error_rate"] = None
    else:
        diag["accuracy"] = None
        diag["error_rate"] = None
        diag["cv_error_rate"] = None

    # -- CV path: "error_rate" present (fclassif_cv's actual key) -----------
    # Correction #2: raw key is "error_rate", emit as "cv_error_rate".
    # Correction #6: guard — fclassif_cv has NO "accuracy" key.
    if "error_rate" in raw:
        cv_error_rate = float(raw["error_rate"])
        diag["cv_error_rate"] = cv_error_rate
        # Derive accuracy from CV error when no point-estimate accuracy present
        if "accuracy" not in raw:
            diag["accuracy"] = round(1.0 - cv_error_rate, 10)

    # -- fold_error_std (CV path) -------------------------------------------
    if "fold_errors" in raw:
        fold_errors = np.asarray(raw["fold_errors"], dtype=float)
        diag["fold_error_std"] = float(np.std(fold_errors))
    else:
        diag["fold_error_std"] = None

    # -- best_ncomp (CV path) -----------------------------------------------
    diag["best_ncomp"] = int(raw["best_ncomp"]) if "best_ncomp" in raw else None

    # -- elastic_multinomial branch (ADV-05 Group B) -------------------------
    # Trigger: "train_accuracy" in raw AND "n_shapelets" NOT in raw.
    # The shapelet_classifier coercion dict ALSO carries "train_accuracy", so
    # we must exclude it here to keep the two discriminators mutually exclusive.
    # Existing point-estimate results use "accuracy" (never "train_accuracy");
    # fclassif_cv uses "error_rate" and "fold_errors".
    # The elastic_multinomial result also carries "n_classes" in the raw dict —
    # override the caller-supplied value with the fdars-computed count.
    has_elastic_multinomial = "train_accuracy" in raw and "n_shapelets" not in raw
    diag["has_elastic_multinomial"] = bool(has_elastic_multinomial)
    if has_elastic_multinomial:
        diag["train_accuracy"] = float(raw["train_accuracy"])
        diag["train_error_rate"] = float(1.0 - raw["train_accuracy"])
        # Override caller-supplied n_classes with the fdars-computed count
        if "n_classes" in raw:
            diag["n_classes"] = int(raw["n_classes"])

        # ASPECT-02 — overfitting gap + class-count flag ----------------------

        # overfitting_gap: train_accuracy minus caller-supplied holdout_accuracy.
        # GROUNDING INVARIANT: the elastic_multinomial result has NO holdout/CV
        # accuracy — it is a caller-measured value.  Emit None when not supplied
        # rather than fabricating a value (T-50B-03).
        train_acc = diag["train_accuracy"]
        if holdout_accuracy is not None:
            diag["overfitting_gap"] = float(train_acc - float(holdout_accuracy))
            diag["overfitting_gap_holdout_source"] = "holdout_accuracy"
        else:
            diag["overfitting_gap"] = None
            diag["overfitting_gap_holdout_source"] = None

        # n_classes_flagged: True when n_classes > 2 (multiclass vs binary).
        # Derived only from the fdars-computed n_classes count; no invented
        # numeric threshold beyond the binary/multiclass structural split.
        n_classes_val = diag["n_classes"]
        if n_classes_val is not None:
            diag["n_classes_flagged"] = bool(n_classes_val > 2)
        else:
            diag["n_classes_flagged"] = None

    else:
        diag["train_accuracy"] = None
        diag["train_error_rate"] = None
        # ASPECT-02 — stable None fields for non-elastic paths
        diag["overfitting_gap"] = None
        diag["overfitting_gap_holdout_source"] = None
        diag["n_classes_flagged"] = None

    # -- shapelet_classifier branch (ADV-01 Phase 72) -----------------------
    # Trigger: "n_shapelets" in raw — unique to shapelet_classifier_fit
    # (converted from opaque PyShapeletClassifierFit handle to dict by the
    # coercion guard in build_diagnostics.__init__.py before dispatch here).
    # CONFIRMED attrs from src/shapelet_mod.rs:123-148.
    has_shapelet_classifier = "n_shapelets" in raw
    diag["has_shapelet_classifier"] = bool(has_shapelet_classifier)
    if has_shapelet_classifier:
        diag["shapelet_n_shapelets"] = int(raw["n_shapelets"])
        diag["shapelet_train_accuracy"] = (
            float(raw["train_accuracy"]) if "train_accuracy" in raw else None
        )
        diag["shapelet_n_classes"] = (
            int(raw["n_classes"]) if raw.get("n_classes") is not None else None
        )
    else:
        diag["shapelet_n_shapelets"] = None
        diag["shapelet_train_accuracy"] = None
        diag["shapelet_n_classes"] = None

    return diag
