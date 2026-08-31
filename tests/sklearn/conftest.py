"""conftest.py for the fdars sklearn test suite.

Skips the entire tests/sklearn/ tree when scikit-learn is not installed
(i.e. when the [sklearn] extra is absent).

This guarantees that the base fdars package can be tested without scikit-learn
installed while still failing loudly when [sklearn] is present but broken.
"""

import pytest

pytest.importorskip("sklearn", reason="[sklearn] extra not installed")
