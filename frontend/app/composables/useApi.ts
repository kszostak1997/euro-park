export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = import.meta.server ? config.apiBase : config.public.apiBase

  const accessToken = useCookie<string | null>('access_token', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7,
  })
  const refreshToken = useCookie<string | null>('refresh_token', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7,
  })

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
  }

  async function refreshTokens(): Promise<boolean> {
    if (!refreshToken.value) return false
    try {
      const tokens = await $fetch<{ access_token: string; refresh_token: string }>(
        '/auth/refresh',
        {
          baseURL,
          method: 'POST',
          body: { refresh_token: refreshToken.value },
        },
      )
      accessToken.value = tokens.access_token
      refreshToken.value = tokens.refresh_token
      return true
    } catch {
      clearTokens()
      return false
    }
  }

  const api = $fetch.create({
    baseURL,
    retry: 1,
    retryStatusCodes: [401],
    onRequest({ options }) {
      if (accessToken.value) {
        const headers = new Headers(options.headers)
        headers.set('Authorization', `Bearer ${accessToken.value}`)
        options.headers = headers
      }
    },
    async onResponseError({ response }) {
      if (response.status === 401) {
        await refreshTokens()
      }
    },
  })

  return { api, accessToken, refreshToken, clearTokens }
}
