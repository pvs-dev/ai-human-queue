import logging
from typing import Optional
import httpx
from app.database import SessionLocal
from app.config import settings as env_settings
from app import crud

logger = logging.getLogger("telegram_bot")

async def send_telegram_notification(title: str, description: Optional[str] = None, item_id: Optional[str] = None):
    """Send push notification to Telegram user when AI creates a new question/decision in the queue."""
    bot_token = env_settings.TELEGRAM_BOT_TOKEN
    chat_id = env_settings.TELEGRAM_ADMIN_CHAT_ID
    webapp_url = env_settings.TELEGRAM_WEBAPP_URL

    try:
        db = SessionLocal()
        try:
            app_settings = crud.get_app_settings(db)
            if app_settings.telegram_bot_token:
                bot_token = app_settings.telegram_bot_token
            if app_settings.telegram_admin_chat_id:
                chat_id = app_settings.telegram_admin_chat_id
            if app_settings.telegram_webapp_url:
                webapp_url = app_settings.telegram_webapp_url
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"Could not load database settings for notification, using env fallback: {e}")

    if not bot_token or not chat_id:
        return

    text = f"🤖 <b>AI требует вашего решения!</b>\n\n<b>{title}</b>"
    if description:
        text += f"\n\n<i>{description[:250]}</i>"

    payload = {
        "chat_id": chat_id,
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
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json=payload,
                timeout=10.0
            )
            if res.status_code != 200:
                logger.warning(f"Telegram notification failed ({res.status_code}): {res.text}")
    except Exception as e:
        logger.warning(f"Failed to send Telegram notification: {e}")
