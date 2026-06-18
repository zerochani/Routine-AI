from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from db import get_db

router = APIRouter(prefix="/routines", tags=["routines"])


class RoutineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    time: str
    repeat_type: str = "daily"


class RoutineUpdate(BaseModel):
    active: bool


@router.get("")
async def list_routines(today: bool = False):
    async with get_db() as db:
        if today:
            today_str = date.today().isoformat()
            is_weekend = int(date.today().weekday() >= 5)
            rows = await db.fetch(
                """SELECT r.*, c.status as completion_status
                   FROM routines r
                   LEFT JOIN completions c ON r.id = c.routine_id AND c.date = $1
                   WHERE r.active = 1 AND (
                     r.repeat_type = 'daily'
                     OR (r.repeat_type = 'weekdays' AND $2 = 0)
                     OR (r.repeat_type = 'weekends' AND $2 = 1)
                   )""",
                today_str, is_weekend
            )
        else:
            rows = await db.fetch("SELECT * FROM routines ORDER BY time")
        return [dict(r) for r in rows]


@router.post("")
async def create_routine(routine: RoutineCreate):
    async with get_db() as db:
        row = await db.fetchrow(
            "INSERT INTO routines (name, description, time, repeat_type) VALUES ($1, $2, $3, $4) RETURNING id",
            routine.name, routine.description, routine.time, routine.repeat_type
        )
        return {"id": row["id"], **routine.model_dump()}


@router.patch("/{routine_id}")
async def update_routine(routine_id: int, update: RoutineUpdate):
    async with get_db() as db:
        await db.execute(
            "UPDATE routines SET active = $1 WHERE id = $2",
            int(update.active), routine_id
        )
        return {"id": routine_id, "active": update.active}


@router.delete("/{routine_id}")
async def delete_routine(routine_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM completions WHERE routine_id = $1", routine_id)
        await db.execute("DELETE FROM routines WHERE id = $1", routine_id)
        return {"deleted": routine_id}


@router.get("/{routine_id}/streak")
async def get_streak(routine_id: int):
    async with get_db() as db:
        rows = await db.fetch(
            "SELECT date, status FROM completions WHERE routine_id = $1 AND status = 'done' ORDER BY date DESC",
            routine_id
        )

    if not rows:
        return {"streak": 0}

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
