from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import promote_to_manager as _promote_to_manager
from tests.conftest import register_and_login as _register_and_login

RESIDENT_EMAIL = "resident@example.com"
MANAGER_EMAIL = "manager@example.com"


async def test_barrier_denies_unknown_plate(client: AsyncClient) -> None:
    response = await client.post(
        "/barrier/check-access", json={"registration_number": "WA99999"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "registration_number": "WA99999",
        "access_granted": False,
    }


async def test_barrier_denies_pending_application(client: AsyncClient) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    await client.post(
        "/applications",
        json={"registration_number": "WA12345", "floor": 1},
        headers={"Authorization": f"Bearer {resident_token}"},
    )

    response = await client.post(
        "/barrier/check-access", json={"registration_number": "WA12345"}
    )

    assert response.json()["access_granted"] is False


async def test_barrier_grants_approved_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_token = await _register_and_login(client, RESIDENT_EMAIL)
    created = await client.post(
        "/applications",
        json={"registration_number": "WA12345", "floor": 1},
        headers={"Authorization": f"Bearer {resident_token}"},
    )
    application_id = created.json()["id"]

    manager_token = await _register_and_login(client, MANAGER_EMAIL)
    await _promote_to_manager(db_session, MANAGER_EMAIL)
    await client.post(
        f"/manager/applications/{application_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    response = await client.post(
        "/barrier/check-access", json={"registration_number": "wa 123-45"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "registration_number": "WA12345",
        "access_granted": True,
    }


async def test_barrier_rejects_invalid_registration_number(client: AsyncClient) -> None:
    response = await client.post(
        "/barrier/check-access", json={"registration_number": "!!"}
    )

    assert response.status_code == 422
