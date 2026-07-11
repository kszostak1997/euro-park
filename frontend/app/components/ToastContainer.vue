<script setup lang="ts">
const { toasts, dismissToast } = useToast()
</script>

<template>
  <div v-if="toasts.length" class="toast-container">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast"
      :class="{
        'toast--success': toast.status < 400,
        'toast--error': toast.status >= 400,
      }"
      @click="dismissToast(toast.id)"
    >
      {{ toast.message }}
    </div>
  </div>
</template>
