from pydantic import BaseModel
from datetime import datetime
from app.schemas.card import CardResponse

class ListCreate(BaseModel):
    title: str
    board_id: str

class ListResponse(BaseModel):
    id: str
    title: str
    board_id: str
    created_at: datetime
    cards: list[CardResponse] = []

    model_config = {"from_attributes": True}