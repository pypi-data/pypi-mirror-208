"""The Mimeo Tools module.

It is meant to store all useful functions that can help in any
non-Mimeo-specific operations. It exports the following functions:
    * get_resource(resource_name: str) -> TextIO
        Return a Mimeo resource.
"""
from __future__ import annotations

import importlib.resources as pkg_resources
from typing import TextIO

from mimeo import resources as data
from mimeo.resources.exc import ResourceNotFoundError


def get_resource(
        resource_name: str,
) -> TextIO:
    """Return a Mimeo resource.

    The resource needs to be included in mimeo.resources package
    to be returned.

    Parameters
    ----------
    resource_name : str
        A Mimeo resource name

    Returns
    -------
    TextIO
        A Mimeo resource

    Raises
    ------
    ResourceNotFound
        If the resource does not exist
    """
    try:
        return pkg_resources.open_text(data, resource_name)
    except FileNotFoundError:
        raise ResourceNotFoundError(resource_name) from FileNotFoundError
