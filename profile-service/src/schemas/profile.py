from pydantic import BaseModel
from datetime import datetime

class ProfileOut(BaseModel):
    user_id: str
    name: str | None
    bio: str | None
    avatar_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
