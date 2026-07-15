<script setup lang="ts">
import type { BarrierCheckResult } from '~/composables/useBarrier'

definePageMeta({ layout: 'manager', middleware: ['auth', 'manager'] })

const { checkAccess } = useBarrier()
const { reportApiError } = useToast()

const plate = ref('')
const plateError = ref('')
const loading = ref(false)
const result = ref<BarrierCheckResult | null>(null)

async function submit() {
  if (!isValidRegistrationNumber(plate.value)) {
    plateError.value = 'Nieprawidłowy numer rejestracyjny'
    result.value = null
    return
  }
  plateError.value = ''
  result.value = null
  loading.value = true
  try {
    result.value = await checkAccess(plate.value)
  } catch (err: unknown) {
    reportApiError(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h1>Brama (test)</h1>
        <p class="panel-subtitle">Panel testowy szlabanu</p>
      </div>
    </div>

    <div class="app-card gate-card">
      <p>
        Funkcja testowa: sprawdza, czy szlaban wpuściłby podany numer rejestracyjny.
      </p>

      <FormInput
        id="gatePlate"
        v-model="plate"
        label="Nr rejestracyjny"
        placeholder="np. WA12345"
        :error="plateError"
      />
      <LoadingButton :loading="loading" @click="submit">Sprawdź dostęp</LoadingButton>

      <div
        v-if="result"
        class="gate-result"
        :class="result.access_granted ? 'gate-result--granted' : 'gate-result--denied'"
      >
        <AppIcon :name="result.access_granted ? 'check' : 'x'" :size="18" />
        <span>
          {{
            result.access_granted
              ? `Dostęp przyznany dla ${result.registration_number}`
              : `Dostęp odrzucony dla ${result.registration_number}`
          }}
        </span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.panel {
  max-width: 420px;
  margin-left: auto;
  margin-right: auto;
}

.gate-card {
  max-width: 420px;
}

.gate-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
}

.gate-result--granted {
  background: var(--color-positive-bg);
  color: var(--color-positive-fg);
}

.gate-result--denied {
  background: var(--color-destructive-bg);
  color: var(--color-destructive-fg);
}
</style>
