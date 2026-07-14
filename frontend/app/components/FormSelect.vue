<script setup lang="ts">
import type { SelectOption } from '~/types/form'

const props = defineProps<{
  id: string
  label: string
  options: SelectOption[]
  error?: string | null
  disabled?: boolean
  required?: boolean
}>()

const model = defineModel<string | number>({ default: '' })

const isOpen = ref(false)
const activeIndex = ref(-1)
const rootEl = ref<HTMLElement | null>(null)
const triggerEl = ref<HTMLButtonElement | null>(null)
const menuEl = ref<HTMLElement | null>(null)
const menuStyle = ref<{ top: string; left: string; width: string }>({
  top: '0px',
  left: '0px',
  width: '0px',
})

const selectedOption = computed(
  () => props.options.find((option) => option.value === model.value) ?? null,
)

function updateMenuPosition() {
  const rect = triggerEl.value?.getBoundingClientRect()
  if (!rect) return
  menuStyle.value = {
    top: `${rect.bottom + 6}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
  }
}

function open() {
  if (props.disabled) return
  activeIndex.value = props.options.findIndex((option) => option.value === model.value)
  updateMenuPosition()
  isOpen.value = true
}

function close() {
  isOpen.value = false
}

function toggle() {
  if (isOpen.value) close()
  else open()
}

function select(option: SelectOption) {
  model.value = option.value
  close()
}

function onTriggerKeydown(event: KeyboardEvent) {
  if (props.disabled) return
  if (!isOpen.value && (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ')) {
    event.preventDefault()
    open()
    return
  }
  if (!isOpen.value) return

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, props.options.length - 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
  } else if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    const option = props.options[activeIndex.value]
    if (option) select(option)
  } else if (event.key === 'Escape') {
    event.preventDefault()
    close()
  }
}

function onClickOutside(event: MouseEvent) {
  const target = event.target as Node
  if (rootEl.value?.contains(target)) return
  if (menuEl.value?.contains(target)) return
  close()
}

onMounted(() => {
  window.addEventListener('click', onClickOutside)
  window.addEventListener('resize', updateMenuPosition)
})
onUnmounted(() => {
  window.removeEventListener('click', onClickOutside)
  window.removeEventListener('resize', updateMenuPosition)
})
</script>

<template>
  <div ref="rootEl" class="field" :class="{ 'field--error': !!error }">
    <label :for="id">{{ label }}</label>
    <div class="select-wrap">
      <button
        :id="id"
        ref="triggerEl"
        type="button"
        class="select-trigger"
        :class="{ 'select-trigger--open': isOpen }"
        :disabled="disabled"
        :aria-expanded="isOpen"
        :aria-required="required"
        aria-haspopup="listbox"
        @click="toggle"
        @keydown="onTriggerKeydown"
      >
        <span>{{ selectedOption?.label ?? '' }}</span>
        <AppIcon name="chevron-down" :size="16" class="select-chevron" />
      </button>
      <Teleport to="body">
        <ul
          v-if="isOpen"
          ref="menuEl"
          class="select-menu"
          role="listbox"
          :style="menuStyle"
        >
          <li
            v-for="(option, index) in options"
            :key="option.value"
            role="option"
            class="select-option"
            :class="{
              'select-option--active': index === activeIndex,
              'select-option--selected': option.value === model,
            }"
            :aria-selected="option.value === model"
            @mouseenter="activeIndex = index"
            @click="select(option)"
          >
            {{ option.label }}
          </li>
        </ul>
      </Teleport>
    </div>
    <p v-if="error" class="field-error">{{ error }}</p>
  </div>
</template>

<style scoped>
.select-wrap {
  position: relative;
}

.select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 1rem;
  font-family: inherit;
  background: #fff;
  color: var(--color-text);
  cursor: pointer;
  text-align: left;
}

.select-trigger:disabled {
  opacity: 0.5;
  cursor: default;
}

.select-trigger--open,
.select-trigger:focus-visible {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: var(--shadow-focus);
}

.select-chevron {
  flex-shrink: 0;
  color: var(--color-grey);
  transition: transform 0.15s ease;
}

.select-trigger--open .select-chevron {
  transform: rotate(180deg);
}
</style>

<style>
.select-menu {
  position: fixed;
  z-index: 120;
  margin: 0;
  padding: 0.35rem;
  list-style: none;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  max-height: 220px;
  overflow-y: auto;
}

.select-menu .select-option {
  padding: 0.55rem 0.65rem;
  border-radius: 6px;
  font-size: 0.9375rem;
  color: var(--color-text);
  cursor: pointer;
}

.select-menu .select-option--active {
  background: #eff6ff;
}

.select-menu .select-option--selected {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
