"""
Authentication API — login + rate limiting.
Route /api/auth/login אינו מוגן (הוא שמייצר את ה-token).
"""
from collections import defaultdict
from time import time

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

# ── Rate limiter: 5 ניסיונות ב-5 דקות לכל IP ─────────────────
_WINDOW  = 300   # שניות
_MAX     = 5
_attempts: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str) -> None:
    now  = time()
    hits = [t for t in _attempts[ip] if now - t < _WINDOW]
    if len(hits) >= _MAX:
        remaining = int(_WINDOW - (now - hits[0]))
        raise HTTPException(
            status_code=429,
            detail=f"יותר מדי ניסיונות התחברות. נסה שוב בעוד {remaining // 60 + 1} דקות.",
        )
    hits.append(now)
    _attempts[ip] = hits


@router.post("/login")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    ip = request.client.host if request.client else "unknown"
    _check_rate_limit(ip)

    # אותה שגיאה לשם משתמש שגוי ולסיסמה שגויה — מונע מניית שמות משתמש
    valid = (
        form.username == settings.ADMIN_USERNAME
        and bool(settings.ADMIN_PASSWORD_HASH)
        and verify_password(form.password, settings.ADMIN_PASSWORD_HASH)
    )
    if not valid:
        raise HTTPException(status_code=401, detail="שם משתמש או סיסמה שגויים")

    token = create_access_token(form.username)
    return {"access_token": token, "token_type": "bearer"}
