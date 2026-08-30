"""
AI Queue Application Runner
Launches FastAPI backend + static React frontend on http://localhost:8000
"""
import sys
import os
import socket
import uvicorn

# Force UTF-8 stdout if needed on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

def get_lan_ip():
    """Detect LAN IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public DNS IP (does not actually send packets)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    lan_ip = get_lan_ip()

    print("==================================================")
    print("🚀 AI Action Queue Server Started (Single-User Global Shared State)")
    print(f"💻 Desktop / Local:    http://localhost:{port}")
    print(f"📱 Phone (LAN WiFi):   http://{lan_ip}:{port}")
    print(f"📚 Swagger API Docs:   http://localhost:{port}/docs")
    print("==================================================")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
