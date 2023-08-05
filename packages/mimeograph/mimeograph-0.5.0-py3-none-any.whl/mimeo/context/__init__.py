"""The Mimeo Context package.

This package provides support fot Mimeo-Template-dependent utilities.

It contains the following modules:
* mimeo_context_manager
    The Mimeo Context Manager module.
* mimeo_context
    The Mimeo Context module.
* mimeo_iteration
    The Mimeo Iteration module.
* decorators
    The Mimeo Context Decorators module.
* exc
    The Mimeo Context Exceptions module.

The Mimeo Context package exports the following classes:
- MimeoIteration:
    A class representing a single iteration in a Mimeo Template.
- MimeoContext:
    A class managing Mimeo-Template-dependent utilities.
- MimeoContextManager:
    An OnlyOneAlive class managing Mimeo Contexts.

To use this package, simply import the desired class:
    from mimeo.context import MimeoContextManager
"""
from .mimeo_iteration import MimeoIteration
from .mimeo_context import MimeoContext
from .mimeo_context_manager import MimeoContextManager

__all__ = ["MimeoIteration", "MimeoContext", "MimeoContextManager"]
