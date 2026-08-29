"""
AI Queue Application Runner
Launches FastAPI backend + static React frontend on http://localhost:8000
"""
import sys
import os
import uvicorn

# Force UTF-8 stdout if needed on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print("==================================================")
    print(f"[*] AI Action Queue Server starting at http://localhost:{port}")
    print(f"[*] Open in mobile browser, desktop, or Telegram Mini App")
    print(f"[*] API Documentation available at http://localhost:{port}/docs")
    print("==================================================")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
