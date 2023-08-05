"""The Mimeo package.

This package provides the Mimeo functionality with the highest level
class together with the Mimeo Configuration class:
* MimeoConfig
    A class representing Mimeo Configuration.
* Mimeograph
    A class responsible for the Mimeo processing.

It includes __main__.py module to provide a Command Line Interface
for the Mimeo.

This package is not meant to be used directly on low-level classes.
That's why we do not recommend importing particular packages, that are
internally used by Mimeograph:
* cli
    The Mimeo CLI package
* config
    The Mimeo Configuration package
* consumers
    The Mimeo Consumers package
* context
    The Mimeo Context package
* database
    The Mimeo Database package
* generators
    The Mimeo Generators package
* logging
    The Mimeo Logging package
* meta
    The Mimeo Meta package
* resources
    The Mimeo Resources package
* utils
    The Mimeo Utils package

The same apply to the following modules included by the Mimeo package:
* mimeo
    The Mimeo module
* tools
    The Mimeo Tools module

To use this package, simply import the desired classes:
    from mimeo import MimeoConfig, Mimeograph
"""
from __future__ import annotations

from .config import MimeoConfig
from .mimeo import Mimeograph

__version__ = "0.5.0"
__all__ = ["MimeoConfig", "Mimeograph"]
