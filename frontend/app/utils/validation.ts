export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isValidEmail(value: string): boolean {
  return EMAIL_PATTERN.test(value)
}

// Mirrors the backend's RegistrationNumber validator (app/schemas/validators.py):
// 2-3 letters followed by 4-5 letters/digits, after stripping spaces/dashes.
const REGISTRATION_NUMBER_PATTERN = /^[A-Z]{2,3}[A-Z0-9]{4,5}$/

export function isValidRegistrationNumber(value: string): boolean {
  const normalized = value.trim().toUpperCase().replace(/[\s-]/g, '')
  return REGISTRATION_NUMBER_PATTERN.test(normalized)
}
