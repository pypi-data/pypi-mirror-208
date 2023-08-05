import time
import math
import itertools
from typing import TypeVar

from pydantic import BaseModel
from pypika.queries import QueryBuilder
from pypika import PostgreSQLQuery, Table, Field, Criterion, EmptyCriterion, CustomFunction, functions as fn

from ..utils.data import Order, OrderType, Condition, ConditionType, Page, Pageable, Paging, Top, Metadata
from .data import Key, Schema, SaveType, TableData, FieldData, RelatedTableData, OrderData, FieldType
from .database_errors import DatabaseError, DeleteError, SaveError
from .postgres_connection import Pool, Connection

T = TypeVar("T", bound=BaseModel)


class PostgresRepository:
    """SQL based repository implementation.
    :param pool: Database connection pool.
    :param schema: Representation of master and related tables including columns, sub-queries and storage restrictions.
    :param relation_separator: Character that will be used in order to separate related tables from each column.
    """

    def __init__(self, pool: Pool, schema: Schema, relation_separator: str = "_"):
        self._pool = pool
        self._relation_separator = relation_separator
        self.__construct_schema_data(schema)

    def __construct_schema_data(self, schema: Schema):

        # master table:
        self._master_table: TableData = \
            TableData(schema.table, Table(schema.table).as_(schema.alias) if schema.alias else Table(schema.table))

        # master columns:
        self._master_columns: dict[str, FieldData] = dict()
        for column in schema.columns:
            self._master_columns[column.alias if column.alias else column.name] = FieldData(
                FieldType.column,
                (self._master_table.table[column.name]).as_(column.alias)
                if column.alias else self._master_table.table[column.name],
                column.name,
                column.insertable,
                column.updatable
            )

        # statement fields:
        self._statement_fields: dict[str, FieldData] = dict()
        if schema.statement_fields:
            for statement_field in schema.statement_fields:
                self._statement_fields[statement_field.alias] = FieldData(
                    FieldType.statement,
                    self._master_table.table[statement_field.alias],
                    statement=statement_field.statement,
                    relations_aliases=statement_field.relations_aliases
                )

        # primary key:
        self._primary_key: dict[str, FieldData] = \
            dict(itertools.islice(self._master_columns.items(), len(schema.primary_key)))

        # related tables:
        self._related_tables: dict[str, RelatedTableData] = dict()
        self._related_columns: dict[str, FieldData] = dict()
        self._related_forced_tables_aliases: list[str] = list()

        if schema.relations:
            for relation in schema.relations:
                table_alias: str = relation.alias if relation.alias else relation.table
                related_table = Table(relation.table).as_(relation.alias) if relation.alias else Table(relation.table)
                self._related_tables[table_alias] = RelatedTableData(
                    related_table, relation.table, relation.join_type,
                    relation.join_through, relation.join_forced
                )
                if relation.join_forced:
                    self._related_forced_tables_aliases.append(table_alias)
                for column in relation.columns:
                    column_alias: str = \
                        f"{relation.table}{self._relation_separator}{column.alias if column.alias else column.name}"
                    self._related_columns[column_alias] = FieldData(
                        FieldType.related_column,
                        (related_table[column.name]).as_(column_alias),
                        column.name
                    )

        # related columns and fields:
        self._columns: dict[str, FieldData] = {**self._master_columns, **self._related_columns}
        self._columns_and_statement_fields: dict[str, FieldData] = {**self._columns, **self._statement_fields}

        # order by:
        self._order_by: list[OrderData] = list()
        if schema.order:
            self._order_by.extend([OrderData(self._columns_and_statement_fields[order.alias].field, order.type)
                                   for order in schema.order])
        else:
            self._order_by.extend([OrderData(pk.field, OrderType.asc) for pk in self._primary_key.values()])

    @staticmethod
    def __base_model_aliases(cls: type[T]) -> list[str]:
        return [f.alias for f in cls.__fields__.values()]

    async def fetch(self, q: str, params: list = None, connection: Connection = None):
        """Retrieve records from raw PSQL query.
        :param q: Query.
        :param params: Query parameters.
        :param connection: (asyncpg) Connection that will execute the query.
        :return: Records as dictionary.
        """

        try:
            print(f"query:: {q}")
            if connection:
                return [dict(r) for r in (await connection.fetch(q, *params) if params else await connection.fetch(q))]
            async with self._pool.acquire() as connection_:
                return [dict(r) for r in
                        (await connection_.fetch(q, *params) if params else await connection_.fetch(q))]
        except Exception as e:
            raise DatabaseError(e)

    async def fetch_one(self, q: str, params: list = None, connection: Connection = None) -> dict[str, any] | None:
        """Retrieve record from raw PSQL query.
        :param q: Query.
        :param params: Query parameters.
        :param connection: (asyncpg) Connection that will execute the query.
        :return: Record as dictionary.
        """

        data = await self.fetch(q, params, connection)

        return data[0] if data else None

    async def execute(self, q: str, params: list = None, connection: Connection = None) -> any:
        """Execute raw PSQL query.
        :param q: Query.
        :param params: Query parameters.
        :param connection: (asyncpg) Connection that will execute the query.
        :return: Execution results as dictionary.
        """

        return await self.fetch(q, params, connection)

    async def _fetch(self, q: QueryBuilder,
                     replace_fields: bool = True,
                     connection: Connection = None) -> list[dict[str, any]]:

        query = self._replace_statement_fields(q) if replace_fields else str(q)

        return await self.fetch(query, connection=connection)

    async def _fetch_one(self, q: QueryBuilder,
                         replace_fields: bool = True,
                         connection: Connection = None) -> dict[str, any] | None:

        data = await self._fetch(q, replace_fields, connection)

        return data[0] if data else None

    async def _execute(self, q: QueryBuilder,
                       returning_aliases: list[str] = None,
                       connection: Connection = None) -> any:

        table = Table(self._master_table.name)

        for field in self._aliases_to_fields(returning_aliases, select=False):
            field_ = field if isinstance(field, Field) else field.field
            q = q.returning(table[field_.name].as_(field_.alias))

        return await self._fetch(q, False, connection)

    def _create_primary_key_criterion(self, key: Key, select: bool = True) -> Criterion:
        return Criterion.all([f.field == key.values[i] if select else (Field(name=f.name) == key.values[i]) for i, f in
                              enumerate(self._primary_key.values())])

    def _aliases_to_fields(self, aliases: list[str] = None, select: bool = True) -> list[FieldData]:

        fields = list()
        accepted = self._columns_and_statement_fields if select else self._master_columns
        if aliases:
            for alias in aliases:
                field = accepted.get(alias)
                if not field:
                    continue
                fields.append(field)
        return fields if fields else list(
            self._master_columns.values() if select else self._primary_key.values())

    def _order_to_fields(self, order: list[Order]) -> list[OrderData]:

        data = list()
        for order_ in order:
            field_data = self._columns_and_statement_fields.get(order_.alias)
            if not field_data:
                continue
            data.append(OrderData(field_data.field, order_.type))

        return data if data else self._order_by

    def _conditions_to_criterion(self, conditions: list[Condition] = None, select: bool = True) -> Criterion:

        if not conditions:
            return EmptyCriterion()

        criteria = list()
        for con in conditions:
            field_data = self._columns.get(con.alias)
            if not field_data:
                continue
            field = field_data.field if select else Field(name=field_data.name)
            if isinstance(con.value, list):
                if con.type == ConditionType.range:
                    if con.value[0]:
                        criteria.append(con.value[0] <= field)
                    if con.value[1]:
                        criteria.append(field <= con.value[1])
                elif con.type == ConditionType.any:
                    any_func = CustomFunction("any", ["p1"])
                    criteria.append(field == any_func(con.value))
            else:
                criteria.append(field == con.value)

        return Criterion.all(criteria)

    def _replace_statement_fields(self, q: QueryBuilder) -> str:

        query = str(q)

        for field_data in self._statement_fields.values():
            query = query.replace(f"\"{self._master_table.table.alias}\".\"{field_data.field.name}\"",
                                  f"{field_data.statement} \"{field_data.field.name}\"")

        return query

    def _filter_save_data(self, data: dict[str, any], type_: SaveType) -> dict[str, any]:

        data_: dict[str, any] = dict()

        for k, v in data.items():
            column = self._master_columns.get(k)
            if not column:
                continue
            if type_ == SaveType.insert and not column.insertable:
                raise SaveError(f"column:'{column.name}' is not insertable", column.name)
            if type_ == SaveType.update and not column.updatable:
                raise SaveError(f"column:'{column.name}' is not updatable", column.name)
            data_[column.name] = v

        if not data_:
            raise SaveError("no columns provided")

        return data_

    def __init_select_query(self, fields: list[FieldData],
                            criterion: Criterion = None,
                            order: list[OrderData] = None,
                            count_query: bool = False) -> tuple[QueryBuilder, QueryBuilder | None]:

        q = PostgreSQLQuery.from_(self._master_table.table)

        table_aliases = self._related_forced_tables_aliases.copy()

        for field in fields:
            if field.type_ == FieldType.statement and field.relations_aliases:
                table_aliases.extend(field.relations_aliases)
            else:
                table_aliases.append(field.field.table.alias)

        if criterion:
            table_aliases.extend([t.alias for t in criterion.tables_])
            q = q.where(criterion)

        if order:
            table_aliases.extend([order_.field.table.alias for order_ in order])

        for alias in filter(lambda ta: ta != self._master_table.table.alias, set(table_aliases)):
            related_table = self._related_tables[alias]
            q = q \
                .join(related_table.table, related_table.join_type) \
                .on(self._master_table.table[related_table.join_through.from_column_name] ==
                    related_table.table[related_table.join_through.to_column_name])

        cq = q.select(fn.Count("*")) if count_query else None

        for field in fields:
            q = q.select(field.field)

        if order:
            for order_ in order:
                q = q.orderby(order_.field, order=order_.order_type)

        return q, cq

    def _init_select_query(self, aliases: list[str] = None,
                           criterion: Criterion = None,
                           order: list[Order] = None,
                           set_order: bool = True,
                           count_query: bool = False) -> tuple[QueryBuilder, QueryBuilder | None]:

        fields = self._aliases_to_fields(aliases)
        order_ = self._order_to_fields(order) if order else (self._order_by if set_order else None)

        return self.__init_select_query(fields, criterion, order_, count_query)

    async def _find_one(self, aliases: list[str] = None,
                        criterion: Criterion = None,
                        order: list[Order] = None,
                        connection: Connection = None) -> dict[str, any] | None:

        q, _ = self._init_select_query(aliases, criterion, order)

        return await self._fetch_one(q.limit(1), connection=connection)

    async def _find_all(self, aliases: list[str] = None,
                        criterion: Criterion = None,
                        order: list[Order] = None,
                        connection: Connection = None) -> list[dict[str, any]]:

        q, _ = self._init_select_query(aliases, criterion, order)

        return await self._fetch(q, connection=connection)

    async def _find_many(self, aliases: list[str] = None,
                         criterion: Criterion = None,
                         page: Pageable = Pageable(),
                         order: list[Order] = None,
                         connection: Connection = None) -> Page | Top:

        if connection:
            return await self.__find_many(connection, aliases, criterion, page, order)
        async with self._pool.acquire() as connection_:
            return await self.__find_many(connection_, aliases, criterion, page, order)

    async def __find_many(self, connection: Connection,
                          aliases: list[str] = None,
                          criterion: Criterion = None,
                          page: Pageable = Pageable(),
                          order: list[Order] = None) -> Page | Top:

        if page.top_size < 0:
            data = await self._find_all(aliases, criterion, order, connection)
            return Top(data, page.top_size, False)

        start = time.time()

        calc_top = page.top_size > 0
        q, cq = self._init_select_query(aliases, criterion, order, count_query=not calc_top)

        # top implementation
        if calc_top:
            records = await self._fetch(q.limit(page.top_size + 1), connection=connection)
            has_more = len(records) > page.top_size
            return Top(records[:-1] if has_more else records, page.top_size, has_more)

        # paging implementation
        page_no = page.page_no if page.page_no > 0 else 1
        records = await self._fetch(q.limit(page.page_size).offset((page_no - 1) * page.page_size),
                                    connection=connection)

        # retrieve count only if we do not mention page ether we are not on
        # first page and there are no records from first retrieve
        count = None
        total_pages = None
        retrieve_pre_page = len(records) == 0 and page.page_no > 1

        if retrieve_pre_page or page.page_no == 0:
            record = await self._fetch_one(cq, connection=connection)
            count = record["count"] if record.get("count") else 0
            total_pages = math.ceil(count / page.page_size)

        if retrieve_pre_page and total_pages > 0:
            page_no = total_pages
            records = await self._fetch(q.limit(page.page_size).offset((page_no - 1) * page.page_size),
                                        connection=connection)

        return Page(records, Paging(page_no, page.page_size, total_pages, count),
                    Metadata(int((time.time() - start) * 1000)))

    async def _update(self, data: BaseModel | dict[str, any],
                      criterion: Criterion,
                      returning_aliases: list[str] = None,
                      connection: Connection = None) -> list[dict[str, any]] | None:

        if isinstance(criterion, EmptyCriterion):
            raise SaveError("update without conditions is not allowed")

        uq = PostgreSQLQuery.update(self._master_table.name)

        data_ = data.dict(by_alias=True, exclude_unset=True) if isinstance(data, BaseModel) else data.copy()

        for v, k in self._filter_save_data(data_, SaveType.update).items():
            uq = uq.set(v, k)
        uq = uq.where(criterion)

        return await self._execute(uq, returning_aliases, connection)

    async def _delete(self, criterion: Criterion,
                      returning_aliases: list[str] = None,
                      connection: Connection = None) -> list[dict[str, any]] | None:

        if isinstance(criterion, EmptyCriterion):
            raise DeleteError("delete without conditions is not allowed")

        dq = PostgreSQLQuery \
            .from_(self._master_table.name) \
            .delete() \
            .where(criterion)

        return await self._execute(dq, returning_aliases, connection)

    async def find_by_pk(self, key: Key,
                         aliases: list[str] = None,
                         connection: Connection = None) -> dict[str, any] | None:
        """Find the record from passed key.
        :param key: Record identifier.
        :param aliases: List of fields that will be selected by the query.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :return: Record as dictionary.
        """

        criterion = self._create_primary_key_criterion(key)

        q, _ = self._init_select_query(aliases, criterion, set_order=False)

        return await self._fetch_one(q, connection=connection)

    async def exists_by_pk(self, key: Key, connection: Connection = None) -> bool:
        """Find if record exists from passed key.
        :param key: Record identifier.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :return: Record existence.
        """

        aliases = [pk.field.alias for pk in self._primary_key.values()]

        return await self.find_by_pk(key, aliases, connection) is not None

    async def find_one(self, aliases: list[str] = None,
                       conditions: list[Condition] = None,
                       order: list[Order] = None,
                       connection: Connection = None) -> dict[str, any] | None:
        """Find one record from passed filters.
        :param aliases: List of fields that will be selected by the query.
        :param conditions: List of filters that will be applied to query.
        :param order: Order that will be applied to query.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :return: Record as dictionary.
        """

        criterion = self._conditions_to_criterion(conditions)

        return await self._find_one(aliases, criterion, order, connection)

    async def find_all(self, aliases: list[str] = None,
                       conditions: list[Condition] = None,
                       order: list[Order] = None,
                       connection: Connection = None) -> list[dict[str, any]]:
        """Find all records from passed filters.
        :param aliases: List of fields that will be selected by the query.
        :param conditions: List of filters that will be applied to query.
        :param order: Order in which the records will be returned.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :return: Records as dictionary list.
        """

        criterion = self._conditions_to_criterion(conditions)

        return await self._find_all(aliases, criterion, order, connection)

    async def find_all_by_pk(self, keys: list[Key],
                             aliases: list[str] = None,
                             order: list[Order] = None,
                             connection: Connection = None) -> list[dict[str, any]]:
        """Find all records from passed keys.
        :param keys: Records identifiers.
        :param aliases: List of fields that will be selected by the query.
        :param order: Order in which the records will be returned.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :return: Record as dictionary.
        """

        if not keys:
            raise DatabaseError("no keys provided")

        criterion = Criterion.any([self._create_primary_key_criterion(key) for key in keys])

        return await self._find_all(aliases, criterion, order, connection)

    async def find_many(self, aliases: list[str] = None,
                        conditions: list[Condition] = None,
                        page: Pageable = Pageable(),
                        order: list[Order] = None,
                        connection: Connection = None) -> Page | Top:
        """Find records from passed filters using paging.
        :param aliases: List of fields that will be selected by the query.
        :param conditions: List of filters that will be applied to query.
        :param page: Limit and offset of the query.
        :param order: Order in which the records will be returned.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :return: Records wrapped by Page or Top dataclass.
        """

        criterion = self._conditions_to_criterion(conditions)

        return await self._find_many(aliases, criterion, page, order, connection)

    async def insert(self, data: BaseModel | dict[str, any],
                     returning_aliases: list[str] = None,
                     connection: Connection = None) -> dict[str, any]:
        """Insert one record from dictionary.
        :param data: Master column aliases with values.
        :param returning_aliases: Query returning data.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to insert-constraints or no master column is specified.
        :return: Execution results as dictionary.
        """

        data_ = self._filter_save_data(
            data.dict(by_alias=True, exclude_unset=True) if isinstance(data, BaseModel) else data.copy(),
            SaveType.insert
        )

        iq = PostgreSQLQuery \
            .into(self._master_table.name) \
            .columns(list(data_.keys())) \
            .insert(list(data_.values()))

        records = await self._execute(iq, returning_aliases, connection)

        return records[0] if len(records) > 0 else None

    async def insert_returning_master(self, data: BaseModel | dict[str, any],
                                      connection: Connection = None):
        """Insert one record from dictionary and return all master columns.
        :param data: Master column aliases with values.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to insert-constraints or no master column is specified.
        :return: Execution results as dictionary.
        """

        return await self.insert(data, list(self._master_columns.keys()), connection)

    async def insert_data(self, data: BaseModel | dict[str, any],
                          returning: type[T],
                          connection: Connection = None) -> T:
        """Insert a record using model.
        :param data: Model which contains master table column properties.
        :param returning: Result type.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to insert-constraints or no master column is specified.
        :return: Execution results with returning type.
        """

        result = await self.insert(data, self.__base_model_aliases(returning), connection)

        return returning(**result) if result else None

    async def insert_bulk(self, aliases: list[str],
                          data: list[list],
                          returning_aliases: list[str] = None,
                          connection: Connection = None) -> list[dict[str, any]]:
        """Insert many records at once from list.
        :param aliases: Master column aliases.
        :param data: Master column values.
        :param returning_aliases: Query returning data.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to insert-constraints or no master column is specified.
        :return: Execution result as dictionary list.
        """

        for d in data:
            if len(d) == len(aliases):
                continue
            raise SaveError("invalid bulk insert data")

        column_names: dict[str, int] = dict()
        for i, alias in enumerate(aliases):
            column = self._master_columns.get(alias)
            if not column:
                continue
            if not column.insertable:
                raise SaveError(f"column:'{column.name}' is not insertable", column.name)
            column_names[column.name] = i
        if not column_names:
            raise SaveError("no columns provided")

        iq = PostgreSQLQuery \
            .into(self._master_table.name) \
            .columns(list(column_names.keys()))

        for d in data:
            iq = iq.insert([d[i] for i in column_names.values()])

        return await self._execute(iq, returning_aliases, connection)

    async def update(self, data: BaseModel | dict[str, any],
                     conditions: list[Condition],
                     returning_aliases: list[str] = None,
                     connection: Connection = None) -> list[dict[str, any]] | None:
        """Update records with new data according conditions.
        :param data: Master column aliases with values.
        :param conditions: List of filters that will be applied into the query.
        :param returning_aliases: Query returning data.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to update-constraints or no master column is specified.
        :return: Execution results as dictionary list.
        """

        criterion = self._conditions_to_criterion(conditions, select=False)

        return await self._update(data, criterion, returning_aliases, connection)

    async def update_by_pk(self, key: Key,
                           data: BaseModel | dict[str, any],
                           returning_aliases: list[str] = None,
                           connection: Connection = None) -> dict[str, any] | None:
        """Update record with new data according to passed key.
        :param key: Record identifier.
        :param data: Master column aliases with values.
        :param returning_aliases: Query returning data.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to update-constraints or no master column is specified.
        :return: Execution result as dictionary.
        """

        criterion = self._create_primary_key_criterion(key, select=False)

        records = await self._update(data, criterion, returning_aliases, connection)

        return records[0] if len(records) > 0 else None

    async def update_data(self, data: BaseModel | dict[str, any],
                          conditions: list[Condition],
                          returning: type[T],
                          connection: Connection = None) -> list[T] | None:
        """Update records with new data according conditions using model.
        :param data: Model which contains master table column properties.
        :param conditions: List of filters that will be applied into the query.
        :param returning: Result type.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to update-constraints or no master column is specified.
        :return: Execution results with returning type.
        """

        results = await self.update(data, conditions, self.__base_model_aliases(returning), connection)

        return [returning(**r) for r in results] if results else None

    async def update_data_by_pk(self, key: Key,
                                data: BaseModel | dict[str, any],
                                returning: type[T],
                                connection: Connection = None) -> T | None:
        """Update record with new data according to passed key using model.
        :param key: Record identifier.
        :param data: Model which contains master table column properties.
        :param returning: Result type.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When does not adjust to update-constraints or no master column is specified.
        :return: Execution result with returning type.
        """

        result = await self.update_by_pk(key, data, self.__base_model_aliases(returning), connection)

        return returning(**result) if result else None

    async def delete(self, conditions: list[Condition],
                     returning_aliases: list[str] = None,
                     connection: Connection = None) -> list[dict[str, any]] | None:
        """Delete records according conditions.
        :param conditions: List of filters that will be applied into the query.
        :param returning_aliases: Query returning data.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When conditions are empty.
        :return: Execution results as dictionary list.
        """

        criterion = self._conditions_to_criterion(conditions, select=False)

        return await self._delete(criterion, returning_aliases, connection)

    async def delete_by_pk(self, key: Key,
                           returning_aliases: list[str] = None,
                           connection: Connection = None) -> dict[str, any] | None:
        """Delete records according to passed key.
        :param key: Record identifier.
        :param returning_aliases: Query returning data.
        :param connection: (asyncpg) Connection that will execute the generated query.
        :raise SaveError: When conditions are empty.
        :return: Execution results as dictionary.
        """

        criterion = self._create_primary_key_criterion(key, select=False)

        records = await self._delete(criterion, returning_aliases, connection)

        return records[0] if len(records) > 0 else None
