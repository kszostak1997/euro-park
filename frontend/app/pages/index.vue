<script setup lang="ts">
const config = useRuntimeConfig()
const baseURL = import.meta.server ? config.apiBase : config.public.apiBase

const { data, error, status } = await useFetch<{ status: string }>('/health', {
  baseURL,
})

const clientBase = config.public.apiBase

const email = ref('test@example.com')
const password = ref('supersecret123')
const accessToken = ref('')
const refreshToken = ref('')
const lastAction = ref('')
const result = ref<unknown>(null)
const actionError = ref('')

async function call(action: string, fn: () => Promise<unknown>) {
  lastAction.value = action
  actionError.value = ''
  result.value = null
  try {
    result.value = await fn()
  } catch (err: unknown) {
    const fetchError = err as { data?: { detail?: string }; message?: string }
    actionError.value = fetchError.data?.detail ?? fetchError.message ?? 'Unknown error'
  }
}

const register = () =>
  call('register', () =>
    $fetch('/auth/register', {
      baseURL: clientBase,
      method: 'POST',
      body: { email: email.value, password: password.value },
    }),
  )

const login = () =>
  call('login', async () => {
    const res = await $fetch<{ access_token: string; refresh_token: string }>(
      '/auth/login',
      {
        baseURL: clientBase,
        method: 'POST',
        body: { email: email.value, password: password.value },
      },
    )
    accessToken.value = res.access_token
    refreshToken.value = res.refresh_token
    return res
  })

const me = () =>
  call('me', () =>
    $fetch('/auth/me', {
      baseURL: clientBase,
      headers: { Authorization: `Bearer ${accessToken.value}` },
    }),
  )

const refresh = () =>
  call('refresh', async () => {
    const res = await $fetch<{ access_token: string; refresh_token: string }>(
      '/auth/refresh',
      {
        baseURL: clientBase,
        method: 'POST',
        body: { refresh_token: refreshToken.value },
      },
    )
    accessToken.value = res.access_token
    refreshToken.value = res.refresh_token
    return res
  })

const registrationNumber = ref('WA12345')
const floor = ref(2)
const comment = ref('proszę o miejsce')
const applicationId = ref('')
const authHeaders = () => ({ Authorization: `Bearer ${accessToken.value}` })

const createApplication = () =>
  call('createApplication', () =>
    $fetch('/applications', {
      baseURL: clientBase,
      method: 'POST',
      headers: authHeaders(),
      body: {
        registration_number: registrationNumber.value,
        floor: floor.value,
        comment: comment.value,
      },
    }),
  )

const listApplications = () =>
  call('listApplications', () =>
    $fetch('/applications', { baseURL: clientBase, headers: authHeaders() }),
  )

const getApplication = () =>
  call('getApplication', () =>
    $fetch(`/applications/${applicationId.value}`, {
      baseURL: clientBase,
      headers: authHeaders(),
    }),
  )

const updateApplication = () =>
  call('updateApplication', () =>
    $fetch(`/applications/${applicationId.value}`, {
      baseURL: clientBase,
      method: 'PATCH',
      headers: authHeaders(),
      body: {
        registration_number: registrationNumber.value,
        floor: floor.value,
        comment: comment.value,
      },
    }),
  )

const statusFilter = ref('')
const managerApplicationId = ref('')
const changeComment = ref('Proszę poprawić dane')

const listAllApplications = () =>
  call('listAllApplications', () =>
    $fetch('/manager/applications', {
      baseURL: clientBase,
      headers: authHeaders(),
      query: statusFilter.value ? { status: statusFilter.value } : {},
    }),
  )

const approveApplication = () =>
  call('approveApplication', () =>
    $fetch(`/manager/applications/${managerApplicationId.value}/approve`, {
      baseURL: clientBase,
      method: 'POST',
      headers: authHeaders(),
    }),
  )

const rejectApplication = () =>
  call('rejectApplication', () =>
    $fetch(`/manager/applications/${managerApplicationId.value}/reject`, {
      baseURL: clientBase,
      method: 'POST',
      headers: authHeaders(),
    }),
  )

const requestChanges = () =>
  call('requestChanges', () =>
    $fetch(`/manager/applications/${managerApplicationId.value}/request-changes`, {
      baseURL: clientBase,
      method: 'POST',
      headers: authHeaders(),
      body: { comment: changeComment.value },
    }),
  )

const barrierRegistrationNumber = ref('WA12345')

const checkBarrierAccess = () =>
  call('checkBarrierAccess', () =>
    $fetch('/barrier/check-access', {
      baseURL: clientBase,
      method: 'POST',
      body: { registration_number: barrierRegistrationNumber.value },
    }),
  )

interface UserRow {
  id: number
  email: string
  role: string
}

interface ApplicationRow {
  id: number
  user_id: number
  registration_number: string
  floor: number
  status: string
}

const allUsers = ref<UserRow[]>([])
const allApplications = ref<ApplicationRow[]>([])

const loadAllUsers = () =>
  call('loadAllUsers', async () => {
    const res = await $fetch<UserRow[]>('/manager/users', {
      baseURL: clientBase,
      headers: authHeaders(),
    })
    allUsers.value = res
    return res
  })

const loadAllApplicationsOverview = () =>
  call('loadAllApplicationsOverview', async () => {
    const res = await $fetch<{ items: ApplicationRow[] }>('/manager/applications', {
      baseURL: clientBase,
      headers: authHeaders(),
      query: { size: 100 },
    })
    allApplications.value = res.items
    return res
  })
