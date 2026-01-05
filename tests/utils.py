import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import Base
from models import Book, User
from routers.auth import bcrypt_context
from main import app


SQLALCHEMY_TEST_URL = "sqlite:///./testdb.db"


engine = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    user = {"username": "testuser", "id": 1, "user_role": "admin"}
    return user


@pytest.fixture
def test_book():
    book = Book(
        title="test_title",
        author="test_author",
        summary="test_summary",
        category="test_category",
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(book)
    db.commit()
    yield book
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM books;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = User(
        username="testuser",
        email="testuser@email.com",
        hashed_password=bcrypt_context.hash("test1234!"),
        is_active=True,
        role="admin",
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()