"""The Mimeo Context Manager module.

It exports only one class:
    * MimeoContextManager
        An OnlyOneAlive class managing Mimeo Contexts.
"""
from __future__ import annotations

from types import TracebackType

from mimeo.config import MimeoConfig
from mimeo.context import MimeoContext
from mimeo.context.exc import VarNotFoundError
from mimeo.meta import Alive, OnlyOneAlive


class MimeoContextManager(Alive, metaclass=OnlyOneAlive):
    """An OnlyOneAlive class managing Mimeo Contexts.

    It allows you to initialize a context, get the currently processing
    context, switch it or reach any other. Besides that it gives you
    access to Mimeo Vars.
    The only way to use it successfully it is by `with` statement:
        with MimeoContextManager(mimeo_config) as mimeo_mng:
            ...

    Methods
    -------
    get_context(self, context: str) -> MimeoContext
        Return a Mimeo Context with a specific name.
    get_current_context(self) -> MimeoContext
        Return the current Mimeo Context.
    set_current_context(self, context: MimeoContext)
        Set the current Mimeo Context.
    get_var(self, variable_name: str)
        Return a specific Mimeo Var value.
    """

    def __init__(
            self,
            mimeo_config: MimeoConfig = None,
    ):
        """Initialize MimeoContextManager class.

        Parameters
        ----------
        mimeo_config : MimeoConfig
            The Mimeo Configuration
        """
        super().__init__()
        self._mimeo_config = mimeo_config
        self._vars = {}
        self._contexts = {}
        self._current_context = None

    def __enter__(
            self,
    ) -> MimeoContextManager:
        """Enter the MimeoContextManager instance.

        Extends Alive __enter__ function and initializes vars.

        Returns
        -------
        self : MimeoContextManager
            A MimeoContextManager instance
        """
        super().__enter__()
        self._vars = self._mimeo_config.vars
        return self

    def __exit__(
            self,
            exc_type: type | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        """Exit the MimeoContextManager instance.

        Extends Alive __enter__ function and removes internal
        attributes.

        Parameters
        ----------
        exc_type : type | None
            An exception's type
        exc_val : BaseException | None
            An exception's value
        exc_tb  TracebackType | None
            An exception's traceback

        Returns
        -------
        None
            A None value
        """
        super().__exit__(exc_type, exc_val, exc_tb)
        self._vars = None
        self._contexts = None

    def get_context(
            self,
            context: str,
    ) -> MimeoContext:
        """Return a Mimeo Context with a specific name.

        If the context does not exist, it is initialized.

        Parameters
        ----------
        context : str
            A context's name

        Returns
        -------
        MimeoContext
            A specific Mimeo Context

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        """
        super().assert_alive()
        if context not in self._contexts:
            self._contexts[context] = MimeoContext(context)
        return self._contexts[context]

    def get_current_context(
            self,
    ) -> MimeoContext:
        """Return the current Mimeo Context.

        Returns
        -------
        MimeoContext
            The current Mimeo Context

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        """
        super().assert_alive()
        return self._current_context

    def set_current_context(
            self,
            context: MimeoContext,
    ):
        """Set the current Mimeo Context.

        Parameters
        ----------
        context : MimeoContext
            A Mimeo Context to be set as the current one

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        """
        super().assert_alive()
        self._current_context = context

    def get_var(
            self,
            variable_name: str,
    ) -> str | int | bool | dict:
        """Return a specific Mimeo Var value.

        Parameters
        ----------
        variable_name : str
            The Mimeo Var name

        Returns
        -------
        value : str | int | bool | dict
            The Mimeo Var value

        Raises
        ------
        InstanceNotAlive
            If the MimeoContextManager instance is not alive
        VarNotFoundError
            If the Mimeo Var with the `variable_name` provided does not
            exist
        """
        super().assert_alive()
        value = self._vars.get(variable_name)
        if value is None:
            raise VarNotFoundError(variable_name)
        return value
