"""The Mimeo Consumers package.

It contains modules supporting the Mimeo Config output directions:
* consumer
    The Mimeo Consumer module.
* consumer_factory
    The Mimeo Consumer Factory module.
* raw_consumer
    The Mimeo Raw Consumer module.
* file_consumer
    The Mimeo File Consumer module.
* http_consumer
    The Mimeo HTTP Consumer module.

This package exports the following classes:
* Consumer:
    An abstract class for data consumers in Mimeo.
* ConsumerFactory:
    A Factory class instantiating a Consumer based on Mimeo Config.
* RawConsumer:
    A Consumer implementation printing data in the standard output.
    Corresponds to the 'stdout' output direction
* FileConsumer:
    A Consumer implementation saving data in the filesystem.
    Corresponds to the 'file' output direction
* HttpConsumer:
    A Consumer implementation sending data in HTTP requests.
    Corresponds to the 'http' output direction

To use this package, simply import the desired class:
    from mimeo.consumers import ConsumerFactory
"""

from .consumer import Consumer
from .file_consumer import FileConsumer
from .raw_consumer import RawConsumer
from .http_consumer import HttpConsumer
from .consumer_factory import ConsumerFactory

__all__ = ["Consumer", "FileConsumer", "RawConsumer", "HttpConsumer", "ConsumerFactory"]
