"""The Mimeo Database Exceptions module.

It contains all custom exceptions related to Mimeo Context:
    * InvalidIndexError
        A custom Exception class for invalid row index.
    * InvalidSexError
        A custom Exception class for uninitialized context's iteration.
    * CountryNotFound
        A custom Exception class for not found context's iteration.
    * OutOfStockError
        A custom Exception class for invalid special field's name.
"""


from __future__ import annotations


class InvalidIndexError(Exception):
    """A custom Exception class for invalid row index.

    Raised while attempting to get data at row that does not exist.
    """

    def __init__(
            self,
            index: int,
            last_index: int,
    ):
        """Initialize InvalidIndexError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        index : int
            An invalid index
        last_index : str
            The last existing index
        """
        msg = f"Provided index [{index}] is out or the range: 0-{last_index}!"
        super().__init__(msg)


class InvalidSexError(Exception):
    """A custom Exception class for invalid sex.

    Raised when sex provided to filter forenames is not supported.
    """

    def __init__(
            self,
            supported_sex_list: tuple,
    ):
        """Initialize InvalidSexError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        supported_sex_list : int
            A list of supported sex values
        """
        super().__init__(f"Invalid sex (use {' / '.join(supported_sex_list)})!")


class DataNotFoundError(Exception):
    """A custom Exception class for not found data.

    Raised while attempting to filter data by a column's value that
    does not match any row.
    """


class OutOfStockError(Exception):
    """A custom Exception class for consuming all data.

    Raised while attempting to get next unique value when all were
    consumed already.
    """
