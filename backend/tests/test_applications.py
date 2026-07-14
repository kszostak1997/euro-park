from httpx import AsyncClient

from tests.conftest import auth_headers as _auth_headers_default
from tests.conftest import create_application as _create_application

APPLICANT_EMAIL = "resident@example.com"
OTHER_EMAIL = "neighbor@example.com"


async def _auth_headers(client: AsyncClient, email: str = APPLICANT_EMAIL) -> dict:
    return await _auth_headers_default(client, email)


async def test_create_application_success(client: AsyncClient) -> None:
    headers = await _auth_headers(client)

    response = await client.post(
        "/applications",
        json={
            "registration_number": "wa 123-45",
            "floor": 1,
            "applicant_comment": "proszę o miejsce",
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["registration_number"] == "WA12345"
    assert body["floor"] == 1
    assert body["status"] == "PENDING"
    assert body["applicant_comment"] == "proszę o miejsce"
    assert body["manager_comment"] is None
    assert body["user_email"] == APPLICANT_EMAIL


async def test_create_application_rejects_floor_out_of_range(
    client: AsyncClient,
) -> None:
    headers = await _auth_headers(client)

    response = await client.post(
        "/applications",
        json={"registration_number": "WA12345", "floor": 99},
        headers=headers,
    )

    assert response.status_code == 422


async def test_create_application_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/applications", json={"registration_number": "WA12345", "floor": 1}
    )

    assert response.status_code == 401


async def test_create_application_invalid_registration_number(
    client: AsyncClient,
) -> None:
    headers = await _auth_headers(client)

    response = await client.post(
        "/applications",
        json={"registration_number": "!!!", "floor": 1},
        headers=headers,
    )

    assert response.status_code == 422


async def test_list_applications_returns_only_own(client: AsyncClient) -> None:
    headers_a = await _auth_headers(client, APPLICANT_EMAIL)
    await _create_application(client, headers_a, "WA11111")

    headers_b = await _auth_headers(client, OTHER_EMAIL)
    await _create_application(client, headers_b, "WA22222")

    response = await client.get("/applications", headers=headers_a)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["registration_number"] == "WA11111"


async def test_get_application_not_found_for_other_user(client: AsyncClient) -> None:
    headers_a = await _auth_headers(client, APPLICANT_EMAIL)
    created = await _create_application(client, headers_a)

    headers_b = await _auth_headers(client, OTHER_EMAIL)
    response = await client.get(f"/applications/{created['id']}", headers=headers_b)

    assert response.status_code == 404


async def test_update_application_while_pending_succeeds(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    created = await _create_application(client, headers)

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"floor": 0},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["floor"] == 0


async def test_update_application_forbidden_when_approved(
    client: AsyncClient, db_session
) -> None:
    from app.models.application import Application, ApplicationStatus

    headers = await _auth_headers(client)
    created = await _create_application(client, headers)

    application = await db_session.get(Application, created["id"])
    application.status = ApplicationStatus.APPROVED
    db_session.add(application)
    await db_session.commit()

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"floor": 0},
        headers=headers,
    )

    assert response.status_code == 409


async def test_update_application_not_owned_returns_404(client: AsyncClient) -> None:
    headers_a = await _auth_headers(client, APPLICANT_EMAIL)
    created = await _create_application(client, headers_a)

    headers_b = await _auth_headers(client, OTHER_EMAIL)
    response = await client.patch(
        f"/applications/{created['id']}",
        json={"floor": 0},
        headers=headers_b,
    )

    assert response.status_code == 404


async def test_update_application_empty_patch_does_not_change_status(
    client: AsyncClient, db_session
) -> None:
    from app.models.application import Application, ApplicationStatus

    headers = await _auth_headers(client)
    created = await _create_application(client, headers)

    application = await db_session.get(Application, created["id"])
    application.status = ApplicationStatus.NEEDS_CHANGES
    application.manager_comment = "Popraw numer rejestracyjny"
    db_session.add(application)
    await db_session.commit()

    response = await client.patch(
        f"/applications/{created['id']}",
        json={},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NEEDS_CHANGES"
    assert body["manager_comment"] == "Popraw numer rejestracyjny"


async def test_update_application_does_not_overwrite_manager_comment(
    client: AsyncClient, db_session
) -> None:
    from app.models.application import Application, ApplicationStatus

    headers = await _auth_headers(client)
    created = await _create_application(client, headers)

    application = await db_session.get(Application, created["id"])
    application.status = ApplicationStatus.NEEDS_CHANGES
    application.manager_comment = "Popraw numer rejestracyjny"
    db_session.add(application)
    await db_session.commit()

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"registration_number": "WA99999", "applicant_comment": "poprawiłem"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["applicant_comment"] == "poprawiłem"
    assert body["manager_comment"] == "Popraw numer rejestracyjny"
