"""The Mimeo CLI package.

It contains the following modules:
* job
    The Mimeo Job module.
* parsers
    The Mimeo Parser module.
* exc
    The Mimeo CLI Exceptions module.

The Mimeo CLI package exports classes responsible for preparation and executing a Mimeo
processing job from the command line:
* MimeoJob
    A class representing a single Mimeo processing job.
* MimeoArgumentParser
    A custom ArgumentParser for the Mimeo CLI.
* MimeoConfigParser
    A class parsing source Mimeo Configuration with Mimeo arguments.

To use this package, simply import it:
    from mimeo.cli import MimeoJob
"""
from .parsers import MimeoArgumentParser, MimeoConfigParser
from .job import MimeoJob

__all__ = ["MimeoJob", "MimeoArgumentParser", "MimeoConfigParser"]
