from pydantic import BaseModel
from datetime import datetime

class CardCreate(BaseModel):
    title: str
    description: str | None = None
    list_id: str

class CardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

class CardMove(BaseModel):
    list_id: str
    order: float

class CardResponse(BaseModel):
    id: str
    title: str
    description: str | None
    list_id: str
    order: float
    created_at: datetime

    model_config = {"from_attributes": True}