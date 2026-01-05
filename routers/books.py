import requests
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from config import Config
from models import Book
from routers.auth import get_current_user, redirect_to_login


N8N_WEBHOOK_URL = Config.N8N_WEBHOOK_URL

templates = Jinja2Templates(directory='templates')

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


class EditBookRequest(BaseModel):
    title: str = Field(max_length=200)
    author: str = Field(max_length=200)
    category: str = Field(max_length=200)
    summary: str = Field(max_length=1000)


## Pages ##

@router.get('/my-books-page')
async def render_my_books_page(request: Request, db: db_dependency):

    token = request.cookies.get('access_token')

    if token is None:
        return redirect_to_login()

    try:
        user = await get_current_user(token)
    except HTTPException:
        return redirect_to_login()
        
    if user is None:
        return redirect_to_login()
    
    books = db.query(Book).filter(Book.owner_id==user.get("id")).all()

    return templates.TemplateResponse('books.html', {
        'request': request,
        'books': books
    })


@router.get('/edit-book-page/{book_id}')
async def render_edit_book_page(request: Request, book_id: int, db: db_dependency):
    token = request.cookies.get('access_token')

    if token is None:
        return redirect_to_login()

    try:
        user = await get_current_user(token)
    except HTTPException:
        return redirect_to_login()
        
    if user is None:
        return redirect_to_login()
    
    book = db.query(Book).filter(Book.owner_id == user.get('id')).filter(Book.id == book_id).first()

    return templates.TemplateResponse('edit_book.html', {
        'request': request,
        'book': book
    })

## Endpoints ##

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
    

@router.put('/edit-book/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit_book(
    book_id: int, edit_book_request: EditBookRequest, db: db_dependency, user: user_dependency
    ):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )

    book_model = db.query(Book).filter(Book.id == book_id).first()

    book_model.title = edit_book_request.title
    book_model.author = edit_book_request.author
    book_model.category = edit_book_request.category
    book_model.summary = edit_book_request.summary

    try:
        db.add(book_model)
        db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database storage failed.",
        ) from exc
    

@router.delete('/delete-book/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int, db: db_dependency, user: user_dependency
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed.'
        )
    
    try:
        db.query(Book).filter(Book.id==book_id).delete()
        db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database interaction failed",
        ) from exc