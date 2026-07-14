<script setup lang="ts">
definePageMeta({ middleware: 'guest', layout: 'auth' })

const email = ref('')
const password = ref('')
const error = ref('')
const emailError = ref('')
const loading = ref(false)

const { login } = useAuth()
const { extractApiErrorMessage } = useToast()

function validate(): boolean {
  emailError.value = isValidEmail(email.value) ? '' : 'Adres email jest nieprawidłowy'
  return !emailError.value
}

async function handleSubmit() {
  error.value = ''
  if (!validate()) {
    return
  }

  loading.value = true
  try {
    const user = await login(email.value, password.value)
    await navigateTo(roleLandingPath(user.role))
  } catch (err: unknown) {
    error.value = extractApiErrorMessage(err, 401, 'Nie udało się zalogować')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card">
    <h1>Zaloguj się</h1>
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
        :disabled="loading"
        autocomplete="current-password"
      />
      <LoadingButton class="btn--full" type="submit" :loading="loading">
        Zaloguj się
      </LoadingButton>
    </form>
    <p class="form-footer">
      Nie masz konta?
      <NuxtLink to="/register">Zarejestruj się</NuxtLink>
    </p>
  </div>
</template>
