from starlette import status
from .utils import (
    app,
    override_get_db,
    override_get_current_user,
    client,
    test_book,
    TestingSessionLocal,
    bcrypt_context,
    Book,
)
from routers.admin import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_books(test_book):

    response = client.get("/admin/all-books")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "test_title",
            "author": "test_author",
            "summary": "test_summary",
            "category": "test_category",
            "owner_id": 1,
        }
    ]


def test_get_all_books_not_existing_user(monkeypatch, test_book):
    """Using monkeypatch"""

    monkeypatch.setitem(app.dependency_overrides, get_current_user, lambda: None)

    response = client.get("/admin/all-books")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication failed."}


def test_get_all_books_not_admin_user(monkeypatch, test_book):
    """Using monkeypatch"""

    override_get_current_user_regular = lambda: {
        "username": "testuser",
        "id": 1,
        "user_role": "regular",
    }

    monkeypatch.setitem(
        app.dependency_overrides, get_current_user, override_get_current_user_regular
    )

    response = client.get("/admin/all-books")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication failed."}


def test_delete_book(test_book):

    response = client.delete("/admin/delete/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Book).filter(Book.id == 1).first()

    assert model is None


def test_delete_book_not_existing_user(monkeypatch, test_book):
    """Using monkeypatch"""

    monkeypatch.setitem(app.dependency_overrides, get_current_user, lambda: None)

    response = client.delete("/admin/delete/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication failed."}

    db = TestingSessionLocal()
    all_books = db.query(Book).all()

    assert len(all_books) == 1


def test_delete_book_not_admin_user(monkeypatch, test_book):
    """Using monkeypatch"""

    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: {
            "username": "testuser",
            "email": "testuser@email.com",
            "hashed_password": bcrypt_context.hash("test1234!"),
            "is_active": True,
            "user_role": "regular",
        },
    )

    response = client.delete("/admin/delete/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication failed."}

    db = TestingSessionLocal()
    all_books = db.query(Book).all()

    assert len(all_books) == 1
