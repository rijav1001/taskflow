from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.card import CardCreate, CardUpdate, CardMove, CardResponse
from app.services.card_service import create_card, update_card, move_card, delete_card, get_card
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cards", tags=["Cards"])

@router.post("", response_model=CardResponse)
async def create(data: CardCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_card(data, user.id, db)

@router.get("/{card_id}", response_model=CardResponse)
async def get(card_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_card(card_id, user.id, db)

@router.put("/{card_id}", response_model=CardResponse)
async def update(card_id: str, data: CardUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_card(card_id, data, user.id, db)

@router.put("/{card_id}/move", response_model=CardResponse)
async def move(card_id: str, data: CardMove, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await move_card(card_id, data, user.id, db)

@router.delete("/{card_id}", status_code=204)
async def delete(card_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_card(card_id, user.id, db)