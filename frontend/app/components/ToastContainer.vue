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

<style scoped>
.toast-container {
  position: fixed;
  top: 4.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  z-index: 1000;
  width: calc(100% - 2rem);
  max-width: 420px;
}

.toast {
  background: #323232;
  color: #fff;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  font-size: 0.9rem;
  cursor: pointer;
  max-width: 100%;
  word-break: break-word;
}

.toast--success {
  background: var(--color-success);
}

.toast--error {
  background: var(--color-error);
}
</style>
