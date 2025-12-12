from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.like import Like


async def like_post(db: AsyncSession, user_id: int, post_id: int) -> Like:
    # проверим, нет ли уже лайка
    q = select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
    res = await db.execute(q)
    like = res.scalar_one_or_none()
    if like:
        return like

    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


async def unlike_post(db: AsyncSession, user_id: int, post_id: int) -> None:
    q = delete(Like).where(Like.user_id == user_id, Like.post_id == post_id)
    await db.execute(q)
    await db.commit()


async def get_likes_count(db: AsyncSession, post_id: int) -> int:
    q = select(func.count(Like.id)).where(Like.post_id == post_id)
    res = await db.execute(q)
    return res.scalar() or 0


async def get_likes_for_post(db: AsyncSession, post_id: int):
    q = select(Like).where(Like.post_id == post_id)
    res = await db.execute(q)
    return res.scalars().all()