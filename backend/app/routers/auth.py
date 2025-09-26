from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from ..core.schemas import AuthTokens, UserCreate, UserRead
from ..db import get_session, settings
from ..models import RefreshToken, User

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(data: dict, expires_minutes: int) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_auth_tokens(user: User, session: Session) -> AuthTokens:
    access = create_token({"sub": str(user.id)}, settings.access_token_expiry_minutes)
    refresh = create_token({"sub": str(user.id), "type": "refresh"}, settings.refresh_token_expiry_minutes)
    token_model = RefreshToken(user_id=user.id, token=refresh, expires_at=datetime.utcnow() + timedelta(minutes=settings.refresh_token_expiry_minutes))
    session.add(token_model)
    session.commit()
    return AuthTokens(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead(id=user.id, email=user.email, created_at=user.created_at)


@router.post("/login", response_model=AuthTokens)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)) -> AuthTokens:
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return create_auth_tokens(user, session)


@router.post("/refresh", response_model=AuthTokens)
def refresh_token(refresh_token: str, session: Session = Depends(get_session)) -> AuthTokens:
    token_obj = session.exec(select(RefreshToken).where(RefreshToken.token == refresh_token)).first()
    if not token_obj or token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    user_id = int(payload["sub"])
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return create_auth_tokens(user, session)

