"""The Mimeo Renderers module.

This module contains classes useful in value rendering. It exports
the following renderers:
    * MimeoRenderer
        A Facade class rendering Mimeo Utils, Vars and Special Fields.
    * UtilsRenderer
        A class rendering Mimeo Utils.
    * VarsRenderer
        A class rendering Mimeo Vars.
    * SpecialFieldsRenderer
        A class rendering Mimeo Special Fields.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from mimeo.config import MimeoConfig
from mimeo.context import MimeoContext, MimeoContextManager
from mimeo.context.decorators import mimeo_context
from mimeo.utils import (AutoIncrementUtil, CityUtil, CountryUtil,
                         CurrentIterationUtil, DateTimeUtil, DateUtil,
                         FirstNameUtil, KeyUtil, LastNameUtil, MimeoUtil,
                         RandomIntegerUtil, RandomItemUtil, RandomStringUtil)
from mimeo.utils.exc import InvalidMimeoUtilError, NotASpecialFieldError

logger = logging.getLogger(__name__)


class UtilsRenderer:
    """A class rendering Mimeo Utils.

    It contains only class methods.

    Methods
    -------
    render_raw(mimeo_util_key: str) -> Any
        Render a Mimeo Util in a raw form.
    render_parametrized(mimeo_util_config: dict) -> Any
        Render a Mimeo Util in a parametrized form.
    """

    MIMEO_UTILS = {
        RandomStringUtil.KEY: RandomStringUtil,
        RandomIntegerUtil.KEY: RandomIntegerUtil,
        RandomItemUtil.KEY: RandomItemUtil,
        DateUtil.KEY: DateUtil,
        DateTimeUtil.KEY: DateTimeUtil,
        AutoIncrementUtil.KEY: AutoIncrementUtil,
        CurrentIterationUtil.KEY: CurrentIterationUtil,
        KeyUtil.KEY: KeyUtil,
        CityUtil.KEY: CityUtil,
        CountryUtil.KEY: CountryUtil,
        FirstNameUtil.KEY: FirstNameUtil,
        LastNameUtil.KEY: LastNameUtil,
    }
    _INSTANCES = {}

    @classmethod
    def render_raw(
            cls,
            mimeo_util_key: str,
    ) -> Any:
        """Render a Mimeo Util in a raw form.

        Parameters
        ----------
        mimeo_util_key : str
            A Mimeo Util key (name)

        Returns
        -------
        Any
            Rendered Mimeo Util value.

        Raises
        ------
        InvalidMimeoUtil
            If the Mimeo Util name does not match any existing Mimeo
            Util.
        """
        return cls.render_parametrized({
            MimeoConfig.MODEL_MIMEO_UTIL_NAME_KEY: mimeo_util_key,
        })

    @classmethod
    def render_parametrized(
            cls,
            mimeo_util_config: dict,
    ) -> Any:
        """Render a Mimeo Util in a parametrized form.

        Parameters
        ----------
        mimeo_util_config : dict
            A Mimeo Util configuration

        Returns
        -------
        Any
            Rendered Mimeo Util value.

        Raises
        ------
        InvalidMimeoUtil
            If the Mimeo Util configuration does not include Mimeo
            Util name, or the parametrized name does not match any
            existing Mimeo Util.
        InvalidValue
            If a Mimeo Util is incorrectly parametrized.
        InvalidSexError
            If the First Name Mimeo Util has not supported `sex`
            parameter value assigned.
        """
        logger.fine("Rendering a mimeo util [%s]", mimeo_util_config)
        mimeo_util = cls._get_mimeo_util(mimeo_util_config)
        return mimeo_util.render()

    @classmethod
    def _get_mimeo_util(
            cls,
            config: dict,
    ) -> MimeoUtil:
        """Get a Mimeo Util instance based on the configuration.

        All instances are cached to not re-create a Util with the same
        parameters. This method instantiate a Mimeo Util for the first
        time and use the one in the future.

        Parameters
        ----------
        config : dict
            A Mimeo Util configuration

        Returns
        -------
        MimeoUtil
            A Mimeo Util instance

        Raises
        ------
        InvalidMimeoUtil
            If the Mimeo Util configuration does not include Mimeo
            Util name, or the parametrized name does not match any
            existing Mimeo Util.
        """
        cache_key = cls._generate_cache_key(config)
        if cache_key not in cls._INSTANCES:
            return cls._instantiate_mimeo_util(cache_key, config)
        return cls._INSTANCES.get(cache_key)

    @staticmethod
    def _generate_cache_key(
            config: dict,
    ) -> str:
        """Generate an internal Mimeo Util key from its parameters.

        This method ensures that Mimeo Util instances are cached
        properly for the same parameters.

        Parameters
        ----------
        config : dict
            A Mimeo Util configuration

        Returns
        -------
        str
            An internal Mimeo Util cache key
        """
        return "-".join(":".join([key, str(val)]) for key, val in config.items())

    @classmethod
    def _instantiate_mimeo_util(
            cls,
            cache_key: str,
            config: dict,
    ) -> MimeoUtil:
        """Instantiate a Mimeo Util based on the configuration.

        After instantiation the Mimeo Util is cached for the future.

        Parameters
        ----------
        cache_key : str
            An internal Mimeo Util cache key
        config : dict
            A Mimeo Util configuration

        Returns
        -------
        MimeoUtil
            A Mimeo Util instance

        Raises
        ------
        InvalidMimeoUtil
            If the Mimeo Util configuration does not include Mimeo
            Util name, or the parametrized name does not match any
            existing Mimeo Util.
        """
        mimeo_util_name = cls.get_mimeo_util_name(config)
        mimeo_util = cls.MIMEO_UTILS.get(mimeo_util_name)(**config)
        cls._INSTANCES[cache_key] = mimeo_util
        return mimeo_util

    @classmethod
    def get_mimeo_util_name(
            cls,
            config: dict,
    ) -> str:
        """Return a verified Mimeo Util name.

        Parameters
        ----------
        config : dict
            A Mimeo Util configuration

        Returns
        -------
        str
            A Mimeo Util name

        Raises
        ------
        InvalidMimeoUtil
            If the Mimeo Util configuration does not include Mimeo
            Util name, or the parametrized name does not match any
            existing Mimeo Util.
        """
        mimeo_util_name = config.get(MimeoConfig.MODEL_MIMEO_UTIL_NAME_KEY)
        if mimeo_util_name is None:
            msg = f"Missing Mimeo Util name in configuration [{config}]!"
            raise InvalidMimeoUtilError(msg)
        if mimeo_util_name not in cls.MIMEO_UTILS:
            msg = f"No such Mimeo Util [{mimeo_util_name}]!"
            raise InvalidMimeoUtilError(msg)
        return mimeo_util_name


class VarsRenderer:
    """A class rendering Mimeo Vars.

    It contains only a class method.

    Methods
    -------
    render(var: str) -> Any
        Render a Mimeo Var.
    """

    @classmethod
    def render(
            cls,
            var: str,
    ) -> str | int | bool | dict:
        """Render a Mimeo Var.

        Parameters
        ----------
        var : str
            A variable name

        Returns
        -------
        Any
            A variable value

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        VarNotFoundError
            If the Mimeo Var with the `var` provided does not exist
        """
        logger.fine("Rendering a variable [%s]", var)
        return MimeoContextManager().get_var(var)


class SpecialFieldsRenderer:
    """A class rendering Mimeo Special Fields.

    It contains only a class method.

    Methods
    -------
    render(field_name: str, context: MimeoContext = None) -> Any
        Render a Mimeo Special Field.
    """

    @classmethod
    @mimeo_context
    def render(
            cls,
            field: str,
            context: MimeoContext = None,
    ) -> str | int | bool:
        """Render a Mimeo Special Field.

        Parameters
        ----------
        field : str
            A special field name
        context : MimeoContext, default None
            A current Mimeo Context injected by a decorator

        Returns
        -------
        str | int | bool

        Raises
        ------
        UninitializedContextIterationError
            If no iteration has been initialized yet for the context
        SpecialFieldNotFoundError
            If the special field does not exist.
        """
        logger.fine("Rendering a special field [%s]", field)
        return context.curr_iteration().get_special_field(field)


class MimeoRenderer:
    """A Facade class rendering Mimeo Utils, Vars and Special Fields.

    It contains only class methods.

    Methods
    -------
    render(value: Any) -> Any
        Render a value.
    get_special_field_name(wrapped_field_name: str) -> str
        Extract a special field name.
    is_special_field(special_field: str) -> bool
        Verify if the field is special (of form {:FIELD_NAME:}).
    is_raw_mimeo_util(value: str) -> bool
        Verify if the value is a raw Mimeo Util.
    is_parametrized_mimeo_util(value: dict)
        Verify if the value is a parametrized Mimeo Util.
    """

    _UTILS_PATTERN = re.compile("^{(.+)}$")
    _VARS_PATTERN = re.compile(".*({[A-Z_0-9]+})")
    _SPECIAL_FIELDS_PATTERN = re.compile(".*({:([a-zA-Z]+:)?[-_a-zA-Z0-9]+:})")

    @classmethod
    def get_special_field_name(
            cls,
            wrapped_field_name: str,
    ) -> str:
        """Extract a special field name.

        Parameters
        ----------
        wrapped_field_name : str
            A field name wrapped with curly braces and colons,
            e.g. {:Field:}

        Returns
        -------
        str
            A special field name

        Raises
        ------
        NotASpecialField
            If the `wrapped_field_name` is not of form {:FIELD_NAME:}
        """
        if not cls.is_special_field(wrapped_field_name):
            raise NotASpecialFieldError(wrapped_field_name)

        return wrapped_field_name[2:][:-2]

    @classmethod
    def is_special_field(
            cls,
            special_field: str,
    ) -> bool:
        """Verify if the field is special (of form {:FIELD_NAME:}).

        Parameters
        ----------
        special_field : str
            A special field

        Returns
        -------
        bool
            True if the field is of form {:FIELD_NAME:}. Otherwise,
            False.
        """
        return bool(re.match(r"^{:([a-zA-Z]+:)?[-_a-zA-Z0-9]+:}$", special_field))

    @classmethod
    def is_raw_mimeo_util(
            cls,
            value: str,
    ) -> bool:
        """Verify if the value is a raw Mimeo Util.

        Parameters
        ----------
        value : str
            A string value

        Returns
        -------
        bool
            True if the value is a raw Mimeo Util, e.g. {random_str}.
            Otherwise, False.
        """
        raw_mimeo_utils = UtilsRenderer.MIMEO_UTILS.keys()
        raw_mimeo_utils_re = "^{(" + "|".join(raw_mimeo_utils) + ")}$"
        return bool(re.match(raw_mimeo_utils_re, value))

    @classmethod
    def is_parametrized_mimeo_util(
            cls,
            value: dict,
    ):
        """Verify if the value is a parametrized Mimeo Util.

        Parameters
        ----------
        value : dict
            A dict value

        Returns
        -------
        bool
            True if the value is a dictionary having only one key,
            "_mimeo_util". Otherwise, False.
        """
        return (isinstance(value, dict) and
                len(value) == 1 and
                MimeoConfig.MODEL_MIMEO_UTIL_KEY in value)

    @classmethod
    def render(
            cls,
            value: Any,
    ) -> Any:
        """Render a value.

        This method renders a value accordingly to its type and form.
        If the value takes a form of Mimeo Util it is rendered as
        Mimeo Util (raw or parametrized); if it takes a form of
        a special field this renderer will try to reach it from
        the current context; when the value takes a form of a Mimeo Var,
        then it uses Mimeo Vars defined in Mimeo Config.
        Otherwise, the raw value is returned.
        It is recursively called to return a final value.

        Parameters
        ----------
        value : Any
            A value to be rendered

        Returns
        -------
        Any
            A rendered value

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        UninitializedContextIterationError
            If no iteration has been initialized yet for the context
        VarNotFoundError
            If the Mimeo Var does not exist
        InvalidMimeoUtil
            If the Mimeo Util node has missing _name property, or it
            does not match any Mimeo Util.
        InvalidValue
            If Mimeo Util node is incorrectly parametrized
        OutOfStockError
            If all unique values have been consumed already
        DataNotFoundError
            If database does not contain the expected value
        InvalidSexError
            If the First Name Mimeo Util has not supported `sex`
            parameter value assigned.
        """
        logger.fine("Rendering a value [%s]", value)
        try:
            if isinstance(value, str):
                value = cls._render_string_value(value)
            if cls.is_parametrized_mimeo_util(value):
                value = cls._render_parametrized_mimeo_util(value)
        except Exception:
            logger.exception("An error occurred for [%s].", value)
            raise
        return value

    @classmethod
    def _render_string_value(
            cls,
            value: str,
    ) -> Any:
        """Render a string value.

        Depending on value form it can render it as a raw value,
        a special field, a Mimeo Var or a raw Mimeo Util.

        Parameters
        ----------
        value : str
            A string value

        Returns
        -------
        Any
            A rendered value
        """
        if cls._SPECIAL_FIELDS_PATTERN.match(value):
            return cls._render_special_field(value)
        if cls._VARS_PATTERN.match(value):
            return cls._render_var(value)
        if cls.is_raw_mimeo_util(value):
            return cls._render_raw_mimeo_util(value)
        return value

    @classmethod
    def _render_special_field(
            cls,
            value: str,
    ) -> Any:
        """Render a value containing a Mimeo Special Field.

        This method finds first special field and replaces all
        occurrences. Then the result is passed to the render() method
        again, to return a final value.

        Parameters
        ----------
        value : str
            A value containing a Mimeo Special Field

        Returns
        -------
        Any
            A rendered value

        Raises
        ------
        UninitializedContextIterationError
            If no iteration has been initialized yet for the context
        SpecialFieldNotFoundError
            If the special field does not exist.
        """
        match = next(cls._SPECIAL_FIELDS_PATTERN.finditer(value))
        wrapped_special_field = match.group(1)
        r_val = SpecialFieldsRenderer.render(wrapped_special_field[2:][:-2])
        logger.fine("Rendered special field value [%s]", r_val)
        if len(wrapped_special_field) != len(value):
            r_val = str(r_val).lower() if isinstance(r_val, bool) else str(r_val)
            r_val = value.replace(wrapped_special_field, str(r_val))
        return cls.render(r_val)

    @classmethod
    def _render_var(
            cls,
            value: str,
    ) -> Any:
        """Render a value containing a Mimeo Var.

        This method finds first variable and replaces all occurrences.
        Then the result is passed to the render() method again, to
        return a final value.

        Parameters
        ----------
        value : str
            A value containing a Mimeo Var

        Returns
        -------
        Any
            A rendered value

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        VarNotFoundError
            If the Mimeo Var with the `var` provided does not exist
        """
        match = next(cls._VARS_PATTERN.finditer(value))
        wrapped_var = match.group(1)
        r_val = VarsRenderer.render(wrapped_var[1:][:-1])
        logger.fine("Rendered variable value [%s]", r_val)
        if cls.is_parametrized_mimeo_util(r_val):
            r_val = cls._render_parametrized_mimeo_util(r_val)
        if len(wrapped_var) != len(value):
            r_val = str(r_val).lower() if isinstance(r_val, bool) else str(r_val)
            r_val = value.replace(wrapped_var, str(r_val))
        return cls.render(r_val)

    @classmethod
    def _render_raw_mimeo_util(
            cls,
            value: str,
    ) -> Any:
        """Render a raw Mimeo Util.

        Parameters
        ----------
        value : str
            A raw Mimeo Util

        Returns
        -------
        Any
            A rendered value

        Raises
        ------
        OutOfStockError
            If all unique values have been consumed already
        DataNotFoundError
            If database does not contain the expected value
        """
        rendered_value = UtilsRenderer.render_raw(value[1:][:-1])
        return cls.render(rendered_value)

    @classmethod
    def _render_parametrized_mimeo_util(
            cls,
            value: dict,
    ) -> Any:
        """Render a parametrized Mimeo Util.

        Before the Mimeo Util itself will be rendered, first all its
        parameters (except name) are rendered.

        Parameters
        ----------
        value : str
            A parametrized Mimeo Util

        Returns
        -------
        Any
            A rendered value

        Raises
        ------
        InvalidValue
            If a Mimeo Util is incorrectly parametrized.
        OutOfStockError
            If all unique values have been consumed already
        DataNotFoundError
            If database does not contain the expected value
        InvalidSexError
            If the First Name Mimeo Util has not supported `sex`
            parameter value assigned.
        """
        mimeo_util = value[MimeoConfig.MODEL_MIMEO_UTIL_KEY]
        mimeo_util = cls._render_mimeo_util_parameters(mimeo_util)
        logger.fine("Pre-rendered mimeo util [%s]", mimeo_util)
        r_val = UtilsRenderer.render_parametrized(mimeo_util)
        return cls.render(r_val)

    @classmethod
    def _render_mimeo_util_parameters(
            cls,
            mimeo_util_config: dict,
    ) -> dict:
        """Render Mimeo Util's parameters.

        Parameters
        ----------
        mimeo_util_config : dict
            A parametrized Mimeo Util

        Returns
        -------
        dict
            A Mimeo Util with pre-rendered parameters

        Raises
        ------
        InvalidValue
            If a Mimeo Util is incorrectly parametrized.
        OutOfStockError
            If all unique values have been consumed already
        DataNotFoundError
            If database does not contain the expected value
        InvalidSexError
            If the First Name Mimeo Util has not supported `sex`
            parameter value assigned.
        """
        logger.fine("Rendering mimeo util parameters")
        return {key: cls.render(value) if key != "_name" else value
                for key, value in mimeo_util_config.items()}
