"""
Main Plugin API
"""

from typing import Callable, Optional

from commitguard.config import Config
from commitguard.precommit.run import ReportProgress
from commitguard.terminal import bold_info, error, fail, info, ok, out, warning

__all__ = [
    "Config",
    "ReportProgress",
    "error",
    "fail",
    "info",
    "bold_info",
    "ok",
    "out",
    "warning",
]
