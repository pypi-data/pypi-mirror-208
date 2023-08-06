"""Functions to manage environment variables from a .env file.

   A subset of the CPython `dotenv library <https://saurabh-kumar.com/python-dotenv/>`_. It does
   not support variables or double quotes.

   The simplest way to define keys and values is to put them in single quotes. \ and ' are
   escaped by \ in single quotes. Newlines can occur in quotes for multiline values. Comments
   start with # and apply for the rest of the line.

   File format example:

   .. code-block::

       key=value
         key2 = value2
       'key3' = 'value with spaces'
       # comment
       key4 = value3 # comment 2
       'key5'=value4
       key=value5 # overrides the first one
       multiline = 'hello
       world
       how are you?'

"""

from __future__ import annotations

import typing
from typing import Optional

def get_key(dotenv_path: str, key_to_get: str) -> Optional[str]:
    """Get the value for the given key from the given .env file. If the key occurs multiple
    times in the file, then the last value will be returned.

    Returns None if the key isn't found or doesn't have a value."""
    ...

def load_dotenv() -> None:
    """Does nothing in CircuitPython because os.getenv will automatically read .env when
    available.

    Present in CircuitPython so CPython-compatible code can use it without error."""
    ...
