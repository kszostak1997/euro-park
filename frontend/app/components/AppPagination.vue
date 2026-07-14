<script setup lang="ts">
const props = defineProps<{
  page: number
  size: number
  total: number
  loading?: boolean
}>()

const emit = defineEmits<{ 'update:page': [page: number] }>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.size)))

const pageNumbers = computed<(number | '...')[]>(() => {
  const total = totalPages.value
  const current = props.page
  const pages: (number | '...')[] = [1]

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)

  if (start > 2) pages.push('...')
  for (let p = start; p <= end; p++) pages.push(p)
  if (end < total - 1) pages.push('...')
  if (total > 1) pages.push(total)

  return pages
})

function goTo(p: number) {
  if (p < 1 || p > totalPages.value || p === props.page || props.loading) return
  emit('update:page', p)
}
</script>

<template>
  <div class="pagination">
    <span class="pagination-info">{{ total }} wyników</span>
    <div class="pagination-controls">
      <button
        type="button"
        class="page-btn"
        :disabled="loading || page <= 1"
        aria-label="Poprzednia strona"
        @click="goTo(page - 1)"
      >
        ‹
      </button>
      <template v-for="(p, idx) in pageNumbers">
        <span v-if="p === '...'" :key="`ellipsis-${idx}`" class="page-ellipsis">…</span>
        <button
          v-else
          :key="`page-${p}`"
          type="button"
          class="page-btn"
          :class="{ 'page-btn--active': p === page }"
          :disabled="loading"
          :aria-current="p === page ? 'page' : undefined"
          @click="goTo(p)"
        >
          {{ p }}
        </button>
      </template>
      <button
        type="button"
        class="page-btn"
        :disabled="loading || page >= totalPages"
        aria-label="Następna strona"
        @click="goTo(page + 1)"
      >
        ›
      </button>
    </div>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 0.8125rem;
  color: var(--color-grey-dark);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-btn {
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.4rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: #fff;
  color: var(--color-text);
  font-size: 0.8125rem;
  line-height: 1;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #f8fafc;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.page-ellipsis {
  padding: 0 0.25rem;
  color: var(--color-grey);
  font-size: 0.8125rem;
}
</style>
