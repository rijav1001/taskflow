from pydantic import BaseModel
from datetime import datetime
from app.schemas.list import ListResponse

class BoardCreate(BaseModel):
    title: str

class BoardUpdate(BaseModel):
    title: str

class BoardResponse(BaseModel):
    id: str
    title: str
    owner_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class BoardDetailResponse(BaseModel):
    id: str
    title: str
    owner_id: str
    created_at: datetime
    lists: list[ListResponse] = []

    model_config = {"from_attributes": True}