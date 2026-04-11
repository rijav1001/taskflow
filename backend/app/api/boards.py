from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardDetailResponse
from app.services.board_service import create_board, get_user_boards, get_board_detail, update_board, delete_board
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/boards", tags=["Boards"])

@router.post("", response_model=BoardResponse)
async def create(data: BoardCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_board(data, user.id, db)

@router.get("", response_model=list[BoardResponse])
async def list_boards(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_user_boards(user.id, db)

@router.get("/{board_id}", response_model=BoardDetailResponse)
async def get_board(board_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_board_detail(board_id, user.id, db)

@router.put("/{board_id}", response_model=BoardResponse)
async def update(board_id: str, data: BoardUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_board(board_id, data, user.id, db)

@router.delete("/{board_id}", status_code=204)
async def delete(board_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await delete_board(board_id, user.id, db)