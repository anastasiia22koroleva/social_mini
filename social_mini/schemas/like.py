from datetime import datetime
from pydantic import BaseModel


class LikeOut(BaseModel):
    """Отдельный лайк."""
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LikesSummary(BaseModel):
    """Краткая инфа по лайкам поста."""
    post_id: int
    likes_count: int