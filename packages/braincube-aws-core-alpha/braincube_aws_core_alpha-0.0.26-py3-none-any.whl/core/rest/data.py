import json
from dataclasses import dataclass
from typing import Generic, TypeVar, Type
from http import HTTPStatus

from ..utils.convert import try_str_to_float
from ..utils.data import Order, OrderType, Condition, ConditionType, Pageable

reserved_keys = ["fields", "pageNo", "pageSize", "topSize", "order"]

T = TypeVar("T")


@dataclass()
class HTTPResponse:
    status: HTTPStatus
    body: any = None
    headers: dict[str, any] = None


@dataclass()
class QueryParameters:
    fields: list[str] = None
    conditions: list[Condition] = None
    page: Pageable = Pageable()
    order: list[Order] = None


@dataclass()
class HTTPRequest(Generic[T]):
    query_parameters: QueryParameters = QueryParameters()
    body: T = None
    headers: dict[str, any] = None
    path_parameters: dict[str, any] = None


def http_event_to_request(cls: Type[T], event: dict[str, any], context) -> HTTPRequest[T]:
    data = json.loads(event["body"]) if event.get("body") else None

    request = HTTPRequest(QueryParameters(),
                          cls(**data) if cls is not dict else data,
                          event.get("headers"),
                          event.get("pathParameters"))

    params: dict[str, any] | None = event.get("queryStringParameters")

    if params:
        fields = params["fields"].replace(" ", "").split(",") if params.get("fields") else list()
        pageable = Pageable(page_param(params, alias="pageNo"),
                            page_param(params, alias="pageSize", default=20, max_=50, min_=1),
                            page_param(params, alias="topSize", max_=1000, min_=-1))

        conditions = list()
        for k, v in params.items():
            key = k.strip()
            if key in reserved_keys:
                continue
            else:
                value = v.strip()
                value_ = value.lower()
                if value_.startswith("range(") and value_.endswith(")"):
                    condition_type = ConditionType.range
                    data = condition_param("range", value)
                    if not len(data) >= 2:
                        continue
                elif value_.startswith("any(") and value_.endswith(")"):
                    condition_type = ConditionType.any
                    data = condition_param("any", value)
                else:
                    condition_type = ConditionType.compare
                    data = try_str_to_float(value)
                conditions.append(Condition(condition_type, key, data))

        order = list()
        for order_ in (params["order"].split(",") if params.get("order") else list()):
            o = order_.strip().split(" ")
            if len(o) < 1:
                continue
            order_type = OrderType.asc
            if len(o) == 2:
                order_type = next((e for e in OrderType if e.value == o[1].upper()), None)
            if not order_type:
                continue
            order.append(Order(order_type, alias=o[0]))

        request.query_parameters = QueryParameters(fields, conditions, pageable, order)

    return request


def page_param(params: dict[str, any], alias: str, default: int = 0, max_: int = None, min_: int = 0) -> int:
    try:
        if not params.get(alias):
            return default
        value_ = int(params[alias])
        return value_ if (max_ >= value_ >= min_ if max_ else value_ >= min_) else default
    except ValueError:
        return default


def condition_param(type_, p) -> list:
    return [try_str_to_float(i) for i in p[len(type_) + 1:len(p) - 1].replace(" ", "").split(",")]
