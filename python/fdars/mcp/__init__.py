"""fdars.mcp — MCP (Model Context Protocol) server surface for fdars.

This subpackage requires Python 3.10 or later. The ``mcp`` SDK package
(``mcp>=2.0.0``) uses language features (``match`` statements,
``ExceptionGroup``) that are not available in Python 3.9.

Install the extra to use this subpackage::

    pip install fdars[mcp]

Note
----
The ``fdars.mcp`` subpackage is **not** registered in ``fdars.__init__`` and
is never imported by a plain ``import fdars``. Users import it explicitly::

    from fdars.mcp.server import mcp
    from fdars.mcp._registry import registry
"""

import sys as _sys

if _sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

# Deferred imports — only reached on Python 3.10+.
from fdars.mcp._registry import HandleRegistry, registry  # noqa: E402
from fdars.mcp import server  # noqa: E402

__all__ = ["HandleRegistry", "registry", "server"]
