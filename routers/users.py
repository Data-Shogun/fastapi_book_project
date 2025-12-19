from typing import Annotated
from fastapi import APIRouter, Depends
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from .auth import get_current_user


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

    user_model = db.query(User).filter(User.username == user.get("username")).first()
    return user_model
