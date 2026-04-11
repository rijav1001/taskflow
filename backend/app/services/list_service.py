from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.list import List
from app.models.board import Board
from app.schemas.list import ListCreate
from datetime import datetime, timezone
import uuid

async def create_list(data: ListCreate, user_id: str, db: AsyncSession) -> List:
    # verify board exists and belongs to user
    result = await db.execute(
        select(Board)
        .where(Board.id == data.board_id, Board.owner_id == user_id, Board.deleted_at == None)
    )

    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    lst = List(
        id=str(uuid.uuid4()),
        title=data.title,
        board_id=data.board_id
    )
    db.add(lst)
    await db.commit()

    result = await db.execute(
        select(List)
        .where(List.id == lst.id)
        .options(selectinload(List.cards))
    )
    return result.scalar_one()

async def get_list(list_id: str, user_id: str, db: AsyncSession) -> List:
    result = await db.execute(
        select(List)
        .join(Board, Board.id == List.board_id)
        .where(List.id == list_id, Board.owner_id == user_id, List.deleted_at == None)
        .options(selectinload(List.cards))
    )
    
    lst = result.scalar_one_or_none()
    if not lst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return lst

async def delete_list(list_id: str, user_id: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(List)
        .join(Board, Board.id == List.board_id)
        .where(List.id == list_id, Board.owner_id == user_id, List.deleted_at == None)
    )
    
    lst = result.scalar_one_or_none()
    if not lst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    lst.deleted_at = datetime.now(timezone.utc)
    await db.commit()