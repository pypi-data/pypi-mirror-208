"""The Mimeo Generators package.

It contains modules supporting the Mimeo Config output formats:
* generator
    The Mimeo Generator module.
* generator_factory
    The Mimeo Generator Factory module.
* xml_generator
    The Mimeo XML Generator module.
* exc
    The Mimeo Generators Exceptions module.

This package exports the following classes:
* Generator:
    An abstract class for data generators in Mimeo.
* GeneratorFactory:
    A Factory class instantiating a Generator based on Mimeo Config.
* XMLGenerator:
    A Generator implementation producing data in the XML format.
    Corresponds to the 'xml' output format

To use this package, simply import the desired class:
    from mimeo.generators import GeneratorFactory
    from mimeo.generators.exc import UnsupportedStructureError
"""
from .generator import Generator
from .xml_generator import XMLGenerator
from .generator_factory import GeneratorFactory

__all__ = ["Generator", "XMLGenerator", "GeneratorFactory"]
