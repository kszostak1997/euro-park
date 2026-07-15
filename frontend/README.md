# Euro Park: frontend

Frontend dla systemu zarządzania wnioskami o miejsce parkingowe.

## Struktura projektu

```
app/
├── composables/
├── middleware/
├── pages/
├── components/
├── layouts/
├── types/
└── utils/
```

## Uruchomienie lokalne

Wymaga osobno uruchomionego backendu (patrz [backend/README.md](../backend/README.md)).

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Lint / formatowanie

```bash
npm run lint
npm run format
```
