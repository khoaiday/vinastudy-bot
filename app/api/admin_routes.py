"""Admin API: duyệt tài khoản, thống kê, quản lý lớp."""
import logging
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import os
from app.config import ADMIN_SECRET, TELEGRAM_TOKEN as _TELEGRAM_TOKEN_CONFIG

def _get_tg_token() -> str:
    """Đọc TELEGRAM_TOKEN tại runtime để tránh lỗi khi Railway chưa inject env var lúc startup."""
    return os.getenv("TELEGRAM_TOKEN") or _TELEGRAM_TOKEN_CONFIG or ""
from app.database import crud

logger = logging.getLogger(__name__)
router = APIRouter()


def require_admin(x_admin_token: str = Header(default="")):
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(403, "Không có quyền admin")


# ── Pydantic ───────────────────────────────────────────────────────────

class RejectBody(BaseModel):
    reason: str = "Thông tin không hợp lệ"


class NotifyBody(BaseModel):
    message: str


class CreateUserBody(BaseModel):
    ho_ten:         str
    lop:            str = "3"
    gioi_tinh:      str = "nam"
    character_type: str = "chien_binh"
    telegram_id:    int | None = None
    email:          str | None = None
    status:         str = "approved"


class UpdateUserBody(BaseModel):
    ho_ten:         str | None = None
    lop:            str | None = None
    gioi_tinh:      str | None = None
    character_type: str | None = None
    telegram_id:    int | None = None
    status:         str | None = None


# ── Pending accounts ───────────────────────────────────────────────────

