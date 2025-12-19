import requests
from fastapi import APIRouter
from starlette import status
from pydantic import BaseModel, Field
from config import Config


N8N_WEBHOOK_URL = Config.N8N_WEBHOOK_URL

router = APIRouter(prefix="/books", tags=["books"])


class AddBookRequest(BaseModel):
    title: str = Field(max_length=200)
    author: str = Field(max_length=200)


# @router.post('/add-book', status_code=status.HTTP_201_CREATED)
# def add_new_book(add_book_request: AddBookRequest):

