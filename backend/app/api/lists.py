from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.list import ListCreate, ListResponse
from app.services.list_service import create_list, delete_list, get_list
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/lists", tags=["Lists"])

@router.post("", response_model=ListResponse)
async def create(data: ListCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_list(data, user.id, db)

@router.get("/{list_id}", response_model=ListResponse)
async def get(list_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_list(list_id, user.id, db)

@router.delete("/{list_id}", status_code=204)
async def delete(list_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_list(list_id, user.id, db)