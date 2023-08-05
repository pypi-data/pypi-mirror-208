"""The Mimeo Configuration module.

It contains classes representing Mimeo Configuration components
at all levels. All of them are Data Transfer Objects:
    * MimeoDTO
        A superclass for all Mimeo configuration DTOs
    * MimeoConfig
        A MimeoDTO class representing Mimeo Configuration
    * MimeoOutput
        A MimeoDTO class representing Mimeo Output Details
    * MimeoTemplate
        A MimeoDTO class representing Mimeo Template
    * MimeoModel
        A MimeoDTO class representing Mimeo Model
"""
from __future__ import annotations

import re

from mimeo.config.exc import (InvalidIndentError, InvalidMimeoConfigError,
                              InvalidMimeoModelError,
                              InvalidMimeoTemplateError, InvalidVarsError,
                              MissingRequiredPropertyError,
                              UnsupportedPropertyValueError)
from mimeo.logging import setup_logging

# setup logging when mimeo is used as a python library
setup_logging()


class MimeoDTO:
    """A superclass for all Mimeo configuration DTOs.

    It is meant to store a source dictionary for logging purposes.

    Methods
    -------
    __str__
        Return the stringified source dictionary of a DTO.
    """

    def __init__(
            self, source: dict,
    ):
        """Initialize MimeoDTO class.

        Parameters
        ----------
        source : dict
            The source dictionary for a Mimeo DTO
        """
        self._source = source

    def __str__(
            self,
    ):
        """Return the stringified source dictionary of a DTO."""
        return str(self._source)


