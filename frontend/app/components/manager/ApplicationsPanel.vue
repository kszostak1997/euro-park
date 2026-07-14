<script setup lang="ts">
import type { ApplicationPage, ApplicationRow } from '~/types/application'
import type { SelectOption } from '~/types/form'
import type { UserPage } from '~/types/user'

const PAGE_SIZE = 10

const { api } = useApiClient()
const { showToast } = useToast()
const {
  listAll,
  approve: approveApplication,
  reject: rejectApplication,
  requestChanges,
} = useApplications()

const STATUS_FILTER_OPTIONS: SelectOption[] = [
  { value: '', label: 'Wszystkie statusy' },
  { value: 'PENDING', label: 'Oczekujące' },
  { value: 'NEEDS_CHANGES', label: 'Do poprawy' },
  { value: 'APPROVED', label: 'Zaakceptowane' },
  { value: 'REJECTED', label: 'Odrzucone' },
]

const statusFilter = ref('')
const page = ref(1)

watch(statusFilter, () => {
  page.value = 1
})

const {
  data: applicationsPage,
  pending,
  refresh,
} = useAsyncData<ApplicationPage>(
  'manager-applications',
  () =>
    listAll({
      ...(statusFilter.value ? { status: statusFilter.value } : {}),
      page: page.value,
      size: PAGE_SIZE,
    }),
  { watch: [statusFilter, page] },
)

const applications = computed<ApplicationRow[]>(() => applicationsPage.value?.items ?? [])

const { data: usersForLabels } = useAsyncData<UserPage>('manager-users-all', () =>
  api('/manager/users', { query: { size: 100 } }),
)

const userEmailById = computed(() => {
  const map = new Map<number, string>()
  for (const u of usersForLabels.value?.items ?? []) map.set(u.id, u.email)
  return map
})

function userLabel(userId: number): string {
  return userEmailById.value.get(userId) ?? `#${userId}`
}

const REVIEWABLE_STATUSES = new Set(['PENDING', 'NEEDS_CHANGES'])

function isReviewable(status: string): boolean {
  return REVIEWABLE_STATUSES.has(status)
}

const actionLoadingId = ref<number | null>(null)

async function runAction(app: ApplicationRow, fn: () => Promise<unknown>) {
  actionLoadingId.value = app.id
  try {
    await fn()
    showToast(200)
    await refresh()
  } catch (err: unknown) {
    const fetchError = err as { data?: { detail?: string }; status?: number }
    showToast(fetchError.status ?? 500, fetchError.data?.detail)
  } finally {
    actionLoadingId.value = null
  }
}

const approve = (app: ApplicationRow) => runAction(app, () => approveApplication(app.id))

const reject = (app: ApplicationRow) => runAction(app, () => rejectApplication(app.id))

const requestChangesTarget = ref<ApplicationRow | null>(null)
const requestChangesComment = ref('')

function openRequestChanges(app: ApplicationRow) {
  requestChangesTarget.value = app
  requestChangesComment.value = ''
}

function closeRequestChanges() {
  requestChangesTarget.value = null
  requestChangesComment.value = ''
}

