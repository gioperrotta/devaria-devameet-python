from pydantic import BaseModel, Field
from typing import List


class CreateMeet(BaseModel):
    name: str = Field(..., min_length=2)
    color: str = Field(..., regex='#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$')


class UpdateObjectMeet(BaseModel):
    id: int = None
    name: str
    x: int = Field(..., ge=0, le=7)
    y: int = Field(..., ge=0, le=7)
    zindex: int
    orientation: str = Field(..., regex='(top|right|bottom|left)')


class UpdateMeet(BaseModel):
    name: str = Field(..., min_length=2)
    color: str = Field(..., regex='#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$')
    objects: List[UpdateObjectMeet] = []