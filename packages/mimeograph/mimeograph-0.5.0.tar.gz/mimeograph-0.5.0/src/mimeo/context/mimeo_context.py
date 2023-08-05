"""The Mimeo Context module.

It exports only one class:
    * MimeoContext
        A class managing Mimeo-Template-dependent utilities.
"""
from __future__ import annotations

import random

from mimeo.context import MimeoIteration
from mimeo.context.exc import (ContextIterationNotFoundError,
                               MinimumIdentifierReachedError,
                               UninitializedContextIterationError)
from mimeo.database import MimeoDB
from mimeo.database.exc import DataNotFoundError, OutOfStockError


class MimeoContext:
    """A class managing Mimeo-Template-dependent utilities.

    It allows you to reach a specific iteration of a template
    generation, and ensures uniqueness of all values generated
    by Mimeo Utils (and supporting this feature). Giving access
    to all iterations, it allows you to get a key or any special field
    of them.

    Attributes
    ----------
    name : str
        A context name (a model's root name if not explicitly
        defined in a Mimeo Configuration)

    Methods
    -------
    next_id() -> int
        Increment an identifier and return the current (incremented) one.
    curr_id() -> int
        Return the current identifier within the context.
    prev_id() -> int
        Decrement an identifier and return the current (decremented) one.
    next_iteration() -> MimeoIteration
        Initialize a next iteration within the context.
    curr_iteration() -> MimeoIteration
        Return the current iteration within the context.
    get_iteration(iteration_id: int) -> MimeoIteration
        Return a specific iteration from the context.
    clear_iterations()
        Clear out all context iterations.
    next_country_index() -> int
        Provide next unique country index.
    next_city_index(country: str = None) -> int
        Provide next unique city index.
    next_first_name_index(sex: str = None) -> int
        Provide next unique first name index.
    next_last_name_index() -> int
        Provide next unique last name index.
    """

    _ALL = "_ALL_"
    _INITIAL_COUNT = "init-count"
    _INDEXES = "indexes"

    def __init__(
            self,
            name: str,
    ):
        """Initialize MimeoContext class.

        Parameters
        ----------
        name : str
            A context name
        """
        self.name = name
        self._id = 0
        self._iterations = []
        self._countries_indexes = None
        self._cities_indexes = {}
        self._first_names_indexes = {}
        self._last_names_indexes = None

    def next_id(
            self,
    ) -> int:
        """Increment an identifier and return the current (incremented) one.

        Identifier is used by Auto Increment Mimeo Util.

        Returns
        -------
        int
            A next identifier within the context
        """
        self._id += 1
        return self.curr_id()

    def curr_id(
            self,
    ) -> int:
        """Return the current identifier within the context.

        Identifier is used by Auto Increment Mimeo Util.

        Returns
        -------
        int
            The current identifier within the context
        """
        return self._id

    def prev_id(
            self,
    ) -> int:
        """Decrement an identifier and return the current (decremented) one.

        Identifier is used by Auto Increment Mimeo Util.
        This method is meant to be used when an error appear
        after incrementation.

        Returns
        -------
        int
            A previous identifier within the context

        Raises
        ------
        MinimumIdentifierReachedError
            If the current identifier (before decrement) equals 0
        """
        if self._id == 0:
            raise MinimumIdentifierReachedError
        self._id -= 1
        return self.curr_id()

    def next_iteration(
            self,
    ) -> MimeoIteration:
        """Initialize a next iteration within the context.

        To initialize the iteration, it gets the last iteration id and
        provides its incrementation.

        Returns
        -------
        next_iteration : MimeoIteration
            The initialized iteration
        """
        if len(self._iterations) == 0:
            next_iteration_id = 1
        else:
            next_iteration_id = self._iterations[-1].id + 1
        next_iteration = MimeoIteration(next_iteration_id)
        self._iterations.append(next_iteration)
        return next_iteration

    def curr_iteration(
            self,
    ) -> MimeoIteration:
        """Return the current iteration within the context.

        Returns
        -------
        int
            The current iteration within the context

        Raises
        ------
        UninitializedContextIterationError
            If no iteration has been initialized yet for the context
        """
        if len(self._iterations) == 0:
            raise UninitializedContextIterationError(self.name)
        return self._iterations[-1]

    def get_iteration(
            self,
            iteration_id: int,
    ) -> MimeoIteration:
        """Return a specific iteration from the context.

        Returns
        -------
        int
            A specific iteration

        Raises
        ------
        ContextIterationNotFoundError
            If the context does not have an iteration with the id
            provided
        """
        iteration = next(filter(lambda i: i.id == iteration_id, self._iterations), None)
        if iteration is None:
            raise ContextIterationNotFoundError(iteration_id, self.name)
        return iteration

    def clear_iterations(
            self,
    ):
        """Clear out all context iterations.

        This method is meant to be used in case of nested templates.
        Thanks to iteration reset the nested template is properly
        generated in context of the next parent template's iteration.
        """
        self._iterations = []

    def next_country_index(
            self,
    ) -> int:
        """Provide next unique country index.

        When used for the first time in the specific context
        it populates internal countries' indexes list. This approach
        ensures country uniqueness without time-consuming operations.
        Each time it verifies if the internal list still contains some
        indexes.
        This method is used by the Country Mimeo Util to get a country
        entry at a specific index in database.

        Returns
        -------
        int
            Next unique country identifier

        Raises
        ------
        OutOfStockError
            If all countries' indexes have been consumed already
        """
        self._initialize_countries_indexes()
        self._validate_countries()

        return self._countries_indexes.pop()

    def next_city_index(
            self,
            country: str = None,
    ) -> int:
        """Provide next unique city index.

        When used for the first time in the specific context
        it populates internal cities' indexes map. Each `country` key
        has its own list initialized as same as country-agnostic one.
        This approach ensures city uniqueness without time-consuming
        operations. Each time it verifies if the internal list still
        contains some indexes.
        This method is used by the City Mimeo Util to get a city entry
        at a specific index in database.

        Parameters
        ----------
        country : str, default _ALL_
            A country limitation to find cities. When None - all
            countries are considered.

        Returns
        -------
        int
            Next unique city identifier

        Raises
        ------
        CountryNotFound
            If database does not contain any cities for the provided
            `country`
        OutOfStockError
            If all cities' indexes have been consumed already
        """
        country = country if country is not None else MimeoContext._ALL
        self._initialize_cities_indexes(country)
        self._validate_cities(country)

        return self._cities_indexes[country][MimeoContext._INDEXES].pop()

    def next_first_name_index(
            self,
            sex: str = None,
    ) -> int:
        """Provide next unique first name index.

        When used for the first time in the specific context
        it populates internal first names' indexes map. Each `sex` key
        has its own list initialized as same as sex-agnostic one.
        This approach ensures forename uniqueness without
        time-consuming operations. Each time it verifies if the internal
        list still contains some indexes.
        This method is used by the First Name Mimeo Util to get a
        first name entry at a specific index in database.

        Parameters
        ----------
        sex : str, default _ALL_
            A sex limitation to find names. When None - both
            sexes are considered.

        Returns
        -------
        int
            Next unique first name identifier

        Raises
        ------
        InvalidSexError
            If `sex` is not 'M' nor 'F' value
        OutOfStockError
            If all first names' indexes have been consumed already
        """
        sex = sex if sex is not None else MimeoContext._ALL
        self._initialize_first_names_indexes(sex)
        self._validate_first_names(sex)

        return self._first_names_indexes[sex][MimeoContext._INDEXES].pop()

    def next_last_name_index(
            self,
    ) -> int:
        """Provide next unique last name index.

        When used for the first time in the specific context
        it populates internal last names' indexes list. This approach
        ensures surnames uniqueness without time-consuming operations.
        Each time it verifies if the internal list still contains some
        indexes.
        This method is used by the Last Name Mimeo Util to get a
        last name entry at a specific index in database.

        Returns
        -------
        int
            Next unique last name identifier

        Raises
        ------
        OutOfStockError
            If all last names' indexes have been consumed already
        """
        self._initialize_last_names_indexes()
        self._validate_last_names()

        return self._last_names_indexes.pop()

    def _initialize_countries_indexes(
            self,
    ):
        """Initialize countries' indexes with unique integers.

        The list length and range depends on the number of country
        records in database.
        """
        if self._countries_indexes is None:
            num_of_entries = MimeoDB.NUM_OF_COUNTRIES
            countries_indexes = random.sample(range(num_of_entries), num_of_entries)
            self._countries_indexes = countries_indexes

    def _initialize_cities_indexes(
            self,
            country: str,
    ):
        """Initialize cities' indexes with unique integers.

        The list length and range depends on the number of city
        records in database for the `country`.

        Raises
        ------
        CountryNotFound
            If database does not contain any cities for the provided
            `country`
        """
        if country not in self._cities_indexes:
            if country == MimeoContext._ALL:
                num_of_entries = MimeoDB.NUM_OF_CITIES
            else:
                country_cities = MimeoDB().get_cities_of(country)
                num_of_entries = len(country_cities)
                if num_of_entries == 0:
                    msg = (f"Mimeo database doesn't contain any cities "
                           f"of provided country [{country}].")
                    raise DataNotFoundError(msg)

            cities_indexes = random.sample(range(num_of_entries), num_of_entries)
            self._cities_indexes[country] = {
                MimeoContext._INITIAL_COUNT: num_of_entries,
                MimeoContext._INDEXES: cities_indexes,
            }

    def _initialize_first_names_indexes(
            self,
            sex: str,
    ):
        """Initialize first names' indexes with integers.

        The list length and range depends on the number of first name
        records in database for the `sex`.

        Raises
        ------
        InvalidSexError
            If `sex` is not 'M' nor 'F' value
        """
        if sex not in self._first_names_indexes:
            if sex == MimeoContext._ALL:
                num_of_entries = MimeoDB.NUM_OF_FIRST_NAMES
            else:
                first_names_for_sex = MimeoDB().get_first_names_by_sex(sex)
                num_of_entries = len(first_names_for_sex)

            first_names_indexes = random.sample(range(num_of_entries), num_of_entries)
            self._first_names_indexes[sex] = {
                MimeoContext._INITIAL_COUNT: num_of_entries,
                MimeoContext._INDEXES: first_names_indexes,
            }

    def _initialize_last_names_indexes(
            self,
    ):
        """Initialize last names' indexes with unique integers.

        The list length and range depends on the number of last name
        records in database.
        """
        if self._last_names_indexes is None:
            num_of_entries = MimeoDB.NUM_OF_LAST_NAMES
            last_names_indexes = random.sample(range(num_of_entries), num_of_entries)
            self._last_names_indexes = last_names_indexes

    def _validate_countries(
            self,
    ):
        """Verify if all countries' indexes have been consumed.

        Raises
        ------
        OutOfStockError
            If all countries' indexes have been consumed already
        """
        if len(self._countries_indexes) == 0:
            msg = (f"No more unique values, "
                   f"database contain only {MimeoDB.NUM_OF_COUNTRIES} countries.")
            raise OutOfStockError(msg)

    def _validate_cities(
            self,
            country: str,
    ):
        """Verify if all cities' indexes have been consumed.

        Raises
        ------
        OutOfStockError
            If all cities' indexes have been consumed already
        """
        if len(self._cities_indexes[country][MimeoContext._INDEXES]) == 0:
            init_count = self._cities_indexes[country][MimeoContext._INITIAL_COUNT]
            if country == MimeoContext._ALL:
                msg = (f"No more unique values, "
                       f"database contain only {init_count} cities.")
            else:
                msg = (f"No more unique values, "
                       f"database contain only {init_count} cities of {country}.")
            raise OutOfStockError(msg)

    def _validate_first_names(
            self,
            sex: str,
    ):
        """Verify if all first names' indexes have been consumed.

        Raises
        ------
        OutOfStockError
            If all first names' indexes have been consumed already
        """
        if len(self._first_names_indexes[sex][MimeoContext._INDEXES]) == 0:
            init_count = self._first_names_indexes[sex][MimeoContext._INITIAL_COUNT]
            if sex == MimeoContext._ALL:
                msg = (f"No more unique values, "
                       f"database contain only {init_count} first names.")
            else:
                sex_info = "male" if sex == "M" else "female"
                msg = (f"No more unique values, "
                       f"database contain only {init_count} {sex_info} first names.")
            raise OutOfStockError(msg)

    def _validate_last_names(
            self,
    ):
        """Verify if all last names' indexes have been consumed.

        Raises
        ------
        OutOfStockError
            If all last names' indexes have been consumed already
        """
        if len(self._last_names_indexes) == 0:
            msg = (f"No more unique values, "
                   f"database contain only {MimeoDB.NUM_OF_LAST_NAMES} last names.")
            raise OutOfStockError(msg)
