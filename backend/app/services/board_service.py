from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.board import Board
from app.models.list import List
from app.models.card import Card
from app.schemas.board import BoardCreate, BoardUpdate
from datetime import datetime, timezone
import uuid

async def create_board(data: BoardCreate, user_id: str, db: AsyncSession) -> Board:
    board = Board(
        id=str(uuid.uuid4()),
        title=data.title,
        owner_id=user_id
    )

    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board

async def get_user_boards(user_id: str, db: AsyncSession) -> list[Board]:
    result = await db.execute(
        select(Board)
        .where(Board.owner_id == user_id, Board.deleted_at == None)
    )

    return result.scalars().all()

async def get_board_detail(board_id: str, user_id: str, db: AsyncSession) -> Board:
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id, Board.owner_id == user_id, Board.deleted_at == None)
        .options(
            selectinload(Board.lists.and_(List.deleted_at == None)).selectinload(List.cards.and_(Card.deleted_at == None))
        )

    )

    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board

async def update_board(board_id: str, data: BoardUpdate, user_id: str, db: AsyncSession) -> Board:
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id, Board.owner_id == user_id, Board.deleted_at == None)
    )

    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    board.title = data.title
    await db.commit()
    await db.refresh(board)
    return board

async def delete_board(board_id: str, user_id: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id, Board.owner_id == user_id, Board.deleted_at == None)
    )

    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    Board.deleted_at = datetime.now(timezone.utc)
    await db.commit()