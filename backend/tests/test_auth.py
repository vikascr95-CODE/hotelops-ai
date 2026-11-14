
def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newstaff@hotel.com",
            "password": "StrongPassword123!"
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "receptionist"
    assert "hashed_password" not in response.json()


def test_duplicate_registration(client):
    payload = {
        "email": "duplicate@hotel.com",
        "password": "StrongPassword123!"
    }

    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@hotel.com",
            "password": "StrongPassword123!"
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@hotel.com",
            "password": "StrongPassword123!"
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "wrong@hotel.com",
            "password": "StrongPassword123!"
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "wrong@hotel.com",
            "password": "IncorrectPassword123!"
        },
    )

    assert response.status_code == 401


def test_profile_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_authenticated_profile(client):
    client.post(
        "/auth/register",
        json={
            "email": "profile@hotel.com",
            "password": "StrongPassword123!"
        },
    )

    login = client.post(
        "/auth/login",
        data={
            "username": "profile@hotel.com",
            "password": "StrongPassword123!"
        },
    )

    token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "profile@hotel.com"
    assert response.json()["role"] == "receptionist"
