from datetime import datetime
from pydantic import BaseModel


class FollowOut(BaseModel):
    id: int
    follower_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True