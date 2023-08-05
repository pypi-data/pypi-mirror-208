"""The Mimeo Database package.

This package exposes databases support required by Mimeo Utils.

It contains the following modules:
* mimeo_db
    The Mimeo Database module.
* cities
    The Cities module.
* countries
    The Countries module.
* first_names
    The First Names module.
* last_names
    The Last Names module.
* exc
    The Mimeo Database Exceptions module.

The Mimeo Context package exports the following classes:
* MimeoDB
    Facade class exposing READ operations on all Mimeo CSV data.
* CitiesDB
    Class exposing READ operations on cities CSV data.
* CountriesDB
    Class exposing READ operations on countries CSV data.
* FirstNamesDB
    Class exposing READ operations on forenames CSV data.
* LastNamesDB
    Class exposing READ operations on surnames CSV data.
* City
    DTO class representing a single row in cities CSV data.
* Country
    DTO class representing a single row in countries CSV data.
* FirstName
    DTO class representing a single row in forenames CSV data.

To use this package, simply import the desired class:
    from mimeo.database import MimeoDB
    from mimeo.database.exc import DataNotFoundError
"""
from __future__ import annotations

from .cities import CitiesDB, City
from .countries import CountriesDB, Country
from .first_names import FirstName, FirstNamesDB
from .last_names import LastNamesDB
from .mimeo_db import MimeoDB

__all__ = [
    "City",
    "Country",
    "FirstName",
    "CitiesDB",
    "CountriesDB",
    "FirstNamesDB",
    "LastNamesDB",
    "MimeoDB",
]
