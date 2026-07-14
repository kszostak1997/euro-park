export type ApplicationStatus = 'PENDING' | 'NEEDS_CHANGES' | 'APPROVED' | 'REJECTED'

export interface ApplicationRow {
  id: number
  user_id: number
  registration_number: string
  floor: number
  status: ApplicationStatus
  comment: string | null
  created_at: string
}

export interface ApplicationPage {
  items: ApplicationRow[]
  total: number
  page: number
  size: number
}

export interface ApplicationInput {
  registration_number: string
  floor: number
  comment?: string | null
}
