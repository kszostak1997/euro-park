export interface AuthUser {
  id: number
  email: string
  role: 'USER' | 'MANAGER' | 'ADMIN'
  is_active: boolean
  created_at: string
}

interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export function roleLandingPath(role: string): string {
  return role === 'USER' ? '/applications' : '/manager'
}

export function useAuth() {
  const user = useState<AuthUser | null>('auth-user', () => null)
  const { api, accessToken, refreshToken, clearTokens } = useApi()
  const config = useRuntimeConfig()
  const baseURL = import.meta.server ? config.apiBase : config.public.apiBase

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
      user.value = await api<AuthUser>('/auth/me')
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
    user.value = null
  }

  return { user, isLoggedIn, register, login, logout, fetchCurrentUser }
}
