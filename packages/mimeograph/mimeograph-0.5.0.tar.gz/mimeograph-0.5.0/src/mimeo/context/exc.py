"""The Mimeo Context Exceptions module.

It contains all custom exceptions related to Mimeo Context:
    * MinimumIdentifierReachedError
        A custom Exception class for reaching minimum identifier.
    * UninitializedContextIterationError
        A custom Exception class for uninitialized context's iteration.
    * ContextIterationNotFoundError
        A custom Exception class for not found context's iteration.
    * InvalidSpecialFieldNameError
        A custom Exception class for invalid special field's name.
    * InvalidSpecialFieldValueError
        A custom Exception class for invalid special field's value.
    * SpecialFieldNotFoundError
        A custom Exception class for not found special field.
    * VarNotFoundError
        A custom Exception class for not found var.
"""
from __future__ import annotations


class MinimumIdentifierReachedError(Exception):
    """A custom Exception class for reaching minimum identifier.

    Raised when using MimeoContext.prev_id() method and id is equal to
    0.
    """

    def __init__(
            self,
    ):
        """Initialize MinimumIdentifierReachedError exception with details.

        Extends Exception constructor with a constant message.
        """
        super().__init__("There's no previous ID!")


class UninitializedContextIterationError(Exception):
    """A custom Exception class for uninitialized context's iteration.

    Raised while attempting to access the current iteration without
    prior initialization.
    """

    def __init__(
            self,
            context_name: str,
    ):
        """Initialize UninitializedContextIterationError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        context_name : str
            A current context name
        """
        msg = ("No iteration has been initialized "
               f"for the current context [{context_name}]")
        super().__init__(msg)


class ContextIterationNotFoundError(Exception):
    """A custom Exception class for not found context's iteration.

    Raised while attempting to access an iteration that does not exist.
    """

    def __init__(
            self,
            iteration_id: int,
            context_name: str,
    ):
        """Initialize ContextIterationNotFoundError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        iteration_id : int
            A current context name
        context_name : str
            A current context name
        """
        msg = (f"No iteration with id [{iteration_id}] "
               f"has been initialized for the current context [{context_name}]")
        super().__init__(msg)


class InvalidSpecialFieldNameError(Exception):
    """A custom Exception class for invalid special field's name.

    Raised while attempting to save a special field and provided name
    is not a string value.
    """

    def __init__(
            self,
    ):
        """Initialize InvalidSpecialFieldNameError exception with details.

        Extends Exception constructor with a constant message.
        """
        super().__init__("A special field name needs to be a string value!")


class InvalidSpecialFieldValueError(Exception):
    """A custom Exception class for invalid special field's value.

    Raised while attempting to save a special field and provided value
    is non-atomic one.
    """

    def __init__(
            self,
            field_value: dict | list,
    ):
        """Initialize InvalidSpecialFieldValueError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        field_value : dict | list
            A special field value
        """
        msg = f"Provided field value [{field_value}] is invalid (use any atomic value)!"
        super().__init__(msg)


class SpecialFieldNotFoundError(Exception):
    """A custom Exception class for not found special field.

    Raised while attempting to access a special field that does not
    exist.
    """

    def __init__(
            self,
            field_name: str,
    ):
        """Initialize SpecialFieldNotFoundError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        field_name : str
            A special field name
        """
        super().__init__(f"Special Field [{field_name}] has not been found!")


class VarNotFoundError(Exception):
    """A custom Exception class for not found var.

    Raised while attempting to access a variable that does not exist.
    """

    def __init__(
            self,
            variable_name: str,
    ):
        """Initialize VarNotFoundError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        variable_name : str
            A variable name
        """
        super().__init__(f"Provided variable [{variable_name}] is not defined!")
