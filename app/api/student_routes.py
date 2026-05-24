"""Student API: hoàn tất đăng ký, upload avatar, chỉnh sửa profile."""
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.auth.google_oauth import decode_session_token
from app.auth.avatar import generate_avatar_pipeline
from app.database import crud
from app.config import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)
router = APIRouter()

CHAR_LABEL = {
    "chien_binh": "⚔️ Chiến Binh",
    "phu_thuy":   "🔮 Phù Thủy",
    "xa_thu":     "🏹 Xạ Thủ",
    "hiep_si":    "🛡️ Hiệp Sĩ",
}


async def _send_tg(chat_id: int, text: str) -> None:
    """Gửi tin nhắn Telegram plain-text, log lỗi rõ ràng."""
    if not (chat_id and TELEGRAM_TOKEN):
        logger.warning(f"_send_tg skipped: chat_id={chat_id!r}, token={'set' if TELEGRAM_TOKEN else 'MISSING'}")
        return
    try:
        import httpx
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text},  # plain text
            )
        result = resp.json()
        if result.get("ok"):
            logger.info(f"TG notify sent → chat_id={chat_id}")
        else:
            logger.warning(f"TG notify API error → {result}")
    except Exception as e:
        logger.warning(f"TG notify exception (chat_id={chat_id}): {e}")


def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Chưa đăng nhập")
    payload = decode_session_token(auth[7:])
    if not payload:
        raise HTTPException(401, "Token hết hạn, đăng nhập lại")
    return payload


# ── Pydantic models ────────────────────────────────────────────────────

class CompleteProfileBody(BaseModel):
    ho_ten:          str
    lop:             str = "3"
    gioi_tinh:       str = "nam"
    character_type:  str = "chien_binh"
    avatar_face_b64: str
    telegram_id:     int | None = None


class UpdateProfileBody(BaseModel):
    ho_ten:          str | None = None
    lop:             str | None = None
    gioi_tinh:       str | None = None
    character_type:  str | None = None
    avatar_face_b64: str | None = None


# ── Routes ──────────────────────────────────────────────────────────────

@router.post("/complete-profile")
async def complete_profile(body: CompleteProfileBody, request: Request):
    """Bước 2-3: Lưu tên, nhân vật, tạo avatar → status = pending."""
    payload  = get_current_user(request)
    google_id = payload["sub"]

    user = await crud.get_web_user_by_google_id(google_id)
    if not user:
        raise HTTPException(404, "Tài khoản không tồn tại")

    # Generate avatar
    avatar_result = generate_avatar_pipeline(
        body.avatar_face_b64, body.character_type, body.gioi_tinh)
    if not avatar_result["ok"]:
        raise HTTPException(500, f"Lỗi tạo avatar: {avatar_result['error']}")

    await crud.update_web_user_profile(
        google_id       = google_id,
        ho_ten          = body.ho_ten,
        lop             = body.lop,
        character_type  = body.character_type,
        avatar_original = body.avatar_face_b64,
        avatar_cartoon  = avatar_result["cartoon_b64"],
        avatar_final    = avatar_result["final_b64"],
        gioi_tinh       = body.gioi_tinh,
    )

    # Nếu trước đó bị từ chối → reset lại pending để đăng ký lại
    if user.get("status") == "rejected":
        await crud.update_web_user_admin(
            user["id"], {"status": "pending", "rejection_reason": None}
        )

    # Lưu telegram_id nếu có (gửi từ link bot)
    tg_id = body.telegram_id or user.get("telegram_id")
    if body.telegram_id:
        await crud.patch_web_user(google_id, {"telegram_id": body.telegram_id})
        logger.info(f"telegram_id={body.telegram_id} saved for google_id={google_id}")
    else:
        logger.warning(f"complete_profile: telegram_id NOT sent from browser (google_id={google_id}). "
                       f"Existing in DB: {user.get('telegram_id')!r}")

    # ── Thông báo Telegram: Đã gửi hồ sơ ───────────────────────────────
    char_label = CHAR_LABEL.get(body.character_type, body.character_type)
    await _send_tg(
        tg_id,
        f"⏳ *Đã gửi hồ sơ thành công!*\n\n"
        f"👤 *Tên:* {body.ho_ten}\n"
        f"📚 *Lớp:* {body.lop}\n"
        f"🎮 *Nhân vật:* {char_label}\n\n"
        f"Thầy đang xem xét hồ sơ và sẽ thông báo khi được duyệt.\n"
        f"Thường trong vòng *24 giờ* 🚀",
    )

    return JSONResponse({"ok": True, "status": "pending",
                         "cartoon_b64":  avatar_result["cartoon_b64"],
                         "avatar_final": avatar_result["final_b64"]})


