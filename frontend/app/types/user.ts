import type { AuthUser } from '~/composables/useAuth'

export interface UserPage {
  items: AuthUser[]
  total: number
  page: number
  size: number
}
