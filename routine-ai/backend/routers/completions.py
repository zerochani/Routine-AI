from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from db import get_db

router = APIRouter(prefix="/completions", tags=["completions"])


class CompletionCreate(BaseModel):
    routine_id: int
    status: str
    date: str = ""


@router.post("")
async def create_completion(body: CompletionCreate):
    record_date = body.date or date.today().isoformat()
    async with get_db() as db:
        await db.execute(
            """INSERT INTO completions (routine_id, date, status) VALUES ($1, $2, $3)
               ON CONFLICT (routine_id, date) DO UPDATE SET status = EXCLUDED.status""",
            body.routine_id, record_date, body.status
        )
    return {"routine_id": body.routine_id, "date": record_date, "status": body.status}


@router.get("")
async def list_completions(routine_id: int = None, date_str: str = None):
    async with get_db() as db:
        query = "SELECT * FROM completions WHERE 1=1"
        params = []
        i = 1
        if routine_id:
            query += f" AND routine_id = ${i}"
            params.append(routine_id)
            i += 1
        if date_str:
            query += f" AND date = ${i}"
            params.append(date_str)
        rows = await db.fetch(query, *params)
        return [dict(r) for r in rows]
