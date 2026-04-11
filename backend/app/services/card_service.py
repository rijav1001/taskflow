from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from fastapi import HTTPException, status
from app.models.card import Card
from app.models.list import List
from app.models.board import Board
from app.schemas.card import CardCreate, CardUpdate, CardMove
from app.services.lexorank import get_initial_order, get_between_order, rebalance
from datetime import datetime, timezone
import uuid

async def _verify_list(list_id: str, user_id: str, db: AsyncSession) -> List:
    result = await db.execute(
        select(List)
        .join(Board, Board.id == List.board_id)
        .where(List.id == list_id, Board.owner_id == user_id, List.deleted_at == None)
    )

    lst = result.scalar_one_or_none()
    if not lst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return lst

async def create_card(data: CardCreate, user_id: str, db: AsyncSession) -> Card:
    await _verify_list(data.list_id, user_id, db)

    # get the highest order in the list and add GAP
    result = await db.execute(
        select(Card.order)
        .where(Card.list_id == data.list_id, Card.deleted_at == None)
        .order_by(Card.order.desc())
        .limit(1)
    )

    last_order = result.scalar_one_or_none()
    order = (last_order + 1000.0) if last_order is not None else get_initial_order()

    card = Card(
        id=str(uuid.uuid4()),
        title=data.title,
        description=data.description,
        list_id=data.list_id,
        order=order
    )

    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card

async def get_card(card_id: str, user_id: str, db: AsyncSession) -> Card:
    result = await db.execute(
        select(Card)
        .join(List, List.id == Card.list_id)
        .join(Board, Board.id == List.board_id)
        .where(Card.id == card_id, Board.owner_id == user_id, Card.deleted_at == None)
    )
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card

async def update_card(card_id: str, data: CardUpdate, user_id: str, db: AsyncSession) -> Card:
    result = await db.execute(
        select(Card)
        .join(List, List.id == Card.list_id)
        .join(Board, Board.id == List.board_id)
        .where(Card.id == card_id, Board.owner_id == user_id, Card.deleted_at == None)
    )

    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    if data.title is not None:
        card.title = data.title
    if data.description is not None:
        card.description = data.description

    await db.commit()
    await db.refresh(card)
    return card

async def move_card(card_id: str, data: CardMove, user_id: str, db: AsyncSession) -> Card:
    async with db.begin_nested():
        # Lock the card row to prevent race conditions
        result = await db.execute(
            select(Card)
            .where(Card.id == card_id, Card.deleted_at == None)
            .with_for_update()
        )

        card = result.scalar_one_or_none()
        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

        # verify target list belongs to user
        await _verify_list(data.list_id, user_id, db)

        # get all cards in target list sorted by order
        result = await db.execute(
            select(Card)
            .where(Card.list_id == data.list_id, Card.deleted_at == None, Card.id != card_id)
            .order_by(Card.order)
        )

        cards = result.scalars().all()

        # find before and after based on desired order
        before = None
        after = None
        for c in cards:
            if c.order <= data.order:
                before = c.order
            else:
                after = c.order
                break

        try:
            new_order = get_between_order(before, after)
        except ValueError:
            # rebalance needed
            all_orders = [c.order for c in cards]
            all_orders.append(data.order)
            all_orders.sort()
            new_orders = rebalance(all_orders)
            for c, o in zip(sorted(cards, key=lambda x: x.order), new_orders):
                c.order = o
            new_order = new_orders[len(new_orders) // 2]

        card.list_id = data.list_id
        card.order = new_order

    await db.commit()
    await db.refresh(card)
    return card

async def delete_card(card_id: str, user_id: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(Card)
        .join(List, List.id == Card.list_id)
        .join(Board, Board.id == List.board_id)
        .where(Card.id == card_id, Board.owner_id == user_id, Card.deleted_at == None)
    )

    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    card.deleted_at = datetime.now(timezone.utc)
    await db.commit()