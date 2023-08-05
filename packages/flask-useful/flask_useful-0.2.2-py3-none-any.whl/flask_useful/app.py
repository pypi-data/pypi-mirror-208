"""
The module contains functions for automating the configuration of the application object.
"""

from __future__ import annotations

import typing as t

from flask import Blueprint, Flask
from flask.cli import AppGroup
from werkzeug.utils import find_modules, import_string


__all__ = (
    'register_blueprints',
    'register_commands',
    'register_extensions',
)


AppOrBp = t.Union[Flask, Blueprint]


def get_import_prefix(app: AppOrBp) -> str:
    if app.import_name == '__main__':
        return ''
    return f'{app.import_name}.'


def get_import_path(app: AppOrBp, import_path: str) -> str:
    """Returns the absolute path to import a module or package."""
    prefix = get_import_prefix(app)
    return (prefix + import_path).strip('.')


def register_blueprints(
    app: AppOrBp,
    import_path: str,
    recursive: bool = False,
    include_packages: bool = False,
) -> None:
    """
    Registers Blueprint for the specified application.

    The argument `import_path` must be a valid import name for the package that contains the modules.
    One module - one Blueprint.
    The variable named `bp` must contain an instance of Blueprint.

    If the `BLUEPRINT_DISABLED` attribute is set in the module, then Blueprint will be ignored.
    """
    modules_names = list(find_modules(
        get_import_path(app, import_path),
        recursive=recursive,
        include_packages=include_packages,
    ))

    for name in modules_names:
        mod = import_string(name)

        if hasattr(mod, 'bp') and not getattr(mod.bp, 'BLUEPRINT_DISABLED', False):
            if isinstance(mod.bp, Blueprint):
                app.register_blueprint(mod.bp)


def register_commands(app: Flask, import_name: str) -> None:
    """Initializes console commands found at the specified import path.

    If the __all__ attribute is specified in the module,
    it will be used to fund commands.
    Otherwise, the search is performed using the `dir` function.

    Command is an object inherited from `flask.cli.AppGroup`.
    """
    m = import_string(get_import_path(app, import_name))

    for name in getattr(m, '__all__', dir(m)):
        prop = getattr(m, name)

        if isinstance(prop, AppGroup):
            app.cli.add_command(prop)


def register_extensions(app: Flask, import_name: str) -> None:
    """Initializes all Flask extensions found in the specified import path.

    If the __all__ attribute is specified in the module,
    it will be used to search for extension instances.
    Otherwise, the search is performed using the `dir` function.

    An extension is an object that has an init_app method.
    """
    m = import_string(get_import_path(app, import_name))

    for name in getattr(m, '__all__', dir(m)):
        prop = getattr(m, name)
        init_app = getattr(prop, 'init_app', None)

        if callable(init_app):
            init_app(app)
