from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette import status


router = APIRouter(
    prefix='',
    tags=['home']
)


@router.get('/')
async def homepage():
    return RedirectResponse(url='/books/my-books-page', status_code=status.HTTP_302_FOUND)