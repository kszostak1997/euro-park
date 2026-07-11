from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.token import LoginRequest, RefreshRequest, TokenPair
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(request: Request, data: UserCreate, db: DbSession) -> User:
    return await AuthService(db).register(data)


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: DbSession) -> TokenPair:
    return await AuthService(db).login(data.email, data.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest, db: DbSession) -> TokenPair:
    return await AuthService(db).refresh(data.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser) -> User:
    return current_user
