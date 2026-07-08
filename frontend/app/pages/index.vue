<script setup lang="ts">
const config = useRuntimeConfig()
const baseURL = import.meta.server
  ? config.apiBase
  : config.public.apiBase

const { data, error, status } = await useFetch<{ status: string }>('/health', {
  baseURL,
})
</script>

<template>
  <main style="font-family: sans-serif; padding: 2rem">
    <h1>Euro Park — parking wspólnoty</h1>
    <p v-if="status === 'pending'">Sprawdzam backend…</p>
    <p v-else-if="error" style="color: #c0392b">
      Brak połączenia z API
    </p>
    <p v-else style="color: #27ae60">
      Backend odpowiada: status = {{ data?.status }}
    </p>
  </main>
</template>
