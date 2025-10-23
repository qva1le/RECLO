import logging
import redis.asyncio as redis

class RedisManager:
    def __init__(self, host: str, port: int, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.redis: redis.Redis | None = None

    async def connect(self):
        logging.info(f"Connecting to Redis host={self.host}, port={self.port}, db={self.db}")
        self.redis = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        logging.info("Redis connected successfully")

    async def set(self, key: str, value: str, expire: int | None = None):
        if not self.redis:
            raise RuntimeError("Redis is not connected")
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str) -> str | None:
        if not self.redis:
            raise RuntimeError("Redis is not connected")
        return await self.redis.get(key)

    async def delete(self, key: str):
        if not self.redis:
            raise RuntimeError("Redis is not connected")
        await self.redis.delete(key)

    async def ttl(self, key: str) -> int:
        if not self.redis:
            raise RuntimeError("Redis is not connected")
        return await self.redis.ttl(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            await self.redis.connection_pool.disconnect()
            logging.info("Redis connection closed")
