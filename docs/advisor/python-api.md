# Python API

The Python advisor surface is **recommend-only**: call `build_diagnostics` to
compute a deterministic, offline diagnostics report from your fdars result, then
call `advise` (or the `describe_cluster_differences` convenience wrapper) to get
a schema-validated `Advice` object with `interpretation`, `recommendations`, and
`caveats`. The API returns `Advice` and stops — it does not re-run fdars or
compute a before/after delta. See the [overview](index.md) for the full picture.

## Worked example

The fence below loads the Canadian Weather dataset, clusters the 35 daily
temperature curves into four groups with `kmeans_fd`, and builds the offline
cluster diagnostics with `build_diagnostics`. No `ANTHROPIC_API_KEY` is
required — the fence runs fully offline in the docs build.

```python exec="1" html="1" source="above"
from docs_data import load_canadian_weather
from fdars.clustering import kmeans_fd
from fdars.advisor import build_diagnostics

day, X, meta = load_canadian_weather("temperature")
result = kmeans_fd(X, day, k=4, seed=42)
diag = build_diagnostics(result, method="clustering", argvals=day)

print(f"k (clusters):              {diag['k']}")
print(f"cluster sizes:             {diag['cluster_sizes']}")
print(f"mean amplitude separation: {diag['mean_amplitude_separation']:.4f}  FDARS_FENCE_OK")
print(f"mean phase separation:     {diag['mean_phase_separation']:.4f}")
```

---

## Functions

### `build_diagnostics`

```
build_diagnostics(result, method, *, argvals=None, **kwargs) -> dict
```

Compute a deterministic, JSON-serialisable diagnostics dict from an fdars result.

**Offline and deterministic** — uses only NumPy and fdars submodules. No
`anthropic` import, no network call, no RNG, no wall-clock dependency. Two calls
on the same input always return an equal dict.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `result` | `dict` or result wrapper | — | Native fdars output dict, or a wrapper whose `.raw` attribute is the underlying dict |
| `method` | `str` | — | The fdars method that produced `result`; one of `"alignment"`, `"fpca"`, `"basis"`, `"smoothing"`, `"clustering"` |
| `argvals` | `array_like` | `None` | Shared evaluation grid, shape `(m,)`. Used for amplitude/phase distance computations |
| `**kwargs` | | | Reserved for future per-method options |

**Returns**

A plain-Python `dict` with JSON-serialisable values (`float`, `list`, `str`,
`bool`, `int`, `None`). No NumPy scalars. Keys depend on `method`:

- `"clustering"` — `k`, `cluster_means`, `cluster_sizes`,
  `pairwise_amplitude_distance`, `pairwise_phase_distance`,
  `mean_amplitude_separation`, `mean_phase_separation`
- `"alignment"` — `mean_length`, `mean_min`, `mean_max`, `mean_avg`, `n_obs`,
  `amplitude_distances`, `phase_distances`, `amplitude_mean`, `amplitude_max`,
  `phase_mean`, `phase_max`, `converged`, `n_iter`
- `"fpca"` — `n_components`, `n_obs`, `eigenvalues`, `explained_variance_ratio`,
  `cumulative_variance_explained`, `total_variance`, `phase_leakage_indicator`,
  `phase_leakage_flagged`
- `"basis"` and `"smoothing"` — GCV curve, optimal value, and EDF keys

**Raises**

`ValueError` if `method` is not in the supported set.

---

### `advise`

```
advise(diagnostics, *, task, domain_context, model="claude-opus-4-8") -> Advice
```

Return a schema-validated `Advice` object by passing `diagnostics` to Claude
with a grounding-invariant system prompt.

Requires the `[advisor]` extra (`pip install fdars[advisor]`). Raises
`ImportError` if the `anthropic` package is not installed.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `diagnostics` | `dict` | — | Output from `build_diagnostics` |
| `task` | `str` | — | Task family: `"interpretation"`, `"parameter"`, or `"method"` |
| `domain_context` | `str` | — | Free-text description of the problem domain, dataset, or analysis goal |
| `model` | `str` | `"claude-opus-4-8"` | Claude model identifier |

**Returns**

`Advice` — schema-validated advice with `interpretation`, `recommendations`, and `caveats`.

---

### `describe_cluster_differences`

```
describe_cluster_differences(
    result,
    *,
    argvals=None,
    domain_context="",
    model="claude-opus-4-8",
    run_llm=True,
    **kwargs,
)
```

Convenience wrapper that runs `build_diagnostics(method="clustering")` (Stage 1,
offline) and optionally `advise(task="interpretation")` (Stage 2, LLM) in
sequence for a clustering result.

