from fastapi import APIRouter, Request, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.token import LoginRequest, RefreshRequest, TokenPair
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(request: Request, data: UserCreate, db: DbSession) -> User:
    return await AuthService(db).register(data)


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: DbSession) -> TokenPair:
    return await AuthService(db).login(data.email, data.password)


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("10/minute")
async def refresh(request: Request, data: RefreshRequest, db: DbSession) -> TokenPair:
    return await AuthService(db).refresh(data.refresh_token)


@router.get("/current-user", response_model=UserRead)
async def read_current_user(current_user: CurrentUser) -> User:
    return current_user
