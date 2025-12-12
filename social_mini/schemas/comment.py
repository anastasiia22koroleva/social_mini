from datetime import datetime
from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    """Входная схема для создания комментария."""
    pass


class CommentOut(CommentBase):
    """Схема вывода комментария."""
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # pydantic v2