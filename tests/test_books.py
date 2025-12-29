import json
import requests
from routers.books import get_db, get_current_user
from .utils import (
    app,
    override_get_db,
    override_get_current_user,
    client,
    test_book,
    TestingSessionLocal,
    Book,
    text,
)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_books_authenticated(test_book):

    response = client.get("/books/my-books")
    assert response.status_code == 200
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


def test_get_all_books_unauthenticated(test_book):

    app.dependency_overrides[get_current_user] = lambda: None

    response = client.get("/books/my-books")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}

    app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_books_user_with_not_books(test_book):
    def override_get_db_fake():
        db = TestingSessionLocal()
        db.execute(text("DELETE FROM books;"))

        book_owned_by_second_user = Book(
            title="test_title 2",
            author="test_author 2",
            summary="test_summary",
            category="test_category",
            owner_id=2,
        )

        db.add(book_owned_by_second_user)
        db.commit()

        response = client.get("/books/my-books")

        assert response.status_code == 200
        assert response.json() == []

        db.execute(text("DELETE FROM books;"))


def test_get_one_book_info_authenticated(test_book):

    response = client.get("/books/book-info/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "test_title",
        "author": "test_author",
        "summary": "test_summary",
        "category": "test_category",
        "owner_id": 1,
    }


def test_get_one_book_info_unauthenticated(test_book):

    app.dependency_overrides[get_current_user] = lambda: None

    response = client.get("/books/book-info/1")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}

    app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_one_book_info_not_found(test_book):

    response = client.get("/books/book-info/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found."}


def test_add_new_book(monkeypatch, test_book):

    class FakeResp:
        def __init__(self, payload):
            self.content = json.dumps(payload).encode()

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        return FakeResp(
            {"output": {"summary_by_ai": "ai summary", "category_by_ai": "ai category"}}
        )

    monkeypatch.setattr("routers.books.requests.post", fake_post)

    request_data = {"title": "The Compound Effect", "author": "Darren Hardy"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Book).filter(Book.id == 2).first()

    assert model.title == request_data.get("title")
    assert model.author == request_data.get("author")


def test_add_new_book_unauthenticated(monkeypatch, test_book):

    class FakeResp:
        def __init__(self, payload):
            self.content = json.dumps(payload).encode()

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        return FakeResp(
            {"output": {"summary_by_ai": "ai summary", "category_by_ai": "ai category"}}
        )

    monkeypatch.setattr("routers.books.requests.post", fake_post)

    app.dependency_overrides[get_current_user] = lambda: None

    request_data = {"title": "The Compound Effect", "author": "Darren Hardy"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}

    app.dependency_overrides[get_current_user] = override_get_current_user


def test_add_new_book_webhook_output(monkeypatch, test_book):

    class FakeResp:
        def __init__(self, payload):
            self.content = json.dumps(payload).encode()

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        return FakeResp(
            {"output": {"summary_by_ai": "ai summary", "category_by_ai": "ai category"}}
        )

    monkeypatch.setattr("routers.books.requests.post", fake_post)

    request_data = {"title": "The Compound Effect", "author": "Darren Hardy"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 201

    db = TestingSessionLocal()
    book_model = db.query(Book).filter(Book.id == 2).first()

    assert book_model.summary == "ai summary"
    assert book_model.category == "ai category"


def test_add_new_book_webhook_without_output_key(monkeypatch, test_book):

    class FakeResp:
        def __init__(self, payload):
            self.content = json.dumps(payload).encode()

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        return FakeResp(
            {"summary_by_ai": "test summary", "category_by_ai": "test category"}
        )

    monkeypatch.setattr("routers.books.requests.post", fake_post)

    request_data = {"title": "Deep Work", "author": "Cal Newport"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 201

    db = TestingSessionLocal()
    book_model = db.query(Book).filter(Book.id == 2).first()

    assert book_model.summary == "test summary"
    assert book_model.category == "test category"


def test_add_new_book_db_failure(monkeypatch, test_book):
    class FakeResp:
        def __init__(self, payload):
            self.content = json.dumps(payload).encode()

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        return FakeResp(
            {"output": {"summary_by_ai": "ai summary", "category_by_ai": "ai category"}}
        )

    monkeypatch.setattr("routers.books.requests.post", fake_post)

    class FakeDB:
        def add(self, obj):
            pass

        # Raise an error on commit method
        def commit(self):
            raise Exception("Simulated database error")

        def close(self):
            pass

    def override_fake_db():
        db = FakeDB()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setitem(app.dependency_overrides, get_db, override_fake_db)

    request_data = {"author": "Cal Newport", "title": "Deep Work"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 500
    assert response.json() == {"detail": "Database storage failed."}


def test_add_new_book_response_not_json(monkeypatch, test_book):

    class FakeResp:
        def __init__(self, payload):
            self.content = payload

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        return FakeResp("Not JSON")

    monkeypatch.setattr("routers.books.requests.post", fake_post)

    request_data = {"author": "Cal Newport", "title": "So Good They Can't Ignore You"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Invalid response received from webhook service (malformed JSON)"
    }


def test_add_new_book_webhook_failed_response(monkeypatch, test_book):

    def fake_post_raising_connection_error(url, json=None, timeout=None):
        raise requests.exceptions.ConnectionError(
            "Failed to connect to webhook serivce."
        )

    monkeypatch.setattr(
        "routers.books.requests.post", fake_post_raising_connection_error
    )

    request_data = {"title": "Deep Work", "author": "Cal Newport"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 503
    assert response.json() == {"detail": "Webhook service is unreachable or timedout."}

    def fake_post_raising_timeout_error(url, json=None, timeout=None):
        raise requests.exceptions.Timeout("Connection timed out.")

    monkeypatch.setattr("routers.books.requests.post", fake_post_raising_timeout_error)

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 503
    assert response.json() == {"detail": "Webhook service is unreachable or timedout."}


def test_add_book_failed_length_validation_request(test_book):

    request_data = {"title": "test book" * 250, "author": "test author"}

    response = client.post("/books/add-book", json=request_data)

    assert response.status_code == 422
    assert response.json().get("detail")[0].get("type") == "string_too_long"
    assert (
        response.json().get("detail")[0].get("msg")
        == "String should have at most 200 characters"
    )