@router.get("/pending")
async def get_pending(request: Request,
                      x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    users = await crud.get_web_users_by_status("pending")
    return JSONResponse({"users": users, "total": len(users)})


@router.post("/approve/{user_id}")
async def approve_user(user_id: int, request: Request,
                        x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    user = await crud.get_web_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    # Phê duyệt → tạo student record nếu chưa có
    await crud.approve_web_user(user_id)
    await crud.sync_web_user_to_student(user_id)

    # Thông báo qua Telegram nếu có telegram_id
    tg_token = _get_tg_token()
    if user.get("telegram_id") and tg_token:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    json={
                        "chat_id": user["telegram_id"],
                        "text": (
                            f"🎉 *Chào mừng {user['ho_ten']}!*\n\n"
                            "Tài khoản Chiến Binh Toán của em đã được duyệt!\n"
                            "Hãy quay lại bot để bắt đầu hành trình 🚀"
                        ),
                        "parse_mode": "Markdown",
                    }
                )
        except Exception as e:
            logger.warning(f"Telegram notify failed: {e}")

    return JSONResponse({"ok": True, "message": f"Đã duyệt {user['ho_ten']}"})


@router.post("/reject/{user_id}")
async def reject_user(user_id: int, body: RejectBody,
                      x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    user = await crud.get_web_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    await crud.reject_web_user(user_id, body.reason)

    # Thông báo qua Telegram nếu có telegram_id
    tg_id = user.get("telegram_id")
    tg_notified = False
    tg_error    = ""

    tg_token = _get_tg_token()
    if not tg_id:
        tg_error = "Không có Telegram ID trong hồ sơ"
        logger.warning(f"TG reject notify skipped: user_id={user_id}, telegram_id=None")
    elif not tg_token:
        tg_error = "TELEGRAM_TOKEN chưa được cấu hình trong web service"
        logger.warning("TG reject notify skipped: TELEGRAM_TOKEN MISSING")
    else:
        try:
            import httpx
            msg = (
                f"❌ Hồ sơ bị từ chối\n\n"
                f"Xin chào {user.get('ho_ten', '')}, "
                f"hồ sơ đăng ký của em chưa được duyệt.\n\n"
                f"📋 Lý do: {body.reason}\n\n"
                f"👉 Mở lại trang đăng ký, đọc lý do và nộp lại hồ sơ nhé! 🔄"
            )
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.post(
                    f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    json={"chat_id": tg_id, "text": msg},
                )
            result = resp.json()
            if result.get("ok"):
                tg_notified = True
                logger.info(f"TG reject notify sent → chat_id={tg_id}")
            else:
                tg_error = result.get("description", "Telegram API error")
                logger.warning(f"TG reject notify API error → {result}")
        except Exception as e:
            tg_error = str(e)
            logger.warning(f"TG reject notify exception → {e}")

    return JSONResponse({
        "ok":          True,
        "message":     f"Đã từ chối {user['ho_ten']}",
        "tg_notified": tg_notified,
        "tg_error":    tg_error,
        "telegram_id": tg_id,
    })


# ── Students list ──────────────────────────────────────────────────────

@router.get("/students")
async def get_students(x_admin_token: str = Header(default=""),
                       status: str = "approved"):
    require_admin(x_admin_token)
    if status == "all":
        users = await crud.get_all_web_users()
    else:
        users = await crud.get_web_users_by_status(status)
    return JSONResponse({"users": users, "total": len(users)})


@router.get("/students/{user_id}/results")
async def get_student_results(user_id: int,
                               x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    user = await crud.get_web_user_by_id(user_id)
    if not user or not user.get("telegram_id"):
        return JSONResponse({"results": []})
    summary = await crud.get_student_results_summary(user["telegram_id"])
    return JSONResponse(summary or {"results": []})


@router.get("/students/{user_id}/full-stats")
async def get_student_full_stats(user_id: int,
                                  x_admin_token: str = Header(default="")):
    """Thống kê đầy đủ: XP, level, streak, badge, từng buổi học."""
    require_admin(x_admin_token)
    user = await crud.get_web_user_by_id(user_id)
    if not user or not user.get("telegram_id"):
        return JSONResponse({"ok": False, "error": "Không có telegram_id"})
    from app.services.gamification import BADGES, tinh_cap_do
    stats = await crud.get_student_full_stats(user["telegram_id"])
    if not stats:
        return JSONResponse({"ok": True, "stats": None})
    icon, _, _ = tinh_cap_do(stats["xp"])
    stats["level_icon"] = icon
    badge_list = []
    for bk in (stats.get("badges") or []):
        if bk in BADGES:
            badge_list.append({"key": bk, "icon": BADGES[bk]["icon"],
                                "ten": BADGES[bk]["ten"], "mo_ta": BADGES[bk]["mo_ta"]})
    stats["badge_list"] = badge_list
    return JSONResponse({"ok": True, "stats": stats})


# ── Admin CRUD users ───────────────────────────────────────────────────

@router.post("/users")
async def create_user(body: CreateUserBody,
                      x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    user = await crud.create_web_user_admin(
        ho_ten=body.ho_ten, lop=body.lop, gioi_tinh=body.gioi_tinh,
        character_type=body.character_type, telegram_id=body.telegram_id,
        email=body.email, status=body.status,
    )
    if body.status == "approved" and body.telegram_id:
        await crud.sync_web_user_to_student(user["id"])
    return JSONResponse({"ok": True, "user": user})


@router.put("/users/{user_id}")
async def update_user(user_id: int, body: UpdateUserBody,
                      x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        await crud.update_web_user_admin(user_id, updates)
    if body.status == "approved":
        await crud.sync_web_user_to_student(user_id)
    user = await crud.get_web_user_by_id(user_id)
    return JSONResponse({"ok": True, "user": user})


@router.delete("/users/{user_id}")
async def delete_user(user_id: int,
                      x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    user = await crud.get_web_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "Không tìm thấy user")
    await crud.delete_web_user(user_id)
    return JSONResponse({"ok": True, "message": f"Đã xóa {user['ho_ten']}"})


# ── Test avatar pipeline ───────────────────────────────────────────────

@router.get("/test-avatar")
async def test_avatar(x_admin_token: str = Header(default=""),
                      character: str = "chien_binh",
                      gioi_tinh: str = "nam"):
    """
    Kiểm tra pipeline tạo avatar — trả về HTML để xem ảnh thẳng trên browser.
    Không cần ảnh thật: tạo khuôn mặt giả bằng PIL rồi chạy qua pipeline.
    URL: /api/admin/test-avatar?character=chien_binh&gioi_tinh=nam
    Header: x-admin-token: <ADMIN_SECRET>
    """
    require_admin(x_admin_token)
    import time, io, base64, os
    from PIL import Image, ImageDraw
    from fastapi.responses import HTMLResponse

    # ── Tạo khuôn mặt giả 300×300 ────────────────────────────────────
    face = Image.new("RGB", (300, 300), (25, 18, 55))
    d    = ImageDraw.Draw(face)
    d.ellipse([30, 25, 270, 275], fill=(220, 170, 125))   # da mặt
    d.ellipse([75,  90, 118, 125], fill=(45, 32, 18))     # mắt trái
    d.ellipse([182, 90, 225, 125], fill=(45, 32, 18))     # mắt phải
    d.ellipse([82,  96, 104, 116], fill=(255, 255, 255))  # highlight mắt trái
    d.ellipse([196, 96, 218, 116], fill=(255, 255, 255))
    d.ellipse([130, 148, 170, 175], fill=(195, 145, 105)) # mũi
    d.arc([90, 175, 210, 228], start=8, end=172, fill=(165, 75, 75), width=5)  # miệng

    buf = io.BytesIO()
    face.save(buf, format="JPEG", quality=92)
    face_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    # ── Chạy pipeline ─────────────────────────────────────────────────
    token   = os.getenv("REPLICATE_API_TOKEN", "")
    t0      = time.time()
    from app.auth.avatar import generate_avatar_pipeline
    result  = generate_avatar_pipeline(face_b64, character, gioi_tinh)
    elapsed = round(time.time() - t0, 2)

    token_status = "✅ Đã set" if token else "❌ CHƯA SET — thêm REPLICATE_API_TOKEN vào Railway"
    method = "🤖 AnimeGAN2 (Replicate AI)" if elapsed > 3 else "🎨 PIL enhance (fallback)"

    if not result["ok"]:
        html = f"""<!DOCTYPE html><html><body style="font-family:monospace;background:#111;color:#f55;padding:24px">
<h2>❌ Pipeline thất bại</h2>
<p><b>Lỗi:</b> {result['error']}</p>
<p><b>REPLICATE_API_TOKEN:</b> {token_status}</p>
<p><b>Thời gian:</b> {elapsed}s</p>
<p>Xem Railway Logs để biết chi tiết (tìm dòng <code>[avatar]</code>)</p>
</body></html>"""
        from fastapi.responses import HTMLResponse
        return HTMLResponse(html, status_code=200)

    cartoon_src = result["cartoon_b64"]
    final_src   = result["final_b64"]
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Avatar Test</title>
<style>
  body{{font-family:sans-serif;background:#0a0a1a;color:#eee;text-align:center;padding:24px}}
  .row{{display:flex;gap:32px;justify-content:center;flex-wrap:wrap;margin:24px 0}}
  .card{{background:#161630;border-radius:12px;padding:16px;min-width:200px}}
  img{{max-width:300px;border-radius:8px}}
  .ok{{color:#4f8}}  .warn{{color:#fa4}}
  pre{{text-align:left;background:#111;padding:12px;border-radius:8px;font-size:13px}}
</style></head>
<body>
<h2>🧪 Avatar Pipeline Test</h2>
<div class="row">
  <div class="card"><p>REPLICATE_API_TOKEN</p>
    <b class="{'ok' if token else 'warn'}">{token_status}</b></div>
  <div class="card"><p>Method</p><b>{method}</b></div>
  <div class="card"><p>Thời gian</p><b>{elapsed}s</b></div>
  <div class="card"><p>Character</p><b>{character} / {gioi_tinh}</b></div>
</div>
<div class="row">
  <div class="card">
    <p>Mặt sau filter (cartoon_b64)</p>
    <img src="{cartoon_src}">
  </div>
  <div class="card">
    <p>Nhân vật hoàn chỉnh (final_b64)</p>
    <img src="{final_src}">
  </div>
</div>
<p style="color:#888">Nếu ảnh vẫn xấu + token chưa set → thêm REPLICATE_API_TOKEN vào Railway web service</p>
</body></html>"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(html)


# ── Dashboard stats ────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(x_admin_token: str = Header(default="")):
    require_admin(x_admin_token)
    pending   = await crud.get_web_users_by_status("pending")
    approved  = await crud.get_web_users_by_status("approved")
    rejected  = await crud.get_web_users_by_status("rejected")
    students  = await crud.get_all_students()
    leaderboard = await crud.get_leaderboard(5)
    return JSONResponse({
        "pending_count":  len(pending),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "total_students": len(students),
        "top5":           leaderboard,
    })