async function submitRequestChanges() {
  if (!requestChangesTarget.value || !requestChangesComment.value.trim()) return
  const app = requestChangesTarget.value
  await runAction(app, () => requestChanges(app.id, requestChangesComment.value))
  closeRequestChanges()
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h1>Panel zarządcy</h1>
        <p class="panel-subtitle">
          <span v-if="pending" class="sk sk-subtitle" />
          <template v-else>
            {{ applicationsPage?.total ?? 0 }} {{ pluralWniosek(applicationsPage?.total ?? 0) }}
          </template>
        </p>
      </div>
      <FormSelect
        id="statusFilter"
        v-model="statusFilter"
        label="Filtr statusu"
        :options="STATUS_FILTER_OPTIONS"
        class="status-filter"
      />
    </div>

    <Modal v-if="requestChangesTarget" title="Poproś o poprawki" @close="closeRequestChanges">
      <p class="modal-subtitle">{{ requestChangesTarget.registration_number }}</p>
      <FormInput
        id="requestChangesComment"
        v-model="requestChangesComment"
        label="Komentarz dla wnioskodawcy"
        placeholder="np. Popraw numer rejestracyjny"
      />
      <div class="form-actions">
        <LoadingButton
          :loading="actionLoadingId === requestChangesTarget.id"
          :disabled="!requestChangesComment.trim()"
          @click="submitRequestChanges"
        >
          Wyślij
        </LoadingButton>
        <LoadingButton
          variant="outline"
          :disabled="actionLoadingId === requestChangesTarget.id"
          @click="closeRequestChanges"
        >
          Anuluj
        </LoadingButton>
      </div>
    </Modal>

    <div class="app-card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nr rejestracyjny</th>
            <th>Użytkownik</th>
            <th>Piętro</th>
            <th>Złożony</th>
            <th>Status</th>
            <th class="actions-col">Akcje</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="pending">
            <tr v-for="n in PAGE_SIZE" :key="`sk-${n}`">
              <td><span class="sk" style="width: 80px; height: 12px" /></td>
              <td><span class="sk" style="width: 140px; height: 12px" /></td>
              <td><span class="sk" style="width: 20px; height: 12px" /></td>
              <td><span class="sk" style="width: 90px; height: 12px" /></td>
              <td><span class="sk" style="width: 70px; height: 21px; border-radius: 6px" /></td>
              <td class="actions-col">
                <span class="sk" style="width: 90px; height: 21px; border-radius: 6px" />
              </td>
            </tr>
          </template>

          <template v-else-if="!applications.length">
            <tr>
              <td colspan="6" class="empty-row">
                Nie ma wniosków spełniających wybrany filtr.
              </td>
            </tr>
            <tr
              v-for="n in PAGE_SIZE - 1"
              :key="`filler-${n}`"
              class="filler-row"
              aria-hidden="true"
            >
              <td colspan="6">&nbsp;</td>
            </tr>
          </template>

          <template v-else>
            <template v-for="a in applications" :key="a.id">
              <tr>
                <td>{{ a.registration_number }}</td>
                <td>{{ userLabel(a.user_id) }}</td>
                <td>{{ a.floor }}</td>
                <td>{{ formatDate(a.created_at) }}</td>
                <td><StatusBadge :status="a.status" /></td>
                <td class="actions-col">
                  <div v-if="isReviewable(a.status)" class="row-actions">
                    <IconButton
                      variant="positive"
                      label="Zatwierdź"
                      :disabled="actionLoadingId === a.id"
                      @click="approve(a)"
                    >
                      <AppIcon name="check" />
                    </IconButton>
                    <IconButton
                      variant="destructive"
                      label="Odrzuć"
                      :disabled="actionLoadingId === a.id"
                      @click="reject(a)"
                    >
                      <AppIcon name="x" />
                    </IconButton>
                    <IconButton
                      variant="neutral"
                      label="Poproś o poprawki"
                      :disabled="actionLoadingId === a.id"
                      @click="openRequestChanges(a)"
                    >
                      <AppIcon name="message" />
                    </IconButton>
                  </div>
                  <span v-else class="no-actions">—</span>
                </td>
              </tr>
            </template>
            <tr
              v-for="n in Math.max(0, PAGE_SIZE - applications.length)"
              :key="`filler-${n}`"
              class="filler-row"
              aria-hidden="true"
            >
              <td colspan="6">&nbsp;</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div class="pagination-slot">
      <Pagination
        v-model:page="page"
        :size="PAGE_SIZE"
        :total="applicationsPage?.total ?? 0"
        :loading="pending"
      />
    </div>
  </section>
</template>

<style scoped>
.status-filter {
  min-width: 200px;
  margin-bottom: 0;
}

.empty-row {
  text-align: center;
  color: var(--color-grey-dark);
}

.pagination-slot {
  min-height: 2.5rem;
}
</style>
