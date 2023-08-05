# braincube-aws-core

Microframework for Python AWS lambdas.

[![Language](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![pypi](https://img.shields.io/pypi/v/braincube-aws-core-alpha.svg)](https://pypi.org/project/braincube-aws-core-alpha/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Installation

```bash
pip install braincube-aws-core-alpha
```

## Built With

- [asyncpg](https://github.com/MagicStack/asyncpg) - A fast PostgreSQL Database Client Library for Python/asyncio.
- [pydantic](https://github.com/pydantic/pydantic) - Data validation using Python type hints.
- [pypika](https://github.com/kayak/pypika) - Python Query Builder.

### Application Controllers Example

```python
import asyncio

from http import HTTPStatus

from core.rest.data import HTTPRequest, HTTPResponse
from core.rest.app_module import AppModule
from core.rest.app_controller import AppController

from pydantic import BaseModel


class AccountDto(BaseModel):
    id: int
    iban: str
    bban: str


_accounts = [
    AccountDto(1, "EUR27100777770209299700", "EURC12345612345678"),
    AccountDto(2, "GR27100777770209299700", "GRC12345612345678"),
]

app = AppController("/accounts")


@app.get("/{id}")
async def get_account(request: HTTPRequest) -> HTTPResponse:
    account = next((a for a in _accounts if a.id == request.path_parameters["id"]), None)
    return HTTPResponse(HTTPStatus.OK if account else HTTPStatus.NO_CONTENT, account)


@app.post()
async def create_account(request: HTTPRequest[AccountDto]) -> HTTPResponse:
    return HTTPResponse(HTTPStatus.OK)


loop = asyncio.get_event_loop()

module = AppModule([app])


def main(event, context):
    return loop.run_until_complete(module.serve(event, context))
```

### Dependency Injection Example

```python
from core.di.injector import inject
from core.dal.postgres_connection import get_pool, Pool


@inject("data_warehouse_pool")
async def provide_warehouse_pool() -> Pool:
    return await get_pool()


@inject(qualifier="pool:data_warehouse_pool")
class BankService:

    def __init__(self, pool: Pool):
        self._pool = pool
```

### Postgres Repository Example

```python
from core.rest.data import HTTPRequest
from core.utils.data import Order, OrderType
from core.dal.data import Key, Schema, Column, Relation, SimpleColumn, JoinType, JoinThrough, StatementField
from core.dal.postgres_connection import get_pool, Pool
from core.dal.postgres_repository import PostgresRepository

# schema definition
equities = Schema(
    table="equities",
    alias="e",
    primary_key=["id"],
    order=[Order(type=OrderType.asc, alias="name")],
    statement_fields=[
        StatementField(alias="isTypeOne",
                       statement="CASE WHEN e.type = 1 then True else False END",
                       relations_aliases=[])
    ],
    columns=[
        Column(name="id", updatable=False, insertable=False),
        Column(name="name"),
        Column(name="type"),
        Column(name="issuer_id", alias="issuerId"),
        Column(name="industry_sector", alias="industrySector"),
        Column(name="isin"),
        Column(name="reference"),
        Column(name="bloomberg_code", alias="bloombergCode"),
        Column(name="market_symbol", alias="marketSymbol"),
        Column(name="currency"),
        Column(name="country", ),
        Column(name="min_amount", alias="minAmount"),
    ],
    relations=[
        Relation(
            table="parties",
            alias="p",
            join_forced=False,
            columns=[
                SimpleColumn(name="name"),
                SimpleColumn(name="short_name", alias="shortName"),
            ],
            join_type=JoinType.left,
            join_through=JoinThrough(from_column_name="issuer_id", to_column_name="id")
        )
    ]
)


# repository definition
class EquitiesRepo(PostgresRepository):

    def __init__(self, pool: Pool):
        super().__init__(pool, equities)


# repository usage

request = HTTPRequest()

repo = EquitiesRepo(await get_pool())

await repo.find_by_id(key=Key(request.path_parameters["id"]), aliases=request.query_parameters.fields)

await repo.exists_by_id(key=Key("9448a57b-f686-4935-b152-566baab712db"))

await repo.find_one(
    aliases=request.query_parameters.fields,
    conditions=request.query_parameters.conditions,
    order=request.query_parameters.order)

await repo.find_all(
    aliases=request.query_parameters.fields,
    conditions=request.query_parameters.conditions,
    order=request.query_parameters.order)

await repo.find_all_by_id([
    Key("9448a57b-f686-4935-b152-566baab712db"),
    Key("43c8ec37-9a59-44eb-be90-def391ba2f02")],
    aliases=request.query_parameters.fields,
    order=request.query_parameters.order)

await repo.find_all_page(
    aliases=request.query_parameters.fields,
    conditions=request.query_parameters.conditions,
    page=request.query_parameters.page,
    order=request.query_parameters.order)

await repo.insert(
    data={
        "name": "Bursa de Valori Bucuresti SA",
        "type": 1,
        "industrySector": 40,
        "isin": "ROBVBAACNOR0",
        "bloombergCode": "BBG000BBWMC5",
        "marketSymbol": "BVB RO Equity",
        "currency": "RON",
        "country": "RO",
    })

await repo.insert_bulk(
    aliases=["name", "type", "industrySector", "isin", "bloombergCode", "marketSymbol", "currency", "country"],
    data=[
        ["Bursa de Valori Bucuresti SA", 1, 40, "ROBVBAACNOR0", "BBG000BBWMC5", "BVB RO Equity", "RON", "RO"],
        ["Citigroup Inc", 1, 40, "US1729674242", "BBG000FY4S11", "C US Equity", "USD", "US"],
        ["Coca-Cola HBC AG", 1, 49, "CH0198251305", "BBG004HJV2T1", "EEE GA Equity", "EUR", "GR"],
    ]
)

await repo.update(
    data={
        "type": 1,
        "isin": 40,
    },
    conditions=request.query_parameters.conditions,
    returning_aliases=request.query_parameters.fields)

await repo.update_by_id(
    Key("9448a57b-f686-4935-b152-566baab712db"),
    data={
        "type": 1,
        "isin": 40,
    }, returning_aliases=[])

await repo.delete(
    conditions=request.query_parameters.conditions,
    returning_aliases=["id", "name", "type"])

await repo.delete_by_id(
    Key("9448a57b-f686-4935-b152-566baab712db"),
    returning_aliases=["id", "name", "type"])

await repo.fetch_raw("SELECT * FROM equities WHERE type = $1 and isin = $2", [1, "TREEGYO00017"])

await repo.fetch_one_raw("SELECT * FROM equities WHERE id = $1", ["2b67122a-f47e-41b1-b7f7-53be5ca381a0"])

await repo.execute_raw("DELETE FROM equities WHERE id = $1", ["2b67122a-f47e-41b1-b7f7-53be5ca381a0"])
```

### Query params format

```
fields=name, type, industrySector, isin, bloombergCode, parties_name, parties_shortName

type=1
isin=range(40, 49)
id=any(9448a57b-f686-4935-b152-566baab712db, 43c8ec37-9a59-44eb-be90-def391ba2f02)

page_no=1
page_size=50
top_size=50
order=name, id DESC
```

### Local Development Requirements

To use the SAM CLI, you need the following tools.

* [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3](https://www.python.org/downloads/)
* [Docker](https://hub.docker.com/search/?type=edition&offering=community)

### Run server locally

```bash
# open ssh tunel
sudo sh ssh_tunnel_Analog_JBox.sh
# apply code changes to docker image
sam-api$ sam build
# start server locally on http://127.0.0.1:3000
sam-api$ sam local start-api --warm-containers EAGER
# or run function locally using event.json as parameter
sam-api$ sam local invoke ApiFunction --event events/event.json
```

### Deploy to AWS

```bash
sam build --use-container
sam deploy --guided --profile analog_user --region eu-west-1
```

### Build and deploy new package version using twine

```bash
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
```

```bash
python3 -m build
twine upload --skip-existing dist/*
```

### Resources

* [SAM template.yml](https://github.com/aws/serverless-application-model/blob/master/docs/internals/generated_resources.rst)
* [asyncpg driver](https://magicstack.github.io/asyncpg/current/)
* [PyPika query builder](https://pypika.readthedocs.io/en/latest/)
* [Pydantic](https://docs.pydantic.dev/)
