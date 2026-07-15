# Euro Park: system wniosków parkingowych

Aplikacja webowa dla wspólnoty mieszkaniowej "Euro Park" do składania i obsługi wniosków o przydział miejsca parkingowego, z weryfikacją dostępu szlabanu na podstawie numeru rejestracyjnego.

## Setup (Docker)

```bash
cp .env.example .env   # wygeneruj sekret: python3 -c "import secrets; print(secrets.token_urlsafe(48))"
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
4. Zarządca (`manager@manager.com` albo `admin@admin.com`) akceptuje, odrzuca lub odsyła wniosek do poprawy z komentarzem — w panelu zarządcy dostępne są też zakładki "Użytkownicy" (zarządzanie kontami) oraz "Brama (test)" (testowe sprawdzenie dostępu po numerze rejestracyjnym). Zatwierdzony wniosek można też cofnąć z powrotem do statusu oczekującego.
5. Użytkownik widzi status wniosku i, jeśli wymaga poprawy, może go edytować.
6. Szlaban odpytuje `POST /barrier/check-access` o dostęp na podstawie numeru rejestracyjnego; dostęp jest przyznawany wyłącznie dla zaakceptowanych wniosków.


## Lint / formatowanie

## Frontend
```bash
npm run lint
npm run format
```

## Backend

```bash
ruff check .
black --check .
```

## Testy

```bash
pytest
```

## Przegląd API

| Metoda | Ścieżka | Autoryzacja | Opis |
|---|---|---|---|
| POST | `/auth/register` | brak | Utworzenie konta `USER` |
| POST | `/auth/login` | brak | Pobranie pary access + refresh token |
| POST | `/auth/refresh` | brak | Rotacja refresh tokenu na nową parę |
| GET | `/auth/current-user` | Bearer | Profil aktualnie zalogowanego użytkownika |
| POST | `/applications` | Bearer | Złożenie wniosku o miejsce parkingowe |
| GET | `/applications` | Bearer | Lista własnych wniosków |
| GET | `/applications/{id}` | Bearer | Pobranie własnego wniosku |
| PATCH | `/applications/{id}` | Bearer | Edycja własnego wniosku (tylko w statusie `PENDING`/`NEEDS_CHANGES`) |
| POST | `/barrier/check-access` | brak | Szlaban: sprawdzenie, czy numer rejestracyjny ma zaakceptowany wniosek |
| GET | `/manager/applications` | Zarządca/Admin | Lista wszystkich wniosków (paginacja, filtrowanie po statusie, sortowanie) |
| POST | `/manager/applications/{id}/approve` | Zarządca/Admin | Zatwierdzenie wniosku |
| POST | `/manager/applications/{id}/reject` | Zarządca/Admin | Odrzucenie wniosku |
| POST | `/manager/applications/{id}/request-changes` | Zarządca/Admin | Odesłanie do poprawy (komentarz wymagany) |
| POST | `/manager/applications/{id}/revoke` | Zarządca/Admin | Cofnięcie zatwierdzonego wniosku (`APPROVED`) z powrotem do `PENDING` |
| GET | `/manager/users` | Zarządca/Admin | Lista użytkowników (paginacja) |
| POST | `/manager/users` | Admin | Utworzenie użytkownika z podaną rolą |
| PATCH | `/manager/users/{id}/role` | Admin | Zmiana roli użytkownika |
| DELETE | `/manager/users/{id}` | Admin | Usunięcie użytkownika |

Pełne schematy request/response dostępne w Swagger UI (`/docs`).
