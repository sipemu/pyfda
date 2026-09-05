---
phase: 74-deepen-regression-family-thin-pages
reviewed: 2026-09-05T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - scripts/run_page_fences.py
  - docs/regression/frechet-regression.md
  - docs/regression/function-on-function.md
  - docs/regression/additive-sof.md
  - docs/regression/concurrent-regression.md
  - docs/regression/functional-glm.md
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: resolved
resolution: All 5 findings (WR-01, WR-02, IN-01, IN-02, IN-03) fixed 2026-09-05; fence gates re-run green including WR-01 preset-PYTHONPATH check.
---

# Phase 74: Code Review Report

**Reviewed:** 2026-09-05
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Phase 74 deepened five regression-family pages from 20–35% parity to full parity, and
introduced `scripts/run_page_fences.py` as a new offline fence-verification tool. API
accuracy was the primary concern; all six known discrepancies catalogued in RESEARCH.md
(frechet_anova signature/defaults/return-keys, predict_fof arg order, fof_cv parameter
names, fam defaults, model_selection_ncomp `max_comp`, variable_selection 9 keys) were
correctly fixed in the delivered pages. No stale API references remain.

Two warnings were found: a `setdefault` call in `run_page_fences.py` that silently
drops the `scripts/` directory from `PYTHONPATH` when the user has an existing
`PYTHONPATH` set (causing `ImportError` on `docs_fig` for all `html="1"` fences), and
a missing `encoding` argument on `read_text()` that can corrupt multi-byte characters
on non-UTF-8 systems. Three info items were found: two dead imports in a fence body
and one non-idiomatic sentinel embedding.

---

## Warnings

### WR-01: `PYTHONPATH` set with `setdefault` silences `scripts/` when env is pre-populated

**File:** `scripts/run_page_fences.py:39`
**Issue:** `env.setdefault("PYTHONPATH", "scripts")` only sets `PYTHONPATH` when the
key is **absent** from the environment. If the calling shell already has `PYTHONPATH`
set (e.g., from a conda environment, a virtualenv activation, or a CI matrix that
adds project paths), the `scripts/` directory is **not** added. Every `html="1"` fence
on all five pages imports `from docs_fig import fig, render` — those fences will then
fail with `ModuleNotFoundError: No module named 'docs_fig'`, and the script reports
failure for the wrong reason with no clear diagnostic.

All five reviewed pages have at least one `html="1"` exec fence that imports `docs_fig`,
so this affects every page when run in a pre-populated environment.

**Fix:**
```python
# Replace line 39:
env.setdefault("PYTHONPATH", "scripts")

# With:
existing = env.get("PYTHONPATH", "")
env["PYTHONPATH"] = os.pathsep.join(filter(None, ["scripts", existing]))
```

This always prepends `scripts/` so `docs_fig` is importable regardless of any
pre-existing `PYTHONPATH`.

---

### WR-02: `page.read_text()` without explicit `encoding` can corrupt non-ASCII content

**File:** `scripts/run_page_fences.py:32`
**Issue:** `page.read_text()` uses the system default encoding, which is locale-dependent.
On systems where `locale` is not `UTF-8` (e.g., certain CI images, Windows with default
codepage), reading `frechet-regression.md` — which contains `é` in "Fréchet" and `ε` in
LaTeX — will either raise `UnicodeDecodeError` or silently corrupt the source. The
corrupted source then produces malformed fence bodies that fail to parse or execute.

**Fix:**
```python
# Line 32 — replace:
src = page.read_text()

# With:
src = page.read_text(encoding="utf-8")
```

---

## Info

### IN-01: Dead imports in `additive-sof.md` figure fence body

**File:** `docs/regression/additive-sof.md:393-394`
**Issue:** Inside the `exec="1" html="1"` fence (Section 8, "Figure: Partial-Effect
Curves from FAM"), two import statements are present but neither identifier is ever
referenced in the fence body:

```python
from fdars.scalar_on_function import fam as _fam   # _fam never used
import fdars.scalar_on_function as _sof             # _sof never used
```

`fam` was already imported on line 378 (without alias), and the `result` variable on
line 389 was produced by that earlier import. The two dead imports are leftover from an
intermediate authoring draft and execute unnecessary module imports at docs-build time.

**Fix:** Remove lines 393–394 from the fence body entirely. The fence runs correctly
without them.

---

### IN-02: Sentinel embedded inside f-string output in `frechet-regression.md` fence 0

**File:** `docs/regression/frechet-regression.md:107`
**Issue:** Fence 0 (the `frechet_mean` SPD example) mixes the `FDARS_FENCE_OK` sentinel
into a longer f-string rather than printing it on its own line:

```python
print(f"positive diagonal: {mean_spd[0, 0] > 0} {mean_spd[1, 1] > 0}  FDARS_FENCE_OK")
```

This produces rendered docs output reading `positive diagonal: True True  FDARS_FENCE_OK`,
which looks like a typo or debugging artifact to a reader of the built page. Every other
exec fence across all five pages (21 in total) uses the canonical standalone form
`print("FDARS_FENCE_OK")`. Mixing the sentinel into assertion output also means that if
the fence fails silently (no exception but wrong result), the sentinel still appears in
stdout and `run_page_fences.py` passes incorrectly.

`run_page_fences.py` only checks `SENTINEL in proc.stdout` (a substring check), so the
fence currently passes. But the correctness check on the diagonal positivity is not
independently verifiable from the tool output.

**Fix:**
```python
# Replace line 107:
print(f"positive diagonal: {mean_spd[0, 0] > 0} {mean_spd[1, 1] > 0}  FDARS_FENCE_OK")

# With:
print(f"positive diagonal: {mean_spd[0, 0] > 0} {mean_spd[1, 1] > 0}")
print("FDARS_FENCE_OK")
```

---

### IN-03: `run_page_fences.py` leaks temp file if `subprocess.run` raises an OS exception

**File:** `scripts/run_page_fences.py:44-54`
**Issue:** The temp file is created with `delete=False`, written, then passed to
`subprocess.run()`. The `os.unlink(path)` call on line 50 runs unconditionally after
`subprocess.run()` returns — but if `subprocess.run()` itself raises an OS-level
exception (e.g., `OSError: [Errno 8] Exec format error` if the interpreter path is
wrong, or an out-of-memory condition), the `unlink` is skipped and the temp `.py` file
is orphaned in the system temp directory.

In practice this only matters in failure scenarios, but it is straightforward to harden.

**Fix:**
```python
# Wrap the subprocess.run and cleanup in try/finally:
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
    fh.write(body)
    path = fh.name
try:
    proc = subprocess.run(
        [sys.executable, path], capture_output=True, text=True, env=env
    )
finally:
    os.unlink(path)
if proc.returncode != 0 or SENTINEL not in proc.stdout:
    ...
```

---

_Reviewed: 2026-09-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
