"""Compatibility import for :mod:`backend.core.signals`."""

import sys

from backend.core import signals as _signals

sys.modules[__name__] = _signals
