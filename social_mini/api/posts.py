from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from social_mini import crud, database, schemas
from social_mini.core.security import get_current_user
from social_mini.models.user import User

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=schemas.PostOut)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud.create_post(db, post, owner_id=current_user.id)

@router.get("/", response_model=list[schemas.PostOut])
async def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.get_posts(db, skip=skip, limit=limit)

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    post = await crud.get_post(db, post_id)
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await crud.delete_post(db, post_id)
    return {"ok": True}