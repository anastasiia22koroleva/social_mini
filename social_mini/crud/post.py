# app/crud/post.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from social_mini.models.post import Post
from social_mini.schemas import PostCreate  # если используешь схемы

async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Post).offset(skip).limit(limit))
    return result.scalars().all()

async def create_post(db: AsyncSession, post: PostCreate, owner_id: int):
    db_post = Post(**post.model_dump(), owner_id=owner_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def get_post(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalars().first()

async def delete_post(db: AsyncSession, post_id: int):
    post = await get_post(db, post_id)
    if post:
        await db.delete(post)
        await db.commit()
    return post