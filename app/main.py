"""
app/main.py

Aplikasi utama FastAPI untuk Backend UdaraSiaga.
Menyediakan endpoint REST API, dokumentasi OpenAPI (/docs), dan frontend dummy (/dummy).
"""


from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import advice, attributions, events, health, lapis2, lapis3, layers, map_modes, simulate

from app.core.config import BACKEND_DIR, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inisialisasi otomatis skema database saat startup
    try:
        from app.db.repositories.volcano_repo import VolcanoRepository
        from app.db.schema import init_db_schema
        from app.db.session import get_db_connection

        conn = get_db_connection()
        init_db_schema(conn)
        conn.close()

        if VolcanoRepository.count_all() == 0:
            from scripts.db.seed_database import seed_all
            seed_all()
    except Exception as e:
        print(f"Warning: Database auto-init error: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS: localhost dan wildcard untuk mendukung pembukaan frontend dari file://
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router
app.include_router(health.router)
app.include_router(events.router)
app.include_router(simulate.router)
app.include_router(lapis2.router)
app.include_router(lapis3.router)
# map_modes before layers: its fixed paths must win over /layers/{name}
app.include_router(advice.router)
app.include_router(map_modes.router)

app.include_router(layers.router)
app.include_router(attributions.router)

# Mount frontend dummy jika foldernya ada
frontend_dummy_dir = BACKEND_DIR / "frontend-dummy"
if frontend_dummy_dir.exists():
    app.mount("/dummy", StaticFiles(directory=str(frontend_dummy_dir), html=True), name="dummy")



FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#0f172a"/>
  <polygon points="16,4 4,28 28,28" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5"/>
  <circle cx="16" cy="18" r="3.5" fill="#ef4444"/>
</svg>"""


@app.get("/favicon.ico", include_in_schema=False)
def get_favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "version": settings.VERSION,
        "docs": "/docs",
        "frontend_dummy": "/dummy",
        "disclaimer": settings.DISCLAIMER,
    }
