from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
import aiosqlite
from db import get_db

router = APIRouter(prefix="/routines", tags=["routines"])


class RoutineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    time: str  # "HH:MM"
    repeat_type: str = "daily"  # daily | weekdays | weekends


class RoutineUpdate(BaseModel):
    active: bool


@router.get("")
async def list_routines(today: bool = False):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        if today:
            today_str = date.today().isoformat()
            weekday = date.today().weekday()  # 0=Mon, 6=Sun
            is_weekend = weekday >= 5
            repeat_filter = "active = 1 AND (repeat_type = 'daily' OR (repeat_type = 'weekdays' AND ? = 0) OR (repeat_type = 'weekends' AND ? = 1))"
            async with db.execute(
                f"SELECT r.*, c.status as completion_status FROM routines r LEFT JOIN completions c ON r.id = c.routine_id AND c.date = ? WHERE {repeat_filter}",
                (today_str, int(is_weekend), int(is_weekend))
            ) as cursor:
                rows = await cursor.fetchall()
        else:
            async with db.execute("SELECT * FROM routines ORDER BY time") as cursor:
                rows = await cursor.fetchall()
        return [dict(r) for r in rows]


@router.post("")
async def create_routine(routine: RoutineCreate):
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO routines (name, description, time, repeat_type) VALUES (?, ?, ?, ?)",
            (routine.name, routine.description, routine.time, routine.repeat_type)
        )
        await db.commit()
        return {"id": cursor.lastrowid, **routine.model_dump()}


@router.patch("/{routine_id}")
async def update_routine(routine_id: int, update: RoutineUpdate):
    async with get_db() as db:
        await db.execute(
            "UPDATE routines SET active = ? WHERE id = ?",
            (int(update.active), routine_id)
        )
        await db.commit()
        return {"id": routine_id, "active": update.active}


@router.delete("/{routine_id}")
async def delete_routine(routine_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM completions WHERE routine_id = ?", (routine_id,))
        await db.execute("DELETE FROM routines WHERE id = ?", (routine_id,))
        await db.commit()
        return {"deleted": routine_id}


@router.get("/{routine_id}/streak")
async def get_streak(routine_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT date, status FROM completions WHERE routine_id = ? AND status = 'done' ORDER BY date DESC",
            (routine_id,)
        ) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        return {"streak": 0}

    from datetime import timedelta
    streak = 0
    check = date.today()
    for row in rows:
        row_date = date.fromisoformat(row["date"])
        if row_date == check:
            streak += 1
            check -= timedelta(days=1)
        elif row_date < check:
            break

    return {"streak": streak}
