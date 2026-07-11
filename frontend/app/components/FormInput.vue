<script setup lang="ts">
defineProps<{
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
</script>

<template>
  <div class="field" :class="{ 'field--error': !!error }">
    <label :for="id">{{ label }}</label>
    <input
      :id="id"
      v-model="model"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :autocomplete="autocomplete"
      :minlength="minlength"
      :maxlength="maxlength"
    />
    <p v-if="error" class="field-error">{{ error }}</p>
  </div>
</template>
