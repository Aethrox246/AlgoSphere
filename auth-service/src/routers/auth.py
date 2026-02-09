from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import random
from redis.asyncio import Redis
from ..database import get_db
from ..models.user import User
from ..models.email_otp import EmailOTP
from src.schemas.user import UserCreate, UserOut
from ..utils.security import verify_password, create_access_token, create_refresh_token, decode_token, get_password_hash
from ..dependencies import oauth2_scheme, get_current_user, limiter
from src.schemas.auth import Token, ForgotPasswordRequest, ResetPasswordRequest
from src.utils.email import send_otp_email
from src.config import REDIS_URL


router = APIRouter(prefix="/auth", tags=["auth"])

redis = Redis.from_url(REDIS_URL)





@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,  # ← Add this
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(select(User).where(User.email == form_data.username)).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.is_active or (user.suspended_until and user.suspended_until > datetime.now(timezone.utc)) or user.deleted_at:
        raise HTTPException(status_code=403, detail="Account inactive, suspended or deleted")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    jti = decode_token(refresh_token)["jti"]
    await redis.setex(f"refresh:{jti}", 30*24*3600, user.id)

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
async def refresh(
    request: Request,  # ← Add this
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token)
    jti = payload["jti"]
    user_id = int(payload["sub"])

    stored_user_id = await redis.get(f"refresh:{jti}")
    if not stored_user_id or int(stored_user_id) != user_id:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    await redis.delete(f"refresh:{jti}")
    new_jti = decode_token(new_refresh)["jti"]
    await redis.setex(f"refresh:{new_jti}", 30*24*3600, user.id)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }


@router.post("/logout")
@limiter.limit("10/minute")
async def logout(
    request: Request,  # ← Add this
    token: str = Depends(oauth2_scheme)
):
    payload = decode_token(token)
    jti = payload["jti"]
    await redis.delete(f"refresh:{jti}")
    return {"message": "Logged out successfully"}


@router.post("/password/forgot")
@limiter.limit("5/minute")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    user=await db.execute(select(User).where(User.email == request.email)).scalar_one_or_none()
    if not user:
        return {"message":"If the email exists, an OTP has been sent."}
    
    otp = str(random.randint(100000, 999999))
    otp_hash = get_password_hash(otp)

    otp_entry = EmailOTP(
        user_id=user.id,
        code_hash=otp_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db.add(otp_entry)
    await db.commit()

    await send_otp_email(user.email, otp)

    return {"message":"If the email exists, an OTP has been sent."}

@router.post("/password/reset")
@limiter.limit("5/minute")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(select(User).where(User.email == request.email)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find latest valid OTP
    otp_entry = await db.execute(
        select(EmailOTP)
        .where(EmailOTP.user_id == user.id)
        .where(EmailOTP.used_at.is_(None))
        .where(EmailOTP.expires_at > datetime.now(timezone.utc))
        .order_by(EmailOTP.created_at.desc())
    ).scalar_one_or_none()

    if not otp_entry or not verify_password(request.otp, otp_entry.code_hash):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Mark OTP as used
    otp_entry.used_at = datetime.now(timezone.utc)
    user.password_hash = get_password_hash(request.new_password)
    user.last_login_at = None  # Optional: force re-login

    # Revoke all refresh sessions
    await redis.delete(f"refresh:*")  # Simple way - in production use pattern delete

    await db.commit()

    return {"message": "Password reset successful. Please login again."}

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def signup(
    request: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check for existing email
    existing_email = await db.execute(select(User).where(User.email == request.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check for existing username
    existing_username = await db.execute(select(User).where(User.username == request.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash password
    hashed_password = get_password_hash(request.password)

    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=hashed_password,
        is_active=True  # Change to False if you want email verification first
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Optional: send welcome/verification email (placeholder)
    # await send_welcome_email(new_user.email)

    return new_user
