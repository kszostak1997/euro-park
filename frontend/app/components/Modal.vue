<script setup lang="ts">
defineProps<{ title: string }>()
const emit = defineEmits<{ close: [] }>()

const panelEl = ref<HTMLElement | null>(null)

const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

function getFocusable(): HTMLElement[] {
  if (!panelEl.value) return []
  return Array.from(panelEl.value.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR))
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
    return
  }
  if (event.key !== 'Tab') return

  const focusable = getFocusable()
  if (focusable.length === 0) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last?.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first?.focus()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  document.body.style.overflow = 'hidden'
  ;(getFocusable()[0] ?? panelEl.value)?.focus()
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="emit('close')">
      <div
        ref="panelEl"
        class="modal-panel"
        role="dialog"
        aria-modal="true"
        tabindex="-1"
        :aria-label="title"
      >
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <button
            type="button"
            class="modal-close"
            aria-label="Zamknij"
            @click="emit('close')"
          >
            <AppIcon name="x" :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 100;
}

.modal-panel {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  width: 100%;
  max-width: 440px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-text);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--color-grey-dark);
  border-radius: 6px;
}

.modal-close:hover {
  background: #f1f5f9;
}
</style>
