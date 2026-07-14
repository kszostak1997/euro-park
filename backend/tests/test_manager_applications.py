from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum
from tests.conftest import auth_headers as _auth_headers
from tests.conftest import create_application as _create_application
from tests.conftest import promote as _promote

RESIDENT_EMAIL = "resident@example.com"
MANAGER_EMAIL = "manager@example.com"


async def _manager_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    headers = await _auth_headers(client, MANAGER_EMAIL)
    await _promote(db_session, MANAGER_EMAIL, RoleEnum.MANAGER)
    return headers


async def test_list_requires_manager_role(client: AsyncClient) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)

    response = await client.get("/manager/applications", headers=resident_headers)

    assert response.status_code == 403


async def test_manager_can_list_all_applications(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    await _create_application(client, resident_headers, "WA11111")
    await _create_application(client, resident_headers, "WA22222")

    headers = await _manager_headers(client, db_session)
    response = await client.get("/manager/applications", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_manager_can_filter_by_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    approved = await _create_application(client, resident_headers, "WA11111")
    await _create_application(client, resident_headers, "WA22222")

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    for i in range(3):
        await _create_application(client, resident_headers, f"WA1000{i}")

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/approve", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


async def test_manager_reject_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/reject", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"


async def test_manager_cannot_review_already_decided_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/request-changes",
        json={"comment": "Proszę podać poprawne piętro"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "NEEDS_CHANGES"
    assert response.json()["manager_comment"] == "Proszę podać poprawne piętro"

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    application = await _create_application(client, resident_headers)

    headers = await _manager_headers(client, db_session)
    response = await client.post(
        f"/manager/applications/{application['id']}/revoke", headers=headers
    )

    assert response.status_code == 409


async def test_manager_applications_list_includes_user_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    await _create_application(client, resident_headers)

    headers = await _manager_headers(client, db_session)
    response = await client.get("/manager/applications", headers=headers)

    assert response.status_code == 200
    assert response.json()["items"][0]["user_email"] == RESIDENT_EMAIL
