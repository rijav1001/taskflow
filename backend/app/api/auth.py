from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserRegister, UserResponse, Token
from app.services.auth_service import register_user, login_user
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await register_user(data, db)

@router.post("/login", response_model=Token)
async def login(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await login_user(data, db)