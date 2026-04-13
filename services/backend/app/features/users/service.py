from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.features.users.models import User
from app.features.users.repository import UserRepository
from app.features.users.schemas import (
    LoginIn,
    RefreshIn,
    RegisterIn,
    TokenOut,
    UserOut,
    UserUpdateIn,
)


class UserService:

    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def register(self, payload: RegisterIn) -> UserOut:
        existing = await self._repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = User(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            phone=payload.phone,
        )
        user = await self._repo.create(user)
        return UserOut.model_validate(user)

    async def login(self, payload: LoginIn) -> TokenOut:
        user = await self._repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            # Same error message for both — prevents email enumeration
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

        token_payload = {"sub": str(user.id), "is_admin": user.is_admin}
        return TokenOut(
            access_token=create_access_token(token_payload),
            refresh_token=create_refresh_token(token_payload),
        )

    async def refresh(self, payload: RefreshIn) -> TokenOut:
        data = decode_token(payload.refresh_token)
        user = await self._repo.get_by_id(int(data["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        token_payload = {"sub": str(user.id), "is_admin": user.is_admin}
        return TokenOut(
            access_token=create_access_token(token_payload),
            refresh_token=create_refresh_token(token_payload),
        )

    async def get_profile(self, user_id: int) -> UserOut:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserOut.model_validate(user)

    async def update_profile(self, user_id: int, payload: UserUpdateIn) -> UserOut:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        user = await self._repo.save(user)
        return UserOut.model_validate(user)
