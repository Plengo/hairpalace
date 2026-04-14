from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.features.users.schemas import (
    LoginIn,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    RefreshIn,
    RegisterIn,
    TokenOut,
    UserOut,
    UserUpdateIn,
)
from app.features.users.service import UserService

router = APIRouter(prefix="/auth", tags=["Auth & Users"])


def _service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: RegisterIn, svc: UserService = Depends(_service)) -> UserOut:
    return await svc.register(payload)


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn, svc: UserService = Depends(_service)) -> TokenOut:
    return await svc.login(payload)


@router.post("/refresh", response_model=TokenOut)
async def refresh(payload: RefreshIn, svc: UserService = Depends(_service)) -> TokenOut:
    return await svc.refresh(payload)


@router.get("/me", response_model=UserOut)
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    svc: UserService = Depends(_service),
) -> UserOut:
    return await svc.get_profile(user_id)


@router.patch("/me", response_model=UserOut)
async def update_profile(
    payload: UserUpdateIn,
    user_id: int = Depends(get_current_user_id),
    svc: UserService = Depends(_service),
) -> UserOut:
    return await svc.update_profile(user_id, payload)


@router.post("/password-reset/request", status_code=202)
async def request_password_reset(
    payload: PasswordResetRequestIn,
    svc: UserService = Depends(_service),
) -> dict:
    await svc.request_password_reset(payload)
    return {"detail": "If that email is registered, a reset link has been sent."}


@router.post("/password-reset/confirm", status_code=200)
async def confirm_password_reset(
    payload: PasswordResetConfirmIn,
    svc: UserService = Depends(_service),
) -> dict:
    await svc.confirm_password_reset(payload)
    return {"detail": "Password updated successfully."}
