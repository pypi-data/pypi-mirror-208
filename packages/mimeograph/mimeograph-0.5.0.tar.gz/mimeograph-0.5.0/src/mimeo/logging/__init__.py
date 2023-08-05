"""The Mimeo Logging package.

It contains helpful modules to customize logs produced by Mimeo:
* filters
    The Mimeo Logging Filters module.

This package exports the following classes:
* RegularFilter:
    A Filter subclass filtering out log records below INFO level.
* DetailedFilter:
    A Filter subclass filtering out log records above DEBUG level.

It also includes a single function to set up logging in the application:
* setup_logging
    Set up customized logging configuration.

To use this package, simply import the desired class or function:
    from mimeo.logging import RegularFilter
    from mimeo.logging import setup_logging
"""
from __future__ import annotations

import logging.config

import yaml
from haggis.logs import add_logging_level

from mimeo import tools

from .filters import DetailedFilter, RegularFilter

__all__ = ["DetailedFilter", "RegularFilter", "setup_logging"]


def setup_logging():
    """Set up customized logging configuration.

    The configuration is stored in the logging.yaml file in
    the resources package. Besides that a new log level is defined,
    FINE, together with a method logger.fine().
    """
    add_logging_level("FINE", logging.DEBUG - 1)
    with tools.get_resource("logging.yaml") as config_file:
        config = yaml.safe_load(config_file.read())
        logging.config.dictConfig(config)
