import os
from fastapi import APIRouter
from pydantic import BaseModel
from db import get_db

router = APIRouter(prefix="/push", tags=["push"])

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")


class PushSubscription(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    return {"key": VAPID_PUBLIC_KEY}


@router.post("/subscribe")
async def subscribe(sub: PushSubscription):
    async with get_db() as db:
        await db.execute(
            """INSERT OR REPLACE INTO push_subscriptions (endpoint, p256dh, auth)
               VALUES (?, ?, ?)""",
            (sub.endpoint, sub.p256dh, sub.auth)
        )
        await db.commit()
    return {"subscribed": True}


@router.delete("/subscribe")
async def unsubscribe(sub: PushSubscription):
    async with get_db() as db:
        await db.execute(
            "DELETE FROM push_subscriptions WHERE endpoint = ?",
            (sub.endpoint,)
        )
        await db.commit()
    return {"unsubscribed": True}
