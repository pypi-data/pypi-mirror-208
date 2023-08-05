import aiomysql as _aiomysql
from loguru._logger import Logger
from typing import Any, MutableMapping
import loguru

from ..types import Relation
from ._connector import Connector


class MySQL(Connector):
    def __init__(self, database: str,
                 host: str = 'localhost', port: int | str = 3306,
                 user: str = 'root', password: str | None = None,
                 logger: Logger = loguru.logger):
        self.database: str = database
        self.host: str = host
        self.port: str | int = port
        self.user: str = user
        self.password: str | None = password

        self.logger: Logger = logger
        self.pool: _aiomysql.Pool | None = None

        super().__init__(placeholder='%s', constraint_wrapper='`', value_wrapper="'")

    async def create_pool(self) -> bool:
        try:
            self.pool = await _aiomysql.create_pool(
                db=self.database, host=self.host, port=self.port, user=self.user, password=self.password
            )
            return True
        except Exception as error:
            self.logger.error(error)
            return False

    async def close_pool(self) -> bool:
        try:
            self.pool.close()
            return True
        except Exception as error:
            self.logger.error(error)
            return False

    async def execute(self, query: str, args: tuple[Any, ...] = ()) -> bool:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(_aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, args)
                    await connection.commit()
                    return True
        except Exception as error:
            self.logger.error(error)
            return False

    async def columns(self, tablename: str) -> list[str]:
        query, args = 'SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA` = %s AND `TABLE_NAME` = %s;', (self.database, tablename)
        async with self.pool.acquire() as connection:
            async with connection.cursor(_aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                await connection.commit()
                return [record['COLUMN_NAME'] for record in await cursor.fetchall()]

    async def fetchall(self, query: str, args: tuple[Any, ...] = ()) -> list[MutableMapping]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(_aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, args)
                    await connection.commit()
                    return await cursor.fetchall()
        except Exception as error:
            self.logger.error(error)
            return []

    async def _constructor__select_relations(
            self, relation: Relation
    ) -> tuple[str, tuple[Any, ...]]:
        return await super()._constructor__select_relations(relation)

    async def _constructor__select_instances(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        return await super()._constructor__select_instances(instance, tablename)

    async def _constructor__insert_instance(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        placeholders = ', '.join(['%s' for _ in range(len(instance.keys()))])
        columns, values = str(tuple(instance.keys())).replace("'", ''), tuple(instance.values())
        await self.execute(f'INSERT INTO {tablename} {columns} VALUES ({placeholders});', values)
        return f'SELECT * FROM `{tablename}` WHERE `id` = LAST_INSERT_ID();', ()

    async def _constructor__update_instances(
            self,
            instance: dict[str, Any], tablename: str, where: dict[str, Any]
    ) -> tuple[str, tuple[Any, ...]]:
        values = ', '.join([f'{key} = %s' for key in instance.keys()])
        conditions = ' AND '.join([f'{key} = %s' for key in where.keys()])
        await self.execute(f'UPDATE {tablename} SET {values} WHERE {conditions};', tuple(instance.values()) + tuple(where.values()))
        conditions = ' AND '.join([f'{key} = %s' for key in instance.keys()])
        return f'SELECT * FROM {tablename} WHERE {conditions};', tuple(instance.values())

    async def _constructor__delete_instances(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        conditions = ' AND '.join([f'{key} = %s' for key in instance.keys()])
        return f'DELETE FROM {tablename} WHERE {conditions};', tuple(instance.values())
