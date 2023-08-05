from __future__ import annotations

import re
import typing as t

from flask import (
    current_app,
    redirect,
    url_for,
    request,
    flash as _flash
)


__all__ = (
    'camel_to_list', 'camel_to_snake', 'snake_to_camel',
    'get_route_param_names', 'make_redirect', 'flash',
)


def camel_to_list(s: str, lower: bool = False) -> t.List[str]:
    """Converts a camelcase string to a list."""
    lst = re.findall(r'([A-Z][a-z0-9]+)', s) or [s]
    return [w.lower() for w in lst] if lower else lst


def camel_to_snake(name: str) -> str:
    """Converts a camelcase string to a snake case string."""
    return '_'.join(camel_to_list(name, lower=True))


def snake_to_camel(name: str) -> str:
    """Converts a snake case string to a camelcase string."""
    return ''.join(name.title().split('_'))


def get_route_param_names(endpoint):
    """
    Returns parameter names from the route.

    Arguments:
        endpoint (str): The absolute name of the endpoint.
    """
    try:
        g = current_app.url_map.iter_rules(endpoint)
        return next(g).arguments
    except KeyError:
        return {}


def make_redirect(actions, params, var_name='action'):
    """
    Depending on the button pressed in the form, it creates a 302 redirect.

    Arguments:
        actions (dict):
            Mapping action names to endpoint names.
        params (object):
            An object whose property values will be used for parameters in the URL rule.
        var_name (str):
            The name of the variable whose value is used as the name of the action.

    Example:
        from functools import partial

        post_redirect = partial(make_redirect, {
            'Save': 'update',
            'Save and Create': 'create',
            'Save and Close': 'index',
        })

        @app.route('/create')
        def create():
            # ...
            if form.validate_on_submit():
                product = Product()
                form.populate_obj(product)
                db.session.add(product)
                db.session.commit()
                return post_redirect(product)
            # ...
    """
    endpoint = actions[request.form.get(var_name)]
    return redirect(make_url(endpoint, params))


def make_url(endpoint, params, **kwargs):
    """
    Creates the URL of the specified endpoint, using the passed object as rule parameter values.

    Arguments:
        endpoint (str):
            the endpoint of the URL (name of the function).
        params (object):
            An object whose property values will be used for parameters in the URL rule.
    """
    values = {}

    for name in get_route_param_names(endpoint):
        if isinstance(params, dict):
            values[name] = params.get(name)
        else:
            values[name] = getattr(params, name, None)

    return url_for(endpoint, **values, **kwargs)


class Flash:
    """
    A wrapper for flash messages that standardizes message categories.
    """

    def __call__(self, message: str, level: str = 'info') -> None:
        _flash(message, level)

    def debug(self, message: str) -> None:
        self(message, 'debug')

    def error(self, message: str) -> None:
        self(message, 'error')

    def info(self, message: str) -> None:
        self(message, 'info')

    def success(self, message: str) -> None:
        self(message, 'success')

    def warning(self, message: str) -> None:
        self(message, 'warning')


flash = Flash()
