"""Google OAuth 2.0 utilities."""
import secrets
import logging
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone

import httpx
import jwt

from app.config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI, SECRET_KEY,
)

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_login_url(state: str = "") -> str:
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
        "state":         state or secrets.token_urlsafe(16),
    }
    return GOOGLE_AUTH_URL + "?" + urlencode(params)


async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        })
        if resp.status_code != 200:
            logger.error(f"Google token exchange failed: {resp.text}")
            raise ValueError("Không thể xác thực với Google")
        return resp.json()


async def get_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code != 200:
            raise ValueError("Không lấy được thông tin Google")
        return resp.json()
    # returns: {id, email, name, picture, ...}


def create_session_token(google_id: str, email: str, extra: dict = None) -> str:
    payload = {
        "sub":   google_id,
        "email": email,
        "iat":   datetime.now(timezone.utc),
        "exp":   datetime.now(timezone.utc) + timedelta(days=7),
        **(extra or {}),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_session_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
