"""The Alive module.

It exports classes allowing you to define a class as alive and forbid
to have more than one alive instance at the same time. This
functionality is similar to the Singleton pattern. However, using
OnlyOneAlive class you can instantiate a class multiple times.
Thanks to that a single instance will not store several configurations
depending on execution time. This pattern ensures your instances are
consistent and will be reached whenever needed using a constructor.

The complete pattern is supported using 2 exported classes:
    * OnlyOneAlive
        A type ensuring there's only one instance qualified to be used.
    * Alive
        A superclass for OnlyOneAlive classes.

Example
-------
class SomeClass(Alive, metaclass=OnlyOneAlive):

    def __init__(self, config: dict = None):
        self._config = config

    def get_x(self):
        super().assert_alive()
        return self._config.get('x', None)


with SomeClass({'x': 1}) as alive_1:
    x_1 = alive_1.get_x()

    alive_2 = SomeClass()
    x_2 = alive_2.get_x()

    print('Alive 1:', x_1)  # 1
    print('Alive 2:', x_2)  # 1
"""
from __future__ import annotations

from types import TracebackType

from mimeo.meta.exc import InstanceNotAliveError


class OnlyOneAlive(type):
    """A type ensuring there's only one instance qualified to be used.

    The OnlyOneAlive type caches all instances being created for each
    Alive subclass. If there is any instance being alive, it is
    returned by a constructor. Otherwise, an Alive subclass is
    instantiated and returned.
    """

    _INSTANCES = {}

    def __call__(
            cls,
            *args,
            **kwargs,
    ):
        """Ensure there's only one instance qualified to be used."""
        if cls not in cls._INSTANCES:
            cls._INSTANCES[cls] = []

        alive_instance = next((i for i in cls._INSTANCES[cls] if i.is_alive()), None)
        if alive_instance is None:
            instance = super().__call__(*args, **kwargs)
            cls._INSTANCES[cls].append(instance)
            return instance
        return alive_instance


class Alive:
    """A superclass for OnlyOneAlive classes.

    It provides several features defined to use OnlyOneAlive pattern:
    * Context Manager functionality
    * a method checking if an instance is alive
    * a method throwing an exception when the instance is not alive

    Methods
    -------
    is_alive()
        Verify if the instance is alive.
    assert_alive()
        Assert the instance is alive.
    """

    def __init__(
            self,
    ):
        self._alive = False

    def __enter__(
            self,
    ) -> Alive:
        """Enter the Alive instance.

        It sets the internal `alive` attribute to True.

        Returns
        -------
        self : Alive
            A Alive instance
        """
        self._alive = True
        return self

    def __exit__(
            self,
            exc_type: type | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        """Exit the Alive instance.

        It sets the internal `alive` attribute to False.

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
        self._alive = False

    def assert_alive(
            self,
    ) -> bool:
        """Assert the instance is alive.

        Returns
        -------
        bool
            True

        Raises
        ------
        InstanceNotAlive
            If the instance is not alive
        """
        if not self.is_alive():
            raise InstanceNotAliveError
        return self.is_alive()

    def is_alive(
            self,
    ) -> bool:
        """Verify if the instance is alive."""
        return self._alive