class MimeoConfig(MimeoDTO):
    """A MimeoDTO class representing Mimeo Configuration.

    It is a python representation of a Mimeo Configuration file / dictionary.

    Attributes
    ----------
    OUTPUT_KEY : str
        A Mimeo Configuration output details key
    OUTPUT_DIRECTION_KEY : str
        A Mimeo Configuration output direction key
    OUTPUT_FORMAT_KEY : str
        A Mimeo Configuration output format key
    OUTPUT_XML_DECLARATION_KEY : str
        A Mimeo Configuration xml declaration key
    OUTPUT_INDENT_KEY : str
        A Mimeo Configuration indent key
    OUTPUT_DIRECTORY_PATH_KEY : str
        A Mimeo Configuration output directory path key
    OUTPUT_FILE_NAME_KEY : str
        A Mimeo Configuration output file name key
    OUTPUT_METHOD_KEY : str
        A Mimeo Configuration http method key
    OUTPUT_PROTOCOL_KEY : str
        A Mimeo Configuration http protocol key
    OUTPUT_HOST_KEY : str
        A Mimeo Configuration http host key
    OUTPUT_PORT_KEY : str
        A Mimeo Configuration http port key
    OUTPUT_ENDPOINT_KEY : str
        A Mimeo Configuration http endpoint key
    OUTPUT_USERNAME_KEY : str
        A Mimeo Configuration http username key
    OUTPUT_PASSWORD_KEY : str
        A Mimeo Configuration http password key
    VARS_KEY : str
        A Mimeo Configuration vars key
    TEMPLATES_KEY : str
        A Mimeo Configuration templates key
    TEMPLATES_COUNT_KEY : str
        A Mimeo Configuration template's count key
    TEMPLATES_MODEL_KEY : str
        A Mimeo Configuration template's model key
    MODEL_CONTEXT_KEY : str
        A Mimeo Configuration model's context name key
    MODEL_ATTRIBUTES_KEY : str
        A Mimeo Configuration attributes key (for nodes' attributes)
    MODEL_VALUE_KEY : str
        A Mimeo Configuration value key (for nodes' value)
    MODEL_MIMEO_UTIL_KEY : str
        A Mimeo Configuration Mimeo Util key
    MODEL_MIMEO_UTIL_NAME_KEY : str
        A Mimeo Configuration Mimeo Util's name key
    SUPPORTED_OUTPUT_FORMATS : set
        A set of supported output formats
    OUTPUT_DIRECTION_FILE : str
        The 'file' output direction
    OUTPUT_DIRECTION_STD_OUT : str
        The 'stdout' output direction
    OUTPUT_DIRECTION_HTTP : str
        The 'http' output direction
    OUTPUT_DIRECTION_HTTP_REQUEST_POST : str
        The 'POST' http request method
    OUTPUT_DIRECTION_HTTP_REQUEST_PUT : str
        The 'PUT' http request method
    SUPPORTED_OUTPUT_DIRECTIONS : set
        List of supported output directions
    SUPPORTED_REQUEST_METHODS : set
        List of supported http request methods
    REQUIRED_HTTP_DETAILS : set
        List of required http request output direction details

    output : MimeoOutput, default {}
        A Mimeo Output Details settings
    vars : dict, default {}
        A Mimeo Configuration vars setting
    templates : list
        A Mimeo Templates setting
    """

    OUTPUT_KEY = "output"
    OUTPUT_DIRECTION_KEY = "direction"
    OUTPUT_FORMAT_KEY = "format"
    OUTPUT_XML_DECLARATION_KEY = "xml_declaration"
    OUTPUT_INDENT_KEY = "indent"
    OUTPUT_DIRECTORY_PATH_KEY = "directory_path"
    OUTPUT_FILE_NAME_KEY = "file_name"
    OUTPUT_METHOD_KEY = "method"
    OUTPUT_PROTOCOL_KEY = "protocol"
    OUTPUT_HOST_KEY = "host"
    OUTPUT_PORT_KEY = "port"
    OUTPUT_ENDPOINT_KEY = "endpoint"
    OUTPUT_USERNAME_KEY = "username"
    OUTPUT_PASSWORD_KEY = "password"
    VARS_KEY = "vars"
    TEMPLATES_KEY = "_templates_"
    TEMPLATES_COUNT_KEY = "count"
    TEMPLATES_MODEL_KEY = "model"
    MODEL_CONTEXT_KEY = "context"
    MODEL_ATTRIBUTES_KEY = "_attrs"
    MODEL_VALUE_KEY = "_value"
    MODEL_MIMEO_UTIL_KEY = "_mimeo_util"
    MODEL_MIMEO_UTIL_NAME_KEY = "_name"

    OUTPUT_FORMAT_XML = "xml"

    OUTPUT_DIRECTION_FILE = "file"
    OUTPUT_DIRECTION_STD_OUT = "stdout"
    OUTPUT_DIRECTION_HTTP = "http"

    OUTPUT_DIRECTION_HTTP_REQUEST_POST = "POST"
    OUTPUT_DIRECTION_HTTP_REQUEST_PUT = "PUT"

    SUPPORTED_OUTPUT_FORMATS = (OUTPUT_FORMAT_XML,)

    SUPPORTED_OUTPUT_DIRECTIONS = (OUTPUT_DIRECTION_STD_OUT,
                                   OUTPUT_DIRECTION_FILE,
                                   OUTPUT_DIRECTION_HTTP)
    SUPPORTED_REQUEST_METHODS = (OUTPUT_DIRECTION_HTTP_REQUEST_POST,
                                 OUTPUT_DIRECTION_HTTP_REQUEST_PUT)
    REQUIRED_HTTP_DETAILS = (OUTPUT_HOST_KEY,
                             OUTPUT_ENDPOINT_KEY,
                             OUTPUT_USERNAME_KEY,
                             OUTPUT_PASSWORD_KEY)

    def __init__(
            self,
            config: dict,
    ):
        """Initialize MimeoConfig class.

        Extends MimeoDTO constructor.

        Parameters
        ----------
        config : dict
            A source config dictionary
        """
        super().__init__(config)
        self.output = MimeoOutput(config.get(self.OUTPUT_KEY, {}))
        self.vars = self._get_vars(config)
        self.templates = self._get_templates(config)

    @classmethod
    def _get_vars(
            cls,
            config: dict,
    ) -> dict:
        """Extract variables from the source dictionary.

        Parameters
        ----------
        config : dict
            A source config dictionary

        Returns
        -------
        variables : dict
            Customized variables or an empty dictionary

        Raises
        ------
        InvalidVarsError
            If (1) the vars key does not point to a dictionary or
            (2) some variable's name does not start with a letter,
            is not SNAKE_UPPER_CASE with possible digits or
            (3) some variable's value points to non-atomic value nor Mimeo Util
        """
        variables = config.get(MimeoConfig.VARS_KEY, {})
        if not isinstance(variables, dict):
            msg = f"vars property does not store an object: {variables}"
            raise InvalidVarsError(msg)
        for var, val in variables.items():
            if not re.match(r"^[A-Z][A-Z_0-9]*$", var):
                msg = (f"Provided var [{var}] is invalid "
                       f"(you can use upper-cased name with underscore and digits, "
                       f"starting with a letter)!")
                raise InvalidVarsError(msg)
            if isinstance(val, (list, dict)) and not cls._is_mimeo_util_object(val):
                msg = (f"Provided var [{var}] is invalid "
                       f"(you can use ony atomic values and Mimeo Utils)!")
                raise InvalidVarsError(msg)
        return variables

    @classmethod
    def _get_templates(
            cls,
            config: dict,
    ) -> list:
        """Extract Mimeo Templates from the source dictionary.

        Parameters
        ----------
        config : dict
            A source config dictionary

        Returns
        -------
        list
            A Mimeo Templates list

        Raises
        ------
        IncorrectMimeoConfig
            If (1) the source dictionary does not include the _templates_ key or
            (2) the _templates_ key does not point to a list
        """
        templates = config.get(cls.TEMPLATES_KEY)
        if templates is None:
            msg = f"No templates in the Mimeo Config: {config}"
            raise InvalidMimeoConfigError(msg)
        if not isinstance(templates, list):
            msg = f"_templates_ property does not store an array: {config}"
            raise InvalidMimeoConfigError(msg)
        return [MimeoTemplate(template)
                for template in config.get(cls.TEMPLATES_KEY)]

    @classmethod
    def _is_mimeo_util_object(
            cls,
            obj: dict,
    ) -> bool:
        """Verify if the object is a Mimeo Util.

        Parameters
        ----------
        obj : dict
            An object to verify

        Returns
        -------
        bool
            True if the object is a dictionary having only one key: _mimeo_util.
            Otherwise, False.
        """
        return (isinstance(obj, dict) and
                len(obj) == 1 and
                cls.MODEL_MIMEO_UTIL_KEY in obj)


