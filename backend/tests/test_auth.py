from httpx import AsyncClient

EMAIL = "resident@example.com"
PASSWORD = "supersecret123"


async def _register(client: AsyncClient, email: str = EMAIL, password: str = PASSWORD):
    return await client.post(
        "/auth/register", json={"email": email, "password": password}
    )


async def _login(client: AsyncClient, email: str = EMAIL, password: str = PASSWORD):
    return await client.post("/auth/login", json={"email": email, "password": password})


async def test_register_success(client: AsyncClient) -> None:
    response = await _register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == EMAIL
    assert body["role"] == "USER"
    assert "hashed_password" not in body
    assert "password" not in body


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await _register(client)
    response = await _register(client)

    assert response.status_code == 409


async def test_login_success(client: AsyncClient) -> None:
    await _register(client)
    response = await _login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient) -> None:
    await _register(client)
    response = await _login(client, password="wrong-password")

    assert response.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await _login(client, email="nobody@example.com")

    assert response.status_code == 401


async def test_protected_route_requires_token(client: AsyncClient) -> None:
    response = await client.get("/auth/me")

    assert response.status_code == 401


async def test_protected_route_with_valid_token(client: AsyncClient) -> None:
    await _register(client)
    login_response = await _login(client)
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


async def test_refresh_rotates_token(client: AsyncClient) -> None:
    await _register(client)
    login_response = await _login(client)
    original_refresh_token = login_response.json()["refresh_token"]

    refresh_response = await client.post(
        "/auth/refresh", json={"refresh_token": original_refresh_token}
    )
    assert refresh_response.status_code == 200
    new_refresh_token = refresh_response.json()["refresh_token"]
    assert new_refresh_token != original_refresh_token

    reuse_response = await client.post(
        "/auth/refresh", json={"refresh_token": original_refresh_token}
    )
    assert reuse_response.status_code == 401
