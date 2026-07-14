from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum, User
from tests.conftest import promote_to_manager as _promote_to_manager
from tests.conftest import register_and_login as _register_and_login

RESIDENT_EMAIL = "resident@example.com"
MANAGER_EMAIL = "manager@example.com"
PASSWORD = "supersecret123"


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


async def _promote_to_admin(db_session: AsyncSession, email: str) -> None:
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.role = RoleEnum.ADMIN
    db_session.add(user)
    await db_session.commit()


async def _admin_headers(
    client: AsyncClient, db_session: AsyncSession, email: str
) -> dict:
    token = await _register_and_login(client, email)
    await _promote_to_admin(db_session, email)
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
    emails = {user["email"] for user in response.json()["items"]}
    assert RESIDENT_EMAIL in emails
    assert MANAGER_EMAIL in emails


async def test_manager_can_paginate_users(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    for i in range(3):
        await _register_and_login(client, f"resident{i}@example.com")

    headers = await _manager_headers(client, db_session)
    response = await client.get(
        "/manager/users", params={"page": 1, "size": 2}, headers=headers
    )

    body = response.json()
    assert body["total"] >= 4  # 3 residents + the manager account itself
    assert len(body["items"]) == 2


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


async def test_manager_request_changes_rejects_whitespace_only_comment(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/request-changes",
        json={"comment": "   "},
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
    assert response.json()["manager_comment"] == "Proszę podać poprawne piętro"

    resident_headers = {"Authorization": f"Bearer {resident_token}"}
    edit_response = await client.patch(
        f"/applications/{application['id']}",
        json={"floor": 0},
        headers=resident_headers,
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["floor"] == 0


async def test_manager_can_revoke_approved_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    await client.post(
        f"/manager/applications/{application['id']}/approve", headers=headers
    )

    response = await client.post(
        f"/manager/applications/{application['id']}/revoke", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


async def test_manager_cannot_revoke_non_approved_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/revoke", headers=headers
    )

    assert response.status_code == 409


async def test_manager_applications_list_includes_user_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    await _create_application(client, resident_token)

    headers = await _manager_headers(client, db_session)
    response = await client.get("/manager/applications", headers=headers)

    assert response.status_code == 200
    assert response.json()["items"][0]["user_email"] == RESIDENT_EMAIL


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
    await _register_and_login(client, RESIDENT_EMAIL)
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
    await _register_and_login(client, RESIDENT_EMAIL)
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
    await _register_and_login(client, RESIDENT_EMAIL)
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
    await _register_and_login(client, RESIDENT_EMAIL)
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
