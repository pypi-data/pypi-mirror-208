from enum import Enum
from typing import Generic, TypeVar, Type
from dataclasses import dataclass


class Scope(Enum):
    request = "REQUEST"
    singleton = "SINGLETON"


T = TypeVar("T")


@dataclass()
class Dependency(Generic[T]):
    scope: Scope
    cls: Type[T]
    params: list[tuple[type, str | None]] = None
    name: str = None
    instance: T = None
    factory: callable = None


def qualifier_to_data(qualifier: str) -> dict[str, str]:
    d = dict()
    for s in qualifier.split(","):
        q = s.split(":")
        d[q[0]] = q[1]
    return d
