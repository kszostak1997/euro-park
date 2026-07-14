<script setup lang="ts">
definePageMeta({ middleware: 'guest', layout: 'auth' })

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const { login } = useAuth()
const { reportApiError } = useToast()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const user = await login(email.value, password.value)
    await navigateTo(roleLandingPath(user.role))
  } catch (err: unknown) {
    error.value = reportApiError(err, 401, 'Nie udało się zalogować')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card">
    <h1>Zaloguj się</h1>
    <p v-if="error" class="alert alert--error">{{ error }}</p>
    <form @submit.prevent="handleSubmit">
      <FormInput
        id="email"
        v-model="email"
        label="Email"
        type="email"
        required
        :disabled="loading"
        autocomplete="email"
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
