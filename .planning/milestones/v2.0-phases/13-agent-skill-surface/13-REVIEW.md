---
phase: 13-agent-skill-surface
reviewed: 2026-08-10T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - .claude/skills/fdars-advisor/SKILL.md
  - .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py
  - tests/test_skill.py
findings:
  critical: 3
  warning: 4
  info: 2
  total: 9
status: issues_found
---

# Phase 13: Code Review Report

**Reviewed:** 2026-08-10
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Three files were reviewed: the agentskills.io manifest (SKILL.md), the offline
walkthrough script (fdars_advisor_walkthrough.py), and the test suite
(test_skill.py). The manifest is structurally sound. The walkthrough script has
two blockers: a guaranteed `TypeError` crash on the GCV/EDF print lines when the
keys are absent (the sentinel `'n/a'` is passed to `:.6f`), and the test that
is supposed to verify a non-empty delta block contains a false-positive path
that passes even when the delta is completely empty. The third blocker is in
`advisor.py`: `_require_anthropic()` crashes with an unhandled `ValueError`
when the installed `anthropic` package carries a non-dot-separated pre-release
suffix (e.g. `0.72.0rc1`). Four warnings cover duplicate subprocess runs,
the Anthropic API call parameters that do not match the documented SDK surface,
the `allowed-tools` field type mismatch in SKILL.md, and the missing teardown
of the singleton registry in the test suite.

---

## Critical Issues

### CR-01: `TypeError` crash on GCV/EDF print when keys are absent

**File:** `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py:93-94`

**Issue:** `before_result.get('gcv', 'n/a')` returns the string `'n/a'` when
the key is absent. That string is then formatted with `:.6f`, which raises
`TypeError: unsupported format character` at runtime. The `pspline_fit_gcv`
result dict does include `gcv` and `edf` for a successful run, so the crash
is latent rather than guaranteed today — but if the upstream fdars API ever
renames or drops those keys, or a future test exercises a method that returns
a different dict shape, the script exits non-zero and the offline walkthrough
promise is broken.

```python
# Current (crashes if key is absent):
print(f"  GCV (before): {before_result.get('gcv', 'n/a'):.6f}")
print(f"  EDF (before): {before_result.get('edf', 'n/a'):.4f}")

# Fix: guard the format specifier on the actual value type
gcv = before_result.get('gcv')
edf = before_result.get('edf')
print(f"  GCV (before): {gcv:.6f}" if gcv is not None else "  GCV (before): n/a")
print(f"  EDF (before): {edf:.4f}" if edf is not None else "  EDF (before): n/a")
```

---

### CR-02: `test_walkthrough_delta_nonempty` gives a false pass when the delta is empty

**File:** `tests/test_skill.py:147-153`

**Issue:** The test asserts that at least one value line exists after the
"Delta (" header by filtering `splitlines()[1:]` for lines containing `": "`.
However the script unconditionally prints `"No fabrication: every delta value
is fdars-computed."` (walkthrough.py line 154) after the delta block. That
line contains `": "`. When the delta dict is empty the script instead prints
`"    (no scalar finite keys in common)"` — which does not contain `": "` —
but the fabrication disclaimer line that follows does. So `lines_after` has
length >= 1 and the assertion passes even though the delta block is empty.
This defeats the purpose of the test entirely.

```python
# Current (false-positive):
lines_after = [ln for ln in remainder.splitlines()[1:] if ": " in ln]
assert len(lines_after) >= 1, ...

# Fix: filter to lines that match the actual delta value format:
# "    <key>: [+-]<number>" — require a digit after the colon and space.
import re as _re
lines_after = [
    ln for ln in remainder.splitlines()[1:]
    if _re.search(r":\s+[+\-]?\d", ln)
]
assert len(lines_after) >= 1, (
    f"Delta block is empty — expected >=1 numeric value lines after header.\n"
    f"stdout after header: {remainder!r}"
)
```

---

### CR-03: `_require_anthropic()` crashes with `ValueError` on pre-release version strings

**File:** `python/fdars/advisor.py:767-772`

**Issue:** The version check splits `anthropic.__version__` on `.` and calls
`int()` on each of the first three parts. A version string like `"0.72.0rc1"`
(no dot before the suffix) splits as `['0', '72', '0rc1']`; `int('0rc1')`
raises `ValueError`, crashing the import guard with an unhandled exception
instead of a clear `ImportError`. Pre-release wheels are common in environments
where developers pin to a release candidate ahead of a stable release.

```python
# Current (crashes on rc/alpha/beta suffixes without a dot separator):
installed = tuple(
    int(x) for x in anthropic.__version__.split(".")[:3]
)

# Fix: strip non-numeric trailing characters from each part before conversion
import re as _re

def _parse_version(v: str) -> tuple[int, ...]:
    parts = v.split(".")[:3]
    result = []
    for p in parts:
        m = _re.match(r"(\d+)", p)
        result.append(int(m.group(1)) if m else 0)
    return tuple(result)

installed = _parse_version(anthropic.__version__)
floor = _parse_version(ADVISOR_ANTHROPIC_MIN_VERSION)
```

---

## Warnings

### WR-01: `test_walkthrough_script_offline` and `test_walkthrough_delta_nonempty` each spawn a full subprocess — 2x the cost for no additional coverage

**File:** `tests/test_skill.py:99-118` and `tests/test_skill.py:121-154`

