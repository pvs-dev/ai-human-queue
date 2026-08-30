import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AppSettings, SettingsUpdate
from app import crud
from app.telegram_bot import send_telegram_notification

router = APIRouter()
logger = logging.getLogger("settings_api")

@router.get("", response_model=AppSettings)
def get_settings(db: Session = Depends(get_db)):
    """Get current dynamic app settings."""
    return crud.get_app_settings(db)

@router.put("", response_model=AppSettings)
def update_settings(update_in: SettingsUpdate, db: Session = Depends(get_db)):
    """Update runtime settings in database."""
    return crud.update_app_settings(db, update_in)

@router.post("/test-telegram")
async def test_telegram_push(db: Session = Depends(get_db)):
    """Send a test push notification to verify Telegram Bot configuration."""
    settings = crud.get_app_settings(db)
    if not settings.telegram_bot_token or not settings.telegram_admin_chat_id:
        raise HTTPException(
            status_code=400,
            detail="Укажите Telegram Bot Token и Admin Chat ID в настройках"
        )
    
    await send_telegram_notification(
        title="🔔 Тестовое уведомление из AI Action Queue",
        description="Связь с Telegram ботом успешно настроена! Уведомления о новых задачах и решениях будут приходить сюда."
    )
    return {"ok": True, "message": "Тестовое уведомление отправлено"}
