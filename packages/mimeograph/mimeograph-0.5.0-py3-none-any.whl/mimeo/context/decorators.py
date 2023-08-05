"""The Mimeo Context Decorators module.

It defines the following decorators:

- @mimeo_context:
    Decorator providing a 'context' parameter to a function
- @mimeo_context_switch:
    Decorator switching context before and after function's call
- @mimeo_next_iteration:
    Decorator incrementing current context's iteration
- @mimeo_clear_iterations:
    Decorator clearing iterations of the current context

"""
from __future__ import annotations

import functools
from typing import Callable

from mimeo.config.mimeo_config import MimeoTemplate
from mimeo.context import MimeoContext, MimeoContextManager


def mimeo_context(
        func: Callable,
) -> Callable:
    """Provide a 'context' parameter to a function.

    It can be used only for functions having defined a 'context'
    parameter. In case the function being decorated is called providing
    this param, decorator simply calls it without any modification.
    Otherwise - and this is the main purpose of the @mimeo_context
    decorator - it provides the current Mimeo Context.

    Parameters
    ----------
    func : Callable
        The function being decorated

    Returns
    -------
    inject_context : Callable
        The decorated function
    """

    @functools.wraps(func)
    def inject_context(
            *args,
            **kwargs,
    ):
        if any(isinstance(arg, MimeoContext) for arg in args) or "context" in kwargs:
            result = func(*args, **kwargs)
        else:
            current_ctx = MimeoContextManager().get_current_context()
            result = func(*args, **kwargs, context=current_ctx)
        return result

    return inject_context


def mimeo_context_switch(
        func: Callable,
) -> Callable:
    """Switch context before and after function's call.

    It can be used only for functions having defined a MimeoTemplate
    parameter. It switches a Mimeo Context to the one defined in
    Mimeo Template, and after the function's being decorated call
    switches back to the previous one. It helps to handle nested
    Mimeo Templates. This decorator meant to be used for
    Generator's function that generates data from a template.

    Parameters
    ----------
    func : Callable
        The function being decorated

    Returns
    -------
    switch_context : Callable
        The decorated function
    """

    @functools.wraps(func)
    def switch_context(
            *args,
            **kwargs,
    ):
        context_mng = MimeoContextManager()
        prev_context = context_mng.get_current_context()

        if "template" in kwargs:
            template = kwargs["template"]
        else:
            template = next(arg for arg in args if isinstance(arg, MimeoTemplate))
        context_name = template.model.context_name
        next_context = context_mng.get_context(context_name)
        context_mng.set_current_context(next_context)
        result = func(*args, **kwargs)

        context_mng.set_current_context(prev_context)
        return result

    return switch_context


def mimeo_next_iteration(
        func: Callable,
):
    """Increment current context's iteration.

    It is meant to be used for Generator's function that
    generates a single data copy.

    Parameters
    ----------
    func : Callable
        The function being decorated

    Returns
    -------
    next_iteration : Callable
        The decorated function
    """

    @functools.wraps(func)
    def next_iteration(
            *args,
            **kwargs,
    ):
        MimeoContextManager().get_current_context().next_iteration()
        return func(*args, **kwargs)

    return next_iteration


def mimeo_clear_iterations(
        func: Callable,
):
    """Clear iterations of the current context.

    It is meant to be used for Generator's function that generates
    data from a template.

    Parameters
    ----------
    func : Callable
        The function being decorated

    Returns
    -------
    clear_iterations : Callable
        The decorated function
    """

    @functools.wraps(func)
    def clear_iterations(
            *args,
            **kwargs,
    ):
        MimeoContextManager().get_current_context().clear_iterations()
        return func(*args, **kwargs)

    return clear_iterations
