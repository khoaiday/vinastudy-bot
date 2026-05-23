"""Google OAuth routes: /auth/google/login & /auth/google/callback."""
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from app.auth.google_oauth import (
    get_login_url, exchange_code, get_user_info, create_session_token,
)
from app.database import crud
from app.config import BASE_DOMAIN

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/google/login")
async def google_login(tg_id: str = ""):
    """Redirect sang Google OAuth. tg_id được forward qua state."""
    url = get_login_url(state=tg_id or "")
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str = "", error: str = "", state: str = ""):
    """Google callback: đổi code → token → user info → tạo session.
    state chứa tg_id (telegram_id) được forward từ login URL."""
    if error or not code:
        return RedirectResponse(f"{BASE_DOMAIN}/register?error=cancelled")

    try:
        tokens    = await exchange_code(code)
        user_info = await get_user_info(tokens["access_token"])
    except ValueError:
        return RedirectResponse(f"{BASE_DOMAIN}/register?error=oauth_fail")

    google_id = user_info["id"]
    email     = user_info["email"]
    picture   = user_info.get("picture", "")

    # Upsert web_user
    web_user = await crud.upsert_web_user(google_id, email, user_info.get("name", ""))

    # Tạo JWT session token
    session_token = create_session_token(google_id, email, {
        "picture": picture,
        "status":  web_user["status"],
    })

    # Forward tg_id (state) về register để JS lưu vào localStorage
    tg_param = f"&tg_id={state}" if state and state.isdigit() else ""

    # Redirect về register với token
    if web_user["status"] == "approved":
        redirect = f"{BASE_DOMAIN}/register?token={session_token}&step=done{tg_param}"
    else:
        redirect = f"{BASE_DOMAIN}/register?token={session_token}&step=2{tg_param}"

    return RedirectResponse(redirect)


@router.get("/me")
async def get_me(request: Request):
    """Lấy thông tin user từ JWT token (gọi từ JS)."""
    from app.auth.google_oauth import decode_session_token
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Chưa đăng nhập")
    token = auth[7:]
    payload = decode_session_token(token)
    if not payload:
        raise HTTPException(401, "Token hết hạn")

    user = await crud.get_web_user_by_google_id(payload["sub"])
    if not user:
        raise HTTPException(404, "Không tìm thấy tài khoản")
    return JSONResponse({
        "google_id":        user["google_id"],
        "email":            user["email"],
        "ho_ten":           user["ho_ten"],
        "character_type":   user["character_type"],
        "avatar_final":     user["avatar_final"],
        "status":           user["status"],
        "rejection_reason": user.get("rejection_reason") or "",
    })
