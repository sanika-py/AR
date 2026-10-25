"""Compatibility import for :mod:`backend.core.engine`."""

import sys

from backend.core import engine as _engine

# Preserve old imports and monkeypatch behavior by aliasing the module object.
sys.modules[__name__] = _engine
