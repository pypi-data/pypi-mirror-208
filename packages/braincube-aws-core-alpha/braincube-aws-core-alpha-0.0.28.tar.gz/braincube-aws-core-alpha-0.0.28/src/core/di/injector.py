from typing import TypeVar, Type
from inspect import signature, isfunction, iscoroutinefunction
from .data import Dependency, Scope, qualifier_to_data

from ..dal.postgres_connection import Pool, get_pool

T = TypeVar("T")


class _Injector:
    """Module that used in order to resolve dependencies from components or route functions."""

    dependencies: list[Dependency] = list()

    @staticmethod
    def init_config():
        _Injector.dependencies.append(Dependency(Scope.singleton, Pool, factory=get_pool))
        # here put any other dependency you want to provide out of the box

    @staticmethod
    def inject(name: str = None, scope: Scope = Scope.singleton, qualifier: str = None):
        def _inject(component):
            data = qualifier_to_data(qualifier) if qualifier else dict()
            if isfunction(component):
                cls = component.__annotations__.get("return")
                if not cls:
                    raise ValueError(f"injected function '{component.__name__}' must specify return type.")

                params = [(v.annotation, data.get(k)) for k, v in signature(component).parameters.items()]
                _Injector.dependencies.append(Dependency(scope, cls, params, name, factory=component))
            else:
                items_ = dict(filter(lambda i: i[0] != "self", signature(component.__init__).parameters.items()))
                params = [(v.annotation, data.get(k)) for k, v in items_.items()]
                _Injector.dependencies.append(Dependency(scope, component, params, name))
            return component

        return _inject

    @staticmethod
    async def provide(cls: Type[T], name: str = None) -> T:

        matched = list(filter(lambda d: (d.cls is cls or issubclass(d.cls, cls)) and
                                        (d.name == name if name else d.name is None), _Injector.dependencies))

        if not matched:
            raise ValueError(f"component name:'{name}', class:'{cls}' not found.")
        if len(matched) > 1:
            raise ValueError(f"multiple matching components have been found for class: '{cls}'")
        if not matched[0].instance:
            nested = list()
            if matched[0].params:
                for param in matched[0].params:
                    nested.append(await _Injector.provide(param[0], param[1]))  # noqa
            if matched[0].factory:
                instance = await matched[0].factory(*nested) \
                    if iscoroutinefunction(matched[0].factory) else matched[0].factory(*nested)
            else:
                instance = matched[0].cls(*nested)
            if matched[0].scope is Scope.request:
                return instance
            matched[0].instance = instance
        return matched[0].instance

    @staticmethod
    def register_instance(cls: Type[T], instance: T, name: str = None):
        _Injector.dependencies.append(Dependency(Scope.singleton, cls, name=name, instance=instance))


def init_config():
    """Dependencies configuration using environment variables."""

    _Injector.init_config()


def inject(name: str = None, scope: Scope = Scope.singleton, qualifier: str = None):
    """Inject a class or function.
    :param name: Component name.
    :param scope: Class of the Scope in which to resolve.
    :param qualifier: Comma separated string, used to specify components by name in case of multiple implementations.
    """

    return _Injector.inject(name, scope, qualifier)


async def provide(cls: Type[T], name: str = None) -> T:
    """Get an instance of the given type.
    :param cls: Interface whose implementation we want.
    :param name: Name of a specific component that implements the interface.
    :returns: An implementation of interface.
    """

    return await _Injector.provide(cls, name)


def register_instance(cls: Type[T], instance: T, name: str = None):
    """Create manually and register an instance of a specific type.
    :param cls: Component type.
    :param instance: Component instance.
    :param name: Component name.
    """

    return _Injector.register_instance(cls, instance, name)
