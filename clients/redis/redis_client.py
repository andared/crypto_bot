from redis import asyncio as aioredis
from settings import logger
import json


class AsyncRedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.client = None

    async def connect(self):
        self.client = await aioredis.from_url(f"redis://{self.host}:{self.port}/{self.db}")

    async def set_value(self, key, value):
        await self.client.set(key, json.dumps(value).encode())

    async def get_value(self, key):
        value = await self.client.get(key)
        return json.loads(value.decode()) if value else None

    async def delete_value(self, key):
        await self.client.delete(key)

    async def flush_all(self):
        await self.client.flushall()

    async def close(self):
        await self.client.close()


class CryptoRedis(AsyncRedisClient):
    async def set_crypto(self, name: str, data: dict):
        logger.info("Make write in redis")
        await super().set_value(name, data)

    async def get_crypto(self, name):
        logger.info("Get write from redis")
        return await super().get_value(name)


redis_client = CryptoRedis()
