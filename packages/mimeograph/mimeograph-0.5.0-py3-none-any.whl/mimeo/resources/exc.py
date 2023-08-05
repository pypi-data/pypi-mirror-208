"""The Mimeo Resources Exceptions module.

It contains all custom exceptions related to Mimeo resources:
    * ResourceNotFound
        A custom Exception class for a not found resource.
"""


from __future__ import annotations


class ResourceNotFoundError(Exception):
    """A custom Exception class for a not found resource.

    Raised while attempting to get a resource that does exist.
    """

    def __init__(
            self,
            resource_name: str,
    ):
        """Initialize ResourceNotFoundError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        resource_name : str
            A resource name
        """
        super().__init__(f"No such resource: [{resource_name}]")
