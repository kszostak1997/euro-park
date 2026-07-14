from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum
from tests.conftest import auth_headers as _auth_headers
from tests.conftest import promote as _promote

RESIDENT_EMAIL = "resident@example.com"
MANAGER_EMAIL = "manager@example.com"
PASSWORD = "supersecret123"


async def _manager_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    headers = await _auth_headers(client, MANAGER_EMAIL)
    await _promote(db_session, MANAGER_EMAIL, RoleEnum.MANAGER)
    return headers


async def _admin_headers(
    client: AsyncClient, db_session: AsyncSession, email: str
) -> dict:
    headers = await _auth_headers(client, email)
    await _promote(db_session, email, RoleEnum.ADMIN)
    return headers


async def test_list_users_requires_manager_role(client: AsyncClient) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)

    response = await client.get("/manager/users", headers=resident_headers)

    assert response.status_code == 403


async def test_manager_can_list_users(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _auth_headers(client, RESIDENT_EMAIL)

    headers = await _manager_headers(client, db_session)
    response = await client.get("/manager/users", headers=headers)

    assert response.status_code == 200
    emails = {user["email"] for user in response.json()["items"]}
    assert RESIDENT_EMAIL in emails
    assert MANAGER_EMAIL in emails


async def test_manager_can_paginate_users(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    for i in range(3):
        await _auth_headers(client, f"resident{i}@example.com")

    headers = await _manager_headers(client, db_session)
    response = await client.get(
        "/manager/users", params={"page": 1, "size": 2}, headers=headers
    )

    body = response.json()
    assert body["total"] >= 4
    assert len(body["items"]) == 2


async def test_manager_cannot_create_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    headers = await _manager_headers(client, db_session)
    response = await client.post(
        "/manager/users",
        json={"email": "new@example.com", "password": PASSWORD},
        headers=headers,
    )

    assert response.status_code == 403


async def test_admin_can_create_user_with_role(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    headers = await _admin_headers(client, db_session, "admin1@example.com")

    response = await client.post(
        "/manager/users",
        json={"email": "created@example.com", "password": PASSWORD, "role": "MANAGER"},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "created@example.com"
    assert body["role"] == "MANAGER"


async def test_admin_cannot_create_user_with_duplicate_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _auth_headers(client, RESIDENT_EMAIL)
    headers = await _admin_headers(client, db_session, "admin2@example.com")

    response = await client.post(
        "/manager/users",
        json={"email": RESIDENT_EMAIL, "password": PASSWORD},
        headers=headers,
    )

    assert response.status_code == 409


async def test_admin_can_change_user_role(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _auth_headers(client, RESIDENT_EMAIL)
    headers = await _admin_headers(client, db_session, "admin3@example.com")

    users = await client.get("/manager/users", headers=headers)
    resident_id = next(
        u["id"] for u in users.json()["items"] if u["email"] == RESIDENT_EMAIL
    )

    response = await client.patch(
        f"/manager/users/{resident_id}/role",
        json={"role": "MANAGER"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["role"] == "MANAGER"


async def test_admin_cannot_change_own_role(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    headers = await _admin_headers(client, db_session, "admin4@example.com")
    users = await client.get("/manager/users", headers=headers)
    admin_id = next(
        u["id"] for u in users.json()["items"] if u["email"] == "admin4@example.com"
    )

    response = await client.patch(
        f"/manager/users/{admin_id}/role",
        json={"role": "USER"},
        headers=headers,
    )

    assert response.status_code == 409


async def test_admin_change_role_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    headers = await _admin_headers(client, db_session, "admin5@example.com")

    response = await client.patch(
        "/manager/users/999999/role",
        json={"role": "MANAGER"},
        headers=headers,
    )

    assert response.status_code == 404


async def test_manager_cannot_delete_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _auth_headers(client, RESIDENT_EMAIL)
    headers = await _manager_headers(client, db_session)
    users = await client.get("/manager/users", headers=headers)
    resident_id = next(
        u["id"] for u in users.json()["items"] if u["email"] == RESIDENT_EMAIL
    )

    response = await client.delete(f"/manager/users/{resident_id}", headers=headers)

    assert response.status_code == 403


async def test_admin_can_delete_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _auth_headers(client, RESIDENT_EMAIL)
    headers = await _admin_headers(client, db_session, "admin6@example.com")
    users = await client.get("/manager/users", headers=headers)
    resident_id = next(
        u["id"] for u in users.json()["items"] if u["email"] == RESIDENT_EMAIL
    )

    response = await client.delete(f"/manager/users/{resident_id}", headers=headers)
    assert response.status_code == 204

    users_after = await client.get("/manager/users", headers=headers)
    emails = {u["email"] for u in users_after.json()["items"]}
    assert RESIDENT_EMAIL not in emails


async def test_admin_cannot_delete_own_account(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    headers = await _admin_headers(client, db_session, "admin7@example.com")
    users = await client.get("/manager/users", headers=headers)
    admin_id = next(
        u["id"] for u in users.json()["items"] if u["email"] == "admin7@example.com"
    )

    response = await client.delete(f"/manager/users/{admin_id}", headers=headers)

    assert response.status_code == 409
