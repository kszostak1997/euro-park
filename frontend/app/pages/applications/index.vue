<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { user } = useAuth()
const { api } = useApi()
const { showToast } = useToast()

interface ApplicationRow {
  id: number
  user_id: number
  registration_number: string
  floor: number
  status: string
  comment: string | null
  created_at: string
}

const registrationNumber = ref('WA12345')
const floor = ref(2)
const comment = ref('')
const applicationId = ref('')

const applications = ref<ApplicationRow[]>([])
const selectedApplication = ref<ApplicationRow | null>(null)

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

const createApplication = () =>
  withLoading(async () => {
    await api('/applications', {
      method: 'POST',
      body: {
        registration_number: registrationNumber.value,
        floor: floor.value,
        comment: comment.value || null,
      },
    })
    showToast(201)
    await listApplications()
  })

const listApplications = () =>
  withLoading(async () => {
    applications.value = await api<ApplicationRow[]>('/applications')
  })

const getApplication = () =>
  withLoading(async () => {
    selectedApplication.value = await api<ApplicationRow>(
      `/applications/${applicationId.value}`,
    )
  })

const updateApplication = () =>
  withLoading(async () => {
    await api(`/applications/${applicationId.value}`, {
      method: 'PATCH',
      body: {
        registration_number: registrationNumber.value,
        floor: floor.value,
        comment: comment.value || null,
      },
    })
    showToast(200)
    await listApplications()
  })

const barrierRegistrationNumber = ref('WA12345')
const barrierResult = ref<{ registration_number: string; access_granted: boolean } | null>(
  null,
)

const checkBarrierAccess = () =>
  withLoading(async () => {
    barrierResult.value = await $fetch('/barrier/check-access', {
      baseURL: useRuntimeConfig().public.apiBase,
      method: 'POST',
      body: { registration_number: barrierRegistrationNumber.value },
    })
  })
</script>

<template>
  <div class="app-content">
    <h1>Moje wnioski</h1>
    <p>Zalogowano jako {{ user?.email }} ({{ user?.role }})</p>

    <hr />

    <h2>Wnioski</h2>
    <FormInput
      id="registrationNumber"
      v-model="registrationNumber"
      label="Nr rejestracyjny"
    />
    <div class="field">
      <label for="floor">Piętro</label>
      <input id="floor" v-model.number="floor" type="number" />
    </div>
    <FormInput id="comment" v-model="comment" label="Komentarz" />
    <FormInput id="applicationId" v-model="applicationId" label="Application ID (do get/update)" />

    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <LoadingButton :loading="loading" @click="createApplication">Utwórz</LoadingButton>
      <LoadingButton variant="outline" :loading="loading" @click="listApplications">
        Lista moich wniosków
      </LoadingButton>
      <LoadingButton
        variant="outline"
        :loading="loading"
        :disabled="!applicationId"
        @click="getApplication"
      >
        Pobierz po ID
      </LoadingButton>
      <LoadingButton
        variant="outline"
        :loading="loading"
        :disabled="!applicationId"
        @click="updateApplication"
      >
        Zaktualizuj
      </LoadingButton>
    </div>

    <ul v-if="applications.length">
      <li v-for="a in applications" :key="a.id">
        #{{ a.id }} — {{ a.registration_number }} — piętro {{ a.floor }} — {{ a.status }}
      </li>
    </ul>

    <pre v-if="selectedApplication" style="background: #f4f4f4; padding: 1rem; overflow-x: auto">{{
      JSON.stringify(selectedApplication, null, 2)
    }}</pre>

    <hr />

    <h2>Sprawdź dostęp (szlaban)</h2>
    <FormInput
      id="barrierRegistrationNumber"
      v-model="barrierRegistrationNumber"
      label="Nr rejestracyjny"
    />
    <div style="display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap">
      <LoadingButton :loading="loading" @click="checkBarrierAccess">
        Sprawdź dostęp
      </LoadingButton>
    </div>

    <p v-if="barrierResult">
      {{ barrierResult.registration_number }} —
      <strong :style="{ color: barrierResult.access_granted ? '#27ae60' : '#c0392b' }">
        {{ barrierResult.access_granted ? 'Dostęp przyznany' : 'Brak dostępu' }}
      </strong>
    </p>
  </div>
</template>