</script>

<template>
  <main style="font-family: sans-serif; padding: 2rem; max-width: 640px">
    <h1>Euro Park</h1>
    <p v-if="status === 'pending'">Sprawdzam backend…</p>
    <p v-else-if="error" style="color: #c0392b">Brak połączenia z API</p>
    <p v-else style="color: #27ae60">Backend odpowiada: status = {{ data?.status }}</p>

    <hr />

    <h2>Auth test</h2>
    <div style="display: flex; flex-direction: column; gap: 0.5rem; max-width: 320px">
      <label>
        Email
        <input v-model="email" type="email" style="width: 100%" />
      </label>
      <label>
        Hasło
        <input v-model="password" type="password" style="width: 100%" />
      </label>
    </div>

    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <button @click="register">Register</button>
      <button @click="login">Login</button>
      <button :disabled="!accessToken" @click="me">Get /auth/me</button>
      <button :disabled="!refreshToken" @click="refresh">Refresh token</button>
    </div>

    <p><strong>Access token:</strong> {{ accessToken || '(none)' }}</p>
    <p><strong>Refresh token:</strong> {{ refreshToken || '(none)' }}</p>

    <hr />

    <h2>Applications test</h2>
    <div style="display: flex; flex-direction: column; gap: 0.5rem; max-width: 320px">
      <label>
        Nr rejestracyjny
        <input v-model="registrationNumber" style="width: 100%" />
      </label>
      <label>
        Piętro
        <input v-model.number="floor" type="number" style="width: 100%" />
      </label>
      <label>
        Komentarz
        <input v-model="comment" style="width: 100%" />
      </label>
      <label>
        Application ID (do get/update)
        <input v-model="applicationId" style="width: 100%" />
      </label>
    </div>

    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <button :disabled="!accessToken" @click="createApplication">Create</button>
      <button :disabled="!accessToken" @click="listApplications">List own</button>
      <button :disabled="!accessToken || !applicationId" @click="getApplication">
        Get by id
      </button>
      <button :disabled="!accessToken || !applicationId" @click="updateApplication">
        Update
      </button>
    </div>

    <hr />

    <h2>Manager test</h2>
    <p style="color: #666; font-size: 0.9rem">
      Wymaga zalogowania jako MANAGER/ADMIN (rolę można nadać tylko bezpośrednio w bazie
      danych).
    </p>
    <div style="display: flex; flex-direction: column; gap: 0.5rem; max-width: 320px">
      <label>
        Filtr statusu
        <select v-model="statusFilter" style="width: 100%">
          <option value="">(wszystkie)</option>
          <option value="PENDING">PENDING</option>
          <option value="NEEDS_CHANGES">NEEDS_CHANGES</option>
          <option value="APPROVED">APPROVED</option>
          <option value="REJECTED">REJECTED</option>
        </select>
      </label>
      <label>
        Application ID
        <input v-model="managerApplicationId" style="width: 100%" />
      </label>
      <label>
        Komentarz (do poprawy)
        <input v-model="changeComment" style="width: 100%" />
      </label>
    </div>

    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <button :disabled="!accessToken" @click="listAllApplications">
        List all (manager)
      </button>
      <button
        :disabled="!accessToken || !managerApplicationId"
        @click="approveApplication"
      >
        Approve
      </button>
      <button
        :disabled="!accessToken || !managerApplicationId"
        @click="rejectApplication"
      >
        Reject
      </button>
      <button :disabled="!accessToken || !managerApplicationId" @click="requestChanges">
        Request changes
      </button>
    </div>

    <hr />

    <h2>Barrier test</h2>
    <div style="display: flex; flex-direction: column; gap: 0.5rem; max-width: 320px">
      <label>
        Nr rejestracyjny
        <input v-model="barrierRegistrationNumber" style="width: 100%" />
      </label>
    </div>

    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <button @click="checkBarrierAccess">Check access</button>
    </div>

    <hr />

    <h2>Overview: all users &amp; applications</h2>
    <p style="color: #666; font-size: 0.9rem">Wymaga zalogowania jako MANAGER/ADMIN.</p>
    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <button :disabled="!accessToken" @click="loadAllUsers">Load all users</button>
      <button :disabled="!accessToken" @click="loadAllApplicationsOverview">
        Load all applications
      </button>
    </div>

    <h3>Users ({{ allUsers.length }})</h3>
    <ul>
      <li v-for="u in allUsers" :key="u.id">
        #{{ u.id }} — {{ u.email }} — {{ u.role }}
      </li>
    </ul>

    <h3>Applications ({{ allApplications.length }})</h3>
    <ul>
      <li v-for="a in allApplications" :key="a.id">
        #{{ a.id }} — {{ a.registration_number }} — piętro {{ a.floor }} —
        {{ a.status }} (user #{{ a.user_id }})
      </li>
    </ul>

    <div v-if="lastAction">
      <h3>Result of "{{ lastAction }}"</h3>
      <p v-if="actionError" style="color: #c0392b">{{ actionError }}</p>
      <pre v-else style="background: #f4f4f4; padding: 1rem; overflow-x: auto">{{
        JSON.stringify(result, null, 2)
      }}</pre>
    </div>
  </main>
</template>
