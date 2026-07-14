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
