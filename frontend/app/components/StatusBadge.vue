<script setup lang="ts">
import type { ApplicationStatus } from '~/types/application'

defineProps<{ status: ApplicationStatus }>()

const STATUS_META: Record<
  ApplicationStatus,
  { label: string; bg: string; fg: string }
> = {
  PENDING: {
    label: 'Oczekuje',
    bg: 'var(--color-neutral-bg)',
    fg: 'var(--color-neutral-fg)',
  },
  NEEDS_CHANGES: {
    label: 'Do poprawy',
    bg: 'var(--color-warning-bg)',
    fg: 'var(--color-warning-fg)',
  },
  APPROVED: {
    label: 'Zaakceptowany',
    bg: 'var(--color-positive-bg)',
    fg: 'var(--color-positive-fg)',
  },
  REJECTED: {
    label: 'Odrzucony',
    bg: 'var(--color-destructive-bg)',
    fg: 'var(--color-destructive-fg)',
  },
}
</script>

<template>
  <span
    class="status-badge"
    :style="{ background: STATUS_META[status].bg, color: STATUS_META[status].fg }"
  >
    {{ STATUS_META[status].label }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-block;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 3px 9px;
  border-radius: 6px;
  white-space: nowrap;
}
</style>
