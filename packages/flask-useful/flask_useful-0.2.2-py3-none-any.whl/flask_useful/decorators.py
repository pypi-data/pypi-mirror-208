from functools import wraps
import typing as t

from .utils import camel_to_snake


_F = t.TypeVar('_F', bound=t.Callable[..., t.Any])


__all__ = ('getattr_or_implement', 'route')


def getattr_or_implement(getter: _F) -> _F:
    """
    Used to get the value of a property in a getter method
    when the property is not known to exist or not.

    If the property does not exist, the getter method must be implemented.

    The getter method never takes any arguments.
    """
    @wraps(getter)
    def wrapper(self: t.Any) -> t.Any:
        try:
            return getter(self)
        except AttributeError as err:
            raise NotImplementedError(
                f'{err} - override the `{self.__class__.__name__}.{getter.__name__}()` method.'
            )
    return t.cast(_F, wrapper)


def setattr_or_implement(setter: _F) -> _F:
    """
    Used to set the value of a property in a setter method
    when the property is not known to exist or not.

    If the property does not exist, the setter method must be implemented.

    The setter method takes only one argument.
    """
    @wraps(setter)
    def wrapper(self: t.Any, value: t.Any) -> None:
        try:
            setter(self, value)
        except AttributeError as err:
            raise NotImplementedError(
                f'{err} - override the `{self.__class__.__name__}.{setter.__name__}()` method.'
            )
    return t.cast(_F, wrapper)


def route(obj, rule, *args, **kwargs):
    """Decorator for the View classes."""
    def decorator(cls):
        endpoint = kwargs.get('endpoint', camel_to_snake(cls.__name__))
        kwargs['view_func'] = cls.as_view(endpoint)
        obj.add_url_rule(rule, *args, **kwargs)
        return cls
    return decorator
