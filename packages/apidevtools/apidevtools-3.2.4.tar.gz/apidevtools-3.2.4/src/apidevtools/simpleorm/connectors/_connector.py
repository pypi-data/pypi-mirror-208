from abc import abstractmethod
from typing import Any, MutableMapping

from ..types import Relation


class Connector:
    def __init__(self, placeholder: str | None = '%s', constraint_wrapper: str | None = '', value_wrapper: str | None = "'"):
        self.placeholder: str | None = placeholder
        self.constraint_wrapper: str | None = constraint_wrapper
        self.value_wrapper: str | None = value_wrapper

    @abstractmethod
    async def create_pool(self) -> bool:
        ...

    @abstractmethod
    async def close_pool(self) -> bool:
        ...

    @abstractmethod
    async def execute(self, query: str, args: tuple[Any, ...] = ()) -> Any:
        ...

    @abstractmethod
    async def columns(self, tablename: str) -> list[str]:
        ...

    @abstractmethod
    async def fetchall(self, query: str, args: tuple[Any, ...] = ()) -> list[MutableMapping]:
        ...

    @abstractmethod
    async def _constructor__select_relations(
            self, relation: Relation
    ) -> tuple[str, tuple[Any, ...]]:
        p, c, v = self.placeholder, self.constraint_wrapper, self.value_wrapper

        conditions = ' AND '.join([f'{c}{key}{c} = {p}' for key in relation.where.keys()])
        return f'SELECT * FROM {c}{relation.rel_schema_t.__tablename__}{c} WHERE {conditions};', tuple(relation.where.values())

    @abstractmethod
    async def _constructor__select_instances(
            self,
            instance: dict, tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        p, c, v = self.placeholder, self.constraint_wrapper, self.value_wrapper

        conditions = ' AND '.join([f'{c}{key}{c} = {p}' for key in instance.keys()])
        return f'SELECT * FROM {c}{tablename}{c} WHERE {conditions};', tuple(instance.values())

    @abstractmethod
    async def _constructor__insert_instance(
            self,
            instance: dict, tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        p, c, v = self.placeholder, self.constraint_wrapper, self.value_wrapper

        placeholders = ', '.join([p for _ in range(len(instance.keys()))])
        columns, values = str(tuple(instance.keys())).replace("'", v), tuple(instance.values())
        return f'INSERT INTO {c}{tablename}{c} {columns} VALUES ({placeholders}) RETURNING *;', values

    @abstractmethod
    async def _constructor__update_instances(
            self,
            instance: dict, tablename: str, where: dict[str, Any]
    ) -> tuple[str, tuple[Any, ...]]:
        p, c, v = self.placeholder, self.constraint_wrapper, self.value_wrapper

        values = ', '.join([f'{c}{key}{c} = {p}' for key in instance.keys()])
        conditions = ' AND '.join([f'{c}{key}{c} = {p}' for key in where.keys()])
        return f'UPDATE {c}{tablename}{c} SET {values} WHERE {conditions} RETURNING *;', (*instance.values(), *where.values())

    @abstractmethod
    async def _constructor__delete_instances(
            self,
            instance: dict, tablename: str
    ) -> tuple[str, tuple[Any, ...]]:
        p, c, v = self.placeholder, self.constraint_wrapper, self.value_wrapper

        conditions = ' AND '.join([f'{c}{key}{c} = {p}' for key in instance.keys()])
        return f'DELETE FROM {c}{tablename}{c} WHERE {conditions} RETURNING *;', tuple(instance.values())
