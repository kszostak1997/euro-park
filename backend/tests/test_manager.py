from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum, User

RESIDENT_EMAIL = "resident@example.com"
MANAGER_EMAIL = "manager@example.com"
PASSWORD = "supersecret123"


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post("/auth/register", json={"email": email, "password": PASSWORD})
    login = await client.post(
        "/auth/login", json={"email": email, "password": PASSWORD}
    )
    return login.json()["access_token"]


async def _promote_to_manager(db_session: AsyncSession, email: str) -> None:
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.role = RoleEnum.MANAGER
    db_session.add(user)
    await db_session.commit()


async def _create_application(
    client: AsyncClient, token: str, registration_number: str = "WA12345"
) -> dict:
    response = await client.post(
        "/applications",
        json={"registration_number": registration_number, "floor": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()


async def _manager_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    token = await _register_and_login(client, MANAGER_EMAIL)
    await _promote_to_manager(db_session, MANAGER_EMAIL)
    return {"Authorization": f"Bearer {token}"}


async def test_list_users_requires_manager_role(client: AsyncClient) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)

    response = await client.get(
        "/manager/users",
        headers={"Authorization": f"Bearer {resident_token}"},
    )

    assert response.status_code == 403


async def test_manager_can_list_users(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register_and_login(client, RESIDENT_EMAIL)

    headers = await _manager_headers(client, db_session)
    response = await client.get("/manager/users", headers=headers)

    assert response.status_code == 200
    emails = {user["email"] for user in response.json()}
    assert RESIDENT_EMAIL in emails
    assert MANAGER_EMAIL in emails


async def test_list_requires_manager_role(client: AsyncClient) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)

    response = await client.get(
        "/manager/applications",
        headers={"Authorization": f"Bearer {resident_token}"},
    )

    assert response.status_code == 403


async def test_manager_can_list_all_applications(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    await _create_application(client, resident_token, "WA11111")
    await _create_application(client, resident_token, "WA22222")

    headers = await _manager_headers(client, db_session)
    response = await client.get("/manager/applications", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_manager_can_filter_by_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    approved = await _create_application(client, resident_token, "WA11111")
    await _create_application(client, resident_token, "WA22222")

    headers = await _manager_headers(client, db_session)
    await client.post(
        f"/manager/applications/{approved['id']}/approve", headers=headers
    )

    response = await client.get(
        "/manager/applications", params={"status": "APPROVED"}, headers=headers
    )

    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == approved["id"]


async def test_manager_can_paginate(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    for i in range(3):
        await _create_application(client, resident_token, f"WA1000{i}")

    headers = await _manager_headers(client, db_session)
    response = await client.get(
        "/manager/applications", params={"page": 1, "size": 2}, headers=headers
    )

    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2


async def test_manager_approve_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/approve", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


async def test_manager_reject_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/reject", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"


async def test_manager_cannot_review_already_decided_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    await client.post(
        f"/manager/applications/{application['id']}/approve", headers=headers
    )

    response = await client.post(
        f"/manager/applications/{application['id']}/reject", headers=headers
    )

    assert response.status_code == 409


async def test_manager_request_changes_requires_comment(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/request-changes",
        json={"comment": ""},
        headers=headers,
    )

    assert response.status_code == 422


async def test_manager_request_changes_lets_resident_edit_again(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/request-changes",
        json={"comment": "Proszę podać poprawne piętro"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "NEEDS_CHANGES"
    assert response.json()["comment"] == "Proszę podać poprawne piętro"

    resident_headers = {"Authorization": f"Bearer {resident_token}"}
    edit_response = await client.patch(
        f"/applications/{application['id']}",
        json={"floor": 3},
        headers=resident_headers,
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["floor"] == 3
