import asyncio
import logging
from typing import Optional
import httpx
from app.config import settings

logger = logging.getLogger("telegram_bot")

async def send_telegram_notification(title: str, description: Optional[str] = None, item_id: Optional[str] = None):
    """Send push notification to Telegram user when AI creates a new question/decision in the queue."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_ADMIN_CHAT_ID:
        return

    text = f"🤖 <b>AI требует вашего решения!</b>\n\n<b>{title}</b>"
    if description:
        text += f"\n\n<i>{description[:200]}</i>"

    webapp_url = settings.TELEGRAM_WEBAPP_URL

    payload = {
        "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "📱 Открыть Action Queue",
                        "web_app": {"url": webapp_url}
                    }
                ]
            ]
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json=payload,
                timeout=10.0
            )
            if res.status_code != 200:
                logger.warning(f"Telegram notification failed: {res.text}")
    except Exception as e:
        logger.warning(f"Failed to send Telegram notification: {e}")
