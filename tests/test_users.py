from .utils import (
    app,
    override_get_db,
    override_get_current_user,
    client,
    test_user,
    TestingSessionLocal,
    User,
)
from routers.users import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user(test_user):

    response = client.get("/users/")
    assert response.status_code == 200

    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert model.username == "testuser"
    assert model.role == "admin"


def test_delete_user(test_user):

    db = TestingSessionLocal()

    existing_user_model = db.query(User).filter(User.id == 1).first()
    assert existing_user_model is not None
    response = client.delete("/users/delete-user")

    assert response.status_code == 204

    deleted_user_mode = db.query(User).filter(User.id == 1).first()
    assert deleted_user_mode is None
