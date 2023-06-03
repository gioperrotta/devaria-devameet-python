from pydantic import BaseModel, Field

class UpdateUser(BaseModel):
    name: str = Field(..., min_length=2)
    avatar: str