<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'manager'] })
</script>

<template>
  <div class="app-content app-content--wide">
    <NuxtPage />
  </div>
</template>
