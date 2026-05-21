"""Admin API: duyệt tài khoản, thống kê, quản lý lớp."""
import logging
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.config import ADMIN_SECRET, TELEGRAM_TOKEN
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
    if user.get("telegram_id") and TELEGRAM_TOKEN:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
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
    return JSONResponse({"ok": True, "message": f"Đã từ chối {user['ho_ten']}"})


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
