"""FastAPI web server — OAuth, registration, admin dashboard."""
import logging
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import WEB_PORT, BASE_DOMAIN
from app.api.auth_routes import router as auth_router
from app.api.student_routes import router as student_router
from app.api.admin_routes import router as admin_router

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# Thư mục gốc project (absolute path — không phụ thuộc working directory)
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="VInaStudy Bot – Web Server", docs_url=None, redoc_url=None)

# ── CORS (allow Railway domain + localhost) ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ────────────────────────────────────────────────────────
static_path = BASE_DIR / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Serve content folder (HTML exercises) — dùng absolute path để tránh lỗi working dir
content_path = BASE_DIR / "content"
if content_path.exists():
    app.mount("/content", StaticFiles(directory=str(content_path)), name="content")
    logger.info(f"✅ Content mounted: {content_path}")
else:
    logger.error(f"❌ Content dir NOT found: {content_path}")

# ── Routers ─────────────────────────────────────────────────────────────
app.include_router(auth_router,    prefix="/auth")
app.include_router(student_router, prefix="/api/student")
app.include_router(admin_router,   prefix="/api/admin")


# ── Pages ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    """Landing / intro page."""
    p = BASE_DIR / "intro.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>VInaStudy Bot</h1><a href='/register'>Đăng ký</a>")


@app.get("/game", response_class=HTMLResponse)
async def game_page():
    """Splash/intro — index.html (được mở từ bot qua WebApp)."""
    p = BASE_DIR / "index.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("...", status_code=503)


@app.get("/map", response_class=HTMLResponse)
async def map_page():
    """Bản đồ chiến dịch — map.html."""
    p = BASE_DIR / "map.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("...", status_code=503)


# Cho phép index.html / map.html theo đúng tên file
@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    return await game_page()


@app.get("/map.html", response_class=HTMLResponse)
async def map_html():
    return await map_page()


@app.get("/profile", response_class=HTMLResponse)
async def profile_page():
    """Trang chỉnh sửa hồ sơ học sinh."""
    p = BASE_DIR / "profile.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("...", status_code=503)


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    p = BASE_DIR / "register.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Trang đăng ký chưa sẵn sàng</h1>", status_code=503)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    p = BASE_DIR / "admin-dashboard.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin dashboard chưa sẵn sàng</h1>", status_code=503)


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page():
    """Bảng xếp hạng chiến binh."""
    p = BASE_DIR / "leaderboard.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("...", status_code=503)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "web"}


# ── DB startup ──────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    from app.database.connection import init_pool
    from app.database.init_db import init_db
    await init_pool()
    await init_db()
    logger.info(f"Web server started — {BASE_DOMAIN}")


@app.on_event("shutdown")
async def shutdown():
    from app.database.connection import close_pool
    await close_pool()


# ── Entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("web_server:app", host="0.0.0.0", port=WEB_PORT,
                reload=False, log_level="info")
