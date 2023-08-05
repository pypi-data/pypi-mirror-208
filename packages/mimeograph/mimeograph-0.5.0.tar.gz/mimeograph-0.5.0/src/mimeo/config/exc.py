"""The Mimeo Configuration Exceptions module.

It contains all custom exceptions related to Mimeo Configuration:
    * UnsupportedPropertyValueError
        A custom Exception class for unsupported properties' values.
    * MissingRequiredPropertyError
        A custom Exception class for missing required properties.
    * InvalidIndentError
        A custom Exception class for invalid indent configuration.
    * InvalidVarsError
        A custom Exception class for invalid vars' configuration.
    * InvalidMimeoModelError
        A custom Exception class for invalid model configuration.
    * InvalidMimeoTemplateError
        A custom Exception class for invalid template configuration.
    * InvalidMimeoConfigError
        A custom Exception class for invalid mimeo configuration.
"""


from __future__ import annotations


class UnsupportedPropertyValueError(Exception):
    """A custom Exception class for unsupported properties' values.

    Raised when a Mimeo Configuration property points to a value
    not being supported by Mimeo.
    """

    def __init__(
            self, prop: str, val: str, supported_values: tuple,
    ):
        """Initialize UnsupportedPropertyValueError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        prop : str
            A property name
        val : str
            A property value
        supported_values : tuple
            A list of supported values for the property
        """
        super().__init__(f"Provided {prop} [{val}] is not supported! "
                         f"Supported values: [{', '.join(supported_values)}].")


class MissingRequiredPropertyError(Exception):
    """A custom Exception class for missing required properties.

    Raised when a Mimeo Configuration does not contain a required
    property.
    """


class InvalidIndentError(Exception):
    """A custom Exception class for invalid indent configuration.

    Raised when a configured indent is negative.
    """

    def __init__(
            self,
            indent: int,
    ):
        """Initialize InvalidIndentError exception with details.

        Extends Exception constructor with a custom message.

        Parameters
        ----------
        indent : int
            A configured indent
        """
        super().__init__(f"Provided indent [{indent}] is negative!")


class InvalidVarsError(Exception):
    """A custom Exception class for invalid vars' configuration.

    Raised when vars are not configured properly.
    """


class InvalidMimeoModelError(Exception):
    """A custom Exception class for invalid model configuration.

    Raised when a Mimeo Model is not configured properly.
    """


class InvalidMimeoTemplateError(Exception):
    """A custom Exception class for invalid template configuration.

    Raised when a Mimeo Template is not configured properly.
    """


class InvalidMimeoConfigError(Exception):
    """A custom Exception class for invalid mimeo configuration.

    Raised when a Mimeo Configuration is not configured properly.
    """
