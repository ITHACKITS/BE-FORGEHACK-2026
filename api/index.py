import sys
import os
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Add root directory to sys.path so app module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app
except Exception as e:
    err_tb = traceback.format_exc()
    print(f"Error importing app.main: {err_tb}")
    app = FastAPI(title="StandbAI API (Startup Error)")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to import app.main", "detail": str(e), "traceback": err_tb}
        )
