import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from claude_client import stream_chat_async
from db import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


def _clean(s) -> str:
    if not s:
        return ""
    return str(s).encode("utf-8", errors="ignore").decode("utf-8")


async def process_action(action_data: dict):
    """Claude가 반환한 action JSON을 실제 DB 작업으로 처리"""
    action = action_data.get("action")
    if action == "add":
        async with get_db() as db:
            await db.execute(
                "INSERT INTO routines (name, description, time, repeat_type) VALUES ($1, $2, $3, $4)",
                _clean(action_data.get("name")),
                _clean(action_data.get("description")),
                _clean(action_data.get("time")) or "09:00",
                _clean(action_data.get("repeat")) or "daily",
            )
    elif action == "delete":
        name = action_data.get("name", "")
        async with get_db() as db:
            await db.execute(
                "UPDATE routines SET active = 0 WHERE name ILIKE $1",
                f"%{name}%"
            )


@router.post("")
async def chat(request: ChatRequest):
    messages = [m.model_dump() for m in request.messages]

    async def generate():
        full_text = ""
        try:
            async for text in stream_chat_async(messages):
                full_text += text
                yield f"data: {json.dumps({'delta': text})}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 첫 줄에서 action JSON 추출 후 처리
        first_line = full_text.strip().split("\n")[0].strip()
        try:
            action_data = json.loads(first_line)
            if action_data.get("action") not in (None, "none", "list"):
                try:
                    await process_action(action_data)
                except Exception as e:
                    import traceback
                    print(f"[process_action error] {e}")
                    traceback.print_exc()
            yield f"data: {json.dumps({'action': action_data})}\n\n"
        except (json.JSONDecodeError, ValueError):
            pass

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
