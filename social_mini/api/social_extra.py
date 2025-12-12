from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from social_mini.database import get_db
from social_mini.models.post import Post
from social_mini.models.user import User
from social_mini.models.like import Like
from social_mini.models.comment import Comment
from social_mini.models.follow import Follow
from social_mini.schemas.comment import CommentCreate, CommentOut
from social_mini.schemas.like import LikeOut, LikesSummary
from social_mini.schemas.follow import FollowOut
from social_mini.core.security import SECRET_KEY, ALGORITHM

# 🟣 ВОТ ОН — router, которого не хватало
router = APIRouter(tags=["social-extra"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# ---------- текущий пользователь по токену ----------
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


# ================= ЛАЙКИ =================

@router.post("/posts/{post_id}/like", response_model=LikeOut)
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем, что пост существует
    res = await db.execute(select(Post).where(Post.id == post_id))
    post = res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Проверяем, есть ли уже лайк (делаем idempotent)
    res = await db.execute(
        select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id)
    )
    like = res.scalar_one_or_none()
    if like:
        return like

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


@router.get("/posts/{post_id}/likes", response_model=LikesSummary)
async def get_likes_for_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(func.count(Like.id)).where(Like.post_id == post_id))
    count = res.scalar() or 0
    return LikesSummary(post_id=post_id, likes_count=count)


# ================= КОММЕНТАРИИ =================

@router.post("/posts/{post_id}/comments", response_model=CommentOut)
async def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем, что пост существует
    res = await db.execute(select(Post).where(Post.id == post_id))
    post = res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        user_id=current_user.id,
        post_id=post_id,
        content=comment_in.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def list_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
    )
    return res.scalars().all()


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = res.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await db.delete(comment)
    await db.commit()
    return


# ================= ПОДПИСКИ =================

@router.post("/users/{user_id}/follow", response_model=FollowOut)
async def follow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Нельзя подписаться на себя")

    # Проверяем, что пользователь есть
    res = await db.execute(select(User).where(User.id == user_id))
    target = res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, существует ли подписка
    res = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.user_id == user_id,
        )
    )
    follow = res.scalar_one_or_none()
    if follow:
        return follow

    follow = Follow(follower_id=current_user.id, user_id=user_id)
    db.add(follow)
    await db.commit()
    await db.refresh(follow)
    return follow


@router.delete("/users/{user_id}/follow", status_code=204)
async def unfollow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        delete(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.user_id == user_id,
        )
    )
    await db.commit()
    return


@router.get("/users/me/following", response_model=List[FollowOut])
async def get_my_following(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Follow).where(Follow.follower_id == current_user.id))
    return res.scalars().all()


@router.get("/users/me/followers", response_model=List[FollowOut])
async def get_my_followers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Follow).where(Follow.user_id == current_user.id))
    return res.scalars().all()