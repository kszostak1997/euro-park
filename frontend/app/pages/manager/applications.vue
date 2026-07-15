<script setup lang="ts">
import type { ApplicationPage, ApplicationRow } from '~/types/application'
import type { SelectOption } from '~/types/form'

definePageMeta({ layout: 'manager', middleware: ['auth', 'manager'] })

const PAGE_SIZE = 10

const {
  listAll,
  approve: approveApplication,
  reject: rejectApplication,
  requestChanges,
  revoke: revokeApplication,
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

const { data: applicationsPage, pending } = useAsyncData<ApplicationPage>(
  'manager-applications',
  () =>
    listAll({
      ...(statusFilter.value ? { status: statusFilter.value } : {}),
      page: page.value,
      size: PAGE_SIZE,
    }),
  { watch: [statusFilter, page] },
)

const applications = computed<ApplicationRow[]>(
  () => applicationsPage.value?.items ?? [],
)

const applicationsWord = computed(() =>
  pluralizePl(applicationsPage.value?.total ?? 0, ['wniosek', 'wnioski', 'wniosków']),
)

const REVIEWABLE_STATUSES = new Set(['PENDING', 'NEEDS_CHANGES'])

function isReviewable(status: string): boolean {
  return REVIEWABLE_STATUSES.has(status)
}

function isRevocable(status: string): boolean {
  return status === 'APPROVED'
}

function applyMutatedApplication(row: ApplicationRow) {
  if (!applicationsPage.value) return
  const items = applicationsPage.value.items
  const idx = items.findIndex((a) => a.id === row.id)
  if (idx === -1) return

  const stillMatchesFilter = !statusFilter.value || row.status === statusFilter.value
  if (!stillMatchesFilter) {
    applicationsPage.value = {
      ...applicationsPage.value,
      items: items.filter((a) => a.id !== row.id),
      total: applicationsPage.value.total - 1,
    }
    return
  }

  applicationsPage.value = {
    ...applicationsPage.value,
    items: replaceById(items, row),
  }
}

const { isLoading, run: runOnApp } = useKeyedAction<ApplicationRow>(
  applyMutatedApplication,
)

function runAction(app: ApplicationRow, fn: () => Promise<ApplicationRow>) {
  return runOnApp(app.id, fn)
}

type ConfirmKind = 'approve' | 'reject' | 'revoke'

const CONFIRM_COPY: Record<
  ConfirmKind,
  {
    title: string
    question: (nr: string) => string
    buttonLabel: string
    variant: 'primary' | 'destructive' | 'outline'
  }
> = {
  approve: {
    title: 'Zatwierdź wniosek',
    question: (nr) => `Zatwierdzić wniosek ${nr}?`,
    buttonLabel: 'Zatwierdź',
    variant: 'primary',
  },
  reject: {
    title: 'Odrzuć wniosek',
    question: (nr) => `Odrzucić wniosek ${nr}?`,
    buttonLabel: 'Odrzuć',
    variant: 'destructive',
  },
  revoke: {
    title: 'Cofnij zatwierdzenie',
    question: (nr) =>
      `Cofnąć zatwierdzenie wniosku ${nr}? Wniosek wróci do statusu oczekującego.`,
    buttonLabel: 'Cofnij',
    variant: 'outline',
  },
}

const {
  target: confirmTarget,
  open: openConfirmRaw,
  close: closeConfirm,
} = useDisclosure<{ app: ApplicationRow; kind: ConfirmKind }>()

const confirmCopy = computed(() =>
  confirmTarget.value ? CONFIRM_COPY[confirmTarget.value.kind] : null,
)

function openConfirm(app: ApplicationRow, kind: ConfirmKind) {
  openConfirmRaw({ app, kind })
}

async function submitConfirm() {
  if (!confirmTarget.value) return
  const { app, kind } = confirmTarget.value
  const action =
    kind === 'approve'
      ? approveApplication
      : kind === 'reject'
        ? rejectApplication
        : revokeApplication
  await runAction(app, () => action(app.id))
  closeConfirm()
}

const {
  target: requestChangesTarget,
  open: openRequestChangesRaw,
  close: closeRequestChangesRaw,
} = useDisclosure<ApplicationRow>()
const requestChangesComment = ref('')

function openRequestChanges(app: ApplicationRow) {
  requestChangesComment.value = ''
  openRequestChangesRaw(app)
}

function closeRequestChanges() {
  requestChangesComment.value = ''
  closeRequestChangesRaw()
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
            {{ applicationsPage?.total ?? 0 }} {{ applicationsWord }}
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

    <AppModal
      v-if="confirmTarget && confirmCopy"
      :title="confirmCopy.title"
      @close="closeConfirm"
    >
      <p class="modal-subtitle">
        {{ confirmCopy.question(confirmTarget.app.registration_number) }}
      </p>
      <div class="form-actions">
        <LoadingButton
          :variant="confirmCopy.variant"
          :loading="isLoading(confirmTarget.app.id)"
          @click="submitConfirm"
        >
          {{ confirmCopy.buttonLabel }}
        </LoadingButton>
        <LoadingButton
          variant="outline"
          :disabled="isLoading(confirmTarget.app.id)"
          @click="closeConfirm"
        >
          Anuluj
        </LoadingButton>
      </div>
    </AppModal>

    <AppModal
      v-if="requestChangesTarget"
      title="Poproś o poprawki"
      @close="closeRequestChanges"
    >
      <p class="modal-subtitle">{{ requestChangesTarget.registration_number }}</p>
      <FormInput
        id="requestChangesComment"
        v-model="requestChangesComment"
        label="Komentarz dla wnioskodawcy"
        placeholder="np. Popraw numer rejestracyjny"
      />
      <div class="form-actions">
        <LoadingButton
          :loading="isLoading(requestChangesTarget.id)"
          :disabled="!requestChangesComment.trim()"
          @click="submitRequestChanges"
        >
          Wyślij
        </LoadingButton>
        <LoadingButton
          variant="outline"
          :disabled="isLoading(requestChangesTarget.id)"
          @click="closeRequestChanges"
        >
          Anuluj
        </LoadingButton>
      </div>
    </AppModal>

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
              <td>
                <span
                  class="sk"
                  style="width: 70px; height: 21px; border-radius: 6px"
                />
              </td>
              <td class="actions-col">
                <span
                  class="sk"
                  style="width: 90px; height: 21px; border-radius: 6px"
                />
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
                <td>{{ a.user_email }}</td>
                <td>{{ a.floor }}</td>
                <td>{{ formatDate(a.created_at) }}</td>
                <td><StatusBadge :status="a.status" /></td>
                <td class="actions-col">
                  <div v-if="isReviewable(a.status)" class="row-actions">
                    <IconButton
                      variant="positive"
                      label="Zatwierdź"
                      :disabled="isLoading(a.id)"
                      @click="openConfirm(a, 'approve')"
                    >
                      <AppIcon name="check" />
                    </IconButton>
                    <IconButton
                      variant="destructive"
                      label="Odrzuć"
                      :disabled="isLoading(a.id)"
                      @click="openConfirm(a, 'reject')"
                    >
                      <AppIcon name="x" />
                    </IconButton>
                    <IconButton
                      variant="neutral"
                      label="Poproś o poprawki"
                      :disabled="isLoading(a.id)"
                      @click="openRequestChanges(a)"
                    >
                      <AppIcon name="message" />
                    </IconButton>
                  </div>
                  <div v-else-if="isRevocable(a.status)" class="row-actions">
                    <IconButton
                      variant="neutral"
                      label="Cofnij zatwierdzenie"
                      :disabled="isLoading(a.id)"
                      @click="openConfirm(a, 'revoke')"
                    >
                      <AppIcon name="undo" />
                    </IconButton>
                  </div>
                  <span v-else class="no-actions">-</span>
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
      <AppPagination
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
</style>
