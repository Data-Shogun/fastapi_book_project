from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from models import User
from database import SessionLocal
from config import Config


router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

JWT_SECRET_KEY = Config.JWT_SECRET_KEY
JWT_HASH_ALGORITHM = Config.JWT_HASH_ALGORITHM


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, user_role: str, expires_delta: timedelta
):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username, "id": user_id, "role": user_role, "exp": expires}
    return jwt.encode(encode, key=JWT_SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)


db_dependency = Annotated[Session, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth_bearer)]
):
    
    try:
        decode = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])
        username: str = decode.get("sub")
        user_id: int = decode.get("id")
        user_role: str = decode.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist anymore",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed."
        ) from exc


def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response


class CreateUserRequest(BaseModel):
    username: str = Field(max_length=200)
    email: str
    password: str = Field(min_length=6)
    role: str = Field(max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


## Pages ##

templates = Jinja2Templates('templates')

@router.get("/register-page")
async def render_register_page(request: Request):

    return templates.TemplateResponse('signup.html', {
        'request': request,       
    })


@router.get("/login-page")
async def render_login_page(request: Request):

    return templates.TemplateResponse('login.html', {
        'request': request,
    })


@router.get('/logout')
async def logout_page():
    return redirect_to_login()

## Endpoints ##

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def add_new_user(create_user_request: CreateUserRequest, db: db_dependency):
    existing_user = (
        db.query(User).filter(User.username == create_user_request.username).first()
        or db.query(User).filter(User.email == create_user_request.email).first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already exists!",
        )

    create_user_model = User(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
    )

    try:
        db.add(create_user_model)
        db.commit()
    except Exception as exc:
        print(exc)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed."
        )

    token = create_access_token(
        user.username, user.id, user.role, timedelta(days=7)
    )

    return {"access_token": token, "token_type": "Bearer"}