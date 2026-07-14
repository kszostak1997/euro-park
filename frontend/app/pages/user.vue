<script setup lang="ts">
import type { ApplicationRow } from '~/types/application'
import type { SelectOption } from '~/types/form'

definePageMeta({ middleware: 'auth' })

const { listOwn, create, update } = useApplications()

const { data: applications, pending } = useAsyncData<ApplicationRow[]>(
  'my-applications',
  () => listOwn(),
  { default: () => [] },
)

const needsChangesCount = computed(
  () => (applications.value ?? []).filter((a) => a.status === 'NEEDS_CHANGES').length,
)

const subtitleText = computed(() => {
  const total = (applications.value ?? []).length
  if (total === 0) return 'Nie masz jeszcze żadnych wniosków'
  let text = `${total} ${pluralWniosek(total)}`
  if (needsChangesCount.value > 0) {
    const verb = needsChangesCount.value === 1 ? 'wymaga poprawy' : 'wymagają poprawy'
    text += ` · ${needsChangesCount.value} ${verb}`
  }
  return text
})

const FLOOR_OPTIONS: SelectOption<number>[] = [
  { value: 0, label: 'Piętro 0' },
  { value: 1, label: 'Piętro 1' },
  { value: 2, label: 'Piętro 2' },
]

const showForm = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const editingManagerComment = ref<string | null>(null)
const formRegistrationNumber = ref('')
const formRegistrationNumberError = ref('')
const formFloor = ref(0)
const formComment = ref('')

function openForm(application?: ApplicationRow) {
  formMode.value = application ? 'edit' : 'create'
  editingId.value = application?.id ?? null
  editingManagerComment.value = application?.manager_comment ?? null
  formRegistrationNumber.value = application?.registration_number ?? ''
  formRegistrationNumberError.value = ''
  formFloor.value = application?.floor ?? 0
  formComment.value = application?.applicant_comment ?? ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

function upsertApplication(row: ApplicationRow) {
  const list = applications.value ?? []
  const idx = list.findIndex((a) => a.id === row.id)
  applications.value =
    idx === -1 ? [row, ...list] : [...list.slice(0, idx), row, ...list.slice(idx + 1)]
}

const { loading: formLoading, submit: submitFormAction } = useModalForm<ApplicationRow>((row) => {
  closeForm()
  upsertApplication(row)
})

function validateForm(): boolean {
  formRegistrationNumberError.value = isValidRegistrationNumber(formRegistrationNumber.value)
    ? ''
    : 'Nieprawidłowy numer rejestracyjny (np. WA12345)'
  return !formRegistrationNumberError.value
}

function submitForm() {
  if (!validateForm()) return

  const data = {
    registration_number: formRegistrationNumber.value,
    floor: formFloor.value,
    applicant_comment: formComment.value || null,
  }
  return formMode.value === 'create'
    ? submitFormAction(() => create(data), 201)
    : submitFormAction(() => update(editingId.value as number, data))
}
</script>

<template>
  <div class="app-content">
    <section class="panel">
      <div class="panel-header">
        <div>
          <h1>Moje wnioski</h1>
          <p class="panel-subtitle">
            <span v-if="pending" class="sk sk-subtitle" />
            <template v-else>{{ subtitleText }}</template>
          </p>
        </div>
        <LoadingButton v-if="!pending && applications?.length" @click="openForm()">
          Złóż wniosek
        </LoadingButton>
      </div>

      <AppModal
        v-if="showForm"
        :title="formMode === 'create' ? 'Nowy wniosek' : 'Popraw wniosek'"
        @close="closeForm"
      >
        <div v-if="editingManagerComment" class="review-comment">
          <p class="review-comment-title">Komentarz zarządcy</p>
          <p class="review-comment-text">{{ editingManagerComment }}</p>
        </div>

        <FormInput
          id="formRegistrationNumber"
          v-model="formRegistrationNumber"
          label="Nr rejestracyjny"
          placeholder="np. WA12345"
          :error="formRegistrationNumberError"
        />
        <FormSelect
          id="formFloor"
          v-model="formFloor"
          label="Piętro"
          :options="FLOOR_OPTIONS"
        />
        <FormInput
          id="formComment"
          v-model="formComment"
          label="Komentarz (opcjonalnie)"
          placeholder="Dodatkowe informacje"
        />
        <div class="form-actions">
          <LoadingButton :loading="formLoading" @click="submitForm">
            {{ formMode === 'create' ? 'Złóż wniosek' : 'Zapisz zmiany' }}
          </LoadingButton>
          <LoadingButton variant="outline" :disabled="formLoading" @click="closeForm">
            Anuluj
          </LoadingButton>
        </div>
      </AppModal>

      <template v-if="pending">
        <div v-for="n in 3" :key="n" class="app-card">
          <div class="skeleton-row">
            <div>
              <span class="sk" style="width: 110px; height: 17px; margin-bottom: 9px" />
              <span class="sk" style="width: 170px; height: 12px" />
            </div>
            <span class="sk" style="width: 82px; height: 21px; border-radius: 6px" />
          </div>
        </div>
      </template>

      <div v-else-if="!applications?.length" class="app-card empty-card">
        <div class="empty-icon">
          <AppIcon name="document" :size="22" />
        </div>
        <p class="empty-title">Brak wniosków</p>
        <p class="empty-text">
          Nie złożyłeś jeszcze wniosku o miejsce parkingowe. Podaj numer rejestracyjny i
          preferowane piętro.
        </p>
        <LoadingButton @click="openForm()">Złóż pierwszy wniosek</LoadingButton>
      </div>

      <template v-else>
        <div v-for="a in applications" :key="a.id" class="app-card">
          <div class="application-row">
            <div>
              <p class="application-nr">{{ a.registration_number }}</p>
              <p class="application-meta">
                Piętro {{ a.floor }} · złożony {{ formatDate(a.created_at) }}
              </p>
            </div>
            <StatusBadge :status="a.status" />
          </div>

          <div v-if="a.status === 'NEEDS_CHANGES' && a.manager_comment" class="review-comment">
            <p class="review-comment-title">Komentarz zarządcy</p>
            <p class="review-comment-text">{{ a.manager_comment }}</p>
          </div>

          <LoadingButton
            v-if="a.status === 'NEEDS_CHANGES' || a.status === 'PENDING'"
            variant="outline"
            class="fix-btn"
            @click="openForm(a)"
          >
            {{ a.status === 'NEEDS_CHANGES' ? 'Popraw wniosek' : 'Edytuj wniosek' }}
          </LoadingButton>
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped>
.application-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.application-nr {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.02em;
}

.application-meta {
  margin: 0.2rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-grey-dark);
}

.review-comment {
  background: #fef6e7;
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  margin-top: 0.7rem;
}

.review-comment-title {
  margin: 0;
  font-size: 0.6875rem;
  font-weight: 700;
  color: #b45309;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.review-comment-text {
  margin: 0.2rem 0 0;
  font-size: 0.8125rem;
  color: #78350f;
  line-height: 1.45;
}

.fix-btn {
  margin-top: 0.65rem;
}
</style>
