"""The Last Names module.

It exports a class related to surnames CSV data:
    * LastNamesDB
        Class exposing READ operations on surnames CSV data.
"""
from __future__ import annotations

from mimeo import tools
from mimeo.database.exc import InvalidIndexError


class LastNamesDB:
    """Class exposing READ operations on surnames CSV data.

    Attributes
    ----------
    NUM_OF_RECORDS : int
        A number of rows in surnames CSV data

    Methods
    -------
    get_last_names() -> list[str]
        Get all last names.
    get_last_name_at(index: int) -> str
        Get a last name at `index` position.
    """

    NUM_OF_RECORDS = 151670
    _LAST_NAMES_DB = "surnames.txt"
    _LAST_NAMES = None

    def get_last_name_at(
            self,
            index: int,
    ) -> str:
        """Get a last name at `index` position.

        Parameters
        ----------
        index : int
            A last name row index

        Returns
        -------
        str
            A last name

        Raises
        ------
        InvalidIndexError
            If the provided `index` is out of bounds
        """
        last_names = self.__get_last_names()
        try:
            return last_names[index]
        except IndexError:
            last_index = LastNamesDB.NUM_OF_RECORDS-1
            raise InvalidIndexError(index, last_index) from IndexError

    @classmethod
    def get_last_names(
            cls,
    ) -> list[str]:
        """Get all last names.

        Returns
        -------
        list[str]
            List of all last names
        """
        return cls.__get_last_names().copy()

    @classmethod
    def __get_last_names(
            cls,
    ) -> list:
        """Get all last names from cache.

        The last names list is initialized for the first time and
        cached in internal class attribute.

        Returns
        -------
        list[str]
            List of all last names
        """
        if cls._LAST_NAMES is None:
            with tools.get_resource(LastNamesDB._LAST_NAMES_DB) as last_names:
                cls._LAST_NAMES = [line.rstrip() for line in last_names.readlines()]
        return cls._LAST_NAMES
