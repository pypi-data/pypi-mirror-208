"""Language features module

The `__future__` module is used by other Python implementations to
enable forward compatibility for features enabled by default in an upcoming version.
"""

from __future__ import annotations

from typing import Any

annotations: Any
"""In CPython, ``from __future import annotations``
indicates that evaluation of annotations is postponed, as described in PEP 563.
CircuitPython (and MicroPython) ignore annotations entirely, whether or not this feature is imported.
This is a limitation of CircuitPython and MicroPython for efficiency reasons.
"""
