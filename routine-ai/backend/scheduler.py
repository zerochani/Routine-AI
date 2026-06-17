import asyncio
import os
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from claude_client import generate_notification_message
import aiosqlite

DB_PATH = os.getenv("DB_PATH", "routine.db")


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _check_and_send():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    weekday = now.weekday()  # 0=Mon, 6=Sun
    is_weekend = weekday >= 5

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # 이 시간에 발송해야 할 루틴 조회
        async with db.execute(
            """SELECT * FROM routines
               WHERE active = 1 AND time = ?
               AND (
                 repeat_type = 'daily'
                 OR (repeat_type = 'weekdays' AND ? = 0)
                 OR (repeat_type = 'weekends' AND ? = 1)
               )""",
            (current_time, int(is_weekend), int(is_weekend))
        ) as cursor:
            routines = await cursor.fetchall()

        if not routines:
            return

        # 구독 목록 조회
        async with db.execute("SELECT * FROM push_subscriptions") as cursor:
            subscriptions = await cursor.fetchall()

        if not subscriptions:
            return

    for routine in routines:
        try:
            message = generate_notification_message(routine["name"], routine["description"] or "")
            await _send_push_to_all(subscriptions, routine["name"], message)
        except Exception as e:
            print(f"[Scheduler] Error for routine {routine['name']}: {e}")


async def _send_push_to_all(subscriptions, title: str, body: str):
    import json
    from pywebpush import webpush, WebPushException

    vapid_private = os.getenv("VAPID_PRIVATE_KEY", "")
    vapid_claims = {"sub": os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")}

    import base64
    private_key_pem = base64.urlsafe_b64decode(vapid_private + "==").decode("utf-8")

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]},
                },
                data=json.dumps({"title": title, "body": body}),
                vapid_private_key=private_key_pem,
                vapid_claims=vapid_claims,
            )
        except WebPushException as e:
            print(f"[Push] Failed to send to {sub['endpoint'][:30]}...: {e}")


def check_and_send_notifications():
    _run_async(_check_and_send())


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_notifications, "cron", minute="*")
    return scheduler
