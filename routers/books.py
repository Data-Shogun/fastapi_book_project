import requests
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from config import Config
from models import Book
from routers.auth import get_current_user


N8N_WEBHOOK_URL = Config.N8N_WEBHOOK_URL

router = APIRouter(prefix="/books", tags=["books"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class AddBookRequest(BaseModel):
    title: str = Field(max_length=200)
    author: str = Field(max_length=200)


@router.get("/my-books", status_code=status.HTTP_200_OK)
async def get_all_books(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )

    books = db.query(Book).filter(Book.owner_id == user.get("id")).all()
    return books


@router.post("/add-book", status_code=status.HTTP_201_CREATED)
async def add_new_book(
    add_book_request: AddBookRequest, user: user_dependency, db: db_dependency
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )

    payload = {"title": add_book_request.title, "author": add_book_request.author}

    response_dict = json.loads(requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60e3).content)
    if "output" in response_dict:
        result = response_dict["output"]
    else:
        result = response_dict

    new_book = Book(
        title=add_book_request.title,
        author=add_book_request.author,
        summary=result.get("summary_by_ai"),
        category=result.get("category_by_ai"),
        owner_id=user.get("id"),
    )

    try:
        db.add(new_book)
        db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database storage failed.",
        ) from exc
