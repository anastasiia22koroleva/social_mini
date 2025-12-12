from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.follow import Follow


async def follow_user(db: AsyncSession, follower_id: int, user_id: int) -> Follow:
    if follower_id == user_id:
        raise ValueError("Нельзя подписаться на себя")

    q = select(Follow).where(
        Follow.follower_id == follower_id,
        Follow.user_id == user_id,
    )
    res = await db.execute(q)
    existing = res.scalar_one_or_none()
    if existing:
        return existing

    follow = Follow(follower_id=follower_id, user_id=user_id)
    db.add(follow)
    await db.commit()
    await db.refresh(follow)
    return follow


async def unfollow_user(db: AsyncSession, follower_id: int, user_id: int) -> None:
    q = delete(Follow).where(
        Follow.follower_id == follower_id,
        Follow.user_id == user_id,
    )
    await db.execute(q)
    await db.commit()


async def get_following(db: AsyncSession, user_id: int):
    q = select(Follow).where(Follow.follower_id == user_id)
    res = await db.execute(q)
    return res.scalars().all()


async def get_followers(db: AsyncSession, user_id: int):
    q = select(Follow).where(Follow.user_id == user_id)
    res = await db.execute(q)
    return res.scalars().all()