import asyncpg as _asyncpg
from loguru._logger import Logger
from typing import Any, MutableMapping
import loguru

from ..types import Relation
from ._connector import Connector


class PostgreSQL(Connector):
    def __init__(self, database: str,
                 host: str = 'localhost', port: int | str = 5432,
                 user: str = 'postgres', password: str | None = None,
                 logger: Logger = loguru.logger):
        self.database: str = database
        self.host: str = host
        self.port: str | int = port
        self.user: str = user
        self.password: str | None = password

        self.logger: Logger = logger
        self.pool: _asyncpg.pool.Pool | None = None

        super().__init__(None, None, None)

    async def create_pool(self) -> bool:
        try:
            self.pool = await _asyncpg.pool.create_pool(
                database=self.database, host=self.host, port=self.port, user=self.user, password=self.password
            )
            return True
        except OSError:
            self.logger.error('Pool creation failed')
            return False

    async def close_pool(self) -> bool:
        try:
            await self.pool.expire_connections()
            await self.pool.close()
            return True
        except AttributeError:
            self.logger.error(f'Attempting to close not acquired pool')
            return False

    async def execute(self, query: str, args: tuple[Any, ...] = ()) -> Any:
        try:
            async with self.pool.acquire() as connection:
                return await connection.execute(query, *args)
        except Exception as error:
            self.logger.error(error)

    async def columns(self, tablename: str) -> list[str]:
        query, args = 'SELECT "column_name" FROM "information_schema"."columns" WHERE "table_name" = $1;', (tablename,)
        async with self.pool.acquire() as connection:
            return [dict(record)['column_name'] for record in await connection.fetch(query, *args)]

    async def fetchall(self, query: str, args: tuple[Any, ...] = ()) -> list[MutableMapping]:
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetch(query, *args)
        except Exception as error:
            self.logger.error(error)
            return []

    async def _constructor__select_relations(
            self, relation: Relation
    ) -> tuple[str, tuple[Any, ...]]:
        conditions = ' AND '.join([f'"{key}" = ${index + 1}' for index, key in enumerate(relation.where.keys())])
        return f'SELECT * FROM "{relation.rel_schema_t.__tablename__}" WHERE {conditions};', tuple(relation.where.values())

    async def _constructor__select_instances(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        conditions = ' AND '.join([f'"{key}" = ${index + 1}' for index, key in enumerate(instance.keys())])
        return f'SELECT * FROM "{tablename}" WHERE {conditions};', tuple(instance.values())

    async def _constructor__insert_instance(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        placeholders = ', '.join([f'${index + 1}' for index in range(len(instance.keys()))])
        columns, values = str(tuple(instance.keys())).replace("'", '"'), instance.values()
        return f'INSERT INTO "{tablename}" {columns} VALUES ({placeholders}) RETURNING *;', tuple(values)

    async def _constructor__update_instances(
            self,
            instance: dict[str, Any], tablename: str, where: dict[str, Any]
    ) -> tuple[str, tuple[Any, ...]]:
        values = ', '.join([f'"{key}" = ${index + 1}' for index, key in enumerate(instance.keys())])
        conditions = ' AND '.join([f'"{key}" = \'{value}\'' for key, value in where.items()])
        return f'UPDATE "{tablename}" SET {values} WHERE {conditions} RETURNING *;', tuple(instance.values())

    async def _constructor__delete_instances(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        conditions = ' AND '.join([f'"{key}" = ${index + 1}' for index, key in enumerate(instance.keys())])
        return f'DELETE FROM "{tablename}" WHERE {conditions} RETURNING *;', tuple(instance.values())
