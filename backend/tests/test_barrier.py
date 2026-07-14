from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum
from tests.conftest import auth_headers as _auth_headers
from tests.conftest import create_application as _create_application
from tests.conftest import promote as _promote

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
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    await _create_application(client, resident_headers, "WA12345")

    response = await client.post(
        "/barrier/check-access", json={"registration_number": "WA12345"}
    )

    assert response.json()["access_granted"] is False


async def test_barrier_grants_approved_application(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    resident_headers = await _auth_headers(client, RESIDENT_EMAIL)
    created = await _create_application(client, resident_headers, "WA12345")

    manager_headers = await _auth_headers(client, MANAGER_EMAIL)
    await _promote(db_session, MANAGER_EMAIL, RoleEnum.MANAGER)
    await client.post(
        f"/manager/applications/{created['id']}/approve", headers=manager_headers
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
