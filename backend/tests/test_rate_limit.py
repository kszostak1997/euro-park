from httpx import AsyncClient

from app.core.rate_limit import limiter


async def test_login_is_rate_limited_after_threshold(client: AsyncClient) -> None:
    email = "ratelimited@example.com"
    password = "supersecret123"
    await client.post("/auth/register", json={"email": email, "password": password})

    limiter.enabled = True
    limiter.reset()
    try:
        responses = [
            await client.post(
                "/auth/login", json={"email": email, "password": password}
            )
            for _ in range(11)
        ]
        assert any(r.status_code == 429 for r in responses)
    finally:
        limiter.reset()
        limiter.enabled = False
