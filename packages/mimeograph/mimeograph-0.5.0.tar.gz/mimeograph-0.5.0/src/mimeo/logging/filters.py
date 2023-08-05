"""The Mimeo Logging Filters module.

This module contains all filters used in logging.
It exports the following filters:
    * RegularFilter
        A Filter subclass filtering out log records below INFO level.
    * DetailedFilter
        A Filter subclass filtering out log records above DEBUG level.
"""
from __future__ import annotations

from logging import DEBUG, INFO, Filter, LogRecord


class RegularFilter(Filter):
    """A Filter subclass filtering out log records below INFO level.

    It is meant to be used for logging info in regular format.

    Methods
    -------
    filter(record: LogRecord)
        Determine if the specified record is to be logged.
    """

    def filter(
            self,
            record: LogRecord,
    ) -> bool:
        """Determine if the specified record is to be logged.

        Parameters
        ----------
        record : LogRecord
            A log record

        Returns
        -------
        bool
            True if the log record's level is at least INFO
        """
        return record.levelno >= INFO


class DetailedFilter(Filter):
    """A Filter subclass filtering out log records above DEBUG level.

    It is meant to be used for logging info in detailed format.

    Methods
    -------
    filter(record: LogRecord)
        Determine if the specified record is to be logged.
    """

    def filter(
            self,
            record: LogRecord,
    ):
        """Determine if the specified record is to be logged.

        Parameters
        ----------
        record : LogRecord
            A log record

        Returns
        -------
        bool
            True if the log record's level is at most DEBUG
        """
        return record.levelno <= DEBUG
