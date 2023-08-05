from loguru._logger import Logger
from typing import Any
import loguru
import inspect as _inspect

from ..utils import INF, is_dict as _is_dict
from .types import RecordType, Record, Schema, Records, Relation, Instance
from .connectors._connector import Connector


class ORM:
    def __init__(self, connector: Connector, logger: Logger = loguru.logger):
        self.connector: Connector = connector
        self.logger: Logger = logger

    async def create_pool(self) -> bool:
        try:
            is_created = await self.connector.create_pool()
            self.logger.info(f'`ORM.connector: {self.connector.__class__.__name__}` pool created')
            return is_created
        except Exception as error:
            self.logger.error(error)
            return False

    async def close_pool(self) -> bool:
        try:
            is_closed = await self.connector.close_pool()
            self.logger.info(f'`ORM.connector: {self.connector.__class__.__name__}` pool closed')
            return is_closed
        except Exception as error:
            self.logger.error(f'{error}')
            return False

    async def execute(self, query: str, args: tuple[Any, ...] = ()) -> Any:
        return await self.connector.execute(query, args)

    async def select(
            self,
            query: str, args: tuple[Any, ...] = (), record_t: RecordType = dict[str, Any],
            *, rel_depth: int = 0
    ) -> Records:
        records = Records(await self.connector.fetchall(query, args), record_t)
        if rel_depth and _is_dict(record_t):
            self.logger.warning(f'`ORM.select(..., rel_depth={rel_depth})` but `record_t` is not `Schema` ({record_t})')
        for index, record in enumerate(await records.all()) if not _is_dict(record_t) and rel_depth else ():
            for relation in record.relations():
                query, args = await self.connector._constructor__select_relations(relation)
                instances = await (await self.select(query, args, relation.rel_schema_t, rel_depth=rel_depth - 1)).all()
                records, record = await self.__attach_instances(records, record, relation, instances, index)
        return records

    async def insert(
            self,
            instance: Instance, record_t: RecordType = dict[str, Any], tablename: str = None
    ) -> Record:
        instance, tablename = await self.__parse_parameters(instance, tablename)
        query, args = await self.connector._constructor__insert_instance(instance, tablename)
        return await Records(await self.connector.fetchall(query, args), record_t).first()

    async def update(
            self,
            instance: Instance, where: dict[str, Any], record_t: RecordType = dict[str, Any], tablename: str = None,
            *, rel_depth: int = 0
    ) -> Records:
        instance, tablename = await self.__parse_parameters(instance, tablename)
        query, args = await self.connector._constructor__update_instances(instance, tablename, where)
        records = Records(await self.connector.fetchall(query, args), record_t)
        if rel_depth and _is_dict(record_t):
            self.logger.warning(f'`ORM.update(..., rel_depth={rel_depth})` but `record_t` is not `Schema` ({record_t})')
        for index, record in enumerate(await records.all()) if not _is_dict(record_t) and rel_depth else ():
            for relation in record.relations():
                query, args = await self.connector._constructor__select_relations(relation)
                instances = await (await self.select(query, args, relation.rel_schema_t, rel_depth=rel_depth - 1)).all()
                records, record = await self.__attach_instances(records, record, relation, instances, index)
        return records

    async def delete(
            self,
            instance: Instance, record_t: RecordType = dict[str, Any], tablename: str = None,
            *, rel_depth: int = 0, del_depth: int = INF
    ) -> Records:
        instance, tablename = await self.__parse_parameters(instance, tablename)
        query, args = await self.connector._constructor__select_instances(instance, tablename)
        records = await self.select(query, args, record_t)
        if del_depth and _is_dict(record_t):
            self.logger.warning(f'`ORM.delete(..., del_depth={del_depth})` but `record_t` is not `Schema` ({record_t})')
        if rel_depth and _is_dict(record_t):
            self.logger.warning(f'`ORM.delete(..., rel_depth={rel_depth})` but `record_t` is not `Schema` ({record_t})')
        for index, record in enumerate(await records.all()) if not _is_dict(record_t) and del_depth else ():
            for relation in record.relations():
                instances = await (await self.delete(
                    relation.where, relation.rel_schema_t, relation.rel_schema_t.__tablename__, del_depth=del_depth - 1
                )).all()
                if rel_depth:
                    records, record = await self.__attach_instances(records, record, relation, instances, index)
        await self.connector.execute(*(await self.connector._constructor__delete_instances(instance, tablename)))
        return records

    async def __attach_instances(
            self,
            records: Records, record: Record, relation: Relation, instances: list[Schema], index: int
    ) -> tuple[Records, Record]:
        if isinstance(record, dict):
            record[relation.propname] = instances
        elif isinstance(record, Schema):
            record = relation.ext_schema_t(**dict(record))
            setattr(record, relation.propname, instances)
        records._records[index] = relation.ext_schema_t(**dict(record))
        return records, record

    async def __parse_parameters(
            self,
            instance: Instance, tablename: str
    ) -> tuple[dict[str, Any], str]:
        if isinstance(instance, Schema):
            tablename = instance.__tablename__
            noupdate = instance.__noupdate__
            instance = dict(await instance.into_db())
            if _inspect.stack()[1][3] == 'update':
                for key in noupdate:
                    instance.pop(key)
        if not tablename:
            raise AttributeError('Specify "tablename" if "instance" is a "dict", otherwise pass "Schema" object')
        db_columns = await self.connector.columns(tablename)
        instance_columns = set(instance.keys())
        columns = instance_columns.intersection(db_columns)
        for key in instance_columns.difference(db_columns):
            if key not in columns:
                instance.pop(key)
        return instance, tablename
