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


@app.get("/ping/replicate")
async def ping_replicate():
    """Kiểm tra Replicate API riêng — trả về lỗi chính xác nếu có."""
    import os, io
    from PIL import Image

    token = os.getenv("REPLICATE_API_TOKEN", "")
    if not token:
        return {"ok": False, "step": "token", "error": "REPLICATE_API_TOKEN chưa set"}

    # Kiểm tra import
    try:
        import replicate as _rep
        rep_version = getattr(_rep, "__version__", "unknown")
    except ImportError as e:
        return {"ok": False, "step": "import", "error": str(e)}

    # Gọi API thật với ảnh nhỏ
    try:
        os.environ["REPLICATE_API_TOKEN"] = token
        img = Image.new("RGB", (128, 128), (200, 150, 100))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        buf.seek(0)

        output = _rep.run(
            "ptran1203/pytorch-animegan:7d44f1878a07e7b5a32af9727c1f6120cac04203d48f3f7b0432e28fa8e5c6b6",
            input={"image": buf, "style": "BarbieFace"},
        )
        url = str(output[0]) if isinstance(output, list) else str(output)
        return {"ok": True, "step": "done", "output_url": url,
                "replicate_version": rep_version, "token_prefix": token[:8] + "..."}
    except Exception as e:
        return {"ok": False, "step": "api_call", "error": str(e),
                "replicate_version": rep_version, "token_prefix": token[:8] + "..."}


