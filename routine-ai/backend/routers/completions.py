from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from db import get_db

router = APIRouter(prefix="/completions", tags=["completions"])


class CompletionCreate(BaseModel):
    routine_id: int
    status: str  # done | skip
    date: str = ""


@router.post("")
async def create_completion(body: CompletionCreate):
    record_date = body.date or date.today().isoformat()
    async with get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO completions (routine_id, date, status) VALUES (?, ?, ?)",
            (body.routine_id, record_date, body.status)
        )
        await db.commit()
    return {"routine_id": body.routine_id, "date": record_date, "status": body.status}


@router.get("")
async def list_completions(routine_id: int = None, date_str: str = None):
    async with get_db() as db:
        import aiosqlite
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM completions WHERE 1=1"
        params = []
        if routine_id:
            query += " AND routine_id = ?"
            params.append(routine_id)
        if date_str:
            query += " AND date = ?"
            params.append(date_str)
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        return [dict(r) for r in rows]
