<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'positive' | 'destructive' | 'neutral'
    label: string
    disabled?: boolean
  }>(),
  { variant: 'neutral', disabled: false },
)
</script>

<template>
  <button
    type="button"
    class="icon-btn"
    :class="`icon-btn--${variant}`"
    :aria-label="label"
    :title="label"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<style scoped>
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    border-color 0.15s ease;
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.icon-btn--positive {
  color: var(--color-positive-fg);
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.icon-btn--positive:hover:not(:disabled) {
  background: var(--color-positive-bg);
}

.icon-btn--destructive {
  color: var(--color-destructive-fg);
  border-color: #fecaca;
  background: #fef2f2;
}

.icon-btn--destructive:hover:not(:disabled) {
  background: var(--color-destructive-bg);
}

.icon-btn--neutral {
  color: var(--color-neutral-fg);
  border-color: var(--color-border);
  background: #f8fafc;
}

.icon-btn--neutral:hover:not(:disabled) {
  background: var(--color-neutral-bg);
}
</style>
