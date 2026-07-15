<script setup lang="ts">
const props = defineProps<{
  id: string
  label: string
  type?: string
  placeholder?: string
  error?: string | null
  disabled?: boolean
  required?: boolean
  autocomplete?: string
  minlength?: number
  maxlength?: number
}>()

const model = defineModel<string>({ default: '' })

const showPassword = ref(false)
const isPasswordField = computed(() => props.type === 'password')
const inputType = computed(() => {
  if (!isPasswordField.value) return props.type ?? 'text'
  return showPassword.value ? 'text' : 'password'
})
</script>

<template>
  <div class="field" :class="{ 'field--error': !!error }">
    <label :for="id">{{ label }}</label>
    <div
      class="field-input-wrap"
      :class="{ 'field-input-wrap--toggle': isPasswordField }"
    >
      <input
        :id="id"
        v-model="model"
        class="field-control"
        :type="inputType"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        :minlength="minlength"
        :maxlength="maxlength"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${id}-error` : undefined"
      />
      <button
        v-if="isPasswordField"
        type="button"
        class="field-toggle"
        tabindex="-1"
        :aria-label="showPassword ? 'Ukryj hasło' : 'Pokaż hasło'"
        @click="showPassword = !showPassword"
      >
        <AppIcon :name="showPassword ? 'eye-off' : 'eye'" :size="18" />
      </button>
    </div>
    <p v-if="error" :id="`${id}-error`" class="field-error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.field-input-wrap {
  position: relative;
}

.field-input-wrap input {
  width: 100%;
}

.field-input-wrap--toggle input {
  padding-right: 2.25rem;
}

.field-toggle {
  position: absolute;
  top: 50%;
  right: 0.6rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  background: transparent;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--color-grey);
}

.field-toggle:hover {
  color: var(--color-grey-dark);
}
</style>