@app.get("/ping/avatar", response_class=HTMLResponse)
async def ping_avatar(character: str = "chien_binh", gioi_tinh: str = "nam"):
    """Public test endpoint — kiểm tra pipeline avatar (không cần auth)."""
    import time, io, base64, os
    from PIL import Image, ImageDraw
    from app.auth.avatar import generate_avatar_pipeline

    face = Image.new("RGB", (300, 300), (25, 18, 55))
    d    = ImageDraw.Draw(face)
    d.ellipse([30,  25, 270, 275], fill=(220, 170, 125))
    d.ellipse([75,  90, 118, 125], fill=(45, 32, 18))
    d.ellipse([182, 90, 225, 125], fill=(45, 32, 18))
    d.ellipse([82,  96, 104, 116], fill=(255, 255, 255))
    d.ellipse([196, 96, 218, 116], fill=(255, 255, 255))
    d.ellipse([130, 148, 170, 175], fill=(195, 145, 105))
    d.arc([90, 175, 210, 228], start=8, end=172, fill=(165, 75, 75), width=5)

    buf = io.BytesIO()
    face.save(buf, format="JPEG", quality=92)
    face_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    token   = os.getenv("REPLICATE_API_TOKEN", "")
    t0      = time.time()
    from fastapi.concurrency import run_in_threadpool
    result  = await run_in_threadpool(generate_avatar_pipeline, face_b64, character, gioi_tinh)
    elapsed = round(time.time() - t0, 2)

    if not result["ok"]:
        return HTMLResponse(f"""<!DOCTYPE html><html><body
          style="font-family:monospace;background:#111;color:#f66;padding:32px">
          <h2>❌ Avatar pipeline THẤT BẠI</h2>
          <p><b>Lỗi:</b> {result['error']}</p>
          <p><b>REPLICATE_API_TOKEN:</b> {"✅ đã set" if token else "❌ CHƯA SET"}</p>
          <p><b>Elapsed:</b> {elapsed}s</p>
          <p>Xem Railway Logs → tìm dòng <code>[avatar] step</code> để biết bước nào lỗi</p>
          </body></html>""")

    method = "🤖 AnimeGAN2 AI" if elapsed > 3 else "🎨 PIL enhance (fallback)"
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Avatar Test</title>
<style>body{{font-family:sans-serif;background:#0a0a1a;color:#eee;text-align:center;padding:24px}}
.row{{display:flex;gap:24px;justify-content:center;flex-wrap:wrap;margin:20px 0}}
.card{{background:#161630;border-radius:12px;padding:14px}}
img{{max-width:280px;border-radius:8px;display:block;margin:8px auto}}
.ok{{color:#4f8}}.warn{{color:#fa4}}</style></head>
<body>
<h2>🧪 Avatar Pipeline Test — {character}/{gioi_tinh}</h2>
<div class="row">
  <div class="card">REPLICATE_API_TOKEN<br>
    <b class="{'ok' if token else 'warn'}">{"✅ đã set" if token else "❌ chưa set"}</b></div>
  <div class="card">Method<br><b>{method}</b></div>
  <div class="card">Thời gian<br><b>{elapsed}s</b></div>
</div>
<div class="row">
  <div class="card"><p>Mặt sau filter</p>
    <img src="{result['cartoon_b64']}"></div>
  <div class="card"><p>Nhân vật hoàn chỉnh</p>
    <img src="{result['final_b64']}"></div>
</div>
</body></html>""")


@app.post("/ping/avatar-upload", response_class=HTMLResponse)
async def ping_avatar_upload(request: Request,
                              character: str = "chien_binh",
                              gioi_tinh: str = "nam"):
    """
    Test avatar pipeline với ảnh thật — upload qua form.
    Dùng để kiểm tra chất lượng IP-Adapter trước khi đưa vào production.
    """
    import time, io, base64
    from fastapi.concurrency import run_in_threadpool
    from app.auth.avatar import generate_avatar_pipeline

    # Nhận file upload
    form    = await request.form()
    file    = form.get("image")
    if not file or not hasattr(file, "read"):
        return HTMLResponse("<h2 style='color:red'>Thiếu field 'image'</h2>", status_code=400)

    raw = await file.read()
    face_b64 = "data:image/jpeg;base64," + base64.b64encode(raw).decode()

    t0     = time.time()
    result = await run_in_threadpool(generate_avatar_pipeline, face_b64, character, gioi_tinh)
    elapsed = round(time.time() - t0, 1)

    if not result["ok"]:
        return HTMLResponse(f"""<!DOCTYPE html><html><body
          style="font-family:monospace;background:#111;color:#f66;padding:32px">
          <h2>❌ Pipeline thất bại</h2>
          <p><b>Lỗi:</b> {result['error']}</p>
          <p><b>Elapsed:</b> {elapsed}s</p>
          </body></html>""")

    final_src = result["final_b64"]
    method    = "🤖 IP-Adapter" if elapsed > 25 else "🎨 AnimeGAN2 / PIL fallback"
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Avatar Upload Test</title>
<style>
  body{{font-family:sans-serif;background:#0a0a1a;color:#eee;text-align:center;padding:24px}}
  img{{max-width:400px;border-radius:12px;border:2px solid #0ae0fe}}
  .info{{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin:16px 0}}
  .card{{background:#161630;border-radius:10px;padding:12px 20px;font-size:.9rem}}
  form{{margin-top:28px;background:#161630;border-radius:12px;padding:20px;display:inline-block}}
  input[type=file]{{color:#eee}}
  button{{margin-top:12px;padding:10px 28px;background:#0ae0fe;color:#000;
          border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:1rem}}
</style></head>
<body>
<h2>🧪 Avatar Test — {character} / {gioi_tinh}</h2>
<div class="info">
  <div class="card">Method<br><b>{method}</b></div>
  <div class="card">Thời gian<br><b>{elapsed}s</b></div>
  <div class="card">Character<br><b>{character}</b></div>
</div>
<img src="{final_src}" alt="avatar">
<br><br>
<form method="POST" enctype="multipart/form-data"
      action="/ping/avatar-upload?character={character}&gioi_tinh={gioi_tinh}">
  <div>Thử ảnh khác:</div>
  <input type="file" name="image" accept="image/*" required>
  <br><button type="submit">Convert lại</button>
</form>
<div style="margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
  {''.join(f'<a href="/ping/avatar-upload-form?character={c}&gioi_tinh={gioi_tinh}" style="padding:6px 14px;background:#161630;border:1px solid #0ae0fe;border-radius:6px;color:#0ae0fe;text-decoration:none">{c}</a>'
           for c in ["chien_binh","phu_thuy","xa_thu","hiep_si"])}
</div>
</body></html>""")


@app.get("/ping/avatar-upload-form", response_class=HTMLResponse)
async def ping_avatar_upload_form(character: str = "chien_binh", gioi_tinh: str = "nam"):
    """Form upload ảnh để test pipeline."""
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Avatar Test Upload</title>
<style>
  body{{font-family:sans-serif;background:#0a0a1a;color:#eee;text-align:center;padding:40px}}
  form{{background:#161630;border-radius:14px;padding:32px;display:inline-block;min-width:300px}}
  select,input[type=file]{{width:100%;padding:8px;margin:8px 0;background:#0a0a1a;
    border:1px solid #0ae0fe33;border-radius:6px;color:#eee}}
  button{{margin-top:16px;width:100%;padding:12px;background:#0ae0fe;color:#000;
    border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:1rem}}
</style></head>
<body>
<h2>🧪 Test Avatar Pipeline</h2>
<form method="POST" enctype="multipart/form-data" id="f">
  <div style="margin-bottom:12px;text-align:left">
    <label>Character</label>
    <select name="character" onchange="this.form.action='/ping/avatar-upload?character='+this.value+'&gioi_tinh='+document.querySelector('[name=gioi_tinh]').value">
      {''.join(f'<option value="{c}" {"selected" if c==character else ""}>{c}</option>' for c in ["chien_binh","phu_thuy","xa_thu","hiep_si"])}
    </select>
    <label>Giới tính</label>
    <select name="gioi_tinh">
      <option value="nam" {"selected" if gioi_tinh=="nam" else ""}>Nam</option>
      <option value="nu"  {"selected" if gioi_tinh=="nu"  else ""}>Nữ</option>
    </select>
    <label>Ảnh mặt (JPEG/PNG)</label>
    <input type="file" name="image" accept="image/*" required>
  </div>
  <button type="submit" onclick="this.form.action='/ping/avatar-upload?character='+this.form.character.value+'&gioi_tinh='+this.form.gioi_tinh.value">
    🎨 Convert → Anime
  </button>
</form>
</body></html>""")


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
