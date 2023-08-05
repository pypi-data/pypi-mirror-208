import aioredis as _aioredis
import loguru
from loguru._logger import Logger
from typing import Any

from ..utils import evaluate as _evaluate


class Redis:
    def __init__(self, database: int = 0,
                 host: str = 'localhost', port: int | str = 6379,
                 user: str | None = None, password: str | None = None,
                 logger: Logger = loguru.logger):
        self.database: int = database
        self.host: str = host
        self.port: str | int = port
        self.user: str | None = user
        self.password: str | None = password

        self.logger: Logger = logger
        self.pool: _aioredis.Redis | None = None

    async def create_pool(self) -> bool:
        try:
            self.pool = _aioredis.Redis(
                db=self.database, host=self.host, port=self.port, username=self.user, password=self.password
            )
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

    async def set(self, key: Any, value: Any) -> Any:
        try:
            if await self.pool.set(str(key), str(value)):
                return value
        except Exception as error:
            self.logger.error(error)
        return None

    async def get(self, key: Any, convert: bool = False) -> bytes | None:
        try:
            value = await self.pool.get(str(key))
            return _evaluate(value, convert)
        except Exception as error:
            self.logger.error(error)
            return None

    async def delete(self, key: Any, convert: bool = False) -> bytes | None:
        try:
            value = await self.pool.delete(str(key))
            return _evaluate(value, convert)
        except Exception as error:
            self.logger.error(error)
            return None

