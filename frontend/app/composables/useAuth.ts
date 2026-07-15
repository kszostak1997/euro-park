import type { AuthUser } from '~/types/user'

interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export function roleLandingPath(role: string): string {
  return role === 'USER' ? '/user' : '/manager/applications'
}

export function useAuth() {
  const user = useState<AuthUser | null>('auth-user', () => null)
  const { api, accessToken, refreshToken, clearTokens, baseURL } = useApiClient()

  const isLoggedIn = computed(() => user.value !== null)

  async function register(email: string, password: string): Promise<AuthUser> {
    return $fetch<AuthUser>('/auth/register', {
      baseURL,
      method: 'POST',
      body: { email, password },
    })
  }

  async function fetchCurrentUser(): Promise<AuthUser | null> {
    if (!accessToken.value) {
      user.value = null
      return null
    }
    try {
      user.value = await api<AuthUser>('/auth/current-user')
      return user.value
    } catch {
      user.value = null
      return null
    }
  }

  async function login(email: string, password: string): Promise<AuthUser> {
    const tokens = await $fetch<TokenPair>('/auth/login', {
      baseURL,
      method: 'POST',
      body: { email, password },
    })
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token

    const current = await fetchCurrentUser()
    if (!current) {
      throw new Error('Zalogowano, ale nie udało się pobrać danych użytkownika')
    }
    return current
  }

  function logout() {
    clearTokens()
  }

  async function ensureCurrentUser(): Promise<AuthUser | null> {
    if (!user.value) {
      await fetchCurrentUser()
    }
    return user.value
  }

  return {
    user,
    isLoggedIn,
    register,
    login,
    logout,
    fetchCurrentUser,
    ensureCurrentUser,
  }
}
