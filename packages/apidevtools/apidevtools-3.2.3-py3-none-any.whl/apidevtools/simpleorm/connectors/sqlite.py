import aiosqlite as _aiosqlite
from loguru._logger import Logger
from typing import Any, MutableMapping
import loguru

from ..types import Relation
from ._connector import Connector


class SQLite(Connector):
    __memory = ':memory:'

    def __init__(self, database: str = __memory,
                 logger: Logger = loguru.logger):
        self.database: str = database if database.endswith(('.sqlite', '.db')) or database == self.__memory else f'{database}.sqlite'

        self.logger: Logger = logger
        self.pool: _aiosqlite.Connection | None = None

        super().__init__(placeholder='?', constraint_wrapper='"', value_wrapper="'")

    async def create_pool(self) -> bool:
        try:
            self.pool = await _aiosqlite.connect(database=self.database)
            return True
        except Exception as error:
            self.logger.error(error)
            return False

    async def close_pool(self) -> bool:
        try:
            await self.pool.close()
            return True
        except Exception as error:
            self.logger.error(error)
            return False

    async def execute(self, query: str, args: tuple[Any, ...] = ()) -> bool:
        try:
            await self.pool.execute(query, args) if len(args) else await self.pool.executescript(query)
            await self.pool.commit()
            return True
        except Exception as error:
            self.logger.error(error)
            return False

    async def columns(self, tablename: str) -> list[str]:
        cursor: _aiosqlite.Cursor = await self.pool.execute(f'SELECT * FROM {tablename}')
        return list(map(lambda x: x[0], cursor.description))

    async def fetchall(self, query: str, args: tuple[Any, ...] = ()) -> list[MutableMapping]:
        try:
            cursor: _aiosqlite.Cursor = await self.pool.execute(query, args)
            result = [{cursor.description[i][0]: value for i, value in enumerate(row)} for row in await cursor.fetchall()]
            await self.pool.commit()
            return result
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
        return await super()._constructor__insert_instance(instance, tablename)

    async def _constructor__update_instances(
            self,
            instance: dict[str, Any], tablename: str, where: dict[str, Any]
    ) -> tuple[str, tuple[Any, ...]]:
        return await super()._constructor__update_instances(instance, tablename, where)

    async def _constructor__delete_instances(
            self,
            instance: dict[str, Any], tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        return await super()._constructor__delete_instances(instance, tablename)
