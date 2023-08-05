"""The Mimeo Meta package.

This package is meant to store all useful classes that are not
essentially related to any Mimeo component.

It contains the following modules:
* alive
    The Alive module.
* exc
    The Mimeo Meta Exceptions module.

The Mimeo Meta package exports the following classes:
- OnlyOneAlive
    A type ensuring there's only one instance qualified to be used.
- Alive
    A superclass for OnlyOneAlive classes.

To use this package, simply import the desired class:
    from mimeo.meta import Alive, OnlyOneAlive
"""
from __future__ import annotations

from .alive import Alive, OnlyOneAlive

__all__ = ["Alive", "OnlyOneAlive"]
