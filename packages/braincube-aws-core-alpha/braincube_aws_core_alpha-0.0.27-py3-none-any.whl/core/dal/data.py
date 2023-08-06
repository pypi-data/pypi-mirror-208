from enum import Enum
from dataclasses import dataclass

from ..utils.data import Order, OrderType

from pypika import Table, Field


class Key:
    def __init__(self, *args):
        self.values = list(args)


class SaveType(Enum):
    insert = "INSERT"
    update = "UPDATE"


class JoinType(Enum):
    inner = ""
    left = "LEFT"
    right = "RIGHT"
    outer = "FULL OUTER"
    left_outer = "LEFT OUTER"
    right_outer = "RIGHT OUTER"
    full_outer = "FULL OUTER"
    cross = "CROSS"
    hash = "HASH"


@dataclass()
class JoinThrough:
    from_column_name: str
    to_column_name: str


@dataclass()
class SimpleColumn:
    name: str
    alias: str | None = None


@dataclass()
class Column:
    name: str
    alias: str | None = None
    updatable: bool = True
    insertable: bool = True


@dataclass()
class StatementField:
    alias: str
    statement: str
    relations_aliases: list[str] | None = None


@dataclass()
class Relation:
    table: str
    columns: list[SimpleColumn]
    join_type: JoinType
    join_through: JoinThrough
    join_forced: bool = False
    alias: str | None = None


@dataclass()
class Schema:
    table: str
    primary_key: list[str]
    columns: list[Column]
    statement_fields: list[StatementField] | None = None
    relations: list[Relation] | None = None
    order: list[Order] | None = None
    alias: str | None = None


class FieldType(Enum):
    column = "COLUMN"
    statement = "STATEMENT"
    related_column = "RELATED_COLUMN"


@dataclass()
class FieldData:
    type_: FieldType
    field: Field
    name: str = None
    updatable: bool = False
    insertable: bool = False
    statement: str = None
    relations_aliases: list[str] = None


@dataclass()
class OrderData:
    field: Field
    order_type: OrderType


@dataclass()
class TableData:
    name: str
    table: Table


@dataclass()
class RelatedTableData:
    table: Table
    name: str
    join_type: JoinType
    join_through: JoinThrough
    join_forced: bool = False
