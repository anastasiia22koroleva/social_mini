from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..crud import follow as follow_crud
from ..schemas.follow import FollowOut
from ..core.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/{user_id}/follow", response_model=FollowOut)
async def follow(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # проверим, что пользователь есть
    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        follow_obj = await follow_crud.follow_user(db, follower_id=current_user.id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return follow_obj

@router.delete("/{user_id}/follow", status_code=204)
async def unfollow(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    await follow_crud.unfollow_user(db, follower_id=current_user.id, user_id=user_id)
    return

@router.get("/me/following", response_model=list[FollowOut])
async def get_my_following(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    follows = await follow_crud.get_following(db, current_user.id)
    return follows

@router.get("/me/followers", response_model=list[FollowOut])
async def get_my_followers(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    follows = await follow_crud.get_followers(db, current_user.id)
    return follows

