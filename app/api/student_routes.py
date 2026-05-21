"""Student API: hoàn tất đăng ký, upload avatar, chỉnh sửa profile."""
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.auth.google_oauth import decode_session_token
from app.auth.avatar import generate_avatar_pipeline
from app.database import crud

logger = logging.getLogger(__name__)
router = APIRouter()


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
    ho_ten:         str
    lop:            str = "3"
    character_type: str = "chien_binh"
    avatar_face_b64: str           # base64 ảnh mặt đã crop (từ canvas client)
    telegram_id:    int | None = None  # tg_id từ link bot


class UpdateProfileBody(BaseModel):
    ho_ten:         str | None = None
    lop:            str | None = None
    character_type: str | None = None
    avatar_face_b64: str | None = None  # nếu muốn đổi ảnh


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
    avatar_result = generate_avatar_pipeline(body.avatar_face_b64, body.character_type)
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
    )

    # Lưu telegram_id nếu có (gửi từ link bot)
    if body.telegram_id:
        await crud.patch_web_user(google_id, {"telegram_id": body.telegram_id})

    return JSONResponse({"ok": True, "status": "pending",
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
    if body.character_type: updates["character_type"]  = body.character_type

    if body.avatar_face_b64:
        char = body.character_type or user["character_type"]
        res  = generate_avatar_pipeline(body.avatar_face_b64, char)
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
        "character_type": updated["character_type"],
        "avatar_final":   updated["avatar_final"],
    }})


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
