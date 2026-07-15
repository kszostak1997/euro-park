# Euro Park: backend

Backend systemu zarządzania wnioskami o miejsce parkingowe.

## Struktura projektu

```
app/
├── controllers/
├── services/
├── repositories/
├── models/
├── schemas/
├── middleware/
├── core/
└── main.py
tests/
alembic/
```

## Uruchomienie lokalne

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
fastapi dev app/main.py
```

## Testy

```bash
pytest
```

## Lint / formatowanie

```bash
ruff check .
black --check .
```

## API

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