@router.put("/profile")
async def update_profile(body: UpdateProfileBody, request: Request):
    """Học sinh chỉnh sửa hồ sơ (chỉ khi đã approved)."""
    payload  = get_current_user(request)
    google_id = payload["sub"]

    user = await crud.get_web_user_by_google_id(google_id)
    if not user:
        raise HTTPException(404, "Tài khoản không tồn tại")
    if user["status"] != "approved":
        raise HTTPException(403, "Tài khoản chưa được duyệt")

    updates = {}
    if body.ho_ten:         updates["ho_ten"]         = body.ho_ten
    if body.lop:            updates["lop"]             = body.lop
    if body.gioi_tinh:      updates["gioi_tinh"]       = body.gioi_tinh
    if body.character_type: updates["character_type"]  = body.character_type

    if body.avatar_face_b64:
        char = body.character_type or user["character_type"]
        gt   = body.gioi_tinh or user.get("gioi_tinh", "nam")
        res  = generate_avatar_pipeline(body.avatar_face_b64, char, gt)
        if res["ok"]:
            updates["avatar_original"] = body.avatar_face_b64
            updates["avatar_cartoon"]  = res["cartoon_b64"]
            updates["avatar_final"]    = res["final_b64"]

    if updates:
        await crud.patch_web_user(google_id, updates)

    updated = await crud.get_web_user_by_google_id(google_id)
    return JSONResponse({"ok": True, "user": {
        "ho_ten":         updated["ho_ten"],
        "lop":            updated["lop"],
        "gioi_tinh":      updated.get("gioi_tinh", "nam"),
        "character_type": updated["character_type"],
        "avatar_final":   updated["avatar_final"],
    }})


class TgProfileBody(BaseModel):
    tg_id:           int
    ho_ten:          str | None = None
    lop:             str | None = None
    gioi_tinh:       str | None = None
    character_type:  str | None = None
    avatar_face_b64: str | None = None


@router.put("/tg-profile")
async def update_tg_profile(body: TgProfileBody):
    """Cập nhật hồ sơ từ Telegram WebApp (dùng tg_id, không cần JWT)."""
    user = await crud.get_web_user_by_telegram_id(body.tg_id)
    if not user:
        raise HTTPException(404, "Không tìm thấy tài khoản")
    if user["status"] != "approved":
        raise HTTPException(403, "Tài khoản chưa được duyệt")

    updates = {}
    if body.ho_ten:         updates["ho_ten"]        = body.ho_ten.strip()
    if body.lop:            updates["lop"]            = body.lop
    if body.gioi_tinh:      updates["gioi_tinh"]      = body.gioi_tinh
    if body.character_type: updates["character_type"] = body.character_type

    avatar_final = None
    if body.avatar_face_b64:
        char = body.character_type or user["character_type"]
        gt   = body.gioi_tinh or user.get("gioi_tinh", "nam")
        res  = generate_avatar_pipeline(body.avatar_face_b64, char, gt)
        if res["ok"]:
            updates["avatar_original"] = body.avatar_face_b64
            updates["avatar_cartoon"]  = res["cartoon_b64"]
            updates["avatar_final"]    = res["final_b64"]
            avatar_final = res["final_b64"]
        else:
            raise HTTPException(500, f"Lỗi tạo avatar: {res['error']}")

    if updates:
        await crud.patch_web_user(user["google_id"], updates)

    updated = await crud.get_web_user_by_telegram_id(body.tg_id)
    return JSONResponse({
        "ok":           True,
        "ho_ten":       updated["ho_ten"],
        "lop":          updated["lop"],
        "character_type": updated["character_type"],
        "avatar_final": updated["avatar_final"],
    })


