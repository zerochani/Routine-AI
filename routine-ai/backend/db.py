import os
import asyncpg
from contextlib import asynccontextmanager

_pool = None


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        url = os.getenv("DATABASE_URL", "")
        url = url.replace("postgres://", "postgresql://", 1)
        _pool = await asyncpg.create_pool(url)
    return _pool


@asynccontextmanager
async def get_db():
    pool = await _get_pool()
    async with pool.acquire() as conn:
        yield conn


async def init_db():
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS routines (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                time TEXT NOT NULL,
                repeat_type TEXT NOT NULL DEFAULT 'daily',
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id SERIAL PRIMARY KEY,
                routine_id INTEGER NOT NULL REFERENCES routines(id),
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                UNIQUE(routine_id, date)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS push_subscriptions (
                id SERIAL PRIMARY KEY,
                endpoint TEXT UNIQUE NOT NULL,
                p256dh TEXT NOT NULL,
                auth TEXT NOT NULL
            )
        """)
