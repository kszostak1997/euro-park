<script setup lang="ts">
withDefaults(
  defineProps<{
    loading?: boolean
    disabled?: boolean
    variant?: 'primary' | 'grey' | 'outline' | 'destructive'
    type?: 'button' | 'submit'
  }>(),
  {
    loading: false,
    disabled: false,
    variant: 'primary',
    type: 'button',
  },
)
</script>

<template>
  <button
    class="btn"
    :class="[`btn--${variant}`, { 'btn--loading': loading }]"
    :type="type"
    :disabled="loading || disabled"
  >
    <span class="btn-content"><slot /></span>
    <span v-if="loading" class="btn-spinner" aria-hidden="true" />
  </button>
</template>

<style scoped>
.btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1rem;
  line-height: 1;
  padding: 0.75rem 1.5rem;
  height: 2.75rem;
  color: #fff;
  background-color: var(--color-primary);
  border: 1px solid transparent;
  border-radius: var(--radius);
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    opacity 0.2s ease;
}

.btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.btn--grey {
  background-color: var(--color-grey);
}

.btn--grey:hover:not(:disabled) {
  background-color: var(--color-grey-dark);
}

.btn--outline {
  background-color: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn--outline:hover:not(:disabled) {
  background-color: #eff6ff;
}

.btn--destructive {
  background-color: var(--color-error);
}

.btn--destructive:hover:not(:disabled) {
  background-color: #a5311f;
}

.btn--full {
  width: 100%;
}

.btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.btn--loading .btn-content {
  opacity: 0;
}

.btn-spinner {
  position: absolute;
  width: 1.1rem;
  height: 1.1rem;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #fff;
  border-radius: 50%;
  animation: btn-spin 0.6s linear infinite;
}

@keyframes btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
