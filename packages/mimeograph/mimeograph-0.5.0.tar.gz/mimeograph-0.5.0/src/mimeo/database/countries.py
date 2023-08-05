"""The Countries module.

It exports classes related to countries CSV data:
    * Country
        DTO class representing a single row in countries CSV
        data.
    * CountriesDB
        Class exposing READ operations on countries CSV data.
"""
from __future__ import annotations

import pandas

from mimeo import tools
from mimeo.database.exc import InvalidIndexError


class Country:
    """DTO class representing a single row in cities CSV data.

    Attributes
    ----------
    iso_3 : str
        A country ISO3 code
    iso_2 : str
        A country ISO2 code
    name : str
        A country name
    """

    def __init__(
            self,
            iso_3: str,
            iso_2: str,
            name: str,
    ):
        """Initialize Country class.

        Parameters
        ----------
        iso_3 : str
            A country ISO3 code
        iso_2 : str
            A country ISO2 code
        name : str
            A country name
        """
        self.iso_3 = iso_3
        self.iso_2 = iso_2
        self.name = name

    def __str__(
            self,
    ) -> str:
        """Stringify the Country instance.

        Returns
        -------
        str
            A stringified `dict` representation of the Country instance
        """
        return str({
            "iso_3": self.iso_3,
            "iso_2": self.iso_2,
            "name": self.name,
        })

    def __repr__(
            self,
    ) -> str:
        """Represent the Country instance.

        Returns
        -------
        str
            A python representation of the Country instance
        """
        return (f"Country("
                f"iso_3='{self.iso_3}', "
                f"iso_2='{self.iso_2}', "
                f"name='{self.name}')")


class CountriesDB:
    """Class exposing READ operations on countries CSV data.

    Attributes
    ----------
    NUM_OF_RECORDS : int
        A number of rows in countries CSV data

    Methods
    -------
    get_countries() -> list[Country]
        Get all countries.
    get_country_at(index: int) -> Country
        Get a country at `index` position.
    get_country_by_iso_3(iso_3: str) -> Country
        Get a country having a specific ISO3 code.
    get_country_by_iso_3(iso_2: str) -> Country
        Get a country having a specific ISO2 code.
    get_country_by_name(name: str) -> Country
        Get a country having a specific name.
    """

    NUM_OF_RECORDS = 239
    _COUNTRIES_DB = "countries.csv"
    _COUNTRIES_DF = None
    _COUNTRIES = None

    def get_country_at(
            self,
            index: int,
    ) -> Country:
        """Get a country at `index` position.

        Parameters
        ----------
        index : int
            A country row index

        Returns
        -------
        Country
            A specific country

        Raises
        ------
        InvalidIndexError
            If the provided `index` is out of bounds
        """
        countries = self._get_countries()
        try:
            return countries[index]
        except IndexError:
            last_index = CountriesDB.NUM_OF_RECORDS-1
            raise InvalidIndexError(index, last_index) from IndexError

    def get_country_by_iso_3(
            self,
            iso_3: str,
    ) -> Country:
        """Get a country having a specific ISO3 code.

        Parameters
        ----------
        iso_3 : str
            An ISO3 code to find a country

        Returns
        -------
        Country
            A specific country or None
        """
        countries = self._get_countries()
        return next(filter(lambda country: country.iso_3 == iso_3, countries), None)

    def get_country_by_iso_2(
            self,
            iso_2: str,
    ) -> Country:
        """Get a country having a specific ISO2 code.

        Parameters
        ----------
        iso_2 : str
            An ISO2 code to find a country

        Returns
        -------
        Country
            A specific country or None
        """
        countries = self._get_countries()
        return next(filter(lambda country: country.iso_2 == iso_2, countries), None)

    def get_country_by_name(
            self,
            name: str,
    ) -> Country:
        """Get a country having a specific name.

        Parameters
        ----------
        name : str
            A name to find a country

        Returns
        -------
        Country
            A specific country or None
        """
        countries = self._get_countries()
        return next(filter(lambda country: country.name == name, countries), None)

    @classmethod
    def get_countries(
            cls,
    ) -> list[Country]:
        """Get all countries.

        Returns
        -------
        list[Country]
            List of all countries
        """
        return cls._get_countries().copy()

    @classmethod
    def _get_countries(
            cls,
    ) -> list[Country]:
        """Get all countries from cache.

        The countries list is initialized for the first time and cached
        in internal class attribute.

        Returns
        -------
        list[Country]
            List of all countries
        """
        if cls._COUNTRIES is None:
            cls._COUNTRIES = [Country(row.ISO_3, row.ISO_2, row.NAME)
                              for row in cls._get_countries_df().itertuples()]
        return cls._COUNTRIES

    @classmethod
    def _get_countries_df(
            cls,
    ) -> pandas.DataFrame:
        """Load countries CSV data and save in internal class attribute."""
        if cls._COUNTRIES_DF is None:
            data = tools.get_resource(CountriesDB._COUNTRIES_DB)
            cls._COUNTRIES_DF = pandas.read_csv(data)
        return cls._COUNTRIES_DF
