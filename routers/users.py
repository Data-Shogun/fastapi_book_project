from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Book
from routers.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
            , detail="Authentication failed"
        )
    user_model = db.query(User).filter(User.username == user.get("username")).first()
    return user_model


@router.delete("/delete-user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
            , detail="Authentication failed"
        )
    try:
        db.query(User).filter(User.id==user.get('id')).delete()
        # Delete their books
        db.query(Book).filter(Book.owner_id==user.get('id')).delete()
        db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database interaction failed"
        ) from exc
    