**`run_llm=False` offline escape hatch** — when `run_llm=False` the function
returns the raw clustering diagnostics dict with no `anthropic` import and no
network call. This path is fully usable in CI without an API key and is how the
worked example above inspects the feature report.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `result` | `dict` or wrapper | — | fdars clustering result with keys `centers`, `cluster`, `k` |
| `argvals` | `array_like` | `None` | Shared evaluation grid for amplitude/phase distance computation |
| `domain_context` | `str` | `""` | Free-text domain description passed to `advise` |
| `model` | `str` | `"claude-opus-4-8"` | Claude model identifier |
| `run_llm` | `bool` | `True` | When `False`, return the raw diagnostics dict (offline); when `True`, call `advise` and return `Advice` |
| `**kwargs` | | | Forwarded to `build_diagnostics` |

**Returns**

`Advice` when `run_llm=True`; `dict` (raw clustering diagnostics) when `run_llm=False`.

---

## Schema

### `Recommendation`

Each `Advice` object contains a `recommendations` list of `Recommendation`
objects. Every `Recommendation` cites specific diagnostic values in its
`evidence` list — the grounding invariant enforced by the Pydantic schema and
the system prompt.

| Field | Type |
|---|---|
| `action` | `str` |
| `kind` | `Literal["parameter", "method", "none"]` |
| `rationale` | `str` |
| `expected_effect` | `str` |
| `evidence` | `list[str]` |

### `Advice`

| Field | Type |
|---|---|
| `interpretation` | `str` |
| `recommendations` | `list[Recommendation]` |
| `caveats` | `list[str]` |

---

## Recommend-only surface

The Python API is the **recommend-only** surface of the fdars advisor. It
returns an `Advice` object and stops. It does **not** re-run fdars with the
recommended parameters or compute a before/after delta of diagnostic values —
that is the MCP server and Agent Skill surface.

For the full interpret → recommend → re-run → compare agentic loop, see
[MCP Server](mcp.md) *(coming in Phase 16)* and [Agent Skill](agent-skill.md)
*(coming in Phase 17)*.

---

## Illustrative `advise()` call

!!! warning "Requires `ANTHROPIC_API_KEY` — not run in the docs build"
    The fence below is illustrative only. It requires `pip install fdars[advisor]`
    and `ANTHROPIC_API_KEY` to be set. It is **not** an executed fence and does
    not run during the docs build.

```python
from docs_data import load_canadian_weather
from fdars.clustering import kmeans_fd
from fdars.advisor import build_diagnostics, describe_cluster_differences

day, X, meta = load_canadian_weather("temperature")
result = kmeans_fd(X, day, k=4, seed=42)

# Option A: describe_cluster_differences runs both stages in sequence
advice = describe_cluster_differences(
    result,
    argvals=day,
    domain_context=(
        "35 Canadian weather stations clustered by daily temperature curve. "
        "4 climate regions expected: Arctic, Atlantic, Continental, Pacific."
    ),
    run_llm=True,
)

print(advice.interpretation)
for rec in advice.recommendations:
    print(f"[{rec.kind}] {rec.action}")
    for ev in rec.evidence:
        print(f"  evidence: {ev}")
print("caveats:", advice.caveats)

# Option B: build diagnostics first, then call advise directly
diag = build_diagnostics(result, method="clustering", argvals=day)
advice2 = advise(
    diag,
    task="interpretation",
    domain_context="35 Canadian weather stations, 4 climate-region groups.",
    model="claude-opus-4-8",
)
```

A representative `Advice` value returned by `describe_cluster_differences` looks like:

```python
Advice(
    interpretation=(
        "The four clusters show clear amplitude separation "
        "(mean_amplitude_separation ≈ 15.3) driven by the temperature level "
        "difference between Arctic and Pacific stations, with moderate phase "
        "variation (mean_phase_separation ≈ 3.1) reflecting timing shifts in "
        "the seasonal peak."
    ),
    recommendations=[
        Recommendation(
            action="Inspect cluster means to confirm Arctic/Atlantic/Continental/Pacific grouping.",
            kind="none",
            rationale="Cluster sizes [3, 15, 12, 5] match the known regional counts.",
            expected_effect="Confirms that k=4 recovers the four climate regions.",
            evidence=["cluster_sizes=[3, 15, 12, 5]", "mean_amplitude_separation≈15.3"],
        )
    ],
    caveats=["Amplitude and phase distances assume a shared 365-point annual grid."],
)
```
