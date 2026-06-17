import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "routine.db")


def get_db():
    return aiosqlite.connect(DB_PATH)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS routines (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT,
                time        TEXT NOT NULL,
                repeat_type TEXT NOT NULL DEFAULT 'daily',
                active      INTEGER NOT NULL DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                routine_id INTEGER NOT NULL REFERENCES routines(id),
                date       TEXT NOT NULL,
                status     TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS push_subscriptions (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT UNIQUE NOT NULL,
                p256dh   TEXT NOT NULL,
                auth     TEXT NOT NULL
            )
        """)
        await db.commit()
