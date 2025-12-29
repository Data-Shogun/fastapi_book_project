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

    model_config = {
        "json_schema_extra": {
            "example": {"title": "Deep Work", "author": "Cal Newport"}
        }
    }


@router.get("/my-books", status_code=status.HTTP_200_OK)
async def get_all_books(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )

    books = db.query(Book).filter(Book.owner_id == user.get("id")).all()
    return books


@router.get("/book-info/{book_id}", status_code=status.HTTP_200_OK)
async def get_book(book_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )
    return book


@router.post("/add-book", status_code=status.HTTP_201_CREATED)
async def add_new_book(
    add_book_request: AddBookRequest, user: user_dependency, db: db_dependency
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )

    payload = {"title": add_book_request.title, "author": add_book_request.author}

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60)
        response.raise_for_status()  # raises for 4xx/5xx from N8N itself
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook service is unreachable or timedout.",
        ) from exc

    try:
        response_dict = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response received from webhook service (malformed JSON)",
        ) from exc

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
