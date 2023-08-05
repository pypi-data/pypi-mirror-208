from pydantic import BaseModel
from abc import abstractmethod as _abstractmethod, ABC
from typing import Any


class Relation:
    def __init__(self, ext_schema_t: type['Schema'], propname: str, rel_schema_t: type['Schema'], where: dict[str, Any]):
        self.ext_schema_t: type['Schema'] = ext_schema_t
        self.propname: str = propname
        self.rel_schema_t: type['Schema'] = rel_schema_t
        self.where: dict[str, Any] = where


class Schema(BaseModel, ABC):
    __noupdate__ = []

    @property
    @_abstractmethod
    def __tablename__(self) -> str:
        ...

    def relations(self) -> list[Relation]:
        return []

    async def into_db(self) -> 'Schema':
        return self

    async def from_db(self) -> 'Schema':
        return self
