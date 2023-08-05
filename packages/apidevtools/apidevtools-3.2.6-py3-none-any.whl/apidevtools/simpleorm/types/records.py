from typing import MutableMapping, Any, Coroutine, Iterator
from contextlib import suppress as _suppress

from .schema import Schema
from ...utils import is_dict as _is_dict


Instance = dict[str, Any] | Schema
Record = Instance | None
RecordType = type[Instance]


class Records:
    def __init__(self, records: list[MutableMapping], record_t: RecordType = dict[str, Any]):
        self.record_t: RecordType = record_t
        self._unwrap: Coroutine[Any, Any, Instance] = self._unwrapper()
        self._records: list[MutableMapping] = records
        self._aiter: Iterator = iter(records)

    def _unwrapper(self) -> Coroutine[Any, Any, Instance]:
        async def unwrap_to_dict(record: MutableMapping) -> dict[str, Any]:
            return dict(record)

        async def unwrap_to_schema(record: MutableMapping) -> Schema:
            return await self.record_t(**dict(record)).from_db()

        return unwrap_to_dict if _is_dict(self.record_t) else unwrap_to_schema

    def __len__(self) -> int:
        return len(self._records)

    def __aiter__(self) -> 'Records':
        return self

    async def __anext__(self) -> Instance:
        try:
            return await self._unwrap(next(self._aiter))
        except StopIteration:
            raise StopAsyncIteration

    async def all(self) -> list[Instance]:
        return [await self._unwrap(record) for record in self._records]

    async def first(self) -> Record:
        try:
            return await self._unwrap(self._records[0])
        except IndexError:
            return None

    async def last(self) -> Record:
        try:
            return await self._unwrap(self._records[-1])
        except IndexError:
            return None

    def limit(self, length: int) -> 'Records':
        with _suppress(IndexError):
            self._records = self._records[:length]
        return self

    def offset(self, length: int) -> 'Records':
        with _suppress(IndexError):
            self._records = self._records[length:]
        return self

    def order_by(self, columns: str | list[str], direction: str = 'ASC') -> 'Records':
        columns = columns if isinstance(columns, list) else [columns]

        def keys(record) -> tuple[str, ...]:
            if not isinstance(record, dict):
                record = dict(record)
            return tuple([record[column] for column in columns])
        self._records = sorted(
            self._records,
            key=columns if isinstance(columns, str) else keys,
            reverse=(direction.upper() == 'DESC')
        )
        return self
