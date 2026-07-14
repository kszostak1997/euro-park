# Euro Park — system wniosków parkingowych

Aplikacja webowa dla wspólnoty mieszkaniowej "Euro Park" do składania i obsługi wniosków o przydział miejsca parkingowego, z weryfikacją dostępu szlabanu na podstawie numeru rejestracyjnego.

- **Backend:** FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL/SQLite — [backend/README.md](backend/README.md)
- **Frontend:** Nuxt 4 + Vue 3 (Composition API) + TypeScript — [frontend/README.md](frontend/README.md)

## Szybki start (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger / OpenAPI docs: http://localhost:8000/docs
- Baza danych: PostgreSQL, uruchamiana automatycznie jako kontener `db`; migracje Alembic są stosowane automatycznie przy starcie kontenera `backend`.

Domyślne wartości `JWT_SECRET`, adresy API (`NUXT_API_BASE`/`NUXT_PUBLIC_API_BASE`) i dane bazy danych są ustawione w `docker-compose.yml` do celów developerskich/rekrutacyjnych. Przed jakimkolwiek wdrożeniem produkcyjnym **należy wygenerować i podstawić własny `JWT_SECRET`** (np. `python -c "import secrets; print(secrets.token_urlsafe(48))"`).

## Konta testowe (seedowane automatycznie przy starcie backendu)

| Rola | Email | Hasło |
|---|---|---|
| Administrator | `admin@admin.com` | `admin` |
| Zarządca | `manager@manager.com` | `manager` |
| Użytkownik | `test@test.com` | `test` |

Seedowanie jest idempotentne (`backend/app/core/seed.py`) — konta są tworzone tylko przy pierwszym uruchomieniu, kolejne starty ich nie duplikują.

## Struktura repozytorium

```
euro-park/
├── backend/    # FastAPI REST API — patrz backend/README.md
├── frontend/   # Nuxt 4 SPA/SSR — patrz frontend/README.md
└── docker-compose.yml
```

## Przykładowy flow

1. Użytkownik rejestruje konto i loguje się.
2. Składa wniosek o miejsce parkingowe (numer rejestracyjny + preferowane piętro).
3. Wniosek trafia do kolejki oczekujących (`PENDING`).
4. Zarządca (`manager@manager.com`) akceptuje, odrzuca lub odsyła wniosek do poprawy z komentarzem.
5. Użytkownik widzi status wniosku i — jeśli wymaga poprawy — może go edytować.
6. Szlaban odpytuje `POST /barrier/check-access` o dostęp na podstawie numeru rejestracyjnego; dostęp jest przyznawany wyłącznie dla zaakceptowanych wniosków.

Więcej szczegółów technicznych (endpointy, zmienne środowiskowe, testy, lintery) znajduje się w README każdego z podprojektów.