**Issue:** Both tests run the complete walkthrough script as a subprocess
with identical environment (ANTHROPIC_API_KEY stripped, same interpreter).
`test_walkthrough_delta_nonempty` already checks `result.returncode == 0`
before inspecting stdout, so it is a strict superset of
`test_walkthrough_script_offline`. On a cold build with no cached fdars
results each subprocess run may take 30-120 seconds, doubling CI time for
no gain.

**Fix:** Share the subprocess result using a session-scoped fixture, or
merge the exit-code and delta assertions into a single test. The simplest
approach is a module-level fixture:

```python
@pytest.fixture(scope="module")
def _walkthrough_result():
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True, text=True, timeout=120, env=env,
    )

def test_walkthrough_script_offline(_walkthrough_result):
    assert _walkthrough_result.returncode == 0, ...

def test_walkthrough_delta_nonempty(_walkthrough_result):
    # reuse _walkthrough_result
    ...
```

---

### WR-02: `advisor.py` calls `client.messages.parse` with `thinking={"type": "adaptive"}` — neither the method nor the parameter match the documented Anthropic SDK surface

**File:** `python/fdars/advisor.py:991-997`

**Issue:** The Anthropic Python SDK (as of 0.72.0) exposes structured output
via `client.messages.create` with `response_format` (or tool-use extraction),
not via `client.messages.parse(..., output_format=...)`. The attribute
`messages.parse` and the keyword argument `output_format` appear to be
fictitious: the actual parsing API uses `client.messages.create` plus a
`tools`-based extraction pattern, or (in the beta structured-output API)
`client.beta.messages.parse`. Similarly, `thinking={"type": "adaptive"}` is
not a documented parameter name; the extended-thinking API uses
`thinking={"type": "enabled", "budget_tokens": N}`. If this code is exercised
with a real API key it will raise `AttributeError` or `TypeError` at runtime.

**Fix:** Align with the actual SDK surface. If the intent is extended thinking
plus structured output use the beta endpoint:

```python
# Use the beta structured-output endpoint (SDK >= 0.40 with betas)
response = client.beta.messages.parse(
    model=model,
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 8000},
    system=system,
    output_format=Advice,
    messages=[{"role": "user", "content": user_content}],
    betas=["interleaved-thinking-2025-05-14"],
)
```

Verify against the exact SDK version pinned in ADVISOR_ANTHROPIC_MIN_VERSION
before shipping.

---

### WR-03: `allowed-tools` in SKILL.md frontmatter is a scalar string, not a YAML list

**File:** `.claude/skills/fdars-advisor/SKILL.md:19`

**Issue:** The agentskills.io schema expects `allowed-tools` to be a YAML
sequence. The current value `Bash Read` (unquoted, space-separated) is parsed
by PyYAML as the single string `"Bash Read"`, not as `["Bash", "Read"]`.
Discovery tooling that iterates `allowed-tools` as a list will silently treat
`"Bash Read"` as a single unknown tool name or iterate over characters.

```yaml
# Current (string):
allowed-tools: Bash Read

# Fix (YAML list):
allowed-tools:
  - Bash
  - Read
```

---

### WR-04: Singleton `registry` is never cleared between tests — state leakage risk

**File:** `tests/test_skill.py` (module level; no conftest.py present)

**Issue:** The walkthrough script calls `registry.clear()` at the top of
`main()` (walkthrough.py line 67), which is correct for an in-process call.
However the subprocess-based tests in `test_skill.py` each launch a fresh
interpreter, so the risk there is low. But if any future test in this file
imports and calls `run_method` or `compare_run` directly (in-process, without
going through the subprocess path), the module-level singleton `registry` will
accumulate handles across tests. There is no `conftest.py` fixture calling
`registry.clear()` in teardown. The `_registry.py` docstring explicitly calls
this out as "Pitfall 3" and states "Tests call `registry.clear()` in a teardown
fixture to prevent state leakage."

**Fix:** Add a `conftest.py` with an autouse fixture:

```python
# tests/conftest.py
import pytest
from fdars.mcp._registry import registry

@pytest.fixture(autouse=True)
def _clear_registry():
    registry.clear()
    yield
    registry.clear()
```

---

## Info

### IN-01: `test_skill_md_compatibility` passes with a very weak signal — any mention of "Python" or "3.10" suffices

**File:** `tests/test_skill.py:183-188`

**Issue:** The assertion `"3.10" in compat or "Python" in compat` passes if
`compat` contains the word "Python" with no version number at all. This makes
the test nearly impossible to fail for any real SKILL.md. A tighter check
would require both the version floor and the install command to be present.

**Fix:**
```python
assert "3.10" in compat, f"'compatibility' must mention Python 3.10+: {compat!r}"
assert "pip" in compat or "install" in compat, ...
```

---

### IN-02: Walkthrough script module-level docstring says "requires Python >=3.10" but the SKILL.md compatibility field says "Python 3.10+" — both are correct but the wording diverges

**File:** `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py:17` and `.claude/skills/fdars-advisor/SKILL.md:13`

**Issue:** Minor wording inconsistency: the script docstring uses `>=3.10` and
the SKILL.md uses `3.10+`. These are equivalent but a reader skimming the docs
may wonder if one is a typo. Standardising on one form across both artifacts
removes the ambiguity. No functional impact.

**Fix:** Align both to `Python 3.10+` (the SKILL.md convention), or pick
`>=3.10` (the Python packaging convention) and apply it consistently.

---

_Reviewed: 2026-08-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
