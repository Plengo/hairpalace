from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.features.users.schemas import (
    LoginIn,
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
