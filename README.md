# Euro Park: system wniosków parkingowych

Aplikacja webowa dla wspólnoty mieszkaniowej "Euro Park" do składania i obsługi wniosków o przydział miejsca parkingowego, z weryfikacją dostępu szlabanu na podstawie numeru rejestracyjnego.

## Setup (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger / OpenAPI docs: http://localhost:8000/docs


## Konta testowe (seedowane automatycznie przy starcie backendu)

| Rola | Email | Hasło |
|---|---|---|
| Administrator | `admin@admin.com` | `admin` |
| Zarządca | `manager@manager.com` | `manager` |
| Użytkownik | `test@test.com` | `test` |

## Przykładowy flow

1. Użytkownik rejestruje konto i loguje się.
2. Składa wniosek o miejsce parkingowe (numer rejestracyjny + preferowane piętro).
3. Wniosek trafia do kolejki oczekujących (`PENDING`).
4. Zarządca (`manager@manager.com` albo `admin@admin.com`) akceptuje, odrzuca lub odsyła wniosek do poprawy z komentarzem.
5. Użytkownik widzi status wniosku i, jeśli wymaga poprawy, może go edytować.
6. Szlaban odpytuje `POST /barrier/check-access` o dostęp na podstawie numeru rejestracyjnego; dostęp jest przyznawany wyłącznie dla zaakceptowanych wniosków.

