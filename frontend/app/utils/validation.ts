export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isValidEmail(value: string): boolean {
  return EMAIL_PATTERN.test(value)
}

const REGISTRATION_NUMBER_PATTERN = /^[A-Z]{2,3}[A-Z0-9]{4,5}$/

export function isValidRegistrationNumber(value: string): boolean {
  const normalized = value.trim().toUpperCase().replace(/[\s-]/g, '')
  return REGISTRATION_NUMBER_PATTERN.test(normalized)
}