@router.get("/tg-status")
async def tg_status(tg_id: int):
    """Kiểm tra trạng thái tài khoản theo Telegram ID. Dùng bởi HTML WebApp."""
    user = await crud.get_web_user_by_telegram_id(tg_id)
    if not user:
        return JSONResponse({"status": "not_found"})
    return JSONResponse({
        "status":           user["status"],
        "ho_ten":           user.get("ho_ten") or "",
        "character_type":   user.get("character_type") or "chien_binh",
        "avatar_final":     user.get("avatar_final") or "",
        "lop":              user.get("lop") or "3",
        "rejection_reason": user.get("rejection_reason") or "",
    })


class TgCompleteProfileBody(BaseModel):
    telegram_id:     int
    ho_ten:          str
    lop:             str = "3"
    gioi_tinh:       str = "nam"
    character_type:  str = "chien_binh"
    avatar_face_b64: str


@router.post("/tg-complete-profile")
async def tg_complete_profile(body: TgCompleteProfileBody):
    """Đăng ký bằng Telegram ID — không cần Google OAuth."""
    google_id = f"tg_{body.telegram_id}"
    email     = f"tg_{body.telegram_id}@telegram"

    # Upsert web_user (tạo mới hoặc giữ nguyên nếu đã có)
    await crud.upsert_web_user(google_id, email, body.ho_ten)

    # Gắn telegram_id
    await crud.patch_web_user(google_id, {"telegram_id": body.telegram_id})

    # Nếu trước đó bị từ chối → reset về pending
    user = await crud.get_web_user_by_google_id(google_id)
    if user and user.get("status") == "rejected":
        await crud.update_web_user_admin(
            user["id"], {"status": "pending", "rejection_reason": None}
        )

    # Tạo avatar (chạy trong threadpool để không block event loop)
    from fastapi.concurrency import run_in_threadpool
    avatar_result = await run_in_threadpool(
        generate_avatar_pipeline, body.avatar_face_b64, body.character_type, body.gioi_tinh
    )
    if not avatar_result["ok"]:
        raise HTTPException(500, f"Lỗi tạo avatar: {avatar_result['error']}")

    await crud.update_web_user_profile(
        google_id       = google_id,
        ho_ten          = body.ho_ten,
        lop             = body.lop,
        character_type  = body.character_type,
        avatar_original = body.avatar_face_b64,
        avatar_cartoon  = avatar_result["cartoon_b64"],
        avatar_final    = avatar_result["final_b64"],
        gioi_tinh       = body.gioi_tinh,
    )

    # Thông báo Telegram
    char_label = CHAR_LABEL.get(body.character_type, body.character_type)
    await _send_tg(
        body.telegram_id,
        f"⏳ Đã gửi hồ sơ thành công!\n\n"
        f"👤 Tên: {body.ho_ten}\n"
        f"📚 Lớp: {body.lop}\n"
        f"🎮 Nhân vật: {char_label}\n\n"
        f"Thầy đang xem xét hồ sơ và sẽ thông báo khi được duyệt.\n"
        f"Thường trong vòng 24 giờ 🚀",
    )

    return JSONResponse({"ok": True, "status": "pending",
                         "cartoon_b64":  avatar_result["cartoon_b64"],
                         "avatar_final": avatar_result["final_b64"]})


@router.get("/profile")
async def get_profile(request: Request):
    payload  = get_current_user(request)
    user = await crud.get_web_user_by_google_id(payload["sub"])
    if not user:
        raise HTTPException(404, "Không tìm thấy")
    return JSONResponse({
        "ho_ten":         user["ho_ten"],
        "email":          user["email"],
        "lop":            user["lop"],
        "character_type": user["character_type"],
        "avatar_final":   user["avatar_final"],
        "status":         user["status"],
        "created_at":     str(user["created_at"]),
    })


# ── Leaderboard (public) ───────────────────────────────────────────────

@router.get("/leaderboard")
async def leaderboard(top: int = 20):
    """Bảng xếp hạng công khai — không cần đăng nhập."""
    from app.services.gamification import BADGES, tinh_cap_do
    rows = await crud.get_leaderboard_web(min(top, 50))
    for r in rows:
        icon, _, _ = tinh_cap_do(r["xp"])
        r["level_icon"] = icon
        # Chuyển badge keys → {icon, ten}
        badge_list = []
        for bk in (r.get("badges") or []):
            if bk in BADGES:
                badge_list.append({"key": bk, "icon": BADGES[bk]["icon"], "ten": BADGES[bk]["ten"]})
        r["badge_list"] = badge_list
        r.pop("badges", None)
    return JSONResponse({"leaderboard": rows, "total": len(rows)})
