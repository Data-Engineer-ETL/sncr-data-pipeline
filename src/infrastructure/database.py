"""Database connection and session management."""
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from asyncpg import Pool

from src.infrastructure.config import get_settings


class Database:
    """Database connection manager with connection pooling."""
    
    def __init__(self) -> None:
        self._pool: Optional[Pool] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.settings.POSTGRES_HOST,
                port=self.settings.POSTGRES_PORT,
                database=self.settings.POSTGRES_DB,
                user=self.settings.POSTGRES_USER,
                password=self.settings.POSTGRES_PASSWORD,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a connection from the pool."""
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a connection and start a transaction."""
        async with self.acquire() as conn:
            async with conn.transaction():
                yield conn


# Global database instance
db = Database()


async def get_db() -> Database:
    """Dependency for getting database instance."""
    return db
