export interface AuthUser {
  id: number
  email: string
  role: 'USER' | 'MANAGER' | 'ADMIN'
  is_active: boolean
  created_at: string
}

export interface UserPage {
  items: AuthUser[]
  total: number
  page: number
  size: number
}
