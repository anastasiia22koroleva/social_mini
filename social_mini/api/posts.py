from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from social_mini import crud, schemas
from social_mini.core.security import get_current_user
from social_mini.database import get_db
from social_mini.models.user import User
from social_mini.models.post import Post

from ..schemas.comment import CommentCreate, CommentOut
from ..schemas.like import LikeOut, LikesSummary
from ..crud import comment as comment_crud
from ..crud import like as like_crud

router = APIRouter(prefix="/posts", tags=["posts"])


# ---------- Посты ----------

@router.post("/", response_model=schemas.PostOut)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud.create_post(db, post, owner_id=current_user.id)


@router.get("/", response_model=list[schemas.PostOut])
async def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_posts(db, skip=skip, limit=limit)


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await crud.get_post(db, post_id)
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await crud.delete_post(db, post_id)
    return {"ok": True}


@router.put("/{post_id}", response_model=schemas.PostOut)
async def update_post(
    post_id: int,
    post_in: schemas.PostCreate,   # можно завести отдельную схему, но этой достаточно
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ищем пост
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # проверяем, что это наш пост
    if db_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this post",
        )

    # обновляем
    db_post.title = post_in.title
    db_post.content = post_in.content

    await db.commit()
    await db.refresh(db_post)
    return db_post


# ---------- Лайки ----------

@router.post("/{post_id}/like", response_model=LikeOut)
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверим, что пост существует
    q = select(Post).where(Post.id == post_id)
    res = await db.execute(q)
    post = res.scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    like = await like_crud.like_post(db, current_user.id, post_id)
    return like


@router.delete("/{post_id}/like", status_code=204)
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await like_crud.unlike_post(db, current_user.id, post_id)
    return


@router.get("/{post_id}/likes", response_model=LikesSummary)
async def get_likes(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Можно не проверять существование поста, но лучше всё-таки:
    q = select(Post).where(Post.id == post_id)
    res = await db.execute(q)
    post = res.scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    count = await like_crud.get_likes_count(db, post_id)
    return LikesSummary(post_id=post_id, likes_count=count)


# ---------- Комментарии ----------

@router.post("/{post_id}/comments", response_model=CommentOut)
async def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверим пост
    q = select(Post).where(Post.id == post_id)
    res = await db.execute(q)
    post = res.scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    comment = await comment_crud.create_comment(
        db=db,
        user_id=current_user.id,
        post_id=post_id,
        data=comment_in,
    )
    return comment


@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def list_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    comments = await comment_crud.get_comments_for_post(db, post_id)
    return comments


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = await comment_crud.delete_comment(db, comment_id, current_user.id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden or comment not found",
        )
    return