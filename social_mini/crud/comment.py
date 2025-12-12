from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.comment import Comment
from ..schemas.comment import CommentCreate


async def create_comment(
    db: AsyncSession,
    user_id: int,
    post_id: int,
    data: CommentCreate,
) -> Comment:
    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=data.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments_for_post(db: AsyncSession, post_id: int):
    q = select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.desc())
    res = await db.execute(q)
    return res.scalars().all()


async def delete_comment(db: AsyncSession, comment_id: int, user_id: int) -> bool:
    q = select(Comment).where(Comment.id == comment_id)
    res = await db.execute(q)
    comment = res.scalar_one_or_none()
    if not comment:
        return False
    if comment.user_id != user_id:
        # не владелец — запрещаем
        return False
    await db.delete(comment)
    await db.commit()
    return True