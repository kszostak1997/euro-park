export type ApplicationStatus = 'PENDING' | 'NEEDS_CHANGES' | 'APPROVED' | 'REJECTED'

export interface ApplicationRow {
  id: number
  user_id: number
  user_email: string
  registration_number: string
  floor: number
  status: ApplicationStatus
  applicant_comment: string | null
  manager_comment: string | null
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
  applicant_comment?: string | null
}