class MimeoOutput(MimeoDTO):
    """A MimeoDTO class representing Mimeo Output Details.

    It is a python representation of a Mimeo Output Details configuration node.

    Attributes
    ----------
    direction : str, default 'file'
        The configured output direction
    format : str, default 'xml'
        A Mimeo Configuration output format setting
    xml_declaration : bool, default False
        A Mimeo Configuration xml declaration setting
    indent : int, default 0
        A Mimeo Configuration indent setting
    directory_path : str, default 'mimeo-output'
        The configured file output directory
    file_name : str, default 'mimeo-output-{}.{output_format}'
        The configured file output file name template
    method : str, default POST
        The configured http output request method
    protocol : str, default 'http'
        The configured http output protocol
    host : str
        The configured http output host
    port : str
        The configured http output port
    endpoint : str
        The configured http output endpoint
    auth : str, default 'basic'
        The configured http output auth method
    username : str
        The configured http output username
    password : str
        The configured http output password
    """

    def __init__(
            self,
            output: dict,
    ):
        """Initialize MimeoOutput class.

        Extends MimeoDTO constructor.

        Parameters
        ----------
        output : dict
            A source config output details dictionary
        """
        super().__init__(output)
        self.direction = self._get_direction(output)
        self._validate_output(self.direction, output)
        self.format = self._get_format(output)
        self.xml_declaration = output.get(MimeoConfig.OUTPUT_XML_DECLARATION_KEY, False)
        self.indent = self._get_indent(output)
        self.directory_path = self._get_directory_path(self.direction, output)
        self.file_name = self._get_file_name(self.direction, output, self.format)
        self.method = self._get_method(self.direction, output)
        self.protocol = self._get_protocol(self.direction, output)
        self.host = self._get_host(self.direction, output)
        self.port = self._get_port(self.direction, output)
        self.endpoint = self._get_endpoint(self.direction, output)
        self.username = self._get_username(self.direction, output)
        self.password = self._get_password(self.direction, output)

    @staticmethod
    def _get_direction(
            output: dict,
    ) -> str:
        """Extract output direction from the source dictionary.

        Parameters
        ----------
        output : dict
            A source config output details dictionary

        Returns
        -------
        direction : str
            The configured output direction

        Raises
        ------
        UnsupportedPropertyValueError
            If the configured output direction is not supported
        """
        direction = output.get(
            MimeoConfig.OUTPUT_DIRECTION_KEY,
            MimeoConfig.OUTPUT_DIRECTION_FILE)
        if direction not in MimeoConfig.SUPPORTED_OUTPUT_DIRECTIONS:
            raise UnsupportedPropertyValueError(
                MimeoConfig.OUTPUT_DIRECTION_KEY,
                direction,
                MimeoConfig.SUPPORTED_OUTPUT_DIRECTIONS)
        return direction

    @staticmethod
    def _get_format(
            config: dict,
    ) -> str:
        """Extract an output format from the source dictionary.

        Parameters
        ----------
        config : dict
            A source config dictionary

        Returns
        -------
        output_format : str
            The customized output format or 'xml' by default

        Raises
        ------
        UnsupportedPropertyValueError
            If the customized output format is not supported
        """
        output_format = config.get(
            MimeoConfig.OUTPUT_FORMAT_KEY,
            MimeoConfig.OUTPUT_FORMAT_XML)
        if output_format not in MimeoConfig.SUPPORTED_OUTPUT_FORMATS:
            raise UnsupportedPropertyValueError(
                MimeoConfig.OUTPUT_FORMAT_KEY,
                output_format,
                MimeoConfig.SUPPORTED_OUTPUT_FORMATS)
        return output_format

    @staticmethod
    def _get_indent(
            config: dict,
    ) -> int:
        """Extract an indent value from the source dictionary.

        Parameters
        ----------
        config : dict
            A source config dictionary

        Returns
        -------
        indent : int
            The customized indent or 0 by default

        Raises
        ------
        InvalidIndentError
            If the customized indent is lower than zero
        """
        indent = config.get(MimeoConfig.OUTPUT_INDENT_KEY, 0)
        if indent < 0:
            raise InvalidIndentError(indent)
        return indent

    @staticmethod
    def _get_directory_path(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract an output directory path from the source dictionary.

        It is extracted only when the output direction is 'file'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured output directory path when the output direction is 'file'.
            Otherwise, None. If the 'directory_path' setting is missing returns
            'mimeo-output' by default.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_FILE:
            return output.get(MimeoConfig.OUTPUT_DIRECTORY_PATH_KEY, "mimeo-output")
        return None

    @staticmethod
    def _get_file_name(
            direction: str,
            output: dict,
            output_format: str,
    ) -> str | None:
        """Generate an output file name template based on the source dictionary.

        It is generated only when the output direction is 'file'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured output file name template when the output direction is
            'file'. Otherwise, None. If the 'file_name' setting is missing returns
            'mimeo-output-{}.{output_format}' by default.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_FILE:
            file_name = output.get(MimeoConfig.OUTPUT_FILE_NAME_KEY, "mimeo-output")
            return f"{file_name}-{'{}'}.{output_format}"
        return None

    @staticmethod
    def _get_method(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract an HTTP request method from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        method: str | None
            The configured HTTP request method when the output direction is 'http'.
            Otherwise, None. If the 'method' setting is missing returns
            'POST' by default.
        """
        method = None
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            method = output.get(
                MimeoConfig.OUTPUT_METHOD_KEY,
                MimeoConfig.OUTPUT_DIRECTION_HTTP_REQUEST_POST)
            if method not in MimeoConfig.SUPPORTED_REQUEST_METHODS:
                raise UnsupportedPropertyValueError(
                    MimeoConfig.OUTPUT_METHOD_KEY,
                    method,
                    MimeoConfig.SUPPORTED_REQUEST_METHODS)
        return method

    @staticmethod
    def _get_protocol(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract an HTTP protocol from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured HTTP request method when the output direction is 'http'.
            Otherwise, None. If the 'protocol' setting is missing returns
            'http' by default.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            return output.get(MimeoConfig.OUTPUT_PROTOCOL_KEY,
                              MimeoConfig.OUTPUT_DIRECTION_HTTP)
        return None

    @staticmethod
    def _get_host(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract an HTTP host from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured HTTP host when the output direction is 'http'.
            Otherwise, None.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            return output.get(MimeoConfig.OUTPUT_HOST_KEY)
        return None

    @staticmethod
    def _get_port(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract an HTTP port from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured HTTP port when the output direction is 'http'.
            Otherwise, None.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            return output.get(MimeoConfig.OUTPUT_PORT_KEY)
        return None

    @staticmethod
    def _get_endpoint(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract an HTTP endpoint from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured HTTP request method when the output direction is 'http'.
            Otherwise, None.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            return output.get(MimeoConfig.OUTPUT_ENDPOINT_KEY)
        return None

    @staticmethod
    def _get_username(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract a username from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured username when the output direction is 'http'.
            Otherwise, None.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            return output.get(MimeoConfig.OUTPUT_USERNAME_KEY)
        return None

    @staticmethod
    def _get_password(
            direction: str,
            output: dict,
    ) -> str | None:
        """Extract a password from the source dictionary.

        It is extracted only when the output direction is 'http'.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Returns
        -------
        str | None
            The configured password when the output direction is 'http'.
            Otherwise, None.
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            return output.get(MimeoConfig.OUTPUT_PASSWORD_KEY)
        return None

    @staticmethod
    def _validate_output(
            direction: str,
            output: dict,
    ) -> None:
        """Validate output details in the source dictionary.

        The validation is being done according to the configured output
        direction.

        Parameters
        ----------
        direction : str
            The configured output direction
        output : dict
            A source config output details dictionary

        Raises
        ------
        MissingRequiredPropertyError
            If the output details doesn't include all required settings
            for the direction
        """
        if direction == MimeoConfig.OUTPUT_DIRECTION_HTTP:
            missing_details = []
            for detail in MimeoConfig.REQUIRED_HTTP_DETAILS:
                if detail not in output:
                    missing_details.append(detail)
            if len(missing_details) > 0:
                details_str = ", ".join(missing_details)
                msg = f"Missing required fields is HTTP output details: {details_str}"
                raise MissingRequiredPropertyError(msg)


class MimeoTemplate(MimeoDTO):
    """A MimeoDTO class representing Mimeo Template.

    It is a python representation of a Mimeo Template configuration node.

    Attributes
    ----------
    count : int
        A configured count of the Mimeo Template
    model : MimeoModel
        A configured model of the Mimeo Template
    """

    def __init__(
            self,
            template: dict,
    ):
        """Initialize MimeoTemplate class.

        Extends MimeoDTO constructor.

        Parameters
        ----------
        template : dict
            A source config template dictionary
        """
        super().__init__(template)
        self._validate_template(template)
        self.count = template.get(MimeoConfig.TEMPLATES_COUNT_KEY)
        self.model = MimeoModel(template.get(MimeoConfig.TEMPLATES_MODEL_KEY))

    @staticmethod
    def _validate_template(
            template: dict,
    ) -> None:
        """Validate template in the source dictionary.

        Parameters
        ----------
        template : dict
            A source config template dictionary

        Raises
        ------
        IncorrectMimeoTemplate
            If the source config doesn't include count or model properties
        """
        if MimeoConfig.TEMPLATES_COUNT_KEY not in template:
            msg = f"No count value in the Mimeo Template: {template}"
            raise InvalidMimeoTemplateError(msg)
        if MimeoConfig.TEMPLATES_MODEL_KEY not in template:
            msg = f"No model data in the Mimeo Template: {template}"
            raise InvalidMimeoTemplateError(msg)


class MimeoModel(MimeoDTO):
    """A MimeoDTO class representing Mimeo Model.

    It is a python representation of a Mimeo Model configuration node.

    Attributes
    ----------
    root_name : str
        A root node's tag
    root_data : dict
        A template data
    context_name : str
        A context name (root_name by default)
    """

    def __init__(
            self,
            model: dict,
    ):
        """Initialize MimeoModel class.

        Extends MimeoDTO constructor.

        Parameters
        ----------
        model : dict
            A source config model dictionary
        """
        super().__init__(model)
        self.root_name = MimeoModel._get_root_name(model)
        self.root_data = model.get(self.root_name)
        self.context_name = MimeoModel._get_context_name(model, self.root_name)

    @staticmethod
    def _get_root_name(
            model: dict,
    ) -> str:
        """Extract a root name from the source dictionary.

        Parameters
        ----------
        model : dict
            A source config model dictionary

        Returns
        -------
        str
            The configured root node's tag

        Raises
        ------
        IncorrectMimeoModel
            If the source config has no or more than one root nodes
        """
        model_keys = list(filter(MimeoModel._is_not_configuration_key, iter(model)))
        if len(model_keys) == 0:
            msg = f"No root data in Mimeo Model: {model}"
            raise InvalidMimeoModelError(msg)
        if len(model_keys) > 1:
            msg = f"Multiple root data in Mimeo Model: {model}"
            raise InvalidMimeoModelError(msg)
        return model_keys[0]

    @staticmethod
    def _get_context_name(
            model: dict,
            root_name: str,
    ) -> str:
        """Extract a context name from the source dictionary.

        Parameters
        ----------
        model : dict
            A source config model dictionary
        root_name : str
            The configured root node's tag

        Returns
        -------
        str
            The configured context name.
            If the 'context' setting is missing returns root name by default

        Raises
        ------
        IncorrectMimeoModel
            If the source config has a context name not being a string value
        """
        context_name = model.get(MimeoConfig.MODEL_CONTEXT_KEY, root_name)
        if not isinstance(context_name, str):
            msg = f"Invalid context name in Mimeo Model (not a string value): {model}"
            raise InvalidMimeoModelError(msg)
        return context_name

    @staticmethod
    def _is_not_configuration_key(
            dict_key: str,
    ) -> bool:
        """Verify if the dictionary key is a configuration one.

        Parameters
        ----------
        dict_key : str
            A dictionary key to verify

        Returns
        -------
        bool
            True if the key is 'context', otherwise False
        """
        return dict_key not in [MimeoConfig.MODEL_CONTEXT_KEY]
