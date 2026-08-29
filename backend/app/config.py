import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Locate .env file in root or backend
root_env = Path(__file__).resolve().parent.parent.parent / ".env"
backend_env = Path(__file__).resolve().parent.parent / ".env"

if root_env.exists():
    load_dotenv(dotenv_path=root_env)
elif backend_env.exists():
    load_dotenv(dotenv_path=backend_env)
else:
    load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "AI Human-in-the-Loop Queue"
    
    # Database: Default PostgreSQL, fallback to SQLite if needed
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./queue_app.db")
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBAPP_URL: str = os.getenv("TELEGRAM_WEBAPP_URL", "http://localhost:8000")
    TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
    
    # CORS & Server
    CORS_ORIGINS: list[str] = ["*"]
    WORKER_INTERVAL_SECONDS: int = int(os.getenv("WORKER_INTERVAL_SECONDS", "60"))

settings = Settings()
