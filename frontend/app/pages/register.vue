<script setup lang="ts">
definePageMeta({ middleware: 'guest', layout: 'auth' })

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PASSWORD_MIN = 4
const PASSWORD_MAX = 128

const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')
const loading = ref(false)

const emailError = ref('')
const passwordError = ref('')
const passwordConfirmError = ref('')

const { register, login } = useAuth()
const { showToast } = useToast()

function validate(): boolean {
  emailError.value = EMAIL_PATTERN.test(email.value)
    ? ''
    : 'Adres email jest nieprawidłowy'

  passwordError.value =
    password.value.length >= PASSWORD_MIN && password.value.length <= PASSWORD_MAX
      ? ''
      : `Hasło musi mieć od ${PASSWORD_MIN} do ${PASSWORD_MAX} znaków`

  passwordConfirmError.value =
    passwordConfirm.value === password.value ? '' : 'Hasła nie są identyczne'

  return !emailError.value && !passwordError.value && !passwordConfirmError.value
}

async function handleSubmit() {
  error.value = ''
  if (!validate()) {
    return
  }

  loading.value = true
  try {
    await register(email.value, password.value)
    const user = await login(email.value, password.value)
    showToast(200, 'Konto zostało utworzone')
    await navigateTo(roleLandingPath(user.role))
  } catch (err: unknown) {
    const fetchError = err as { data?: { detail?: string }; status?: number }
    error.value = fetchError.data?.detail ?? 'Nie udało się zarejestrować'
    showToast(fetchError.status ?? 400, error.value)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card">
    <h1>Zarejestruj się</h1>
    <p v-if="error" class="alert alert--error">{{ error }}</p>
    <form novalidate @submit.prevent="handleSubmit">
      <FormInput
        id="email"
        v-model="email"
        label="Email"
        type="email"
        required
        :disabled="loading"
        autocomplete="email"
        :error="emailError"
      />
      <FormInput
        id="password"
        v-model="password"
        label="Hasło"
        type="password"
        required
        :minlength="PASSWORD_MIN"
        :maxlength="PASSWORD_MAX"
        :disabled="loading"
        autocomplete="new-password"
        :error="passwordError"
      />
      <FormInput
        id="password-confirm"
        v-model="passwordConfirm"
        label="Powtórz hasło"
        type="password"
        required
        :minlength="PASSWORD_MIN"
        :maxlength="PASSWORD_MAX"
        :disabled="loading"
        autocomplete="new-password"
        :error="passwordConfirmError"
      />
      <LoadingButton class="btn--full" type="submit" :loading="loading">
        Zarejestruj się
      </LoadingButton>
    </form>
    <p class="form-footer">
      Masz już konto?
      <NuxtLink to="/login">Zaloguj się</NuxtLink>
    </p>
  </div>
</template>
