"""
FastAPI dependencies — שימוש: Depends(require_admin) על כל route מוגן.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.core.security import decode_access_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def require_admin(token: str = Depends(oauth2_scheme)) -> str:
    try:
        username = decode_access_token(token)
        if username != settings.ADMIN_USERNAME:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token לא תקין או פג תוקף — יש להתחבר מחדש",
            headers={"WWW-Authenticate": "Bearer"},
        )
