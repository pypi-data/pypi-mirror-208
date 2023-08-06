"""
A module for exposing useful information from the current system to templates.
"""

# built-in
from functools import lru_cache
import platform
import sys
from typing import Any, Dict


@lru_cache(maxsize=1)
def system_data() -> Dict[str, Any]:
    """Obtain useful system configuration data."""

    return {
        "sys": {
            "base_exec_prefix": sys.base_exec_prefix,
            "base_prefix": sys.base_prefix,
            "byteorder": sys.byteorder,
            "exec_prefix": sys.exec_prefix,
            "executable": sys.executable,
            "platform": sys.platform,
            "prefix": sys.prefix,
            "version": sys.version,
        },
        "platform": {
            "bits": platform.architecture()[0],
            "linkage": platform.architecture()[1],
            "machine": platform.machine(),
            "node": platform.node(),
            "processor": platform.processor(),
            "implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "release": platform.release(),
            "system": platform.system(),
            "version": platform.version(),
        },
    }
