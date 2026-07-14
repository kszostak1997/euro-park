# Euro Park: frontend

Nuxt 4 / Vue 3 (Composition API, TypeScript) client for the parking-application management system.

## Stack

- Nuxt 4, Vue 3 Composition API, TypeScript
- `useFetch`/`$fetch` via a typed API client composable (cookie-based JWT storage, automatic refresh-on-401)
- ESLint + Prettier

## Project structure

```
app/
├── composables/   # useAuth, useApplications, useApiClient, useToast, useModalForm
├── middleware/    # auth.ts (require login), guest.ts (redirect logged-in users), manager.ts (role gate)
├── pages/         # login.vue, register.vue, user.vue (resident dashboard), manager.vue + manager/applications.vue + manager/users.vue (manager/admin dashboard)
├── components/    # shared UI (FormInput, FormSelect, AppModal, AppPagination, StatusBadge, ...)
├── layouts/       # default app shell + auth layout
├── types/         # shared TS types (ApplicationRow, AuthUser, ...)
└── utils/         # small helpers (date formatting, validation)
```

## Running locally (without Docker)

Requires the backend running separately (see [backend/README.md](../backend/README.md)), by default at `http://localhost:8000`.

```bash
cd frontend
cp .env.example .env   # adjust NUXT_API_BASE / NUXT_PUBLIC_API_BASE if the backend isn't on localhost:8000
npm install
npm run dev
```

App available at http://localhost:3000.

## Running with Docker

See the [root README](../README.md). `docker compose up --build`.

## Environment variables

| Variable | Default (`nuxt.config.ts`) | Notes |
|---|---|---|
| `NUXT_API_BASE` | `http://backend:8000` | Server-side (SSR) base URL used inside the docker network. When running `npm run dev` outside Docker, override this to `http://localhost:8000` (see `.env.example`); otherwise SSR requests (e.g. route middleware) will fail to resolve the `backend` hostname. |
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | Client-side (browser) base URL. |

## Lint / format

```bash
npm run lint
npm run format
```

## Auth model

JWT access/refresh tokens are stored in cookies (`useApiClient.ts`) and attached as `Authorization: Bearer` headers on every API call. A 401 triggers an automatic single refresh-and-retry; if the refresh itself fails, the user is logged out client-side.

Note: these cookies are not `httpOnly`/`secure`, since the client reads them to build the `Authorization` header itself rather than relying on the browser to send them automatically. This is a reasonable trade-off for this project's scope, but it does mean tokens are readable from client-side JS; a production deployment would want the backend to set `httpOnly` cookies directly (or a server-side proxy) instead.

## Composables

- `useAuth()`: `login`, `register`, `logout`, `fetchCurrentUser`, plus reactive `user`/`isLoggedIn` state.
- `useApplications()`: `listOwn`, `create`, `update` (resident operations) and `listAll`, `approve`, `reject`, `requestChanges`, `revoke` (manager operations).
