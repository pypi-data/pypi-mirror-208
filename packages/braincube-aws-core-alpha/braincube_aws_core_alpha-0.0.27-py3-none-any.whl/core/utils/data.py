import glob
import importlib
from os.path import basename, isfile, join

from enum import Enum
from dataclasses import dataclass


class OrderType(Enum):
    asc = "ASC"
    desc = "DESC"


@dataclass()
class Order:
    type: OrderType
    alias: str


class ConditionType(Enum):
    any = "ANY"
    range = "RANGE"
    compare = "COMPARE"


@dataclass()
class Condition:
    type: ConditionType
    alias: str
    value: any


@dataclass()
class Paging:
    pageNo: int
    pageSize: int
    totalPages: int = None
    totalCount: int = None


@dataclass
class Metadata:
    dataElapsed: int


@dataclass()
class Page:
    data: list[dict[str, any]]
    paging: Paging
    meta: Metadata = None


@dataclass()
class Top:
    data: list[dict[str, any]]
    topSize: int
    hasMore: bool


@dataclass
class Pageable:
    page_no: int = 0
    page_size: int = 20
    top_size: int = 0


def import_directories(root: str, paths: list[str]):
    for path in paths:
        for module_name in get_module_names(f"{root}{path.replace('.', '/')}"):
            importlib.import_module(f"{path}.{module_name}")


def import_modules(paths: list[str]):
    for path in paths:
        importlib.import_module(path)


def get_module_names(path: str):
    modules = glob.glob(join(path, "*.py"))
    return [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")]
