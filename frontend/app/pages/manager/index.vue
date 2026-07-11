<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { user } = useAuth()
const { api } = useApi()
const { showToast } = useToast()

if (user.value && user.value.role === 'USER') {
  await navigateTo('/applications')
}

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

const loading = ref(false)

async function withLoading(fn: () => Promise<void>) {
  loading.value = true
  try {
    await fn()
  } catch (err: unknown) {
    const fetchError = err as { data?: { detail?: string }; status?: number }
    showToast(fetchError.status ?? 500, fetchError.data?.detail)
  } finally {
    loading.value = false
  }
}

const statusFilter = ref('')
const managerApplicationId = ref('')
const changeComment = ref('Proszę poprawić dane')
const managedApplications = ref<ApplicationRow[]>([])

const listAllApplications = () =>
  withLoading(async () => {
    const res = await api<{ items: ApplicationRow[] }>('/manager/applications', {
      query: statusFilter.value ? { status: statusFilter.value } : {},
    })
    managedApplications.value = res.items
  })

const approveApplication = () =>
  withLoading(async () => {
    await api(`/manager/applications/${managerApplicationId.value}/approve`, {
      method: 'POST',
    })
    showToast(200)
    await listAllApplications()
  })

const rejectApplication = () =>
  withLoading(async () => {
    await api(`/manager/applications/${managerApplicationId.value}/reject`, {
      method: 'POST',
    })
    showToast(200)
    await listAllApplications()
  })

const requestChanges = () =>
  withLoading(async () => {
    await api(`/manager/applications/${managerApplicationId.value}/request-changes`, {
      method: 'POST',
      body: { comment: changeComment.value },
    })
    showToast(200)
    await listAllApplications()
  })

const allUsers = ref<UserRow[]>([])
const allApplications = ref<ApplicationRow[]>([])

const loadAllUsers = () =>
  withLoading(async () => {
    allUsers.value = await api<UserRow[]>('/manager/users')
  })

const loadAllApplicationsOverview = () =>
  withLoading(async () => {
    const res = await api<{ items: ApplicationRow[] }>('/manager/applications', {
      query: { size: 100 },
    })
    allApplications.value = res.items
  })
</script>

<template>
  <div class="app-content">
    <h1>Panel zarządcy</h1>
    <p>Zalogowano jako {{ user?.email }} ({{ user?.role }})</p>

    <hr />

    <h2>Wnioski do rozpatrzenia</h2>
    <div class="field">
      <label for="statusFilter">Filtr statusu</label>
      <select id="statusFilter" v-model="statusFilter">
        <option value="">(wszystkie)</option>
        <option value="PENDING">PENDING</option>
        <option value="NEEDS_CHANGES">NEEDS_CHANGES</option>
        <option value="APPROVED">APPROVED</option>
        <option value="REJECTED">REJECTED</option>
      </select>
    </div>
    <FormInput id="managerApplicationId" v-model="managerApplicationId" label="Application ID" />
    <FormInput id="changeComment" v-model="changeComment" label="Komentarz (do poprawy)" />

    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <LoadingButton :loading="loading" @click="listAllApplications">
        Lista wszystkich wniosków
      </LoadingButton>
      <LoadingButton
        :loading="loading"
        :disabled="!managerApplicationId"
        @click="approveApplication"
      >
        Zatwierdź
      </LoadingButton>
      <LoadingButton
        variant="outline"
        :loading="loading"
        :disabled="!managerApplicationId"
        @click="rejectApplication"
      >
        Odrzuć
      </LoadingButton>
      <LoadingButton
        variant="grey"
        :loading="loading"
        :disabled="!managerApplicationId"
        @click="requestChanges"
      >
        Poproś o poprawki
      </LoadingButton>
    </div>

    <ul v-if="managedApplications.length">
      <li v-for="a in managedApplications" :key="a.id">
        #{{ a.id }} — {{ a.registration_number }} — piętro {{ a.floor }} — {{ a.status }}
        (user #{{ a.user_id }})
      </li>
    </ul>

    <hr />

    <h2>Przegląd: wszyscy użytkownicy i wnioski</h2>
    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <LoadingButton :loading="loading" @click="loadAllUsers">
        Wczytaj użytkowników
      </LoadingButton>
      <LoadingButton variant="outline" :loading="loading" @click="loadAllApplicationsOverview">
        Wczytaj wnioski
      </LoadingButton>
    </div>

    <h3>Użytkownicy ({{ allUsers.length }})</h3>
    <ul>
      <li v-for="u in allUsers" :key="u.id">#{{ u.id }} — {{ u.email }} — {{ u.role }}</li>
    </ul>

    <h3>Wnioski ({{ allApplications.length }})</h3>
    <ul>
      <li v-for="a in allApplications" :key="a.id">
        #{{ a.id }} — {{ a.registration_number }} — piętro {{ a.floor }} — {{ a.status }}
        (user #{{ a.user_id }})
      </li>
    </ul>
  </div>
</template>
