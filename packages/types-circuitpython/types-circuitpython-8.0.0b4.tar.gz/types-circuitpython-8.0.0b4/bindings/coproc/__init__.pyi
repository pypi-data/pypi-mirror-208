"""COPROC Module

The `coproc` module adds ability to load and run
programs on a co-processor or a different cpu core.

.. code-block:: python

    import coproc

    shared_mem = coproc.CoprocMemory(address=0x500007fc, length=1024)

    with open("program.bin", "rb") as f:
        program = coproc.Coproc(buffer=f.read(), memory=shared_mem)

    coproc.run(program)
    print(coproc.memory(program)[0])
    # coproc.halt(program)
"""

from __future__ import annotations

from typing import overload

from circuitpython_typing import ReadableBuffer

...

def run(*coproc: Coproc) -> None:
    """Runs the loaded program."""
    ...

def halt(*coproc: Coproc) -> None:
    """Halts the loaded program."""
    ...

def memory(*coproc: Coproc) -> CoprocMemory:
    """Returns the shared memory as a bytearray."""
    ...

class Coproc:
    def __init__(self, buffer: ReadableBuffer, memory: CoprocMemory) -> None:
        """Loads the program binary into memory.

        :param buffer: The program binary to run on the core/co-processor
        :param memory: The `CoprocMemory` object used to access shared memory"""
    def deinit(self) -> None:
        """Releases control of the underlying hardware so other classes can use it."""
        ...
    def __enter__(self) -> Coproc:
        """No-op used in Context Managers."""
        ...
    def __exit__(self) -> None:
        """Close the request."""
        ...

class CoprocMemory:
    def __init__(self, address: int, length: int) -> None:
        """Initialize coproc shared memory.

        :param address: address of shared memory
        :param length: length of shared memory"""
    def __bool__(self) -> bool:
        """``coproc_memory`` is ``True`` if its length is greater than zero.
        This is an easy way to check for its existence.
        """
        ...
    def __len__(self) -> int:
        """Return the length. This is used by (`len`)"""
        ...
    @overload
    def __getitem__(self, index: slice) -> bytearray: ...
    @overload
    def __getitem__(self, index: int) -> int:
        """Returns the value at the given index."""
        ...
    @overload
    def __setitem__(self, index: slice, value: ReadableBuffer) -> None: ...
    @overload
    def __setitem__(self, index: int, value: int) -> None:
        """Set the value at the given index."""
        ...
