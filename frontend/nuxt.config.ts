// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/eslint'],
  css: ['~/assets/css/main.css', '~/assets/css/input.css'],
  runtimeConfig: {
    apiBase: 'http://backend:8000',
    public: {
      apiBase: 'http://localhost:8000',
    },
  },
})
