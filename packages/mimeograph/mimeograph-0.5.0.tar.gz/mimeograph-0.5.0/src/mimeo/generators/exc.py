"""The Mimeo Generators Exceptions module.

It contains all custom exceptions related to content of Mimeo Models:
    * UnsupportedStructureError
        A custom Exception class for an unsupported structure.
"""


from __future__ import annotations


class UnsupportedStructureError(Exception):
    """A custom Exception class for an unsupported structure.

    Raised while attempting to generate data from a Mimeo Model having a list
    of non-only atomic / non-only dict items.
    """

    def __init__(
            self,
            field_name: str,
            structure: list,
    ):
        """Initialize UnsupportedStructureError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        field_name : str
            A field name
        structure : list
            An unsupported structure
        """
        super().__init__("An array can include only atomic types (including Mimeo "
                         "Utils) or only JSON objects! Unsupported structure found in "
                         f"{field_name}: {structure}")
