import pytest
from jose import jwt
from datetime import timedelta
from .utils import (
    app,
    override_get_db,
    override_get_current_user,
    client,
    test_user,
    TestingSessionLocal,
    bcrypt_context,
    User
)
from routers.auth import (
    get_db,
    get_current_user,
    create_access_token,
    JWT_SECRET_KEY,
    JWT_HASH_ALGORITHM,
    bcrypt_context,
    authenticate_user,
    HTTPException
)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    is_authenicated_user = authenticate_user('testuser', 'test1234!', db)

    assert is_authenicated_user.username == 'testuser'
    assert is_authenicated_user.id == 1
    assert is_authenicated_user.email == 'testuser@email.com'
    assert is_authenicated_user.role == 'admin'
    assert bcrypt_context.verify('test1234!', is_authenicated_user.hashed_password)

    not_authenicated_user = authenticate_user('testuser', 'wrongpassword', db)

    assert not_authenicated_user is False


def test_create_access_token(test_user):
    username = "testuser"
    user_id = 1
    user_role = "admin"
    expires_delta = timedelta(days=1)
    token = create_access_token(
        username=username,
        user_id=user_id,
        user_role=user_role,
        expires_delta=expires_delta,
    )
    decoded_token = jwt.decode(
        token,
        key=JWT_SECRET_KEY,
        algorithms=[JWT_HASH_ALGORITHM],
        options={"verify_signature": False},
    )

    assert decoded_token.get("sub") == username
    assert decoded_token.get("id") == user_id
    assert decoded_token.get("role") == user_role


@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_user):

    encode = {"sub": "testuser", "id": 1, "role": "admin"}

    # Here we use jwt (instead of create_token function)
    token = jwt.encode(encode, key=JWT_SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

    db = TestingSessionLocal()

    current_user = await get_current_user(token=token)

    assert current_user.get("user_role") == "admin"

    user_model = db.query(User).filter(User.id == 1).first()

    assert user_model.username == current_user.get("username")
    assert user_model.id == current_user.get("id")
    assert user_model.role == current_user.get("user_role")


@pytest.mark.asyncio
async def test_get_current_user_missing_payload(test_user):

    encode = {"role": "user"}
    token = jwt.encode(encode, key=JWT_SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

    db = TestingSessionLocal()

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'User does not exist anymore'

    

def test_add_new_user(test_user):
    create_user_request = {
        "username": "testuser2",
        "email": "testuser2@email.com",
        "password": "test1234!!",
        "role": "regular_user",
    }

    response = client.post("/auth/register", json=create_user_request)

    assert response.status_code == 201

    db = TestingSessionLocal()
    user_model_2 = db.query(User).filter(User.id == 2).first()

    assert user_model_2.username == create_user_request.get("username")
    assert user_model_2.email == create_user_request.get("email")
    assert user_model_2.role == create_user_request.get("role")
    assert bcrypt_context.verify(
        create_user_request.get("password"), user_model_2.hashed_password
    )


def test_login_for_access_token_authenticated(test_user):
    login_request = {
        "username": "testuser",
        "password": "test1234!",
    }

    response = client.post("/auth/token", data=login_request)

    assert response.status_code == 200

    token = response.json().get("access_token")
    decode = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])

    assert decode.get("sub") == "testuser"
    assert decode.get("role") == "admin"
    assert decode.get("id") == 1


def test_login_for_access_token_authenticated_failed(test_user):
    login_request_wrong_password = {
        "username": "testuser",
        "password": "wrong_password",
    }

    response = client.post("/auth/token", data=login_request_wrong_password)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}

    login_request_wrong_username = {
        "username": "usernotexisting",
        "password": "test1234!",
    }

    response = client.post("/auth/token", data=login_request_wrong_username)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed."}
