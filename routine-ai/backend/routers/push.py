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
            """INSERT INTO push_subscriptions (endpoint, p256dh, auth) VALUES ($1, $2, $3)
               ON CONFLICT (endpoint) DO UPDATE SET p256dh = EXCLUDED.p256dh, auth = EXCLUDED.auth""",
            sub.endpoint, sub.p256dh, sub.auth
        )
    return {"subscribed": True}


@router.delete("/subscribe")
async def unsubscribe(sub: PushSubscription):
    async with get_db() as db:
        await db.execute(
            "DELETE FROM push_subscriptions WHERE endpoint = $1",
            sub.endpoint
        )
    return {"unsubscribed": True}
